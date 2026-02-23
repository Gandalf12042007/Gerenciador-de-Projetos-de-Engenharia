# ✅ Sistema Completo: Tratamento de Erro "Projeto Não Selecionado"

## 📦 O que foi criado

Um sistema completo e pronto para usar que fornece mensagens de erro padronizadas quando um usuário tenta acessar um recurso que requer ter um projeto selecionado sem o fazer.

---

## 📁 Arquivos Criados

### Backend

| Arquivo | Descrição | Localização |
|---------|-----------|-----------|
| `project_exceptions.py` | 3 exceções customizadas (400, 404, 403) | `backend/exceptions/` |
| `project_validator.py` | Decoradores e classe de validação | `backend/utils/` |
| `VALIDACAO_PROJETO.md` | Documentação detalhada de uso | `backend/` |
| `ERRO_PROJETO_NAO_SELECIONADO.md` | Guia rápido de integração | `backend/` |
| `EXEMPLO_VALIDACAO_PROJETO.py` | 5 exemplos de implementação | `backend/routes/` |
| `test_project_validation.py` | Testes unitários e de integração | `backend/tests/` |

### Frontend

| Arquivo | Descrição | Localização |
|---------|-----------|-----------|
| `TRATAMENTO_ERRO_PROJETO.js` | Classe e utilitários JS para tratar erros | `web/` |

---

## 🎯 Resumo da Solução

### Backend - 3 Exceções Customizadas

```python
# Nenhum projeto selecionado
ProjetoNaoSelecionadoException(400)
# → "❌ Nenhum projeto foi selecionado..."
# → Header: X-Error-Type: NO_PROJECT_SELECTED

# Projeto não existe
ProjetoInvalidoException(404)
# → "❌ Projeto #999 não foi encontrado..."
# → Header: X-Error-Type: INVALID_PROJECT

# Usuário sem acesso
ProjetoAcessoNegadoException(403)
# → "❌ Você não tem permissão para acessar..."
# → Header: X-Error-Type: PROJECT_ACCESS_DENIED
```

### Backend - Decoradores Reutilizáveis

```python
@validar_projeto_selecionado  # Valida se projeto_id foi fornecido
@validar_projeto_existe        # Valida se projeto existe no BD
@verificar_acesso_projeto      # Valida se usuário tem acesso
```

### Frontend - Tratamento Automático

```javascript
class ProjectAPIError {
  handle() {
    // Trata automaticamente baseado no tipo de erro
    // Mostra notificação apropriada
    // Redireciona se necessário
  }
}
```

---

## 🚀 Como Usar

### Passo 1: Revisar os arquivos

Comece lendo em ordem:
1. `backend/ERRO_PROJETO_NAO_SELECIONADO.md` (visão geral)
2. `backend/routes/EXEMPLO_VALIDACAO_PROJETO.py` (5 exemplos)
3. `backend/exceptions/project_exceptions.py` (código das exceções)
4. `backend/utils/project_validator.py` (código dos validadores)

### Passo 2: Integrar em uma rota existente

**Antes:**
```python
@router.get("/tarefas/{projeto_id}")
async def listar_tarefas(projeto_id: int, current_user: dict = Depends(get_current_active_user)):
    if not permission_manager.is_project_member(user_id, projeto_id):
        raise HTTPException(status_code=403, detail="Acesso negado")
```

**Depois:**
```python
from utils.project_validator import validar_projeto_selecionado, validar_projeto_existe, verificar_acesso_projeto

@router.get("/tarefas/{projeto_id}")
@validar_projeto_selecionado
@validar_projeto_existe
@verificar_acesso_projeto
async def listar_tarefas(projeto_id: int, current_user: dict = Depends(get_current_active_user)):
    # Tudo já foi validado!
```

### Passo 3: Testar

```bash
# Teste com projeto_id inválido
curl http://localhost:8000/api/tarefas/null
# Resposta: 400 "Nenhum projeto foi selecionado"

# Teste com projeto inexistente
curl http://localhost:8000/api/tarefas/999
# Resposta: 404 "Projeto #999 não foi encontrado"
```

### Passo 4: Integrar no frontend

Copie o código de `web/TRATAMENTO_ERRO_PROJETO.js` para seu projeto e use:

