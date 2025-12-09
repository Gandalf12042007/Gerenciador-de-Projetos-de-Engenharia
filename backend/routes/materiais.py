"""
Rotas para gerenciamento de materiais
Controle de estoque, fornecedores e consumo por projeto
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel
from middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/materiais", tags=["Materiais"])

class MaterialCreate(BaseModel):
    nome: str
    categoria: str
    unidade: str
    preco_unitario: float
    fornecedor: Optional[str] = None
    descricao: Optional[str] = None

class MaterialUpdate(BaseModel):
    nome: Optional[str] = None
    categoria: Optional[str] = None
    unidade: Optional[str] = None
    preco_unitario: Optional[float] = None
    fornecedor: Optional[str] = None
    descricao: Optional[str] = None

@router.get("/{projeto_id}")
async def listar_materiais(
    projeto_id: int,
    categoria: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Lista todos os materiais de um projeto
    Categorias: cimento, areia, brita, aco, madeira, eletrico, hidraulico, acabamento, outros
    """
    from database.db_helper import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
            SELECT m.*, 
                   m.quantidade_estoque,
                   m.quantidade_usada,
                   (m.preco_unitario * m.quantidade_estoque) as valor_estoque,
                   (m.preco_unitario * m.quantidade_usada) as valor_usado
            FROM materiais m
            WHERE m.projeto_id = %s
        """
        params = [projeto_id]
        
        if categoria:
            query += " AND m.categoria = %s"
            params.append(categoria)
        
        query += " ORDER BY m.nome"
        
        cursor.execute(query, params)
        materiais = cursor.fetchall()
        
        # Calcular totais
        total_estoque = sum(m['valor_estoque'] for m in materiais)
        total_usado = sum(m['valor_usado'] for m in materiais)
        
        return {
            "success": True,
            "total_materiais": len(materiais),
            "total_estoque": total_estoque,
            "total_usado": total_usado,
            "materiais": materiais
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.post("/{projeto_id}")
async def criar_material(
    projeto_id: int,
    material: MaterialCreate,
    current_user: dict = Depends(get_current_user)
):
    """Adiciona um novo material ao projeto"""
    from database.db_helper import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
            INSERT INTO materiais 
            (projeto_id, nome, categoria, unidade, preco_unitario,
             fornecedor, descricao, quantidade_estoque, quantidade_usada)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 0, 0)
        """
        cursor.execute(query, (
            projeto_id, material.nome, material.categoria,
            material.unidade, material.preco_unitario,
            material.fornecedor, material.descricao
        ))
        
        material_id = cursor.lastrowid
        conn.commit()
        
        return {
            "success": True,
            "message": "Material adicionado com sucesso",
            "material_id": material_id
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.put("/{material_id}")
async def atualizar_material(
    material_id: int,
    material: MaterialUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Atualiza informações de um material"""
    from database.db_helper import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        updates = []
        params = []
        
        if material.nome:
            updates.append("nome = %s")
            params.append(material.nome)
        if material.categoria:
            updates.append("categoria = %s")
            params.append(material.categoria)
        if material.unidade:
            updates.append("unidade = %s")
            params.append(material.unidade)
        if material.preco_unitario is not None:
            updates.append("preco_unitario = %s")
            params.append(material.preco_unitario)
        if material.fornecedor:
            updates.append("fornecedor = %s")
            params.append(material.fornecedor)
        if material.descricao:
            updates.append("descricao = %s")
            params.append(material.descricao)
        
        if not updates:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
        
        params.append(material_id)
        query = f"UPDATE materiais SET {', '.join(updates)} WHERE id = %s"
        
        cursor.execute(query, params)
        conn.commit()
        
        return {
            "success": True,
            "message": "Material atualizado com sucesso"
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.post("/{material_id}/adicionar-estoque")
async def adicionar_estoque(
    material_id: int,
    quantidade: float,
    current_user: dict = Depends(get_current_user)
):
    """Adiciona quantidade ao estoque de um material"""
    from database.db_helper import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE materiais
            SET quantidade_estoque = quantidade_estoque + %s
            WHERE id = %s
        """, (quantidade, material_id))
        
        conn.commit()
        
        return {
            "success": True,
            "message": f"Adicionado {quantidade} unidades ao estoque"
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.post("/{material_id}/usar")
async def usar_material(
    material_id: int,
    quantidade: float,
    current_user: dict = Depends(get_current_user)
):
    """Registra uso de material (consome do estoque)"""
    from database.db_helper import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Verificar estoque disponível
        cursor.execute("""
            SELECT quantidade_estoque FROM materiais WHERE id = %s
        """, (material_id,))
        
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Material não encontrado")
        
        if result['quantidade_estoque'] < quantidade:
            raise HTTPException(
                status_code=400,
                detail=f"Estoque insuficiente. Disponível: {result['quantidade_estoque']}"
            )
        
        # Atualizar estoque e uso
        cursor.execute("""
            UPDATE materiais
            SET quantidade_estoque = quantidade_estoque - %s,
                quantidade_usada = quantidade_usada + %s
            WHERE id = %s
        """, (quantidade, quantidade, material_id))
        
        conn.commit()
        
        return {
            "success": True,
            "message": f"Consumido {quantidade} unidades do estoque"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.delete("/{material_id}")
async def deletar_material(
    material_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Deleta um material do projeto"""
    from database.db_helper import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM materiais WHERE id = %s", (material_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Material não encontrado")
        
        return {
            "success": True,
            "message": "Material deletado com sucesso"
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
