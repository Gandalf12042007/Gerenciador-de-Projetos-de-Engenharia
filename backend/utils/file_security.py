"""
Segurança de Upload de Arquivos
Desenvolvido por: Vicente de Souza
"""

import os
import mimetypes
from pathlib import Path
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class FileSecurityValidator:
    """Validador de segurança para uploads de arquivos"""
    
    # Extensões permitidas
    ALLOWED_EXTENSIONS = {
        # Documentos
        '.pdf', '.doc', '.docx', '.txt', '.odt',
        '.xlsx', '.xls', '.csv',
        '.ppt', '.pptx',
        # Imagens
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',
        # Arquivos de projeto
        '.dwg', '.dxf', '.step', '.iges', '.stp',
        # Compactados
        '.zip', '.rar', '.7z', '.tar', '.gz'
    }
    
    # MIME types permitidos
    ALLOWED_MIMETYPES = {
        # Documentos
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain',
        'application/vnd.oasis.opendocument.text',
        # Planilhas
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/csv',
        # Apresentações
        'application/vnd.ms-powerpoint',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        # Imagens
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/bmp',
        'image/webp',
        'image/x-windows-bmp',
        # Compactados
        'application/zip',
        'application/x-rar-compressed',
        'application/x-7z-compressed',
        'application/x-tar',
        'application/gzip'
    }
    
    # Limites de tamanho por tipo
    SIZE_LIMITS = {
        'documento': 50 * 1024 * 1024,  # 50MB para documentos
        'imagem': 10 * 1024 * 1024,      # 10MB para imagens
        'padrao': 100 * 1024 * 1024      # 100MB padrão
    }
    
    # Assinaturas de arquivo (magic bytes) - proteção contra disfarce
    MAGIC_BYTES = {
        b'%PDF': '.pdf',
        b'\xff\xd8\xff': '.jpg',
        b'\x89PNG\r\n': '.png',
        b'GIF8': '.gif',
        b'BM': '.bmp',
        b'PK\x03\x04': '.zip',
        b'Rar!\x1a\x07': '.rar',
        b'\x50\x4b\x03\x04': '.zip',
    }
    
    @staticmethod
    def validar_arquivo(
        caminho_arquivo: str,
        tipo_documento: str = 'padrao'
    ) -> Tuple[bool, str]:
        """
        Valida segurança do arquivo
        
        Args:
            caminho_arquivo: Caminho completo do arquivo
            tipo_documento: 'documento', 'imagem' ou 'padrao'
            
        Returns:
            (sucesso, mensagem_erro)
        """
        try:
            arquivo = Path(caminho_arquivo)
            
            # 1. Verificar se existe
            if not arquivo.exists():
                return False, "Arquivo não encontrado"
            
            # 2. Verificar extensão
            ext = arquivo.suffix.lower()
            if ext not in FileSecurityValidator.ALLOWED_EXTENSIONS:
                return False, f"Extensão '{ext}' não permitida"
            
            # 3. Verificar tamanho
            tamanho = arquivo.stat().st_size
            limite = FileSecurityValidator.SIZE_LIMITS.get(
                tipo_documento,
                FileSecurityValidator.SIZE_LIMITS['padrao']
            )
            if tamanho > limite:
                return False, f"Arquivo excede {limite / 1024 / 1024:.0f}MB"
            
            # 4. Verificar MIME type
            mime_type, _ = mimetypes.guess_type(str(arquivo))
            if mime_type and mime_type not in FileSecurityValidator.ALLOWED_MIMETYPES:
                return False, f"MIME type '{mime_type}' não permitido"
            
            # 5. Verificar magic bytes (assinatura)
            with open(arquivo, 'rb') as f:
                header = f.read(8)
                
            arquivo_valido = False
            for magic, tipo_ext in FileSecurityValidator.MAGIC_BYTES.items():
                if header.startswith(magic):
                    if tipo_ext == ext:
                        arquivo_valido = True
                    else:
                        return False, f"Arquivo disfarçado: extensão não corresponde"
            
            # Se não encontrou magic bytes mas MIME é válido, aceita
            if not arquivo_valido and mime_type not in FileSecurityValidator.ALLOWED_MIMETYPES:
                logger.warning(f"Arquivo sem assinatura reconhecida: {arquivo.name}")
            
            # 6. Verificar path traversal
            if '..' in str(arquivo) or arquivo.is_symlink():
                return False, "Path traversal detectado"
            
            logger.info(f"Arquivo validado com sucesso: {arquivo.name}")
            return True, "OK"
            
        except Exception as e:
            logger.error(f"Erro ao validar arquivo: {str(e)}")
            return False, f"Erro na validação: {str(e)}"
    
    @staticmethod
    def sanitizar_nome_arquivo(nome_original: str) -> str:
        """
        Remove caracteres perigosos do nome do arquivo
        
        Args:
            nome_original: Nome do arquivo original
            
        Returns:
            Nome sanitizado
        """
        import re
        import uuid
        
        # Gerar UUID para evitar conflitos
        ext = Path(nome_original).suffix
        novo_nome = f"{uuid.uuid4()}{ext}"
        
        # Remover caracteres especiais
        novo_nome = re.sub(r'[^\w\s.-]', '', novo_nome)
        novo_nome = re.sub(r'[\s]+', '_', novo_nome)
        
        return novo_nome


