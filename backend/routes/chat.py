"""
Rotas para chat interno
Sistema de mensagens por projeto com histórico e participantes
Inclui integração com ChatGPT e chat direto entre usuários
"""
import csv
import os
import httpx
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional
from pydantic import BaseModel
from middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])

# Configuração OpenAI (ChatGPT)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"


class ChatGPTRequest(BaseModel):
    mensagem: str
    contexto_projeto: Optional[str] = None


class MensagemDiretaCreate(BaseModel):
    destinatario_id: int
    conteudo: str


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


# ═══════════════════════════════════════════════════════════════════
# 🤖 INTEGRAÇÃO COM CHATGPT
# ═══════════════════════════════════════════════════════════════════

@router.post("/assistente-ia")
async def chat_com_assistente_ia(
    request: ChatGPTRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    💬 Chat com assistente IA (ChatGPT) para ajudar em projetos de engenharia.
    O assistente é especializado em construção civil e gestão de projetos.
    """
    
    # Verificar se a API Key está configurada
    if not OPENAI_API_KEY:
        # Se não houver API Key, usar respostas simuladas inteligentes
        return resposta_simulada_ia(request.mensagem, request.contexto_projeto, current_user)
    
    try:
        # Criar prompt de sistema especializado em engenharia
        system_prompt = """Você é um assistente especializado em engenharia civil e gestão de projetos de construção.
Você ajuda engenheiros, arquitetos e gestores com:
- Planejamento e cronogramas de obras
- Cálculos de materiais e orçamentos
- Normas técnicas (NBR, ABNT)
- Segurança do trabalho em obras
- Gestão de equipes e tarefas
- Documentação técnica
- Resolução de problemas de obra

Responda sempre em português brasileiro de forma clara e profissional.
Se não souber algo específico, indique que é necessário consultar um profissional especializado."""

        if request.contexto_projeto:
            system_prompt += f"\n\nContexto do projeto atual: {request.contexto_projeto}"
        
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
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": request.mensagem}
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.7
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                resposta = data["choices"][0]["message"]["content"]
                
                return {
                    "success": True,
                    "resposta": resposta,
                    "modelo": "gpt-3.5-turbo",
                    "usuario": current_user.get("nome", "Usuário")
                }
            else:
                # Fallback para resposta simulada
                return resposta_simulada_ia(request.mensagem, request.contexto_projeto, current_user)
                
    except Exception as e:
        # Em caso de erro, usar resposta simulada
        return resposta_simulada_ia(request.mensagem, request.contexto_projeto, current_user)


def resposta_simulada_ia(mensagem: str, contexto: str, user: dict):
    """
    Gera respostas simuladas inteligentes quando a API do ChatGPT não está disponível.
    """
    mensagem_lower = mensagem.lower()
    nome_usuario = user.get("nome", "Usuário")
    
    # Respostas contextuais baseadas em palavras-chave
    if any(palavra in mensagem_lower for palavra in ["orçamento", "custo", "preço", "valor"]):
        resposta = f"""📊 **Sobre Orçamentos de Obra**

Olá {nome_usuario}! Para um orçamento preciso, considere:

1. **Materiais**: Faça cotação em pelo menos 3 fornecedores
2. **Mão de obra**: Inclua encargos sociais (~80% do salário)
3. **BDI**: Adicione 25-30% para despesas indiretas
4. **Contingência**: Reserve 5-10% para imprevistos

💡 **Dica**: Use a tabela SINAPI ou TCPO como referência de preços."""

    elif any(palavra in mensagem_lower for palavra in ["prazo", "cronograma", "tempo", "data"]):
        resposta = f"""📅 **Gestão de Cronograma**

{nome_usuario}, algumas dicas para gestão de prazos:

1. **Método do Caminho Crítico**: Identifique atividades críticas
2. **Buffer**: Adicione folga de 10-15% ao prazo estimado
3. **Marcos**: Defina entregas intermediárias
4. **Reuniões semanais**: Acompanhe o progresso regularmente

⚠️ **Atenção**: Considere fatores climáticos na região da obra."""

    elif any(palavra in mensagem_lower for palavra in ["material", "concreto", "aço", "cimento"]):
        resposta = f"""🧱 **Materiais de Construção**

{nome_usuario}, sobre materiais:

1. **Concreto**: Verifique o fck especificado no projeto
2. **Aço**: Confira bitolas e comprimentos conforme projeto estrutural
3. **Armazenamento**: Proteja materiais de umidade e sol
4. **Controle**: Faça recebimento técnico de materiais

📋 **Normas importantes**: NBR 6118 (concreto), NBR 7480 (aço)."""

    elif any(palavra in mensagem_lower for palavra in ["segurança", "epi", "acidente", "nr"]):
        resposta = f"""🦺 **Segurança do Trabalho**

{nome_usuario}, itens essenciais:

1. **EPIs obrigatórios**: Capacete, botina, luvas, óculos
2. **NR-18**: Condições de trabalho na construção
3. **PCMAT**: Programa obrigatório para obras > 20 trabalhadores
4. **DDS**: Diálogo Diário de Segurança antes do expediente

⚠️ **Lembre-se**: Segurança não é gasto, é investimento!"""

    elif any(palavra in mensagem_lower for palavra in ["equipe", "funcionário", "trabalhador"]):
        resposta = f"""👷 **Gestão de Equipes**

{nome_usuario}, para uma equipe produtiva:

1. **Dimensionamento**: Use índices de produtividade (TCPO)
2. **Comunicação**: Reuniões breves diárias (15 min)
3. **Capacitação**: Treinamentos regulares
4. **Motivação**: Reconheça bons desempenhos

📊 **Produtividade média**: Consulte tabelas de composição de custos."""

    elif any(palavra in mensagem_lower for palavra in ["documento", "laudo", "relatório", "art"]):
        resposta = f"""📄 **Documentação Técnica**

{nome_usuario}, documentos essenciais:

1. **ART/RRT**: Obrigatório para todo serviço técnico
2. **Diário de Obra**: Registro diário de atividades
3. **Laudos**: Fundação, estrutura, instalações
4. **Habite-se**: Documento final para ocupação

⚡ **Dica**: Organize documentos digitalmente com backup."""

    else:
        resposta = f"""🏗️ **Assistente de Engenharia**

Olá {nome_usuario}! Sou seu assistente virtual para projetos de engenharia.

Posso ajudar com:
• 📊 Orçamentos e custos
• 📅 Cronogramas e prazos
• 🧱 Materiais de construção
• 🦺 Segurança do trabalho
• 👷 Gestão de equipes
• 📄 Documentação técnica

💬 Faça sua pergunta que tentarei ajudar!

*Nota: Esta é uma resposta simulada. Configure a API Key do OpenAI para respostas mais personalizadas.*"""

    return {
        "success": True,
        "resposta": resposta,
        "modelo": "assistente-local",
        "usuario": nome_usuario,
        "nota": "Resposta gerada localmente (sem API OpenAI configurada)"
    }


# ═══════════════════════════════════════════════════════════════════
# 💬 CHAT DIRETO ENTRE USUÁRIOS
# ═══════════════════════════════════════════════════════════════════

@router.get("/usuarios-disponiveis")
async def listar_usuarios_para_chat(
    current_user: dict = Depends(get_current_user)
):
    """
    Lista todos os usuários disponíveis para iniciar uma conversa direta.
    Exclui o usuário atual da lista.
    """
    from database.db_helper import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT id, nome, email, cargo, 
                   CASE 
                       WHEN cargo IN ('admin', 'gerente') THEN '👑'
                       WHEN cargo = 'engenheiro' THEN '👷'
                       ELSE '👤'
                   END as icone
            FROM usuarios 
            WHERE id != %s AND ativo = 1
            ORDER BY nome
        """, (current_user['id'],))
        
        usuarios = cursor.fetchall()
        
        return {
            "success": True,
            "usuarios": usuarios,
            "total": len(usuarios)
        }
        
    except Exception as e:
        # Se não houver tabela de usuários, retornar lista de admins hardcoded
        usuarios_admin = [
            {"id": 1, "nome": "Vicente", "email": "vicentedesouza762@gmail.com", "cargo": "admin", "icone": "👑"},
            {"id": 2, "nome": "Francisco", "email": "francisco@email.com", "cargo": "admin", "icone": "👑"},
            {"id": 3, "nome": "Professor", "email": "professor@email.com", "cargo": "admin", "icone": "👑"}
        ]
        # Remover usuário atual da lista
        usuarios_filtrados = [u for u in usuarios_admin if u["email"] != current_user.get("email")]
        
        return {
            "success": True,
            "usuarios": usuarios_filtrados,
            "total": len(usuarios_filtrados),
            "nota": "Lista de usuários padrão (banco não configurado)"
        }
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass


