# 📋 TAREFAS PENDENTES - Francisco (Frontend)

**Data:** 08 de Dezembro de 2025  
**Responsável:** Francisco  
**Status:** 🔴 URGENTE - Trabalho crítico para conclusão do projeto

---

## ⚠️ IMPORTANTE

Vicente já finalizou **100% do Backend** (32 endpoints funcionando). O sistema está **bloqueado** esperando você completar o frontend. Sem as telas, não conseguimos testar o sistema completo nem entregar o projeto.

**PRAZO SUGERIDO:** 10-12 dias trabalhando em paralelo

---

## 🎨 FASE 1: DESIGN (2 dias) - PRIORIDADE MÁXIMA

### Task #3: Criar Protótipo no Figma

**Status:** ❌ NÃO INICIADO  
**Tempo estimado:** 2 dias  
**Bloqueador:** SIM - Frontend depende disso

#### O que fazer:

1. **Criar Design System**
   - [ ] Definir paleta de cores (sugestão: azul/cinza engenharia)
   - [ ] Escolher tipografia (fonte principal + secundária)
   - [ ] Criar componentes reutilizáveis:
     - [ ] Botões (primary, secondary, danger)
     - [ ] Cards de projeto
     - [ ] Formulários e inputs
     - [ ] Tabelas
     - [ ] Modais
     - [ ] Sidebar/Menu lateral
     - [ ] Header com perfil de usuário

2. **Prototipar 10 Telas Principais**
   
   #### Tela 1: Registro (register.html)
   - Form com: Nome, Email, Senha, Confirmar Senha, Cargo
   - Validações visuais
   - Link "Já tem conta? Faça login"
   
   #### Tela 2: Perfil do Usuário (profile.html)
   - Foto de perfil (upload)
   - Formulário editável: Nome, Cargo, Telefone, Bio
   - Informações read-only: Email, Data de cadastro
   - Botões: Salvar, Alterar Senha, Excluir Conta
   
   #### Tela 3: Dashboard Melhorado (projects/index.html)
   - Cards de projeto maiores e mais informativos
   - Barra de progresso visual
   - Filtros por status
   - Gráficos de métricas (opcional)
   
   #### Tela 4: Kanban de Tarefas (tasks.html)
   - 3 colunas: A Fazer | Em Execução | Concluídas
   - Cards arrastáveis (drag & drop)
   - Modal para criar/editar tarefa
   - Filtros por responsável e prioridade
   
   #### Tela 5: Equipe (team.html)
   - Lista de membros com foto e papel
   - Permissões configuráveis
   - Botão "Convidar membro"
   - Destaque do engenheiro responsável
   
   #### Tela 6: Documentos (documents.html)
   - Upload de arquivos (drag & drop)
   - Lista com categorias (Plantas, RRT, Fotos, etc.)
   - Download e visualização
   - Versionamento de documentos
   
   #### Tela 7: Materiais (materials.html)
   - Tabela de materiais com estoque
   - Botões: Adicionar Material, Registrar Uso
   - Indicador visual de estoque baixo
   - Total em estoque (R$)
   
   #### Tela 8: Orçamento (budget.html)
   - Tabela de itens orçamentários
   - Gráfico: Previsto vs Gasto
   - Botão: Adicionar Item, Registrar Pagamento
   - Resumo financeiro no topo
   
   #### Tela 9: Relatórios (reports.html)
   - Dashboard com métricas do projeto
   - Gráficos de produtividade
   - Timeline de atividades
   - Botão "Exportar PDF"
   
   #### Tela 10: Chat (chat.html)
   - Lista de mensagens em ordem cronológica
   - Input para nova mensagem
   - Lista de participantes
   - Busca de mensagens

**Entrega:** Arquivo .fig ou link do Figma compartilhado

---

## 💻 FASE 2: IMPLEMENTAÇÃO (8-10 dias)

### Task #6: Criar Primeira Tela (register.html)

**Status:** ❌ NÃO INICIADO  
**Tempo estimado:** 1 dia

#### Estrutura do arquivo:
```
web/
├── register.html          ← CRIAR ESTE
├── login.html            ← JÁ EXISTE (usar como base)
├── api-client.js         ← JÁ EXISTE (usar para chamadas API)
└── projects/
    └── index.html        ← JÁ EXISTE (ver estrutura)
```

#### API Disponível para usar:
- **POST /auth/register**
  ```javascript
  {
    "nome": "Francisco Silva",
    "email": "francisco@email.com",
    "senha": "senha123",
    "cargo": "Desenvolvedor Frontend"
  }
  ```

#### Exemplo de integração:
```javascript
// Ver web/projects/app.js para referência
async function registrar(dados) {
    const response = await fetch('http://localhost:8000/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados)
    });
    return await response.json();
}
```

---

### Tarefas Restantes (criar uma por uma):

#### 2. profile.html (1 dia)
- **API disponível:** GET/PUT /auth/me
- Layout de perfil com formulário editável
- Upload de foto (usar /documentos/upload)

#### 3. Melhorar projects/index.html (1 dia)
- **API disponível:** GET /projetos, GET /metricas/{id}/dashboard
- Adicionar mais métricas visuais
- Melhorar cards de projeto

