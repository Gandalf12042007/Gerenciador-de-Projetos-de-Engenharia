# 🔒 Guia de Segurança - Gerenciador de Projetos

**Status:** ⚠️ DESENVOLVIMENTO (não pronto para produção)  
**Última atualização:** Dezembro 2025  
**Responsável:** Sistema de Segurança

---

## 📋 Checklist de Segurança

### ✅ Implementado (Desenvolvimento)

- [x] **SQL Injection** - Prepared statements em 100% das queries
- [x] **Hash de Senhas** - Bcrypt com salt automático
- [x] **JWT** - Tokens com expiração 30 min
- [x] **Connection Pooling** - Gerenciamento de conexões
- [x] **Validação de Entrada** - Pydantic models com constraints
- [x] **Força de Senha** - Mín. 8 chars, 1 maiúscula, 1 número
- [x] **Logging de Segurança** - Tentativas falhas registradas
- [x] **Erro Genérico** - Sem exposição de detalhes sensíveis

### ⚠️ Parcialmente Implementado

- [ ] **Rate Limiting** - Proteção contra brute force
- [ ] **HTTPS** - Suportado, mas sem certificado
- [ ] **CORS** - Configurado, mas flexível em dev
- [ ] **CSRF** - Não implementado (apenas API)
- [ ] **Auditoria Completa** - Apenas login/registro

### ❌ Não Implementado

- [ ] **OAuth 2.0** - Login com Google/Microsoft
- [ ] **2FA** - Autenticação de dois fatores
- [ ] **Criptografia de Dados** - Campos sensíveis
- [ ] **Backup Automático** - Banco de dados
- [ ] **WAF** - Web Application Firewall
- [ ] **Penetration Testing** - Testes de segurança

---

## 🔐 Configurações de Produção

### 1. Variáveis de Ambiente (.env)

```bash
# ❌ NUNCA faça isso:
SECRET_KEY="chave-fraca"
DB_PASSWORD="123456"

# ✅ SEMPRE faça assim:
SECRET_KEY="<gerar com secrets.token_urlsafe(32)>"
DB_PASSWORD="<senha forte com 20+ caracteres>"
```

**Gerar SECRET_KEY segura:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

### 2. Força de Senha

**Requisitos atuais:**
- ✅ Mínimo 8 caracteres
- ✅ 1 letra maiúscula (A-Z)
- ✅ 1 número (0-9)

