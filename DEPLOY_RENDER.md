# 🎨 Deploy no Render - Guia Completo

## Gerenciador de Projetos de Engenharia Civil
**Desenvolvedor:** Vicente de Souza  
**Data:** Dezembro 2025

---

## 🎯 Por que Render?

- ✅ **Grátis permanente** (750h/mês web service)
- ✅ **PostgreSQL grátis** (90 dias, depois $7/mês)
- ✅ **Deploy automático** via GitHub
- ✅ **HTTPS automático** (SSL grátis)
- ✅ **Mais confiável** que Heroku free tier
- ✅ **Uptime melhor** que Railway

**Desvantagens vs Railway:**
- ❌ MySQL pago (PostgreSQL grátis)
- ❌ Precisa adaptar código (trocar mysql por psycopg2)

---

## 📋 Pré-requisitos

1. Conta no GitHub (já tem ✅)
2. Repositório no GitHub (já tem ✅)
3. Conta no Render.com (criar agora)

---

## 🚀 Passo a Passo

### **1. Criar Conta no Render**

1. Acesse: https://render.com
2. Clique **"Get Started"**
3. Login com GitHub (autorize acesso)

### **2. Criar PostgreSQL Database**

1. Dashboard → **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name:** `gerenciador-projetos-db`
   - **Database:** `gerenciador_projetos`
   - **User:** `projeto_user`
   - **Region:** Oregon (mais próximo)
   - **Plan:** Free (90 dias grátis)
3. Clique **"Create Database"**
4. Aguarde ~2 min para provisionar

**⚠️ IMPORTANTE:** Anote as credenciais:
- **Internal Database URL** (para backend)
- **External Database URL** (para conectar localmente)

### **3. Adaptar Código para PostgreSQL**

**Render usa PostgreSQL (não MySQL)**. Ajustes necessários:

#### A. Atualizar `requirements.txt`
```bash
# Trocar
mysql-connector-python==8.2.0

# Por
psycopg2-binary==2.9.9
```

#### B. Atualizar conexão no código
```python
# backend/config.py ou onde configura DB
# Trocar mysql.connector por psycopg2

import psycopg2
from psycopg2 import pool

# Usar DATABASE_URL do Render
DATABASE_URL = os.getenv("DATABASE_URL")

# Pool de conexões
connection_pool = psycopg2.pool.SimpleConnectionPool(
    1, 20,
    DATABASE_URL
)
```

#### C. Ajustar SQL queries
```sql
-- MySQL usa AUTO_INCREMENT
id INT AUTO_INCREMENT PRIMARY KEY

-- PostgreSQL usa SERIAL
id SERIAL PRIMARY KEY

-- MySQL usa NOW()
created_at TIMESTAMP DEFAULT NOW()

-- PostgreSQL usa CURRENT_TIMESTAMP
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

### **4. Criar Web Service**

1. Dashboard → **"New +"** → **"Web Service"**
2. Conecte ao GitHub repo
3. Configure:
   - **Name:** `gerenciador-projetos-api`
   - **Region:** Oregon
   - **Branch:** `main`
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `bash start.sh`
   - **Plan:** Free

### **5. Configurar Variáveis de Ambiente**

No Web Service → **"Environment"** → adicione:

```bash
# Database (copie do PostgreSQL criado)
DATABASE_URL=${{postgres.DATABASE_URL}}

# Ou configure manualmente
DB_HOST=seu-db.render.com
DB_PORT=5432
DB_USER=projeto_user
DB_PASSWORD=senha_gerada_pelo_render
DB_NAME=gerenciador_projetos

# JWT Security (MUDE!)
SECRET_KEY=SUA_CHAVE_SUPER_SECRETA_MUDE_AGORA_123456
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15

# Upload
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=104857600

# Email 2FA
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-de-app

# Environment
ENVIRONMENT=production
DEBUG=False
PYTHON_VERSION=3.11.0
```

### **6. Deploy!**

1. Clique **"Create Web Service"**
2. Render faz build e deploy automático
3. Aguarde ~5-7 minutos (primeiro deploy é lento)
4. Logs em tempo real na aba **"Logs"**

### **7. Importar Schema PostgreSQL**

**Opção 1 - Via Render Shell:**
```bash
# No dashboard do Database → "Connect" → "PSQL Command"
psql -h seu-db.render.com -U projeto_user gerenciador_projetos

