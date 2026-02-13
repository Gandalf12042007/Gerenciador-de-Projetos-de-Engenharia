"""
DocumentRepository - Repositório para operações de Documentos
"""

import logging
from typing import List, Dict, Any, Optional
from .base_repository import BaseRepository

logger = logging.getLogger(__name__)


class DocumentRepository(BaseRepository):
    """Repositório para gerenciamento de documentos"""
    
    def __init__(self):
        super().__init__()
        self.table_name = "documentos"
        self.primary_key = "id"
    
    def find_by_project(self, project_id: int, categoria: str = None) -> List[Dict[str, Any]]:
        """Lista documentos de um projeto"""
        query = """
            SELECT d.*, u.nome as autor_nome
            FROM documentos d
            LEFT JOIN usuarios u ON d.autor_id = u.id
            WHERE d.projeto_id = %s
        """
        params = [project_id]
        
        if categoria:
            query += " AND d.categoria = %s"
            params.append(categoria)
        
        query += " ORDER BY d.criado_em DESC"
        
        try:
            return self.execute_raw(query, tuple(params), fetch=True) or []
        except Exception as e:
            logger.error(f"Error finding documents by project {project_id}: {str(e)}")
            raise
    
    def find_by_task(self, task_id: int) -> List[Dict[str, Any]]:
        """Lista documentos anexados a uma tarefa"""
        query = """
            SELECT d.*, u.nome as autor_nome
            FROM documentos d
            LEFT JOIN usuarios u ON d.autor_id = u.id
            WHERE d.tarefa_id = %s
            ORDER BY d.criado_em DESC
        """
        
        try:
            return self.execute_raw(query, (task_id,), fetch=True) or []
        except Exception as e:
            logger.error(f"Error finding documents by task {task_id}: {str(e)}")
            raise
    
    def find_recent(self, project_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Lista documentos recentes de um projeto"""
        query = """
            SELECT d.*, u.nome as autor_nome
            FROM documentos d
            LEFT JOIN usuarios u ON d.autor_id = u.id
            WHERE d.projeto_id = %s
            ORDER BY d.criado_em DESC
            LIMIT %s
        """
        
        try:
            return self.execute_raw(query, (project_id, limit), fetch=True) or []
        except Exception as e:
            logger.error(f"Error finding recent documents: {str(e)}")
            raise
    
    def search(self, project_id: int, termo: str) -> List[Dict[str, Any]]:
        """Pesquisa documentos por nome ou descrição"""
        query = """
            SELECT d.*, u.nome as autor_nome
            FROM documentos d
            LEFT JOIN usuarios u ON d.autor_id = u.id
            WHERE d.projeto_id = %s
            AND (d.nome LIKE %s OR d.descricao LIKE %s)
            ORDER BY d.criado_em DESC
        """
        
        search_term = f"%{termo}%"
        
        try:
            return self.execute_raw(
                query, 
                (project_id, search_term, search_term), 
                fetch=True
            ) or []
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            raise
    
    def get_categories(self, project_id: int) -> List[str]:
        """Lista categorias de documentos usadas no projeto"""
        query = """
            SELECT DISTINCT categoria
            FROM documentos
            WHERE projeto_id = %s AND categoria IS NOT NULL
            ORDER BY categoria
        """
        
        try:
            result = self.execute_raw(query, (project_id,), fetch=True) or []
            return [r['categoria'] for r in result]
        except Exception as e:
            logger.error(f"Error getting document categories: {str(e)}")
            raise
    
    def get_statistics(self, project_id: int) -> Dict[str, Any]:
        """Retorna estatísticas de documentos do projeto"""
        query = """
            SELECT 
                COUNT(*) as total,
                SUM(tamanho) as tamanho_total,
                COUNT(DISTINCT categoria) as categorias
            FROM documentos
            WHERE projeto_id = %s
        """
        
        try:
            result = self.execute_raw(query, (project_id,), fetch=True)
            return result[0] if result else {}
        except Exception as e:
            logger.error(f"Error getting document statistics: {str(e)}")
            raise
    
    def update_version(self, doc_id: int, new_version: int, new_path: str) -> bool:
        """Atualiza versão do documento"""
        return self.update(doc_id, {
            'versao': new_version,
            'caminho': new_path
        })
