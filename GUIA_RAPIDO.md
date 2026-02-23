# Guia Rapido - Como Rodar o Sistema Corrigido

## 🚀 Inicio Rapido (3 passos)

### 1. Iniciar Docker
```bash
# Abrir terminal no diretorio do projeto
cd Gerenciador-de-Projetos-de-Engenharia

# Iniciar todos os servicos
docker-compose up -d
```

**Aguarde 30-60 segundos** para os servicos iniciarem completamente.

---

### 2. Verificar se esta rodando
```bash
# Verificar status dos containers
docker ps

# Voce deve ver 3 containers rodando:
# - projetos_db (MySQL)
# - projetos_backend (FastAPI)
# - projetos_phpmyadmin (PhpMyAdmin)
```

---

### 3. Acessar o Sistema

#### Frontend (Interface Web)
Abra no navegador:
```
web/login.html
```

**Credenciais de teste:**
```
Email: vicentedesouza762@gmail.com
Senha: Abacaxi371
```

#### API (Backend)
```
http://localhost:8000
```

#### Documentacao Swagger
```
http://localhost:8000/docs
```

#### PhpMyAdmin (Banco de Dados)
```
http://localhost:8080
Usuario: root
Senha: root_password_123
```

---

## 🛠️ Comandos Uteis

### Ver logs do backend
```bash
docker logs -f projetos_backend
```

### Ver logs do banco
```bash
docker logs -f projetos_db
```

### Parar o sistema
```bash
docker-compose down
```

### Parar e remover volumes (reset completo)
```bash
docker-compose down -v
```

### Reiniciar apenas o backend
```bash
docker-compose restart backend
```

---

## ✅ Validar Correcoes

Execute o script de validacao:
```bash
python validar_correcoes.py
```

Resultado esperado:
```
RESULTADO: TODAS AS CORRECOES APLICADAS COM SUCESSO!
Verificacoes passaram: 7/7 (100.0%)
```

---

## 🧪 Testar Endpoints Corrigidos

### 1. Login (com is_admin)
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "vicentedesouza762@gmail.com",
    "senha": "Abacaxi371"
  }'
```

**Resposta esperada:**
```json
{
  "access_token": "eyJ...",
  "user_id": 1,
  "nome": "Vicente de Souza",
  "email": "vicentedesouza762@gmail.com"
}
```

---

### 2. Listar Projetos
```bash
# Substitua SEU_TOKEN pelo token recebido no login
curl -X GET http://localhost:8000/api/projetos/ \
  -H "Authorization: Bearer SEU_TOKEN"
```

---

### 3. Criar Tarefa (com auditoria funcionando)
```bash
curl -X POST http://localhost:8000/api/tarefas/ \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "projeto_id": 1,
    "titulo": "Teste de Tarefa",
    "descricao": "Testando auditoria",
    "status": "pendente"
  }'
```

---

## 📊 Verificar Banco de Dados

### Opcao 1: PhpMyAdmin
1. Acesse http://localhost:8080
2. Login: root / root_password_123
3. Selecione database: `gerenciador_projetos`
4. Verifique as novas tabelas:
   - `tokens_reset_senha`
   - `custos_financeiro`
   - `orcamentos_financeiro`
   - `faturas`
   - `fluxo_caixa`
   - `tipos_custo`

### Opcao 2: MySQL CLI
```bash
# Conectar ao container MySQL
docker exec -it projetos_db mysql -u root -p

# Senha: root_password_123

# Listar databases
SHOW DATABASES;

# Usar o database
USE gerenciador_projetos;

# Listar tabelas
SHOW TABLES;

# Verificar migrations aplicadas
SELECT * FROM _migrations ORDER BY executado_em DESC;
```

---

## 🐛 Solucao de Problemas

### Problema: "Port 3306 already in use"
**Solucao:** Voce tem outro MySQL rodando. Pare-o ou mude a porta no docker-compose.yml:
```yaml
ports:
  - "3307:3306"  # Mude de 3306 para 3307
```

---

### Problema: "Port 8000 already in use"
**Solucao:** Outra aplicacao esta usando a porta 8000. Mude no docker-compose.yml:
```yaml
ports:
  - "8001:8000"  # Mude de 8000 para 8001
```

---

### Problema: Container backend reinicia constantemente
**Solucao:** Veja os logs:
```bash
docker logs projetos_backend
```

Provavelmente erro de conexao com banco. Verifique se o container `projetos_db` esta saudavel:
```bash
docker ps
```

---

### Problema: "Cannot connect to Docker daemon"
**Solucao:** Inicie o Docker Desktop:
1. Abra Docker Desktop
2. Aguarde inicializar completamente
3. Execute `docker-compose up -d` novamente

---

## 📁 Estrutura do Projeto

```
Gerenciador-de-Projetos-de-Engenharia/
├── backend/                    # API FastAPI
│   ├── routes/                # Endpoints
│   │   ├── auth.py           # ✅ Corrigido (is_admin)
│   │   ├── tarefas.py        # ✅ Corrigido (imports + codigo duplicado)
│   │   ├── chat.py           # ✅ Corrigido (placeholders)
│   │   └── equipes.py        # ✅ Corrigido (placeholders)
│   └── app.py                # Aplicacao principal
│
├── database/                  # Banco de dados
│   ├── migrations/           # Scripts SQL
│   │   ├── 004_tokens_reset_senha.sql      # ✅ NOVO
│   │   └── 005_modulo_financeiro.sql       # ✅ NOVO
│   └── schema_completo.sql   # Schema completo
│
├── web/                       # Frontend
│   ├── login.html            # Tela de login
│   └── projects/             # Dashboard
│
├── docker-compose.yml         # Configuracao Docker
├── validar_correcoes.py      # ✅ Script de validacao
├── RELATORIO_CORRECOES.md    # ✅ Relatorio detalhado
└── GUIA_RAPIDO.md            # ✅ Este arquivo
```

---

## 🎯 O Que Foi Corrigido?

1. ✅ Imports quebrados em tarefas.py
2. ✅ Codigo duplicado removido
3. ✅ Token JWT agora inclui flag is_admin
4. ✅ Placeholders SQL padronizados (? → %s)
5. ✅ Tabela tokens_reset_senha criada
6. ✅ Tabelas do modulo financeiro criadas
7. ✅ Auditoria funcionando corretamente

**Total:** 7/7 correcoes aplicadas (100%)

---

## 📞 Proximos Passos

1. ✅ Iniciar Docker
2. ✅ Fazer login no sistema
3. ✅ Testar funcionalidades corrigidas
4. ⏭️ Implementar logica do modulo financeiro
5. ⏭️ Adicionar testes automatizados
6. ⏭️ Deploy em producao

---

## 📖 Documentacao Adicional

- **Relatorio Completo:** `RELATORIO_CORRECOES.md`
- **Analise do Projeto:** `ANALISE_IMPLEMENTACAO.md`
- **README Principal:** `README.md`
- **Swagger API:** http://localhost:8000/docs

---

**Data:** 13/02/2026  
**Status:** ✅ Sistema Corrigido e Funcional  
**Desenvolvido por:** Vicente de Souza & Francisco
