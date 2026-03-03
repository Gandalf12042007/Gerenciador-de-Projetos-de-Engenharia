# 🚀 GUIA COMPLETO DE DEPLOYMENT - FASE 5

**Desenvolvido por:** Vicente de Souza  
**Data de Atualização:** 03 de março de 2026  
**Versão:** 1.0.0

---

## 📋 ÍNDICE

1. [Pré-Requisitos](#pré-requisitos)
2. [Chooser Provedor](#chooser-provedor)
3. [Deployment Railway](#deployment-railway)
4. [Deployment Render](#deployment-render)
5. [Deployment Docker](#deployment-docker)
6. [Testes em Produção](#testes-em-produção)
7. [Monitoramento](#monitoramento)
8. [Troubleshooting](#troubleshooting)

---

## 🛠️ PRÉ-REQUISITOS

### Requisitos Obrigatórios:
- [x] Git instalado `git --version`
- [x] Python 3.9+ (para testes locais)
- [x] Node.js 16+ (opcional, para build frontend)
- [x] Repositório GitHub criado
- [x] Banco de dados PostgreSQL (ou MySQL)

### Requisitos Recomendados:
- Docker instalado
- Postman ou Insomnia (testar API)
- ngrok (expor localhost)

### Variáveis de Ambiente:

```bash
# Backend
DATABASE_URL=postgresql://user:password@host:5432/dbname
JWT_SECRET=use-a-chave-super-secreta-aqui
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
LOG_LEVEL=info
CORS_ORIGINS=https://seu-dominio.com
DEBUG=false

# Email (SendGrid)
SENDGRID_API_KEY=sua-chave-sendgrid

# Banco de Dados
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=gerenciador_projetos
DB_USER=seu_usuario
DB_PASSWORD=sua_senha

# Segurança
MAX_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_MINUTES=15
SESSION_TIMEOUT_MINUTES=30
```

---

## 🌐 CHOOSER PROVEDOR

### Comparativo:

| Provedor | Custo | Facilidade | Escalabilidade | Suporte | Recomendado |
|----------|-------|-----------|-----------------|---------|------------|
| **Railway** | $5-50/mês | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ MELHOR |
| **Render** | Grátis-$7 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ✅ BOA |
| **Heroku** | $7-50/mês | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ PADRÃO |
| **AWS EC2** | $5-100+/mês | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ❓ AVANÇADO |
| **Digital Ocean** | $5-40/mês | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ BOA |

**⭐ Recomendação: Railway (melhor custo/benefício)**

---

## 🚀 DEPLOYMENT RAILWAY

### Passo 1: Preparar Repositório

```bash
# Navegar até raiz do projeto
cd c:\Users\vicen\Gerenciador-de-Projetos-de-Engenharia-3

# Inicializar git (se não estiver)
git init

# Adicionar arquivo de configuração Railway
cat > railway.json << 'EOF'
{
  "stageId": "prod",
  "buildCommand": "pip install -r backend/requirements.txt",
  "startCommand": "cd backend && python app.py",
  "environmentSize": "standard"
}
EOF

# Commit
git add -A
git commit -m "Fase 5: Preparado para deployment"
git push origin main
```

### Passo 2: Criar Conta Railway

1. Ir para [railway.app](https://railway.app)
2. Clicar em "Create New Project"
3. Conectar GitHub
4. Selecionar repositório
5. Autorizar acesso

### Passo 3: Configurar Variáveis

No painel Railway:

1. Projeto → Settings → Variables
2. Adicionar variáveis:

```
DATABASE_URL              postgresql://user:pass@host:5432/db
JWT_SECRET               use-chave-super-secreta
LOG_LEVEL                info
CORS_ORIGINS             https://seu-app.railway.app
DEBUG                    false
```

### Passo 4: Deploy Automático

```bash
# Push ativa deployment automático
git push origin main

# Acompanhar no dashboard Railway
# Ou via CLI:
npm install -g @railway/cli
railway login
railway link <project-id>
railway up
```

### Passo 5: Acessar Aplicação

```
Frontend: https://seu-projeto.up.railway.app/login.html
API: https://seu-projeto.up.railway.app/api
Docs: https://seu-projeto.up.railway.app/docs
```

---

## 🎯 DEPLOYMENT RENDER

### Passo 1: Criar Web Service

1. Ir para [render.com](https://render.com)
2. New → Web Service
3. Conectar GitHub
4. Selecionar repositório

### Passo 2: Configurar

**Build Command:**
```bash
pip install -r backend/requirements.txt
```

**Start Command:**
```bash
cd backend && python app.py
```

**Environment:**
- Runtime: Python 3.11
- Region: Escolher mais próximo

### Passo 3: Variáveis de Ambiente

Settings → Environment:

```
DATABASE_URL=postgresql://...
JWT_SECRET=sua-chave
LOG_LEVEL=info
PORT=8000
```

### Passo 4: Deploy

Fazer push em `main`:
```bash
git push origin main
```

Render fará deploy automático.

---

## 🐳 DEPLOYMENT DOCKER

### Dockerfile (já existe)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 8000

CMD ["python", "app.py"]
```

### Passos:

#### 1. Build Local

```bash
docker build -t gerenciador-projetos:latest .
docker run -p 8000:8000 gerenciador-projetos:latest
```

#### 2. Push para Docker Hub

```bash
docker login
docker tag gerenciador-projetos seu-usuario/gerenciador-projetos
docker push seu-usuario/gerenciador-projetos:latest
```

#### 3. Deploy com Docker Compose

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: gerenciador
      POSTGRES_PASSWORD: senha123
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    image: seu-usuario/gerenciador-projetos:latest
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:senha123@db:5432/gerenciador
      JWT_SECRET: sua-chave-secreta
    depends_on:
      - db

volumes:
  postgres_data:
```

```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## ✅ TESTES EM PRODUÇÃO

### 1. Health Check

```bash
# Verificar se API está respondendo
curl https://seu-app.com/health
# Esperado: {"status": "ok", "version": "1.0.0"}
```

### 2. Teste de Login

```bash
# Fazer login
curl -X POST https://seu-app.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test@123"}'

# Esperado: {"access_token": "...", "token_type": "bearer"}
```

### 3. Teste de API

```bash
# Listar projetos (requer token)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://seu-app.com/api/projects

# Esperado: [{"id": 1, "name": "Projeto 1", ...}]
```

### 4. Teste PWA

```javascript
// No console do navegador
window.pwaInstaller.getInfo()
// Verdadeiro: {installed: false, online: true, ...}
```

### 5. Teste Responsividade

1. Abrir DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Testar em:
   - iPhone 12 (390x844)
   - iPad (768x1024)
   - Desktop (1920x1080)

### 6. Teste Offline

```javascript
// Simular offline em DevTools
// Network → Offline
// Navegar em cache deve funcionar
```

### 7. Teste de Performance

```bash
# Usar Google PageSpeed Insights
# ou Lighthouse (DevTools → Lighthouse)
# Meta: Score > 90
```

---

## 📊 MONITORAMENTO

### Logs

**Railway:**
```bash
# Via CLI
railway logs

# Ou no dashboard → Deployments → Logs
```

**Render:**
```bash
# Dashboard → Service → Logs
```

### Alertas

**Configurar notificações para:**
- Erros críticos na API
- Taxa de erro alta (>5%)
- Downtime
- Disco cheio
- Memória alta (>80%)

### Métricas

Monitorar:
- Tempo de resposta médio < 200ms
- Taxa de erro 5xx < 0.1%
- Uptime > 99%
- Requisições/segundo

### Ferramentas Recomendadas:

- **Sentry** (error tracking)
- **DataDog** (APM)
- **New Relic** (monitoramento)
- **Uptime Robot** (disponibilidade)

---

## 🔧 TROUBLESHOOTING

### Problema: "502 Bad Gateway"

**Causa:** Aplicação não iniciou corretamente

**Solução:**
1. Verificar logs: `railway logs`
2. Checar variáveis de ambiente
3. Verificar conexão do banco de dados
4. Restartar serviço

### Problema: "Connection refused"

**Causa:** Banco de dados não acessível

**Solução:**
```bash
# Testar conexão
psql postgresql://user:pass@host/db

# Ou via python
python -c "import psycopg2; print('OK')"
```

### Problema: "Import Error"

**Causa:** Dependência não instalada

**Solução:**
```bash
# Verificar requirements.txt
pip install -r backend/requirements.txt

# Testes locais
python -c "from fastapi import FastAPI; print('OK')"
```

### Problema: PWA não instala

**Causa:** Falta manifest.json ou HTTPS

**Solução:**
1. Verificar `/manifest.json` existe
2. Usando HTTPS (produção)
3. Headers corretos:
   ```
   Content-Type: application/manifest+json
   ```

### Problema: Lento em mobilem

**Causa:** Muitos assets não otimizados

**Solução:**
1. Minificar CSS/JS
2. Comprimir imagens
3. Usar CDN
4. Cache headers adequados

### Problema: CORS errors

**Causa:** Origem não permitida

**Solução:**
```python
# Em backend/config.py
CORS_ORIGINS = [
    "https://seu-app.com",
    "https://www.seu-app.com",
    "http://localhost:3000"  # Desenvolvimento
]
```

---

## 📝 CHECKLIST FINAL

Antes de Produção:

- [ ] Banco de dados PostgreSQL/MySQL em nuvem
- [ ] SSL/TLS configurado (HTTPS)
- [ ] Variáveis de ambiente seguras
- [ ] Backups automáticos ativados
- [ ] Rate limiting ativo
- [ ] Logs centralizados
- [ ] Alertas configurados
- [ ] Teste de login funciona
- [ ] API responde corretamente
- [ ] PWA instalável
- [ ] Responsivo (mobile/tablet/desktop)
- [ ] Performance > 90 (Lighthouse)
- [ ] Sem erros de segurança
- [ ] Documentação atualizada
- [ ] Equipe orientada

---

## 🎯 PÓS-DEPLOYMENT

### Semana 1:
- Monitorar números
- Corrigir bugs críticos
- Otimizar performance

### Semana 2-4:
- Coletar feedback
- Implementar melhorias
- Expandir funcionalidade

### Monthly:
- Análise de métricas
- Planejamento de features
- Atualização de dependências

---

## 📞 SUPORTE

Problemas? Contate:

- **Email:** vicentedesouza762@gmail.com
- **GitHub Issues:** [seu-repo]/issues
- **Discord/Slack:** [seu-servidor]

---

**Versão:** 1.0.0  
**Última atualização:** 03/03/2026  
**Desenvolvido com ❤️ por Vicente de Souza**
