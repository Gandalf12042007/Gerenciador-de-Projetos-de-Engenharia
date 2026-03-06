# 🔍 DIAGNÓSTICO COMPLETO - FASE 1

## 📊 MAPA DE ROTAS BACKEND

### ✅ Endpoints Disponíveis no Backend:
```
/api/auth/login          - POST (Autenticação)
/api/projetos/           - GET, POST, PUT, DELETE
/api/projetos/{id}       - GET
/api/tarefas/            - GET, POST, PUT, DELETE
/api/tarefas/projeto/{id} - GET (tarefas por projeto)
/api/documentos/         - GET, POST, PUT, DELETE
/api/equipes/            - GET, POST, PUT, DELETE
... (+ outros endpoints)
```

## ❌ PROBLEMAS ENCONTRADOS NO FRONTEND

### 1. **ERRO CRÍTICO: dashboard.js - URLs SEM /api**

**Arquivo:** `web/projects/dashboard.js`

**Linhas com problema:**
- Linha 77: `const projectsResponse = await api.get('/projetos/');`
  - ❌ Envia para: `http://localhost:8000/projetos/` (404 Not Found)
  - ✅ Deveria ser: `http://localhost:8000/api/projetos/`

- Linha 86: `const projectTasks = await api.get(`/tarefas/projeto/${project.id}`);`
  - ❌ Envia para: `http://localhost:8000/tarefas/projeto/1` (404 Not Found)
  - ✅ Deveria ser: `http://localhost:8000/api/tarefas/projeto/1`

**SOLUÇÃO:** Adicionar `/api` antes dos endpoints

---

### 2. **BOTÕES DE CRIAÇÃO NÃO FUNCIONAM**

**Arquivo:** `web/projects/app.js`

**Problema:** Botões de criar projetos/tarefas não têm handlers ou os handlers estão chamando a função errada
- Botão "Novo Projeto" → ID: `#newProjectBtn`
- Botão "Criar Tarefa" → Não encontrado
- Modal de Criação → Precisa ser implementado

**Status:** ❌ Não implementado ou com evento faltando

---

### 3. **INTERFACES DESORGANIZADAS**

**Problema Visual:** 
- CSS não responsivo
- Layout quebrado em mobile
- Cards mal dimensionados
- Botões fora do lugar

**Arquivo:** `web/projects/global.css`, `web/projects/dashboard.css`

**Status:** ⚠️ Precisa de reorganização visual

---

## 📋 CHECKLIST DE CORREÇÕES NECESSÁRIAS

### FASE 2: Corrigir Erro Crítico (Dashboard)
- [ ] Corrigir URL `/projetos/` → `/api/projetos/`
- [ ] Corrigir URL `/tarefas/projeto/` → `/api/tarefas/projeto/`
- [ ] Testar se dashboard carrega dados corretamente
- [ ] Verificar console do navegador para outros erros

### FASE 3: Reviver Botões Mortos
- [ ] Localizar TODOS os botões que devem ter listeners
- [ ] Implementar handlers para:
  - Criar Projeto
  - Criar Tarefa
  - Editar Projeto/Tarefa
  - Deletar Projeto/Tarefa
- [ ] Testar cada botão

### FASE 4: Checkup Geral
- [ ] Revisar imports (estão faltando?)
- [ ] Verificar chamadas não-API
- [ ] Validar formatos de dados
- [ ] Testes de fluxo completo

### FASE 5: Design Jira-like
- [ ] Criar novo CSS com estilo profissional
- [ ] Implementar Quadro Kanban
- [ ] Redesenhar Dashboard
- [ ] Adicionar Sidebar melhorado

---

## 🎯 PRÓXIMO PASSO

Vou começar a corrigir imediatamente os erros encontrados!
