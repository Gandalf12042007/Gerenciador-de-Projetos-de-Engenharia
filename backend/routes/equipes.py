"""
Rotas de Equipes - Gerenciamento de membros e permissões
Autor: Vicente de Souza
"""

import sys
from pathlib import Path
from typing import List, Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

# Adiciona o diretório database ao path
database_dir = Path(__file__).parent.parent.parent / "database"
sys.path.insert(0, str(database_dir))

from db_helper import DatabaseHelper
from backend.middleware.auth_middleware import get_current_active_user

router = APIRouter(prefix="/equipes", tags=["Equipes"])

# ===== SCHEMAS =====

class EquipeCreate(BaseModel):
    projeto_id: int
    usuario_id: int
    papel: str  # gerente, engenheiro, tecnico, colaborador
    data_entrada: date

class EquipeUpdate(BaseModel):
    papel: Optional[str] = None
    data_saida: Optional[date] = None
    ativo: Optional[bool] = None

class MembroEquipe(BaseModel):
    id: int
    projeto_id: int
    projeto_nome: str
    usuario_id: int
    usuario_nome: str
    usuario_email: str
    usuario_cargo: Optional[str]
    papel: str
    data_entrada: str
    data_saida: Optional[str]
    ativo: bool

class PermissaoCreate(BaseModel):
    usuario_id: int
    permissao_id: int
    projeto_id: Optional[int] = None

# ===== ENDPOINTS =====

