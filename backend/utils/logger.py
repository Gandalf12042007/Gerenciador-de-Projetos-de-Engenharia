"""
Logger Configuração - Sistema de Logging Estruturado
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path

# Diretório de logs
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


class ColoredFormatter(logging.Formatter):
    """Formatter com cores para terminal"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            reset = self.COLORS['RESET']
            record.levelname = f"{color}{record.levelname}{reset}"
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """Formatter JSON para logs estruturados"""
    
    def format(self, record):
        import json
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Adicionar exception se existir
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Adicionar campos extras
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'ip_address'):
            log_data['ip_address'] = record.ip_address
        
        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(
    log_level: str = None,
    log_to_file: bool = True,
    log_to_console: bool = True,
    json_format: bool = False
):
    """
    Configura logging global da aplicação
    
    Args:
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Se deve salvar logs em arquivo
        log_to_console: Se deve exibir no console
        json_format: Se deve usar formato JSON (para produção)
    """
    log_level = log_level or os.getenv('LOG_LEVEL', 'INFO')
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Limpar handlers existentes
    root_logger.handlers = []
    
    # Formato padrão
    default_format = '[%(asctime)s] %(levelname)-8s %(name)s:%(lineno)d - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Handler de console
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        if json_format:
            console_handler.setFormatter(JSONFormatter())
        else:
            console_handler.setFormatter(ColoredFormatter(default_format, date_format))
        
        root_logger.addHandler(console_handler)
    
    # Handler de arquivo
    if log_to_file:
        # Log geral (rotação por tamanho)
        file_handler = RotatingFileHandler(
            LOG_DIR / 'app.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        
        if json_format:
            file_handler.setFormatter(JSONFormatter())
        else:
            file_handler.setFormatter(logging.Formatter(default_format, date_format))
        
        root_logger.addHandler(file_handler)
        
        # Log de erros separado
        error_handler = RotatingFileHandler(
            LOG_DIR / 'error.log',
            maxBytes=10 * 1024 * 1024,
            backupCount=10,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(default_format, date_format))
        root_logger.addHandler(error_handler)
        
        # Log de auditoria (rotação diária)
        audit_handler = TimedRotatingFileHandler(
            LOG_DIR / 'audit.log',
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        audit_handler.setLevel(logging.INFO)
        audit_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s - %(message)s', date_format
        ))
        
        # Apenas logger de auditoria usa esse handler
        audit_logger = logging.getLogger('audit')
        audit_logger.addHandler(audit_handler)
    
    # Reducir logs de bibliotecas externas
    logging.getLogger('uvicorn').setLevel(logging.WARNING)
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Retorna logger configurado para o módulo
    
    Args:
        name: Nome do módulo (__name__)
    
    Returns:
        Logger configurado
    """
    return logging.getLogger(name)


class RequestLogger:
    """Logger contextual para requests HTTP"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.request_id = None
        self.user_id = None
        self.ip_address = None
    
    def set_context(self, request_id: str = None, user_id: int = None, ip_address: str = None):
        """Define contexto do request"""
        self.request_id = request_id
        self.user_id = user_id
        self.ip_address = ip_address
    
    def _log(self, level: int, message: str, *args, **kwargs):
        """Log com contexto"""
        extra = {
            'request_id': self.request_id,
            'user_id': self.user_id,
            'ip_address': self.ip_address
        }
        extra.update(kwargs.pop('extra', {}))
        self.logger.log(level, message, *args, extra=extra, **kwargs)
    
    def debug(self, message: str, *args, **kwargs):
        self._log(logging.DEBUG, message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        self._log(logging.INFO, message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        self._log(logging.WARNING, message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        self._log(logging.ERROR, message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        self._log(logging.CRITICAL, message, *args, **kwargs)


# Inicializar logging ao importar
setup_logging()
