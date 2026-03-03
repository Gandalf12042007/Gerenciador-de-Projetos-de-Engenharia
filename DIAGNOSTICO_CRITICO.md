# 🔍 DIAGNÓSTICO CRÍTICO - SISTEMA DE ENGENHARIA

**Data**: 02/03/2026  
**Status**: 🔴 **CRÍTICO - NÃO PRONTO PARA PRODUÇÃO**

---

## 📋 PROBLEMAS IDENTIFICADOS

### ETAPA 1 - ESTABILIDADE ABSOLUTA ❌

#### 1️⃣ **Senhas em Texto Plano** 🚨 CRÍTICO
- **Local**: `backend/routes/auth.py` (linhas 75-170)
- **Problema**: Senhas hardcoded sem hash no código-fonte
- **Risco**: Qualquer pessoa com acesso ao código vê todas as senhas
- **Solução**: Migrar para bcrypt hashing

```python
# ❌ ERRADO (atual):
"senha": "Admin@2026",

# ✅ CORRETO (necessário):
"senha_hash": "$2b$12$...(bcrypt hash)..."
```

#### 2️⃣ **Comparação de Senha Insegura** 🚨 CRÍTICO
- **Local**: `backend/routes/auth.py` linha 172
- **Problema**: `if credentials.senha == user["senha"]` (comparação direta)
- **Risco**: Timing attack, sem proteção
- **Solução**: Usar `verify_password()` do passlib

```python
# ❌ ERRADO (atual):
if credentials.senha == user["senha"]:

# ✅ CORRETO (necessário):
if verify_password(credentials.senha, user["senha_hash"]):
```

#### 3️⃣ **Sem Normalização de Email** ❌
- **Local**: `backend/routes/auth.py` linha 171
- **Problema**: Email é case-sensitive
- **Risco**: `user@test.com` ≠ `USER@TEST.COM` (mesmo usuário, 2 contas)
- **Solução**: Normalizar para lowercase

```python
# ✅ CORRETO:
email_normalizado = credentials.email.lower()
if email_normalizado in USUARIOS_ADMIN:
```

#### 4️⃣ **Usuários Hardcoded no Código** ❌
- **Local**: `backend/routes/auth.py` (linhas 75-170)
- **Problema**: 7 usuários definidos no código, não no banco
- **Risco**: Não pode adicionar usuários sem editar código e rearranca
- **Solução**: Migrar para banco de dados (SQLite)

#### 5️⃣ **Sem Logs de Erro de Login** ❌
- **Local**: Apenas loga sucesso (linha 185)
- **Problema**: Não rastreia tentativas falhadas
- **Risco**: Impossível detectar ataques/problemas
- **Solução**: Registrar todas as tentativas (sucesso e falha)

#### 6️⃣ **Sem Limite de Tentativas de Login** ❌
- **Local**: Rate limit existe mas é fraco
- **Problema**: Brute force é fácil
- **Risco**: Conta pode ser acessada por qualquer um
- **Solução**: 3 tentativas → 15 minutos bloqueado

#### 7️⃣ **Sem Controle de Sessão** ❌
- **Problema**: Token não tem logout real
- **Risco**: Usuário faz logout, mas token ainda vale
- **Solução**: Implementar blacklist ou refresh token

---

### ETAPA 2 - CONTROLE DE ACESSO 🟡

#### 1️⃣ **RBAC Incompleto** ❌
- **Problema**: Sistema tem `roles` mas não valida permissões
- **Risco**: Admin e Gerente têm as mesmas funcionalidades
- **Solução**: Implementar middleware de permissões

#### 2️⃣ **Sem Validação de Objeto** ❌
- **Problema**: Usuário A pode editar projeto do Usuário B
- **Risco**: Vazamento de dados/sabotagem
- **Solução**: Verificar ownership em cada rota

---

### ETAPA 3 - WORKFLOW ❌

#### 1️⃣ **Sem Validação de Transição de Status** ❌
- **Problema**: Pode pular de "Backlog" direto para "Concluído"
- **Risco**: Não há controle do fluxo
- **Solução**: Backend valida transições permitidas

---

### ETAPA 4 - RASTREABILIDADE ❌

#### 1️⃣ **Sem Histórico de Alterações** ❌
- **Problema**: Não registra quem alterou o quê
- **Risco**: Impossível auditar mudanças
- **Solução**: Manter tabela `audit_log`

