"""
Rotas para gerenciamento de orçamentos
Controle financeiro de custos por categoria e análise de gastos
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel
from middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/orcamentos", tags=["Orçamentos"])

class OrcamentoCreate(BaseModel):
    categoria: str
    descricao: str
    valor_previsto: float
    data_prevista: Optional[str] = None

class OrcamentoUpdate(BaseModel):
    categoria: Optional[str] = None
    descricao: Optional[str] = None
    valor_previsto: Optional[float] = None
    valor_gasto: Optional[float] = None
    data_prevista: Optional[str] = None
    data_pagamento: Optional[str] = None
    status: Optional[str] = None

@router.get("/{projeto_id}")
async def listar_orcamentos(
    projeto_id: int,
    categoria: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Lista todos os itens do orçamento de um projeto
    Categorias: mao_de_obra, materiais, equipamentos, servicos, impostos, outros
    Status: previsto, pago, atrasado
    """
    from database.db_helper import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
            SELECT o.*,
                   (o.valor_previsto - o.valor_gasto) as diferenca,
                   CASE 
                       WHEN o.valor_gasto = 0 THEN 'previsto'
                       WHEN o.data_pagamento IS NULL AND o.data_prevista < CURDATE() THEN 'atrasado'
                       ELSE 'pago'
                   END as status_calculado
            FROM orcamentos o
            WHERE o.projeto_id = %s
        """
        params = [projeto_id]
        
        if categoria:
            query += " AND o.categoria = %s"
            params.append(categoria)
        
        if status:
            having_clause = {
                'previsto': 'HAVING status_calculado = "previsto"',
                'pago': 'HAVING status_calculado = "pago"',
                'atrasado': 'HAVING status_calculado = "atrasado"'
            }
            query += f" {having_clause.get(status, '')}"
        
        query += " ORDER BY o.data_prevista, o.categoria"
        
        cursor.execute(query, params)
        orcamentos = cursor.fetchall()
        
        # Calcular totais
        total_previsto = sum(o['valor_previsto'] for o in orcamentos)
        total_gasto = sum(o['valor_gasto'] for o in orcamentos)
        diferenca_total = total_previsto - total_gasto
        
        # Estatísticas por categoria
        categorias = {}
        for o in orcamentos:
            cat = o['categoria']
            if cat not in categorias:
                categorias[cat] = {
                    'previsto': 0,
                    'gasto': 0,
                    'quantidade': 0
                }
            categorias[cat]['previsto'] += o['valor_previsto']
            categorias[cat]['gasto'] += o['valor_gasto']
            categorias[cat]['quantidade'] += 1
        
        return {
            "success": True,
            "total_itens": len(orcamentos),
            "resumo": {
                "total_previsto": total_previsto,
                "total_gasto": total_gasto,
                "diferenca": diferenca_total,
                "percentual_gasto": (total_gasto / total_previsto * 100) if total_previsto > 0 else 0
            },
            "por_categoria": categorias,
            "orcamentos": orcamentos
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.post("/{projeto_id}")
async def criar_orcamento(
    projeto_id: int,
    orcamento: OrcamentoCreate,
    current_user: dict = Depends(get_current_user)
):
    """Adiciona um novo item ao orçamento do projeto"""
    from database.db_helper import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
            INSERT INTO orcamentos 
            (projeto_id, categoria, descricao, valor_previsto, 
             valor_gasto, data_prevista, status)
            VALUES (%s, %s, %s, %s, 0, %s, 'previsto')
        """
        cursor.execute(query, (
            projeto_id, orcamento.categoria, orcamento.descricao,
            orcamento.valor_previsto, orcamento.data_prevista
        ))
        
        orcamento_id = cursor.lastrowid
        conn.commit()
        
        return {
            "success": True,
            "message": "Item adicionado ao orçamento",
            "orcamento_id": orcamento_id
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.put("/{orcamento_id}")
async def atualizar_orcamento(
    orcamento_id: int,
    orcamento: OrcamentoUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Atualiza um item do orçamento"""
    from database.db_helper import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        updates = []
        params = []
        
        if orcamento.categoria:
            updates.append("categoria = %s")
            params.append(orcamento.categoria)
        if orcamento.descricao:
            updates.append("descricao = %s")
            params.append(orcamento.descricao)
        if orcamento.valor_previsto is not None:
            updates.append("valor_previsto = %s")
            params.append(orcamento.valor_previsto)
        if orcamento.valor_gasto is not None:
            updates.append("valor_gasto = %s")
            params.append(orcamento.valor_gasto)
        if orcamento.data_prevista:
            updates.append("data_prevista = %s")
            params.append(orcamento.data_prevista)
        if orcamento.data_pagamento:
            updates.append("data_pagamento = %s")
            params.append(orcamento.data_pagamento)
        if orcamento.status:
            updates.append("status = %s")
            params.append(orcamento.status)
        
        if not updates:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
        
        params.append(orcamento_id)
        query = f"UPDATE orcamentos SET {', '.join(updates)} WHERE id = %s"
        
        cursor.execute(query, params)
        conn.commit()
        
        return {
            "success": True,
            "message": "Orçamento atualizado com sucesso"
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.post("/{orcamento_id}/registrar-pagamento")
async def registrar_pagamento(
    orcamento_id: int,
    valor_pago: float,
    data_pagamento: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Registra pagamento de um item do orçamento"""
    from database.db_helper import get_db_connection
    from datetime import date
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        data = data_pagamento or date.today().isoformat()
        
        cursor.execute("""
            UPDATE orcamentos
            SET valor_gasto = valor_gasto + %s,
                data_pagamento = %s,
                status = 'pago'
            WHERE id = %s
        """, (valor_pago, data, orcamento_id))
        
        conn.commit()
        
        return {
            "success": True,
            "message": f"Pagamento de R$ {valor_pago:.2f} registrado"
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.get("/{projeto_id}/resumo")
async def resumo_orcamento(
    projeto_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Retorna resumo financeiro do projeto"""
    from database.db_helper import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Totais gerais
        cursor.execute("""
            SELECT 
                SUM(valor_previsto) as total_previsto,
                SUM(valor_gasto) as total_gasto,
                COUNT(*) as total_itens
            FROM orcamentos
            WHERE projeto_id = %s
        """, (projeto_id,))
        
        totais = cursor.fetchone()
        
        # Por categoria
        cursor.execute("""
            SELECT 
                categoria,
                SUM(valor_previsto) as previsto,
                SUM(valor_gasto) as gasto,
                COUNT(*) as itens
            FROM orcamentos
            WHERE projeto_id = %s
            GROUP BY categoria
        """, (projeto_id,))
        
        por_categoria = cursor.fetchall()
        
        # Itens atrasados
        cursor.execute("""
            SELECT COUNT(*) as atrasados
            FROM orcamentos
            WHERE projeto_id = %s
              AND status = 'previsto'
              AND data_prevista < CURDATE()
        """, (projeto_id,))
        
        atrasados = cursor.fetchone()['atrasados']
        
        total_prev = totais['total_previsto'] or 0
        total_gast = totais['total_gasto'] or 0
        
        return {
            "success": True,
            "resumo": {
                "total_previsto": total_prev,
                "total_gasto": total_gast,
                "saldo": total_prev - total_gast,
                "percentual_gasto": (total_gast / total_prev * 100) if total_prev > 0 else 0,
                "total_itens": totais['total_itens'],
                "itens_atrasados": atrasados
            },
            "por_categoria": por_categoria
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.delete("/{orcamento_id}")
async def deletar_orcamento(
    orcamento_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Deleta um item do orçamento"""
    from database.db_helper import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM orcamentos WHERE id = %s", (orcamento_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item não encontrado")
        
        return {
            "success": True,
            "message": "Item deletado do orçamento"
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
