# 🏗️ Guia de Arquitetura -  Microserviços

**Transformar monolito em arquitetura escalável de microserviços**

---

## 📋 **Visão Geral da Migração**

### Antes (Monolito):
```
┌─────────────────────────────────────┐
│  FastAPI Monolítico (um único app)  │
├─────────────────────────────────────┤
│  • Auth                             │
│  • Projetos                         │
│  • Tarefas                          │
│  • Chat                             │
│  • IA/Sugestões                     │
│  • Financeiro                       │
│  • Notificações                     │
│  • Relatórios                       │
└─────────────────────────────────────┘
        ↓         ↓         ↓
    PostgreSQL  Redis  S3/Storage
```

### Depois (Microserviços):
```
┌─────────────┐  ┌─────────────┐  ┌──────────────┐
│   API       │  │   Chat      │  │   IA         │
│  Gateway    │  │  Service    │  │  Service     │
└──────┬──────┘  └──────┬──────┘  └──────┬───────┘
       │                │                │
       └────────┬───────┴────────┬───────┘
                │                │
       ┌────────┴──────┐  ┌──────┴────────┐
       │   Message     │  │   Service    │
       │   Queue       │  │  Registry    │
       │  (RabbitMQ)   │  │  (Consul)    │
       └───────────────┘  └──────────────┘
                │
       ┌────────┴──────────────┬────────────┐
       │                       │            │
    PostgreSQL               Redis        S3
```

---

## 🎯 **Serviços a Criar**

### 1. **API Gateway** (FastAPI)
- Ponto único de entrada
- Roteamento de requisições
- Autenticação centralizada
- Rate limiting
- Logging/Monitoring

### 2. **Auth Service** (FastAPI)
- Login/Logout
- Token Generation
- 2FA
- Gerenciamento de usuários

### 3. **Core Service** (FastAPI)
- Projetos
- Tarefas
- Documentos
- Equipes

### 4. **Chat Service** (FastAPI + WebSocket)
- Mensagens em tempo real
- Histórico
- Notificações

### 5. **IA Service** (FastAPI + Python)
- Sugestões de tarefas
- Análise de riscos
- Recomendações

### 6. **Financeiro Service** (FastAPI)
- Custos
- Orçamentos
- Faturas
- Relatórios

### 7. **Notificações Service** (Celery)
- Email
- Push notifications
- In-app notifications

---

## 🏗️ **Passo 1: Criar Estrutura de Pastas**

```
gerenciador-projetos-microservices/
├── api-gateway/
│   ├── main.py
│   ├── config.py
│   ├── routes/
│   │   ├── router.py
│   │   └── middleware.py
│   └── requirements.txt
│
├── auth-service/
│   ├── main.py
│   ├── models.py
│   ├── routes/
│   └── requirements.txt
│
├── core-service/
│   ├── main.py
│   ├── models.py
│   ├── routes/
│   │   ├── projetos.py
│   │   ├── tarefas.py
│   │   └── documentos.py
│   └── requirements.txt
│
├── chat-service/
│   ├── main.py
│   ├── models.py
│   ├── websocket/
│   │   └── handler.py
│   └── requirements.txt
│
├── ia-service/
│   ├── main.py
│   ├── ml/
│   │   ├── sugestoes.py
│   │   └── analise.py
│   └── requirements.txt
│
├── financeiro-service/
│   ├── main.py
│   ├── models.py
│   ├── routes/
│   └── requirements.txt
│
├── notificacoes-service/
│   ├── tasks.py
│   ├── email/
│   └── requirements.txt
│
├── shared/
│   ├── schemas.py        # Schemas compartilhadas
│   ├── utils.py          # Utilitários
│   └── config.py         # Configuração comum
│
├── docker-compose.yml     # Orquestração
├── .env.example
└── README.md
```

---

## 🔌 **Passo 2: API Gateway (Roteador Central)**

Criar `api-gateway/main.py`:

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
import os
from datetime import datetime

app = FastAPI(title="API Gateway")

# URLs dos serviços
SERVICES = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001"),
    "core": os.getenv("CORE_SERVICE_URL", "http://core-service:8002"),
    "chat": os.getenv("CHAT_SERVICE_URL", "http://chat-service:8003"),
    "ia": os.getenv("IA_SERVICE_URL", "http://ia-service:8004"),
    "financeiro": os.getenv("FINANCEIRO_SERVICE_URL", "http://financeiro-service:8005"),
}

# Cliente HTTP
client = httpx.AsyncClient(timeout=30.0)

