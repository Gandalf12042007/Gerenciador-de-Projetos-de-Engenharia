"""
BaseRepository - Classe base para todos os repositórios
Implementa padrão Repository para abstração de acesso a dados
"""

import sys
import os
import logging
from typing import List, Dict, Any, Optional, TypeVar, Generic
from abc import ABC, abstractmethod

# Adicionar path do database
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'database'))
from db_helper import DatabaseHelper

logger = logging.getLogger(__name__)

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """
    Classe base abstrata para repositories.
    Implementa operações CRUD comuns.
    """
    
    def __init__(self):
        self.db = DatabaseHelper()
        self.table_name: str = ""
        self.primary_key: str = "id"
    
    def find_all(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Lista todos os registros com paginação"""
        query = f"SELECT * FROM {self.table_name} LIMIT %s OFFSET %s"
        try:
            result = self.db.execute_query(query, (limit, offset), fetch=True)
            logger.debug(f"[{self.table_name}] Found {len(result or [])} records")
            return result or []
        except Exception as e:
            logger.error(f"[{self.table_name}] Error in find_all: {str(e)}")
            raise
    
    def find_by_id(self, id: int) -> Optional[Dict[str, Any]]:
        """Busca registro por ID"""
        query = f"SELECT * FROM {self.table_name} WHERE {self.primary_key} = %s"
        try:
            result = self.db.execute_query(query, (id,), fetch=True)
            return result[0] if result else None
        except Exception as e:
            logger.error(f"[{self.table_name}] Error in find_by_id({id}): {str(e)}")
            raise
    
    def find_by(self, field: str, value: Any) -> List[Dict[str, Any]]:
        """Busca registros por campo específico"""
        query = f"SELECT * FROM {self.table_name} WHERE {field} = %s"
        try:
            result = self.db.execute_query(query, (value,), fetch=True)
            return result or []
        except Exception as e:
            logger.error(f"[{self.table_name}] Error in find_by({field}={value}): {str(e)}")
            raise
    
    def create(self, data: Dict[str, Any]) -> int:
        """Cria novo registro e retorna ID"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        
        try:
            result = self.db.execute_query(query, tuple(data.values()))
            logger.info(f"[{self.table_name}] Created record with ID: {result}")
            return result
        except Exception as e:
            logger.error(f"[{self.table_name}] Error in create: {str(e)}")
            raise
    
    def update(self, id: int, data: Dict[str, Any]) -> bool:
        """Atualiza registro por ID"""
        if not data:
            return False
            
        set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE {self.primary_key} = %s"
        values = list(data.values()) + [id]
        
        try:
            self.db.execute_query(query, tuple(values))
            logger.info(f"[{self.table_name}] Updated record ID: {id}")
            return True
        except Exception as e:
            logger.error(f"[{self.table_name}] Error in update({id}): {str(e)}")
            raise
    
    def delete(self, id: int) -> bool:
        """Remove registro por ID"""
        query = f"DELETE FROM {self.table_name} WHERE {self.primary_key} = %s"
        try:
            self.db.execute_query(query, (id,))
            logger.info(f"[{self.table_name}] Deleted record ID: {id}")
            return True
        except Exception as e:
            logger.error(f"[{self.table_name}] Error in delete({id}): {str(e)}")
            raise
    
    def count(self, where: str = None, params: tuple = None) -> int:
        """Conta registros com filtro opcional"""
        query = f"SELECT COUNT(*) as total FROM {self.table_name}"
        if where:
            query += f" WHERE {where}"
        
        try:
            result = self.db.execute_query(query, params, fetch=True)
            return result[0]['total'] if result else 0
        except Exception as e:
            logger.error(f"[{self.table_name}] Error in count: {str(e)}")
            raise
    
    def exists(self, id: int) -> bool:
        """Verifica se registro existe"""
        return self.find_by_id(id) is not None
    
    def execute_raw(self, query: str, params: tuple = None, fetch: bool = False) -> Any:
        """Executa query SQL raw"""
        try:
            return self.db.execute_query(query, params, fetch=fetch)
        except Exception as e:
            logger.error(f"[{self.table_name}] Error in execute_raw: {str(e)}")
            raise
