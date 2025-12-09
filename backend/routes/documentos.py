"""
Rotas para gerenciamento de documentos
Permite upload, download, versionamento e organização de arquivos técnicos
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List, Optional
from datetime import datetime
import os
import uuid
from middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/documentos", tags=["Documentos"])

# Diretório para armazenar uploads
UPLOAD_DIR = "uploads/documentos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/{projeto_id}")
async def listar_documentos(
    projeto_id: int,
    categoria: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Lista todos os documentos de um projeto
    Filtros: categoria (plantas, rrt, diario, medicoes, fotos, relatorios)
    """
    from database.db_helper import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
            SELECT d.*, u.nome as uploaded_por_nome,
                   COUNT(v.id) as total_versoes
            FROM documentos d
            LEFT JOIN usuarios u ON d.uploaded_por = u.id
            LEFT JOIN versoes_documento v ON d.id = v.documento_id
            WHERE d.projeto_id = %s
        """
        params = [projeto_id]
        
        if categoria:
            query += " AND d.categoria = %s"
            params.append(categoria)
        
        query += " GROUP BY d.id ORDER BY d.data_upload DESC"
        
        cursor.execute(query, params)
        documentos = cursor.fetchall()
        
        return {
            "success": True,
            "total": len(documentos),
            "documentos": documentos
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.post("/{projeto_id}/upload")
async def upload_documento(
    projeto_id: int,
    file: UploadFile = File(...),
    categoria: str = "outros",
    descricao: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Faz upload de um novo documento
    Categorias: plantas, rrt, diario, medicoes, fotos, relatorios, outros
    """
    from database.db_helper import get_db_connection
    
    # Gerar nome único para arquivo
    extensao = os.path.splitext(file.filename)[1]
    nome_unico = f"{uuid.uuid4()}{extensao}"
    caminho_arquivo = os.path.join(UPLOAD_DIR, nome_unico)
    
    # Salvar arquivo
    with open(caminho_arquivo, "wb") as f:
        conteudo = await file.read()
        f.write(conteudo)
    
    tamanho_bytes = len(conteudo)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Inserir documento
        query = """
            INSERT INTO documentos 
            (projeto_id, nome, categoria, descricao, caminho_arquivo, 
             tamanho_bytes, uploaded_por, data_upload)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """
        cursor.execute(query, (
            projeto_id, file.filename, categoria, descricao,
            caminho_arquivo, tamanho_bytes, current_user['id']
        ))
        
        doc_id = cursor.lastrowid
        
        # Criar primeira versão
        query_versao = """
            INSERT INTO versoes_documento
            (documento_id, numero_versao, caminho_arquivo, tamanho_bytes,
             criado_por, data_criacao, comentario)
            VALUES (%s, 1, %s, %s, %s, NOW(), 'Versão inicial')
        """
        cursor.execute(query_versao, (
            doc_id, caminho_arquivo, tamanho_bytes, current_user['id']
        ))
        
        conn.commit()
        
        return {
            "success": True,
            "message": "Documento enviado com sucesso",
            "documento_id": doc_id,
            "nome": file.filename,
            "tamanho": tamanho_bytes
        }
        
    except Exception as e:
        conn.rollback()
        # Remover arquivo se houver erro
        if os.path.exists(caminho_arquivo):
            os.remove(caminho_arquivo)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.post("/{documento_id}/nova-versao")
async def criar_nova_versao(
    documento_id: int,
    file: UploadFile = File(...),
    comentario: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Cria uma nova versão de um documento existente"""
    from database.db_helper import get_db_connection
    
    # Salvar nova versão do arquivo
    extensao = os.path.splitext(file.filename)[1]
    nome_unico = f"{uuid.uuid4()}{extensao}"
    caminho_arquivo = os.path.join(UPLOAD_DIR, nome_unico)
    
    with open(caminho_arquivo, "wb") as f:
        conteudo = await file.read()
        f.write(conteudo)
    
    tamanho_bytes = len(conteudo)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Obter última versão
        cursor.execute("""
            SELECT MAX(numero_versao) as ultima_versao
            FROM versoes_documento
            WHERE documento_id = %s
        """, (documento_id,))
        
        result = cursor.fetchone()
        nova_versao = (result['ultima_versao'] or 0) + 1
        
        # Criar nova versão
        query = """
            INSERT INTO versoes_documento
            (documento_id, numero_versao, caminho_arquivo, tamanho_bytes,
             criado_por, data_criacao, comentario)
            VALUES (%s, %s, %s, %s, %s, NOW(), %s)
        """
        cursor.execute(query, (
            documento_id, nova_versao, caminho_arquivo,
            tamanho_bytes, current_user['id'], comentario
        ))
        
        # Atualizar documento principal
        cursor.execute("""
            UPDATE documentos
            SET caminho_arquivo = %s, tamanho_bytes = %s
            WHERE id = %s
        """, (caminho_arquivo, tamanho_bytes, documento_id))
        
        conn.commit()
        
        return {
            "success": True,
            "message": f"Versão {nova_versao} criada com sucesso",
            "versao": nova_versao
        }
        
    except Exception as e:
        conn.rollback()
        if os.path.exists(caminho_arquivo):
            os.remove(caminho_arquivo)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.get("/{documento_id}/versoes")
async def listar_versoes(
    documento_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Lista todas as versões de um documento"""
    from database.db_helper import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT v.*, u.nome as criado_por_nome
            FROM versoes_documento v
            LEFT JOIN usuarios u ON v.criado_por = u.id
            WHERE v.documento_id = %s
            ORDER BY v.numero_versao DESC
        """, (documento_id,))
        
        versoes = cursor.fetchall()
        
        return {
            "success": True,
            "total_versoes": len(versoes),
            "versoes": versoes
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.delete("/{documento_id}")
async def deletar_documento(
    documento_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Deleta um documento e todas suas versões"""
    from database.db_helper import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Buscar arquivos para deletar
        cursor.execute("""
            SELECT caminho_arquivo FROM documentos WHERE id = %s
            UNION
            SELECT caminho_arquivo FROM versoes_documento WHERE documento_id = %s
        """, (documento_id, documento_id))
        
        arquivos = cursor.fetchall()
        
        # Deletar do banco
        cursor.execute("DELETE FROM documentos WHERE id = %s", (documento_id,))
        conn.commit()
        
        # Deletar arquivos físicos
        for arquivo in arquivos:
            caminho = arquivo['caminho_arquivo']
            if os.path.exists(caminho):
                os.remove(caminho)
        
        return {
            "success": True,
            "message": "Documento deletado com sucesso"
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
