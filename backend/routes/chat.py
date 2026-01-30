"""
Rotas para chat interno
Sistema de mensagens por projeto com histórico e participantes
"""
import csv
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional
from pydantic import BaseModel
from middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])


# WebSocket manager para múltiplos projetos (rooms)
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, projeto_id: int, websocket: WebSocket):
        await websocket.accept()
        if projeto_id not in self.active_connections:
            self.active_connections[projeto_id] = []
        self.active_connections[projeto_id].append(websocket)

    def disconnect(self, projeto_id: int, websocket: WebSocket):
        if projeto_id in self.active_connections:
            self.active_connections[projeto_id].remove(websocket)
            if not self.active_connections[projeto_id]:
                del self.active_connections[projeto_id]

    async def broadcast(self, projeto_id: int, message: dict):
        if projeto_id in self.active_connections:
            for connection in self.active_connections[projeto_id]:
                await connection.send_json(message)


manager = ConnectionManager()


class MensagemCreate(BaseModel):
    conteudo: str
    mencoes: Optional[list[int]] = None  # IDs de usuários mencionados


# WebSocket endpoint para chat em tempo real por projeto
@router.websocket("/ws/{projeto_id}")
async def websocket_chat(websocket: WebSocket, projeto_id: int):
    await manager.connect(projeto_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Espera-se: {"autor_id": int, "conteudo": str, "mencoes": [int]}
            from database.db_helper import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            try:
                # Buscar ou criar chat
                cursor.execute("SELECT id FROM chats WHERE projeto_id = %s", (projeto_id,))
                chat = cursor.fetchone()
                if not chat:
                    cursor.execute("INSERT INTO chats (projeto_id, nome, criado_em) VALUES (%s, 'Chat do Projeto', NOW())", (projeto_id,))
                    chat_id = cursor.lastrowid
                else:
                    chat_id = chat['id']
                # Adicionar participante
                cursor.execute("INSERT OR IGNORE INTO chat_participantes (chat_id, usuario_id, juntou_em) VALUES (%s, %s, NOW())", (chat_id, data['autor_id']))
                # Inserir mensagem
                cursor.execute("INSERT INTO mensagens (chat_id, autor_id, conteudo, enviada_em) VALUES (%s, %s, %s, NOW())", (chat_id, data['autor_id'], data['conteudo']))
                mensagem_id = cursor.lastrowid
                # Notificações de menção
                if data.get('mencoes'):
                    for usuario_id in data['mencoes']:
                        cursor.execute("INSERT INTO notificacoes (usuario_id, tipo, conteudo, lida, criada_em) VALUES (%s, 'mencao', %s, 0, NOW())", (usuario_id, f"Você foi mencionado em uma mensagem do projeto {projeto_id}"))
                conn.commit()
                # Broadcast para todos do projeto
                await manager.broadcast(projeto_id, {
                    "mensagem_id": mensagem_id,
                    "autor_id": data['autor_id'],
                    "conteudo": data['conteudo'],
                    "mencoes": data.get('mencoes', []),
                    "projeto_id": projeto_id
                })
            except Exception as e:
                conn.rollback()
                await websocket.send_json({"error": str(e)})
            finally:
                cursor.close()
                conn.close()
    except WebSocketDisconnect:
        manager.disconnect(projeto_id, websocket)


@router.get("/{projeto_id}/exportar-logs")
async def exportar_logs_chat(
    projeto_id: int,
    formato: str = "csv",
    current_user: dict = Depends(get_current_user)
):
    """
    Exporta logs do chat do projeto em CSV ou JSON (apenas admin)
    """
    from database.db_helper import get_db_connection
    # Verificar se usuário é admin (ajuste conforme seu sistema de permissões)
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Apenas administradores podem exportar logs")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT m.id, m.chat_id, m.autor_id, u.nome as autor_nome, m.conteudo, m.enviada_em
            FROM mensagens m
            LEFT JOIN usuarios u ON m.autor_id = u.id
            LEFT JOIN chats c ON m.chat_id = c.id
            WHERE c.projeto_id = %s
            ORDER BY m.enviada_em
        """, (projeto_id,))
        mensagens = cursor.fetchall()
        
        if formato == "json":
            return JSONResponse(content=mensagens)
        
        # CSV
        def iter_csv():
            header = ["id", "chat_id", "autor_id", "autor_nome", "conteudo", "enviada_em"]
            yield ",".join(header) + "\n"
            for m in mensagens:
                row = [str(m.get(h, "")) if m.get(h) is not None else "" for h in header]
                yield ",".join(row) + "\n"
        return StreamingResponse(iter_csv(), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=chat_{projeto_id}_logs.csv"})
    finally:
        cursor.close()
        conn.close()


@router.get("/{projeto_id}/mensagens")
async def listar_mensagens(
    projeto_id: int,
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Lista mensagens do chat do projeto (mais recentes primeiro)"""
    from database.db_helper import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Buscar ID do chat do projeto
        cursor.execute("""
            SELECT id FROM chats WHERE projeto_id = %s
        """, (projeto_id,))
        
        chat = cursor.fetchone()
        if not chat:
            # Criar chat se não existir
            cursor.execute("""
                INSERT INTO chats (projeto_id, nome, criado_em)
                VALUES (%s, 'Chat do Projeto', NOW())
            """, (projeto_id,))
            conn.commit()
            chat_id = cursor.lastrowid
        else:
            chat_id = chat['id']
        
        # Listar mensagens
        cursor.execute("""
            SELECT m.*, u.nome as autor_nome, u.email as autor_email
            FROM mensagens m
            LEFT JOIN usuarios u ON m.autor_id = u.id
            WHERE m.chat_id = %s
            ORDER BY m.enviada_em DESC
            LIMIT %s OFFSET %s
        """, (chat_id, limit, offset))
        
        mensagens = cursor.fetchall()
        
        # Contar total
        cursor.execute("""
            SELECT COUNT(*) as total FROM mensagens WHERE chat_id = %s
        """, (chat_id,))
        
        total = cursor.fetchone()['total']
        
        return {
            "success": True,
            "chat_id": chat_id,
            "total_mensagens": total,
            "mensagens": mensagens
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.post("/{projeto_id}/mensagens")
async def enviar_mensagem(
    projeto_id: int,
    mensagem: MensagemCreate,
    current_user: dict = Depends(get_current_user)
):
    """Envia uma nova mensagem no chat do projeto"""
    from database.db_helper import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Buscar ou criar chat
        cursor.execute("""
            SELECT id FROM chats WHERE projeto_id = %s
        """, (projeto_id,))
        
        chat = cursor.fetchone()
        if not chat:
            cursor.execute("""
                INSERT INTO chats (projeto_id, nome, criado_em)
                VALUES (%s, 'Chat do Projeto', NOW())
            """, (projeto_id,))
            chat_id = cursor.lastrowid
        else:
            chat_id = chat['id']
        
        # Adicionar usuário como participante se não estiver
        cursor.execute("""
            INSERT OR IGNORE INTO chat_participantes (chat_id, usuario_id, juntou_em)
            VALUES (%s, %s, NOW())
        """, (chat_id, current_user['id']))
        
        # Inserir mensagem
        cursor.execute("""
            INSERT INTO mensagens (chat_id, autor_id, conteudo, enviada_em)
            VALUES (%s, %s, %s, NOW())
        """, (chat_id, current_user['id'], mensagem.conteudo))
        
        mensagem_id = cursor.lastrowid
        
        # Criar notificações para menções
        if mensagem.mencoes:
            for usuario_id in mensagem.mencoes:
                cursor.execute("""
                    INSERT INTO notificacoes 
                    (usuario_id, tipo, conteudo, lida, criada_em)
                    VALUES (%s, 'mencao', %s, 0, NOW())
                """, (
                    usuario_id,
                    f"{current_user['nome']} mencionou você em uma mensagem"
                ))
        
        conn.commit()
        
        return {
            "success": True,
            "message": "Mensagem enviada",
            "mensagem_id": mensagem_id
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.get("/{projeto_id}/participantes")
async def listar_participantes(
    projeto_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Lista participantes do chat do projeto"""
    from database.db_helper import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT cp.*, u.nome, u.email, u.cargo
            FROM chat_participantes cp
            LEFT JOIN usuarios u ON cp.usuario_id = u.id
            LEFT JOIN chats c ON cp.chat_id = c.id
            WHERE c.projeto_id = %s
            ORDER BY cp.juntou_em
        """, (projeto_id,))
        
        participantes = cursor.fetchall()
        
        return {
            "success": True,
            "total_participantes": len(participantes),
            "participantes": participantes
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.delete("/{mensagem_id}")
async def deletar_mensagem(
    mensagem_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Deleta uma mensagem (apenas autor ou admin)"""
    from database.db_helper import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Verificar se é o autor
        cursor.execute("""
            SELECT autor_id FROM mensagens WHERE id = %s
        """, (mensagem_id,))
        
        mensagem = cursor.fetchone()
        if not mensagem:
            raise HTTPException(status_code=404, detail="Mensagem não encontrada")
        
        if mensagem['autor_id'] != current_user['id']:
            # Verificar se é admin (você pode adicionar lógica de permissão aqui)
            raise HTTPException(status_code=403, detail="Sem permissão para deletar")
        
        cursor.execute("DELETE FROM mensagens WHERE id = %s", (mensagem_id,))
        conn.commit()
        
        return {
            "success": True,
            "message": "Mensagem deletada"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.get("/{projeto_id}/buscar")
async def buscar_mensagens(
    projeto_id: int,
    termo: str,
    current_user: dict = Depends(get_current_user)
):
    """Busca mensagens por texto no chat do projeto"""
    from database.db_helper import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT m.*, u.nome as autor_nome
            FROM mensagens m
            LEFT JOIN usuarios u ON m.autor_id = u.id
            LEFT JOIN chats c ON m.chat_id = c.id
            WHERE c.projeto_id = %s
              AND m.conteudo LIKE %s
            ORDER BY m.enviada_em DESC
            LIMIT 50
        """, (projeto_id, f"%{termo}%"))
        
        resultados = cursor.fetchall()
        
        return {
            "success": True,
            "total_encontrados": len(resultados),
            "termo_busca": termo,
            "resultados": resultados
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
