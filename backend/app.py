"""
API - Gerenciador de Projetos de Engenharia Civil
Desenvolvido por: Vicente de Souza
"""

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.exceptions import RequestValidationError
from config import settings
from middleware.rate_limit import limiter, rate_limit_exception_handler
from slowapi.errors import RateLimitExceeded
from openapi_config import custom_openapi

# Importar rotas
from routes import auth, projetos, tarefas, equipes, documentos, materiais, orcamentos, chat, metricas, notificacoes

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Customizar OpenAPI/Swagger com documentação detalhada
app.openapi = lambda: custom_openapi(app)

# Adicionar middleware de rate limiting
app.state.limiter = limiter

# Registrar handler de rate limiting
app.add_exception_handler(RateLimitExceeded, rate_limit_exception_handler)

# Configurar CORS
# Desenvolvimento: permite tudo (*) 
# Produção: apenas domínios específicos
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
app.include_router(documentos.router)
app.include_router(materiais.router)
app.include_router(orcamentos.router)
app.include_router(chat.router)
app.include_router(metricas.router)
app.include_router(notificacoes.router)


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


# ===== SERVIR FRONTEND ESTÁTICO =====
# Diretório do frontend
WEB_DIR = Path(__file__).parent.parent / "web"

# Montar arquivos estáticos se o diretório existir
if WEB_DIR.exists():
    # Arquivos assets (imagens, css de assets)
    assets_dir = WEB_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
    
    # Diretório de estilos globais
    styles_dir = WEB_DIR / "styles"
    if styles_dir.exists():
        app.mount("/styles", StaticFiles(directory=str(styles_dir)), name="styles")
    
    # Arquivos de projetos (CSS, JS específicos)
    projects_dir = WEB_DIR / "projects"
    if projects_dir.exists():
        app.mount("/projects", StaticFiles(directory=str(projects_dir), html=True), name="projects")
    
    # Rota para servir arquivos JS e CSS na raiz
    @app.get("/api-client.js")
    async def serve_api_client():
        """Serve o api-client.js"""
        return FileResponse(WEB_DIR / "api-client.js", media_type="application/javascript")
    
    @app.get("/app.js")
    async def serve_app_js():
        """Serve o app.js"""
        return FileResponse(WEB_DIR / "app.js", media_type="application/javascript")
    
    @app.get("/styles.css")
    async def serve_styles():
        """Serve o styles.css"""
        return FileResponse(WEB_DIR / "styles.css", media_type="text/css")
    
    # Rota para servir index.html na raiz
    @app.get("/app")
    async def serve_app():
        """Redireciona para o frontend"""
        index_file = WEB_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"error": "Frontend not found"}
    
    # Servir login.html (ambas rotas: /login e /login.html)
    @app.get("/login")
    async def serve_login():
        login_file = WEB_DIR / "login.html"
        if login_file.exists():
            return FileResponse(login_file, media_type="text/html")
        return {"error": "Login page not found"}
    
    @app.get("/login.html")
    async def serve_login_html():
        login_file = WEB_DIR / "login.html"
        if login_file.exists():
            return FileResponse(login_file, media_type="text/html")
        return {"error": "Login page not found"}
    
    # Servir register.html
    @app.get("/register")
    async def serve_register():
        register_file = WEB_DIR / "register.html"
        if register_file.exists():
            return FileResponse(register_file, media_type="text/html")
        return {"error": "Register page not found"}
    
    @app.get("/register.html")
    async def serve_register_html():
        register_file = WEB_DIR / "register.html"
        if register_file.exists():
            return FileResponse(register_file, media_type="text/html")
        return {"error": "Register page not found"}
    
    # Servir entrar-projeto.html
    @app.get("/entrar-projeto")
    async def serve_entrar_projeto():
        file = WEB_DIR / "entrar-projeto.html"
        if file.exists():
            return FileResponse(file, media_type="text/html")
        return {"error": "Page not found"}
    
    @app.get("/entrar-projeto.html")
    async def serve_entrar_projeto_html():
        file = WEB_DIR / "entrar-projeto.html"
        if file.exists():
            return FileResponse(file, media_type="text/html")
        return {"error": "Page not found"}
    
    # Servir forgot-password.html
    @app.get("/forgot-password")
    async def serve_forgot_password():
        forgot_file = WEB_DIR / "forgot-password.html"
        if forgot_file.exists():
            return FileResponse(forgot_file, media_type="text/html")
        return {"error": "Forgot password page not found"}
    
    @app.get("/forgot-password.html")
    async def serve_forgot_password_html():
        forgot_file = WEB_DIR / "forgot-password.html"
        if forgot_file.exists():
            return FileResponse(forgot_file, media_type="text/html")
        return {"error": "Forgot password page not found"}


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
