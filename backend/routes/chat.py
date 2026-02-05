"""
Rotas para chat interno
Sistema de mensagens por projeto com histórico e participantes
Inclui integração com ChatGPT e chat direto entre usuários
Corrigido para SQLite com DatabaseHelper
"""
import sys
import os
import httpx
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional, List
from pydantic import BaseModel

# Adicionar path do database
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'database'))
from db_helper import DatabaseHelper

from middleware.auth_middleware import get_current_active_user

router = APIRouter(prefix="/chat", tags=["Chat"])

# Configuração OpenAI (ChatGPT)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"


class ChatGPTRequest(BaseModel):
    mensagem: str
    contexto_projeto: Optional[str] = None


class MensagemCreate(BaseModel):
    conteudo: str
    mencoes: Optional[List[int]] = None


class MensagemDiretaCreate(BaseModel):
    destinatario_id: int
    conteudo: str


# WebSocket manager para múltiplos projetos (rooms)
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, projeto_id: int, websocket: WebSocket):
        await websocket.accept()
        if projeto_id not in self.active_connections:
            self.active_connections[projeto_id] = []
        self.active_connections[projeto_id].append(websocket)

    def disconnect(self, projeto_id: int, websocket: WebSocket):
        if projeto_id in self.active_connections:
            if websocket in self.active_connections[projeto_id]:
                self.active_connections[projeto_id].remove(websocket)
            if not self.active_connections[projeto_id]:
                del self.active_connections[projeto_id]

    async def broadcast(self, projeto_id: int, message: dict):
        if projeto_id in self.active_connections:
            for connection in self.active_connections[projeto_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass


manager = ConnectionManager()


# ===================== CHAT GPT =====================

@router.post("/ia/perguntar")
async def perguntar_chatgpt(
    request: ChatGPTRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Faz uma pergunta ao ChatGPT com contexto do projeto
    Requer API key da OpenAI configurada
    """
    if not OPENAI_API_KEY:
        # Modo simulado sem API key
        return {
            "success": True,
            "resposta": f"[Modo Simulado] Sua pergunta foi: '{request.mensagem}'. "
                       f"Para respostas reais do ChatGPT, configure a variável OPENAI_API_KEY.",
            "modelo": "simulado"
        }
    
    try:
        # Preparar contexto
        system_message = """Você é um assistente especializado em engenharia civil e 
        gerenciamento de projetos de construção. Ajude com questões técnicas, 
        planejamento, materiais, orçamentos e cronogramas."""
        
        if request.contexto_projeto:
            system_message += f"\n\nContexto do projeto atual: {request.contexto_projeto}"
        
        # Fazer requisição à API OpenAI
        async with httpx.AsyncClient() as client:
            response = await client.post(
                OPENAI_API_URL,
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": request.mensagem}
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.7
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Erro na API do ChatGPT")
            
            data = response.json()
            resposta = data["choices"][0]["message"]["content"]
            
            return {
                "success": True,
                "resposta": resposta,
                "modelo": "gpt-3.5-turbo"
            }
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Timeout na requisição ao ChatGPT")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===================== CHAT DO PROJETO =====================

@router.get("/projeto/{projeto_id}/mensagens")
async def listar_mensagens_projeto(
    projeto_id: int,
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_active_user)
):
    """Lista mensagens do chat do projeto"""
    db = DatabaseHelper()
    
    try:
        # Buscar ou criar chat do projeto
        chat = db.execute_query(
            "SELECT id FROM chats WHERE projeto_id = ?",
            (projeto_id,),
            fetch=True
        )
        
        if not chat:
            # Criar chat
            chat_id = db.execute_query(
                "INSERT INTO chats (projeto_id, nome, criado_em) VALUES (?, ?, datetime('now'))",
                (projeto_id, 'Chat do Projeto')
            )
        else:
            chat_id = chat[0]['id']
        
        # Listar mensagens
        mensagens = db.execute_query(
            """
            SELECT m.id, m.chat_id, m.autor_id, m.conteudo, m.mensagem, m.enviada_em, m.criado_em,
                   u.nome as autor_nome, u.email as autor_email
            FROM mensagens m
            LEFT JOIN usuarios u ON m.autor_id = u.id
            WHERE m.chat_id = ?
            ORDER BY COALESCE(m.enviada_em, m.criado_em) DESC
            LIMIT ? OFFSET ?
            """,
            (chat_id, limit, offset),
            fetch=True
        )
        
        # Formatar mensagens
        mensagens_formatadas = []
        for m in (mensagens or []):
            mensagens_formatadas.append({
                "id": m['id'],
                "chat_id": m['chat_id'],
                "autor_id": m['autor_id'],
                "conteudo": m['conteudo'] or m['mensagem'],
                "enviada_em": m['enviada_em'] or m['criado_em'],
                "autor_nome": m['autor_nome'],
                "autor_email": m['autor_email']
            })
        
        # Contar total
        total = db.execute_query(
            "SELECT COUNT(*) as total FROM mensagens WHERE chat_id = ?",
            (chat_id,),
            fetch=True
        )
        
        return {
            "success": True,
            "chat_id": chat_id,
            "total": total[0]['total'] if total else 0,
            "mensagens": mensagens_formatadas
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projeto/{projeto_id}/mensagens")
async def enviar_mensagem_projeto(
    projeto_id: int,
    mensagem: MensagemCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Envia mensagem no chat do projeto"""
    db = DatabaseHelper()
    user_id = current_user.get("user_id") or current_user.get("id")
    
    try:
        # Buscar ou criar chat
        chat = db.execute_query(
            "SELECT id FROM chats WHERE projeto_id = ?",
            (projeto_id,),
            fetch=True
        )
        
        if not chat:
            chat_id = db.execute_query(
                "INSERT INTO chats (projeto_id, nome, criado_em) VALUES (?, ?, datetime('now'))",
                (projeto_id, 'Chat do Projeto')
            )
        else:
            chat_id = chat[0]['id']
        
        # Inserir mensagem
        mensagem_id = db.execute_query(
            """
            INSERT INTO mensagens (chat_id, autor_id, conteudo, mensagem, enviada_em, criado_em)
            VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
            """,
            (chat_id, user_id, mensagem.conteudo, mensagem.conteudo)
        )
        
        # Criar notificações para menções
        if mensagem.mencoes:
            for usuario_id in mensagem.mencoes:
                db.execute_query(
                    """
                    INSERT INTO notificacoes (usuario_id, tipo, titulo, mensagem, criado_em)
                    VALUES (?, 'mencao', 'Você foi mencionado', ?, datetime('now'))
                    """,
                    (usuario_id, f"Você foi mencionado em uma mensagem no projeto {projeto_id}")
                )
        
        # Broadcast via WebSocket
        await manager.broadcast(projeto_id, {
            "tipo": "nova_mensagem",
            "mensagem_id": mensagem_id,
            "autor_id": user_id,
            "conteudo": mensagem.conteudo,
            "projeto_id": projeto_id
        })
        
        return {
            "success": True,
            "message": "Mensagem enviada",
            "mensagem_id": mensagem_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projeto/{projeto_id}/participantes")
async def listar_participantes(
    projeto_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """Lista participantes do chat do projeto"""
    db = DatabaseHelper()
    
    try:
        participantes = db.execute_query(
            """
            SELECT DISTINCT u.id, u.nome, u.email, u.cargo
            FROM equipes e
            JOIN usuarios u ON e.usuario_id = u.id
            WHERE e.projeto_id = ? AND e.ativo = 1
            """,
            (projeto_id,),
            fetch=True
        )
        
        return {
            "success": True,
            "total": len(participantes) if participantes else 0,
            "participantes": participantes or []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===================== CONVERSAS =====================

@router.get("/conversas")
async def listar_conversas(
    current_user: dict = Depends(get_current_active_user)
):
    """Lista todas as conversas do usuário (projetos onde participa)"""
    db = DatabaseHelper()
    user_id = current_user.get("user_id") or current_user.get("id")
    
    try:
        # Conversas de projetos - projetos criados ou onde participa
        projetos = db.execute_query(
            """
            SELECT DISTINCT p.id as projeto_id, p.nome as projeto_nome,
                   'projeto' as tipo
            FROM projetos p
            LEFT JOIN equipes e ON p.id = e.projeto_id AND e.ativo = 1
            WHERE p.criador_id = ? OR e.usuario_id = ?
            """,
            (user_id, user_id),
            fetch=True
        )
        
        return {
            "success": True,
            "projetos": projetos or [],
            "conversas_diretas": []  # Tabela mensagens_diretas não existe neste schema
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usuarios-disponiveis")
async def listar_usuarios_disponiveis(
    current_user: dict = Depends(get_current_active_user)
):
    """Lista usuários disponíveis para chat direto"""
    db = DatabaseHelper()
    user_id = current_user.get("user_id") or current_user.get("id")
    
    try:
        usuarios = db.execute_query(
            """
            SELECT id, nome, email, cargo
            FROM usuarios
            WHERE id != ? AND ativo = 1
            ORDER BY nome
            """,
            (user_id,),
            fetch=True
        )
        
        return {
            "success": True,
            "usuarios": usuarios or []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/direto/enviar")
async def enviar_mensagem_direta(
    mensagem: MensagemDiretaCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Envia mensagem direta para outro usuário
    Nota: Usando tabela mensagens com chat_id especial para chat direto
    """
    db = DatabaseHelper()
    user_id = current_user.get("user_id") or current_user.get("id")
    
    try:
        # Criar ou buscar chat direto entre os dois usuários
        # Usar projeto_id = NULL e nome especial para chat direto
        usuarios_ids = sorted([user_id, mensagem.destinatario_id])
        chat_nome = f"direto_{usuarios_ids[0]}_{usuarios_ids[1]}"
        
        chat = db.execute_query(
            "SELECT id FROM chats WHERE nome = ? AND projeto_id IS NULL",
            (chat_nome,),
            fetch=True
        )
        
        if not chat:
            chat_id = db.execute_query(
                "INSERT INTO chats (projeto_id, nome, tipo, criado_em) VALUES (NULL, ?, 'direto', datetime('now'))",
                (chat_nome,)
            )
        else:
            chat_id = chat[0]['id']
        
        # Inserir mensagem
        mensagem_id = db.execute_query(
            """
            INSERT INTO mensagens (chat_id, autor_id, usuario_id, conteudo, mensagem, enviada_em, criado_em)
            VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """,
            (chat_id, user_id, mensagem.destinatario_id, mensagem.conteudo, mensagem.conteudo)
        )
        
        # Notificar destinatário
        db.execute_query(
            """
            INSERT INTO notificacoes (usuario_id, tipo, titulo, mensagem, criado_em)
            VALUES (?, 'mensagem', 'Nova mensagem', ?, datetime('now'))
            """,
            (mensagem.destinatario_id, "Você recebeu uma nova mensagem")
        )
        
        return {
            "success": True,
            "message": "Mensagem enviada",
            "mensagem_id": mensagem_id,
            "chat_id": chat_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/direto/{outro_usuario_id}")
async def listar_mensagens_diretas(
    outro_usuario_id: int,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user)
):
    """Lista mensagens diretas com outro usuário"""
    db = DatabaseHelper()
    user_id = current_user.get("user_id") or current_user.get("id")
    
    try:
        # Buscar chat direto
        usuarios_ids = sorted([user_id, outro_usuario_id])
        chat_nome = f"direto_{usuarios_ids[0]}_{usuarios_ids[1]}"
        
        chat = db.execute_query(
            "SELECT id FROM chats WHERE nome = ? AND projeto_id IS NULL",
            (chat_nome,),
            fetch=True
        )
        
        if not chat:
            return {
                "success": True,
                "mensagens": []
            }
        
        chat_id = chat[0]['id']
        
        mensagens = db.execute_query(
            """
            SELECT m.id, m.autor_id, m.usuario_id as destinatario_id, 
                   COALESCE(m.conteudo, m.mensagem) as conteudo, 
                   COALESCE(m.enviada_em, m.criado_em) as enviada_em, m.lida,
                   u.nome as remetente_nome
            FROM mensagens m
            JOIN usuarios u ON m.autor_id = u.id
            WHERE m.chat_id = ?
            ORDER BY COALESCE(m.enviada_em, m.criado_em) DESC
            LIMIT ?
            """,
            (chat_id, limit),
            fetch=True
        )
        
        # Marcar como lidas
        db.execute_query(
            """
            UPDATE mensagens 
            SET lida = 1 
            WHERE chat_id = ? AND usuario_id = ? AND lida = 0
            """,
            (chat_id, user_id)
        )
        
        return {
            "success": True,
            "mensagens": mensagens or []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket endpoint para chat em tempo real
@router.websocket("/ws/{projeto_id}")
async def websocket_chat(websocket: WebSocket, projeto_id: int):
    await manager.connect(projeto_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Broadcast para todos do projeto
            await manager.broadcast(projeto_id, {
                "tipo": "mensagem",
                "autor_id": data.get('autor_id'),
                "conteudo": data.get('conteudo'),
                "projeto_id": projeto_id
            })
    except WebSocketDisconnect:
        manager.disconnect(projeto_id, websocket)

