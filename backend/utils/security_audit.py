"""
Utilitários de Segurança - Rate Limit e Auditoria de Autenticação
Bloqueia tentativas excessivas de login
Mantém histórico de acessos
"""

import sqlite3
from datetime import datetime, timedelta
import os
import sys

# Adicionar path do database
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'database'))

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'gerenciador.db')

MAX_FAILED_ATTEMPTS = 3
LOCKOUT_MINUTES = 15

def registro_log_auth(email: str, acao: str, sucesso: bool, ip_address: str = None, motivo: str = None):
    """
    Registra tentativa de autenticação no banco
    
    Args:
        email: Email do usuário
        acao: 'login_tentativa', 'login_sucesso', 'logout', etc
        sucesso: True se bem-sucedido
        ip_address: IP da requisição (opcional)
        motivo: Motivo da falha (opcional)
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO auth_logs (email, acao, ip_address, sucesso, motivo, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            email.lower(),
            acao,
            ip_address,
            sucesso,
            motivo,
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"⚠️ Erro ao registrar log: {e}")

def registrar_tentativa_falhada(email: str, ip_address: str = None):
    """
    Registra tentativa falhada de login
    Bloqueia conta se passar de 3 tentativas
    
    Args:
        email: Email do usuário
        ip_address: IP da requisição (opcional)
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Inserir tentativa falhada
        cursor.execute('''
            INSERT INTO failed_login_attempts (email, ip_address, timestamp)
            VALUES (?, ?, ?)
        ''', (email.lower(), ip_address, datetime.now()))
        
        # Contar tentativas dos últimos 15 minutos
        tempo_limite = datetime.now() - timedelta(minutes=LOCKOUT_MINUTES)
        cursor.execute('''
            SELECT COUNT(*) FROM failed_login_attempts
            WHERE email = ? AND timestamp > ?
        ''', (email.lower(), tempo_limite))
        
        count = cursor.fetchone()[0]
        
        # Se passou de 3, bloquear por 15 minutos
        if count >= MAX_FAILED_ATTEMPTS:
            bloqueado_ate = datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)
            cursor.execute('''
                UPDATE failed_login_attempts
                SET bloqueado_ate = ?
                WHERE email = ? AND bloqueado_ate IS NULL
            ''', (bloqueado_ate, email.lower()))
        
        conn.commit()
        conn.close()
        
        return count
        
    except Exception as e:
        print(f"⚠️ Erro ao registrar tentativa falhada: {e}")
        return 0

def esta_bloqueado(email: str) -> bool:
    """
    Verifica se email está bloqueado por

 rate limit
    
    Args:
        email: Email do usuário
        
    Returns:
        True se está bloqueado, False senão
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT bloqueado_ate FROM failed_login_attempts
            WHERE email = ? AND bloqueado_ate IS NOT NULL
            ORDER BY bloqueado_ate DESC
            LIMIT 1
        ''', (email.lower(),))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            bloqueado_ate = datetime.fromisoformat(result[0])
            return datetime.now() < bloqueado_ate
        
        return False
        
    except Exception as e:
        print(f"⚠️ Erro ao verificar bloqueio: {e}")
        return False

def tempo_ate_desbloquear(email: str) -> int:
    """
    Retorna quantos minutos faltam para desbloquear
    
    Args:
        email: Email do usuário
        
    Returns:
        Minutos até desbloquear (0 se não está bloqueado)
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT bloqueado_ate FROM failed_login_attempts
            WHERE email = ? AND bloqueado_ate IS NOT NULL
            ORDER BY bloqueado_ate DESC
            LIMIT 1
        ''', (email.lower(),))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            bloqueado_ate = datetime.fromisoformat(result[0])
            diferenca = bloqueado_ate - datetime.now()
            minutos = int(diferenca.total_seconds() / 60)
            return max(0, minutos)
        
        return 0
        
    except Exception as e:
        print(f"⚠️ Erro ao calcular tempo: {e}")
        return 0

def limpar_tentativas_antigas():
    """
    Limpa tentativas de login com mais de 24 horas
    Deve ser chamado periodicamente
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        tempo_limite = datetime.now() - timedelta(hours=24)
        
        cursor.execute('''
            DELETE FROM failed_login_attempts
            WHERE timestamp < ?
        ''', (tempo_limite,))
        
        deletados = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deletados > 0:
            print(f"✅ Limpas {deletados} tentativas antigas")
        
        return deletados
        
    except Exception as e:
        print(f"⚠️ Erro ao limpar tentativas: {e}")
        return 0

def limpar_logs_antigos(dias=30):
    """
    Limpa logs com mais de X dias
    
    Args:
        dias: Número de dias a manter (padrão: 30)
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        tempo_limite = datetime.now() - timedelta(days=dias)
        
        cursor.execute('''
            DELETE FROM auth_logs
            WHERE timestamp < ?
        ''', (tempo_limite,))
        
        deletados = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deletados > 0:
            print(f"✅ Limpos {deletados} logs com mais de {dias} dias")
        
        return deletados
        
    except Exception as e:
        print(f"⚠️ Erro ao limpar logs: {e}")
        return 0

def obter_ultimos_logs(email: str = None, limit: int = 10):
    """
    Obtém últimos logs de autenticação
    
    Args:
        email: Email específico ou None para todos
        limit: Limite de registros
        
    Returns:
        Lista de dicts com logs
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        if email:
            cursor.execute('''
                SELECT email, acao, sucesso, motivo, timestamp
                FROM auth_logs
                WHERE email = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (email.lower(), limit))
        else:
            cursor.execute('''
                SELECT email, acao, sucesso, motivo, timestamp
                FROM auth_logs
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        logs = []
        for row in rows:
            logs.append({
                'email': row[0],
                'acao': row[1],
                'sucesso': row[2],
                'motivo': row[3],
                'timestamp': row[4]
            })
        
        return logs
        
    except Exception as e:
        print(f"⚠️ Erro ao obter logs: {e}")
        return []