```javascript
try {
  const tarefas = await API.Tarefas.listar(projectId);
} catch (error) {
  if (error instanceof ProjectAPIError) {
    error.handle(); // Trata automaticamente!
  }
}
```

---

## 📋 Checklist de Implementação

### Fase 1: Setup (30 min)
- [ ] Revisar `ERRO_PROJETO_NAO_SELECIONADO.md`
- [ ] Revisar `EXEMPLO_VALIDACAO_PROJETO.py`
- [ ] Entender as 3 exceções customizadas
- [ ] Entender os 3 decoradores

### Fase 2: Implementação Backend (2-3 horas)
- [ ] Adicionar imports em 1-2 rotas de teste
- [ ] Testar localmente com curl/Postman
- [ ] Adicionar gradualmente aos outros endpoints:
  - [ ] `routes/tarefas.py`
  - [ ] `routes/documentos.py`
  - [ ] `routes/materiais.py`
  - [ ] `routes/equipes.py`
  - [ ] `routes/orcamentos.py`

### Fase 3: Implementação Frontend (1-2 horas)
- [ ] Copiar classe `ProjectAPIError` para `web/api-client.js`
- [ ] Adicionar função `showNotification()`
- [ ] Testar com requisições reais
- [ ] Adicionar tratamento a todos os endpoints do cliente

### Fase 4: Testes (1 hora)
- [ ] Executar testes em `test_project_validation.py`
- [ ] Testar cenários com Postman
- [ ] Testar cenários no navegador
- [ ] Verificar mensagens de erro

### Fase 5: Documentação (30 min)
- [ ] Adicionar exemplos ao README
- [ ] Documentar mudanças no CHANGELOG
- [ ] Treinar equipe

**Tempo Total: 5-7 horas para implementação completa**

---

## 📊 Endpoints Prioritários para Atualizar

### Prioritário (usuários veem primeiro)
1. `GET /projetos/` - Listar projetos
2. `GET /tarefas/projeto/{projeto_id}` - Listar tarefas
3. `GET /documentos/projeto/{projeto_id}` - Listar documentos
4. `POST /tarefas` - Criar tarefa

### Importante
5. `GET /equipes/projeto/{projeto_id}` - Listar equipes
6. `GET /materiais/projeto/{projeto_id}` - Listar materiais
7. `GET /orcamentos/projeto/{projeto_id}` - Listar orçamentos
8. `GET /metricas/projeto/{projeto_id}` - Listar métricas

### Depois
- Todos os outros endpoints que usam `projeto_id`

---

## 💡 Exemplos de Mensagens

### Cenário 1: Usuário clica em "Tarefas" sem selecionar projeto
```
HTTP 400 Bad Request
{
  "detail": "❌ Nenhum projeto foi selecionado. Selecione um projeto para continuar."
}
Header: X-Error-Type: NO_PROJECT_SELECTED

→ Cliente mostra: "⚠️ Projeto Não Selecionado"
→ Redireciona para lista de projetos
```

### Cenário 2: Projeto foi deletado
```
HTTP 404 Not Found
{
  "detail": "❌ Projeto #1 não foi encontrado. Verifique se o ID está correto ou se o projeto foi deletado."
}
Header: X-Error-Type: INVALID_PROJECT

→ Cliente mostra: "❌ Projeto Não Encontrado"
→ Oferece voltar
```

### Cenário 3: Usuário não é membro
```
HTTP 403 Forbidden
{
  "detail": "❌ Você não tem permissão para acessar o projeto #5"
}
Header: X-Error-Type: PROJECT_ACCESS_DENIED

→ Cliente mostra: "🔒 Acesso Negado"
→ Bloqueia acesso
```

---

## 🔍 Testando Antes de Implementar

Faça um teste manual para entender como funciona:

```bash
# 1. Inicie o servidor
cd backend && python -m uvicorn app:app --reload

# 2. Em outro terminal, teste:

# Teste 1: Projeto não selecionado
curl -X GET "http://localhost:8000/api/tarefas/" \
  -H "Authorization: Bearer seu_token"

# Teste 2: Projeto inválido  
curl -X GET "http://localhost:8000/api/tarefas/999" \
  -H "Authorization: Bearer seu_token"

# Teste 3: Acesso negado (use token de outro usuário)
curl -X GET "http://localhost:8000/api/tarefas/1" \
  -H "Authorization: Bearer outro_token"
```

