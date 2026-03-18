#!/usr/bin/env python3
"""
Aplica ajustes de compatibilidade no SQLite para o backend atual.

Este script resolve divergencias entre o schema antigo e o codigo:
- adiciona coluna `project_code` em `projetos`
- cria tabelas `auth_logs` e `failed_login_attempts`
- cria tabela `password_reset_tokens`
"""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "gerenciador.db")


def _column_exists(cursor: sqlite3.Cursor, table: str, column: str) -> bool:
    cursor.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cursor.fetchall()]
    return column in cols


def main() -> None:
    print(f"[INFO] DB: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # projeto: codigo de convite/acesso exigido por services/project_service.py
    if not _column_exists(cursor, "projetos", "project_code"):
        cursor.execute("ALTER TABLE projetos ADD COLUMN project_code TEXT")
        print("[OK] Coluna project_code adicionada em projetos")
    else:
        print("[OK] Coluna project_code ja existe")

    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_projetos_project_code ON projetos(project_code)"
    )
    print("[OK] Indice ux_projetos_project_code verificado")

    # tabelas de auditoria/autenticacao usadas por utils/security_audit.py
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS auth_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            acao TEXT NOT NULL,
            ip_address TEXT,
            sucesso INTEGER,
            motivo TEXT,
            timestamp TEXT DEFAULT (datetime('now', 'localtime'))
        )
        """
    )
    print("[OK] Tabela auth_logs verificada")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS failed_login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            ip_address TEXT,
            timestamp TEXT DEFAULT (datetime('now', 'localtime')),
            bloqueado_ate TEXT
        )
        """
    )
    print("[OK] Tabela failed_login_attempts verificada")

    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_failed_login_email_time ON failed_login_attempts(email, timestamp)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_auth_logs_email_time ON auth_logs(email, timestamp)"
    )

    # tabela de reset de senha usada por utils/password_reset.py
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            token_hash TEXT NOT NULL UNIQUE,
            expires_at TEXT NOT NULL,
            used INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            used_at TEXT,
            ip_address TEXT
        )
        """
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_password_reset_email ON password_reset_tokens(email)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_password_reset_token_hash ON password_reset_tokens(token_hash)"
    )
    print("[OK] Tabela password_reset_tokens verificada")

    conn.commit()
    conn.close()
    print("[DONE] Migracao de compatibilidade SQLite concluida")


if __name__ == "__main__":
    main()
