"""
Rotas para métricas e relatórios
Análise de progresso, produtividade e indicadores de desempenho
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/metricas", tags=["Métricas"])

@router.get("/{projeto_id}/dashboard")
async def dashboard_projeto(
    projeto_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Retorna métricas gerais do projeto para dashboard"""
    from database.db_helper import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Informações básicas do projeto
        cursor.execute("""
            SELECT * FROM projetos WHERE id = %s
        """, (projeto_id,))
        projeto = cursor.fetchone()
        
        if not projeto:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
        
        # Tarefas
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'a_fazer' THEN 1 ELSE 0 END) as a_fazer,
                SUM(CASE WHEN status = 'em_execucao' THEN 1 ELSE 0 END) as em_execucao,
                SUM(CASE WHEN status = 'concluida' THEN 1 ELSE 0 END) as concluidas,
                SUM(CASE WHEN data_limite < CURDATE() AND status != 'concluida' THEN 1 ELSE 0 END) as atrasadas
            FROM tarefas
            WHERE projeto_id = %s
        """, (projeto_id,))
        tarefas = cursor.fetchone()
        
        # Membros da equipe
        cursor.execute("""
            SELECT COUNT(*) as total_membros
            FROM equipes
            WHERE projeto_id = %s
        """, (projeto_id,))
        equipe = cursor.fetchone()
        
        # Orçamento
        cursor.execute("""
            SELECT 
                SUM(valor_previsto) as orcamento_total,
                SUM(valor_gasto) as gasto_total
            FROM orcamentos
            WHERE projeto_id = %s
        """, (projeto_id,))
        orcamento = cursor.fetchone()
        
        # Materiais
        cursor.execute("""
            SELECT 
                COUNT(*) as total_materiais,
                SUM(preco_unitario * quantidade_estoque) as valor_estoque
            FROM materiais
            WHERE projeto_id = %s
        """, (projeto_id,))
        materiais = cursor.fetchone()
        
        # Documentos
        cursor.execute("""
            SELECT COUNT(*) as total_documentos
            FROM documentos
            WHERE projeto_id = %s
        """, (projeto_id,))
        docs = cursor.fetchone()
        
        # Calcular progresso geral
        progresso = 0
        if tarefas['total'] > 0:
            progresso = (tarefas['concluidas'] / tarefas['total']) * 100
        
        return {
            "success": True,
            "projeto": {
                "id": projeto['id'],
                "nome": projeto['nome'],
                "status": projeto['status'],
                "progresso": round(progresso, 1),
                "data_inicio": projeto['data_inicio'],
                "data_fim_prevista": projeto['data_fim_prevista']
            },
            "tarefas": tarefas,
            "equipe": equipe,
            "orcamento": {
                "total": orcamento['orcamento_total'] or 0,
                "gasto": orcamento['gasto_total'] or 0,
                "saldo": (orcamento['orcamento_total'] or 0) - (orcamento['gasto_total'] or 0),
                "percentual_gasto": round((orcamento['gasto_total'] or 0) / (orcamento['orcamento_total'] or 1) * 100, 1)
            },
            "materiais": materiais,
            "documentos": docs
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.get("/{projeto_id}/produtividade")
async def analise_produtividade(
    projeto_id: int,
    periodo_dias: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Análise de produtividade da equipe"""
    from database.db_helper import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Tarefas concluídas por membro nos últimos X dias
        cursor.execute("""
            SELECT 
                e.usuario_id,
                u.nome,
                u.cargo,
                COUNT(t.id) as tarefas_concluidas,
                AVG(DATEDIFF(t.data_conclusao, t.data_inicio)) as tempo_medio_dias
            FROM equipes e
            LEFT JOIN usuarios u ON e.usuario_id = u.id
            LEFT JOIN tarefas t ON t.responsavel_id = e.usuario_id 
                AND t.projeto_id = %s
                AND t.status = 'concluida'
                AND t.data_conclusao >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            WHERE e.projeto_id = %s
            GROUP BY e.usuario_id, u.nome, u.cargo
            ORDER BY tarefas_concluidas DESC
        """, (projeto_id, periodo_dias, projeto_id))
        
        por_membro = cursor.fetchall()
        
        # Taxa de conclusão no prazo
        cursor.execute("""
            SELECT 
                COUNT(*) as total_concluidas,
                SUM(CASE WHEN data_conclusao <= data_limite THEN 1 ELSE 0 END) as no_prazo,
                SUM(CASE WHEN data_conclusao > data_limite THEN 1 ELSE 0 END) as atrasadas
            FROM tarefas
            WHERE projeto_id = %s
              AND status = 'concluida'
              AND data_conclusao >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        """, (projeto_id, periodo_dias))
        
        conclusao = cursor.fetchone()
        
        taxa_no_prazo = 0
        if conclusao['total_concluidas'] > 0:
            taxa_no_prazo = (conclusao['no_prazo'] / conclusao['total_concluidas']) * 100
        
        return {
            "success": True,
            "periodo_dias": periodo_dias,
            "por_membro": por_membro,
            "conclusao_prazo": {
                "total": conclusao['total_concluidas'],
                "no_prazo": conclusao['no_prazo'],
                "atrasadas": conclusao['atrasadas'],
                "taxa_sucesso": round(taxa_no_prazo, 1)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.get("/{projeto_id}/timeline")
async def timeline_projeto(
    projeto_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Timeline de atividades do projeto"""
    from database.db_helper import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Histórico de ações (simplificado - você pode adicionar tabela de logs)
        cursor.execute("""
            SELECT 
                'tarefa_criada' as tipo,
                t.titulo as descricao,
                t.data_criacao as data,
                u.nome as usuario
            FROM tarefas t
            LEFT JOIN usuarios u ON t.responsavel_id = u.id
            WHERE t.projeto_id = %s
            
            UNION ALL
            
            SELECT 
                'documento_upload' as tipo,
                d.nome as descricao,
                d.data_upload as data,
                u.nome as usuario
            FROM documentos d
            LEFT JOIN usuarios u ON d.uploaded_por = u.id
            WHERE d.projeto_id = %s
            
            UNION ALL
            
            SELECT 
                'membro_adicionado' as tipo,
                CONCAT(u.nome, ' - ', e.papel) as descricao,
                e.data_entrada as data,
                'Sistema' as usuario
            FROM equipes e
            LEFT JOIN usuarios u ON e.usuario_id = u.id
            WHERE e.projeto_id = %s
            
            ORDER BY data DESC
            LIMIT 50
        """, (projeto_id, projeto_id, projeto_id))
        
        eventos = cursor.fetchall()
        
        return {
            "success": True,
            "total_eventos": len(eventos),
            "eventos": eventos
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.get("/{projeto_id}/relatorio-completo")
async def relatorio_completo(
    projeto_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Relatório completo do projeto para exportação"""
    from database.db_helper import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Chamar todas as métricas
        dashboard = await dashboard_projeto(projeto_id, current_user)
        produtividade = await analise_produtividade(projeto_id, 30, current_user)
        
        # Adicionar análise financeira detalhada
        cursor.execute("""
            SELECT 
                categoria,
                SUM(valor_previsto) as previsto,
                SUM(valor_gasto) as gasto
            FROM orcamentos
            WHERE projeto_id = %s
            GROUP BY categoria
        """, (projeto_id,))
        
        financeiro_detalhado = cursor.fetchall()
        
        return {
            "success": True,
            "gerado_em": "NOW()",
            "projeto_id": projeto_id,
            "dashboard": dashboard,
            "produtividade": produtividade,
            "financeiro_detalhado": financeiro_detalhado
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
