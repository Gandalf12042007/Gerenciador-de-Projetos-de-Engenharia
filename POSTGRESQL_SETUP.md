# 🐘 PostgreSQL Setup Guide

**Este guia mostra como migrar para PostgreSQL mantendo SQLite como fallback**

---

## 📋 **Pré-requisitos**

### Windows:
```powershell
# 1. Baixar PostgreSQL 15+ em:
# https://www.postgresql.org/download/windows/

# 2. Instalar psycopg2 (driver Python)
pip install psycopg2-binary

# 3. Verificar instalação
psql --version
```

### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
pip install psycopg2-binary
```

### macOS:
```bash
brew install postgresql
pip install psycopg2-binary
```

---

## 🚀 **Passo 1: Criar Banco de Dados PostgreSQL**

### Via comando (Simples):
```bash
# Conectar ao PostgreSQL
psql -U postgres

# Criar database
CREATE DATABASE gerenciador_projetos;

# Criar usuário (opcional)
CREATE USER app_user WITH PASSWORD 'sua_senha_aqui';

# Dar permissões
GRANT ALL PRIVILEGES ON DATABASE gerenciador_projetos TO app_user;

# Sair
\q
```

---

## ⚙️ **Passo 2: Configurar .env**

Edite `backend/.env`:

```env
# Use PostgreSQL
DB_TYPE=postgresql

# Credenciais PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=sua_senha
POSTGRES_DB=gerenciador_projetos

# Resto da configuração (igual)
SECRET_KEY=sua_chave_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
LOG_LEVEL=INFO
```

---

## 📊 **Passo 3: Migrar Dados (Automático)**

### Option A: Migração Completa (Recomendado)

```bash
cd backend

# 1. Criar backup automático
python migrate_to_postgresql.py

# Isso vai:
# ✅ Criar backup do SQLite
# ✅ Criar schema no PostgreSQL
# ✅ Migrar todos os dados
# ✅ Validar integridade
```

### Option B: Apenas Criar Schema

```bash
# Se preferir não migrar dados ainda:
python migrate_to_postgresql.py --backup-only

# Depois criar dados novos manualmente:
python -c "from database.seed import Seeder; Seeder({...}).seed_todas_tabelas()"
```

### Option C: Reverter para SQLite

```bash
# Se der problema, reverter:
python migrate_to_postgresql.py --restore ./database/gerenciador.db.backup-20260212-193000
```

---

## ✅ **Passo 4: Iniciar com PostgreSQL**

```bash
# Navegue para o backend
cd backend

# Inicie o servidor (vai usar PostgreSQL automaticamente)
python app.py

# Deverá aparecer:
# INFO: Starting server process
# INFO: API rodando em: http://0.0.0.0:8000
```

---

## 🔄 **Voltar para SQLite (Se Necessário)**

```env
# No .env, mude para:
DB_TYPE=sqlite
SQLITE_PATH=./database/gerenciador.db

# Inicie novamente:
python app.py
```

---

## 🧪 **Testar se Está Funcionando**

```bash
# Teste as 7 contas:
python testar_contas.py

# Deverá mostrar:
# ✅ vicentedesouza762@gmail.com - SUCCESS
# ✅ francisco@projeto.com - SUCCESS
# ... e assim por diante
```

---

## 📊 **Comparação: SQLite vs PostgreSQL**

| Aspecto | SQLite | PostgreSQL |
|---------|--------|-----------|
| **Conexões Simultâneas** | ~5 | 1000+ |
| **Dados Concorrentes** | ❌ Lento | ✅ Otimizado |
| **Produção** | ❌ Não recomendado | ✅ Ideal |
| **Escalabilidade** | Baixa | Alta |
| **Backup** | Manual | Integrado |
| **Segurança** | Básica | Avançada |
| **Setup** | Imediato | 5 minutos |

---

## 🛠️ **Troubleshooting**

### Erro: "psycopg2 not found"
```bash
pip install psycopg2-binary
```

### Erro: "FATAL: password authentication failed"
- Verifique POSTGRES_PASSWORD no .env
- Reinicie PostgreSQL depois de mudar senha

### Erro: "Database does not exist"
```bash
# Crie manualmente:
psql -U postgres -c "CREATE DATABASE gerenciador_projetos;"
```

### Erro: "Cannot load dump: version mismatch"
- Deletar o arquivo `.sql` e executar novamente
- Versão PostgreSQL pode estar diferente

---

## 🔐 **Segurança em Produção**

Antes de fazer deploy:

```env
# .env.prod
DB_TYPE=postgresql
POSTGRES_HOST=seu-servidor.com
POSTGRES_PORT=5432
POSTGRES_USER=app_user  # Não usar 'postgres'!
POSTGRES_PASSWORD=senha_muito_secreta_aleatoria_32_chars
POSTGRES_DB=gerenciador_projetos
SECRET_KEY=chave_super_secreta_aleatoria
DEBUG=False
ENVIRONMENT=production
LOG_LEVEL=WARNING
```

---

## 📈 **Performance (Depois da Migração)**

### Índices Automáticos (PostgreSQL):
```sql
-- Indexar colunas frequentemente consultadas
CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_projetos_status ON projetos(status);
CREATE INDEX idx_tarefas_projeto ON tarefas(projeto_id);
```

### Backup Automático:
```bash
# Linux: adicione ao crontab
0 2 * * * /usr/bin/pg_dump -U postgres gerenciador_projetos > /backup/db-$(date +\%Y\%m\%d).sql
```

---

## ✨ **Próximas Melhorias**

- [ ] Replicação (alta disponibilidade)
- [ ] Particionamento de tabelas
- [ ] Connection pooling (pgBouncer)
- [ ] Monitoring (Grafana + Prometheus)
- [ ] Backup automático na nuvem

---

**Dúvidas? Verifique os logs:**

```bash
# Ver logs PostgreSQL (Linux)
sudo tail -f /var/log/postgresql/postgresql.log

# Ver logs da API
tail -f backend/api.log
```

**Sucesso! 🎉**
