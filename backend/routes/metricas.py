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

