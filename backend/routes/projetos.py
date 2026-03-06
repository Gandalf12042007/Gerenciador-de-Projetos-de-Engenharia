"""
Rotas de Projetos - CRUD
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
import sys
import os
import csv

# Adicionar path do database
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'database'))
from db_helper import DatabaseHelper

from middleware.auth_middleware import get_current_active_user
from utils.audit import registrar_auditoria
from middleware.permissions import permission_manager
from utils.permissions_decorators import verify_project_access, verify_project_modify, verify_project_delete

router = APIRouter(prefix="/projetos", tags=["Projetos"])


# Schemas
class ProjetoCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    endereco: Optional[str] = None
    cliente: Optional[str] = None
    valor_total: Optional[float] = None
    data_inicio: Optional[date] = None
    data_fim_prevista: Optional[date] = None
    status: str = "planejamento"


class ProjetoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    endereco: Optional[str] = None
    cliente: Optional[str] = None
    valor_total: Optional[float] = None
    data_inicio: Optional[date] = None
    data_fim_prevista: Optional[date] = None
    data_fim_real: Optional[date] = None
    status: Optional[str] = None
    progresso_percentual: Optional[float] = None


class ProjetoResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str]
    endereco: Optional[str]
    cliente: Optional[str]
    valor_total: Optional[float]
    data_inicio: Optional[date]
    data_fim_prevista: Optional[date]
    data_fim_real: Optional[date]
    status: str
    progresso_percentual: float
    criador_id: int
    criado_em: str
    atualizado_em: str
    project_code: Optional[str] = None


class JoinProjectRequest(BaseModel):
    code: str = Field(..., min_length=4, max_length=10, description="Código de acesso ao projeto")


@router.post("/join", response_model=ProjetoResponse)
async def join_project(
    join_data: JoinProjectRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Permite que um usuário entre em um projeto usando código"""
    from services.project_service import ProjectService
    svc = ProjectService()
    user_id = current_user.get("user_id") or current_user.get("id")
    project = svc.join_project_by_code(user_id, join_data.code)
    if not project:
        raise HTTPException(status_code=404, detail="Código de projeto inválido")
    # transformação semelhante à de listar_projetos
    return ProjetoResponse(
        id=project['id'],
        nome=project['nome'],
        descricao=project.get('descricao'),
        endereco=project.get('endereco'),
        cliente=project.get('cliente'),
        valor_total=float(project['valor_total']) if project.get('valor_total') else None,
        data_inicio=project.get('data_inicio'),
        data_fim_prevista=project.get('data_fim_prevista'),
        data_fim_real=project.get('data_fim_real'),
        status=project['status'],
        progresso_percentual=float(project.get('progresso_percentual', 0)),
        criador_id=project['criador_id'],
        criado_em=str(project['criado_em']),
        atualizado_em=str(project['atualizado_em']),
        project_code=project.get('project_code')
    )


@router.get("/", response_model=List[ProjetoResponse])
async def listar_projetos(
    status_filter: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
    current_user: dict = Depends(get_current_active_user)
):
    """Lista projetos visíveis ao usuário (ou todos para admin)"""
    from services.project_service import ProjectService
    svc = ProjectService()
    user_id = current_user.get("user_id") or current_user.get("id")
    result = svc.list_user_projects(user_id, status_filter, page, per_page)
    # Paginação já feita pelo serviço
    return result["items"]


