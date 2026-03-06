"""
Sistema de Status Inteligente - Gerenciador de Projetos
Define status, transições e cores para projetos e tarefas
Desenvolvido por: Vicente de Souza
"""

from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime, date


class StatusProjeto(str, Enum):
    """Status disponíveis para projetos"""
    PLANEJAMENTO = "planejamento"
    EM_ANDAMENTO = "em_andamento"
    EM_REVISAO = "em_revisao"
    PAUSADO = "pausado"
    CONCLUIDO = "concluido"
    CANCELADO = "cancelado"


class StatusTarefa(str, Enum):
    """Status disponíveis para tarefas"""
    A_FAZER = "a_fazer"
    EM_ANDAMENTO = "em_andamento"
    EM_REVISAO = "em_revisao"
    CONCLUIDA = "concluida"
    BLOQUEADA = "bloqueada"


class PrioridadeTarefa(str, Enum):
    """Níveis de prioridade"""
    URGENTE = "urgente"
    ALTA = "alta"
    MEDIA = "media"
    BAIXA = "baixa"


# Configuração de cores para status (frontend)
STATUS_CORES = {
    # Projetos
    "planejamento": {"cor": "#3B82F6", "bg": "#EFF6FF", "label": "Planejamento"},
    "em_andamento": {"cor": "#F59E0B", "bg": "#FFFBEB", "label": "Em Andamento"},
    "em_revisao": {"cor": "#8B5CF6", "bg": "#F5F3FF", "label": "Em Revisão"},
    "pausado": {"cor": "#6B7280", "bg": "#F3F4F6", "label": "Pausado"},
    "concluido": {"cor": "#22C55E", "bg": "#F0FDF4", "label": "Concluído"},
    "cancelado": {"cor": "#EF4444", "bg": "#FEF2F2", "label": "Cancelado"},
    # Tarefas
    "a_fazer": {"cor": "#94A3B8", "bg": "#F8FAFC", "label": "A Fazer"},
    "bloqueada": {"cor": "#DC2626", "bg": "#FEF2F2", "label": "Bloqueada"},
}

# Cores para prioridades
PRIORIDADE_CORES = {
    "urgente": {"cor": "#DC2626", "bg": "#FEF2F2", "icon": "🔴"},
    "alta": {"cor": "#F97316", "bg": "#FFF7ED", "icon": "🟠"},
    "media": {"cor": "#EAB308", "bg": "#FEFCE8", "icon": "🟡"},
    "baixa": {"cor": "#22C55E", "bg": "#F0FDF4", "icon": "🟢"},
}

# Transições permitidas entre status de projeto
TRANSICOES_PROJETO = {
    "planejamento": ["em_andamento", "cancelado"],
    "em_andamento": ["em_revisao", "pausado", "concluido", "cancelado"],
    "em_revisao": ["em_andamento", "concluido"],
    "pausado": ["em_andamento", "cancelado"],
    "concluido": [],  # Status final
    "cancelado": [],  # Status final
}

# Transições permitidas entre status de tarefa
TRANSICOES_TAREFA = {
    "a_fazer": ["em_andamento", "bloqueada"],
    "em_andamento": ["em_revisao", "a_fazer", "bloqueada", "concluida"],
    "em_revisao": ["em_andamento", "concluida"],
    "concluida": ["em_andamento"],  # Pode reabrir
    "bloqueada": ["a_fazer", "em_andamento"],
}


def pode_transicionar_projeto(status_atual: str, novo_status: str) -> bool:
    """
    Verifica se a transição de status é permitida para projetos.
    
    Args:
        status_atual: Status atual do projeto
        novo_status: Status desejado
        
    Returns:
        True se transição é permitida
    """
    transicoes = TRANSICOES_PROJETO.get(status_atual, [])
    return novo_status in transicoes