#### 2️⃣ **Sem Comentários em Tarefas** ❌
- **Solução**: Adicionar tabela `task_comments`

#### 3️⃣ **Sem Soft Delete** ❌
- **Problema**: Deletar projeto remove tudo
- **Risco**: Perda de dados
- **Solução**: Marcar como `deleted_at` ao invés de deletar

---

### ETAPA 5 - DASHBOARD 🟡

#### 1️⃣ **Dashboard Existente Mas Incompleto** 
- ✅ Mostra projetos básicos
- ❌ Sem gráficos reais de produtividade
- ❌ Sem alertas de tarefas atrasadas
- ❌ Sem carga de trabalho por pessoa

---

### ETAPA 6 - SEGURANÇA 🔴

#### 1️⃣ **Sem HTTPS** ❌
- **Problema**: Token é transmitido em texto plano
- **Solução**: HTTPS obrigatório em produção

#### 2️⃣ **Sem Recuperação de Senha Segura** ❌
- **Solução**: Email com token temporário

#### 3️⃣ **Sem 2FA** ❌
- **Código existe** mas não é obrigatório
- **Solução**: 2FA opcional por enquanto

---

### ETAPA 7 - DOCUMENTAÇÃO ❌

#### 1️⃣ **README Técnico Incompleto**
- Falta: Instalação, Configuração, Backup

---

### ETAPA 8 - HOSPEDAGEM 🔴

#### 1️⃣ **Rodando Apenas em Localhost**
- **Problema**: Só funciona no computador de uma pessoa
- **Solução**: Montar em VPS (DigitalOcean, AWS, etc.)

---

## 📊 RESUMO DO STATUS

| Etapa | Status | Crítico? |
|-------|--------|----------|
| 1. Estabilidade | 🔴 CRÍTICO | ✅ Sim |
| 2. Controle Acesso | 🟡 Parcial | ✅ Sim |
| 3. Workflow | 🔴 Falta | ✅ Sim |
| 4. Rastreabilidade | 🔴 Falta | ✅ Sim |
| 5. Dashboard | 🟡 Parcial | ❌ Não |
| 6. Segurança | 🔴 Falta | ✅ Sim |
| 7. Docs | 🔴 Falta | ❌ Não |
| 8. Hospedagem | 🔴 Falta | ❌ Não |

---

## ⚡ AÇÃO IMEDIATA NECESSÁRIA

### Prioridade 1 (Antes de qualquer nova feature):

1. **Migrar senhas para bcrypt**
   - [ ] Normalizar emails (lowercase)
   - [ ] Hash de todas as senhas com bcrypt
   - [ ] Mover usuários para banco de dados
   - [ ] Testar login com novas senhas

2. **Adicionar logs de segurança**
   - [ ] Log de toda tentativa de login (sucesso/falha)
   - [ ] Log de quem alterou o quê
   - [ ] Log de exclusões

3. **Implementar RBAC completo**
   - [ ] Middleware de permissões
   - [ ] Validação de ownership
   - [ ] Separar endpoints admin vs gerente vs engenheiro

4. **Workflow profissional**
   - [ ] Validar transições de status no backend
   - [ ] Impedir pulos de etapa

---

## 🚨 POR QUE ISSO IMPORTA PARA EMPRESA

Um sistema interno de empresa não pode ter:
- ❌ Senhas em texto plano = Todo funcionário vê senha de todos
- ❌ Sem logs = Impossível investigar quem fez o quê
- ❌ Sem controle de acesso = Qualquer um edita projeto de qualquer um
- ❌ Sem workflow = Tarefas descontroladas

**Resultado**: Sistema é rejeitado pela TI/Compliance da empresa.

---

## ✅ PRÓXIMOS PASSOS

Seguir **rigorosamente** a sequência:

1. **ETAPA 1 (Esta semana)**: Estabilidade Absoluta
2. **ETAPA 2 (Semana que vem)**: RBAC Completo
3. **ETAPA 3 (Semana 3)**: Workflow Profissional
4. **ETAPA 4 (Semana 4)**: Rastreabilidade
5. **ETAPA 5 (Semana 5)**: Dashboard Gerencial
6. Depois: Segurança avançada, Docs, Hospedagem

---

**Conclusão**: Sistema acadêmico funciona, mas **NÃO está pronto para produção interna de empresa**.

Necessário: **1-2 semanas de hardening** antes de usar em produção.
