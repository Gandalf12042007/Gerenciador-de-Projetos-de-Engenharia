#  Gerenciador de Projetos de Engenharia Civil

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3.3+-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Sistema completo para gerenciamento de projetos de engenharia civil com controle de tarefas, equipes, documentos e orcamentos.**

[Demo](#demo) | [Instalacao](#instalacao) | [Documentacao](#documentacao) | [Contribuir](#contribuindo)

</div>

---

## Indice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Arquitetura](#arquitetura)
- [Instalacao](#instalacao)
- [Configuracao](#configuracao)
- [Uso](#uso)
- [API Documentation](#api-documentation)
- [Testes](#testes)
- [Deploy](#deploy)
- [Roadmap](#roadmap)
- [Contribuindo](#contribuindo)
- [Autor](#autor)

---

## Sobre o Projeto

O **Gerenciador de Projetos de Engenharia Civil** e uma aplicacao web full-stack desenvolvida para auxiliar engenheiros, arquitetos e equipes de construcao no gerenciamento completo de projetos.

### Motivacao

- Centralizar informacoes de projetos
- Facilitar a colaboracao entre equipes
- Automatizar o controle de prazos e tarefas
- Gerenciar documentos tecnicos de forma organizada
- Acompanhar orcamentos e custos

---

## Funcionalidades

### Dashboard Interativo
- Visao geral de todos os projetos
- Graficos de progresso e estatisticas
- Alertas de tarefas atrasadas
- Metricas de desempenho

### Gestao de Projetos
- CRUD completo de projetos
- Definicao de status e progresso
- Controle de datas e prazos
- Associacao com clientes

### Gerenciamento de Tarefas
- Quadro Kanban visual
- Priorizacao por niveis
- Atribuicao de responsaveis
- Estimativas de horas
- Comentarios e historico

### Controle de Equipes
- Gestao de membros por projeto
- Niveis de permissao (Gerente, Coordenador, Engenheiro, Tecnico)
- Convites por email
- Historico de atividades

### Gestao de Documentos
- Upload de arquivos tecnicos
- Suporte a DWG, PDF, DOC, XLS
- Versionamento automatico
- Categorizacao flexivel
- Busca avancada

### Orcamentos
- Cadastro de materiais e custos
- Controle de gastos por projeto
- Relatorios financeiros

### Chat Integrado (IA)
- Assistente virtual com IA
- Suporte a multiplos modelos (OpenAI, Gemini, Ollama)

### Notificacoes
- Alertas em tempo real
- Notificacoes de prazos
- Avisos de atribuicoes

### Seguranca
- Autenticacao JWT
- Hash de senhas (SHA256)
- Rate limiting
- Protecao CORS
- Validacao de inputs
- Logs de auditoria

---

## Tecnologias

### Backend
| Tecnologia | Versao | Descricao |
|------------|--------|-----------|
| Python | 3.11+ | Linguagem principal |
| FastAPI | 0.100+ | Framework web assincrono |
| Pydantic | 2.0+ | Validacao de dados |
| SQLAlchemy | 2.0+ | ORM |
| PyJWT | 2.8+ | Autenticacao JWT |
| MySQL | 8.0+ | Banco de dados principal |
| SQLite | 3.3+ | Banco de desenvolvimento |
| SlowAPI | 0.1.9 | Rate limiting |

### Frontend
| Tecnologia | Descricao |
|------------|-----------|
| HTML5 | Estrutura semantica |
| CSS3 | Estilos com animacoes |
| JavaScript (ES6+) | Logica do cliente |
| Chart.js | Graficos interativos |

### DevOps
| Tecnologia | Descricao |
|------------|-----------|
| Docker | Containerizacao |
| Docker Compose | Orquestracao |
| Railway | Deploy em nuvem |
| GitHub Actions | CI/CD |

---

## Arquitetura

O projeto segue uma arquitetura em camadas profissional:

```
backend/
|
+-- app/                      # Aplicacao principal
|   +-- models/               # Modelos SQLAlchemy
|   +-- repositories/         # Camada de acesso a dados
|   |   +-- base_repository.py
|   |   +-- project_repository.py
|   |   +-- user_repository.py
|   |   +-- task_repository.py
|   |   +-- team_repository.py
|   |   +-- document_repository.py
|   +-- services/             # Logica de negocio
|   |   +-- auth_service.py
|   |   +-- project_service.py
|   |   +-- user_service.py
|   |   +-- task_service.py
|   |   +-- team_service.py
|   |   +-- document_service.py
|   |   +-- notification_service.py
|   +-- schemas/              # Schemas Pydantic
|   +-- utils/                # Utilitarios
|
+-- routes/                   # Rotas FastAPI
+-- middleware/               # Middlewares
+-- config.py                 # Configuracoes
+-- app.py                    # Entry point

web/                          # Frontend
+-- index.html               # Login
+-- projects/                # Paginas do sistema
+-- assets/                  # Recursos estaticos
```

### Padroes Utilizados

- **Repository Pattern**: Abstracao do acesso a dados
- **Service Layer**: Logica de negocio isolada
- **Dependency Injection**: Injecao de dependencias
- **JWT Authentication**: Tokens seguros
- **RESTful API**: Endpoints padronizados

---

## Instalacao

### Pre-requisitos

- Python 3.11+
- pip (gerenciador de pacotes)
- MySQL 8.0+ (opcional, pode usar SQLite)
- Docker (opcional)

### Instalacao Local

1. **Clone o repositorio**
```bash
git clone https://github.com/Gandalf12042007/Gerenciador-de-Projetos-de-Engenharia.git
cd Gerenciador-de-Projetos-de-Engenharia
```

2. **Crie ambiente virtual**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. **Instale dependencias**
```bash
cd backend
pip install -r requirements.txt
```

4. **Configure variaveis de ambiente**
```bash
cp .env.example .env
```

5. **Inicialize o banco**
```bash
cd ../database
python init_sqlite.py
```

6. **Inicie o servidor**
```bash
cd ../backend
python app.py
```

7. **Acesse o sistema**
```
API: http://localhost:8000
Docs: http://localhost:8000/docs
Frontend: http://localhost:3000
```

### Instalacao com Docker

```bash
docker-compose up -d
```

---

## Configuracao

### Variaveis de Ambiente

Crie um arquivo `.env` na pasta `backend/`:

```env
DB_TYPE=sqlite
SQLITE_PATH=../database/gerenciador.db
SECRET_KEY=sua-chave-secreta-muito-segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_PORT=8000
ENVIRONMENT=development
DEBUG=True
CORS_ORIGINS=http://localhost:3000
```

---

## Uso

### Usuario de Teste

```
Email: admin@teste.com
Senha: admin123
```

### Fluxo Basico

1. **Login** - Autentique-se no sistema
2. **Dashboard** - Visualize metricas gerais
3. **Projetos** - Crie/gerencie projetos
4. **Equipes** - Adicione membros
5. **Tarefas** - Crie tarefas no Kanban
6. **Documentos** - Faca upload de arquivos

---

## API Documentation

### Endpoints Principais

| Metodo | Endpoint | Descricao |
|--------|----------|-----------|
| POST | /auth/login | Login |
| POST | /auth/register | Registro |
| GET | /projetos | Listar projetos |
| POST | /projetos | Criar projeto |
| GET | /projetos/{id} | Detalhes projeto |
| PUT | /projetos/{id} | Atualizar projeto |
| DELETE | /projetos/{id} | Deletar projeto |
| GET | /tarefas | Listar tarefas |
| POST | /tarefas | Criar tarefa |
| GET | /equipes/{projeto_id}/membros | Membros |
| POST | /documentos/upload | Upload documento |

### Documentacao Interativa

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Testes

```bash
cd backend
pytest
pytest --cov=. --cov-report=html
```

---

## Deploy

### Railway

1. Conecte o repositorio ao Railway
2. Configure as variaveis de ambiente
3. Deploy automatico via push

### Docker (Producao)

```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## Roadmap

### Versao 1.0 (Atual)
- [x] CRUD completo de projetos
- [x] Sistema de tarefas e Kanban
- [x] Gestao de equipes
- [x] Upload de documentos
- [x] Autenticacao JWT
- [x] Dashboard com estatisticas
- [x] Arquitetura em camadas
- [x] Repository Pattern
- [x] Service Layer

### Versao 1.1
- [ ] Relatorios exportaveis (PDF)
- [ ] Notificacoes por email
- [ ] App mobile (PWA)
- [ ] Integracao com calendario

### Versao 2.0
- [ ] BI e Analytics avancado
- [ ] Integracao com AutoCAD
- [ ] Sistema de aprovacoes
- [ ] Multi-tenancy

---

## Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/NovaFeature`)
3. Commit suas mudancas (`git commit -m 'Add: NovaFeature'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abra um Pull Request

---

## Autor

**Vicente de Souza**

- GitHub: https://github.com/Gandalf12042007
- Email: vicentedesouza762@gmail.com

---

<div align="center">

**Se este projeto te ajudou, considere dar uma estrela!**

Made with love by Vicente de Souza

</div>