#### 4. tasks.html - Kanban (2 dias)
- **APIs disponíveis:** 
  - GET /tarefas/{projeto_id}
  - POST /tarefas/{projeto_id}
  - PUT /tarefas/{tarefa_id}
- Implementar drag & drop entre colunas
- Modals para criar/editar

#### 5. team.html (1 dia)
- **API disponível:** GET/POST/PUT/DELETE /equipes/{projeto_id}
- Lista de membros
- Gerenciar permissões

#### 6. documents.html (1-2 dias)
- **APIs disponíveis:**
  - GET /documentos/{projeto_id}
  - POST /documentos/{projeto_id}/upload
  - GET /documentos/{id}/versoes
- Upload com drag & drop
- Download de arquivos

#### 7. materials.html (1 dia)
- **APIs disponíveis:** GET/POST/PUT/DELETE /materiais/{projeto_id}
- Tabela de materiais
- Registrar entrada/saída

#### 8. budget.html (1 dia)
- **APIs disponíveis:** GET/POST/PUT /orcamentos/{projeto_id}
- Tabela de orçamento
- Gráficos financeiros

#### 9. reports.html (1 dia)
- **API disponível:** GET /metricas/{projeto_id}/relatorio-completo
- Exibir métricas
- Gráficos com Chart.js

#### 10. chat.html (1 dia)
- **APIs disponíveis:** 
  - GET /chat/{projeto_id}/mensagens
  - POST /chat/{projeto_id}/mensagens
- Interface de chat simples
- Lista de mensagens

---

## 📚 RECURSOS PARA AJUDAR

### Documentação da API
- **Swagger:** http://localhost:8000/docs
- **Total de endpoints:** 32 (todos funcionando)

### Arquivos para usar como referência:
1. `web/login.html` - Estrutura HTML básica
2. `web/projects/app.js` - Como fazer chamadas API
3. `web/api-client.js` - Cliente HTTP reutilizável

### Tecnologias que você vai usar:
- **HTML5** - Estrutura das páginas
- **CSS3** - Estilização (pode usar framework como Bootstrap/Tailwind)
- **JavaScript Vanilla** - Lógica e integração com API
- **Fetch API** - Requisições HTTP
- **localStorage** - Armazenar token JWT

### Bibliotecas sugeridas (opcional):
- **Chart.js** - Para gráficos em relatórios
- **SortableJS** - Para drag & drop no Kanban
- **Bootstrap 5** ou **Tailwind CSS** - Framework CSS

---

## 🎯 PRIORIDADES

### CRÍTICO (fazer primeiro):
1. ✅ Figma completo (#3)
2. ✅ register.html (#6)
3. ✅ tasks.html (Kanban)
4. ✅ documents.html

### IMPORTANTE (fazer depois):
5. ⚠️ profile.html
6. ⚠️ team.html
7. ⚠️ materials.html
8. ⚠️ budget.html

### DESEJÁVEL (se der tempo):
9. 📊 reports.html
10. 💬 chat.html

---

## ✅ CHECKLIST DIÁRIO

**Dia 1-2:** Design no Figma  
- [ ] Design System completo
- [ ] 10 telas prototipadas
- [ ] Compartilhar link com Vicente

**Dia 3:** register.html  
- [ ] HTML estruturado
- [ ] CSS estilizado
- [ ] Integração com API
- [ ] Validações funcionando
- [ ] Testar cadastro completo

**Dia 4-5:** tasks.html (Kanban)  
- [ ] Layout de 3 colunas
- [ ] Cards de tarefas
- [ ] Drag & drop funcionando
- [ ] Modal de criar/editar
- [ ] Integração com API

**Dia 6:** documents.html  
- [ ] Upload de arquivos
- [ ] Lista de documentos
- [ ] Download funcionando
- [ ] Categorização

**Dia 7:** profile.html + team.html  
- [ ] Tela de perfil completa
- [ ] Tela de equipe completa

**Dia 8:** materials.html + budget.html  
- [ ] Gerenciamento de materiais
- [ ] Controle orçamentário

**Dia 9-10:** reports.html + chat.html  
- [ ] Relatórios com gráficos
- [ ] Chat funcional

---

## 🆘 AJUDA E SUPORTE

### Quando tiver dúvidas:

1. **Consultar documentação:** http://localhost:8000/docs
2. **Ver código existente:** `web/projects/app.js`
3. **Testar APIs:** Use Swagger ou Postman
4. **Pedir ajuda:** Chamar Vicente no chat do projeto

### Comandos úteis:

```bash
# Iniciar sistema completo
.\start-sistema.bat

# Backend roda em: http://localhost:8000
# Frontend roda em: http://localhost:3000
```

---

## 🎉 RESULTADO ESPERADO

Ao final, o sistema terá:
- ✅ **Backend completo** (32 APIs) - Vicente ✅
- ✅ **Database completo** (18 tabelas) - Vicente ✅
- ✅ **Frontend completo** (10 páginas) - Francisco ⏳
- ✅ **Sistema 100% funcional** - Ambos 🎯

**Bom trabalho! Qualquer dúvida, é só chamar!** 🚀

---

_Documento criado por Vicente de Souza - 08/12/2025_