@router.get("/audit/logs")
async def consultar_auditoria(
    projeto_id: int = None,
    usuario_id: int = None,
    data_inicio: str = None,
    data_fim: str = None,
    formato: str = "json",
    current_user: dict = Depends(get_current_active_user)
):
    """
    Consulta/exporta logs de auditoria (apenas admins)
    """
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Apenas administradores podem consultar logs de auditoria")
    
    db = DatabaseHelper()
    
    try:
        query = "SELECT a.*, u.nome as usuario_nome FROM audit_trail a LEFT JOIN usuarios u ON a.usuario_id = u.id WHERE 1=1"
        params = []
        
        if projeto_id:
            query += " AND (a.entidade = 'projeto' AND a.entidade_id = ?)"
            params.append(projeto_id)
        if usuario_id:
            query += " AND a.usuario_id = ?"
            params.append(usuario_id)
        if data_inicio:
            query += " AND a.criado_em >= ?"
            params.append(data_inicio)
        if data_fim:
            query += " AND a.criado_em <= ?"
            params.append(data_fim)
        
        query += " ORDER BY a.criado_em DESC"
        logs = db.execute_query(query, tuple(params), fetch=True) or []
        
        if formato == "csv":
            def iter_csv():
                header = ["id", "usuario_id", "usuario_nome", "entidade", "entidade_id", "acao", "detalhes", "ip", "user_agent", "criado_em"]
                yield ",".join(header) + "\n"
                for l in logs:
                    row = [str(l.get(h, "")) if l.get(h, "") is not None else "" for h in header]
                    yield ",".join(row) + "\n"
            return StreamingResponse(iter_csv(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=audit_logs.csv"})
        
        return JSONResponse(content=logs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar auditoria: {str(e)}")


@router.get("/{projeto_id}", response_model=ProjetoResponse)
async def buscar_projeto(
    projeto_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Busca projeto por ID.
    ADMINISTRADORES têm acesso a qualquer projeto.
    """
    user_id = current_user.get("user_id") or current_user.get("id")
    is_admin = current_user.get("is_admin", False)
    
    # Verificar se usuário tem acesso ao projeto (admin tem acesso total)
    if not permission_manager.is_project_member(user_id, projeto_id, is_admin=is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem acesso a este projeto"
        )
    
    db = DatabaseHelper()
    
    projetos = db.execute_query(
        """
        SELECT id, nome, descricao, endereco, cliente, valor_total,
               data_inicio, data_fim_prevista, data_fim_real, status,
               progresso_percentual, criador_id, criado_em, atualizado_em
        FROM projetos
        WHERE id = %s
        """,
        (projeto_id,),
        fetch=True
    )
    
    if not projetos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado"
        )
    
    p = projetos[0]
    return {
        "id": p['id'],
        "nome": p['nome'],
        "descricao": p.get('descricao'),
        "endereco": p.get('endereco'),
        "cliente": p.get('cliente'),
        "valor_total": float(p['valor_total']) if p.get('valor_total') else None,
        "data_inicio": p.get('data_inicio'),
        "data_fim_prevista": p.get('data_fim_prevista'),
        "data_fim_real": p.get('data_fim_real'),
        "status": p['status'],
        "progresso_percentual": float(p.get('progresso_percentual', 0)),
        "criador_id": p['criador_id'],
        "criado_em": str(p['criado_em']),
        "atualizado_em": str(p['atualizado_em'])
    }


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def criar_projeto(
    projeto: ProjetoCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Cria novo projeto com código de acesso automático
    """
    from services.project_service import ProjectService

    svc = ProjectService()
    try:
        user_id = current_user.get("user_id") or current_user.get("id")
        proj_id = svc.create_project(
            name=projeto.nome,
            description=projeto.descricao,
            created_by=user_id
        )
        # Buscar projeto para obter código
        project = svc.repo.get_by_id(proj_id)
        return {
            "success": True,
            "message": "Projeto criado com sucesso",
            "data": {
                "id": proj_id,
                "project_code": project.get("project_code")
            }
        }
    except Exception as e:
        logger.error(f"Erro ao criar projeto: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar projeto"
        )


@router.put("/{projeto_id}")
async def atualizar_projeto(
    projeto_id: int,
    projeto: ProjetoUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """Atualiza projeto existente (apenas gerente) usando serviço"""
    from services.project_service import ProjectService
    svc = ProjectService()
    user_id = current_user.get("user_id") or current_user.get("id")
    updated = svc.update_project(projeto_id, projeto.dict(exclude_unset=True), user_id)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada ou projeto inexistente"
        )
    return {"message": "Projeto atualizado com sucesso"}


@router.delete("/{projeto_id}")
async def deletar_projeto(
    projeto_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Deleta projeto (apenas criador)
    """
    user_id = current_user.get("user_id") or current_user.get("id")
    
    # Verificar permissão (apenas criador pode deletar)
    if not permission_manager.can_delete_project(user_id, projeto_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o criador do projeto pode deletá-lo"
        )
    
    db = DatabaseHelper()
    
    # Verificar se projeto existe
    existing = db.execute_query(
        "SELECT id FROM projetos WHERE id = %s",
        (projeto_id,),
        fetch=True
    )
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado"
        )
    
    try:
        db.execute_query("DELETE FROM projetos WHERE id = %s", (projeto_id,))
        return {"message": "Projeto deletado com sucesso"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar projeto: {str(e)}"
        )


# ============================================
# SISTEMA DE CÓDIGOS DE ACESSO
# ============================================

class EntrarPorCodigoRequest(BaseModel):
    codigo: str


class EntrarProjetoAdminRequest(BaseModel):
    projeto_id: int


@router.post("/admin/entrar-projeto")
async def admin_entrar_projeto(
    request: EntrarProjetoAdminRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """
    [ADMIN ONLY] Permite administrador acessar qualquer projeto diretamente,
    sem precisar de código de acesso.
    """
    from utils.project_codes import adicionar_usuario_ao_projeto
    
    # Verificar se é admin
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem usar esta função"
        )
    
    db = DatabaseHelper()
    projeto = db.execute_query(
        "SELECT id, nome, descricao, cliente, status FROM projetos WHERE id = %s",
        (request.projeto_id,),
        fetch=True
    )
    
    if not projeto or len(projeto) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado"
        )
    
    projeto = projeto[0]
    user_id = current_user.get("user_id") or current_user.get("id")
    
    # Adicionar admin como gerente do projeto (para ter todas as permissões)
    try:
        resultado = adicionar_usuario_ao_projeto(projeto['id'], user_id, "gerente")
    except:
        # Já é membro, ok
        pass
    
    return {
        "message": "Acesso concedido ao projeto (Admin)",
        "projeto": {
            "id": projeto['id'],
            "nome": projeto['nome'],
            "descricao": projeto.get('descricao'),
            "cliente": projeto.get('cliente'),
            "status": projeto['status']
        }
    }


@router.post("/entrar-por-codigo")
async def entrar_por_codigo(
    request: EntrarPorCodigoRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Usuário entra em projeto usando código (serviço)."""
    from services.project_service import ProjectService
    svc = ProjectService()

    codigo = request.codigo.strip().upper()
    user_id = current_user.get("user_id") or current_user.get("id")

    project = svc.join_project_by_code(user_id, codigo)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projeto não encontrado com este código")

    return {
        "message": "Usuário adicionado ao projeto com sucesso",
        "projeto": {
            "id": project['id'],
            "nome": project['nome'],
            "descricao": project.get('descricao'),
            "cliente": project.get('cliente'),
            "status": project['status']
        }
    }


@router.get("/{projeto_id}/codigo")
async def obter_codigo_projeto(
    projeto_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """Retorna o código de acesso do projeto (somente gerente)"""
    from services.project_service import ProjectService
    svc = ProjectService()
    user_id = current_user.get("user_id") or current_user.get("id")
    code = svc.get_project_code(project_id, user_id)
    if code is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissão negada ou projeto inexistente")
    return {"codigo_acesso": code}


@router.post("/{projeto_id}/regenerar-codigo")
async def regenerar_codigo_projeto(
    projeto_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """Regenera o código de acesso do projeto (somente gerente)"""
    from services.project_service import ProjectService
    svc = ProjectService()
    user_id = current_user.get("user_id") or current_user.get("id")
    new_code = svc.regenerate_project_code(project_id, user_id)
    if new_code is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissão negada ou projeto inexistente")
    return {"message": "Código regenerado com sucesso", "codigo_acesso": new_code}


@router.get("/verificar-codigo/{codigo}")
async def verificar_codigo(codigo: str):
    """Verifica se um código de projeto existe (público, para frontend)"""
    from services.project_service import ProjectService
    svc = ProjectService()
    code = codigo.strip().upper()
    exists = svc.check_code_exists(code)
    return {"valido": exists, "projeto_nome": None if not exists else ""}
