"""
Rotas para gerenciamento de documentos
Permite upload, download, versionamento e organização de arquivos técnicos
"""
import sys
import os
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from typing import Optional
from pydantic import BaseModel

# Adicionar path do database
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'database'))
from db_helper import DatabaseHelper

from middleware.auth_middleware import get_current_active_user

# Logger para auditoria
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documentos", tags=["Documentos"])

# Diretório para armazenar uploads
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'uploads', 'documentos')
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Extensões permitidas
ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.dwg', '.dxf', '.png', '.jpg', '.jpeg', '.zip'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


class DocumentoUpdate(BaseModel):
    descricao: Optional[str] = None
    categoria: Optional[str] = None


@router.get("/projeto/{projeto_id}")
async def listar_documentos(
    projeto_id: int,
    categoria: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Lista todos os documentos de um projeto
    Categorias: plantas, rrt, diario, medicoes, fotos, relatorios, contratos, outros
    """
    db = DatabaseHelper()
    
    try:
        if categoria:
            documentos = db.execute_query(
                """
                SELECT d.id, d.projeto_id, d.nome, d.descricao,
                       d.categoria, d.tamanho_bytes, d.tipo, d.caminho_arquivo,
                       d.uploaded_por, d.criado_em, u.nome as uploaded_por_nome
                FROM documentos d
                LEFT JOIN usuarios u ON d.uploaded_por = u.id
                WHERE d.projeto_id = %s AND d.categoria = %s
                ORDER BY d.criado_em DESC
                """,
                (projeto_id, categoria),
                fetch=True
            )
        else:
            documentos = db.execute_query(
                """
                SELECT d.id, d.projeto_id, d.nome, d.descricao,
                       d.categoria, d.tamanho_bytes, d.tipo, d.caminho_arquivo,
                       d.uploaded_por, d.criado_em, u.nome as uploaded_por_nome
                FROM documentos d
                LEFT JOIN usuarios u ON d.uploaded_por = u.id
                WHERE d.projeto_id = %s
                ORDER BY d.criado_em DESC
                """,
                (projeto_id,),
                fetch=True
            )
        
        return {
            "success": True,
            "total": len(documentos),
            "documentos": documentos
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projeto/{projeto_id}/upload")
async def upload_documento(
    projeto_id: int,
    file: UploadFile = File(...),
    categoria: str = "outros",
    descricao: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Faz upload de um documento para o projeto
    Categorias: plantas, rrt, diario, medicoes, fotos, relatorios, contratos, outros
    """
    db = DatabaseHelper()
    user_id = current_user.get("user_id") or current_user.get("id")
    
    try:
        # Validar extensão
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Extensão não permitida. Permitidas: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Ler conteúdo
        content = await file.read()
        
        # Validar tamanho
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Arquivo muito grande. Máximo: {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Gerar nome único
        nome_unico = f"{uuid.uuid4()}{ext}"
        projeto_dir = os.path.join(UPLOAD_DIR, str(projeto_id))
        os.makedirs(projeto_dir, exist_ok=True)
        
        caminho = os.path.join(projeto_dir, nome_unico)
        
        # Salvar arquivo
        with open(caminho, 'wb') as f:
            f.write(content)
        
        # Registrar no banco
        # tipo deve ser um dos valores permitidos: 'contrato', 'projeto', 'laudo', 'orcamento', 
        # 'nota_fiscal', 'outro', 'plantas', 'rrt', 'diario', 'medicoes', 'fotos', 'relatorios', 'outros'
        tipo_documento = categoria if categoria in ('contrato', 'projeto', 'laudo', 'orcamento', 
            'nota_fiscal', 'outro', 'plantas', 'rrt', 'diario', 'medicoes', 'fotos', 'relatorios', 'outros') else 'outros'
        
        doc_id = db.execute_query(
            """
            INSERT INTO documentos 
            (projeto_id, nome, descricao, categoria, tamanho_bytes, tipo, caminho_arquivo, uploaded_por)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                projeto_id, file.filename, descricao,
                categoria, len(content), tipo_documento, caminho, user_id
            )
        )
        
        logger.info(f"Documento {file.filename} uploaded por {user_id} no projeto {projeto_id}")
        
        return {
            "success": True,
            "message": "Documento uploaded com sucesso",
            "documento_id": doc_id,
            "nome": file.filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{documento_id}/download")
async def download_documento(
    documento_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """Faz download de um documento"""
    db = DatabaseHelper()
    
    try:
        doc = db.execute_query(
            "SELECT * FROM documentos WHERE id = %s",
            (documento_id,),
            fetch=True
        )
        
        if not doc:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        
        doc = doc[0]
        caminho = doc['caminho_arquivo']
        
        if not caminho or not os.path.exists(caminho):
            raise HTTPException(status_code=404, detail="Arquivo não encontrado no servidor")
        
        return FileResponse(
            path=caminho,
            filename=doc['nome'],
            media_type=doc.get('tipo', 'application/octet-stream')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{documento_id}")
async def atualizar_documento(
    documento_id: int,
    dados: DocumentoUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """Atualiza informações de um documento"""
    db = DatabaseHelper()
    
    try:
        updates = []
        params = []
        
        if dados.descricao is not None:
            updates.append("descricao = %s")
            params.append(dados.descricao)
        if dados.categoria:
            updates.append("categoria = %s")
            params.append(dados.categoria)
        
        if not updates:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
        
        params.append(documento_id)
        query = f"UPDATE documentos SET {', '.join(updates)} WHERE id = %s"
        
        db.execute_query(query, tuple(params))
        
        return {
            "success": True,
            "message": "Documento atualizado com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{documento_id}")
async def deletar_documento(
    documento_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """Deleta um documento"""
    db = DatabaseHelper()
    user_id = current_user.get("user_id") or current_user.get("id")
    
    try:
        # Buscar documento
        doc = db.execute_query(
            "SELECT * FROM documentos WHERE id = %s",
            (documento_id,),
            fetch=True
        )
        
        if not doc:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        
        doc = doc[0]
        
        # Deletar arquivo físico
        caminho = doc.get('caminho_arquivo')
        if caminho and os.path.exists(caminho):
            os.remove(caminho)
        
        # Deletar do banco
        db.execute_query("DELETE FROM documentos WHERE id = %s", (documento_id,))
        
        logger.info(f"Documento {doc['nome']} deletado por {user_id}")
        
        return {
            "success": True,
            "message": "Documento deletado com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projeto/{projeto_id}/categorias")
async def listar_categorias(
    projeto_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """Lista categorias com contagem de documentos"""
    db = DatabaseHelper()
    
    try:
        categorias = db.execute_query(
            """
            SELECT categoria, COUNT(*) as quantidade
            FROM documentos
            WHERE projeto_id = %s
            GROUP BY categoria
            ORDER BY quantidade DESC
            """,
            (projeto_id,),
            fetch=True
        )
        
        return {
            "success": True,
            "categorias": categorias
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