# ============ MIDDLEWARE ============

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log todas as requisições"""
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] {request.method} {request.url.path}")
    
    response = await call_next(request)
    print(f"[{timestamp}] Response: {response.status_code}")
    return response

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """Validar token em rotas protegidas"""
    # Rotas públicas que não precisam de token
    public_routes = ["/health", "/auth/login", "/auth/register"]
    
    if request.url.path in public_routes:
        return await call_next(request)
    
    # Verificar token
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return JSONResponse(
            status_code=401,
            content={"detail": "Token de autenticação não fornecido"}
        )
    
    # Validar token no Auth Service (pode fazer cache)
    try:
        response = await client.post(
            f"{SERVICES['auth']}/validate-token",
            headers={"Authorization": auth_header}
        )
        
        if response.status_code != 200:
            return JSONResponse(status_code=401, content={"detail": "Token inválido"})
        
        # Adicionar usuário ao request
        request.state.user = response.json()
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})
    
    return await call_next(request)

# ============ ROTEAMENTO ============

@app.get("/health")
async def health_check():
    """Health check do gateway"""
    return {
        "status": "ok",
        "gateway": "operational",
        "timestamp": datetime.now().isoformat()
    }

# Roteamento para AUTH SERVICE
@app.post("/auth/login")
async def login(credentials: dict):
    response = await client.post(
        f"{SERVICES['auth']}/login",
        json=credentials
    )
    return response.json()

# Roteamento para CORE SERVICE
@app.get("/projetos/")
async def listar_projetos(request: Request):
    token = request.headers.get("Authorization")
    response = await client.get(
        f"{SERVICES['core']}/projetos/",
        headers={"Authorization": token}
    )
    return response.json()

@app.post("/projetos/")
async def criar_projeto(request: Request, projeto_data: dict):
    token = request.headers.get("Authorization")
    response = await client.post(
        f"{SERVICES['core']}/projetos/",
        json=projeto_data,
        headers={"Authorization": token}
    )
    return response.json()

# Roteamento para CHAT SERVICE
@app.get("/chat/mensagens/{projeto_id}")
async def listar_mensagens(projeto_id: int, request: Request):
    token = request.headers.get("Authorization")
    response = await client.get(
        f"{SERVICES['chat']}/mensagens/{projeto_id}",
        headers={"Authorization": token}
    )
    return response.json()

@app.post("/chat/mensagens/")
async def enviar_mensagem(request: Request, msg_data: dict):
    token = request.headers.get("Authorization")
    response = await client.post(
        f"{SERVICES['chat']}/mensagens/",
        json=msg_data,
        headers={"Authorization": token}
    )
    return response.json()

# Roteamento para IA SERVICE
@app.get("/ia/sugestoes/{projeto_id}")
async def obter_sugestoes(projeto_id: int, request: Request):
    token = request.headers.get("Authorization")
    response = await client.get(
        f"{SERVICES['ia']}/sugestoes/{projeto_id}",
        headers={"Authorization": token}
    )
    return response.json()

# Roteamento para FINANCEIRO SERVICE
@app.get("/financeiro/resumo/{projeto_id}")
async def resumo_financeiro(projeto_id: int, request: Request):
    token = request.headers.get("Authorization")
    response = await client.get(
        f"{SERVICES['financeiro']}/resumo/{projeto_id}",
        headers={"Authorization": token}
    )
    return response.json()

# ============ ERROR HANDLING ============

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Erro interno: {str(exc)}"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 🔐 **Passo 3: Auth Service Isolado**

Criar `auth-service/main.py`:

```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from pydantic import BaseModel
import jwt
import os
from datetime import datetime, timedelta
import sqlite3

app = FastAPI(title="Auth Service", docs_url="/docs")
security = HTTPBearer()

SECRET_KEY = os.getenv("SECRET_KEY", "sua-chave-secreta")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480

# ============ MODELOS ============

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    nome: str
    email: str
    role: str

class TokenValidation(BaseModel):
    valid: bool
    user_id: int
    nome: str
    role: str

# ============ FUNÇÕES ============

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Criar JWT token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verificar e decodificar JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

# ============ ROTAS ============

@app.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login e geração de token"""
    # Buscar usuário no banco (exemplo simplificado)
    db = sqlite3.connect("../database/gerenciador.db")
    user = db.execute(
        "SELECT id, nome, email, role FROM usuarios WHERE email = ?",
        (request.email,)
    ).fetchone()
    db.close()
    
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    user_id, nome, email, role = user
    
    # Criar token
    token = create_access_token(
        data={
            "user_id": user_id,
            "nome": nome,
            "email": email,
            "role": role
        }
    )
    
    return TokenResponse(
        access_token=token,
        user_id=user_id,
        nome=nome,
        email=email,
        role=role
    )

@app.post("/validate-token", response_model=TokenValidation)
async def validate_token(credentials: HTTPAuthCredentials = Depends(security)):
    """Validar token (chamada do Gateway)"""
    token = credentials.credentials
    
    try:
        payload = verify_token(token)
        return TokenValidation(
            valid=True,
            user_id=payload["user_id"],
            nome=payload["nome"],
            role=payload["role"]
        )
    except HTTPException:
        return TokenValidation(valid=False, user_id=0, nome="", role="")

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "auth-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

---

## 📦 **Passo 4: Docker Compose para Orquestração**

