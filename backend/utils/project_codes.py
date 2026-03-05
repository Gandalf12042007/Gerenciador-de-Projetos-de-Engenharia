"""
Utilitário para geração de códigos de projeto
Formato Profissional: ENG-2026-0001 (Prefixo + Ano + Sequencial)
Desenvolvido por: Vicente de Souza
"""

import random
import string
import sys
import os
from datetime import datetime

# Adicionar path do database
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'database'))
from db_helper import DatabaseHelper

# Prefixo padrão para projetos de engenharia
PREFIXO_PROJETO = "ENG"


def obter_proximo_numero_sequencial(ano: int = None) -> int:
    """
    Obtém o próximo número sequencial para o ano especificado.
    Analisa os códigos existentes no formato ENG-ANO-XXXX.
    
    Args:
        ano: Ano para buscar sequencial (padrão: ano atual)
        
    Returns:
        Próximo número sequencial disponível
    """
    if ano is None:
        ano = datetime.now().year
    
    db = DatabaseHelper()
    
    # Buscar maior número do ano atual
    resultado = db.execute_query(
        """
        SELECT codigo_acesso FROM projetos 
        WHERE codigo_acesso LIKE %s
        ORDER BY codigo_acesso DESC LIMIT 1
        """,
        (f"{PREFIXO_PROJETO}-{ano}-%",),
        fetch=True
    )
    
    if resultado and len(resultado) > 0:
        ultimo_codigo = resultado[0].get('codigo_acesso', '')
        try:
            # Extrair número sequencial do código (última parte)
            partes = ultimo_codigo.split('-')
            if len(partes) == 3:
                ultimo_num = int(partes[2])
                return ultimo_num + 1
        except (ValueError, IndexError):
            pass
    
    # Primeiro projeto do ano
    return 1


def gerar_codigo_projeto(ano: int = None) -> str:
    """
    Gera um código único para projeto no formato profissional.
    Formato: ENG-2026-0001
    
    - ENG: Prefixo fixo (Engenharia)
    - 2026: Ano atual
    - 0001: Número sequencial (4 dígitos com zeros à esquerda)
    
    Args:
        ano: Ano para o código (padrão: ano atual)
        
    Returns:
        Código no formato ENG-AAAA-NNNN
    """
    if ano is None:
        ano = datetime.now().year
    
    numero = obter_proximo_numero_sequencial(ano)
    return f"{PREFIXO_PROJETO}-{ano}-{numero:04d}"


def gerar_codigo_unico() -> str:
    """
    Gera um código garantidamente único verificando no banco.
    Formato: ENG-2026-0001
    """
    db = DatabaseHelper()
    max_tentativas = 100
    ano = datetime.now().year
    
    for _ in range(max_tentativas):
        codigo = gerar_codigo_projeto(ano)
        
        # Verifica se já existe no banco
        existente = db.execute_query(
            "SELECT id FROM projetos WHERE codigo_acesso = %s",
            (codigo,),
            fetch=True
        )
        
        if not existente or len(existente) == 0:
            return codigo
        
        # Se existe, força incremento
        numero = obter_proximo_numero_sequencial(ano)
    
    # Fallback extremo com timestamp
    return f"{PREFIXO_PROJETO}-{ano}-{int(datetime.now().timestamp()) % 10000:04d}"


def gerar_codigo_legado():
    """
    Gera um código no formato legado (LETRA + 4 NÚMEROS).
    Mantido para compatibilidade.
    Formato: A1234, B9876, X4521
    """
    letra = random.choice(string.ascii_uppercase)
    numeros = random.randint(1000, 9999)
    return f"{letra}{numeros}"


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
