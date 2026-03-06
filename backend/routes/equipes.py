"""
Rotas de Equipes - Gerenciamento de membros e permissões
Autor: Vicente de Souza
Corrigido para SQLite com DatabaseHelper
"""

import sys
import secrets
from pathlib import Path
from typing import List, Optional
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel

# Adiciona o diretório database ao path
database_dir = Path(__file__).parent.parent.parent / "database"
sys.path.insert(0, str(database_dir))

from db_helper import DatabaseHelper
from middleware.auth_middleware import get_current_active_user

router = APIRouter(prefix="/equipes", tags=["Equipes"])

# ===== SCHEMAS =====

class EquipeCreate(BaseModel):
    projeto_id: int
    usuario_id: int
    papel: str  # gerente, engenheiro, tecnico, colaborador
    data_entrada: Optional[str] = None


class EquipeUpdate(BaseModel):
    papel: Optional[str] = None
    data_saida: Optional[str] = None
    ativo: Optional[bool] = None


class PermissaoCreate(BaseModel):
    usuario_id: int
    permissao_id: int
    projeto_id: Optional[int] = None


class ConviteEquipeCreate(BaseModel):
    projeto_id: int
    email_convidado: str
    papel: str  # gerente, engenheiro, tecnico, colaborador
    expiracao_horas: Optional[int] = 48


class ConviteAceitar(BaseModel):
    token: str
    usuario_id: int


class CodigoConviteCreate(BaseModel):
    projeto_id: int
    papel: str = "colaborador"  # gerente, engenheiro, tecnico, colaborador, cliente
    expiracao_horas: int = 168  # 7 dias por padrão


class CodigoConviteAceitar(BaseModel):
    codigo: str


class EnviarConviteEmail(BaseModel):
    projeto_id: int
    email_destinatario: str
    papel: str = "colaborador"
    expiracao_horas: int = 168  # 7 dias por padrão


# ===== ENDPOINTS =====

@router.get("/projeto/{projeto_id}")
async def listar_membros_projeto(
    projeto_id: int,
    ativo: Optional[bool] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Lista todos os membros de um projeto
    """
    db = DatabaseHelper()
    
    try:
        # Verificar se projeto existe
        projeto = db.execute_query(
            "SELECT id, nome FROM projetos WHERE id = %s",
            (projeto_id,),
            fetch=True
        )
        
        if not projeto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Projeto {projeto_id} não encontrado"
            )
        
        # Buscar membros com JOIN em usuarios
        query = """
            SELECT 
                e.id,
                e.projeto_id,
                p.nome as projeto_nome,
                e.usuario_id,
                u.nome as usuario_nome,
                u.email as usuario_email,
                u.cargo as usuario_cargo,
                e.papel,
                e.data_entrada,
                e.data_saida,
                e.ativo
            FROM equipes e
            INNER JOIN usuarios u ON e.usuario_id = u.id
            INNER JOIN projetos p ON e.projeto_id = p.id
            WHERE e.projeto_id = %s
        """
        params = [projeto_id]
        
        if ativo is not None:
            query += " AND e.ativo = %s"
            params.append(1 if ativo else 0)
        
        query += " ORDER BY e.data_entrada DESC"
        
        membros = db.execute_query(query, tuple(params), fetch=True)
        
        # Formatar resposta
        return [
            {
                "id": m['id'],
                "projeto_id": m['projeto_id'],
                "projeto_nome": m['projeto_nome'],
                "usuario_id": m['usuario_id'],
                "usuario_nome": m['usuario_nome'],
                "usuario_email": m['usuario_email'],
                "usuario_cargo": m['usuario_cargo'],
                "papel": m['papel'],
                "data_entrada": str(m['data_entrada']) if m['data_entrada'] else None,
                "data_saida": str(m['data_saida']) if m['data_saida'] else None,
                "ativo": bool(m['ativo'])
            }
            for m in (membros or [])
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar membros: {str(e)}"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def adicionar_membro(
    membro: EquipeCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Adiciona um novo membro à equipe do projeto
    """
    db = DatabaseHelper()
    
    try:
        # Verificar se projeto existe
        projeto = db.execute_query(
            "SELECT id FROM projetos WHERE id = %s", 
            (membro.projeto_id,), 
            fetch=True
        )
        if not projeto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Projeto {membro.projeto_id} não encontrado"
            )
        
        # Verificar se usuário existe
        usuario = db.execute_query(
            "SELECT id FROM usuarios WHERE id = %s", 
            (membro.usuario_id,), 
            fetch=True
        )
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário {membro.usuario_id} não encontrado"
            )
        
        # Verificar se já existe membro ativo
        existente = db.execute_query(
            """
            SELECT id FROM equipes 
            WHERE projeto_id = %s AND usuario_id = %s AND ativo = 1
            """,
            (membro.projeto_id, membro.usuario_id),
            fetch=True
        )
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuário já é membro ativo deste projeto"
            )
        
        # Validar papel
        papeis_validos = ['gerente', 'engenheiro', 'tecnico', 'colaborador']
        if membro.papel not in papeis_validos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Papel inválido. Use: {', '.join(papeis_validos)}"
            )
        
        # Inserir membro
        data_entrada = membro.data_entrada or datetime.now().strftime('%Y-%m-%d')
        membro_id = db.execute_query(
            """
            INSERT INTO equipes (projeto_id, usuario_id, papel, data_entrada, ativo, criado_em)
            VALUES (%s, %s, %s, %s, 1, datetime('now'))
            """,
            (membro.projeto_id, membro.usuario_id, membro.papel, data_entrada)
        )
        
        return {
            "message": "Membro adicionado à equipe com sucesso",
            "id": membro_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao adicionar membro: {str(e)}"
        )


