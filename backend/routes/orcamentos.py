"""
Rotas para gerenciamento de orçamentos
Controle financeiro de custos por categoria e análise de gastos
"""
import sys
import os
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from pydantic import BaseModel

# Adicionar path do database
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'database'))
from db_helper import DatabaseHelper

from middleware.auth_middleware import get_current_active_user

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


@router.get("/projeto/{projeto_id}")
async def listar_orcamentos(
    projeto_id: int,
    categoria: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Lista todos os itens do orçamento de um projeto
    Categorias: mao_de_obra, materiais, equipamentos, servicos, impostos, outros
    """
    db = DatabaseHelper()
    
    try:
        if categoria:
            orcamentos = db.execute_query(
                """
                SELECT id, projeto_id, categoria, descricao, 
                       valor_previsto, valor_real,
                       (valor_previsto - valor_real) as diferenca,
                       data_prevista, data_pagamento, status
                FROM orcamentos
                WHERE projeto_id = %s AND categoria = %s
                ORDER BY data_prevista, categoria
                """,
                (projeto_id, categoria),
                fetch=True
            )
        else:
            orcamentos = db.execute_query(
                """
                SELECT id, projeto_id, categoria, descricao, 
                       valor_previsto, valor_real,
                       (valor_previsto - valor_real) as diferenca,
                       data_prevista, data_pagamento, status
                FROM orcamentos
                WHERE projeto_id = %s
                ORDER BY data_prevista, categoria
                """,
                (projeto_id,),
                fetch=True
            )
        
        # Calcular totais
        total_previsto = sum(o.get('valor_previsto', 0) or 0 for o in orcamentos)
        total_gasto = sum(o.get('valor_real', 0) or 0 for o in orcamentos)
        diferenca_total = total_previsto - total_gasto
        
        # Estatísticas por categoria
        categorias = {}
        for o in orcamentos:
            cat = o.get('categoria', 'outros')
            if cat not in categorias:
                categorias[cat] = {'previsto': 0, 'real': 0}
            categorias[cat]['previsto'] += o.get('valor_previsto', 0) or 0
            categorias[cat]['real'] += o.get('valor_real', 0) or 0
        
        return {
            "success": True,
            "total_itens": len(orcamentos),
            "total_previsto": total_previsto,
            "total_gasto": total_gasto,
            "diferenca": diferenca_total,
            "por_categoria": categorias,
            "orcamentos": orcamentos
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projeto/{projeto_id}")
async def criar_orcamento(
    projeto_id: int,
    orcamento: OrcamentoCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Adiciona um novo item ao orçamento"""
    db = DatabaseHelper()
    
    try:
        orcamento_id = db.execute_query(
            """
            INSERT INTO orcamentos 
            (projeto_id, categoria, descricao, valor_previsto, valor_real, data_prevista, status)
            VALUES (%s, %s, %s, %s, 0, %s, 'previsto')
            """,
            (
                projeto_id, orcamento.categoria, orcamento.descricao,
                orcamento.valor_previsto, orcamento.data_prevista
            )
        )
        
        return {
            "success": True,
            "message": "Item de orçamento adicionado com sucesso",
            "orcamento_id": orcamento_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{orcamento_id}")
async def atualizar_orcamento(
    orcamento_id: int,
    orcamento: OrcamentoUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """Atualiza um item do orçamento"""
    db = DatabaseHelper()
    
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
            updates.append("valor_real = %s")
            params.append(orcamento.valor_gasto)
        if orcamento.data_prevista:
            updates.append("data_prevista = %s")
            params.append(orcamento.data_prevista)
        if orcamento.data_pagamento:
            updates.append("data_pagamento = %s")
            params.append(orcamento.data_pagamento)
        
        if not updates:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
        
        params.append(orcamento_id)
        query = f"UPDATE orcamentos SET {', '.join(updates)} WHERE id = %s"
        
        db.execute_query(query, tuple(params))
        
        return {
            "success": True,
            "message": "Orçamento atualizado com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{orcamento_id}/registrar-pagamento")
async def registrar_pagamento(
    orcamento_id: int,
    valor: float,
    current_user: dict = Depends(get_current_active_user)
):
    """Registra um pagamento parcial ou total"""
    db = DatabaseHelper()
    
    try:
        db.execute_query(
            """
            UPDATE orcamentos
            SET valor_real = valor_real + %s,
                data_pagamento = datetime('now', 'localtime'),
                status = 'pago'
            WHERE id = %s
            """,
            (valor, orcamento_id)
        )
        
        return {
            "success": True,
            "message": f"Pagamento de R$ {valor:.2f} registrado"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{orcamento_id}")
async def deletar_orcamento(
    orcamento_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """Deleta um item do orçamento"""
    db = DatabaseHelper()
    
    try:
        # Verificar se existe
        existing = db.execute_query(
            "SELECT id FROM orcamentos WHERE id = %s",
            (orcamento_id,),
            fetch=True
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Item de orçamento não encontrado")
        
        db.execute_query("DELETE FROM orcamentos WHERE id = %s", (orcamento_id,))
        
        return {
            "success": True,
            "message": "Item de orçamento deletado com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projeto/{projeto_id}/resumo")
async def resumo_orcamento(
    projeto_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """Retorna um resumo financeiro do projeto"""
    db = DatabaseHelper()
    
    try:
        # Total geral
        totais = db.execute_query(
            """
            SELECT 
                COALESCE(SUM(valor_previsto), 0) as total_previsto,
                COALESCE(SUM(valor_real), 0) as total_gasto
            FROM orcamentos
            WHERE projeto_id = %s
            """,
            (projeto_id,),
            fetch=True
        )
        
        total = totais[0] if totais else {'total_previsto': 0, 'total_gasto': 0}
        
        # Por categoria
        por_categoria = db.execute_query(
            """
            SELECT categoria,
                   COALESCE(SUM(valor_previsto), 0) as previsto,
                   COALESCE(SUM(valor_real), 0) as gasto
            FROM orcamentos
            WHERE projeto_id = %s
            GROUP BY categoria
            """,
            (projeto_id,),
            fetch=True
        )
        
        return {
            "success": True,
            "projeto_id": projeto_id,
            "total_previsto": total['total_previsto'],
            "total_gasto": total['total_gasto'],
            "saldo": total['total_previsto'] - total['total_gasto'],
            "percentual_executado": (total['total_gasto'] / total['total_previsto'] * 100) if total['total_previsto'] > 0 else 0,
            "por_categoria": por_categoria
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

