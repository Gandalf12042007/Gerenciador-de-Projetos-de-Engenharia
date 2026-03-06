"""
Validações Inteligentes - Gerenciador de Projetos
Previne erros do usuário e garante integridade dos dados
Desenvolvido por: Vicente de Souza
"""

import re
from typing import Optional, List, Dict, Tuple
from datetime import date, datetime


class ValidacaoErro(Exception):
    """Exceção para erros de validação"""
    def __init__(self, campo: str, mensagem: str):
        self.campo = campo
        self.mensagem = mensagem
        super().__init__(f"{campo}: {mensagem}")


class ValidadorProjeto:
    """Validações para projetos"""
    
    @staticmethod
    def validar_nome(nome: str) -> Tuple[bool, str]:
        """
        Valida nome do projeto.
        - Mínimo 3 caracteres
        - Máximo 200 caracteres
        - Não pode ser apenas espaços
        """
        if not nome or not nome.strip():
            return False, "Nome do projeto é obrigatório"
        
        nome = nome.strip()
        
        if len(nome) < 3:
            return False, "Nome deve ter pelo menos 3 caracteres"
        
        if len(nome) > 200:
            return False, "Nome não pode exceder 200 caracteres"
        
        return True, ""
    
    @staticmethod
    def validar_datas(data_inicio: Optional[date], data_fim: Optional[date]) -> Tuple[bool, str]:
        """
        Valida datas do projeto.
        - Data fim não pode ser anterior à data início
        """
        if data_inicio and data_fim:
            if isinstance(data_inicio, str):
                data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d").date()
            if isinstance(data_fim, str):
                data_fim = datetime.strptime(data_fim, "%Y-%m-%d").date()
            
            if data_fim < data_inicio:
                return False, "Data de término não pode ser anterior à data de início"
        
        return True, ""
    
    @staticmethod
    def validar_valor(valor: Optional[float]) -> Tuple[bool, str]:
        """
        Valida valor do projeto.
        - Deve ser positivo se informado
        """
        if valor is not None and valor < 0:
            return False, "Valor do projeto deve ser positivo"
        
        return True, ""
    
    @staticmethod
    def validar_status(status: str, status_atual: str = None) -> Tuple[bool, str]:
        """
        Valida status do projeto e transição.
        """
        from utils.status_manager import StatusProjeto, pode_transicionar_projeto
        
        status_validos = [s.value for s in StatusProjeto]
        
        if status not in status_validos:
            return False, f"Status inválido. Valores permitidos: {', '.join(status_validos)}"
        
        if status_atual and not pode_transicionar_projeto(status_atual, status):
            return False, f"Não é possível mudar de '{status_atual}' para '{status}'"
        
        return True, ""
    
    @classmethod
    def validar_projeto_completo(cls, dados: Dict) -> List[Dict]:
        """
        Valida todos os campos do projeto.
        Retorna lista de erros encontrados.
        """
        erros = []
        
        # Validar nome
        ok, msg = cls.validar_nome(dados.get('nome', ''))
        if not ok:
            erros.append({"campo": "nome", "mensagem": msg})
        
        # Validar datas
        ok, msg = cls.validar_datas(dados.get('data_inicio'), dados.get('data_fim_prevista'))
        if not ok:
            erros.append({"campo": "datas", "mensagem": msg})
        
        # Validar valor
        ok, msg = cls.validar_valor(dados.get('valor_total'))
        if not ok:
            erros.append({"campo": "valor_total", "mensagem": msg})
        
        return erros