@router.put("/{membro_id}")
async def atualizar_membro(
    membro_id: int,
    dados: EquipeUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Atualiza informações de um membro da equipe
    """
    db = DatabaseHelper()
    
    try:
        # Verificar se membro existe
        membro = db.execute_query(
            "SELECT id FROM equipes WHERE id = %s",
            (membro_id,),
            fetch=True
        )
        if not membro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Membro {membro_id} não encontrado"
            )
        
        # Construir update dinamicamente
        updates = []
        params = []
        
        if dados.papel is not None:
            papeis_validos = ['gerente', 'engenheiro', 'tecnico', 'colaborador']
            if dados.papel not in papeis_validos:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Papel inválido. Use: {', '.join(papeis_validos)}"
                )
            updates.append("papel = %s")
            params.append(dados.papel)
        
        if dados.data_saida is not None:
            updates.append("data_saida = %s")
            params.append(dados.data_saida)
        
        if dados.ativo is not None:
            updates.append("ativo = %s")
            params.append(1 if dados.ativo else 0)
        
        if not updates:
            return {"message": "Nenhuma alteração solicitada"}
        
        params.append(membro_id)
        query = f"UPDATE equipes SET {', '.join(updates)} WHERE id = %s"
        
        db.execute_query(query, tuple(params))
        
        return {"message": "Membro atualizado com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar membro: {str(e)}"
        )


@router.delete("/{membro_id}")
async def remover_membro(
    membro_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Remove um membro da equipe (soft delete - marca como inativo)
    """
    db = DatabaseHelper()
    
    try:
        # Verificar se membro existe
        membro = db.execute_query(
            "SELECT id, ativo FROM equipes WHERE id = %s",
            (membro_id,),
            fetch=True
        )
        if not membro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Membro {membro_id} não encontrado"
            )
        
        # Soft delete
        db.execute_query(
            "UPDATE equipes SET ativo = 0, data_saida = date('now') WHERE id = %s",
            (membro_id,)
        )
        
        return {"message": "Membro removido da equipe com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover membro: {str(e)}"
        )


