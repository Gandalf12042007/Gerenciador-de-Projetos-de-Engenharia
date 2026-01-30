"""
Rotas de Projetos - CRUD
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import date
import sys
import os
import csv

# Adicionar path do database
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'database'))
from db_helper import DatabaseHelper

from middleware.auth_middleware import get_current_active_user
from utils.audit import registrar_auditoria
from middleware.permissions import permission_manager
from utils.permissions_decorators import verify_project_access, verify_project_modify, verify_project_delete

router = APIRouter(prefix="/projetos", tags=["Projetos"])


# Schemas
class ProjetoCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    endereco: Optional[str] = None
    cliente: Optional[str] = None
    valor_total: Optional[float] = None
    data_inicio: Optional[date] = None
    data_fim_prevista: Optional[date] = None
    status: str = "planejamento"


class ProjetoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    endereco: Optional[str] = None
    cliente: Optional[str] = None
    valor_total: Optional[float] = None
    data_inicio: Optional[date] = None
    data_fim_prevista: Optional[date] = None
    data_fim_real: Optional[date] = None
    status: Optional[str] = None
    progresso_percentual: Optional[float] = None


class ProjetoResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str]
    endereco: Optional[str]
    cliente: Optional[str]
    valor_total: Optional[float]
    data_inicio: Optional[date]
    data_fim_prevista: Optional[date]
    data_fim_real: Optional[date]
    status: str
    progresso_percentual: float
    criador_id: int
    criado_em: str
    atualizado_em: str


@router.get("/", response_model=List[ProjetoResponse])
async def listar_projetos(
    status_filter: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Lista projetos do usuário (onde é membro da equipe)
    
    Query params:
        status_filter: Filtrar por status (opcional)
    """
    db = DatabaseHelper()
    user_id = current_user.get("user_id") or current_user.get("id")
    
    # Listar apenas projetos onde usuário é membro da equipe
    if status_filter:
        projetos = db.execute_query(
            """
            SELECT DISTINCT p.id, p.nome, p.descricao, p.endereco, p.cliente, p.valor_total,
                   p.data_inicio, p.data_fim_prevista, p.data_fim_real, p.status,
                   p.progresso_percentual, p.criador_id, p.criado_em, p.atualizado_em
            FROM projetos p
            INNER JOIN equipes e ON p.id = e.projeto_id
            WHERE e.usuario_id = %s AND e.ativo = 1 AND p.status = %s
            ORDER BY p.criado_em DESC
            """,
            (user_id, status_filter),
            fetch=True
        )
    else:
        projetos = db.execute_query(
            """
            SELECT DISTINCT p.id, p.nome, p.descricao, p.endereco, p.cliente, p.valor_total,
                   p.data_inicio, p.data_fim_prevista, p.data_fim_real, p.status,
                   p.progresso_percentual, p.criador_id, p.criado_em, p.atualizado_em
            FROM projetos p
            INNER JOIN equipes e ON p.id = e.projeto_id
            WHERE e.usuario_id = %s AND e.ativo = 1
            ORDER BY p.criado_em DESC
            """,
            (user_id,),
            fetch=True
        )
    
    # Os resultados já vêm como dicionários do db_helper
    result = []
    for p in projetos or []:
        result.append({
            "id": p['id'],
            "nome": p['nome'],
            "descricao": p.get('descricao'),
            "endereco": p.get('endereco'),
            "cliente": p.get('cliente'),
            "valor_total": float(p['valor_total']) if p.get('valor_total') else None,
            "data_inicio": p.get('data_inicio'),
            "data_fim_prevista": p.get('data_fim_prevista'),
            "data_fim_real": p.get('data_fim_real'),
            "status": p['status'],
            "progresso_percentual": float(p.get('progresso_percentual', 0)),
            "criador_id": p['criador_id'],
            "criado_em": str(p['criado_em']),
            "atualizado_em": str(p['atualizado_em'])
        })
    return result


