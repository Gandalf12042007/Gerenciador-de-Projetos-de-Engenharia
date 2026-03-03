# 🚀 GUIA RÁPIDO - SISTEMA PRONTO PARA USO

## ✅ Status Atual

- ✅ **Backend**: Rodando em `http://localhost:8000`
- ✅ **Login**: Funcionando corretamente
- ✅ **API**: Todos os endpoints respondendo
- ✅ **Projetos**: 2 projetos de teste carregados
- ✅ **Tarefas**: 28 tarefas distribuídas nos projetos
- ✅ **Dashboard**: Pronto para visualizar métricas

---

## 🎯 COMO USAR O SISTEMA

### 1️⃣ Acessar o Sistema

1. Abra seu navegador favorito
2. Acesse: **`http://localhost:8000/login`**

### 2️⃣ Fazer Login

Use uma destas contas:

**Administrador:**
- Email: `vicentedesouza762@gmail.com`
- Senha: `Admin@2026`

**Outros usuários:**
- Email: `francisco@projeto.com` | Senha: `Admin@2026`
- Email: `gerenteteste@projeto.com` | Senha: `Gerente@123`
- Email: `engenheiroteste@projeto.com` | Senha: `Engenheiro@123`
- Email: `tecnicoteste@projeto.com` | Senha: `Tecnico@123`

### 3️⃣ Após Login

- **Admin**: Acesso direto ao dashboard com métricas gerais
- **Outros**: Redirecionados para seleção de projeto

---

## 📊 DADOS DISPONÍVEIS

### Projetos
- ✅ **Prédio Comercial Centro** (ID: 13)
  - 4 tarefas
  - Valor: R$ 1.000.000
  
- ✅ **Residência Bairro Sul** (ID: 14)
  - 4 tarefas
  - Valor: R$ 500.000

### Tarefas
- Total: 28 tarefas
- Status: A fazer, Em andamento, Concluído, Atrasado
- Prioridades: Alta, Média, Baixa

### Equipes
- 21 membros vinculados aos projetos
- Papéis: Gerente, Engenheiro, Técnico

---

## 🛠️ OPERAÇÕES DISPONÍVEIS

### Dashboard (Admin)
- 📈 Visualizar resumo de projetos
- 📊 Gráficos de status
- 📋 Lista de tarefas atrasadas
- 👥 Progresso por responsável

### Gerenciamento de Projetos
- ✏️ Criar/editar projetos
- 👥 Adicionar membros à equipe
- 📝 Gerenciar tarefas

### Tarefas
- ✅ Marcar como concluída
- 🔄 Mudar status
- 📅 Atribuir responsáveis
- ⚠️ Definir prioridades

---

## 🧪 TESTES DISPONÍVEIS

### Teste Rápido
```bash
python test_simple.py
```
*Valida login e carregamento de dados*

### Teste Completo
```bash
python teste_dashboard_completo.py
```
*Teste de ponta a ponta de todas as funcionalidades*

### Teste de Fluxo
```bash
python teste_dashboard_debug.py
```
*Testa múltiplas credenciais e endpoints*

---

## 📝 LOGS E DEBUGUE

### Ver Logs da Aplicação
1. Abra o dashboard
2. Pressione **F12** para abrir o Developer Tools
3. Acesse a aba **Console**
4. Veja os logs de carregamento do dashboard

### Verificar Requisições HTTP
1. Pressione **F12**
2. Acesse a aba **Network**
3. Veja todas as requisições sendo feitas

### Logs do Backend
Veja a janela do terminal onde o Uvicorn está rodando

---

## ⚙️ TECNOLOGIAS UTILIZADAS

- **Backend**: FastAPI (Python)
- **Frontend**: HTML5 + JavaScript Vanilla
- **Autenticação**: JWT (JSON Web Tokens)
- **Banco de Dados**: SQLite
- **Gráficos**: Chart.js
- **Framework de UI**: CSS Flexbox

---

## 🐛 SOLUÇÃO DE PROBLEMAS

### "Não consigo acessar o sistema"
✓ Verifique se o servidor está rodando em `http://localhost:8000`
✓ Verifique se a porta 8000 não está bloqueada

### "O login não funciona"
✓ Verifique se usar a credencial correta
✓ Verifique se o banco de dados foi populado com `python database/seed_sqlite.py`

### "Dashboard carrega mas não mostra dados"
✓ Abra o console (F12) para ver erros JavaScript
✓ Verifique se os projetos foram criados no banco

### "Erro 405 em /api/tarefas/"
✓ Isso é esperado! GET /api/tarefas/ não está implementado
✓ Use `/api/tarefas/projeto/{id}` para carregar tarefas

---

## 📂 ESTRUTURA DO PROJETO

```
├── backend/                 # APIs FastAPI
│   ├── routes/             # Endpoints da aplicação
│   ├── app.py              # Configuração principale
│   └── requirements.txt     # Dependências Python
├── web/                    # Frontend
│   ├── login.html          # Página de login
│   ├── entrar-projeto.html # Seleção de projeto
│   ├── projects/           # Páginas de projeto
│   │   └── dashboard.html  # Dashboard
│   └── api-client.js       # Cliente HTTP
└── database/               # Banco de dados
    ├── gerenciador.db      # Arquivo SQLite
    └── seed_sqlite.py      # Script para popular dados
```

---

## 📞 SUPORTE

Para mais informações sobre o projeto, consulte:
- `README.md` - Documentação geral
- `PLANO_EVOLUCAO_5_FASES.md` - Plano de desenvolvimento
- `STATUS_SISTEMA.md` - Status técnico detalhado

---

**Sistema criado em: 2025**
**Última atualização: 2025-01-22**
