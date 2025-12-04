"""
Teste simples do servidor - sem banco de dados
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="API - Teste Gerenciador de Projetos",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "✅ API está funcionando!",
        "desenvolvedor": "Vicente de Souza",
        "status": "online"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/projetos")
async def projetos_mock():
    return {
        "projetos": [
            {
                "id": 1,
                "nome": "Residencial Vista Verde",
                "status": "em_andamento",
                "progresso": 45
            },
            {
                "id": 2,
                "nome": "Ponte Rio Verde",
                "status": "planejamento",
                "progresso": 15
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 Teste do Servidor FastAPI")
    print("📍 API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("="*60 + "\n")
    
    uvicorn.run("test_server:app", host="0.0.0.0", port=8000, reload=True)
