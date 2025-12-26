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
    
    # Banco de Dados
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "gerenciador_projetos")
    DB_PORT: int = int(os.getenv("DB_PORT", 3306))
    
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
    
    @property
    def db_config(self) -> dict:
        """Retorna configuração do banco de dados"""
        return {
            'host': self.DB_HOST,
            'user': self.DB_USER,
            'password': self.DB_PASSWORD,
            'database': self.DB_NAME,
            'port': self.DB_PORT,
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci'
        }


settings = Settings()
