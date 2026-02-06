"""
Configuração de Testes - pytest
"""

import os
import sys
import pytest
from pathlib import Path

# Adicionar paths do projeto
TEST_DIR = Path(__file__).parent
BACKEND_DIR = TEST_DIR.parent
DATABASE_DIR = BACKEND_DIR.parent / "database"

sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(DATABASE_DIR))

# Configurar ambiente de testes
os.environ["ENVIRONMENT"] = "test"
os.environ["DB_TYPE"] = "sqlite"
os.environ["SQLITE_PATH"] = ":memory:"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["DEBUG"] = "True"


@pytest.fixture(scope="session")
def test_db():
    """Cria banco de dados de teste em memória"""
    from db_helper import DatabaseHelper
    
    db = DatabaseHelper()
    
    # Criar tabelas básicas
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE,
            senha TEXT NOT NULL,
            cargo TEXT DEFAULT 'engenheiro',
            is_admin INTEGER DEFAULT 0,
            ativo INTEGER DEFAULT 1,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            ultimo_login DATETIME
        )
    """)
    
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS projetos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            endereco TEXT,
            cliente TEXT,
            valor_total REAL,
            data_inicio DATE,
            data_fim_prevista DATE,
            data_fim_real DATE,
            status TEXT DEFAULT 'planejamento',
            progresso_percentual REAL DEFAULT 0,
            criador_id INTEGER,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (criador_id) REFERENCES usuarios(id)
        )
    """)
    
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS equipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            projeto_id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            cargo TEXT DEFAULT 'membro',
            ativo INTEGER DEFAULT 1,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (projeto_id) REFERENCES projetos(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)
    
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            projeto_id INTEGER NOT NULL,
            titulo TEXT NOT NULL,
            descricao TEXT,
            responsavel_id INTEGER,
            prioridade TEXT DEFAULT 'media',
            status TEXT DEFAULT 'pendente',
            data_limite DATE,
            estimativa_horas REAL,
            horas_trabalhadas REAL DEFAULT 0,
            ordem INTEGER DEFAULT 0,
            criador_id INTEGER,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (projeto_id) REFERENCES projetos(id),
            FOREIGN KEY (responsavel_id) REFERENCES usuarios(id)
        )
    """)
    
    yield db


@pytest.fixture
def test_user(test_db):
    """Cria usuário de teste"""
    import hashlib
    
    password_hash = hashlib.sha256("test123".encode()).hexdigest()
    
    try:
        user_id = test_db.execute_query(
            "INSERT INTO usuarios (nome, email, username, senha, is_admin) VALUES (?, ?, ?, ?, ?)",
            ("Test User", "test@test.com", "testuser", password_hash, 0)
        )
    except:
        # Usuário já existe
        result = test_db.execute_query(
            "SELECT id FROM usuarios WHERE email = ?",
            ("test@test.com",),
            fetch=True
        )
        user_id = result[0]['id'] if result else 1
    
    return {
        "id": user_id,
        "nome": "Test User",
        "email": "test@test.com",
        "username": "testuser",
        "is_admin": False
    }


@pytest.fixture
def admin_user(test_db):
    """Cria usuário admin de teste"""
    import hashlib
    
    password_hash = hashlib.sha256("admin123".encode()).hexdigest()
    
    try:
        user_id = test_db.execute_query(
            "INSERT INTO usuarios (nome, email, username, senha, is_admin) VALUES (?, ?, ?, ?, ?)",
            ("Admin User", "admin@test.com", "adminuser", password_hash, 1)
        )
    except:
        result = test_db.execute_query(
            "SELECT id FROM usuarios WHERE email = ?",
            ("admin@test.com",),
            fetch=True
        )
        user_id = result[0]['id'] if result else 2
    
    return {
        "id": user_id,
        "nome": "Admin User",
        "email": "admin@test.com",
        "username": "adminuser",
        "is_admin": True
    }


@pytest.fixture
def test_project(test_db, test_user):
    """Cria projeto de teste"""
    try:
        project_id = test_db.execute_query(
            """INSERT INTO projetos (nome, descricao, status, criador_id) 
               VALUES (?, ?, ?, ?)""",
            ("Projeto Teste", "Descrição do projeto", "em_andamento", test_user["id"])
        )
        
        # Adicionar criador à equipe
        test_db.execute_query(
            "INSERT INTO equipes (projeto_id, usuario_id, cargo) VALUES (?, ?, ?)",
            (project_id, test_user["id"], "gerente")
        )
    except:
        result = test_db.execute_query(
            "SELECT id FROM projetos WHERE nome = ?",
            ("Projeto Teste",),
            fetch=True
        )
        project_id = result[0]['id'] if result else 1
    
    return {
        "id": project_id,
        "nome": "Projeto Teste",
        "descricao": "Descrição do projeto",
        "status": "em_andamento",
        "criador_id": test_user["id"]
    }


@pytest.fixture
def auth_token(test_user):
    """Gera token JWT para testes"""
    import jwt
    from datetime import datetime, timedelta
    
    token_data = {
        "id": test_user["id"],
        "user_id": test_user["id"],
        "email": test_user["email"],
        "nome": test_user["nome"],
        "is_admin": test_user["is_admin"],
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    
    token = jwt.encode(token_data, os.environ["SECRET_KEY"], algorithm="HS256")
    return token


@pytest.fixture
def api_client():
    """Cliente de teste FastAPI"""
    from fastapi.testclient import TestClient
    from app import app
    
    return TestClient(app)
