"""
Rotas para chat interno
Sistema de mensagens por projeto com histórico e participantes
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel
from middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])

class MensagemCreate(BaseModel):
    conteudo: str
    mencoes: Optional[list[int]] = None  # IDs de usuários mencionados

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
            INSERT IGNORE INTO chat_participantes (chat_id, usuario_id, juntou_em)
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
                    VALUES (%s, 'mencao', %s, FALSE, NOW())
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
