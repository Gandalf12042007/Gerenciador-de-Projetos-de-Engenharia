import random
import string
from repositories.project_repository import ProjectRepository


def generate_project_code(length: int = 4) -> str:
    """Gera um código alfanumérico único de tamanho `length` para projeto.

    O código é recriado em loop caso já exista no banco.
    """
    repo = ProjectRepository()
    charset = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(random.choices(charset, k=length))
        if not repo.exists_code(code):
            return code