@router.get("/audit/logs")
async def consultar_auditoria(
    projeto_id: int = None,
    usuario_id: int = None,
    data_inicio: str = None,
    data_fim: str = None,
    formato: str = "json",
    current_user: dict = Depends(get_current_active_user)
):
    """
    Consulta/exporta logs de auditoria (apenas admins)
    """
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Apenas administradores podem consultar logs de auditoria")
    
    from database.db_helper import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = "SELECT a.*, u.nome as usuario_nome FROM audit_trail a LEFT JOIN usuarios u ON a.usuario_id = u.id WHERE 1=1"
        params = []
        
        if projeto_id:
            query += " AND (a.entidade = 'projeto' AND a.entidade_id = %s)"
            params.append(projeto_id)
        if usuario_id:
            query += " AND a.usuario_id = %s"
            params.append(usuario_id)
        if data_inicio:
            query += " AND a.criado_em >= %s"
            params.append(data_inicio)
        if data_fim:
            query += " AND a.criado_em <= %s"
            params.append(data_fim)
        
        query += " ORDER BY a.criado_em DESC"
        cursor.execute(query, tuple(params))
        logs = cursor.fetchall()
        
        if formato == "csv":
            def iter_csv():
                header = ["id", "usuario_id", "usuario_nome", "entidade", "entidade_id", "acao", "detalhes", "ip", "user_agent", "criado_em"]
                yield ",".join(header) + "\n"
                for l in logs:
                    row = [str(l.get(h, "")) if l.get(h, "") is not None else "" for h in header]
                    yield ",".join(row) + "\n"
            return StreamingResponse(iter_csv(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=audit_logs.csv"})
        
        return JSONResponse(content=logs)
    finally:
        cursor.close()
        conn.close()


@router.get("/{projeto_id}", response_model=ProjetoResponse)
async def buscar_projeto(
    projeto_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Busca projeto por ID (apenas membros da equipe)
    """
    user_id = current_user.get("user_id") or current_user.get("id")
    
    # Verificar se usuário tem acesso ao projeto
    if not permission_manager.is_project_member(user_id, projeto_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem acesso a este projeto"
        )
    
    db = DatabaseHelper()
    
    projetos = db.execute_query(
        """
        SELECT id, nome, descricao, endereco, cliente, valor_total,
               data_inicio, data_fim_prevista, data_fim_real, status,
               progresso_percentual, criador_id, criado_em, atualizado_em
        FROM projetos
        WHERE id = %s
        """,
        (projeto_id,),
        fetch=True
    )
    
    if not projetos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado"
        )
    
    p = projetos[0]
    return {
        "id": p['id'],
        "nome": p['nome'],
        "descricao": p.get('descricao'),
        "endereco": p.get('endereco'),
        "cliente": p.get('cliente'),
        "valor_total": float(p['valor_total']) if p.get('valor_total') else None,
        "data_inicio": p.get('data_inicio'),
        "data_fim_prevista": p.get('data_fim_prevista'),
        "data_fim_real": p.get('data_fim_real'),
        "status": p['status'],
        "progresso_percentual": float(p.get('progresso_percentual', 0)),
        "criador_id": p['criador_id'],
        "criado_em": str(p['criado_em']),
        "atualizado_em": str(p['atualizado_em'])
    }


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def criar_projeto(
    projeto: ProjetoCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Cria novo projeto
    """
    db = DatabaseHelper()
    
    try:
        # Inserir projeto
        projeto_id = db.execute_insert(
            """
            INSERT INTO projetos (
                nome, descricao, endereco, cliente, valor_total,
                data_inicio, data_fim_prevista, status, criador_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                projeto.nome,
                projeto.descricao,
                projeto.endereco,
                projeto.cliente,
                projeto.valor_total,
                str(projeto.data_inicio) if projeto.data_inicio else None,
                str(projeto.data_fim_prevista) if projeto.data_fim_prevista else None,
                projeto.status,
                current_user.get("user_id") or current_user.get("id")
            )
        )
        
        user_id = current_user.get("user_id") or current_user.get("id")
        
        # Adicionar criador à equipe como gerente
        from datetime import date as dt_date
        db.execute_insert(
            """
            INSERT INTO equipes (projeto_id, usuario_id, papel, data_entrada, ativo)
            VALUES (%s, %s, 'gerente', %s, 1)
            """,
            (projeto_id, user_id, str(dt_date.today()))
        )
        
        return {"message": "Projeto criado com sucesso", "id": projeto_id}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar projeto: {str(e)}"
        )


@router.put("/{projeto_id}")
async def atualizar_projeto(
    projeto_id: int,
    projeto: ProjetoUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Atualiza projeto existente (apenas gerente ou criador)
    """
    user_id = current_user.get("user_id") or current_user.get("id")
    
    # Verificar permissão (apenas gerente ou dono)
    if not permission_manager.can_modify_project(user_id, projeto_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas gerentes do projeto podem modificá-lo"
        )
    
    db = DatabaseHelper()
    
    # Verificar se projeto existe
    existing = db.execute_query(
        "SELECT id FROM projetos WHERE id = %s",
        (projeto_id,),
        fetch=True
    )
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado"
        )
    
    # Construir query dinamicamente com campos fornecidos
    updates = []
    params = []
    
    for field, value in projeto.dict(exclude_unset=True).items():
        updates.append(f"{field} = %s")
        # Converter datas para string
        if isinstance(value, date):
            value = str(value)
        params.append(value)
    
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum campo para atualizar"
        )
    
    params.append(projeto_id)
    
    query = f"UPDATE projetos SET {', '.join(updates)} WHERE id = %s"
    
    try:
        db.execute_query(query, tuple(params))
        return {"message": "Projeto atualizado com sucesso"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar projeto: {str(e)}"
        )


@router.delete("/{projeto_id}")
async def deletar_projeto(
    projeto_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Deleta projeto (apenas criador)
    """
    user_id = current_user.get("user_id") or current_user.get("id")
    
    # Verificar permissão (apenas criador pode deletar)
    if not permission_manager.can_delete_project(user_id, projeto_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o criador do projeto pode deletá-lo"
        )
    
    db = DatabaseHelper()
    
    # Verificar se projeto existe
    existing = db.execute_query(
        "SELECT id FROM projetos WHERE id = %s",
        (projeto_id,),
        fetch=True
    )
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado"
        )
    
    try:
        db.execute_query("DELETE FROM projetos WHERE id = %s", (projeto_id,))
        return {"message": "Projeto deletado com sucesso"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar projeto: {str(e)}"
        )
