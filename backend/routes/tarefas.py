"""
Rotas de Tarefas - CRUD
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import date
import sys
import os

# Adicionar path do database
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'database'))
from db_helper import DatabaseHelper

from middleware.auth_middleware import get_current_active_user
from middleware.permissions import permission_manager

router = APIRouter(prefix="/tarefas", tags=["Tarefas"])


# Schemas
class TarefaCreate(BaseModel):
    projeto_id: int
    titulo: str
    descricao: Optional[str] = None
    status: str = "a_fazer"
    prioridade: str = "media"
    data_inicio: Optional[date] = None
    data_fim_prevista: Optional[date] = None
    responsavel_id: Optional[int] = None


class TarefaUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    status: Optional[str] = None
    prioridade: Optional[str] = None
    data_inicio: Optional[date] = None
    data_fim_prevista: Optional[date] = None
    data_fim_real: Optional[date] = None
    responsavel_id: Optional[int] = None
    progresso_percentual: Optional[float] = None


@router.get("/projeto/{projeto_id}")
async def listar_tarefas_projeto(
    projeto_id: int,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Lista tarefas de um projeto (apenas membros)
    """
    user_id = current_user.get("user_id") or current_user.get("id")
    
    # Verificar se usuário é membro do projeto
    if not permission_manager.is_project_member(user_id, projeto_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem acesso a este projeto"
        )
    
    db = DatabaseHelper()
    
    if status:
        tarefas = db.execute_query(
            """
            SELECT t.id, t.titulo, t.descricao, t.status, t.prioridade,
                   t.data_inicio, t.data_fim_prevista, t.data_fim_real,
                   t.responsavel_id, t.progresso_percentual, t.ordem,
                   u.nome as responsavel_nome
            FROM tarefas t
            LEFT JOIN usuarios u ON t.responsavel_id = u.id
            WHERE t.projeto_id = %s AND t.status = %s
            ORDER BY t.ordem, t.criado_em
            """,
            (projeto_id, status),
            fetch=True
        )
    else:
        tarefas = db.execute_query(
            """
            SELECT t.id, t.titulo, t.descricao, t.status, t.prioridade,
                   t.data_inicio, t.data_fim_prevista, t.data_fim_real,
                   t.responsavel_id, t.progresso_percentual, t.ordem,
                   u.nome as responsavel_nome
            FROM tarefas t
            LEFT JOIN usuarios u ON t.responsavel_id = u.id
            WHERE t.projeto_id = %s
            ORDER BY t.ordem, t.criado_em
            """,
            (projeto_id,),
            fetch=True
        )
    
    return [
        {
            "id": t[0],
            "titulo": t[1],
            "descricao": t[2],
            "status": t[3],
            "prioridade": t[4],
            "data_inicio": t[5],
            "data_fim_prevista": t[6],
            "data_fim_real": t[7],
            "responsavel_id": t[8],
            "progresso_percentual": float(t[9]) if t[9] else 0,
            "ordem": t[10],
            "responsavel_nome": t[11]
        }
        for t in tarefas
    ]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def criar_tarefa(
    tarefa: TarefaCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Cria nova tarefa (apenas membros do projeto)
    """
    user_id = current_user.get("user_id") or current_user.get("id")
    
    # Verificar se usuário é membro do projeto
    if not permission_manager.is_project_member(user_id, tarefa.projeto_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem acesso a este projeto"
        )
    
    db = DatabaseHelper()
    
    try:
        result = db.execute_query(
            """
            INSERT INTO tarefas (
                projeto_id, titulo, descricao, status, prioridade,
                data_inicio, data_fim_prevista, responsavel_id, criador_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                tarefa.projeto_id,
                tarefa.titulo,
                tarefa.descricao,
                tarefa.status,
                tarefa.prioridade,
                tarefa.data_inicio,
                tarefa.data_fim_prevista,
                tarefa.responsavel_id,
                current_user["user_id"]
            )
        )
        
        return {"message": "Tarefa criada com sucesso", "id": result}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar tarefa: {str(e)}"
        )


@router.put("/{tarefa_id}")
async def atualizar_tarefa(
    tarefa_id: int,
    tarefa: TarefaUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Atualiza tarefa existente (apenas membros do projeto)
    """
    user_id = current_user.get("user_id") or current_user.get("id")
    db = DatabaseHelper()
    
    # Verificar se tarefa existe e obter projeto_id
    existing = db.execute_query(
        "SELECT projeto_id FROM tarefas WHERE id = %s",
        (tarefa_id,),
        fetch=True
    )
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada"
        )
    
    projeto_id = existing[0][0]
    
    # Verificar se usuário é membro do projeto
    if not permission_manager.is_project_member(user_id, projeto_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem acesso a este projeto"
        )
    
    # Construir query
    updates = []
    params = []
    
    for field, value in tarefa.dict(exclude_unset=True).items():
        updates.append(f"{field} = %s")
        params.append(value)
    
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum campo para atualizar"
        )
    
    params.append(tarefa_id)
    query = f"UPDATE tarefas SET {', '.join(updates)} WHERE id = %s"
    
    try:
        db.execute_query(query, tuple(params))
        return {"message": "Tarefa atualizada com sucesso"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar tarefa: {str(e)}"
        )


@router.delete("/{tarefa_id}")
async def deletar_tarefa(
    tarefa_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Deleta tarefa (apenas membros do projeto)
    """
    user_id = current_user.get("user_id") or current_user.get("id")
    db = DatabaseHelper()
    
    # Verificar se tarefa existe e obter projeto_id
    existing = db.execute_query(
        "SELECT projeto_id FROM tarefas WHERE id = %s",
        (tarefa_id,),
        fetch=True
    )
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada"
        )
    
    projeto_id = existing[0][0]
    
    # Verificar se usuário é membro do projeto
    if not permission_manager.is_project_member(user_id, projeto_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem acesso a este projeto"
        )
    
    try:
        db.execute_query("DELETE FROM tarefas WHERE id = %s", (tarefa_id,))
        return {"message": "Tarefa deletada com sucesso"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar tarefa: {str(e)}"
        )
    
    try:
        db.execute_query("DELETE FROM tarefas WHERE id = %s", (tarefa_id,))
        return {"message": "Tarefa deletada com sucesso"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar tarefa: {str(e)}"
        )