# Cole o schema adaptado para PostgreSQL
\i database/schema_postgres.sql
```

**Opção 2 - Localmente:**
```bash
# Conecte via External URL
psql postgresql://projeto_user:senha@seu-db.render.com/gerenciador_projetos

# Importe
\i database/schema_postgres.sql
```

### **8. Obter URL Pública**

Render gera automaticamente:
```
https://gerenciador-projetos-api.onrender.com
```

---

## 🔧 Diferenças MySQL vs PostgreSQL

### Tipos de Dados
| MySQL | PostgreSQL |
|-------|------------|
| `INT AUTO_INCREMENT` | `SERIAL` |
| `DATETIME` | `TIMESTAMP` |
| `TEXT` | `TEXT` (igual) |
| `TINYINT(1)` (boolean) | `BOOLEAN` |

### Funções
| MySQL | PostgreSQL |
|-------|------------|
| `NOW()` | `CURRENT_TIMESTAMP` |
| `CONCAT(a, b)` | `a \|\| b` ou `CONCAT(a, b)` |
| `IFNULL(a, b)` | `COALESCE(a, b)` |

### Auto Increment
```sql
-- MySQL
id INT AUTO_INCREMENT PRIMARY KEY

-- PostgreSQL
id SERIAL PRIMARY KEY
-- Ou
id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY
```

---

## 🔄 Deploy Automático

Render faz deploy automático no push:

```bash
git add .
git commit -m "fix: corrige query PostgreSQL"
git push origin main

# Render detecta e redeploy automático! ✨
```

**Configurar:**
- Já vem ativado por padrão
- Settings → **"Auto-Deploy"** → ✅ Yes

---

## 💰 Custos

### Plano Free
- **Web Service:** Grátis (750h/mês)
- **PostgreSQL:** 90 dias grátis, depois $7/mês
- **Limitações:**
  - Sleep após 15 min inativo (cold start ~30s)
  - 512 MB RAM
  - Sem custom domains no free tier

### Upgrade
- **Starter ($7/mês):** Sem sleep, 1GB RAM
- **Standard ($25/mês):** 4GB RAM, custom domain

---

## 🐛 Troubleshooting

### Erro: "Deploy failed - Build failed"
```bash
# Verifique requirements.txt
# Certifique que tem psycopg2-binary (não mysql)
```

### Erro: "Connection to database failed"
```bash
# Verifique variável DATABASE_URL
# Format: postgresql://user:pass@host:5432/db
```

### Cold Start (demora para responder)
```bash
# Normal no plano Free
# Primeira request após 15min: ~20-30s
# Solução: Upgrade para Starter ($7/mês)
```

### Erro 502 Bad Gateway
```bash
# Logs → veja erro Python
# Comum: falta variável de ambiente
```

---

## 📊 Monitoramento

- **Logs:** Dashboard → Logs (tempo real)
- **Metrics:** Dashboard → Metrics (CPU, RAM)
- **Alerts:** Settings → Notifications (email/Slack)

---

## 🔐 Segurança

- [ ] SECRET_KEY forte (>32 chars)
- [ ] DEBUG=False
- [ ] PostgreSQL com senha forte
- [ ] HTTPS ativado (automático)
- [ ] CORS configurado
- [ ] Rate limiting ativo

---

## 📈 Próximos Passos

1. **Domínio próprio:** Settings → Custom Domain
2. **SSL:** Automático com custom domain
3. **Monitoring:** Integrar Sentry
4. **Backup:** Render Snapshots (manual/auto)

---

## ✅ Checklist

- [ ] PostgreSQL criado e rodando
- [ ] Código adaptado (psycopg2, SERIAL, etc)
- [ ] Web Service criado
- [ ] Variáveis configuradas
- [ ] Schema importado
- [ ] Deploy bem-sucedido
- [ ] `/health` respondendo
- [ ] `/docs` acessível
- [ ] Login funcionando

---

**Desenvolvedor:** Vicente de Souza (Souza371)  
**Repositório:** https://github.com/Gandalf12042007/Gerenciador-de-Projetos-de-Engenharia  
**Data:** Dezembro 2025

**📌 RECOMENDAÇÃO:** Use Railway se quiser manter MySQL. Use Render se preferir PostgreSQL e uptime garantido.
