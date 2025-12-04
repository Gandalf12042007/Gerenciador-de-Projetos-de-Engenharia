# 🏗️ Gerenciador de Projetos de Engenharia Civil

[![Status](https://img.shields.io/badge/Status-MVP%20Funcional-yellow)]()
[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)]()
[![Frontend](https://img.shields.io/badge/Frontend-JavaScript-F7DF1E)]()
[![Database](https://img.shields.io/badge/Database-MySQL-4479A1)]()
[![License](https://img.shields.io/badge/License-Academic-blue)]()

Sistema web para gerenciamento completo de projetos de engenharia civil, desenvolvido como projeto acadêmico com foco em **arquitetura profissional, boas práticas e tecnologias modernas**.

**Desenvolvedor:** Vicente de Souza  
**Data:** Dezembro 2025

---

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Status de Implementação](#-status-de-implementação)
- [Tecnologias](#-tecnologias)
- [Funcionalidades](#-funcionalidades)
- [Instalação](#-instalação)
- [Uso](#-uso)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Documentação](#-documentação)
- [Roadmap](#-roadmap)
- [Contribuição](#-contribuição)

---

## 🎯 Sobre o Projeto

Sistema desenvolvido para **gerenciar obras de engenharia civil**, incluindo:
- Gestão de projetos e equipes
- Controle de tarefas (Kanban)
- Upload de documentos técnicos
- Gestão de materiais e orçamentos
- Chat interno por projeto
- Métricas e relatórios de progresso

### Status Atual: 🟡 **MVP Funcional (45% completo)**

Este é um **protótipo funcional** com as features essenciais implementadas. A base técnica está sólida e preparada para expansão. Veja [`ANALISE_IMPLEMENTACAO.md`](./ANALISE_IMPLEMENTACAO.md) para análise detalhada.

---

## ✅ Status de Implementação

### 🟢 Completo e Funcional

| Módulo | Status | Descrição |
|--------|--------|-----------|
| **Database** | 95% | 18 tabelas normalizadas (3FN), migrations, seeds, testes |
| **Autenticação** | 100% | JWT + Bcrypt, login, registro, validação |
| **API - Projetos** | 100% | CRUD completo (5 endpoints) |
| **API - Tarefas** | 100% | CRUD por projeto (4 endpoints) |
| **Frontend - Login** | 100% | Interface moderna com validação |
| **Frontend - Dashboard** | 80% | Cards, filtros, métricas, integração API |

### 🟡 Parcialmente Implementado

| Módulo | Status | Faltando |
|--------|--------|----------|
| **API - Equipes** | 0% | CRUD + permissões |
| **API - Documentos** | 0% | Upload e versionamento |
| **Frontend - Páginas** | 20% | Register, profile, detalhes, kanban |

### 🔴 Não Implementado

- ❌ Chat interno (WebSocket)
- ❌ Materiais e Orçamentos (API)
- ❌ Métricas e Relatórios
- ❌ Notificações
- ❌ Aplicativo Mobile (Flutter)
- ❌ OAuth (Google/Microsoft)
- ❌ Deploy em produção

---

## 🛠️ Tecnologias

### Backend
- **Python 3.8+** - Linguagem principal
- **FastAPI** - Framework web moderno e rápido
- **MySQL 8.0+** - Banco de dados relacional
- **JWT** - Autenticação via tokens
- **Bcrypt** - Hash de senhas
- **Uvicorn** - Servidor ASGI

### Frontend
- **HTML5/CSS3** - Estrutura e estilo
- **JavaScript (Vanilla)** - Lógica e integração
- **Fetch API** - Requisições HTTP
- **localStorage** - Persistência de tokens

### Database
- **MySQL Connector** - Driver Python
- **Connection Pooling** - Gerenciamento de conexões
- **Migrations** - Controle de versão do schema

### DevOps
- **Git/GitHub** - Controle de versão
- **PowerShell** - Scripts de automação

---

## 🚀 Funcionalidades

### ✅ Implementadas

#### Autenticação
- [x] Login com JWT (30min de expiração)
- [x] Registro de novos usuários
- [x] Hash seguro de senhas (Bcrypt)
- [x] Validação de tokens
- [x] Middleware de autenticação

#### Projetos
- [x] Listar projetos (com filtros)
- [x] Criar novo projeto
- [x] Editar projeto
- [x] Deletar projeto
- [x] Métricas do dashboard

#### Tarefas
- [x] Listar tarefas por projeto
- [x] Criar tarefa
- [x] Atualizar tarefa
- [x] Deletar tarefa
- [x] Filtros por status

#### Interface Web
- [x] Tela de login responsiva
- [x] Dashboard de projetos
- [x] Cards com informações
- [x] Filtros e busca
- [x] Botão de logout
- [x] Loading states
- [x] Error handling

### 🔲 Planejadas

#### Equipes
- [X] Gerenciar membros
- [X] Definir papéis (gerente, engenheiro, técnico)
- [ ] Controle de permissões

#### Documentos
- [ ] Upload de arquivos
- [ ] Versionamento
- [ ] Preview de PDFs
- [ ] Controle de acesso
      
#### Relatórios
- [ ] Curva S (planejado vs realizado)
- [ ] Gráficos de Gantt
- [ ] Dashboard executivo
- [ ] Exportação PDF

---

## 📦 Instalação

### Pré-requisitos
- Python 3.8+
- MySQL 8.0+
- Git

### 1. Clone o repositório
```bash
git clone https://github.com/Gandalf12042007/Gerenciador-de-Projetos-de-Engenharia.git
cd Gerenciador-de-Projetos-de-Engenharia
```

### 2. Configure o Banco de Dados
```bash
# Crie o database no MySQL
mysql -u root -p
CREATE DATABASE gerenciador_projetos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# Execute as migrations
cd database
pip install mysql-connector-python
python migrate.py

# (Opcional) Popule com dados de teste
python seed.py
```

### 3. Configure o Backend
```bash
cd backend

# Instale as dependências
pip install -r requirements.txt

# Crie o arquivo .env
copy .env.example .env

# Edite o .env com suas credenciais do MySQL
# DB_PASSWORD=sua_senha_aqui
# SECRET_KEY=sua_chave_secreta_jwt
```

### 4. Execute a API
```bash
python app.py
```

A API estará disponível em:
- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### 5. Abra o Frontend
```bash
# Abra web/login.html no navegador
# Ou use um servidor local:
cd web
python -m http.server 8080
```

Acesse: http://localhost:8080/login.html

---

## 🎮 Uso

### Login
Use um dos usuários de teste (se executou `seed.py`):
```
Email: admin@empresa.com
Senha: admin123
```

### API - Exemplos

#### Registrar novo usuário
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "email": "joao@email.com",
    "senha": "senha123",
    "cargo": "Engenheiro"
  }'
```

#### Fazer login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@empresa.com",
    "senha": "admin123"
  }'
```

#### Listar projetos (autenticado)
```bash
curl -X GET http://localhost:8000/projetos/ \
  -H "Authorization: Bearer SEU_TOKEN_JWT"
```

Veja mais exemplos em [`backend/README.md`](./backend/README.md)

---

## 📁 Estrutura do Projeto

```
Gerenciador-de-Projetos-de-Engenharia/
├── backend/                    # API REST (FastAPI)
│   ├── app.py                 # Aplicação principal
│   ├── config.py              # Configurações
│   ├── requirements.txt       # Dependências Python
│   ├── .env.example          # Template de variáveis
│   ├── routes/               # Endpoints da API
│   │   ├── auth.py           # Autenticação (3 endpoints)
│   │   ├── projetos.py       # Projetos (5 endpoints)
│   │   └── tarefas.py        # Tarefas (4 endpoints)
│   ├── middleware/           # Middlewares
│   │   └── auth_middleware.py # Validação JWT
│   └── utils/                # Utilitários
│       └── auth.py           # Criptografia
│
├── database/                  # Banco de dados
│   ├── migrations/           # Migrations SQL
│   │   └── 001_initial_schema.sql  # Schema completo (18 tabelas)
│   ├── migrate.py            # Sistema de migrations
│   ├── seed.py               # Dados de teste
│   ├── db_helper.py          # Connection pool
│   ├── test_database.py      # Testes automatizados
│   └── schema.dbml           # Diagrama do banco
│
├── web/                       # Frontend Web
│   ├── login.html            # Tela de login
│   ├── api-client.js         # Cliente HTTP
│   └── projects/             # Dashboard
│       ├── index.html        # Interface
│       ├── app.js            # Lógica
│       └── styles.css        # Estilos
│
├── escopo.md                  # Escopo completo do projeto
├── ANALISE_IMPLEMENTACAO.md   # Análise detalhada (O QUE LER!)
└── README.md                  # Este arquivo
```

---

## 📚 Documentação

### Essencial
- **[ANALISE_IMPLEMENTACAO.md](./ANALISE_IMPLEMENTACAO.md)** - 📊 **Análise completa: O que está feito vs. planejado**
- **[escopo.md](./escopo.md)** - 📋 Escopo original do projeto (visão completa)
- **[backend/README.md](./backend/README.md)** - 🔧 Documentação da API
- **[backend/SETUP.md](./backend/SETUP.md)** - 🚀 Guia de instalação do backend

### API
- **Swagger UI:** http://localhost:8000/docs (quando rodando)
- **ReDoc:** http://localhost:8000/redoc

### Database
- **[database/README.md](./database/README.md)** - Documentação do banco
- **[database/DIAGRAMA.md](./database/DIAGRAMA.md)** - Diagrama ER
- **[database/queries_uteis.sql](./database/queries_uteis.sql)** - Queries úteis

---

## 🗺️ Roadmap

### Fase 1: MVP Core ✅ (Atual - 45%)
- [x] Database completo (18 tabelas)
- [x] Sistema de migrations
- [x] Autenticação JWT
- [x] CRUD de projetos
- [x] CRUD de tarefas
- [x] Frontend básico
- [ ] CRUD de equipes (próximo)
- [ ] Upload de documentos (próximo)

### Fase 2: Features Essenciais 🔲 (30%)
- [ ] Gestão de equipes completa
- [ ] Sistema de documentos com versionamento
- [ ] Materiais e orçamentos
- [ ] Perfil de usuário
- [ ] Tela de registro
- [ ] Página de detalhes do projeto

### Fase 3: Features Avançadas 🔲 (15%)
- [ ] Chat interno (WebSocket)
- [ ] Notificações push
- [ ] Relatórios e gráficos
- [ ] Curva S de progresso
- [ ] Exportação PDF
- [ ] OAuth (Google)

### Fase 4: Mobile 🔲 (0%)
- [ ] App Flutter
- [ ] Modo offline
- [ ] Sincronização

### Fase 5: Produção 🔲 (0%)
- [ ] Deploy AWS/Railway
- [ ] CI/CD
- [ ] Monitoramento
- [ ] Backup automático

**Estimativa para 100%:** ~4 meses de desenvolvimento

---

## 🎓 Para Apresentações Acadêmicas

### Pontos Fortes a Destacar:
✅ **Database profissional** com 18 tabelas normalizadas  
✅ **Sistema de migrations** com controle de versões  
✅ **Testes automatizados** (6/6 passando)  
✅ **Arquitetura REST** moderna (FastAPI)  
✅ **Autenticação segura** (JWT + Bcrypt)  
✅ **Documentação automática** (Swagger)  
✅ **Boas práticas** (3FN, índices, FKs, connection pooling)  

### Contexto Importante:
- Este é um **protótipo MVP funcional** (45% do escopo completo)
- O arquivo `escopo.md` representa a **visão completa do produto**
- A **arquitetura está preparada** para todas as features planejadas
- Foco em **qualidade técnica** sobre quantidade de features

---

## 🤝 Contribuição

Este é um **projeto acadêmico**. Contribuições são bem-vindas!

### Como Contribuir:
1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

### Prioridades de Desenvolvimento:
1. 🔴 **Alta:** CRUD de Equipes, Upload de Documentos
2. 🟡 **Média:** Materiais, Orçamentos, Perfil
3. 🟢 **Baixa:** Chat, Relatórios, Mobile

---

## 📝 Licença

Este projeto é desenvolvido para fins **acadêmicos e educacionais**.

---

## 👨‍💻 Desenvolvedores

**Vicente de Souza**  
GitHub:https://github.com/Souza371
**Francisco....
GitHub:https://github.com/Gandalf12042007

---

## 📊 Estatísticas do Projeto

- **Linhas de código:** ~2,600
- **Commits:** 4
- **Tabelas no banco:** 18
- **Endpoints da API:** 12
- **Testes passando:** 6/6 (100%)
- **Tempo de desenvolvimento:** ~27 dias

---

**⭐ Se este projeto foi útil, considere dar uma estrela no repositório!** 
