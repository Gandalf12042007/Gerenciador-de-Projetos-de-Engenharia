# 🔐 CREDENCIAIS DE TESTE - SISTEMA REFATORADO

## ⚠️ IMPORTANTE: Senhas com Hash Bcrypt
Todas as senhas estão armazenadas com **hash bcrypt seguro** no banco de dados. Use as senhas em **texto plano** abaixo para fazer login pelo frontend.

---

## 📋 USUÁRIOS DISPONÍVEIS

### 🚀 ADMINISTRADORES (Role: admin)
Acesso completo ao sistema

1. **Vicente de Souza** (Seu usuário principal)
   - Email: `vicentedesouza762@gmail.com`
   - Senha: `Admin@2026`
   - Cargo: Administrador
   - Permissões: Gerenciar projetos, usuários, perms

2. **Francisco**
   - Email: `francisco@projeto.com`
   - Senha: `Admin@2026`
   - Cargo: Desenvolvedor
   - Permissões: Admin

3. **Professor**
   - Email: `professor@projeto.com`
   - Senha: `Admin@2026`
   - Cargo: Professor
   - Permissões: Admin

---

### 👔 GERENTE DE PROJETOS (Role: gerente)
Pode criar/gerenciar projetos e equipes

4. **Gerente Teste**
   - Email: `gerenteteste@projeto.com`
   - Senha: `Gerente@123`
   - Cargo: Gerente de Projetos
   - Permissões: Criar projetos, adicionar membros, gerenciar código

---

### 🏗️ ENGENHEIRO (Role: engenheiro)
Pode contribuir em projetos

5. **Engenheiro Teste**
   - Email: `engenheiroteste@projeto.com`
   - Senha: `Engenheiro@123`
   - Cargo: Engenheiro Civil
   - Permissões: Ver/editar tarefas, enviar documentos

---

### 🔧 TÉCNICO (Role: tecnico)
Acesso limitado para tarefas técnicas

6. **Técnico Teste**
   - Email: `tecnicoteste@projeto.com`
   - Senha: `Tecnico@123`
   - Cargo: Técnico em Edificações
   - Permissões: Acesso básico a projetos

---

### 👥 CLIENTE (Role: cliente)
Acesso view-only

7. **Cliente Teste**
   - Email: `clienteteste@projeto.com`
   - Senha: `Cliente@123`
   - Cargo: Cliente
   - Permissões: Visualizar projetos

---

## 🧪 COMO TESTAR

### 1. **Login Local**
```bash
cd c:\Users\franc\projeto\Gerenciador-de-Projetos-de-Engenharia
python backend/app.py
```
Acesse: `http://localhost:5000`

### 2. **Testar com cURL**
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "vicentedesouza762@gmail.com",
    "senha": "Admin@2026"
  }'
```

**Resposta esperada:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "tipo_token": "bearer",
  "usuario": {
    "id": 1,
    "nome": "Vicente de Souza",
    "email": "vicentedesouza762@gmail.com",
    "role": "admin",
    "ativo": true
  }
}
```

### 3. **Testar Endpoints com Token**
```bash
# Usar o access_token recebido acima
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# Listar projetos do usuário
curl -X GET http://localhost:5000/projetos/ \
  -H "Authorization: Bearer $TOKEN"

# Criar novo projeto
curl -X POST http://localhost:5000/projetos/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Projeto Teste",
    "descricao": "Descrição do projeto",
    "cliente": "Cliente XYZ"
  }'
```

---

## 🔒 SEGURANÇA

- ✅ Senhas hasheadas com **bcrypt** (não são armazenadas em texto plano)
- ✅ Tokens JWT com **expiração de 24 horas**
- ✅ AuthMiddleware valida token a cada requisição
- ✅ RBAC via tabela `equipes` (project-based access control)
- ✅ Permissões por role: admin > gerente > engenheiro > tecnico > cliente

---

## 🔄 FLUXO DE AUTENTICAÇÃO REFATORADO

```
Usuario (Frontend)
       ↓
   Login Form
   (email + senha)
       ↓
POST /auth/login
       ↓
   AuthService.authenticate_user()
       ↓
   UserRepository.get_by_email()
   ↓
   bcrypt.verify_password()
       ↓ (se válido)
   AuthService.create_access_token_for_user()
   ↓
   JWT Token criada com:
   {
     "sub": user_id,
     "email": email,
     "role": role,
     "exp": datetime + 24h
   }
       ↓
   TokenResponse retorna:
   {
     "access_token": JWT,
     "tipo_token": "bearer",
     "usuario": {...}
   }
       ↓
   Frontend salva JWT no localStorage
       ↓
   Proximas requisições incluem:
   Headers: {
     "Authorization": "Bearer eyJ0eXAi..."
   }
```

---

## 📊 ESTRUTURA DE BANCO DE DADOS

### Tabela: usuarios
```
id | nome | email | senha_hash (bcrypt) | role | ativo | ...
```

### Tabela: equipes (Team-based RBAC)
```
id | projeto_id | usuario_id | papel | ativo | ...
   |     1      |      1     |gerente|  1   |
   |     1      |      2     |engenheiro
```

### Tabela: projetos
```
id | nome | project_code (4-char) | criador_id | status | ...
1  | Projeto 1 | AB3K | 1 | em_andamento | ...
2  | Projeto 2 | XY9Z | 2 | planejamento | ...
```

---

## 🚀 PRÓXIMOS PASSOS

1. ✅ **Testar login** com credenciais acima
2. ✅ **Criar projeto** e gerar `project_code` automaticamente
3. ✅ **Convidar usuários** pelo código do projeto
4. ✅ **Validar RBAC** - check se apenas gerentes podem regenerar código
5. ✅ **Deploy** em Railway/Render com credenciais em `.env`

---

**Gerado:** 2025
**Sistema:** Gerenciador de Projetos de Engenharia (Refatorado)
**Arquitetura:** FastAPI + JWT + bcrypt + MySQL/SQLite