@router.get("/usuario/{usuario_id}")
async def listar_projetos_usuario(
    usuario_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Lista todos os projetos em que um usuário participa
    """
    db = DatabaseHelper()
    
    try:
        projetos = db.execute_query(
            """
            SELECT 
                e.id as membro_id,
                e.projeto_id,
                p.nome as projeto_nome,
                p.status as projeto_status,
                e.papel,
                e.data_entrada,
                e.ativo
            FROM equipes e
            INNER JOIN projetos p ON e.projeto_id = p.id
            WHERE e.usuario_id = %s
            ORDER BY e.ativo DESC, e.data_entrada DESC
            """,
            (usuario_id,),
            fetch=True
        )
        
        return {
            "usuario_id": usuario_id,
            "total_projetos": len(projetos) if projetos else 0,
            "projetos": projetos or []
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar projetos: {str(e)}"
        )


@router.get("/meus-projetos")
async def listar_meus_projetos(
    current_user: dict = Depends(get_current_active_user)
):
    """
    Lista todos os projetos do usuário logado
    """
    user_id = current_user.get("user_id") or current_user.get("id")
    db = DatabaseHelper()
    
    try:
        projetos = db.execute_query(
            """
            SELECT 
                e.id as membro_id,
                e.projeto_id,
                p.nome as projeto_nome,
                p.descricao,
                p.status as projeto_status,
                e.papel,
                e.data_entrada,
                e.ativo
            FROM equipes e
            INNER JOIN projetos p ON e.projeto_id = p.id
            WHERE e.usuario_id = %s AND e.ativo = 1
            ORDER BY e.data_entrada DESC
            """,
            (user_id,),
            fetch=True
        )
        
        return {
            "total_projetos": len(projetos) if projetos else 0,
            "projetos": projetos or []
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar projetos: {str(e)}"
        )


# ===== CONVITES =====

@router.post("/convites")
async def criar_convite(
    convite: ConviteEquipeCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Cria um convite para adicionar usuário ao projeto
    """
    db = DatabaseHelper()
    
    try:
        # Verificar se projeto existe
        projeto = db.execute_query(
            "SELECT id, nome FROM projetos WHERE id = %s",
            (convite.projeto_id,),
            fetch=True
        )
        if not projeto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Projeto {convite.projeto_id} não encontrado"
            )
        
        # Gerar token único
        token = secrets.token_urlsafe(32)
        expiracao = datetime.now() + timedelta(hours=convite.expiracao_horas)
        
        # Inserir convite
        convite_id = db.execute_query(
            """
            INSERT INTO convites_equipes (
                projeto_id, email_convidado, papel, token, 
                data_expiracao, criado_por, criado_em
            ) VALUES (%s, %s, %s, %s, %s, %s, datetime('now'))
            """,
            (
                convite.projeto_id,
                convite.email_convidado,
                convite.papel,
                token,
                expiracao.strftime('%Y-%m-%d %H:%M:%S'),
                current_user.get("user_id") or current_user.get("id")
            )
        )
        
        return {
            "message": "Convite criado com sucesso",
            "id": convite_id,
            "token": token,
            "expira_em": expiracao.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar convite: {str(e)}"
        )