class ValidadorTarefa:
    """Validações para tarefas"""
    
    @staticmethod
    def validar_titulo(titulo: str) -> Tuple[bool, str]:
        """
        Valida título da tarefa.
        - Mínimo 3 caracteres
        - Máximo 200 caracteres
        """
        if not titulo or not titulo.strip():
            return False, "Título da tarefa é obrigatório"
        
        titulo = titulo.strip()
        
        if len(titulo) < 3:
            return False, "Título deve ter pelo menos 3 caracteres"
        
        if len(titulo) > 200:
            return False, "Título não pode exceder 200 caracteres"
        
        return True, ""
    
    @staticmethod
    def validar_descricao(descricao: Optional[str]) -> Tuple[bool, str]:
        """
        Valida descrição da tarefa.
        - Máximo 2000 caracteres
        """
        if descricao and len(descricao) > 2000:
            return False, "Descrição não pode exceder 2000 caracteres"
        
        return True, ""
    
    @staticmethod
    def validar_prioridade(prioridade: str) -> Tuple[bool, str]:
        """
        Valida prioridade da tarefa.
        """
        from utils.status_manager import PrioridadeTarefa
        
        prioridades_validas = [p.value for p in PrioridadeTarefa]
        
        if prioridade not in prioridades_validas:
            return False, f"Prioridade inválida. Valores permitidos: {', '.join(prioridades_validas)}"
        
        return True, ""
    
    @staticmethod
    def validar_status(status: str, status_atual: str = None) -> Tuple[bool, str]:
        """
        Valida status da tarefa e transição.
        """
        from utils.status_manager import StatusTarefa, pode_transicionar_tarefa
        
        status_validos = [s.value for s in StatusTarefa]
        
        if status not in status_validos:
            return False, f"Status inválido. Valores permitidos: {', '.join(status_validos)}"
        
        if status_atual and not pode_transicionar_tarefa(status_atual, status):
            return False, f"Não é possível mudar de '{status_atual}' para '{status}'"
        
        return True, ""
    
    @classmethod
    def validar_tarefa_completa(cls, dados: Dict) -> List[Dict]:
        """
        Valida todos os campos da tarefa.
        """
        erros = []
        
        # Validar título
        ok, msg = cls.validar_titulo(dados.get('titulo', ''))
        if not ok:
            erros.append({"campo": "titulo", "mensagem": msg})
        
        # Validar descrição
        ok, msg = cls.validar_descricao(dados.get('descricao'))
        if not ok:
            erros.append({"campo": "descricao", "mensagem": msg})
        
        # Validar prioridade
        if dados.get('prioridade'):
            ok, msg = cls.validar_prioridade(dados['prioridade'])
            if not ok:
                erros.append({"campo": "prioridade", "mensagem": msg})
        
        return erros


class ValidadorUsuario:
    """Validações para usuários"""
    
    @staticmethod
    def validar_email(email: str) -> Tuple[bool, str]:
        """
        Valida formato de email.
        """
        if not email:
            return False, "Email é obrigatório"
        
        # Regex simples para email
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            return False, "Formato de email inválido"
        
        return True, ""
    
    @staticmethod
    def validar_senha(senha: str) -> Tuple[bool, str]:
        """
        Valida força da senha.
        - Mínimo 8 caracteres
        - Pelo menos 1 letra maiúscula
        - Pelo menos 1 número
        """
        if not senha:
            return False, "Senha é obrigatória"
        
        if len(senha) < 8:
            return False, "Senha deve ter pelo menos 8 caracteres"
        
        if not re.search(r'[A-Z]', senha):
            return False, "Senha deve conter pelo menos uma letra maiúscula"
        
        if not re.search(r'[0-9]', senha):
            return False, "Senha deve conter pelo menos um número"
        
        return True, ""
    
    @staticmethod
    def validar_nome(nome: str) -> Tuple[bool, str]:
        """
        Valida nome do usuário.
        """
        if not nome or not nome.strip():
            return False, "Nome é obrigatório"
        
        nome = nome.strip()
        
        if len(nome) < 3:
            return False, "Nome deve ter pelo menos 3 caracteres"
        
        if len(nome) > 100:
            return False, "Nome não pode exceder 100 caracteres"
        
        return True, ""


def validar_e_lancar(validacoes: List[Dict]):
    """
    Verifica lista de validações e lança exceção HTTP se houver erros.
    Para uso com FastAPI.
    """
    if validacoes:
        from fastapi import HTTPException
        
        mensagens = [f"{v['campo']}: {v['mensagem']}" for v in validacoes]
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Erro de validação",
                "errors": validacoes,
                "summary": "; ".join(mensagens)
            }
        )