class UploadSecurityManager:
    """Gerenciador de segurança para uploads"""
    
    def __init__(self, diretorio_uploads: str = None):
        if diretorio_uploads is None:
            self.diretorio_uploads = Path(__file__).parent.parent / 'uploads'
        else:
            self.diretorio_uploads = Path(diretorio_uploads)
        
        self.diretorio_uploads.mkdir(parents=True, exist_ok=True)
    
    def salvar_arquivo_seguro(
        self,
        conteudo: bytes,
        nome_original: str,
        tipo_documento: str = 'padrao'
    ) -> Tuple[bool, str, str]:
        """
        Salva arquivo com validações de segurança
        
        Args:
            conteudo: Conteúdo do arquivo em bytes
            nome_original: Nome original do arquivo
            tipo_documento: Tipo de documento
            
        Returns:
            (sucesso, caminho_arquivo, mensagem_erro)
        """
        try:
            # 1. Sanitizar nome
            nome_sanitizado = FileSecurityValidator.sanitizar_nome_arquivo(nome_original)
            
            # 2. Criar caminho seguro
            caminho_completo = self.diretorio_uploads / tipo_documento / nome_sanitizado
            caminho_completo.parent.mkdir(parents=True, exist_ok=True)
            
            # 3. Salvar arquivo temporário
            caminho_temp = Path(str(caminho_completo) + '.tmp')
            with open(caminho_temp, 'wb') as f:
                f.write(conteudo)
            
            # 4. Validar arquivo
            valido, mensagem = FileSecurityValidator.validar_arquivo(
                str(caminho_temp),
                tipo_documento
            )
            
            if not valido:
                caminho_temp.unlink()  # Deletar arquivo inválido
                return False, "", mensagem
            
            # 5. Renomear para arquivo final
            caminho_temp.rename(caminho_completo)
            
            # Retornar path relativo
            caminho_relativo = str(caminho_completo.relative_to(
                self.diretorio_uploads.parent
            ))
            
            return True, caminho_relativo, "OK"
            
        except Exception as e:
            logger.error(f"Erro ao salvar arquivo: {str(e)}")
            return False, "", f"Erro ao salvar: {str(e)}"
    
    def deletar_arquivo_seguro(self, caminho_relativo: str) -> Tuple[bool, str]:
        """
        Deleta arquivo com verificações de segurança
        
        Args:
            caminho_relativo: Caminho relativo do arquivo
            
        Returns:
            (sucesso, mensagem)
        """
        try:
            caminho_completo = self.diretorio_uploads.parent / caminho_relativo
            
            # Verificar se está dentro do diretório de uploads
            if not str(caminho_completo.resolve()).startswith(
                str(self.diretorio_uploads.resolve())
            ):
                return False, "Acesso negado: arquivo fora do diretório permitido"
            
            if caminho_completo.exists():
                caminho_completo.unlink()
                logger.info(f"Arquivo deletado: {caminho_relativo}")
                return True, "OK"
            else:
                return False, "Arquivo não encontrado"
                
        except Exception as e:
            logger.error(f"Erro ao deletar arquivo: {str(e)}")
            return False, f"Erro: {str(e)}"
