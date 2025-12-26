"""
Decoradores de Permissão - FastAPI
Protege rotas com verificação de acesso
Desenvolvido por: Vicente de Souza
"""

from functools import wraps
from fastapi import HTTPException, status, Depends
from typing import Callable
from utils.auth import get_current_user
from middleware.permissions import permission_manager


def require_project_member(func: Callable) -> Callable:
    """
    Decorador: Requer que usuário seja membro do projeto
    Uso: @require_project_member
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extrair projeto_id dos kwargs ou path params
        project_id = kwargs.get('projeto_id') or kwargs.get('id')
        current_user = kwargs.get('current_user')
        
        if not current_user or 'id' not in current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não autenticado"
            )
        
        if not project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID do projeto não fornecido"
            )
        
        # Verificar se é membro
        if not permission_manager.is_project_member(current_user['id'], project_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não é membro deste projeto"
            )
        
        return await func(*args, **kwargs)
    
    return wrapper


def require_project_manager(func: Callable) -> Callable:
    """
    Decorador: Requer que usuário seja gerente do projeto
    Uso: @require_project_manager
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        project_id = kwargs.get('projeto_id') or kwargs.get('id')
        current_user = kwargs.get('current_user')
        
        if not current_user or 'id' not in current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não autenticado"
            )
        
        if not project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID do projeto não fornecido"
            )
        
        # Verificar se é gerente ou dono
        if not permission_manager.can_modify_project(current_user['id'], project_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas gerentes podem realizar esta ação"
            )
        
        return await func(*args, **kwargs)
    
    return wrapper


def require_project_owner(func: Callable) -> Callable:
    """
    Decorador: Requer que usuário seja criador do projeto
    Uso: @require_project_owner
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        project_id = kwargs.get('projeto_id') or kwargs.get('id')
        current_user = kwargs.get('current_user')
        
        if not current_user or 'id' not in current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não autenticado"
            )
        
        if not project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID do projeto não fornecido"
            )
        
        # Verificar se é dono
        if not permission_manager.is_project_owner(current_user['id'], project_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas o criador do projeto pode realizar esta ação"
            )
        
        return await func(*args, **kwargs)
    
    return wrapper


def require_role(min_role: str):
    """
    Decorador parametrizado: Requer papel mínimo
    Uso: @require_role("engenheiro")
    
    Args:
        min_role: Papel mínimo (gerente, engenheiro, tecnico, colaborador)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            project_id = kwargs.get('projeto_id') or kwargs.get('id')
            current_user = kwargs.get('current_user')
            
            if not current_user or 'id' not in current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuário não autenticado"
                )
            
            if not project_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ID do projeto não fornecido"
                )
            
            # Verificar permissão
            if not permission_manager.has_permission(
                current_user['id'], 
                project_id, 
                min_role
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Você precisa ser pelo menos '{min_role}' para esta ação"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# Funções auxiliares para dependency injection no FastAPI
async def verify_project_access(
    projeto_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Dependency: Verifica acesso ao projeto
    Uso em rota: projeto_access: None = Depends(verify_project_access)
    """
    if not permission_manager.is_project_member(current_user['id'], projeto_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem acesso a este projeto"
        )
    return True


async def verify_project_modify(
    projeto_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Dependency: Verifica permissão para modificar projeto
    """
    if not permission_manager.can_modify_project(current_user['id'], projeto_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para modificar este projeto"
        )
    return True


async def verify_project_delete(
    projeto_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Dependency: Verifica permissão para deletar projeto
    """
    if not permission_manager.can_delete_project(current_user['id'], projeto_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o criador pode deletar o projeto"
        )
    return True
