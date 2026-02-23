"""
GUIA DE USO: Validação de Projeto Selecionado

Esta documentação explica como usar o sistema de validação e mensagens de erro
para o caso em que um usuário tenta acessar um recurso sem ter selecionado um projeto.

=== ARQUIVOS CRIADOS ===

1. backend/exceptions/project_exceptions.py
   - ProjetoNaoSelecionadoException: Levantada quando projeto_id não foi fornecido
   - ProjetoInvalidoException: Levantada quando projeto_id é inválido
   - ProjetoAcessoNegadoException: Levantada quando usuário não tem acesso

2. backend/utils/project_validator.py
   - Decoradores para validação automática
   - Classe ProjectValidator com métodos estáticos
   - Funções auxiliares

=== COMO USAR ===

1. EM ENDPOINTS (usando decoradores):

    from utils.project_validator import validar_projeto_selecionado, validar_projeto_existe, verificar_acesso_projeto

    @router.get("/tarefas/projeto/{projeto_id}")
    @validar_projeto_selecionado  # Valida se projeto_id foi fornecido
    @validar_projeto_existe        # Valida se projeto existe
    @verificar_acesso_projeto      # Valida se usuário tem acesso
    async def listar_tarefas_projeto(
        projeto_id: int,
        current_user: dict = Depends(get_current_active_user)
    ):
        # Aqui projeto_id está validado e não pode ser None
        # E o usuário tem acesso garantido
        pass


2. MANUALMENTE (usando ProjectValidator):

    from utils.project_validator import ProjectValidator
    from exceptions.project_exceptions import ProjetoNaoSelecionadoException

    @router.get("/documentos/projeto/{projeto_id}")
    async def listar_documentos(
        projeto_id: int,
        current_user: dict = Depends(get_current_active_user)
    ):
        try:
            # Verificar se projeto_id é válido
            projeto_id = ProjectValidator.verificar_projeto_id(projeto_id)
            
            # Verificar se projeto existe
            if not ProjectValidator.projeto_existe(projeto_id):
                raise ProjetoInvalidoException()
            
            # Verificar se usuário tem acesso
            user_id = current_user.get("id") or current_user.get("user_id")
            is_admin = current_user.get("is_admin", False)
            
            if not ProjectValidator.usuario_acesso_projeto(user_id, projeto_id, is_admin):
                raise ProjetoAcessoNegadoException()
            
            # Prosseguir com lógica
            ...
            
        except ProjetoNaoSelecionadoException as e:
            raise e

=== MENSAGENS DE ERRO ===

Nenhum projeto selecionado:
  Status: 400 BAD_REQUEST
  Mensagem: "❌ Nenhum projeto foi selecionado. Selecione um projeto para continuar."
  Header: X-Error-Type: NO_PROJECT_SELECTED

Projeto inválido:
  Status: 404 NOT_FOUND
  Mensagem: "❌ Projeto #ID não foi encontrado..."
  Header: X-Error-Type: INVALID_PROJECT

Acesso negado:
  Status: 403 FORBIDDEN
  Mensagem: "❌ Você não tem permissão para acessar o projeto #ID"
  Header: X-Error-Type: PROJECT_ACCESS_DENIED

=== NO FRONTEND ===

As respostas de erro podem ser tratadas assim:

async function buscarTarefas(projectId) {
  try {
    const response = await fetch(`/api/tarefas/projeto/${projectId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (!response.ok) {
      const error = await response.json();
      
      // Verificar tipo de erro
      const errorType = response.headers.get('X-Error-Type');
      
      if (errorType === 'NO_PROJECT_SELECTED') {
        mostrarMensagem('erro', 'Selecione um projeto primeiro!');
        redirectToProjectsList();
      } else if (errorType === 'INVALID_PROJECT') {
        mostrarMensagem('erro', 'Projeto não encontrado!');
      } else if (errorType === 'PROJECT_ACCESS_DENIED') {
        mostrarMensagem('erro', 'Você não tem acesso a este projeto');
      }
      
      return;
    }
    
    // Processar dados...
  } catch (error) {
    console.error('Erro:', error);
  }
}

=== EXEMPLO COMPLETO DE INTEGRAÇÃO ===

Ver: backend/routes/tarefas.py (rota atualizada como exemplo)

ANTES:
    if not permission_manager.is_project_member(user_id, projeto_id):
        raise HTTPException(status_code=403, detail="Acesso negado")

DEPOIS:
    @validar_projeto_selecionado
    @validar_projeto_existe
    @verificar_acesso_projeto
    async def listar_tarefas_projeto(...):
        # Tudo já foi validado!

=== BENEFÍCIOS ===

✓ Mensagens de erro consistentes em toda a aplicação
✓ Menos código duplicado
✓ Fácil manutenção
✓ Headers customizados para melhor tratamento no frontend
✓ Emojis nas mensagens para melhor UX
✓ Validações claras e reutilizáveis
"""

# Exemplo de resposta de erro da API:
EXEMPLO_RESPOSTA_ERRO = {
    "detail": "❌ Nenhum projeto foi selecionado. Selecione um projeto para continuar.",
    "status_code": 400,
    "error_type": "NO_PROJECT_SELECTED"
}