---

## 📝 Documentos de Referência

Leia nesta ordem:

1. **ERRO_PROJETO_NAO_SELECIONADO.md**
   - Visão geral da solução
   - Integração rápida
   - Mensagens de erro

2. **VALIDACAO_PROJETO.md**
   - Documentação técnica detalhada
   - Todos os cenários de uso
   - Exemplos de frontend

3. **EXEMPLO_VALIDACAO_PROJETO.py**
   - 5 formas diferentes de usar
   - Código pronto para copiar
   - Casos de uso reais

4. **backend/exceptions/project_exceptions.py**
   - Implementação das exceções
   - Headers customizados
   - Códigos HTTP

5. **backend/utils/project_validator.py**
   - Implementação dos validadores
   - Decoradores
   - Classe ProjectValidator

6. **web/TRATAMENTO_ERRO_PROJETO.js**
   - Cliente JavaScript para API
   - Classe de erro customizada
   - Exemplos de notificações

---

## 🎓 Conceitos-Chave

### 1. Exceções Customizadas vs HTTPException
```python
# ❌ Ruim: Genérico
raise HTTPException(status_code=400, detail="Erro")

# ✅ Bom: Específico e reutilizável
raise ProjetoNaoSelecionadoException()
```

### 2. Decoradores vs Validação Manual
```python
# ✅ Recomendado: Menos código, mais limpo
@validar_projeto_selecionado
@validar_projeto_existe
@verificar_acesso_projeto
async def minhaRota(...):
    pass

# ✓ Alternativa: Mais controle
validacao = ProjectValidator.verificar_projeto_id(projeto_id)
```

### 3. Headers Customizados
```python
# No servidor: Adicionar header com tipo de erro
headers={"X-Error-Type": "NO_PROJECT_SELECTED"}

# No cliente: Verificar header para saber tipo de erro
const errorType = response.headers.get('X-Error-Type')
```

---

## 🎯 Benefícios da Solução

✅ **Consistência**: Mesma mensagem em toda a API  
✅ **Manutenção**: Alterar mensagem em 1 lugar  
✅ **Reutilização**: Decoradores em múltiplos endpoints  
✅ **UX**: Emojis e mensagens claras  
✅ **Frontend**: Headers para tratamento específico  
✅ **Testes**: Fácil de testar com pytest  
✅ **Documentação**: Exemplos práticos inclusos  

---

## ❓ Dúvidas Frequentes

**P: Posso usar em todos os endpoints?**  
R: Sim! Use em qualquer endpoint que precise de `projeto_id`.

**P: Como saber qual decorador usar?**  
R: Use todos os 3: `@validar_projeto_selecionado` → `@validar_projeto_existe` → `@verificar_acesso_projeto`

**P: Preciso mudar o code frontend?**  
R: Não obrigatoriamente, mas é recomendado para melhor UX. Veja `TRATAMENTO_ERRO_PROJETO.js`.

**P: Como testar?**  
R: 3 formas:
1. curl (linha de comando)
2. Postman (interface gráfica)
3. pytest (testes automatizados)

**P: Posso customizar as mensagens?**  
R: Sim! Cada exceção aceita `detail` customizado.

---

## 🚀 Próximos Passos

1. ✅ Revisar este documento
2. ✅ Ler `ERRO_PROJETO_NAO_SELECIONADO.md`
3. ✅ Estudar exemplos em `EXEMPLO_VALIDACAO_PROJETO.py`
4. ✅ Implementar em 1-2 endpoints de teste
5. ✅ Testar e validar
6. ✅ Expandir para outros endpoints
7. ✅ Integrar no frontend
8. ✅ Testar cenários reais

---

## 📞 Suporte

Se tiver dúvidas:
1. Revise a documentação em `backend/VALIDACAO_PROJETO.md`
2. Veja exemplos em `backend/routes/EXEMPLO_VALIDACAO_PROJETO.py`
3. Estude a implementação em `backend/utils/project_validator.py`
4. Execute os testes em `backend/tests/test_project_validation.py`

**Você está pronto para implementar! 🚀**
