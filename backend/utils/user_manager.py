"""
Gerenciamento de Usuários - Buscar do Banco de Dados
Substitui o dicionário hardcoded USUARIOS_ADMIN
"""

import sqlite3
import os
import sys

# Adicionar path do database
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'database'))

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'gerenciador.db')

def obter_usuario_por_email(email: str) -> dict:
    """
    Busca usuário no banco pela email
    
    Args:
        email: Email do usuário (será normalizado para lowercase)
        
    Returns:
        Dict com dados do usuário ou None
    """
    try:
        email_normalized = email.lower()
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, nome, email, senha_hash, telefone, cargo, role, ativo, ultimo_login
            FROM usuarios_new
            WHERE email = ? AND ativo = TRUE
        ''', (email_normalized,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        
        return None
        
    except Exception as e:
        print(f"❌ Erro ao buscar usuário: {e}")
        return None

def usuario_existe(email: str) -> bool:
    """
    Verifica se usuário existe
    
    Args:
        email: Email do usuário
        
    Returns:
        True se existe, False senão
    """
    usuario = obter_usuario_por_email(email)
    return usuario is not None

def atualizar_ultimo_login(email: str):
    """
    Atualiza timestamp do último login
    
    Args:
        email: Email do usuário
    """
    try:
        from datetime import datetime
        
        email_normalized = email.lower()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE usuarios_new
            SET ultimo_login = ?
            WHERE email = ?
        ''', (datetime.now(), email_normalized))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"⚠️ Erro ao atualizar último login: {e}")

def listar_usuarios(role: str = None, limit: int = 100):
    """
    Lista usuários do banco
    
    Args:
        role: Filtrar por role (admin, gerente, etc) ou None para todos
        limit: Máximo de registros
        
    Returns:
        Lista de dicts com usuários
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if role:
            cursor.execute('''
                SELECT id, nome, email, cargo, role, ativo, ultimo_login
                FROM usuarios_new
                WHERE role = ?
                ORDER BY nome
                LIMIT ?
            ''', (role, limit))
        else:
            cursor.execute('''
                SELECT id, nome, email, cargo, role, ativo, ultimo_login
                FROM usuarios_new
                ORDER BY nome
                LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        usuarios = [dict(row) for row in rows]
        return usuarios
        
    except Exception as e:
        print(f"❌ Erro ao listar usuários: {e}")
        return []

def criar_usuario(nome: str, email: str, senha_hash: str, cargo: str, role: str, telefone: str = None) -> bool:
    """
    Cria novo usuário no banco
    
    Args:
        nome: Nome completo
        email: Email único
        senha_hash: Hash bcrypt da senha
        cargo: Cargo/função
        role: Papel (admin, gerente, engenheiro, etc)
        telefone: Telefone opcional
        
    Returns:
        True se criado, False se erro
    """
    try:
        email_normalized = email.lower()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO usuarios_new (nome, email, senha_hash, telefone, cargo, role, ativo)
            VALUES (?, ?, ?, ?, ?, ?, TRUE)
        ''', (nome, email_normalized, senha_hash, telefone, cargo, role))
        
        conn.commit()
        conn.close()
        
        return True
        
    except sqlite3.IntegrityError:
        print(f"❌ Erro: Email {email} já existe")
        return False
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        return False

def atualizar_usuario(email: str, **kwargs) -> bool:
    """
    Atualiza dados do usuário
    
    Args:
        email: Email do usuário
        **kwargs: Campos a atualizar (nome, cargo, role, ativo, etc)
        
    Returns:
        True se atualizado, False se erro
    """
    try:
        email_normalized = email.lower()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Construir SET dinamicamente
        campos = []
        valores = []
        for key, value in kwargs.items():
            if key in ['nome', 'cargo', 'role', 'ativo', 'telefone']:
                campos.append(f"{key} = ?")
                valores.append(value)
        
        if not campos:
            return False
        
        valores.append(email_normalized)
        
        query = f'''
            UPDATE usuarios_new
            SET {', '.join(campos)}
            WHERE email = ?
        '''
        
        cursor.execute(query, valores)
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
        
    except Exception as e:
        print(f"❌ Erro ao atualizar usuário: {e}")
        return False

def contar_usuarios(role: str = None) -> int:
    """
    Conta total de usuários
    
    Args:
        role: Filtrar por role ou None para todos
        
    Returns:
        Número de usuários
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        if role:
            cursor.execute('SELECT COUNT(*) FROM usuarios_new WHERE role = ?', (role,))
        else:
            cursor.execute('SELECT COUNT(*) FROM usuarios_new')
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
        
    except Exception as e:
        print(f"❌ Erro ao contar usuários: {e}")
        return 0
