# 🚂 Deploy no Railway - Guia Completo

## Gerenciador de Projetos de Engenharia Civil
**Desenvolvedor:** Vicente de Souza  
**Data:** Dezembro 2025

---

## 🎯 Por que Railway?

- ✅ **Grátis** para começar ($5 créditos/mês)
- ✅ **MySQL incluído** (addon gratuito)
- ✅ **Deploy automático** via GitHub
- ✅ **HTTPS automático** (SSL grátis)
- ✅ **Logs em tempo real**
- ✅ **Zero configuração de servidor**

**Alternativas:** Render.com, Fly.io, Heroku

---

## 📋 Pré-requisitos

1. Conta no GitHub (já tem ✅)
2. Repositório no GitHub (já tem ✅)
3. Conta no Railway.app (criar agora)

---

## 🚀 Passo a Passo

### **1. Criar Conta no Railway**

1. Acesse: https://railway.app
2. Clique em **"Start a New Project"**
3. Login com GitHub (autorize acesso ao repositório)

### **2. Criar Projeto**

1. No dashboard, clique **"New Project"**
2. Selecione **"Deploy from GitHub repo"**
3. Escolha: `Gandalf12042007/Gerenciador-de-Projetos-de-Engenharia`
4. Railway detecta automaticamente Python e `railway.json`

### **3. Adicionar MySQL Database**

1. No projeto, clique **"New"** → **"Database"** → **"Add MySQL"**
2. Railway cria automaticamente:
   - `MYSQL_URL` (conexão completa)
   - `MYSQLHOST`, `MYSQLPORT`, `MYSQLUSER`, `MYSQLPASSWORD`, `MYSQLDATABASE`

### **4. Configurar Variáveis de Ambiente**

Clique no serviço **backend** → aba **"Variables"** → adicione:

```bash
# Database (Railway preenche automaticamente)
DB_HOST=${{MySQL.MYSQLHOST}}
DB_PORT=${{MySQL.MYSQLPORT}}
DB_USER=${{MySQL.MYSQLUSER}}
DB_PASSWORD=${{MySQL.MYSQLPASSWORD}}
DB_NAME=${{MySQL.MYSQLDATABASE}}

# JWT Security (MUDE ESTAS CHAVES!)
SECRET_KEY=SUA_CHAVE_SUPER_SECRETA_AQUI_MUDE_AGORA_123456789
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15

# Upload
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=104857600

# Email 2FA (Configure seu Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-de-app-google

# Environment
ENVIRONMENT=production
DEBUG=False
```

**⚠️ IMPORTANTE:**
- **Não use** as senhas de exemplo!
- **SECRET_KEY:** Gere uma aleatória: `openssl rand -hex 32`
- **SMTP_PASSWORD:** Use senha de app do Gmail (não sua senha real)

### **5. Importar Schema do Banco**

Opção 1 - **Via Railway Console:**
```bash
# No dashboard, clique no MySQL → "Data" → "Query"
# Cole o conteúdo de database/schema_completo.sql
```

Opção 2 - **Via Railway CLI:**
```bash
# Instalar CLI
npm i -g @railway/cli

# Login
railway login

# Conectar ao MySQL
railway connect MySQL

# Importar
mysql -u root -p < database/schema_completo.sql
```

Opção 3 - **Via código (recomendado):**
```bash
# Adicione migration automática no start.sh (já incluído)
```

### **6. Deploy!**

1. Railway faz deploy automático após configurar variáveis
2. Acompanhe logs em tempo real na aba **"Deployments"**
3. Aguarde ~2-3 minutos

### **7. Obter URL Pública**

1. Vá em **Settings** do serviço backend
2. Clique **"Generate Domain"**
3. Railway gera algo como: `https://seu-projeto.up.railway.app`

### **8. Testar API**

Acesse:
- **Health check:** `https://seu-projeto.up.railway.app/health`
- **Swagger Docs:** `https://seu-projeto.up.railway.app/docs`
- **Criar usuário:** POST `https://seu-projeto.up.railway.app/auth/register`

---

## 🔧 Comandos Úteis

