# 📈 Plano de Melhorias - Manutenção da Estabilidade

**Objetivo:** Elevar o nível do projeto SEM quebrar o que já funciona

---

## 🎯 **FASE 1: PostgreSQL com Fallback (Esta semana)**

### Estratégia Segura:
- ✅ Manter SQLite funcionando (fallback)
- ✅ Configurar PostgreSQL em paralelo
- ✅ Testar tudo com ambos DBs
- ✅ Fazer switch apenas quando 100% funcional

### Arquivos a modificar:
1. `config.py` - Suportar múltiplos DBs
2. `requirements.txt` - Adicionar psycopg2
3. `.env` - Variável para escolher DB
4. `migrate.py` - Script migração automático

### Comando para ativar:
```bash
DB_TYPE=postgresql python app.py
# ou (padrão SQLite, mesmo que antes)
python app.py
```

---

## 🧪 **FASE 2: Testes Automatizados (Semana 2)**

### Cobertura:
- ✅ Auth (login em todas 7 contas)
- ✅ CRUD Projetos
- ✅ Permissões por role
- ✅ Endpoints críticos

### Rodar testes:
```bash
pytest tests/ -v --cov
```

---

## ⚛️ **FASE 3: React Frontend (Semana 3-4)**

### Estratégia:
- ✅ Novo projeto React em `/web-react`
- ✅ Reutilizar API existente
- ✅ Manter HTML antigo em `/web`
- ✅ URL switch: `http://localhost:3000` vs `http://localhost:3001`

### Iniciar:
```bash
npx create-react-app web-react
cd web-react
npm install axios react-router-dom zustand
```

---

## 💄 **FASE 4: Design System + Tema (Semana 4-5)**

### Melhorias CSS:
- ✅ Criar `styles/theme.css` (variáveis globais)
- ✅ Adicionar modo dark/light
- ✅ Melhorar responsividade
- ✅ Componentes reutilizáveis

---

## 💰 **FASE 5: Módulo Financeiro (Semana 5-6)**

### Novas rotas:
- `POST /api/financeiro/custos` - Registrar custo
- `GET /api/financeiro/resumo` - Dashboard
- `GET /api/financeiro/relatorio` - Relatório PDF

### Não quebra nada existente!

---

## 🔄 **FASE 6: Microserviços (Semana 7+)**

### Separação:
- Chat → Serviço independente
- IA → Serviço independente
- Gateway → Orquestra tudo

### Mantém compatibilidade com frontend existente!

---

## ✅ **Status Atual**

- ✅ Backend FastAPI funcionando
- ✅ 5/7 contas de teste funcionando
- ✅ Login em funcionamento
- ✅ APIs prontas
- ✅ Deploy pronto

**PRÓXIMO PASSO:** PostgreSQL com fallback

---

## 📊 **Checklist de Qualidade**

- [ ] Todos os testes passam
- [ ] Sem quebra de compatibilidade
- [ ] Backend funciona com SQLite E PostgreSQL
- [ ] Frontend antigo continua acessível
- [ ] Deploy não afetado
- [ ] 7 contas de teste funcionam em ambos DBs
