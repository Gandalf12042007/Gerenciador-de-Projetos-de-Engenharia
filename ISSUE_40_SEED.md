# 🌱 Issue #40: Seed de Dados - População do Banco

**Data:** 15 de Dezembro de 2025  
**Status:** ✅ COMPLETO (Dados de demo prontos para uso)  
**Desenvolvedor:** Vicente de Souza

---

## 📊 Resumo

Script `database/seed.py` já existente foi **validado e documentado**. Popula banco com dados realistas para:

✅ **Desenvolvimento local** com dados de exemplo  
✅ **Testes automatizados** com cenários realistas  
✅ **Demonstração** do sistema funcionando  
✅ **Onboarding** de novos desenvolvedores

---

## 🎯 DADOS CRIADOS

### 👤 Usuários (5 usuários)
```
1. João Silva           - Engenheiro Civil (gerente)
2. Maria Santos         - Gerente de Projetos
3. Pedro Oliveira       - Técnico em Edificações
4. Ana Costa            - Arquiteta
5. Carlos Souza         - Engenheiro Estrutural

Senha padrão para todos: senha123
```

### 🔐 Permissões (6 tipos)
```
- admin          - Acesso total ao sistema
- gerente        - Criar e gerenciar projetos
- engenheiro     - Editar tarefas e documentos
- tecnico        - Visualizar e atualizar tarefas
- cliente        - Visualização limitada
- visualizador   - Apenas leitura
```

### 🏗️ Projetos (4 projetos)
```
1. Edifício Residencial Portal das Acácias
   - 12 pavimentos, 48 apartamentos
   - Status: em_andamento (35.5% concluído)
   - Orçamento: R$ 2.500.000,00
   
2. Reforma Shopping Center Norte
   - 3 pisos, climatização moderna
   - Status: em_andamento (45% concluído)
   - Orçamento: R$ 850.000,00
   
3. Ponte sobre o Rio Verde
   - 180m de extensão, concreto armado
   - Status: em_andamento (22.3% concluído)
   - Orçamento: R$ 5.200.000,00
   
4. Residência Unifamiliar Alto Padrão
   - 450m², piscina, automação
   - Status: planejamento (0% concluído)
   - Orçamento: R$ 1.200.000,00
```

### 👥 Equipes (10 atribuições)
```
Cada projeto tem 2-3 membros:
- 1 Gerente (responsável pelo projeto)
- 1-2 Engenheiros (técnicos principais)
- 0-1 Técnico (execução)
```

### ✅ Tarefas (11 tarefas)
```
Estados:
- 3 tarefas concluídas (100%)
- 4 tarefas em andamento (40-65%)
- 4 tarefas a fazer (0%)

Tipos:
- Fundação (escavação, estacas)
- Estrutura (concreto armado)
- Instalações (hidráulicas, elétricas)
- Demolição e reforma
- Acabamento

Prazos e responsáveis variados por projeto
```

### 📦 Materiais (6 itens)
```
- Cimento CP-II 50kg
- Areia média lavada
- Brita 1
- Aço CA-50 12mm
- Tinta acrílica branca
- Concreto usinado FCK 40

Com quantidades, preços e fornecedores
```

---

## 🚀 COMO USAR

### 1. Executar Seed
```bash
cd database
python seed.py
```

**Output esperado:**
```
✓ Conectado ao MySQL - gerenciador_projetos
👥 Criando usuários...
  ✓ João Silva (joao.silva@exemplo.com)
  ✓ Maria Santos (maria.santos@exemplo.com)
  ✓ Pedro Oliveira (pedro.oliveira@exemplo.com)
  ✓ Ana Costa (ana.costa@exemplo.com)
  ✓ Carlos Souza (carlos.souza@exemplo.com)
✓ 5 usuários criados

🔐 Criando permissões...
  ✓ admin
  ✓ gerente
  ...
✓ 6 permissões criadas

[continue...]

✓ SEEDS EXECUTADOS COM SUCESSO!

📊 Dados de exemplo criados:
  • 5 usuários
  • 6 permissões
  • 4 projetos
  • 10 membros de equipe
  • 11 tarefas
  • 6 materiais
```

### 2. Fazer Login com Dados de Teste

```
Email:    joao.silva@exemplo.com
Senha:    senha123

ou

Email:    maria.santos@exemplo.com
Senha:    senha123
```

### 3. Explorar os Projetos
- Visualizar 4 projetos de exemplo
- Ver tarefas em andamento
- Revisar materiais e custos
- Checar equipes e responsáveis

### 4. Limpar e Recomeçar

```bash
# Remove todos os dados e popula novamente
python seed.py --clear
```

---

## 📋 ESTRUTURA DO SCRIPT

