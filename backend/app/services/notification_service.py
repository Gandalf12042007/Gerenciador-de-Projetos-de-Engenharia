"""
NotificationService - Lógica de notificações
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'database'))
from db_helper import DatabaseHelper

logger = logging.getLogger(__name__)


class NotificationService:
    """Service para notificações"""
    
    def __init__(self):
        self.db = DatabaseHelper()
    
    def create_notification(
        self,
        user_id: int,
        tipo: str,
        titulo: str,
        mensagem: str,
        link: str = None,
        projeto_id: int = None
    ) -> int:
        """
        Cria nova notificação
        """
        query = """
            INSERT INTO notificacoes (usuario_id, tipo, titulo, mensagem, link, projeto_id, lida)
            VALUES (%s, %s, %s, %s, %s, %s, 0)
        """
        
        try:
            notif_id = self.db.execute_query(
                query, 
                (user_id, tipo, titulo, mensagem, link, projeto_id)
            )
            logger.info(f"Notification created for user {user_id}: {titulo}")
            return notif_id
        except Exception as e:
            logger.error(f"Error creating notification: {str(e)}")
            raise
    
    def get_user_notifications(
        self, 
        user_id: int, 
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Lista notificações do usuário
        """
        query = """
            SELECT id, tipo, titulo, mensagem, link, projeto_id, lida, criado_em
            FROM notificacoes
            WHERE usuario_id = %s
        """
        params = [user_id]
        
        if unread_only:
            query += " AND lida = 0"
        
        query += " ORDER BY criado_em DESC LIMIT %s"
        params.append(limit)
        
        try:
            return self.db.execute_query(query, tuple(params), fetch=True) or []
        except Exception as e:
            logger.error(f"Error getting notifications: {str(e)}")
            raise
    
    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """
        Marca notificação como lida
        """
        query = """
            UPDATE notificacoes 
            SET lida = 1 
            WHERE id = %s AND usuario_id = %s
        """
        
        try:
            self.db.execute_query(query, (notification_id, user_id))
            return True
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            raise
    
    def mark_all_as_read(self, user_id: int) -> int:
        """
        Marca todas notificações como lidas
        """
        query = "UPDATE notificacoes SET lida = 1 WHERE usuario_id = %s AND lida = 0"
        
        try:
            self.db.execute_query(query, (user_id,))
            logger.info(f"All notifications marked as read for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error marking all as read: {str(e)}")
            raise
    
    def get_unread_count(self, user_id: int) -> int:
        """
        Conta notificações não lidas
        """
        query = "SELECT COUNT(*) as count FROM notificacoes WHERE usuario_id = %s AND lida = 0"
        
        try:
            result = self.db.execute_query(query, (user_id,), fetch=True)
            return result[0]['count'] if result else 0
        except Exception as e:
            logger.error(f"Error counting unread: {str(e)}")
            return 0
    
    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """
        Deleta notificação
        """
        query = "DELETE FROM notificacoes WHERE id = %s AND usuario_id = %s"
        
        try:
            self.db.execute_query(query, (notification_id, user_id))
            return True
        except Exception as e:
            logger.error(f"Error deleting notification: {str(e)}")
            raise
    
    def delete_old_notifications(self, days: int = 30) -> int:
        """
        Remove notificações antigas
        """
        query = """
            DELETE FROM notificacoes 
            WHERE lida = 1 AND criado_em < DATE_SUB(NOW(), INTERVAL %s DAY)
        """
        
        try:
            self.db.execute_query(query, (days,))
            logger.info(f"Old notifications cleaned (older than {days} days)")
            return True
        except Exception as e:
            logger.error(f"Error deleting old notifications: {str(e)}")
            raise
    
    # === Notificações específicas ===
    
    def notify_task_assigned(self, user_id: int, task_name: str, project_name: str, project_id: int):
        """Notifica atribuição de tarefa"""
        return self.create_notification(
            user_id=user_id,
            tipo='tarefa',
            titulo='Nova tarefa atribuída',
            mensagem=f'Você foi atribuído à tarefa "{task_name}" no projeto {project_name}',
            link=f'/projetos/{project_id}/tarefas',
            projeto_id=project_id
        )
    
    def notify_task_due_soon(self, user_id: int, task_name: str, due_date: str, project_id: int):
        """Notifica tarefa próxima do prazo"""
        return self.create_notification(
            user_id=user_id,
            tipo='alerta',
            titulo='Prazo se aproximando',
            mensagem=f'A tarefa "{task_name}" vence em {due_date}',
            link=f'/projetos/{project_id}/tarefas',
            projeto_id=project_id
        )
    
    def notify_added_to_project(self, user_id: int, project_name: str, role: str, project_id: int):
        """Notifica adição ao projeto"""
        return self.create_notification(
            user_id=user_id,
            tipo='equipe',
            titulo='Adicionado ao projeto',
            mensagem=f'Você foi adicionado ao projeto "{project_name}" como {role}',
            link=f'/projetos/{project_id}',
            projeto_id=project_id
        )
    
    def notify_comment(self, user_id: int, commenter_name: str, task_name: str, project_id: int):
        """Notifica novo comentário"""
        return self.create_notification(
            user_id=user_id,
            tipo='comentario',
            titulo='Novo comentário',
            mensagem=f'{commenter_name} comentou na tarefa "{task_name}"',
            link=f'/projetos/{project_id}/tarefas',
            projeto_id=project_id
        )
    
    def notify_document_uploaded(self, user_id: int, uploader_name: str, doc_name: str, project_id: int):
        """Notifica upload de documento"""
        return self.create_notification(
            user_id=user_id,
            tipo='documento',
            titulo='Novo documento',
            mensagem=f'{uploader_name} enviou o documento "{doc_name}"',
            link=f'/projetos/{project_id}/documentos',
            projeto_id=project_id
        )
