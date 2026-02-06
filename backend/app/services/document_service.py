"""
DocumentService - Lógica de negócio para Documentos
"""

import os
import logging
import hashlib
import shutil
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from app.repositories import DocumentRepository, TeamRepository

logger = logging.getLogger(__name__)


class DocumentService:
    """Service para operações de documentos"""
    
    UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads" / "documentos"
    ALLOWED_EXTENSIONS = {
        'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
        'dwg', 'dxf', 'rvt',  # Arquivos de engenharia
        'jpg', 'jpeg', 'png', 'gif',  # Imagens
        'zip', 'rar', '7z'  # Compactados
    }
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    def __init__(self):
        self.doc_repo = DocumentRepository()
        self.team_repo = TeamRepository()
        
        # Criar diretório de uploads se não existir
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    def list_documents(
        self, 
        project_id: int, 
        user_id: int,
        categoria: str = None
    ) -> List[Dict[str, Any]]:
        """
        Lista documentos de um projeto
        """
        # Verificar acesso
        if not self.team_repo.is_member(project_id, user_id):
            logger.warning(f"User {user_id} tried to list documents of project {project_id}")
            return []
        
        return self.doc_repo.find_by_project(project_id, categoria)
    
    def get_document(self, doc_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém documento com verificação de acesso
        """
        doc = self.doc_repo.find_by_id(doc_id)
        if not doc:
            return None
        
        if not self.team_repo.is_member(doc['projeto_id'], user_id):
            return None
        
        return doc
    
    def upload_document(
        self,
        project_id: int,
        file_data: bytes,
        filename: str,
        user_id: int,
        categoria: str = None,
        descricao: str = None,
        task_id: int = None
    ) -> Dict[str, Any]:
        """
        Upload de documento
        """
        # Verificar acesso
        if not self.team_repo.is_member(project_id, user_id):
            raise PermissionError("Sem permissão para upload neste projeto")
        
        # Validar extensão
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"Extensão não permitida. Use: {', '.join(self.ALLOWED_EXTENSIONS)}")
        
        # Validar tamanho
        if len(file_data) > self.MAX_FILE_SIZE:
            raise ValueError(f"Arquivo muito grande. Máximo: {self.MAX_FILE_SIZE // (1024*1024)}MB")
        
        # Gerar nome único
        file_hash = hashlib.md5(file_data).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = f"{timestamp}_{file_hash}_{filename}"
        
        # Criar pasta do projeto
        project_dir = self.UPLOAD_DIR / str(project_id)
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Salvar arquivo
        file_path = project_dir / safe_name
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        # Criar registro no banco
        doc_data = {
            'projeto_id': project_id,
            'nome': filename,
            'caminho': str(file_path.relative_to(self.UPLOAD_DIR)),
            'tamanho': len(file_data),
            'tipo': ext,
            'categoria': categoria,
            'descricao': descricao,
            'tarefa_id': task_id,
            'autor_id': user_id,
            'versao': 1
        }
        
        doc_id = self.doc_repo.create(doc_data)
        logger.info(f"Document uploaded: {filename} (ID: {doc_id}) by user {user_id}")
        
        return self.doc_repo.find_by_id(doc_id)
    
    def download_document(self, doc_id: int, user_id: int) -> Optional[tuple]:
        """
        Retorna dados para download do documento
        Returns: (file_path, filename, content_type)
        """
        doc = self.get_document(doc_id, user_id)
        if not doc:
            return None
        
        file_path = self.UPLOAD_DIR / doc['caminho']
        if not file_path.exists():
            logger.error(f"Document file not found: {file_path}")
            return None
        
        content_type = self._get_content_type(doc['tipo'])
        
        return (file_path, doc['nome'], content_type)
    
    def delete_document(self, doc_id: int, user_id: int) -> bool:
        """
        Deleta documento
        """
        doc = self.doc_repo.find_by_id(doc_id)
        if not doc:
            return False
        
        # Verificar se é gerente ou autor
        is_manager = self.team_repo.is_manager(doc['projeto_id'], user_id)
        is_author = doc.get('autor_id') == user_id
        
        if not (is_manager or is_author):
            raise PermissionError("Sem permissão para deletar este documento")
        
        # Remover arquivo físico
        file_path = self.UPLOAD_DIR / doc['caminho']
        if file_path.exists():
            file_path.unlink()
        
        # Remover do banco
        self.doc_repo.delete(doc_id)
        logger.info(f"Document {doc_id} deleted by user {user_id}")
        
        return True
    
    def update_document(
        self,
        doc_id: int,
        file_data: bytes,
        filename: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Atualiza documento (nova versão)
        """
        doc = self.doc_repo.find_by_id(doc_id)
        if not doc:
            raise ValueError("Documento não encontrado")
        
        # Verificar permissão
        if not self.team_repo.is_member(doc['projeto_id'], user_id):
            raise PermissionError("Sem permissão")
        
        # Gerar novo nome
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        file_hash = hashlib.md5(file_data).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_version = (doc.get('versao', 1) or 1) + 1
        safe_name = f"{timestamp}_{file_hash}_v{new_version}_{filename}"
        
        # Salvar novo arquivo
        project_dir = self.UPLOAD_DIR / str(doc['projeto_id'])
        file_path = project_dir / safe_name
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        # Atualizar registro
        self.doc_repo.update(doc_id, {
            'caminho': str(file_path.relative_to(self.UPLOAD_DIR)),
            'tamanho': len(file_data),
            'versao': new_version
        })
        
        logger.info(f"Document {doc_id} updated to version {new_version}")
        
        return self.doc_repo.find_by_id(doc_id)
    
    def search_documents(
        self, 
        project_id: int, 
        termo: str, 
        user_id: int
    ) -> List[Dict[str, Any]]:
        """
        Pesquisa documentos
        """
        if not self.team_repo.is_member(project_id, user_id):
            return []
        
        return self.doc_repo.search(project_id, termo)
    
    def get_categories(self, project_id: int, user_id: int) -> List[str]:
        """
        Lista categorias de documentos do projeto
        """
        if not self.team_repo.is_member(project_id, user_id):
            return []
        
        return self.doc_repo.get_categories(project_id)
    
    def get_statistics(self, project_id: int, user_id: int) -> Dict[str, Any]:
        """
        Retorna estatísticas de documentos
        """
        if not self.team_repo.is_member(project_id, user_id):
            return {}
        
        stats = self.doc_repo.get_statistics(project_id)
        
        # Formatar tamanho
        total_bytes = stats.get('tamanho_total', 0) or 0
        if total_bytes >= 1024 * 1024 * 1024:
            stats['tamanho_formatado'] = f"{total_bytes / (1024*1024*1024):.2f} GB"
        elif total_bytes >= 1024 * 1024:
            stats['tamanho_formatado'] = f"{total_bytes / (1024*1024):.2f} MB"
        elif total_bytes >= 1024:
            stats['tamanho_formatado'] = f"{total_bytes / 1024:.2f} KB"
        else:
            stats['tamanho_formatado'] = f"{total_bytes} bytes"
        
        return stats
    
    def _get_content_type(self, ext: str) -> str:
        """Retorna content type baseado na extensão"""
        content_types = {
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xls': 'application/vnd.ms-excel',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'ppt': 'application/vnd.ms-powerpoint',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'zip': 'application/zip',
            'rar': 'application/x-rar-compressed'
        }
        return content_types.get(ext, 'application/octet-stream')