def pode_transicionar_tarefa(status_atual: str, novo_status: str) -> bool:
    """
    Verifica se a transição de status é permitida para tarefas.
    
    Args:
        status_atual: Status atual da tarefa
        novo_status: Status desejado
        
    Returns:
        True se transição é permitida
    """
    transicoes = TRANSICOES_TAREFA.get(status_atual, [])
    return novo_status in transicoes


def obter_proximos_status_projeto(status_atual: str) -> List[str]:
    """Retorna lista de status possíveis a partir do atual"""
    return TRANSICOES_PROJETO.get(status_atual, [])


def obter_proximos_status_tarefa(status_atual: str) -> List[str]:
    """Retorna lista de status possíveis a partir do atual"""
    return TRANSICOES_TAREFA.get(status_atual, [])


def obter_cor_status(status: str) -> Dict:
    """Retorna configuração de cor para o status"""
    return STATUS_CORES.get(status, {"cor": "#6B7280", "bg": "#F3F4F6", "label": status})


def obter_cor_prioridade(prioridade: str) -> Dict:
    """Retorna configuração de cor para a prioridade"""
    return PRIORIDADE_CORES.get(prioridade, PRIORIDADE_CORES["media"])


def calcular_progresso_automatico(tarefas: List[Dict]) -> float:
    """
    Calcula progresso do projeto baseado nas tarefas.
    
    Args:
        tarefas: Lista de dicionários com dados das tarefas
        
    Returns:
        Percentual de progresso (0-100)
    """
    if not tarefas:
        return 0.0
    
    total = len(tarefas)
    concluidas = sum(1 for t in tarefas if t.get('status') == 'concluida')
    
    return round((concluidas / total) * 100, 2)


def determinar_status_projeto_automatico(tarefas: List[Dict], data_fim_prevista: Optional[date] = None) -> str:
    """
    Determina o status do projeto baseado nas tarefas e prazo.
    
    Args:
        tarefas: Lista de tarefas do projeto
        data_fim_prevista: Data prevista de conclusão
        
    Returns:
        Status sugerido para o projeto
    """
    if not tarefas:
        return "planejamento"
    
    total = len(tarefas)
    concluidas = sum(1 for t in tarefas if t.get('status') == 'concluida')
    em_andamento = sum(1 for t in tarefas if t.get('status') == 'em_andamento')
    bloqueadas = sum(1 for t in tarefas if t.get('status') == 'bloqueada')
    
    # Todas concluídas
    if concluidas == total:
        return "concluido"
    
    # Muitas bloqueadas pode indicar revisão necessária
    if bloqueadas > total * 0.3:
        return "em_revisao"
    
    # Há tarefas em andamento
    if em_andamento > 0 or concluidas > 0:
        return "em_andamento"
    
    return "planejamento"


def verificar_atraso_tarefa(data_fim_prevista: Optional[date]) -> Dict:
    """
    Verifica se tarefa está atrasada.
    
    Args:
        data_fim_prevista: Data prevista de conclusão
        
    Returns:
        Dict com informações de atraso
    """
    if not data_fim_prevista:
        return {"atrasada": False, "dias_atraso": 0}
    
    hoje = date.today()
    
    if isinstance(data_fim_prevista, str):
        data_fim_prevista = datetime.strptime(data_fim_prevista, "%Y-%m-%d").date()
    
    if hoje > data_fim_prevista:
        dias = (hoje - data_fim_prevista).days
        return {"atrasada": True, "dias_atraso": dias}
    
    return {"atrasada": False, "dias_atraso": 0}


def obter_todos_status() -> Dict:
    """Retorna todos os status disponíveis com suas configurações"""
    return {
        "projetos": {s.value: obter_cor_status(s.value) for s in StatusProjeto},
        "tarefas": {s.value: obter_cor_status(s.value) for s in StatusTarefa},
        "prioridades": PRIORIDADE_CORES,
        "transicoes_projeto": TRANSICOES_PROJETO,
        "transicoes_tarefa": TRANSICOES_TAREFA,
    }
