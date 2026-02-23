# 📋 Tratamento de Erro: Projeto Não Selecionado

## 🎯 Objetivo

Criar uma mensagem de erro padrão e consistente quando um usuário tenta acessar um recurso que requer um projeto selecionado, mas não o fez.

## 📁 Arquivos Criados

### 1. `backend/exceptions/project_exceptions.py`
Define 3 exceções customizadas para diferentes cenários:
- **ProjetoNaoSelecionadoException** (400) - Usuário não selecionou projeto
- **ProjetoInvalidoException** (404) - Projeto não existe ou ID inválido  
- **ProjetoAcessoNegadoException** (403) - Usuário não tem acesso

### 2. `backend/utils/project_validator.py`
Contém decoradores e classe utilitária para validação:
- Decorador `@validar_projeto_selecionado`
- Decorador `@validar_projeto_existe`
- Decorador `@verificar_acesso_projeto`
- Classe `ProjectValidator` com métodos estáticos

### 3. `backend/VALIDACAO_PROJETO.md`
Documentação completa sobre como usar o sistema

### 4. `backend/routes/EXEMPLO_VALIDACAO_PROJETO.py`
Exemplos práticos de 5 formas diferentes de usar

## 🚀 Integração Rápida (3 passos)

### Passo 1: Importe as exceções
```python
from exceptions.project_exceptions import (
    ProjetoNaoSelecionadoException,
    ProjetoInvalidoException,
    ProjetoAcessoNegadoException
)
```

### Passo 2: Use em seus endpoints
**Opção A - Com decoradores (recomendado):**
```python
from utils.project_validator import (
    validar_projeto_selecionado,
    validar_projeto_existe,
    verificar_acesso_projeto
)

@router.get("/tarefas/{projeto_id}")
@validar_projeto_selecionado
@validar_projeto_existe
@verificar_acesso_projeto
async def listar_tarefas(projeto_id: int, current_user: dict = Depends(get_current_active_user)):
    # projeto_id já foi validado!
    pass
```

**Opção B - Manualmente:**
```python
from utils.project_validator import ProjectValidator

@router.get("/tarefas/{projeto_id}")
async def listar_tarefas(projeto_id: int, current_user: dict = Depends(get_current_active_user)):
    # Validar
    projeto_id = ProjectValidator.verificar_projeto_id(projeto_id)
    if not ProjectValidator.projeto_existe(projeto_id):
        raise ProjetoInvalidoException()
    # ... etc
```

### Passo 3: Teste
```bash
# Sem projeto_id
curl http://localhost:8000/api/tarefas/null
# Resposta: "❌ Nenhum projeto foi selecionado..."

# Com projeto_id inválido
curl http://localhost:8000/api/tarefas/999
# Resposta: "❌ Projeto #999 não foi encontrado..."
```

## 📱 Mensagens de Erro

### 1️⃣ Nenhum Projeto Selecionado
```json
{
  "detail": "❌ Nenhum projeto foi selecionado. Selecione um projeto para continuar.",
  "status_code": 400
}
```
**Header:** `X-Error-Type: NO_PROJECT_SELECTED`

### 2️⃣ Projeto Inválido
```json
{
  "detail": "❌ Projeto #999 não foi encontrado. Verifique se o ID está correto ou se o projeto foi deletado.",
  "status_code": 404
}
```
**Header:** `X-Error-Type: INVALID_PROJECT`

### 3️⃣ Acesso Negado
```json
{
  "detail": "❌ Você não tem permissão para acessar o projeto #123",
  "status_code": 403
}
```
**Header:** `X-Error-Type: PROJECT_ACCESS_DENIED`

## 🖥️ Tratamento no Frontend

```javascript
async function loadProject(projectId) {
  try {
    const response = await fetch(`/api/tarefas/${projectId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (!response.ok) {
      const errorType = response.headers.get('X-Error-Type');
      const error = await response.json();

      if (errorType === 'NO_PROJECT_SELECTED') {
        showError('Selecione um projeto primeiro!');
        redirectToProjects();
      } else if (errorType === 'INVALID_PROJECT') {
        showError('Projeto não encontrado!');
      } else if (errorType === 'PROJECT_ACCESS_DENIED') {
        showError('Você não tem acesso a este projeto!');
      }
      return;
    }

    // Carregar dados...
  } catch (error) {
    console.error('Erro:', error);
  }
}
```

## 🔧 Integrando em Rotas Existentes

### Antes:
```python
@router.get("/tarefas/{projeto_id}")
async def listar_tarefas(projeto_id: int, current_user: dict = Depends(get_current_active_user)):
    if not permission_manager.is_project_member(user_id, projeto_id):
        raise HTTPException(status_code=403, detail="Acesso negado")
    # ... resto do código
```

### Depois:
```python
from utils.project_validator import validar_projeto_selecionado, validar_projeto_existe, verificar_acesso_projeto

@router.get("/tarefas/{projeto_id}")
@validar_projeto_selecionado
@validar_projeto_existe
@verificar_acesso_projeto
async def listar_tarefas(projeto_id: int, current_user: dict = Depends(get_current_active_user)):
    # ... resto do código (tudo já foi validado!)
```

## 📚 Rotas para Atualizar

Recomendo aplicar em:
- `routes/tarefas.py` - GET/POST com projeto_id
- `routes/documentos.py` - GET/POST com projeto_id
- `routes/materiais.py` - GET/POST com projeto_id
- `routes/equipes.py` - GET/POST com projeto_id
- `routes/orcamentos.py` - GET/POST com projeto_id
- `routes/metricas.py` - GET com projeto_id

## ✅ Checklist de Implementação

- [ ] Revisar `project_exceptions.py`
- [ ] Revisar `project_validator.py`
- [ ] Ler exemplos em `EXEMPLO_VALIDACAO_PROJETO.py`
- [ ] Adicionar decoradores a 1-2 endpoints como teste
- [ ] Testar com cliente (curl, Postman ou navegador)
- [ ] Atualizar código do cliente para tratar erros
- [ ] Adicionar aos outros endpoints gradualmente

## 🎨 Benefícios

✅ Mensagens consistentes em toda a API  
✅ Menos código duplicado  
✅ Fácil manutenção (mudar mensagem em 1 lugar)  
✅ Validações reutilizáveis  
✅ Headers customizados para melhor tratamento  
✅ Emojis nas mensagens para melhor UX  
✅ Documentação clara

## 🤝 Suporte

Para dúvidas sobre uso:
1. Ver `VALIDACAO_PROJETO.md`
2. Ver exemplos em `EXEMPLO_VALIDACAO_PROJETO.py`
3. Ver implementação em `project_exceptions.py` e `project_validator.py`
