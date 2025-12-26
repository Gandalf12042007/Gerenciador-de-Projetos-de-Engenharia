"""
Função de login simplificada para teste
"""
from fastapi import HTTPException, status
from datetime import timedelta
from utils.auth import create_access_token
from config import settings
import logging

logger = logging.getLogger(__name__)

# Usuários de teste hardcoded
USUARIOS_TESTE = {
    "teste01@gmail.com": {
        "id": 1,
        "nome": "Vicente de Souza", 
        "email": "teste01@gmail.com",
        "senha": "Teste123@",
        "telefone": "11 99999-0001",
        "cargo": "Administrador",
        "ativo": True
    },
    "francisco@gmail.com": {
        "id": 2,
        "nome": "Francisco",
        "email": "francisco@gmail.com", 
        "senha": "Teste123@",
        "telefone": "11 99999-0002",
        "cargo": "Desenvolvedor",
        "ativo": True
    }
}

def login_simples(credentials):
    """Login simplificado para teste"""
    
    # Verificar se é usuário de teste
    if credentials.email in USUARIOS_TESTE:
        user_teste = USUARIOS_TESTE[credentials.email]
        if credentials.senha == user_teste["senha"] and user_teste["ativo"]:
            # Criar token
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"user_id": user_teste["id"], "email": user_teste["email"], "nome": user_teste["nome"]},
                expires_delta=access_token_expires
            )
            
            logger.info(f"Login bem-sucedido (teste): {credentials.email}")
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user_id": user_teste["id"],
                "nome": user_teste["nome"],
                "email": user_teste["email"]
            }
    
    # Se não encontrou usuário de teste
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Email ou senha incorretos"
    )