@router.get("/projeto/{projeto_id}", response_model=List[MembroEquipe])
async def listar_membros_projeto(
    projeto_id: int,
    ativo: Optional[bool] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Lista todos os membros de um projeto
    
    Args:
        projeto_id: ID do projeto
        ativo: Filtrar por membros ativos (opcional)
        
    Returns:
        Lista de membros com informações do usuário
    """
    db = DatabaseHelper()
    
    try:
        if not db.connect():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao conectar no banco de dados"
            )
        
        # Verificar se projeto existe
        cursor = db.connection.cursor(dictionary=True)
        cursor.execute("SELECT id, nome FROM projetos WHERE id = %s", (projeto_id,))
        projeto = cursor.fetchone()
        
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
            params.append(ativo)
        
        query += " ORDER BY e.data_entrada DESC"
        
        cursor.execute(query, params)
        membros = cursor.fetchall()
        
        cursor.close()
        
        return [
            MembroEquipe(
                id=m['id'],
                projeto_id=m['projeto_id'],
                projeto_nome=m['projeto_nome'],
                usuario_id=m['usuario_id'],
                usuario_nome=m['usuario_nome'],
                usuario_email=m['usuario_email'],
                usuario_cargo=m['usuario_cargo'],
                papel=m['papel'],
                data_entrada=str(m['data_entrada']),
                data_saida=str(m['data_saida']) if m['data_saida'] else None,
                ativo=bool(m['ativo'])
            )
            for m in membros
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar membros: {str(e)}"
        )
    finally:
        db.disconnect()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def adicionar_membro(
    membro: EquipeCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Adiciona um novo membro à equipe do projeto
    
    Args:
        membro: Dados do membro (usuario_id, projeto_id, papel)
        
    Returns:
        ID do membro criado
    """
    db = DatabaseHelper()
    
    try:
        if not db.connect():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao conectar no banco de dados"
            )
        
        cursor = db.connection.cursor(dictionary=True)
        
        # Verificar se projeto existe
        cursor.execute("SELECT id FROM projetos WHERE id = %s", (membro.projeto_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Projeto {membro.projeto_id} não encontrado"
            )
        
        # Verificar se usuário existe
        cursor.execute("SELECT id FROM usuarios WHERE id = %s", (membro.usuario_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário {membro.usuario_id} não encontrado"
            )
        
        # Verificar se já existe membro ativo
        cursor.execute(
            """
            SELECT id FROM equipes 
            WHERE projeto_id = %s AND usuario_id = %s AND ativo = TRUE
            """,
            (membro.projeto_id, membro.usuario_id)
        )
        if cursor.fetchone():
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
        query = """
            INSERT INTO equipes (projeto_id, usuario_id, papel, data_entrada, ativo)
            VALUES (%s, %s, %s, %s, TRUE)
        """
        cursor.execute(query, (
            membro.projeto_id,
            membro.usuario_id,
            membro.papel,
            membro.data_entrada
        ))
        
        membro_id = cursor.lastrowid
        db.connection.commit()
        cursor.close()
        
        return {
            "message": "Membro adicionado à equipe com sucesso",
            "id": membro_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao adicionar membro: {str(e)}"
        )
    finally:
        db.disconnect()


@router.put("/{membro_id}")
async def atualizar_membro(
    membro_id: int,
    dados: EquipeUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Atualiza dados de um membro da equipe (papel, status, data_saida)
    
    Args:
        membro_id: ID do membro na equipe
        dados: Campos a atualizar
        
    Returns:
        Mensagem de sucesso
    """
    db = DatabaseHelper()
    
    try:
        if not db.connect():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao conectar no banco de dados"
            )
        
        cursor = db.connection.cursor(dictionary=True)
        
        # Verificar se membro existe
        cursor.execute("SELECT id FROM equipes WHERE id = %s", (membro_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Membro {membro_id} não encontrado"
            )
        
        # Construir query dinamicamente
        updates = []
        params = []
        
        dados_dict = dados.dict(exclude_unset=True)
        
        # Validar papel se fornecido
        if 'papel' in dados_dict:
            papeis_validos = ['gerente', 'engenheiro', 'tecnico', 'colaborador']
            if dados_dict['papel'] not in papeis_validos:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Papel inválido. Use: {', '.join(papeis_validos)}"
                )
        
        for campo, valor in dados_dict.items():
            updates.append(f"{campo} = %s")
            params.append(valor)
        
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhum campo para atualizar"
            )
        
        params.append(membro_id)
        query = f"UPDATE equipes SET {', '.join(updates)} WHERE id = %s"
        
        cursor.execute(query, params)
        db.connection.commit()
        cursor.close()
        
        return {"message": "Membro atualizado com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar membro: {str(e)}"
        )
    finally:
        db.disconnect()


@router.delete("/{membro_id}")
async def remover_membro(
    membro_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Remove um membro da equipe (soft delete - marca como inativo)
    
    Args:
        membro_id: ID do membro na equipe
        
    Returns:
        Mensagem de sucesso
    """
    db = DatabaseHelper()
    
    try:
        if not db.connect():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao conectar no banco de dados"
            )
        
        cursor = db.connection.cursor(dictionary=True)
        
        # Verificar se membro existe
        cursor.execute("SELECT id FROM equipes WHERE id = %s", (membro_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Membro {membro_id} não encontrado"
            )
        
        # Soft delete: marca como inativo e define data_saida
        from datetime import date
        cursor.execute(
            """
            UPDATE equipes 
            SET ativo = FALSE, data_saida = %s 
            WHERE id = %s
            """,
            (date.today(), membro_id)
        )
        
        db.connection.commit()
        cursor.close()
        
        return {"message": "Membro removido da equipe com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover membro: {str(e)}"
        )
    finally:
        db.disconnect()


@router.get("/usuario/{usuario_id}/permissoes")
async def listar_permissoes_usuario(
    usuario_id: int,
    projeto_id: Optional[int] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Lista todas as permissões de um usuário (global ou por projeto)
    
    Args:
        usuario_id: ID do usuário
        projeto_id: Filtrar por projeto específico (opcional)
        
    Returns:
        Lista de permissões do usuário
    """
    db = DatabaseHelper()
    
    try:
        if not db.connect():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao conectar no banco de dados"
            )
        
        cursor = db.connection.cursor(dictionary=True)
        
        # Verificar se usuário existe
        cursor.execute("SELECT id, nome FROM usuarios WHERE id = %s", (usuario_id,))
        usuario = cursor.fetchone()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário {usuario_id} não encontrado"
            )
        
        # Buscar permissões
        query = """
            SELECT 
                up.id,
                up.usuario_id,
                up.permissao_id,
                p.nome as permissao_nome,
                p.descricao as permissao_descricao,
                up.projeto_id,
                proj.nome as projeto_nome
            FROM usuario_permissoes up
            INNER JOIN permissoes p ON up.permissao_id = p.id
            LEFT JOIN projetos proj ON up.projeto_id = proj.id
            WHERE up.usuario_id = %s
        """
        params = [usuario_id]
        
        if projeto_id is not None:
            query += " AND up.projeto_id = %s"
            params.append(projeto_id)
        
        cursor.execute(query, params)
        permissoes = cursor.fetchall()
        cursor.close()
        
        return {
            "usuario_id": usuario_id,
            "usuario_nome": usuario['nome'],
            "total_permissoes": len(permissoes),
            "permissoes": permissoes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar permissões: {str(e)}"
        )
    finally:
        db.disconnect()
