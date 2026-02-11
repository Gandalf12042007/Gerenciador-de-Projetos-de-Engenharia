# Backend - API REST

## 🚦 Status da Auditoria (11/02/2026)

> **API auditada e funcional!**
> - Todos os endpoints testados: autenticação, projetos, tarefas, equipes, documentos, chat.
> - Correção: retorno de ID em tarefas, compatibilidade de status.
> - Dados de teste disponíveis.

---

## 🚀 Instalação e Execução

### 1. Instalar Dependências

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e configure:

```bash
copy .env.example .env
```

Edite o `.env` com suas credenciais MySQL ou SQLite.

### 3. Executar API

```bash
python app.py
```

A API estará disponível em:
- **URL:** http://localhost:8000
- **Documentação Swagger:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 📚 Endpoints Disponíveis

### Autenticação
- **POST** `/auth/login` - Login de usuário
- **POST** `/auth/register` - Registro de novo usuário
- **POST** `/auth/validate-token` - Validar token JWT

### Projetos
- **GET** `/projetos/` - Listar todos os projetos
- **GET** `/projetos/{id}` - Buscar projeto por ID
- **POST** `/projetos/` - Criar novo projeto
- **PUT** `/projetos/{id}` - Atualizar projeto
- **DELETE** `/projetos/{id}` - Deletar projeto

### Tarefas
- **GET** `/tarefas/projeto/{projeto_id}` - Listar tarefas de um projeto
- **POST** `/tarefas/` - Criar nova tarefa
- **PUT** `/tarefas/{id}` - Atualizar tarefa
- **DELETE** `/tarefas/{id}` - Deletar tarefa

## 🔐 Autenticação

Todas as rotas (exceto `/auth/login` e `/auth/register`) requerem token JWT no header:

```
Authorization: Bearer seu-token-aqui
```

## 📝 Exemplo de Uso

### 1. Registrar usuário

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"nome": "João Silva", "email": "joao@exemplo.com", "senha": "senha123", "cargo": "Engenheiro Civil"}'
```

### 2. Fazer login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "joao@exemplo.com", "senha": "senha123"}'
```

### 3. Criar tarefa (com token)

```bash
curl -X POST http://localhost:8000/tarefas/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"projeto_id":1,"titulo":"Tarefa Teste","descricao":"Teste","status":"a_fazer","prioridade":"media"}'
```

## 🛠️ Tecnologias

- **FastAPI** - Framework web moderno
- **JWT** - Autenticação com tokens
- **Bcrypt** - Hash seguro de senhas
- **SQLite/MySQL** - Banco de dados
- **Pydantic** - Validação de dados

## 👨‍💻 Desenvolvedor

Vicente de Souza - 2026