Criar `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # ========== GATEWAY ==========
  api-gateway:
    build: ./api-gateway
    ports:
      - "8000:8000"
    environment:
      - AUTH_SERVICE_URL=http://auth-service:8001
      - CORE_SERVICE_URL=http://core-service:8002
      - CHAT_SERVICE_URL=http://chat-service:8003
      - IA_SERVICE_URL=http://ia-service:8004
      - FINANCEIRO_SERVICE_URL=http://financeiro-service:8005
    depends_on:
      - auth-service
      - core-service
      - chat-service
    networks:
      - microservices

  # ========== AUTH SERVICE ==========
  auth-service:
    build: ./auth-service
    expose:
      - "8001"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/auth_db
    depends_on:
      - postgres
    networks:
      - microservices

  # ========== CORE SERVICE ==========
  core-service:
    build: ./core-service
    expose:
      - "8002"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/core_db
    depends_on:
      - postgres
      - redis
    networks:
      - microservices

  # ========== CHAT SERVICE ==========
  chat-service:
    build: ./chat-service
    expose:
      - "8003"
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/chat_db
    depends_on:
      - postgres
      - redis
    networks:
      - microservices

  # ========== IA SERVICE ==========
  ia-service:
    build: ./ia-service
    expose:
      - "8004"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/core_db
    depends_on:
      - postgres
    networks:
      - microservices

  # ========== FINANCEIRO SERVICE ==========
  financeiro-service:
    build: ./financeiro-service
    expose:
      - "8005"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/financeiro_db
    depends_on:
      - postgres
    networks:
      - microservices

  # ========== INFRAESTRUTURA ==========
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=gerenciador_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - microservices

  redis:
    image: redis:7-alpine
    expose:
      - "6379"
    volumes:
      - redis_data:/data
    networks:
      - microservices

  rabbitmq:
    image: rabbitmq:3.12-management
    environment:
      - RABBITMQ_DEFAULT_USER=user
      - RABBITMQ_DEFAULT_PASS=password
    ports:
      - "15672:15672"  # Management UI
    expose:
      - "5672"
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    networks:
      - microservices

volumes:
  postgres_data:
  redis_data:
  rabbitmq_data:

networks:
  microservices:
    driver: bridge
```

---

## 🚀 **Passo 5: Iniciar Microserviços**

```bash
# 1. Clonar repositório
git clone <seu-repo>
cd gerenciador-projetos-microservices

# 2. Criar .env
cp .env.example .env

# 3. Build das imagens
docker-compose build

# 4. Iniciar todos os serviços
docker-compose up -d

# 5. Verificar status
docker-compose ps

# 6. Ver logs
docker-compose logs -f api-gateway

# 7. Parar serviços
docker-compose down
```

---

## 📊 **Passo 6: Service Mesh (Opcional - Avançado)**

Para ambiente de produção, considerar:

### Istio (API Gateway + Service Mesh)
- Roteamento automático
-retry/circuit breaker
- Telemetria

### Consul (Service Registry)
- Auto-discovery
- Health checks
- Load balancing

### Prometheus + Grafana
- Monitoramento
- Alertas
- Métricas

```yaml
# prometheus-compose.yml
prometheus:
  image: prom/prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  ports:
    - "9090:9090"

grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
  depends_on:
    - prometheus
```

---

## 🔄 **Comunicação Inter-Serviços**

### REST (Síncrono)
```python
# core-service chamando financeiro-service
response = await client.get(
    "http://financeiro-service:8005/resumo/1",
    headers={"Authorization": token}
)
```

### Message Queue (Assíncrono)
```python
# Publicar evento
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='task_created')
channel.basic_publish(
    exchange='',
    routing_key='task_created',
    body=json.dumps({"task_id": 123, "projeto_id": 456})
)

# Consumir evento
def callback(ch, method, properties, body):
    print(f"Evento: {body}")

channel.basic_consume(
    queue='task_created',
    on_message_callback=callback
)
channel.start_consuming()
```

---

## 📋 **Checklist - Migração para Microserviços**

- [ ] API Gateway implementado
- [ ] Auth Service isolado
- [ ] Core Service (projetos/tarefas)
- [ ] Chat Service com WebSocket
- [ ] IA Service
- [ ] Financeiro Service
- [ ] Notificações Service
- [ ] Docker Compose configurado
- [ ] Testes de integração passando
- [ ] Documentação API (OpenAPI)
- [ ] Monitoring (Prometheus + Grafana)
- [ ] Logging centralizado (ELK Stack)
- [ ] CI/CD adaptado

---

## ⚠️ **Desafios e Soluções**

| Desafio | Solução |
|---------|---------|
| **Distribuído debuging** | Correlation IDs, Distributed tracing (Jaeger) |
| **Consistência de dados** | Eventos, Saga pattern |
| **Performance** | Caching, Async, Message queues |
| **Segurança** | Token validation, mTLS |
| **Observabilidade** | Logs centralizados, Métricas, APM |

---

**Microserviços são o futuro da escalabilidade! 🚀**
