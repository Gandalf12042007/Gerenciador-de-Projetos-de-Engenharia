"""
Rotas de Projetos - CRUD
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
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Lista todos os projetos
    
    Query params:
        status: Filtrar por status (opcional)
    """
    db = DatabaseHelper()
    
    if status:
        projetos = db.execute_query(
            """
            SELECT id, nome, descricao, endereco, cliente, valor_total,
                   data_inicio, data_fim_prevista, data_fim_real, status,
                   progresso_percentual, criador_id, criado_em, atualizado_em
            FROM projetos
            WHERE status = %s
            ORDER BY criado_em DESC
            """,
            (status,),
            fetch=True
        )
    else:
        projetos = db.execute_query(
            """
            SELECT id, nome, descricao, endereco, cliente, valor_total,
                   data_inicio, data_fim_prevista, data_fim_real, status,
                   progresso_percentual, criador_id, criado_em, atualizado_em
            FROM projetos
            ORDER BY criado_em DESC
            """,
            fetch=True
        )
    
    return [
        {
            "id": p[0],
            "nome": p[1],
            "descricao": p[2],
            "endereco": p[3],
            "cliente": p[4],
            "valor_total": float(p[5]) if p[5] else None,
            "data_inicio": p[6],
            "data_fim_prevista": p[7],
            "data_fim_real": p[8],
            "status": p[9],
            "progresso_percentual": float(p[10]),
            "criador_id": p[11],
            "criado_em": str(p[12]),
            "atualizado_em": str(p[13])
        }
        for p in projetos
    ]


@router.get("/{projeto_id}", response_model=ProjetoResponse)
async def buscar_projeto(
    projeto_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Busca projeto por ID
    """
    db = DatabaseHelper()
    
    projeto = db.execute_query(
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
    
    if not projeto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado"
        )
    
    p = projeto[0]
    return {
        "id": p[0],
        "nome": p[1],
        "descricao": p[2],
        "endereco": p[3],
        "cliente": p[4],
        "valor_total": float(p[5]) if p[5] else None,
        "data_inicio": p[6],
        "data_fim_prevista": p[7],
        "data_fim_real": p[8],
        "status": p[9],
        "progresso_percentual": float(p[10]),
        "criador_id": p[11],
        "criado_em": str(p[12]),
        "atualizado_em": str(p[13])
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
        result = db.execute_query(
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
                projeto.data_inicio,
                projeto.data_fim_prevista,
                projeto.status,
                current_user["user_id"]
            ),
            fetch=False
        )
        
        return {"message": "Projeto criado com sucesso", "id": result}
    
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
    Atualiza projeto existente
    """
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
    Deleta projeto
    """
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