**Sugestão para produção:**
- Adicionar 1 caractere especial (!@#$%^&*)
- Histórico de últimas 5 senhas
- Expiração a cada 90 dias

### 3. JWT - Token Expiração

```python
# Desenvolvimento (atual)
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Produção (recomendado)
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # ou até 5 min
REFRESH_TOKEN_EXPIRE_DAYS = 7
```

### 4. Banco de Dados

**Backup automático:**
```bash
# MySQL backup diário
mysqldump -u root -p gerenciador_projetos > backup_$(date +%Y%m%d).sql

# Restaurar
mysql -u root -p gerenciador_projetos < backup_20251210.sql
```

**Credenciais MySQL:**
```sql
-- ✅ Criar usuário com permissões limitadas (NÃO root)
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'senha_forte_123!';
GRANT SELECT, INSERT, UPDATE, DELETE ON gerenciador_projetos.* TO 'app_user'@'localhost';

-- Em produção:
CREATE USER 'app_user'@'%' IDENTIFIED WITH mysql_native_password BY 'senha_forte_123!';
GRANT SELECT, INSERT, UPDATE, DELETE ON gerenciador_projetos.* TO 'app_user'@'<IP_SERVIDOR>';
FLUSH PRIVILEGES;
```

### 5. Rate Limiting (Próximo Sprint)

```python
# Exemplo com slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter

@app.post("/auth/login")
@limiter.limit("5/minute")  # Máximo 5 tentativas por minuto
async def login(credentials: LoginRequest):
    # ...
```

---

## 🔍 Auditoria e Logging

### Logs de Segurança (Backend)

```
[2025-12-10 14:23:45] WARNING  auth.py - Tentativa de login falhou para email: hacker@evil.com
[2025-12-10 14:24:12] ERROR    auth.py - Erro ao gerar hash de senha: <erro>
[2025-12-10 14:25:00] INFO     auth.py - Novo usuário registrado: usuario@empresa.com
[2025-12-10 14:26:15] WARNING  auth.py - Tentativa de registro com email já existente: joao@email.com
```

### Monitorar

```python
# Ver logs em tempo real
tail -f logs/app.log | grep -i warning

# Analisar padrões de ataque
grep "Tentativa de login falhou" logs/app.log | \
  awk '{print $NF}' | \
  sort | uniq -c | sort -rn
```

---

## 🚀 Deploy Seguro

### Checklist Pré-Deploy

- [ ] Arquivo `.env` preenchido com credenciais REAIS
- [ ] `.env` adicionado ao `.gitignore`
- [ ] `git status` NÃO mostra .env
- [ ] `SECRET_KEY` gerada com `secrets.token_urlsafe(32)`
- [ ] `DB_PASSWORD` forte (20+ chars, mix)
- [ ] `HTTPS` configurado (Let's Encrypt recomendado)
- [ ] Rate limiting ativado
- [ ] Backup automático configurado
- [ ] Logs centralizados (ELK, DataDog, etc.)
- [ ] Monitoramento ativo

### Exemplo: Deploy Railway / Render

```bash
# 1. Gerar SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 2. Adicionar variáveis no painel da plataforma
# Environment Variables:
#   SECRET_KEY = <colar aqui>
#   DB_PASSWORD = <senha mysql em produção>
#   ACCESS_TOKEN_EXPIRE_MINUTES = 15

# 3. Deploy
git push heroku main
```

---

## 🛡️ Proteção contra Ataques Comuns

### 1. SQL Injection ✅ Prevenido

**Status:** Todos os queries usam prepared statements (`%s`)

```python
# ❌ NUNCA faça isso
query = f"SELECT * FROM usuarios WHERE email = '{email}'"

# ✅ SEMPRE faça assim
query = "SELECT * FROM usuarios WHERE email = %s"
db.execute_query(query, (email,))
```

### 2. Brute Force ⚠️ Parcialmente Prevenido

**Implementado:**
- Login falha com mensagem genérica (sem confirmar email)
- Logging de tentativas falhas

**Falta implementar:**
- Rate limiting (máx 5 tentativas/min)
- Block temporário após 10 falhas
- Captcha

### 3. XSS (Cross-Site Scripting) ✅ Prevenido

**Status:** API JSON (não HTML), frontend sanitiza entrada

```javascript
// ✅ Seguro
document.getElementById("user").textContent = user.name;

// ❌ Perigoso
document.getElementById("user").innerHTML = user.name;
```

### 4. CSRF (Cross-Site Request Forgery) ℹ️ N/A

**Status:** API REST com JWT (não afetada por CSRF)

CSRF afeta apenas form-based (session cookies), não APIs com tokens JWT.

### 5. Exposição de Dados ✅ Prevenido

**Implementado:**
- Erros genéricos (sem detalhes técnicos)
- Senhas hasheadas com bcrypt
- Tokens JWT com expiração

**Exemplo seguro:**
```python
# ✅ SEGURO - Erro genérico
raise HTTPException(status_code=500, detail="Erro ao cadastrar usuário")

# ❌ PERIGOSO - Expõe detalhes
raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")
```

---

## 📞 Resposta a Incidentes

### Passos se detectar ataque:

1. **Alertar equipe** - Reunião de emergência
2. **Investigar logs** - Procurar padrões suspeitos
3. **Isolar servidor** - Se for crítico
4. **Backup imediato** - Antes de qualquer mudança
5. **Comunicar usuários** - Se dados foram comprometidos
6. **Atualizar defesas** - Patch/upgrade de dependências
7. **Post-mortem** - Documento de lições aprendidas

### Comando de investigação rápida:

```bash
# Ver últimos acessos suspeitos
grep "falhou" logs/app.log | tail -20

# Ver IPs únicos que geraram erro
grep "erro" logs/app.log | awk '{print $NF}' | sort | uniq

# Reportar para admin
cat logs/app.log | grep -A5 "WARNING" | mail -s "Security Alert" admin@empresa.com
```

---

## 📚 Referências e Boas Práticas

### OWASP Top 10 (2021)
1. ✅ Broken Access Control
2. ✅ Cryptographic Failures
3. ✅ Injection (SQL)
4. ✅ Insecure Design
5. ⚠️ Security Misconfiguration
6. ✅ Vulnerable Components
7. ⚠️ Authentication Failures
8. ✅ Software/Data Integrity Failures
9. ⚠️ Logging/Monitoring Failures
10. ⚠️ SSRF

### Recursos

- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Bcrypt Documentation](https://passlib.readthedocs.io/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8949)
- [MySQL Security Guide](https://dev.mysql.com/doc/refman/8.0/en/security.html)

---

## ✅ Próximas Melhorias

**Sprint 1 (Urgente):**
- [ ] Rate limiting no login
- [ ] 2FA via email
- [ ] Backup automático

**Sprint 2 (Importante):**
- [ ] Criptografia de campos sensíveis
- [ ] Audit trail completo
- [ ] WAF (CloudFlare)

**Sprint 3 (Nice to Have):**
- [ ] OAuth 2.0 (Google)
- [ ] Penetration testing anual
- [ ] SOC2 compliance

---

**Nota Final:** Segurança é um processo contínuo, não um destino. Revise este documento a cada sprint e atualize conforme surgem novas ameaças.

🔐 **Mantenha sua aplicação segura!**
