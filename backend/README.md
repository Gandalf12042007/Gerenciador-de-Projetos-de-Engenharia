# Backend - API REST

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

Edite o `.env` com suas credenciais MySQL.

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
  -d '{
    "nome": "João Silva",
    "email": "joao@exemplo.com",
    "senha": "senha123",
    "cargo": "Engenheiro Civil"
  }'
```

### 2. Fazer login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joao@exemplo.com",
    "senha": "senha123"
  }'
```

### 3. Listar projetos (com token)

```bash
curl -X GET http://localhost:8000/projetos/ \
  -H "Authorization: Bearer seu-token-aqui"
```

## 🛠️ Tecnologias

- **FastAPI** - Framework web moderno
- **JWT** - Autenticação com tokens
- **Bcrypt** - Hash seguro de senhas
- **MySQL** - Banco de dados
- **Pydantic** - Validação de dados

## 👨‍💻 Desenvolvedor

Vicente de Souza - 2025
