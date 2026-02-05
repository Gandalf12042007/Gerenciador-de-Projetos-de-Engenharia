"""
Rotas para gerenciamento de materiais
Controle de estoque, fornecedores e consumo por projeto
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

router = APIRouter(prefix="/materiais", tags=["Materiais"])


class MaterialCreate(BaseModel):
    nome: str
    unidade: str
    preco_unitario: float
    descricao: Optional[str] = None
    fornecedor: Optional[str] = None
    quantidade_prevista: Optional[float] = 0


class MaterialUpdate(BaseModel):
    nome: Optional[str] = None
    unidade: Optional[str] = None
    preco_unitario: Optional[float] = None
    descricao: Optional[str] = None
    fornecedor: Optional[str] = None
    quantidade_prevista: Optional[float] = None


@router.get("/projeto/{projeto_id}")
async def listar_materiais(
    projeto_id: int,
    categoria: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Lista todos os materiais de um projeto
    Categorias: cimento, areia, brita, aco, madeira, eletrico, hidraulico, acabamento, outros
    """
    db = DatabaseHelper()
    
    try:
        if categoria:
            materiais = db.execute_query(
                """
                SELECT id, projeto_id, nome, descricao, unidade, preco_unitario,
                       fornecedor, quantidade_prevista, quantidade_utilizada,
                       (preco_unitario * quantidade_prevista) as valor_previsto,
                       (preco_unitario * quantidade_utilizada) as valor_utilizado
                FROM materiais
                WHERE projeto_id = %s
                ORDER BY nome
                """,
                (projeto_id,),
                fetch=True
            )
        else:
            materiais = db.execute_query(
                """
                SELECT id, projeto_id, nome, descricao, unidade, preco_unitario,
                       fornecedor, quantidade_prevista, quantidade_utilizada,
                       (preco_unitario * quantidade_prevista) as valor_previsto,
                       (preco_unitario * quantidade_utilizada) as valor_utilizado
                FROM materiais
                WHERE projeto_id = %s
                ORDER BY nome
                """,
                (projeto_id,),
                fetch=True
            )
        
        # Calcular totais
        total_previsto = sum(m.get('valor_previsto', 0) or 0 for m in materiais)
        total_utilizado = sum(m.get('valor_utilizado', 0) or 0 for m in materiais)
        
        return {
            "success": True,
            "total_materiais": len(materiais),
            "total_previsto": total_previsto,
            "total_utilizado": total_utilizado,
            "materiais": materiais
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projeto/{projeto_id}")
async def criar_material(
    projeto_id: int,
    material: MaterialCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Adiciona um novo material ao projeto"""
    db = DatabaseHelper()
    
    try:
        material_id = db.execute_query(
            """
            INSERT INTO materiais 
            (projeto_id, nome, descricao, unidade, preco_unitario,
             fornecedor, quantidade_prevista, quantidade_utilizada)
            VALUES (%s, %s, %s, %s, %s, %s, 0, 0)
            """,
            (
                projeto_id, material.nome, material.descricao,
                material.unidade, material.preco_unitario,
                material.fornecedor
            )
        )
        
        return {
            "success": True,
            "message": "Material adicionado com sucesso",
            "material_id": material_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{material_id}")
async def atualizar_material(
    material_id: int,
    material: MaterialUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """Atualiza informações de um material"""
    db = DatabaseHelper()
    
    try:
        updates = []
        params = []
        
        if material.nome:
            updates.append("nome = %s")
            params.append(material.nome)
        if material.unidade:
            updates.append("unidade = %s")
            params.append(material.unidade)
        if material.preco_unitario is not None:
            updates.append("preco_unitario = %s")
            params.append(material.preco_unitario)
        if material.descricao:
            updates.append("descricao = %s")
            params.append(material.descricao)
        if material.fornecedor:
            updates.append("fornecedor = %s")
            params.append(material.fornecedor)
        if material.quantidade_prevista is not None:
            updates.append("quantidade_prevista = %s")
            params.append(material.quantidade_prevista)
        
        if not updates:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
        
        params.append(material_id)
        query = f"UPDATE materiais SET {', '.join(updates)} WHERE id = %s"
        
        db.execute_query(query, tuple(params))
        
        return {
            "success": True,
            "message": "Material atualizado com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{material_id}/adicionar-estoque")
async def adicionar_estoque(
    material_id: int,
    quantidade: float,
    current_user: dict = Depends(get_current_active_user)
):
    """Adiciona quantidade ao estoque de um material"""
    db = DatabaseHelper()
    
    try:
        db.execute_query(
            """
            UPDATE materiais
            SET quantidade_prevista = quantidade_prevista + %s
            WHERE id = %s
            """,
            (quantidade, material_id)
        )
        
        return {
            "success": True,
            "message": f"Adicionado {quantidade} unidades ao estoque"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{material_id}/usar")
async def usar_material(
    material_id: int,
    quantidade: float,
    current_user: dict = Depends(get_current_active_user)
):
    """Registra uso de material (consome do estoque)"""
    db = DatabaseHelper()
    
    try:
        # Verificar estoque disponível
        result = db.execute_query(
            "SELECT quantidade_prevista, quantidade_utilizada FROM materiais WHERE id = %s",
            (material_id,),
            fetch=True
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Material não encontrado")
        
        disponivel = (result[0]['quantidade_prevista'] or 0) - (result[0]['quantidade_utilizada'] or 0)
        if disponivel < quantidade:
            raise HTTPException(
                status_code=400,
                detail=f"Estoque insuficiente. Disponível: {disponivel}"
            )
        
        # Atualizar uso
        db.execute_query(
            """
            UPDATE materiais
            SET quantidade_utilizada = quantidade_utilizada + %s
            WHERE id = %s
            """,
            (quantidade, material_id)
        )
        
        return {
            "success": True,
            "message": f"Consumido {quantidade} unidades do estoque"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{material_id}")
async def deletar_material(
    material_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """Deleta um material do projeto"""
    db = DatabaseHelper()
    
    try:
        # Verificar se existe
        existing = db.execute_query(
            "SELECT id FROM materiais WHERE id = %s",
            (material_id,),
            fetch=True
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Material não encontrado")
        
        db.execute_query("DELETE FROM materiais WHERE id = %s", (material_id,))
        
        return {
            "success": True,
            "message": "Material deletado com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

