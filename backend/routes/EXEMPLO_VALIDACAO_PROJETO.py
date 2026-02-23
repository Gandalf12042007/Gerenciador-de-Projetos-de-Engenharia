"""
EXEMPLO DE IMPLEMENTAÇÃO - Validação de Projeto Selecionado

Este arquivo mostra como usar o novo sistema de validação de projetos
em diferentes tipos de rotas e casos de uso.
"""

# ============= EXEMPLO 1: Endpoint com decoradores =============

from fastapi import APIRouter, Depends, HTTPException, status
from utils.project_validator import validar_projeto_selecionado, validar_projeto_existe, verificar_acesso_projeto
from exceptions.project_exceptions import ProjetoNaoSelecionadoException, ProjetoInvalidoException
from middleware.auth_middleware import get_current_active_user

router = APIRouter(prefix="/exemplo", tags=["Exemplos"])


@router.get("/minhas-tarefas/{projeto_id}")
@validar_projeto_selecionado  # ✓ Se projeto_id não for fornecido ou for inválido
@validar_projeto_existe        # ✓ Se projeto não existir no BD
@verificar_acesso_projeto      # ✓ Se usuário não tiver acesso
async def listar_tarefas_projeto(
    projeto_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Lista tarefas do projeto do usuário.
    
    Se qualquer validação falhar, uma exceção é lançada automaticamente.
    """
    # Aqui temos garantia de:
    # - projeto_id é um inteiro válido
    # - projeto existe no banco de dados
    # - usuário tem acesso ao projeto
    
    db = DatabaseHelper()
    tarefas = db.execute_query(
        """
        SELECT id, titulo, descricao FROM tarefas 
        WHERE projeto_id = %s
        """,
        (projeto_id,),
        fetch=True
    )
    
    return {"data": tarefas, "projeto_id": projeto_id}


# ============= EXEMPLO 2: Validação manual =============

from utils.project_validator import ProjectValidator
from exceptions.project_exceptions import ProjetoAcessoNegadoException

@router.post("/criar-documento/{projeto_id}")
async def criar_documento(
    projeto_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Cria um novo documento no projeto.
    Valida o projeto_id manualmente.
    """
    try:
        # Passo 1: Validar se projeto_id é válido
        projeto_id = ProjectValidator.verificar_projeto_id(projeto_id)
        
        # Passo 2: Validar se projeto existe
        if not ProjectValidator.projeto_existe(projeto_id):
            raise ProjetoInvalidoException()
        
        # Passo 3: Validar se usuário tem acesso
        user_id = current_user.get("id") or current_user.get("user_id")
        is_admin = current_user.get("is_admin", False)
        
        if not ProjectValidator.usuario_acesso_projeto(user_id, projeto_id, is_admin):
            raise ProjetoAcessoNegadoException()
        
        # Passo 4: Criar documento
        # ... código de criação ...
        
        return {"status": "sucesso", "projeto_id": projeto_id}
        
    except ProjetoNaoSelecionadoException:
        raise  # Re-lança a exceção (FastAPI cuidará do HTTP)
    except ProjetoInvalidoException:
        raise
    except ProjetoAcessoNegadoException:
        raise


# ============= EXEMPLO 3: Query parameter =============

@router.get("/relatorio")
async def gerar_relatorio(
    projeto_id: int = None,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Gera relatório do projeto.
    Valida através de query parameter.
    """
    if not projeto_id:
        raise ProjetoNaoSelecionadoException(
            detail="❌ Parâmetro 'projeto_id' é obrigatório. Use /relatorio?projeto_id=123"
        )
    
    # Validar se existe e se tem acesso
    if not ProjectValidator.projeto_existe(projeto_id):
        raise ProjetoInvalidoException()
    
    user_id = current_user.get("id") or current_user.get("user_id")
    is_admin = current_user.get("is_admin", False)
    
    if not ProjectValidator.usuario_acesso_projeto(user_id, projeto_id, is_admin):
        raise ProjetoAcessoNegadoException()
    
    # Gerar relatório...
    return {"projeto_id": projeto_id, "dados": {}}


# ============= EXEMPLO 4: Tratamento customizado =============

from fastapi.responses import JSONResponse

@router.get("/materiais/{projeto_id}")
async def listar_materiais(
    projeto_id: int = None,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Lista materiais do projeto com tratamento customizado de erros.
    """
    try:
        projeto_id = ProjectValidator.verificar_projeto_id(projeto_id)
        
        if not ProjectValidator.projeto_existe(projeto_id):
            return JSONResponse(
                status_code=404,
                content={
                    "erro": "Projeto não encontrado",
                    "codigo": "PROJETO_NAO_EXISTE",
                    "projeto_id": projeto_id
                }
            )
        
        user_id = current_user.get("id") or current_user.get("user_id")
        is_admin = current_user.get("is_admin", False)
        
        if not ProjectValidator.usuario_acesso_projeto(user_id, projeto_id, is_admin):
            return JSONResponse(
                status_code=403,
                content={
                    "erro": "Acesso ao projeto negado",
                    "codigo": "ACESSO_NEGADO",
                    "dica": "Você precisa ser membro do projeto para acessar seus materiais"
                }
            )
        
        # Continuar com lógica...
        materiais = []
        return {"projeto_id": projeto_id, "materiais": materiais}
        
    except ProjetoNaoSelecionadoException as e:
        return JSONResponse(
            status_code=400,
            content={
                "erro": str(e.detail),
                "codigo": "PROJETO_NAO_SELECIONADO",
                "dica": "Selecione um projeto antes de acessar seus materiais"
            }
        )


# ============= EXEMPLO 5: Dentro de função auxiliar =============

async def validar_e_retornar_projeto(projeto_id: Optional[int], user_id: int, is_admin: bool = False):
    """
    Função auxiliar para validar projeto em múltiplos endpoints.
    
    Returns:
        dict com dados do projeto ou lança exceção
    """
    # Validar
    try:
        projeto_id = ProjectValidator.verificar_projeto_id(projeto_id)
    except ProjetoNaoSelecionadoException:
        raise ProjetoNaoSelecionadoException(
            detail="❌ Projeto é obrigatório para esta operação"
        )
    
    if not ProjectValidator.projeto_existe(projeto_id):
        raise ProjetoInvalidoException(
            detail=f"❌ Projeto #{projeto_id} não existe"
        )
    
    if not ProjectValidator.usuario_acesso_projeto(user_id, projeto_id, is_admin):
        raise ProjetoAcessoNegadoException(
            detail=f"❌ Sem permissão para acessar projeto #{projeto_id}"
        )
    
    # Buscar dados do projeto
    db = DatabaseHelper()
    projeto = db.execute_query(
        "SELECT id, nome, status FROM projetos WHERE id = %s",
        (projeto_id,),
        fetch=True
    )
    
    return projeto[0] if projeto else None


@router.get("/tarefas-e-dados/{projeto_id}")
async def obter_tarefas_com_dados(
    projeto_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """Exemplo usando a função auxiliar"""
    
    user_id = current_user.get("id") or current_user.get("user_id")
    is_admin = current_user.get("is_admin", False)
    
    # Validar e obter projeto
    projeto = await validar_e_retornar_projeto(projeto_id, user_id, is_admin)
    
    # Agora uso projeto com segurança
    return {"projeto": projeto}


# ============= MENSAGENS DE ERRO NO CLIENTE =============

"""
RESPOSTAS HTTP que o cliente deve esperar:

1. Projeto não selecionado:
   HTTP 400 Bad Request
   {
     "detail": "❌ Nenhum projeto foi selecionado. Selecione um projeto para continuar."
   }
   Header: X-Error-Type: NO_PROJECT_SELECTED

2. Projeto inválido:
   HTTP 404 Not Found
   {
     "detail": "❌ Projeto #123 não foi encontrado..."
   }
   Header: X-Error-Type: INVALID_PROJECT

3. Acesso negado:
   HTTP 403 Forbidden
   {
     "detail": "❌ Você não tem permissão para acessar o projeto #123"
   }
   Header: X-Error-Type: PROJECT_ACCESS_DENIED

TRATAMENTO NO JAVASCRIPT:

async function buscarDadosProjeto(projectId) {
  try {
    const response = await fetch(`/api/tarefas/${projectId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      const error = await response.json();
      const errorType = response.headers.get('X-Error-Type');

      switch(errorType) {
        case 'NO_PROJECT_SELECTED':
          alert('Por favor, selecione um projeto primeiro!');
          window.location.href = '/projetos';
          break;
          
        case 'INVALID_PROJECT':
          alert('Projeto não encontrado. Talvez tenha sido deletado.');
          window.location.href = '/projetos';
          break;
          
        case 'PROJECT_ACCESS_DENIED':
          alert('Você não tem permissão para acessar este projeto.');
          window.location.href = '/projetos';
          break;
          
        default:
          console.error('Erro:', error.detail);
      }
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('Erro de rede:', error);
    alert('Erro ao buscar dados. Tente novamente.');
  }
}
"""