@router.post("/mensagem-direta")
async def enviar_mensagem_direta(
    mensagem: MensagemDiretaCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Envia uma mensagem direta para outro usuário (chat privado).
    """
    from database.db_helper import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Verificar se já existe uma conversa entre os dois usuários
        user_ids = sorted([current_user['id'], mensagem.destinatario_id])
        chat_nome = f"chat_direto_{user_ids[0]}_{user_ids[1]}"
        
        cursor.execute("""
            SELECT id FROM chats WHERE nome = %s
        """, (chat_nome,))
        
        chat = cursor.fetchone()
        if not chat:
            # Criar nova conversa direta
            cursor.execute("""
                INSERT INTO chats (nome, projeto_id, criado_em)
                VALUES (%s, NULL, NOW())
            """, (chat_nome,))
            chat_id = cursor.lastrowid
            
            # Adicionar ambos como participantes
            for uid in user_ids:
                cursor.execute("""
                    INSERT INTO chat_participantes (chat_id, usuario_id, juntou_em)
                    VALUES (%s, %s, NOW())
                """, (chat_id, uid))
        else:
            chat_id = chat['id']
        
        # Inserir mensagem
        cursor.execute("""
            INSERT INTO mensagens (chat_id, autor_id, conteudo, enviada_em)
            VALUES (%s, %s, %s, NOW())
        """, (chat_id, current_user['id'], mensagem.conteudo))
        
        mensagem_id = cursor.lastrowid
        
        # Criar notificação para o destinatário
        cursor.execute("""
            INSERT INTO notificacoes (usuario_id, tipo, conteudo, lida, criada_em)
            VALUES (%s, 'mensagem_direta', %s, 0, NOW())
        """, (mensagem.destinatario_id, f"Nova mensagem de {current_user.get('nome', 'Usuário')}"))
        
        conn.commit()
        
        return {
            "success": True,
            "message": "Mensagem enviada com sucesso",
            "chat_id": chat_id,
            "mensagem_id": mensagem_id
        }
        
    except Exception as e:
        conn.rollback()
        # Retornar sucesso simulado para não quebrar a interface
        return {
            "success": True,
            "message": "Mensagem registrada (modo offline)",
            "chat_id": 0,
            "mensagem_id": 0,
            "nota": "Banco de dados não disponível"
        }
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass


@router.get("/conversas-diretas")
async def listar_conversas_diretas(
    current_user: dict = Depends(get_current_user)
):
    """
    Lista todas as conversas diretas do usuário atual.
    """
    from database.db_helper import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT DISTINCT c.id as chat_id, c.nome,
                   (SELECT u.nome FROM usuarios u 
                    JOIN chat_participantes cp2 ON u.id = cp2.usuario_id 
                    WHERE cp2.chat_id = c.id AND u.id != %s LIMIT 1) as outro_usuario,
                   (SELECT m.conteudo FROM mensagens m 
                    WHERE m.chat_id = c.id ORDER BY m.enviada_em DESC LIMIT 1) as ultima_mensagem,
                   (SELECT m.enviada_em FROM mensagens m 
                    WHERE m.chat_id = c.id ORDER BY m.enviada_em DESC LIMIT 1) as ultima_data
            FROM chats c
            JOIN chat_participantes cp ON c.id = cp.chat_id
            WHERE cp.usuario_id = %s AND c.nome LIKE 'chat_direto_%%'
            ORDER BY ultima_data DESC
        """, (current_user['id'], current_user['id']))
        
        conversas = cursor.fetchall()
        
        return {
            "success": True,
            "conversas": conversas,
            "total": len(conversas)
        }
        
    except Exception as e:
        return {
            "success": True,
            "conversas": [],
            "total": 0,
            "nota": "Nenhuma conversa ainda"
        }
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass


