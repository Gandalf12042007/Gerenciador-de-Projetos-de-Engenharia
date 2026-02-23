"""
Validador de Projetos - Verifica se projeto_id foi fornecido e é válido
"""

import sys
import os
from typing import Optional
from functools import wraps

# Adicionar path do database
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'database'))
from db_helper import DatabaseHelper

from exceptions.project_exceptions import (
    ProjetoNaoSelecionadoException,
    ProjetoInvalidoException,
    ProjetoAcessoNegadoException
)


def validar_projeto_selecionado(f):
    """
    Decorador para validar se projeto_id foi fornecido nos kwargs
    
    Levanta ProjetoNaoSelecionadoException se projeto_id não estiver presente
    """
    @wraps(f)
    async def wrapper(*args, **kwargs):
        # Procurar por projeto_id nos kwargs
        projeto_id = kwargs.get('projeto_id') or kwargs.get('id')
        
        if not projeto_id or not isinstance(projeto_id, (int, str)):
            raise ProjetoNaoSelecionadoException(
                detail="❌ Nenhum projeto foi selecionado. Selecione um projeto para continuar."
            )
        
        # Tentar converter para int se for string
        try:
            if isinstance(projeto_id, str):
                projeto_id = int(projeto_id)
                kwargs['projeto_id'] = projeto_id
        except (ValueError, TypeError):
            raise ProjetoNaoSelecionadoException(
                detail="❌ ID do projeto inválido. Verifique se o projeto foi selecionado corretamente."
            )
        
        return await f(*args, **kwargs)
    
    return wrapper


def validar_projeto_existe(f):
    """
    Decorador para validar se projeto existe no banco de dados
    
    Levanta ProjetoInvalidoException se projeto não existir
    """
    @wraps(f)
    async def wrapper(*args, **kwargs):
        projeto_id = kwargs.get('projeto_id') or kwargs.get('id')
        
        if not projeto_id:
            raise ProjetoNaoSelecionadoException()
        
        db = DatabaseHelper()
        projeto = db.execute_query(
            "SELECT id FROM projetos WHERE id = %s",
            (projeto_id,),
            fetch=True
        )
        
        if not projeto:
            raise ProjetoInvalidoException(
                detail=f"❌ Projeto #{projeto_id} não foi encontrado. Verifique se o ID está correto ou se o projeto foi deletado."
            )
        
        return await f(*args, **kwargs)
    
    return wrapper


def verificar_acesso_projeto(f):
    """
    Decorador que verifica se usuário tem acesso ao projeto
    Requer que current_user esteja nos kwargs
    
    Levanta ProjetoAcessoNegadoException se não tiver acesso
    """
    @wraps(f)
    async def wrapper(*args, **kwargs):
        projeto_id = kwargs.get('projeto_id') or kwargs.get('id')
        current_user = kwargs.get('current_user')
        
        if not projeto_id:
            raise ProjetoNaoSelecionadoException()
        
        if not current_user:
            raise ProjetoAcessoNegadoException(
                detail="❌ Usuário não autenticado. Faça login para acessar projetos."
            )
        
        user_id = current_user.get("id") or current_user.get("user_id")
        
        # Importar aqui para evitar circular import
        from middleware.permissions import permission_manager
        
        # Verificar se é admin
        is_admin = current_user.get("is_admin", False)
        
        if not is_admin:
            # Verificar se usuário é membro do projeto
            if not permission_manager.is_project_member(user_id, projeto_id):
                raise ProjetoAcessoNegadoException(
                    detail=f"❌ Você não tem permissão para acessar o projeto #{projeto_id}"
                )
        
        return await f(*args, **kwargs)
    
    return wrapper


class ProjectValidator:
    """
    Classe com métodos estáticos para validações de projeto
    """
    
    @staticmethod
    def verificar_projeto_id(projeto_id: Optional[int]) -> int:
        """
        Verifica se projeto_id é válido
        
        Args:
            projeto_id: ID do projeto a validar
            
        Returns:
            projeto_id validado
            
        Raises:
            ProjetoNaoSelecionadoException: Se projeto_id for None/0
            ValueError: Se projeto_id for inválido
        """
        if not projeto_id:
            raise ProjetoNaoSelecionadoException()
        
        try:
            projeto_id = int(projeto_id)
            if projeto_id <= 0:
                raise ValueError("ID deve ser positivo")
            return projeto_id
        except (TypeError, ValueError):
            raise ProjetoNaoSelecionadoException(
                detail="❌ ID do projeto inválido"
            )
    
    @staticmethod
    def projeto_existe(projeto_id: int) -> bool:
        """
        Verifica se projeto existe no banco
        
        Args:
            projeto_id: ID do projeto
            
        Returns:
            True se existe, False caso contrário
        """
        db = DatabaseHelper()
        resultado = db.execute_query(
            "SELECT 1 FROM projetos WHERE id = %s LIMIT 1",
            (projeto_id,),
            fetch=True
        )
        return bool(resultado)
    
    @staticmethod
    def usuario_acesso_projeto(user_id: int, projeto_id: int, is_admin: bool = False) -> bool:
        """
        Verifica se usuário tem acesso ao projeto
        
        Args:
            user_id: ID do usuário
            projeto_id: ID do projeto
            is_admin: True se usuário é admin
            
        Returns:
            True se tem acesso, False caso contrário
        """
        if is_admin:
            return True
        
        from middleware.permissions import permission_manager
        return permission_manager.is_project_member(user_id, projeto_id)