@router.post("/convites/aceitar")
async def aceitar_convite(
    dados: ConviteAceitar,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Aceita um convite de equipe usando o token
    """
    db = DatabaseHelper()
    
    try:
        # Buscar convite pelo token
        convite = db.execute_query(
            """
            SELECT id, projeto_id, papel, email_convidado, data_expiracao, usado
            FROM convites_equipes
            WHERE token = %s
            """,
            (dados.token,),
            fetch=True
        )
        
        if not convite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Convite não encontrado ou inválido"
            )
        
        convite = convite[0]
        
        # Verificar se já foi usado
        if convite.get('usado'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este convite já foi utilizado"
            )
        
        # Verificar expiração
        expiracao = datetime.fromisoformat(convite['data_expiracao'])
        if datetime.now() > expiracao:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este convite expirou"
            )
        
        # Verificar se usuário já está no projeto
        existente = db.execute_query(
            "SELECT id FROM equipes WHERE projeto_id = %s AND usuario_id = %s AND ativo = 1",
            (convite['projeto_id'], dados.usuario_id),
            fetch=True
        )
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuário já é membro deste projeto"
            )
        
        # Adicionar à equipe
        membro_id = db.execute_query(
            """
            INSERT INTO equipes (projeto_id, usuario_id, papel, data_entrada, ativo, criado_em)
            VALUES (%s, %s, %s, date('now'), 1, datetime('now'))
            """,
            (convite['projeto_id'], dados.usuario_id, convite['papel'])
        )
        
        # Marcar convite como usado
        db.execute_query(
            "UPDATE convites_equipes SET usado = 1, usado_em = datetime('now') WHERE id = %s",
            (convite['id'],)
        )
        
        return {
            "message": "Convite aceito! Você foi adicionado ao projeto.",
            "membro_id": membro_id,
            "projeto_id": convite['projeto_id']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao aceitar convite: {str(e)}"
        )


@router.get("/convites/projeto/{projeto_id}")
async def listar_convites_projeto(
    projeto_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Lista convites pendentes de um projeto
    """
    db = DatabaseHelper()
    
    try:
        convites = db.execute_query(
            """
            SELECT 
                c.id, c.email_convidado, c.papel, 
                c.data_expiracao, c.usado, c.criado_em,
                u.nome as criado_por_nome
            FROM convites_equipes c
            LEFT JOIN usuarios u ON c.criado_por = u.id
            WHERE c.projeto_id = %s AND (c.usado = 0 OR c.usado IS NULL)
            ORDER BY c.criado_em DESC
            """,
            (projeto_id,),
            fetch=True
        )
        
        return {
            "projeto_id": projeto_id,
            "total_convites": len(convites) if convites else 0,
            "convites": convites or []
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar convites: {str(e)}"
        )


# ===== CÓDIGO DE CONVITE SIMPLES =====

def gerar_codigo_curto(tamanho: int = 6) -> str:
    """Gera um código alfanumérico maiúsculo fácil de digitar"""
    import string
    import random
    caracteres = string.ascii_uppercase + string.digits
    # Remover caracteres confusos (0, O, I, 1, L)
    caracteres = caracteres.replace('0', '').replace('O', '').replace('I', '').replace('1', '').replace('L', '')
    return ''.join(random.choices(caracteres, k=tamanho))


@router.post("/convites/gerar-codigo")
async def gerar_codigo_convite(
    dados: CodigoConviteCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Gera um código de convite simples (6 caracteres) para compartilhar com clientes/membros
    Apenas admin, gerente ou criador do projeto pode gerar códigos
    """
    db = DatabaseHelper()
    user_id = current_user.get("user_id") or current_user.get("id")
    user_cargo = current_user.get("cargo", "")
    
    try:
        # Verificar se projeto existe
        projeto = db.execute_query(
            "SELECT id, nome, criador_id FROM projetos WHERE id = %s",
            (dados.projeto_id,),
            fetch=True
        )
        if not projeto:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
        
        projeto = projeto[0]
        
        # Verificar permissão (admin, gerente ou criador do projeto)
        if user_cargo not in ['admin', 'gerente'] and projeto.get('criador_id') != user_id:
            # Verificar se é gerente do projeto
            membro = db.execute_query(
                "SELECT papel FROM equipes WHERE projeto_id = %s AND usuario_id = %s AND ativo = 1",
                (dados.projeto_id, user_id),
                fetch=True
            )
            if not membro or membro[0].get('papel') != 'gerente':
                raise HTTPException(status_code=403, detail="Sem permissão para gerar códigos de convite")
        
        # Gerar código único
        codigo = gerar_codigo_curto(6)
        
        # Verificar se código já existe (raro, mas possível)
        tentativas = 0
        while tentativas < 10:
            existente = db.execute_query(
                "SELECT id FROM convites_equipes WHERE token = %s AND (usado = 0 OR usado IS NULL)",
                (codigo,),
                fetch=True
            )
            if not existente:
                break
            codigo = gerar_codigo_curto(6)
            tentativas += 1
        
        # Calcular expiração
        expiracao = datetime.now() + timedelta(hours=dados.expiracao_horas)
        
        # Inserir convite com código simples
        convite_id = db.execute_query(
            """
            INSERT INTO convites_equipes (
                projeto_id, email_convidado, papel, token, 
                data_expiracao, criado_por, criado_em
            ) VALUES (%s, %s, %s, %s, %s, %s, datetime('now'))
            """,
            (
                dados.projeto_id,
                f"codigo_{codigo}@convite.interno",  # Email placeholder
                dados.papel,
                codigo,  # Usar código curto como token
                expiracao.strftime('%Y-%m-%d %H:%M:%S'),
                user_id
            )
        )
        
        return {
            "success": True,
            "message": f"Código de convite gerado para o projeto '{projeto['nome']}'",
            "codigo": codigo,
            "projeto_nome": projeto['nome'],
            "papel": dados.papel,
            "expira_em": expiracao.isoformat(),
            "dias_valido": dados.expiracao_horas // 24
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar código: {str(e)}")


@router.post("/convites/enviar-email")
async def enviar_convite_por_email(
    dados: EnviarConviteEmail,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Gera um código de convite e envia por email usando SendGrid
    O destinatário receberá um email com o código para entrar no projeto
    """
    from utils.email_service import email_service
    
    db = DatabaseHelper()
    user_id = current_user.get("user_id") or current_user.get("id")
    user_cargo = current_user.get("cargo", "")
    user_nome = current_user.get("nome", "Usuário")
    
    try:
        # Verificar se SendGrid está configurado
        if not email_service.is_configured():
            raise HTTPException(
                status_code=503,
                detail="Serviço de email não configurado. Configure SENDGRID_API_KEY."
            )
        
        # Verificar se projeto existe
        projeto = db.execute_query(
            "SELECT id, nome, criador_id FROM projetos WHERE id = %s",
            (dados.projeto_id,),
            fetch=True
        )
        if not projeto:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
        
        projeto = projeto[0]
        
        # Verificar permissão (admin, gerente ou criador do projeto)
        if user_cargo not in ['admin', 'gerente'] and projeto.get('criador_id') != user_id:
            membro = db.execute_query(
                "SELECT papel FROM equipes WHERE projeto_id = %s AND usuario_id = %s AND ativo = 1",
                (dados.projeto_id, user_id),
                fetch=True
            )
            if not membro or membro[0].get('papel') != 'gerente':
                raise HTTPException(status_code=403, detail="Sem permissão para enviar convites")
        
        # Gerar código único
        codigo = gerar_codigo_curto(6)
        
        tentativas = 0
        while tentativas < 10:
            existente = db.execute_query(
                "SELECT id FROM convites_equipes WHERE token = %s AND (usado = 0 OR usado IS NULL)",
                (codigo,),
                fetch=True
            )
            if not existente:
                break
            codigo = gerar_codigo_curto(6)
            tentativas += 1
        
        # Calcular expiração
        expiracao = datetime.now() + timedelta(hours=dados.expiracao_horas)
        
        # Inserir convite
        convite_id = db.execute_query(
            """
            INSERT INTO convites_equipes (
                projeto_id, email_convidado, papel, token, 
                data_expiracao, criado_por, criado_em
            ) VALUES (%s, %s, %s, %s, %s, %s, datetime('now'))
            """,
            (
                dados.projeto_id,
                dados.email_destinatario,
                dados.papel,
                codigo,
                expiracao.strftime('%Y-%m-%d %H:%M:%S'),
                user_id
            )
        )
        
        # Formatar data de expiração
        expira_formatado = expiracao.strftime('%d/%m/%Y às %H:%M')
        
        # Enviar email
        resultado_email = email_service.send_invite_code(
            to_email=dados.email_destinatario,
            codigo=codigo,
            projeto_nome=projeto['nome'],
            papel=dados.papel,
            convidado_por=user_nome,
            expira_em=expira_formatado
        )
        
        if not resultado_email.get('success'):
            # Se falhou o email, ainda retorna o código para uso manual
            return {
                "success": True,
                "warning": "Código gerado mas email não enviado",
                "email_error": resultado_email.get('error'),
                "codigo": codigo,
                "projeto_nome": projeto['nome'],
                "email_destinatario": dados.email_destinatario,
                "papel": dados.papel,
                "expira_em": expiracao.isoformat()
            }
        
        return {
            "success": True,
            "message": f"Convite enviado com sucesso para {dados.email_destinatario}",
            "codigo": codigo,
            "projeto_nome": projeto['nome'],
            "email_destinatario": dados.email_destinatario,
            "papel": dados.papel,
            "expira_em": expiracao.isoformat(),
            "email_enviado": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar convite: {str(e)}")


@router.post("/convites/entrar")
async def entrar_com_codigo(
    dados: CodigoConviteAceitar,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Aceita um código de convite e adiciona o usuário ao projeto
    O usuário deve estar logado
    """
    db = DatabaseHelper()
    user_id = current_user.get("user_id") or current_user.get("id")
    
    try:
        # Normalizar código (maiúsculo, sem espaços)
        codigo = dados.codigo.upper().strip()
        
        # Buscar convite pelo código
        convite = db.execute_query(
            """
            SELECT c.id, c.projeto_id, c.papel, c.expiracao, c.aceito,
                   p.nome as projeto_nome
            FROM convites_equipes c
            JOIN projetos p ON c.projeto_id = p.id
            WHERE c.token = %s
            """,
            (codigo,),
            fetch=True
        )
        
        if not convite:
            raise HTTPException(status_code=404, detail="Código inválido ou expirado")
        
        convite = convite[0]
        
        # Verificar se já foi usado
        if convite.get('aceito'):
            raise HTTPException(status_code=400, detail="Este código já foi utilizado")
        
        # Verificar expiração
        try:
            expiracao = datetime.fromisoformat(convite['expiracao'])
            if datetime.now() > expiracao:
                raise HTTPException(status_code=400, detail="Este código expirou")
        except:
            pass  # Se não conseguir parsear, ignora verificação
        
        # Verificar se usuário já está no projeto
        existente = db.execute_query(
            "SELECT id FROM equipes WHERE projeto_id = %s AND usuario_id = %s AND ativo = 1",
            (convite['projeto_id'], user_id),
            fetch=True
        )
        if existente:
            raise HTTPException(status_code=400, detail="Você já é membro deste projeto")
        
        # Adicionar à equipe
        membro_id = db.execute_query(
            """
            INSERT INTO equipes (projeto_id, usuario_id, papel, data_entrada, ativo, criado_em)
            VALUES (%s, %s, %s, date('now'), 1, datetime('now'))
            """,
            (convite['projeto_id'], user_id, convite['papel'])
        )
        
        # Marcar convite como usado
        db.execute_query(
            "UPDATE convites_equipes SET usado = 1, usado_em = datetime('now') WHERE id = %s",
            (convite['id'],)
        )
        
        return {
            "success": True,
            "message": f"Você entrou no projeto '{convite['projeto_nome']}'!",
            "projeto_id": convite['projeto_id'],
            "projeto_nome": convite['projeto_nome'],
            "papel": convite['papel'],
            "membro_id": membro_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao entrar no projeto: {str(e)}")


@router.get("/convites/validar/{codigo}")
async def validar_codigo(codigo: str):
    """
    Valida um código de convite sem aceitar (público, sem auth)
    Retorna informações do projeto se o código for válido
    """
    db = DatabaseHelper()
    
    try:
        codigo = codigo.upper().strip()
        
        convite = db.execute_query(
            """
            SELECT c.projeto_id, c.papel, c.expiracao, c.aceito,
                   p.nome as projeto_nome, p.descricao as projeto_descricao
            FROM convites_equipes c
            JOIN projetos p ON c.projeto_id = p.id
            WHERE c.token = %s
            """,
            (codigo,),
            fetch=True
        )
        
        if not convite:
            return {"valido": False, "erro": "Código não encontrado"}
        
        convite = convite[0]
        
        if convite.get('aceito'):
            return {"valido": False, "erro": "Código já utilizado"}
        
        try:
            expiracao = datetime.fromisoformat(convite['expiracao'])
            if datetime.now() > expiracao:
                return {"valido": False, "erro": "Código expirado"}
        except:
            pass
        
        return {
            "valido": True,
            "projeto_nome": convite['projeto_nome'],
            "projeto_descricao": convite.get('projeto_descricao', ''),
            "papel": convite['papel']
        }
        
    except Exception as e:
        return {"valido": False, "erro": str(e)}


# ===== PERMISSÕES =====

@router.get("/permissoes/usuario/{usuario_id}")
async def listar_permissoes_usuario(
    usuario_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Lista todas as permissões de um usuário
    """
    db = DatabaseHelper()
    
    try:
        permissoes = db.execute_query(
            """
            SELECT 
                up.id,
                up.permissao_id,
                p.nome as permissao_nome,
                p.descricao as permissao_descricao,
                up.projeto_id,
                pr.nome as projeto_nome
            FROM usuario_permissoes up
            INNER JOIN permissoes p ON up.permissao_id = p.id
            LEFT JOIN projetos pr ON up.projeto_id = pr.id
            WHERE up.usuario_id = %s
            """,
            (usuario_id,),
            fetch=True
        )
        
        return {
            "usuario_id": usuario_id,
            "total_permissoes": len(permissoes) if permissoes else 0,
            "permissoes": permissoes or []
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar permissões: {str(e)}"
        )


@router.post("/permissoes")
async def atribuir_permissao(
    permissao: PermissaoCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Atribui uma permissão a um usuário
    """
    db = DatabaseHelper()
    
    try:
        # Verificar se usuário existe
        usuario = db.execute_query(
            "SELECT id FROM usuarios WHERE id = %s",
            (permissao.usuario_id,),
            fetch=True
        )
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário {permissao.usuario_id} não encontrado"
            )
        
        # Verificar se permissão existe
        perm = db.execute_query(
            "SELECT id FROM permissoes WHERE id = %s",
            (permissao.permissao_id,),
            fetch=True
        )
        if not perm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permissão {permissao.permissao_id} não encontrada"
            )
        
        # Inserir permissão
        perm_id = db.execute_query(
            """
            INSERT INTO usuario_permissoes (usuario_id, permissao_id, projeto_id, criado_em)
            VALUES (%s, %s, %s, datetime('now'))
            """,
            (permissao.usuario_id, permissao.permissao_id, permissao.projeto_id)
        )
        
        return {
            "message": "Permissão atribuída com sucesso",
            "id": perm_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atribuir permissão: {str(e)}"
        )


@router.delete("/permissoes/{permissao_id}")
async def remover_permissao(
    permissao_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Remove uma permissão de um usuário
    """
    db = DatabaseHelper()
    
    try:
        # Verificar se existe
        perm = db.execute_query(
            "SELECT id FROM usuario_permissoes WHERE id = %s",
            (permissao_id,),
            fetch=True
        )
        if not perm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permissão {permissao_id} não encontrada"
            )
        
        db.execute_query(
            "DELETE FROM usuario_permissoes WHERE id = %s",
            (permissao_id,)
        )
        
        return {"message": "Permissão removida com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover permissão: {str(e)}"
        )


@router.get("/permissoes/disponiveis")
async def listar_permissoes_disponiveis(
    current_user: dict = Depends(get_current_active_user)
):
    """
    Lista todas as permissões disponíveis no sistema
    """
    db = DatabaseHelper()
    
    try:
        permissoes = db.execute_query(
            "SELECT id, nome, descricao FROM permissoes ORDER BY nome",
            fetch=True
        )
        
        return {
            "total": len(permissoes) if permissoes else 0,
            "permissoes": permissoes or []
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar permissões: {str(e)}"
        )

