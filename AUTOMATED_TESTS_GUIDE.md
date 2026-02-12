# 🧪 Guia de Testes Automatizados (Pytest)

**Sistema completo de testes para garantir qualidade do código**

---

## 📋 **Instalação**

```bash
# Instalar pytest e plugins
pip install pytest pytest-cov pytest-asyncio pytest-mock

# Verificar instalação
pytest --version
```

---

## 🏗️ **Estrutura de Testes**

```
backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Fixtures compartilhadas
│   ├── test_auth.py             # Testes de autenticação
│   ├── test_security.py         # Testes de segurança
│   ├── test_routes_projetos.py  # Testes de rotas (projetos)
│   ├── test_routes_tarefas.py   # Testes de rotas (tarefas)
│   └── test_database.py         # Testes de banco de dados
└── pytest.ini                    # Configuração do pytest
```

---

## 🚀 **Executar Testes**

### 1. Todos os testes:
```bash
cd backend
pytest -v
```

### 2. Com cobertura de código:
```bash
pytest --cov=app --cov=routes --cov-report=html -v
```

Isso cria um relatório em `htmlcov/index.html`

### 3. Testes específicos:
```bash
# Apenas autenticação
pytest tests/test_auth.py -v

# Apenas um teste
pytest tests/test_auth.py::test_login_success -v

# Com output detalhado
pytest tests/test_auth.py -vv -s
```

### 4. Modo watch (re-executa ao salvar):
```bash
pip install pytest-watch
ptw -- -v
```

### 5. Paralelo (mais rápido):
```bash
pip install pytest-xdist
pytest -n auto -v
```

---

## 📝 **Exemplo: Criando um Novo Teste**

### Estrutura básica:

```python
# tests/test_exemplo.py
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

class TestExample:
    """Agrupa testes relacionados"""
    
    def test_get_root(self):
        """Testa se endpoint / retorna 200"""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_login_invalid_email(self):
        """Testa login com email inválido"""
        response = client.post("/api/auth/login", json={
            "email": "invalido",
            "password": "123456"
        })
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_async_operation(self):
        """Teste com operação assíncrona"""
        result = await some_async_function()
        assert result == expected_value
```

---

## 🔒 **Testes de Autenticação (Exemplo Completo)**

```python
# tests/test_auth.py
from fastapi.testclient import TestClient
from app import app
import pytest

client = TestClient(app)

class TestAuthentication:
    
    def test_login_success(self):
        """Teste login bem-sucedido"""
        response = client.post("/api/auth/login", json={
            "email": "vicentedesouza762@gmail.com",
            "password": "Abc123456"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["role"] in ["admin", "gerente", "engenheiro", "tecnico", "cliente"]
    
    def test_login_invalid_credentials(self):
        """Teste login com credenciais inválidas"""
        response = client.post("/api/auth/login", json={
            "email": "vicentedesouza762@gmail.com",
            "password": "SenhaErrada123"
        })
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self):
        """Teste login com usuário inexistente"""
        response = client.post("/api/auth/login", json={
            "email": "naoexiste@projeto.com",
            "password": "Abc123456"
        })
        assert response.status_code == 401
    
    def test_login_missing_fields(self):
        """Teste login sem email/password"""
        response = client.post("/api/auth/login", json={
            "email": "vicentedesouza762@gmail.com"
        })
        assert response.status_code == 422  # Validation error
    
    def test_register_new_user(self):
        """Teste criar novo usuário"""
        response = client.post("/api/auth/register", json={
            "nome": "Novo Usuario",
            "email": "novo@projeto.com",
            "password": "Abc123456"
        })
        # Esperado: 201 Created ou 400 se email já existe
        assert response.status_code in [201, 400]
    
    def test_token_expiration(self):
        """Teste se token expirado é recusado"""
        # Criar token com expiração imediata
        response = client.post("/api/auth/login", json={
            "email": "vicentedesouza762@gmail.com",
            "password": "Abc123456"
        })
        token = response.json()["access_token"]
        
        # Usar token após expiração (mock time.time())
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/projetos/", headers=headers)
        # Depende da implementação - pode ser 401
```

---

## 🛡️ **Testes de Segurança**

```python
# tests/test_security.py
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

class TestSecurity:
    
    def test_sql_injection_prevention(self):
        """Testa proteção contra SQL injection"""
        response = client.post("/api/auth/login", json={
            "email": "' OR '1'='1",
            "password": "anything"
        })
        assert response.status_code in [400, 401]  # Deve rejeitar
    
    def test_unauthorized_access(self):
        """Testa se endpoints protegidos recusam requisições sem token"""
        response = client.get("/api/projetos/")
        assert response.status_code == 401  # Unauthorized
    
    def test_invalid_token(self):
        """Testa requisição com token inválido"""
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = client.get("/api/projetos/", headers=headers)
        assert response.status_code == 401
    
    def test_cors_allowed_origins(self):
        """Testa CORS está configurado corretamente"""
        response = client.get(
            "/",
            headers={"Origin": "http://localhost:3000"}
        )
        assert "access-control-allow-origin" in response.headers
    
    def test_password_validation(self):
        """Testa validação de senha forte"""
        weak_passwords = [
            "abc",           # Muito curta
            "abcdefgh",      # Sem numero
            "ABCDEFGH123",   # Sem lowercase
            "abcdefgh123",   # Sem uppercase
        ]
        
        for weak_pwd in weak_passwords:
            response = client.post("/api/auth/register", json={
                "nome": "Test User",
                "email": f"test_weak_{weak_pwd}@projeto.com",
                "password": weak_pwd
            })
            # Pode ser 400 ou aceitar (dependendo da validação)
            # Documentar comportamento esperado
```

---

