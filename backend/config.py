"""
Configurações da API - Gerenciador de Projetos
"""

import os
import logging
from dotenv import load_dotenv

load_dotenv()

# ============================================
# CONFIGURAÇÃO DE LOGGING
# ============================================
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='[%(asctime)s] %(levelname)-8s %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class Settings:
    """Configurações da aplicação"""
    
    # Tipo de Banco de Dados (sqlite, mysql, postgresql)
    DB_TYPE: str = os.getenv("DB_TYPE", "sqlite").lower()
    
    # Banco de Dados MySQL
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "gerenciador_projetos")
    DB_PORT: int = int(os.getenv("DB_PORT", 3306))
    
    # Banco de Dados PostgreSQL
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "gerenciador_projetos")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", 5432))
    
    # Banco de Dados SQLite
    SQLITE_PATH: str = os.getenv("SQLITE_PATH", os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "database", "gerenciador.db"
    ))
    
    # Segurança JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "chave-desenvolvimento-insegura-mude-em-producao")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    
    # API
    API_PORT: int = int(os.getenv("PORT", os.getenv("API_PORT", 8000)))
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_TITLE: str = "API - Gerenciador de Projetos de Engenharia"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "API REST para gerenciamento de projetos de engenharia civil"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # CORS
    CORS_ORIGINS: list = (
        ["*"] if os.getenv("ENVIRONMENT") == "development"
        else os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")
    )
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # SendGrid Email
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    SENDGRID_FROM_EMAIL: str = os.getenv("SENDGRID_FROM_EMAIL", "noreply@gerenciador-projetos.com")
    SENDGRID_FROM_NAME: str = os.getenv("SENDGRID_FROM_NAME", "Gerenciador de Projetos")
    APP_URL: str = os.getenv("APP_URL", "http://localhost:3000")
    
    @property
    def db_config(self) -> dict:
        """Retorna configuração do banco de dados"""
        if self.DB_TYPE == "mysql":
            return {
                'host': self.DB_HOST,
                'user': self.DB_USER,
                'password': self.DB_PASSWORD,
                'database': self.DB_NAME,
                'port': self.DB_PORT,
                'charset': 'utf8mb4',
                'collation': 'utf8mb4_unicode_ci'
            }
        elif self.DB_TYPE == "postgresql":
            return {
                'host': self.POSTGRES_HOST,
                'user': self.POSTGRES_USER,
                'password': self.POSTGRES_PASSWORD,
                'database': self.POSTGRES_DB,
                'port': self.POSTGRES_PORT
            }
        else:
            return {
                'database': self.SQLITE_PATH
            }
    
    @property
    def is_sqlite(self) -> bool:
        """Verifica se está usando SQLite"""
        return self.DB_TYPE == "sqlite"
    
    @property
    def is_mysql(self) -> bool:
        """Verifica se está usando MySQL"""
        return self.DB_TYPE == "mysql"
    
    @property
    def is_postgresql(self) -> bool:
        """Verifica se está usando PostgreSQL"""
        return self.DB_TYPE == "postgresql"


settings = Settings()
