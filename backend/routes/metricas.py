"""
Rotas para métricas e relatórios
Análise de progresso, produtividade e indicadores de desempenho
"""
import sys
import os
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

# Adicionar path do database
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'database'))
from db_helper import DatabaseHelper

from middleware.auth_middleware import get_current_active_user

router = APIRouter(prefix="/metricas", tags=["Métricas"])


@router.get("/projeto/{projeto_id}/dashboard")
async def dashboard_projeto(
    projeto_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """Retorna métricas gerais do projeto para dashboard"""
    db = DatabaseHelper()
    
    try:
        # Informações básicas do projeto
        projeto = db.execute_query(
            "SELECT * FROM projetos WHERE id = %s",
            (projeto_id,),
            fetch=True
        )
        
        if not projeto:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
        
        projeto = projeto[0]
        
        # Tarefas
        tarefas = db.execute_query(
            """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'a_fazer' THEN 1 ELSE 0 END) as a_fazer,
                SUM(CASE WHEN status = 'em_execucao' OR status = 'em_andamento' THEN 1 ELSE 0 END) as em_execucao,
                SUM(CASE WHEN status = 'concluida' OR status = 'concluido' THEN 1 ELSE 0 END) as concluidas
            FROM tarefas
            WHERE projeto_id = %s
            """,
            (projeto_id,),
            fetch=True
        )
        
        tarefas_stats = tarefas[0] if tarefas else {
            'total': 0, 'a_fazer': 0, 'em_execucao': 0, 'concluidas': 0
        }
        
        # Membros da equipe
        equipe = db.execute_query(
            """
            SELECT COUNT(*) as total_membros
            FROM equipes
            WHERE projeto_id = %s AND ativo = 1
            """,
            (projeto_id,),
            fetch=True
        )
        
        total_membros = equipe[0]['total_membros'] if equipe else 0
        
        # Orçamento
        orcamento = db.execute_query(
            """
            SELECT 
                COALESCE(SUM(valor_previsto), 0) as orcamento_total,
                COALESCE(SUM(valor_real), 0) as gasto_total
            FROM orcamentos
            WHERE projeto_id = %s
            """,
            (projeto_id,),
            fetch=True
        )
        
        orc_stats = orcamento[0] if orcamento else {'orcamento_total': 0, 'gasto_total': 0}
        
        # Materiais
        materiais = db.execute_query(
            """
            SELECT 
                COUNT(*) as total_materiais,
                COALESCE(SUM(preco_unitario * quantidade_prevista), 0) as valor_previsto
            FROM materiais
            WHERE projeto_id = %s
            """,
            (projeto_id,),
            fetch=True
        )
        
        mat_stats = materiais[0] if materiais else {'total_materiais': 0, 'valor_previsto': 0}
        
        # Documentos
        docs = db.execute_query(
            """
            SELECT COUNT(*) as total_documentos
            FROM documentos
            WHERE projeto_id = %s
            """,
            (projeto_id,),
            fetch=True
        )
        
        total_docs = docs[0]['total_documentos'] if docs else 0
        
        # Calcular progresso geral
        total_tarefas = tarefas_stats['total'] or 0
        concluidas = tarefas_stats['concluidas'] or 0
        progresso = (concluidas / total_tarefas * 100) if total_tarefas > 0 else 0
        
        return {
            "success": True,
            "projeto": {
                "id": projeto['id'],
                "nome": projeto['nome'],
                "status": projeto.get('status', 'em_andamento'),
                "data_inicio": projeto.get('data_inicio'),
                "data_fim_prevista": projeto.get('data_fim_prevista')
            },
            "tarefas": {
                "total": total_tarefas,
                "a_fazer": tarefas_stats['a_fazer'] or 0,
                "em_execucao": tarefas_stats['em_execucao'] or 0,
                "concluidas": concluidas,
                "progresso_percentual": round(progresso, 1)
            },
            "equipe": {
                "total_membros": total_membros
            },
            "financeiro": {
                "orcamento_total": orc_stats['orcamento_total'],
                "gasto_total": orc_stats['gasto_total'],
                "saldo": orc_stats['orcamento_total'] - orc_stats['gasto_total'],
                "percentual_gasto": round((orc_stats['gasto_total'] / orc_stats['orcamento_total'] * 100), 1) if orc_stats['orcamento_total'] > 0 else 0
            },
            "materiais": {
                "total_itens": mat_stats['total_materiais'],
                "valor_previsto": mat_stats['valor_previsto']
            },
            "documentos": {
                "total": total_docs
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projeto/{projeto_id}/tarefas-por-status")
async def tarefas_por_status(
    projeto_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """Retorna distribuição de tarefas por status"""
    db = DatabaseHelper()
    
    try:
        resultado = db.execute_query(
            """
            SELECT status, COUNT(*) as quantidade
            FROM tarefas
            WHERE projeto_id = %s
            GROUP BY status
            """,
            (projeto_id,),
            fetch=True
        )
        
        return {
            "success": True,
            "projeto_id": projeto_id,
            "distribuicao": resultado
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projeto/{projeto_id}/tarefas-por-prioridade")
async def tarefas_por_prioridade(
    projeto_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """Retorna distribuição de tarefas por prioridade"""
    db = DatabaseHelper()
    
    try:
        resultado = db.execute_query(
            """
            SELECT prioridade, COUNT(*) as quantidade
            FROM tarefas
            WHERE projeto_id = %s
            GROUP BY prioridade
            """,
            (projeto_id,),
            fetch=True
        )
        
        return {
            "success": True,
            "projeto_id": projeto_id,
            "distribuicao": resultado
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projeto/{projeto_id}/gastos-por-categoria")
async def gastos_por_categoria(
    projeto_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """Retorna distribuição de gastos por categoria"""
    db = DatabaseHelper()
    
    try:
        resultado = db.execute_query(
            """
            SELECT categoria,
                   COALESCE(SUM(valor_previsto), 0) as previsto,
                   COALESCE(SUM(valor_real), 0) as gasto
            FROM orcamentos
            WHERE projeto_id = %s
            GROUP BY categoria
            ORDER BY gasto DESC
            """,
            (projeto_id,),
            fetch=True
        )
        
        return {
            "success": True,
            "projeto_id": projeto_id,
            "categorias": resultado
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/geral")
async def metricas_gerais(
    current_user: dict = Depends(get_current_active_user)
):
    """Retorna métricas gerais de todos os projetos do usuário"""
    db = DatabaseHelper()
    user_id = current_user.get("user_id") or current_user.get("id")
    
    try:
        # Projetos do usuário
        projetos = db.execute_query(
            """
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN status = 'em_andamento' OR status = 'ativo' THEN 1 ELSE 0 END) as ativos,
                   SUM(CASE WHEN status = 'concluido' THEN 1 ELSE 0 END) as concluidos
            FROM projetos p
            LEFT JOIN equipes e ON p.id = e.projeto_id
            WHERE p.criador_id = %s OR e.usuario_id = %s
            """,
            (user_id, user_id),
            fetch=True
        )
        
        proj_stats = projetos[0] if projetos else {'total': 0, 'ativos': 0, 'concluidos': 0}
        
        # Total de tarefas
        tarefas = db.execute_query(
            """
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN t.status = 'concluida' OR t.status = 'concluido' THEN 1 ELSE 0 END) as concluidas
            FROM tarefas t
            JOIN projetos p ON t.projeto_id = p.id
            LEFT JOIN equipes e ON p.id = e.projeto_id
            WHERE p.criador_id = %s OR e.usuario_id = %s
            """,
            (user_id, user_id),
            fetch=True
        )
        
        tarefas_stats = tarefas[0] if tarefas else {'total': 0, 'concluidas': 0}
        
        return {
            "success": True,
            "projetos": {
                "total": proj_stats['total'] or 0,
                "ativos": proj_stats['ativos'] or 0,
                "concluidos": proj_stats['concluidos'] or 0
            },
            "tarefas": {
                "total": tarefas_stats['total'] or 0,
                "concluidas": tarefas_stats['concluidas'] or 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
async def dashboard_geral(
    current_user: dict = Depends(get_current_active_user)
):
    """
    Dashboard geral do sistema com métricas consolidadas.
    Retorna visão completa para a tela principal.
    """
    db = DatabaseHelper()
    user_id = current_user.get("user_id") or current_user.get("id")
    is_admin = current_user.get("is_admin", False)
    
    try:
        # Query base - admin vê tudo, usuário vê só seus projetos
        if is_admin:
            # Total de projetos
            projetos = db.execute_query(
                """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'planejamento' THEN 1 ELSE 0 END) as planejamento,
                    SUM(CASE WHEN status = 'em_andamento' THEN 1 ELSE 0 END) as em_andamento,
                    SUM(CASE WHEN status = 'em_revisao' THEN 1 ELSE 0 END) as em_revisao,
                    SUM(CASE WHEN status = 'concluido' THEN 1 ELSE 0 END) as concluidos,
                    SUM(CASE WHEN status = 'pausado' THEN 1 ELSE 0 END) as pausados
                FROM projetos
                """,
                fetch=True
            )
            
            # Total de tarefas
            tarefas = db.execute_query(
                """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'a_fazer' THEN 1 ELSE 0 END) as a_fazer,
                    SUM(CASE WHEN status = 'em_andamento' THEN 1 ELSE 0 END) as em_andamento,
                    SUM(CASE WHEN status = 'em_revisao' THEN 1 ELSE 0 END) as em_revisao,
                    SUM(CASE WHEN status = 'concluida' THEN 1 ELSE 0 END) as concluidas
                FROM tarefas
                """,
                fetch=True
            )
            
            # Total de usuários
            usuarios = db.execute_query(
                "SELECT COUNT(*) as total FROM usuarios_new WHERE ativo = 1",
                fetch=True
            )
        else:
            # Projetos do usuário
            projetos = db.execute_query(
                """
                SELECT 
                    COUNT(DISTINCT p.id) as total,
                    SUM(CASE WHEN p.status = 'planejamento' THEN 1 ELSE 0 END) as planejamento,
                    SUM(CASE WHEN p.status = 'em_andamento' THEN 1 ELSE 0 END) as em_andamento,
                    SUM(CASE WHEN p.status = 'em_revisao' THEN 1 ELSE 0 END) as em_revisao,
                    SUM(CASE WHEN p.status = 'concluido' THEN 1 ELSE 0 END) as concluidos,
                    SUM(CASE WHEN p.status = 'pausado' THEN 1 ELSE 0 END) as pausados
                FROM projetos p
                INNER JOIN equipes e ON p.id = e.projeto_id
                WHERE e.usuario_id = %s AND e.ativo = 1
                """,
                (user_id,),
                fetch=True
            )
            
            # Tarefas dos projetos do usuário
            tarefas = db.execute_query(
                """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN t.status = 'a_fazer' THEN 1 ELSE 0 END) as a_fazer,
                    SUM(CASE WHEN t.status = 'em_andamento' THEN 1 ELSE 0 END) as em_andamento,
                    SUM(CASE WHEN t.status = 'em_revisao' THEN 1 ELSE 0 END) as em_revisao,
                    SUM(CASE WHEN t.status = 'concluida' THEN 1 ELSE 0 END) as concluidas
                FROM tarefas t
                INNER JOIN projetos p ON t.projeto_id = p.id
                INNER JOIN equipes e ON p.id = e.projeto_id
                WHERE e.usuario_id = %s AND e.ativo = 1
                """,
                (user_id,),
                fetch=True
            )
            
            usuarios = [{"total": 0}]
        
        proj_stats = projetos[0] if projetos else {}
        tar_stats = tarefas[0] if tarefas else {}
        
        # Calcular progresso geral
        total_tarefas = tar_stats.get('total', 0) or 0
        concluidas = tar_stats.get('concluidas', 0) or 0
        progresso_geral = round((concluidas / total_tarefas * 100), 1) if total_tarefas > 0 else 0
        
        # Atividades recentes (últimas 5)
        atividades = db.execute_query(
            """
            SELECT 'tarefa' as tipo, t.titulo as descricao, t.criado_em as data
            FROM tarefas t
            ORDER BY t.criado_em DESC
            LIMIT 5
            """,
            fetch=True
        ) or []
        
        return {
            "success": True,
            "resumo": {
                "total_projetos": proj_stats.get('total', 0) or 0,
                "projetos_ativos": (proj_stats.get('em_andamento', 0) or 0) + (proj_stats.get('planejamento', 0) or 0),
                "total_tarefas": total_tarefas,
                "tarefas_concluidas": concluidas,
                "progresso_geral": progresso_geral,
                "total_usuarios": usuarios[0]['total'] if usuarios else 0
            },
            "projetos": {
                "total": proj_stats.get('total', 0) or 0,
                "planejamento": proj_stats.get('planejamento', 0) or 0,
                "em_andamento": proj_stats.get('em_andamento', 0) or 0,
                "em_revisao": proj_stats.get('em_revisao', 0) or 0,
                "concluidos": proj_stats.get('concluidos', 0) or 0,
                "pausados": proj_stats.get('pausados', 0) or 0
            },
            "tarefas": {
                "total": total_tarefas,
                "a_fazer": tar_stats.get('a_fazer', 0) or 0,
                "em_andamento": tar_stats.get('em_andamento', 0) or 0,
                "em_revisao": tar_stats.get('em_revisao', 0) or 0,
                "concluidas": concluidas
            },
            "atividades_recentes": atividades
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/config")
async def obter_configuracao_status():
    """
    Retorna configuração de status e cores para o frontend.
    Endpoint público (não requer autenticação).
    """
    from utils.status_manager import obter_todos_status
    
    return {
        "success": True,
        **obter_todos_status()
    }