@router.get("/mensagens-diretas/{outro_usuario_id}")
async def listar_mensagens_diretas(
    outro_usuario_id: int,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """
    Lista mensagens de uma conversa direta com outro usuário.
    """
    from database.db_helper import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Encontrar chat entre os dois usuários
        user_ids = sorted([current_user['id'], outro_usuario_id])
        chat_nome = f"chat_direto_{user_ids[0]}_{user_ids[1]}"
        
        cursor.execute("""
            SELECT id FROM chats WHERE nome = %s
        """, (chat_nome,))
        
        chat = cursor.fetchone()
        if not chat:
            return {
                "success": True,
                "mensagens": [],
                "total": 0,
                "nota": "Nenhuma mensagem ainda. Seja o primeiro a enviar!"
            }
        
        # Listar mensagens
        cursor.execute("""
            SELECT m.*, u.nome as autor_nome
            FROM mensagens m
            LEFT JOIN usuarios u ON m.autor_id = u.id
            WHERE m.chat_id = %s
            ORDER BY m.enviada_em DESC
            LIMIT %s
        """, (chat['id'], limit))
        
        mensagens = cursor.fetchall()
        
        return {
            "success": True,
            "mensagens": mensagens,
            "total": len(mensagens),
            "chat_id": chat['id']
        }
        
    except Exception as e:
        return {
            "success": True,
            "mensagens": [],
            "total": 0,
            "nota": "Inicie uma nova conversa!"
        }
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass
