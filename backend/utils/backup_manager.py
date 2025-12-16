"""
Backup Automático - Sistema de Backup do MySQL
Desenvolvido por: Vicente de Souza
"""

import subprocess
import os
import logging
from datetime import datetime
from pathlib import Path
import schedule
import time

logger = logging.getLogger(__name__)


class BackupManager:
    """Manager para backup automático do MySQL"""
    
    def __init__(self, db_host: str = "localhost", db_user: str = "root", 
                 db_password: str = "", db_name: str = "gerenciador_projetos",
                 backup_dir: str = "backups"):
        """
        Inicializa o gerenciador de backup
        
        Args:
            db_host: Host do MySQL
            db_user: Usuário do MySQL
            db_password: Senha do MySQL
            db_name: Nome do banco
            backup_dir: Diretório para armazenar backups
        """
        self.db_host = db_host
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name
        self.backup_dir = backup_dir
        
        # Criar diretório se não existir
        Path(self.backup_dir).mkdir(parents=True, exist_ok=True)
    
    def criar_backup(self) -> tuple[bool, str]:
        """
        Cria backup do banco de dados
        
        Returns:
            (sucesso, arquivo_backup ou mensagem_erro)
        """
        try:
            # Formato do nome: backup_YYYY-MM-DD_HH-MM-SS.sql
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            arquivo_backup = os.path.join(self.backup_dir, f"backup_{self.db_name}_{timestamp}.sql")
            
            # Comando mysqldump
            comando = [
                "mysqldump",
                f"--host={self.db_host}",
                f"--user={self.db_user}",
                f"--password={self.db_password}",
                "--single-transaction",  # Para InnoDB
                "--routines",            # Incluir stored procedures
                "--triggers",            # Incluir triggers
                self.db_name
            ]
            
            # Executar dump
            logger.info(f"Iniciando backup do banco {self.db_name}...")
            
            with open(arquivo_backup, 'w') as f:
                resultado = subprocess.run(
                    comando,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            if resultado.returncode != 0:
                logger.error(f"Erro ao criar backup: {resultado.stderr}")
                return False, f"Erro ao criar backup: {resultado.stderr}"
            
            # Verificar tamanho do arquivo
            tamanho_mb = os.path.getsize(arquivo_backup) / (1024 * 1024)
            logger.info(f"Backup criado com sucesso: {arquivo_backup} ({tamanho_mb:.2f} MB)")
            
            return True, arquivo_backup
            
        except FileNotFoundError:
            logger.error("mysqldump não encontrado. Instale MySQL Server.")
            return False, "mysqldump não encontrado. Instale MySQL Server."
        except Exception as e:
            logger.error(f"Erro geral ao criar backup: {str(e)}")
            return False, str(e)
    
    def restaurar_backup(self, arquivo_backup: str) -> tuple[bool, str]:
        """
        Restaura banco a partir de um backup
        
        Args:
            arquivo_backup: Caminho do arquivo de backup
            
        Returns:
            (sucesso, mensagem)
        """
        try:
            if not os.path.exists(arquivo_backup):
                return False, f"Arquivo de backup não encontrado: {arquivo_backup}"
            
            logger.info(f"Restaurando backup: {arquivo_backup}")
            
            # Comando mysql para restaurar
            comando = [
                "mysql",
                f"--host={self.db_host}",
                f"--user={self.db_user}",
                f"--password={self.db_password}",
                self.db_name
            ]
            
            with open(arquivo_backup, 'r') as f:
                resultado = subprocess.run(
                    comando,
                    stdin=f,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            if resultado.returncode != 0:
                logger.error(f"Erro ao restaurar backup: {resultado.stderr}")
                return False, f"Erro ao restaurar: {resultado.stderr}"
            
            logger.info(f"Backup restaurado com sucesso")
            return True, "Backup restaurado com sucesso"
            
        except Exception as e:
            logger.error(f"Erro geral ao restaurar backup: {str(e)}")
            return False, str(e)
    
    def listar_backups(self) -> list:
        """
        Lista todos os backups disponíveis
        
        Returns:
            Lista de (arquivo, tamanho_mb, data)
        """
        try:
            backups = []
            
            for arquivo in sorted(os.listdir(self.backup_dir)):
                if arquivo.startswith(f"backup_{self.db_name}"):
                    caminho = os.path.join(self.backup_dir, arquivo)
                    tamanho_mb = os.path.getsize(caminho) / (1024 * 1024)
                    data = datetime.fromtimestamp(os.path.getctime(caminho))
                    
                    backups.append({
                        "arquivo": arquivo,
                        "caminho": caminho,
                        "tamanho_mb": f"{tamanho_mb:.2f}",
                        "data": data.strftime("%Y-%m-%d %H:%M:%S")
                    })
            
            return sorted(backups, key=lambda x: x["data"], reverse=True)
            
        except Exception as e:
            logger.error(f"Erro ao listar backups: {str(e)}")
            return []
    
    def limpar_backups_antigos(self, dias: int = 30):
        """
        Remove backups mais antigos que X dias
        
        Args:
            dias: Número de dias para manter backups
        """
        try:
            agora = datetime.now()
            removidos = 0
            
            for arquivo in os.listdir(self.backup_dir):
                if arquivo.startswith(f"backup_{self.db_name}"):
                    caminho = os.path.join(self.backup_dir, arquivo)
                    idade_dias = (agora - datetime.fromtimestamp(
                        os.path.getctime(caminho)
                    )).days
                    
                    if idade_dias > dias:
                        os.remove(caminho)
                        logger.info(f"Backup removido: {arquivo} ({idade_dias} dias)")
                        removidos += 1
            
            logger.info(f"Limpeza concluída: {removidos} backups removidos")
            return removidos
            
        except Exception as e:
            logger.error(f"Erro ao limpar backups: {str(e)}")
            return 0
    
    def agendar_backup_diario(self, hora: str = "02:00"):
        """
        Agenda backup diário em uma hora específica
        
        Args:
            hora: Hora no formato HH:MM (padrão: 02:00 da manhã)
        """
        def job_backup():
            sucesso, resultado = self.criar_backup()
            if sucesso:
                logger.info(f"✅ Backup agendado completado: {resultado}")
                # Limpar backups com mais de 30 dias
                self.limpar_backups_antigos(dias=30)
            else:
                logger.error(f"❌ Erro no backup agendado: {resultado}")
        
        # Agendar com schedule
        schedule.every().day.at(hora).do(job_backup)
        
        logger.info(f"Backup diário agendado para {hora}")
        
        # Para rodar schedule em background (em produção usar APScheduler)
        while True:
            schedule.run_pending()
            time.sleep(60)