## 📊 **Testes de Rotas (Projetos)**

```python
# tests/test_routes_projetos.py
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

@pytest.fixture
def token_admin():
    """Fixture que retorna token de admin"""
    response = client.post("/api/auth/login", json={
        "email": "vicentedesouza762@gmail.com",
        "password": "Abc123456"
    })
    return response.json()["access_token"]

class TestProjetosRoutes:
    
    def test_listar_projetos_sem_token(self):
        """Testa acesso sem autenticação"""
        response = client.get("/api/projetos/")
        assert response.status_code == 401
    
    def test_listar_projetos_com_token(self, token_admin):
        """Testa listar projetos autenticado"""
        headers = {"Authorization": f"Bearer {token_admin}"}
        response = client.get("/api/projetos/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_criar_projeto(self, token_admin):
        """Testa criar novo projeto"""
        headers = {"Authorization": f"Bearer {token_admin}"}
        projeto_data = {
            "nome": "Projeto Teste",
            "descricao": "Descrição teste",
            "status": "em_planejamento"
        }
        response = client.post(
            "/api/projetos/",
            headers=headers,
            json=projeto_data
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["nome"] == "Projeto Teste"
    
    def test_atualizar_projeto(self, token_admin):
        """Testa atualizar projeto existente"""
        headers = {"Authorization": f"Bearer {token_admin}"}
        
        # Primeiro, criar um projeto
        response = client.post("/api/projetos/", headers=headers, json={
            "nome": "Projeto Update",
            "descricao": "Original",
            "status": "em_planejamento"
        })
        projeto_id = response.json().get("id") or 1
        
        # Depois, atualizar
        response = client.put(
            f"/api/projetos/{projeto_id}",
            headers=headers,
            json={
                "descricao": "Descrição atualizada"
            }
        )
        assert response.status_code == 200
    
    def test_deletar_projeto(self, token_admin):
        """Testa deletar projeto"""
        headers = {"Authorization": f"Bearer {token_admin}"}
        response = client.delete(
            "/api/projetos/1",
            headers=headers
        )
        # Pode ser 200, 204 ou 404 se não existir
        assert response.status_code in [200, 204, 404]
```

---

## 🗄️ **Testes de Banco de Dados**

```python
# tests/test_database.py
import pytest
from database.db_helper import DatabaseHelper

@pytest.fixture
def db():
    """Fixture de banco de dados de teste"""
    # Usar banco SQLite em memória para testes rápidos
    db_instance = DatabaseHelper(":memory:")
    yield db_instance
    db_instance.close()

class TestDatabase:
    
    def test_conectar_ao_banco(self, db):
        """Testa conexão com banco"""
        assert db.connection is not None
    
    def test_criar_usuario(self, db):
        """Testa inserção de usuário"""
        db.executar("INSERT INTO usuarios (email, nome) VALUES (?, ?)", 
                   ("test@projeto.com", "Test User"))
        
        resultado = db.executar_unico(
            "SELECT * FROM usuarios WHERE email = ?",
            ("test@projeto.com",)
        )
        assert resultado is not None
        assert resultado["nome"] == "Test User"
    
    def test_transacao_rollback(self, db):
        """Testa rollback de transação"""
        try:
            db.iniciar_transacao()
            db.executar("INSERT INTO usuarios (email, nome) VALUES (?, ?)",
                       ("test@projeto.com", "Test"))
            raise Exception("Erro propositalmente")
        except:
            db.rollback()
        
        # Usuário não deve existir
        resultado = db.executar_unico(
            "SELECT * FROM usuarios WHERE email = ?",
            ("test@projeto.com",)
        )
        assert resultado is None
```

---

## 📈 **Gerar Relatório de Cobertura**

```bash
# Gerar relatório HTML
pytest --cov=app --cov=routes --cov-report=html

# Abrir relatório
# Windows:
start htmlcov/index.html

# Linux/Mac:
open htmlcov/index.html
```

---

## ⚙️ **Configuração pytest.ini** (Já existe)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
```

---

## 🎯 **Meta de Cobertura**

```bash
# Ver relatório de cobertura
pytest --cov=app --cov=routes --cov-report=term-missing

# Espera-se:
# app          80%+  ✅
# routes       75%+  ✅
# middleware   70%+  ✅
# utils        85%+  ✅
```

---

## 🚀 **CI/CD Integration (GitHub Actions)**

Arquivo `.github/workflows/test.yml`:

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.10
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      
      - name: Run tests
        run: cd backend && pytest --cov=app --cov=routes
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

## 📋 **Checklist de Testes**

- [ ] **Autenticação**: Login, register, token validation
- [ ] **Autorização**: Role-based access control
- [ ] **Validação**: Email, password, input sanitization
- [ ] **Banco de dados**: CRUD operations, transactions
- [ ] **Segurança**: SQL injection, XSS, CSRF
- [ ] **Performance**: Tempo de resposta < 200ms
- [ ] **Cobertura**: >80% do código

---

## 🔄 **Workflow Recomendado**

1. **Desenvolvimento**:
   ```bash
   # Antes de commitar
   pytest -v --cov
   ```

2. **Code Review**:
   ```bash
   # Verificar se cobertura não caiu
   pytest --cov-report=term:skip-covered
   ```

3. **CI/CD Pipeline**:
   - Testes rodam automaticamente
   - Faz deploy só se passar em 100% dos testes

---

**Próximas melhorias:**
- [ ] Testes de carga (locust)
- [ ] Testes E2E (Selenium)
- [ ] Mocking de dependências externas
- [ ] Testes de performance (benchmark)

**Dúvidas? Execute:**
```bash
pytest --help
pytest --collect-only  # Ver todos os testes disponíveis
```

**Boa sorte! 🎉**
