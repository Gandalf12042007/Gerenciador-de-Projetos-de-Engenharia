from datetime import datetime
from typing import Optional
from database.db_helper import get_db_connection

def registrar_auditoria(usuario_id: int, entidade: str, entidade_id: Optional[int], acao: str, detalhes: str = None, ip: str = None, user_agent: str = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO audit_trail (usuario_id, entidade, entidade_id, acao, detalhes, ip, user_agent, criado_em)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (usuario_id, entidade, entidade_id, acao, detalhes, ip, user_agent, datetime.utcnow())
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[AUDIT ERROR] {e}")
    finally:
        cursor.close()
        conn.close()
