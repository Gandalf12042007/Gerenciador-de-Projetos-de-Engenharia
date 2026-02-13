# ⚡ GUIA RÁPIDO FASE 2 - PostgreSQL

**Data:** 12/02/2026  
**Tempo Estimado:** 1-2 horas  
**Objetivo:** Migrar de SQLite para PostgreSQL com fallback seguro

---

## 🎯 Resumo do que vai acontecer:

```
SQLite (Atual)
    ↓
    ✅ Backup automático
    ↓
PostgreSQL (Nova)
    ↓
    ✅ Dados migrados
    ✓ Todas as 7 contas funcionando
    ✓ Rollback disponível se necessário
```

---

## 📋 PRÉ-REQUISITOS

### ✅ Já temos:
- `backend/config.py` - Suporta PostgreSQL
- `backend/migrate_to_postgresql.py` - Script automático
- `POSTGRESQL_SETUP.md` - Documentação completa

### ❓ Você precisa instalar:

#### **Opção A: PostgreSQL Local (Recomendado)**
```powershell
# Windows
# 1. Baixar em: https://www.postgresql.org/download/windows/
# 2. Instalar
# 3. Notará a senha do usuario 'postgres'

# Verificar instalação
psql --version
```

#### **Opção B: PostgreSQL via Docker** (Mais rápido)
```powershell
# Se tiver Docker instalado
docker run -d `
  --name postgres-gerenciador `
  -e POSTGRES_PASSWORD=password123 `
  -e POSTGRES_DB=gerenciador_projetos `
  -p 5432:5432 `
  postgres:15-alpine
```

#### **Opção C: Usar SQLite (Pular esta fase)**
```
Se não quer/conseguir instalar PostgreSQL agora:
- Sistema continua 100% funcional com SQLite
- Pode fazer isso depois
- Documentação fica disponível
```

---

## 🚀 EXECUÇÃO (Escolha uma opção)

### **OPÇÃO 1: Migração Automática (Recomendado)**

```powershell
# 1. Navegar ao backend
cd backend

# 2. Criar arquivo .env com suas credenciais PostgreSQL
# Criar arquivo chamado .env na raiz do projeto com:

DB_TYPE=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=SEU_PASSWORD_AQUI
POSTGRES_DB=gerenciador_projetos

# 3. Executar migração (cria backup automático)
python migrate_to_postgresql.py

# Esperar conclusão...
# ✅ Backup criado: database/gerenciador.db.backup-[timestamp]
# ✅ Schema PostgreSQL criado
# ✅ Dados migrados
# ✅ 7 contas para teste já lá!

# 4. Iniciar servidor
python app.py

# 5. Testar em http://localhost:8000/health
```

### **OPÇÃO 2: Migração Manual com Psycopg2**

```python
# backend/setup_postgresql.py

import psycopg2
from config import Settings

config = Settings()

try:
    # Conectar ao PostgreSQL
    conn = psycopg2.connect(
        host=config.POSTGRES_HOST,
        user=config.POSTGRES_USER,
        password=config.POSTGRES_PASSWORD,
        database="postgres"  # DB padrão
    )
    
    cursor = conn.cursor()
    
    # Criar database se não existir
    cursor.execute(f"CREATE DATABASE {config.POSTGRES_DB};")
    print(f"✅ Database '{config.POSTGRES_DB}' criado")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    # Depois executar seed.py para popular dados
    
except Exception as e:
    print(f"❌ Erro: {e}")

python setup_postgresql.py
```

---

## 🧪 TESTAR MIGRAÇÃO

```powershell
# 1. Executar testes com 7 contas
python testar_contas.py

# Esperadas:
# ✅ vicentedesouza762@gmail.com - SUCCESS
# ✅ francisco@projeto.com - SUCCESS
# ✅ professor@projeto.com - SUCCESS
# ✅ gerenteteste@projeto.com - SUCCESS
# ✅ engenheiroteste@projeto.com - SUCCESS
# ⏳ tecnicoteste@projeto.com - Rate Limit (normal)
# ⏳ clienteteste@projeto.com - Rate Limit (normal)

# 2. Testar em http://localhost:3000
# Login com qualquer conta
# Verificar se funciona igual

# 3. Comparar performance
# PostgreSQL será muito mais rápido!
```

---

## 🔄 SE DER ERRO: Rollback

```powershell
# Se algo der errado:

# 1. Voltar para SQLite
cd backend
python migrate_to_postgresql.py --restore ./database/gerenciador.db.backup-[DATE-TIME]

# Ou manualmente no código backend/config.py:
# Mudar: DB_TYPE=postgresql
# Para:  DB_TYPE=sqlite

# 2. Reiniciar servidor
python app.py

# Dados voltam 100% intactos!
```

---

## 📊 COMPARAÇÃO: SQLite vs PostgreSQL

| Aspecto | SQLite | PostgreSQL |
|---------|--------|-----------|
| **Conexões** | ~5 | 1000+ |
| **Performance** | Boa | Excelente |
| **Múltiplos users** | ⚠️ Lento | ✅ Rápido |
| **Produção** | ❌ Não | ✅ Sim |
| **Setup** | Imediato | 5 min |
| **Backup** | Manual | Automático |
| **Fallback** | N/A | ✅ SQLite |

---

## 📝 CHECKLIST

- [ ] PostgreSQL instalado (verificar com `psql --version`)
- [ ] Arquivo `.env` criado com credenciais
- [ ] Executar `python migrate_to_postgresql.py`
- [ ] Ver mensagem de sucesso: "✅ Migração concluída"
- [ ] Testar com `python testar_contas.py`
- [ ] Logar em http://localhost:3000 com 7 contas
- [ ] Verificar performance melhorada
- [ ] Git commit: "feat: Migrar para PostgreSQL"
- [ ] Git push ao GitHub

---

## 🆘 PROBLEMAS COMUNS

### "psycopg2 not found"
```powershell
pip install psycopg2-binary
```

### "Connection refused"
```
- PostgreSQL não está rodando
- Verificar: psql -U postgres
- Ou iniciar Docker: docker start postgres-gerenciador
```

### "FATAL: password authentication failed"
```
- Senha errada no .env
- Listar usuários: psql -U postgres -c "\du"
```

### "Database does not exist"
```
- Criar manualmente:
psql -U postgres -c "CREATE DATABASE gerenciador_projetos;"
```

---

## ✨ PRÓXIMAS FASES

Após PostgreSQL pronto:

1. **FASE 3:** Testes Automatizados (pytest)
2. **FASE 4:** Módulo Financeiro
3. **FASE 5:** React Migration
4. **FASE 6:** Microserviços

**Qual você quer fazer em seguida? 🚀**
