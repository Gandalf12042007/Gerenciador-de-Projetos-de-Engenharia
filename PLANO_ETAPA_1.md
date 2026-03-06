# 📋 PLANO DE AÇÃO - ETAPA 1: ESTABILIDADE ABSOLUTA

**Prioridade**: 🔴 CRÍTICA  
**Prazo Estimado**: 3-4 dias  
**Impacto**: Sem isso, sistema NÃO pode ir para produção  

---

## 🎯 Objetivo Final

Quando Etapa 1 terminar:
- ✅ Qualquer funcionário pode fazer login com segurança
- ✅ Senhas em hash bcrypt seguro
- ✅ Emails normalizados
- ✅ Logs completos de autenticação
- ✅ Proteção contra brute force
- ✅ Usuários no banco de dados

---

## 📝 CHECKLIST DETALHADO

### ✅ FASE 1: PREPARAÇÃO (2 horas)

- [ ] **1.1** Backupear banco de dados atual
- [ ] **1.2** Criar script de migração de usuários
- [ ] **1.3** Criar tabela `auth_logs` no banco
- [ ] **1.4** Criar tabela `failed_login_attempts` para rate limit

**Arquivos a criar**:
- `database/migration_users_to_db.py` - Migra usuários para DB
- `database/schema_auth.sql` - Schema novo

---

### ✅ FASE 2: MIGRAÇÃO DE USUÁRIOS (4 horas)

#### 2.1 Criar `usuarios` melhorada no banco
```sql
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,  -- LOWERCASE
    senha_hash TEXT NOT NULL,     -- BCRYPT
    telefone TEXT,
    cargo TEXT,
    role TEXT DEFAULT 'usuario',
    ativo BOOLEAN DEFAULT TRUE,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    ultimo_login DATETIME
);
```

#### 2.2 Executar migração
```bash
python database/migration_users_to_db.py
```

#### 2.3 Validar migração
```bash
python database/validate_migration.py
```

**Arquivos a modificar**:
- `database/schema_sqlite.sql` - Adicionar tabelas
- `database/db_helper.py` - Métodos de usuário

---

### ✅ FASE 3: ATUALIZAR AUTH.PY (6 horas)

#### 3.1 Remover usuários hardcoded
- [ ] Remover `USUARIOS_ADMIN` dict
- [ ] Substituir por consulta ao banco

#### 3.2 Implementar busca de usuário no banco
```python
def get_user_from_db(email: str):
    """Busca usuário no banco pela email normalizado"""
    email_normalized = email.lower()
    # Query ao DB
    return user if user else None
```

#### 3.3 Implementar verificação de senha com bcrypt
```python
# Usar verify_password() existente
if not verify_password(credentials.senha, user["senha_hash"]):
    log_failed_login(email)
    raise HTTPException(401, "Email ou senha incorretos")
```

#### 3.4 Adicionar logs de autenticação
```python
logger.info(f"Login bem-sucedido: {email} às {datetime.now()}")
logger.warning(f"Falha de login: {email} (tentativa {attempt})")
```

**Arquivos a modificar**:
- `backend/routes/auth.py` - Principal, substituir lógica de login
- `backend/utils/auth.py` - Já tem funções de hash

---

### ✅ FASE 4: IMPLEMENTAR RATE LIMIT (3 horas)

#### 4.1 Tabela de tentativas falhadas
```sql
CREATE TABLE failed_login_attempts (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL,
    ip_address TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    bloqueado_ate DATETIME
);
```

#### 4.2 Lógica de bloqueio
```python
# 3 tentativas = bloqueado por 15 minutos
if count_failed_attempts(email) >= 3:
    if not is_blocked_expired(email):
        raise HTTPException(429, "Muitas tentativas. Tente em 15 minutos.")
```

**Arquivos a criar**:
- `backend/utils/rate_limit_login.py` - Lógica de bloqueio

---

### ✅ FASE 5: AUDITORIA E LOGS (4 horas)

#### 5.1 Tabela `auth_logs`
```sql
CREATE TABLE auth_logs (
    id INTEGER PRIMARY KEY,
    email TEXT,
    acao TEXT,  -- 'login_sucesso', 'login_falha', 'logout'
    ip_address TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    motivo TEXT
);
```

#### 5.2 Registrar toda ação de autenticação
```python
def log_auth_action(email, acao, motivo=None):
    """Registra ação de autenticação no log"""
    # INSERT INTO auth_logs
```

#### 5.3 Criar endpoint para listar logs (apenas admin)
```python
@router.get("/logs")
@require_admin
async def get_auth_logs():
    """Listar últimas 100 tentativas de login"""
    return db.query(AuthLog).order_by(-AuthLog.timestamp).limit(100)
```

