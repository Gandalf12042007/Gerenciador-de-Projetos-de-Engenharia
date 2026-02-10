"""
Utilitário para geração de códigos de projeto
Formato: LETRA + 4 NÚMEROS (ex: A1234, B9876)
"""

import random
import string
import sys
import os

# Adicionar path do database
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'database'))
from db_helper import DatabaseHelper


def gerar_codigo_projeto():
    """
    Gera um código único para projeto.
    Formato: UMA LETRA MAIÚSCULA + 4 NÚMEROS
    Exemplo: A1234, B9876, X4521
    """
    letra = random.choice(string.ascii_uppercase)
    numeros = random.randint(1000, 9999)
    return f"{letra}{numeros}"


def gerar_codigo_unico():
    """
    Gera um código garantidamente único verificando no banco.
    """
    db = DatabaseHelper()
    max_tentativas = 100
    
    for _ in range(max_tentativas):
        codigo = gerar_codigo_projeto()
        
        # Verifica se já existe no banco
        existente = db.execute_query(
            "SELECT id FROM projetos WHERE codigo_acesso = %s",
            (codigo,),
            fetch=True
        )
        
        if not existente or len(existente) == 0:
            return codigo
    
    # Fallback com mais caracteres se necessário
    return f"{random.choice(string.ascii_uppercase)}{random.randint(10000, 99999)}"


def validar_formato_codigo(codigo: str) -> bool:
    """
    Valida se o código está no formato correto.
    Formato esperado: 1 letra maiúscula + 4 números
    """
    if not codigo or len(codigo) != 5:
        return False
    
    if not codigo[0].isalpha():
        return False
    
    if not codigo[1:].isdigit():
        return False
    
    return True


def buscar_projeto_por_codigo(codigo: str):
    """
    Busca um projeto pelo código de acesso.
    """
    if not validar_formato_codigo(codigo.upper()):
        return None
    
    db = DatabaseHelper()
    projeto = db.execute_query(
        """
        SELECT id, nome, descricao, cliente, status, codigo_acesso
        FROM projetos 
        WHERE codigo_acesso = %s
        """,
        (codigo.upper(),),
        fetch=True
    )
    
    if projeto and len(projeto) > 0:
        return projeto[0]
    return None


def adicionar_usuario_ao_projeto(projeto_id: int, usuario_id: int, funcao: str = "membro"):
    """
    Adiciona um usuário à equipe de um projeto.
    """
    db = DatabaseHelper()
    
    # Verifica se já é membro
    membro = db.execute_query(
        "SELECT id FROM equipes WHERE projeto_id = %s AND usuario_id = %s",
        (projeto_id, usuario_id),
        fetch=True
    )
    
    if membro and len(membro) > 0:
        # Reativa se estava inativo
        db.execute_query(
            "UPDATE equipes SET ativo = 1, funcao = %s WHERE projeto_id = %s AND usuario_id = %s",
            (funcao, projeto_id, usuario_id)
        )
        return {"status": "reativado", "message": "Acesso ao projeto restaurado"}
    
    # Adiciona novo membro
    db.execute_query(
        """
        INSERT INTO equipes (projeto_id, usuario_id, funcao, ativo)
        VALUES (%s, %s, %s, 1)
        """,
        (projeto_id, usuario_id, funcao)
    )
    
    return {"status": "adicionado", "message": "Você foi adicionado ao projeto com sucesso"}