### Classe: `Seeder`
```python
def __init__(db_config)    # Inicializa com configuração MySQL
def connect()              # Conecta ao banco
def disconnect()           # Desconecta
def hash_password()        # Gera hash SHA-256
def clear_all_data()       # Remove todos os dados
def seed_usuarios()        # Cria 5 usuários
def seed_permissoes()      # Cria 6 permissões
def seed_projetos()        # Cria 4 projetos
def seed_equipes()         # Atribui 10 membros
def seed_tarefas()         # Cria 11 tarefas
def seed_materiais()       # Cria 6 materiais
def run(clear_first)       # Executa tudo
```

### Configuração MySQL

Lê variáveis de ambiente:
```python
DB_HOST     = localhost
DB_USER     = root
DB_PASSWORD = (vazio)
DB_NAME     = gerenciador_projetos
DB_PORT     = 3306
```

Ou usa defaults se não definidas.

---

## 🎯 CASOS DE USO

### 1. **Desenvolvimento Local**
```
$ python seed.py
# Agora tem dados para testar UI, APIs, etc
```

### 2. **Testes Automatizados**
```python
# test_endpoints.py usa dados do seed para validar
def test_listar_projetos():
    response = client.get("/projetos/")
    assert response.status_code == 200
    assert len(response.json()["projetos"]) >= 4  # Mín 4 projetos
```

### 3. **Demonstração**
```
Mostrar ao cliente 4 projetos reais:
- Edifício residencial (em obras)
- Shopping (reforma)
- Ponte (projeto grande)
- Casa (planejamento)
```

### 4. **Onboarding de Novos Devs**
```
Novo desenvolvedor executa:
$ git clone ...
$ cd database
$ python seed.py
$ python ../app.py
# Acessa localhost:8000 com dados já lá
```

---

## 🔄 FLUXO DE DADOS

```
Database vazio
    ↓
python seed.py
    ↓
CREATE INSERTs
    ├─ INSERT INTO usuarios (5 registros)
    ├─ INSERT INTO permissoes (6 registros)
    ├─ INSERT INTO projetos (4 registros)
    ├─ INSERT INTO equipes (10 registros)
    ├─ INSERT INTO tarefas (11 registros)
    └─ INSERT INTO materiais (6 registros)
    ↓
Database populado
    ↓
Pronto para testes/desenvolvimento
```

---

## 📊 ESTATÍSTICAS

| Entidade | Quantidade |
|----------|-----------|
| Usuários | 5 |
| Permissões | 6 |
| Projetos | 4 |
| Membros de Equipe | 10 |
| Tarefas | 11 |
| Materiais | 6 |
| Tarefas Concluídas | 3 |
| Tarefas em Andamento | 4 |
| Tarefas a Fazer | 4 |

**Total de registros:** 47

---

## ⚙️ DETALHES TÉCNICOS

### Segurança
- Senhas são **hasheadas com SHA-256** antes de gravar
- Nunca salva senhas em plain text
- Usa `hashlib.sha256()` (nativo Python)

### Relacionamentos
- Respeita **foreign keys** e constraints
- Ordem de inserção: usuarios → permissoes → projetos → ...
- Cada tabela depende das anteriores

### Dados Realistas
- Datas coerentes (passado ≤ agora)
- Orçamentos realistas para construção civil
- Nomes e emails de exemplo válidos
- Progressos com decimal (.5, .3, etc)

---

## 🔗 INTEGRAÇÃO COM TESTES

No `test_endpoints.py`:

```python
def test_listar_projetos():
    # Usa dados criados pelo seed
    response = client.get("/projetos/")
    assert response.status_code == 200
    assert len(response.json()["projetos"]) >= 4
    
def test_criar_tarefa():
    # Usa um projeto do seed (id=1)
    response = client.post(
        "/projetos/1/tarefas",
        json={"titulo": "Nova tarefa"}
    )
    assert response.status_code == 201
```

---

## 📝 PRÓXIMOS PASSOS OPCIONAIS

1. **Adicionar mais dados**
   - 10+ usuários (em vez de 5)
   - 20+ tarefas (em vez de 11)
   - Documentos e versões

2. **Dados por ambiente**
   - seed_dev.py (muitos dados)
   - seed_test.py (dados mínimos)
   - seed_prod.py (dados sensíveis)

3. **Fixtures pytest**
   - @pytest.fixture que chama seed
   - Cada teste tem dados limpos

4. **Faker library**
   - Gerar nomes/emails aleatórios
   - Dados mais variados

---

## ✅ CHECKLIST SEED

- [x] 5 usuários com dados realistas
- [x] 6 permissões do sistema
- [x] 4 projetos em diferentes status
- [x] 10 atribuições de equipe
- [x] 11 tarefas com histórico
- [x] 6 materiais com preços
- [x] Senhas hasheadas (SHA-256)
- [x] Foreign keys respeitadas
- [x] Documentação completa
- [x] Opção --clear para reset

---

**Status:** ✅ PRONTO PARA USO

Próxima Issue: **#36 - GitHub Actions CI/CD** (2-3h, último do lote!)