**Arquivos a criar**:
- `backend/utils/audit_logger.py` - Funções de log

---

### ✅ FASE 6: TESTES COMPLETOS (4 horas)

#### 6.1 Testes de Login
```bash
python backend/tests/test_auth_improved.py
```

**Cenários a testar**:
- [ ] Login correto → Token gerado
- [ ] Senha errada → Erro 401
- [ ] Email não existe → Erro 401
- [ ] Email com maiúsculas → Funciona (normalizado)
- [ ] 3 tentativas erradas → Bloqueado
- [ ] Esperar 15 min → Desbloqueado
- [ ] Login → Registra no log

#### 6.2 Testes de Segurança
```bash
python backend/tests/test_security_improved.py
```

**Cenários**:
- [ ] Senha não está em plaintext no banco
- [ ] Bcrypt hash é válido
- [ ] IP é registrado nos logs
- [ ] Rate limit funciona

**Arquivos a criar**:
- `backend/tests/test_auth_improved.py` - Testes completos
- `backend/tests/test_security_improved.py` - Testes de segurança

---

### ✅ FASE 7: DOCUMENTAÇÃO (2 horas)

#### 7.1 Criar guia de senhas
```markdown
# Guia de Segurança de Senhas

## Para Usuários
- Mínimo 8 caracteres
- 1 letra maiúscula
- 1 número
- Trocar a cada 90 dias (recomendado)

## Para Admins
- Não compartilhar senhas
- Usar senha única para cada pessoa
- Não escrever senhas em texto
```

#### 7.2 Criar guia de recuperação de senha
```markdown
# Como Recuperar Senha

1. Clique em "Esqueci minha senha"
2. Digite seu email
3. Receba link no email
4. Clique e defina senha nova
```

**Arquivos a criar**:
- `docs/GUIA_SENHAS.md`
- `docs/RECUPERACAO_SENHA.md`

---

## 📊 MATRIZ DE TESTES

| Ação | Entrada | Saída Esperada | Status |
|------|---------|---|--------|
| Login com email correto | email + senha correta | Token JWT | ❌ |
| Login com senha errada | email + senha errada | Erro 401 | ❌ |
| Email case-insensitive | USER@TEST.COM | Login funciona | ❌ |
| Brute force (4 tentativas) | 4x tentativas erradas | Bloqueado 15min | ❌ |
| Log de sucesso | Login bem-sucedido | Registrado em DB | ❌ |
| Log de falha | Login falhado | Registrado em DB | ❌ |
| Senha em hash | Consultar DB | Só hash bcrypt visível | ❌ |

---

## 🔍 VALIDAÇÃO FINAL

Quando Fase 7 terminar, executar:

```bash
# 1. Testar login
python test_simple.py

# 2. Validar no banco
sqlite3 database/gerenciador.db ".schema usuarios"

# 3. Ver logs
sqlite3 database/gerenciador.db "SELECT * FROM auth_logs LIMIT 5;"

# 4. Testar rate limit
python tests/test_brute_force.py

# 5. Verificar senhas
python tests/verify_no_plaintext_passwords.py
```

**Sucesso = Todos os testes passam** ✅

---

## 📁 RESUMO DE ARQUIVOS

**Criar**:
- database/migration_users_to_db.py
- database/migration_auth_logs.sql
- backend/utils/rate_limit_login.py
- backend/utils/audit_logger.py
- backend/tests/test_auth_improved.py
- backend/tests/test_security_improved.py
- docs/GUIA_SENHAS.md

**Modificar**:
- backend/routes/auth.py (principal)
- database/db_helper.py
- database/schema_sqlite.sql

**Deletar**:
- Remover `USUARIOS_ADMIN` hardcoded

---

## ⏱️ TIMELINE

- **Dia 1 (4h)**: Preparação + Migração de usuários
- **Dia 2 (6h)**: Atualizar auth.py
- **Dia 3 (7h)**: Rate limit + Logs + Testes
- **Dia 4 (2h)**: Documentação + Validação final

**Total**: ~19 horas = 3 dias de trabalho

---

## 🚨 PONTOS CRÍTICOS

1. **BACKUP antes de começar!**
2. **Testar migração em ambiente de teste primeiro**
3. **Não rodar em produção sem testes completos**
4. **Documentar qualquer mudança no schema**
5. **Comunicar aos usuários sobre mudanças de password**

---

**Próximo passo**: Começar Fase 1 executando este documento como checklist.