### Ver logs em tempo real
```bash
railway logs
```

### Executar comandos no container
```bash
railway run python migrate.py
```

### Reiniciar serviço
```bash
railway restart
```

### Variáveis de ambiente
```bash
railway variables
```

---

## 🔄 Deploy Automático (CI/CD)

Railway faz **deploy automático** quando você dá `git push`:

```bash
# No seu computador
git add .
git commit -m "feat: nova funcionalidade"
git push origin main

# Railway detecta push e faz deploy automático! ✨
```

**Configurar:**
1. Settings → **"Auto Deploy"** → ✅ Ativar
2. Escolha branch: `main`

---

## 📊 Monitoramento

### Logs
- Dashboard → **Deployments** → **Logs**
- Ver erros, requests, performance

### Métricas
- Dashboard → **Metrics**
- CPU, RAM, Network usage

### Alertas
- Settings → **Webhooks**
- Notificações no Discord/Slack

---

## 💰 Custos

### Plano Gratuito (Hobby)
- **$5 créditos/mês** grátis
- Suficiente para:
  - 1 backend pequeno
  - 1 MySQL database
  - ~500,000 requests/mês

### Se acabar créditos
- Upgrade para **Developer ($20/mês)**
- Ou otimize uso (menos workers, sleep inativo)

---

## 🐛 Troubleshooting

### Erro: "Application failed to respond"
```bash
# Verifique logs
railway logs

# Comum: Porta incorreta
# Railway usa variável $PORT, start.sh já trata isso
```

### Erro: "Database connection failed"
```bash
# Verifique variáveis de ambiente
railway variables

# Certifique que MySQL está rodando
# Dashboard → MySQL → Status: Running
```

### Erro: "Build failed"
```bash
# Verifique requirements.txt
# Certifique que todas dependências estão listadas
```

### Deploy lento
```bash
# Normal: primeiro deploy ~3-5 min
# Próximos deploys: ~1-2 min (cache)
```

### Erro 502 Bad Gateway
```bash
# Aplicação crashou. Ver logs:
railway logs --tail 100

# Comum: Falta variável SECRET_KEY
```

---

## 🔐 Segurança em Produção

### ✅ Checklist Obrigatório

- [ ] SECRET_KEY forte e aleatória (>32 chars)
- [ ] DEBUG=False em produção
- [ ] CORS configurado (domínios específicos)
- [ ] HTTPS ativado (Railway faz automático)
- [ ] Senhas de banco fortes
- [ ] Rate limiting ativado (já implementado)
- [ ] Logs de auditoria (já implementado)
- [ ] Backups de banco (Railway snapshot)

---

## 📈 Próximos Passos

Após deploy bem-sucedido:

1. **Configurar domínio próprio**
   - Settings → **Custom Domain**
   - Apontar DNS do seu domínio

2. **Configurar frontend**
   - Atualizar `api-client.js` com nova URL
   - Deploy frontend no Vercel/Netlify

3. **Monitoring**
   - Integrar Sentry para errors
   - Uptime monitoring (UptimeRobot)

4. **Backup**
   - Railway → MySQL → **Snapshots**
   - Automático ou manual

---

## 📞 Suporte

- **Docs Railway:** https://docs.railway.app
- **Discord Railway:** https://discord.gg/railway
- **GitHub Issues:** https://github.com/Gandalf12042007/Gerenciador-de-Projetos-de-Engenharia/issues

---

## ✅ Checklist Final

Antes de considerar deploy completo:

- [ ] Backend respondendo em URL pública
- [ ] Swagger acessível (`/docs`)
- [ ] Health check OK (`/health`)
- [ ] Criação de usuário funciona
- [ ] Login retorna JWT
- [ ] Banco de dados populado
- [ ] Logs sem erros críticos
- [ ] Frontend conectando na API
- [ ] HTTPS funcionando
- [ ] Testes passando

---

**Desenvolvedor:** Vicente de Souza (Souza371)  
**Repositório:** https://github.com/Gandalf12042007/Gerenciador-de-Projetos-de-Engenharia  
**Data:** Dezembro 2025
