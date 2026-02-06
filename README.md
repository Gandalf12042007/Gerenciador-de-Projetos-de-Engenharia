# 🏗️ Gerenciador de Projetos de Engenharia Civil

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3.3+-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Sistema completo para gerenciamento de projetos de engenharia civil com controle de tarefas, equipes, documentos, chat integrado e IA.**

[🚀 Instalação](#-instalação) • [📖 Documentação](#-documentação-da-api) • [👥 Equipe](#-usuários-e-permissões) • [📧 Contato](#-autor)

</div>

---

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Funcionalidades](#-funcionalidades)
- [Tecnologias](#-tecnologias)
- [Arquitetura](#-arquitetura)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Usuários e Permissões](#-usuários-e-permissões)
- [Sistema de Convites](#-sistema-de-convites)
- [Documentação da API](#-documentação-da-api)
- [Deploy](#-deploy)
- [Roadmap](#-roadmap)
- [Autor](#-autor)

---

## 📝 Sobre o Projeto

O **Gerenciador de Projetos de Engenharia Civil** é uma aplicação web full-stack desenvolvida para auxiliar engenheiros, arquitetos e equipes de construção no gerenciamento completo de projetos.

### 🎯 Objetivos

- ✅ Centralizar informações de projetos de engenharia
- ✅ Facilitar a colaboração entre equipes
- ✅ Automatizar o controle de prazos e tarefas
- ✅ Gerenciar documentos técnicos de forma organizada
- ✅ Permitir que clientes acompanhem seus projetos
- ✅ Integrar IA para assistência técnica

---

## ⭐ Funcionalidades

### 📊 Dashboard Interativo
- Visão geral de todos os projetos
- Gráficos de progresso e estatísticas
- Alertas de tarefas atrasadas
- Métricas de desempenho

### 🏗️ Gestão de Projetos
- CRUD completo de projetos
- Definição de status e progresso
- Controle de datas e prazos
- Associação com clientes

### 📋 Quadro de Tarefas (Kanban)
- **Arrastar e soltar** tarefas entre colunas
- Colunas: A Fazer → Em Andamento → Em Revisão → Concluída
- Priorização por níveis (Urgente, Alta, Média, Baixa)
- Campos técnicos de engenharia (Etapa, ART, Responsável Técnico)
- Atribuição de responsáveis
- Datas de início e previsão de término

### 👥 Controle de Equipes
- Gestão de membros por projeto
- Níveis de permissão (Admin, Gerente, Engenheiro, Técnico, Cliente)
- **Sistema de códigos de convite** (6 caracteres)
- Convites por email
- Histórico de atividades

### 📄 Gestão de Documentos
- Upload de arquivos técnicos
- Suporte a DWG, PDF, DOC, XLS, imagens
- **Visualização direta** sem download (iframe)
- Nomes personalizados para documentos
- Categorização flexível
- Download individual

### 💬 Chat Integrado
- **Chat direto** entre usuários
- Chat por projeto
- Histórico de mensagens persistente
- Lista de todos os usuários cadastrados

### 🤖 Assistente IA
- Integração com **Google Gemini**
- Suporte a OpenAI GPT
- Respostas técnicas de engenharia
- Login via Google OAuth

### 🔐 Segurança
- Autenticação JWT
- Hash de senhas com bcrypt (12 rounds)
- Rate limiting (100 req/min)
- Proteção CORS
- Validação de inputs
- Logs de auditoria

### 🔔 Notificações
- Alertas em tempo real
- Notificações de prazos
- Avisos de atribuições

---

## 🛠️ Tecnologias

### Backend
| Tecnologia | Versão | Descrição |
|------------|--------|-----------|
| Python | 3.11+ | Linguagem principal |
| FastAPI | 0.100+ | Framework web assíncrono |
| Pydantic | 2.0+ | Validação de dados |
| SQLite | 3.3+ | Banco de dados |
| bcrypt | 4.0+ | Hash de senhas |
| PyJWT | 2.8+ | Autenticação JWT |
| SlowAPI | 0.1.9 | Rate limiting |
| Uvicorn | 0.23+ | Servidor ASGI |

### Frontend
| Tecnologia | Descrição |
|------------|-----------|
| HTML5 | Estrutura semântica |
| CSS3 | Estilos modernos com gradientes |
| JavaScript (ES6+) | Lógica do cliente |
| Chart.js | Gráficos interativos |

### DevOps
| Tecnologia | Descrição |
|------------|-----------|
| Docker | Containerização |
| Docker Compose | Orquestração |
| Nginx | Proxy reverso |
| Railway | Deploy em nuvem |

---

## 🏛️ Arquitetura

O projeto segue uma arquitetura em camadas profissional:

```
📁 Gerenciador-de-Projetos-de-Engenharia/
│
├── 📁 backend/                    # API FastAPI
│   ├── 📁 app/
│   │   ├── 📁 core/              # Configurações core
│   │   ├── 📁 models/            # Modelos de dados
│   │   ├── 📁 repositories/      # Camada de acesso a dados
│   │   ├── 📁 services/          # Lógica de negócio
│   │   └── 📁 schemas/           # Schemas Pydantic
│   ├── 📁 routes/                # Endpoints da API
│   ├── 📁 middleware/            # Middlewares (auth, rate limit)
│   ├── 📁 utils/                 # Utilitários
│   ├── 📁 tests/                 # Testes automatizados
│   ├── 📄 app.py                 # Entry point
│   └── 📄 config.py              # Configurações
│
├── 📁 database/                   # Banco de dados
│   ├── 📁 migrations/            # Migrações
│   ├── 📄 db_helper.py           # Helper de conexão
│   ├── 📄 schema_sqlite.sql      # Schema SQLite
│   └── 📄 gerenciador.db         # Banco SQLite
│
├── 📁 web/                        # Frontend
│   ├── 📁 projects/              # Páginas do sistema
│   │   ├── 📄 index.html         # Lista de projetos
│   │   ├── 📄 dashboard.html     # Dashboard do projeto
│   │   ├── 📄 kanban.html        # Quadro de tarefas
│   │   ├── 📄 docs.html          # Documentos
│   │   ├── 📄 equipes.html       # Equipes
│   │   └── 📄 chat.html          # Chat do projeto
│   ├── 📄 login.html             # Login
│   ├── 📄 chat.html              # Chat geral com IA
│   ├── 📄 entrar-projeto.html    # Entrar com código
│   └── 📄 api-client.js          # Cliente da API
│
├── 📁 uploads/                    # Arquivos enviados
├── 📁 nginx/                      # Configuração Nginx
├── 📄 docker-compose.yml          # Docker desenvolvimento
├── 📄 docker-compose.prod.yml     # Docker produção
└── 📄 README.md                   # Documentação
```

### Padrões Utilizados

- **Repository Pattern**: Abstração do acesso a dados
- **Service Layer**: Lógica de negócio isolada
- **Dependency Injection**: Injeção de dependências
- **JWT Authentication**: Tokens seguros
- **RESTful API**: Endpoints padronizados

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.11+
- pip (gerenciador de pacotes)
- Git

### Instalação Rápida

```bash
# 1. Clone o repositório
git clone https://github.com/Gandalf12042007/Gerenciador-de-Projetos-de-Engenharia.git
cd Gerenciador-de-Projetos-de-Engenharia

# 2. Crie ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Instale dependências
cd backend
pip install -r requirements.txt

# 4. Inicie o backend
python app.py
```

### Iniciar o Frontend

```bash
# Em outro terminal
cd web
python -m http.server 3000
```

### Acessar o Sistema

| Serviço | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

### Instalação com Docker

```bash
docker-compose up -d
```

---

## ⚙️ Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na pasta `backend/`:

```env
# Banco de Dados
DB_TYPE=sqlite
SQLITE_PATH=../database/gerenciador.db

# Segurança
SECRET_KEY=sua-chave-secreta-muito-segura-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Servidor
API_PORT=8000
ENVIRONMENT=development
DEBUG=True
CORS_ORIGINS=http://localhost:3000

# Google OAuth (opcional)
GOOGLE_CLIENT_ID=seu-client-id
GOOGLE_CLIENT_SECRET=seu-client-secret

# IA (opcional)
GEMINI_API_KEY=sua-api-key-gemini
OPENAI_API_KEY=sua-api-key-openai
```

---

## 👥 Usuários e Permissões

### Contas Padrão do Sistema

| Tipo | Email | Senha | Cargo |
|------|-------|-------|-------|
| 👑 Admin | vicentedesouza762@gmail.com | Admin@2026 | admin |
| 👑 Admin | francisco@projeto.com | Admin@2026 | admin |
| 👑 Admin | professor@projeto.com | Admin@2026 | admin |
| 👔 Gerente | gerenteteste@projeto.com | Gerente@123 | gerente |
| 👷 Engenheiro | engenheiroteste@projeto.com | Engenheiro@123 | engenheiro |
| 🔧 Técnico | tecnicoteste@projeto.com | Tecnico@123 | tecnico |
| 🏠 Cliente | clienteteste@projeto.com | Cliente@123 | cliente |

### Níveis de Permissão

| Cargo | Dashboard | Tarefas | Documentos | Equipes | Chat | Configurações |
|-------|-----------|---------|------------|---------|------|---------------|
| Admin | ✅ | ✅ Tudo | ✅ Tudo | ✅ Gerenciar | ✅ Todos | ✅ |
| Gerente | ✅ | ✅ Tudo | ✅ Tudo | ✅ Gerenciar | ✅ Equipe | ✅ |
| Engenheiro | ✅ | ✅ Criar/Editar | ✅ Upload | ❌ | ✅ Equipe | ❌ |
| Técnico | ✅ | ✅ Próprias | ✅ Ver | ❌ | ✅ Equipe | ❌ |
| Cliente | ✅ Limitado | 👁️ Ver | 👁️ Ver | ❌ | ✅ Gerente | ❌ |

---

## 🎟️ Sistema de Convites

### Como Funciona

O sistema permite que administradores e gerentes gerem **códigos de 6 caracteres** para convidar novos membros para projetos.

### Gerar Código (Admin/Gerente)

1. Acesse a página **Equipes** do projeto
2. Clique em **🔑 Gerar Código**
3. Selecione o papel (Cliente, Colaborador, Técnico, Engenheiro)
4. Defina a validade (1 dia, 7 dias, 30 dias)
5. Compartilhe o código com o convidado

### Entrar com Código (Novo Membro)

1. Acesse: `http://localhost:3000/entrar-projeto.html`
2. Digite o código de 6 caracteres
3. O sistema valida e mostra o nome do projeto
4. Clique em **Entrar no Projeto**
5. Você será adicionado automaticamente à equipe

### API de Convites

```bash
# Gerar código
POST /equipes/convites/gerar-codigo
{
  "projeto_id": 1,
  "papel": "cliente",
  "expiracao_horas": 168
}

# Validar código (público)
GET /equipes/convites/validar/{CODIGO}

# Entrar com código
POST /equipes/convites/entrar
{
  "codigo": "ABC123"
}
```

---

## 📖 Documentação da API

### Endpoints Principais

#### 🔐 Autenticação
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/auth/login` | Login (retorna JWT) |
| POST | `/auth/register` | Registrar usuário |
| POST | `/auth/google` | Login com Google OAuth |
| GET | `/auth/me` | Dados do usuário logado |

#### 🏗️ Projetos
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/projetos` | Listar projetos |
| POST | `/projetos` | Criar projeto |
| GET | `/projetos/{id}` | Detalhes do projeto |
| PUT | `/projetos/{id}` | Atualizar projeto |
| DELETE | `/projetos/{id}` | Deletar projeto |

#### 📋 Tarefas
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/tarefas/projeto/{id}` | Listar tarefas do projeto |
| POST | `/tarefas/projeto/{id}` | Criar tarefa |
| PUT | `/tarefas/{id}` | Atualizar tarefa |
| DELETE | `/tarefas/{id}` | Deletar tarefa |

#### 👥 Equipes
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/equipes/projeto/{id}` | Listar membros |
| POST | `/equipes` | Adicionar membro |
| POST | `/equipes/convites/gerar-codigo` | Gerar código de convite |
| POST | `/equipes/convites/entrar` | Entrar com código |

#### 📄 Documentos
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/documentos/projeto/{id}/documentos` | Listar documentos |
| POST | `/documentos/projeto/{id}/upload` | Upload documento |
| GET | `/documentos/{id}/download` | Download documento |
| GET | `/documentos/{id}/visualizar` | Visualizar (iframe) |
| DELETE | `/documentos/{id}` | Deletar documento |

#### 💬 Chat
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/chat/usuarios-disponiveis` | Listar usuários |
| GET | `/chat/direto/{user_id}` | Mensagens diretas |
| POST | `/chat/direto/enviar` | Enviar mensagem direta |
| GET | `/chat/projeto/{id}` | Chat do projeto |

### Documentação Interativa

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🧪 Testes

```bash
cd backend

# Executar todos os testes
pytest

# Com cobertura
pytest --cov=. --cov-report=html

# Testes específicos
pytest tests/test_auth.py
pytest tests/test_services.py
```

---

## 🚢 Deploy

### Railway (Recomendado)

1. Conecte o repositório ao Railway
2. Configure as variáveis de ambiente
3. Deploy automático via push

### Docker (Produção)

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Estrutura de Produção

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Nginx     │───▶│   FastAPI   │───▶│   SQLite    │
│   (Proxy)   │    │   (Backend) │    │   (Database)│
└─────────────┘    └─────────────┘    └─────────────┘
       │
       ▼
┌─────────────┐
│   Frontend  │
│   (Static)  │
└─────────────┘
```

---

## 📅 Roadmap

### ✅ Versão 1.0 (Atual)
- [x] CRUD completo de projetos
- [x] Sistema de tarefas com Kanban (drag & drop)
- [x] Gestão de equipes
- [x] Upload e visualização de documentos
- [x] Autenticação JWT + Google OAuth
- [x] Dashboard com estatísticas
- [x] Chat entre usuários
- [x] Assistente IA (Gemini)
- [x] Sistema de códigos de convite
- [x] Arquitetura em camadas (Repository + Service)
- [x] Testes automatizados

### 🔜 Versão 1.1
- [ ] Relatórios exportáveis (PDF)
- [ ] Notificações por email
- [ ] App mobile (PWA)
- [ ] Integração com calendário
- [ ] Comentários em tarefas

### 🔮 Versão 2.0
- [ ] BI e Analytics avançado
- [ ] Integração com AutoCAD
- [ ] Sistema de aprovações
- [ ] Multi-tenancy
- [ ] Versionamento de documentos

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'Add: NovaFeature'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abra um Pull Request

---

## 👨‍💻 Autor

<div align="center">

**Vicente de Souza**

[![GitHub](https://img.shields.io/badge/GitHub-Gandalf12042007-181717?style=for-the-badge&logo=github)](https://github.com/Gandalf12042007)
[![Email](https://img.shields.io/badge/Email-vicentedesouza762@gmail.com-EA4335?style=for-the-badge&logo=gmail)](mailto:vicentedesouza762@gmail.com)

</div>

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

<div align="center">

**⭐ Se este projeto te ajudou, considere dar uma estrela!**

🏗️ Made with ❤️ for Engineers

</div>
