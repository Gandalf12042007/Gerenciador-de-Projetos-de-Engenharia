"""
Rotas de Notificações
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import sys
import os

# Adicionar path do database
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'database'))
from db_helper import DatabaseHelper

from middleware.auth_middleware import get_current_active_user

router = APIRouter(prefix="/notificacoes", tags=["Notificações"])


# Schemas
class NotificacaoCreate(BaseModel):
    tipo: str  # tarefa, mensagem, documento, projeto, sistema, mencao
    titulo: str
    mensagem: str
    link: Optional[str] = None


@router.get("/")
async def listar_notificacoes(
    apenas_nao_lidas: bool = False,
    limite: int = 50,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Lista notificações do usuário
    """
    user_id = current_user.get("user_id") or current_user.get("id")
    db = DatabaseHelper()
    
    if apenas_nao_lidas:
        notificacoes = db.execute_query(
            """
            SELECT id, tipo, titulo, mensagem, conteudo, link, lida, criado_em
            FROM notificacoes
            WHERE usuario_id = %s AND lida = 0
            ORDER BY criado_em DESC
            LIMIT %s
            """,
            (user_id, limite),
            fetch=True
        )
    else:
        notificacoes = db.execute_query(
            """
            SELECT id, tipo, titulo, mensagem, conteudo, link, lida, criado_em
            FROM notificacoes
            WHERE usuario_id = %s
            ORDER BY criado_em DESC
            LIMIT %s
            """,
            (user_id, limite),
            fetch=True
        )
    
    return [
        {
            "id": n['id'],
            "tipo": n['tipo'],
            "titulo": n['titulo'],
            "mensagem": n['mensagem'] or n['conteudo'],  # mensagem ou conteudo
            "link": n['link'],
            "lida": bool(n['lida']),
            "criado_em": n['criado_em']
        }
        for n in notificacoes
    ]


@router.get("/nao-lidas/contagem")
async def contar_nao_lidas(
    current_user: dict = Depends(get_current_active_user)
):
    """
    Retorna contagem de notificações não lidas
    """
    user_id = current_user.get("user_id") or current_user.get("id")
    db = DatabaseHelper()
    
    result = db.execute_query(
        "SELECT COUNT(*) as total FROM notificacoes WHERE usuario_id = %s AND lida = 0",
        (user_id,),
        fetch=True
    )
    
    return {"count": result[0]['total'] if result else 0}


@router.put("/{notificacao_id}/marcar-lida")
async def marcar_como_lida(
    notificacao_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Marca notificação como lida
    """
    user_id = current_user.get("user_id") or current_user.get("id")
    db = DatabaseHelper()
    
    # Verificar se pertence ao usuário
    existing = db.execute_query(
        "SELECT id FROM notificacoes WHERE id = %s AND usuario_id = %s",
        (notificacao_id, user_id),
        fetch=True
    )
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada"
        )
    
    db.execute_query(
        "UPDATE notificacoes SET lida = 1 WHERE id = %s",
        (notificacao_id,)
    )
    
    return {"message": "Notificação marcada como lida"}


@router.put("/marcar-todas-lidas")
async def marcar_todas_como_lidas(
    current_user: dict = Depends(get_current_active_user)
):
    """
    Marca todas as notificações como lidas
    """
    user_id = current_user.get("user_id") or current_user.get("id")
    db = DatabaseHelper()
    
    db.execute_query(
        "UPDATE notificacoes SET lida = 1 WHERE usuario_id = %s AND lida = 0",
        (user_id,)
    )
    
    return {"message": "Todas as notificações marcadas como lidas"}


@router.delete("/{notificacao_id}")
async def deletar_notificacao(
    notificacao_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Deleta notificação
    """
    user_id = current_user.get("user_id") or current_user.get("id")
    db = DatabaseHelper()
    
    # Verificar se pertence ao usuário
    existing = db.execute_query(
        "SELECT id FROM notificacoes WHERE id = %s AND usuario_id = %s",
        (notificacao_id, user_id),
        fetch=True
    )
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada"
        )
    
    db.execute_query(
        "DELETE FROM notificacoes WHERE id = %s",
        (notificacao_id,)
    )
    
    return {"message": "Notificação deletada"}


# Função auxiliar para criar notificações (usar em outros módulos)
def criar_notificacao(
    usuario_id: int,
    tipo: str,
    titulo: str,
    mensagem: str,
    link: str = None
):
    """
    Cria uma notificação para um usuário.
    Tipos: tarefa, mensagem, documento, projeto, sistema, mencao
    """
    db = DatabaseHelper()
    
    try:
        db.execute_query(
            """
            INSERT INTO notificacoes (usuario_id, tipo, titulo, mensagem, link)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (usuario_id, tipo, titulo, mensagem, link)
        )
        return True
    except Exception as e:
        print(f"Erro ao criar notificação: {e}")
        return False
