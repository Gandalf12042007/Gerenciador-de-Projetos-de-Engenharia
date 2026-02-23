"""
Exceções customizadas relacionadas a Projetos
"""

from fastapi import HTTPException, status


class ProjetoNaoSelecionadoException(HTTPException):
    """
    Exceção levantada quando usuário tenta acessar um recurso
    que requer um projeto selecionado sem ter fornecido o projeto_id
    """
    def __init__(
        self,
        detail: str = "Nenhum projeto foi selecionado. Selecione um projeto para continuar.",
        headers: dict = None
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            headers=headers or {"X-Error-Type": "NO_PROJECT_SELECTED"}
        )


class ProjetoInvalidoException(HTTPException):
    """
    Exceção levantada quando o projeto_id fornecido é inválido
    """
    def __init__(
        self,
        detail: str = "Projeto não encontrado ou inválido",
        headers: dict = None
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            headers=headers or {"X-Error-Type": "INVALID_PROJECT"}
        )


class ProjetoAcessoNegadoException(HTTPException):
    """
    Exceção levantada quando usuário não tem acesso ao projeto
    """
    def __init__(
        self,
        detail: str = "Você não tem permissão para acessar este projeto",
        headers: dict = None
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            headers=headers or {"X-Error-Type": "PROJECT_ACCESS_DENIED"}
        )
