"""
API - Gerenciador de Projetos de Engenharia Civil
Desenvolvido por: Vicente de Souza
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings

# Importar rotas
from routes import auth, projetos, tarefas, equipes

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rotas
app.include_router(auth.router)
app.include_router(projetos.router)
app.include_router(tarefas.router)
app.include_router(equipes.router)


@app.get("/")
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "API - Gerenciador de Projetos de Engenharia Civil",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "author": "Vicente de Souza"
    }


@app.get("/health")
async def health_check():
    """Health check da API"""
    return {"status": "healthy", "service": "api-gerenciador-projetos"}


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print(f"🚀 {settings.API_TITLE}")
    print(f"📝 Versão: {settings.API_VERSION}")
    print(f"👨‍💻 Desenvolvedor: Vicente de Souza")
    print("="*60)
    print(f"\n📍 API rodando em: http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"📚 Documentação: http://localhost:{settings.API_PORT}/docs")
    print(f"🔍 ReDoc: http://localhost:{settings.API_PORT}/redoc\n")
    
    uvicorn.run(
        "app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
