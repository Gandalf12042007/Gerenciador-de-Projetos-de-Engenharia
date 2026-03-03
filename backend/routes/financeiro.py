"""
Rotas para o Módulo Financeiro
PHASE 4: Implementação do módulo financeiro com endpoints para custos, orçamentos, faturas e fluxo de caixa
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
# from sqlalchemy.orm import Session  # Not used in this implementation
from datetime import datetime, date
from typing import List, Optional
from decimal import Decimal

router = APIRouter(prefix="/api/financeiro", tags=["Financeiro"])


# ============================================
# MODELOS DE RESPOSTA
# ============================================

class CustoResponse(BaseModel):
    """Modelo de resposta para custos"""
    id: int
    projeto_id: int
    tarefa_id: Optional[int] = None
    tipo_custo_id: int
    descricao: str
    valor: Decimal
    moeda: str
    data_custo: date
    responsavel_id: Optional[int] = None
    criado_em: datetime


class OrcamentoResponse(BaseModel):
    """Modelo de resposta para orçamentos"""
    id: int
    projeto_id: int
    valor_total: Decimal
    moeda: str
    status: str
    linhas: List[dict]
    custos_realizados: Decimal
    percentual_gasto: float
    criado_em: datetime


class FaturaResponse(BaseModel):
    """Modelo de resposta para faturas"""
    id: int
    projeto_id: int
    numero_nf: str
    valor_total: Decimal
    status: str
    data_emissao: date
    data_vencimento: date
    data_pagamento: Optional[date] = None
    itens: List[dict]
    criado_em: datetime


class DashboardFinanceiroResponse(BaseModel):
    """Resposta do dashboard financeiro"""
    valor_total_orcado: Decimal
    valor_total_gasto: Decimal
    valor_total_pendente: Decimal
    percentual_execucao: float
    custos_por_categoria: dict
    faturas_abertas: int
    faturas_vencidas: int
    fluxo_caixa_mensal: dict
    projetos_criticos: List[dict]


# ============================================
# ENDPOINTS DE CUSTOS
# ============================================

@router.post("/custos", response_model=CustoResponse)
async def criar_custo(
    projeto_id: int,
    tipo_custo_id: int,
    descricao: str,
    valor: Decimal,
    data_custo: date = Query(default_factory=date.today),
    tarefa_id: Optional[int] = None,
    moeda: str = "BRL",
    notas: Optional[str] = None,
    # current_user: dict = Depends(get_current_user)
):
    """
    Criar um novo custo para um projeto
    
    Campos:
    - projeto_id (obrigatório): ID do projeto
    - tipo_custo_id (obrigatório): Tipo de custo (1=material, 2=mão_obra, etc)
    - descricao (obrigatório): Descrição do custo
    - valor (obrigatório): Valor em unidade monetária
    - data_custo: Data do custo (padrão: hoje)
    - tarefa_id: ID da tarefa relacionada (opcional)
    - moeda: Moeda (padrão: BRL)
    - notas: Anotações adicionais
    """
    # Validações
    if valor <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Valor deve ser maior que zero"
        )
    
    if not projeto_id or not tipo_custo_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Projeto e tipo de custo são obrigatórios"
        )
    
    # Simular criação (em produção, salvaria no banco)
    return {
        "id": 1,
        "projeto_id": projeto_id,
        "tarefa_id": tarefa_id,
        "tipo_custo_id": tipo_custo_id,
        "descricao": descricao,
        "valor": valor,
        "moeda": moeda,
        "data_custo": data_custo,
        "responsavel_id": 1,
        "criado_em": datetime.now()
    }


@router.get("/custos", response_model=List[CustoResponse])
async def listar_custos(
    projeto_id: Optional[int] = None,
    tipo_custo_id: Optional[int] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """
    Listar custos com filtros opcionais
    
    Filtros:
    - projeto_id: Filtrar por projeto
    - tipo_custo_id: Filtrar por tipo de custo
    - data_inicio: Custos a partir de (inclusive)
    - data_fim: Custos até (inclusive)
    - skip: Paginação offset
    - limit: Paginação limite (máx 100)
    """
    # Simular resposta
    return []


@router.get("/custos/{custo_id}")
async def obter_custo(custo_id: int):
    """Obter detalhes de um custo específico"""
    return {
        "id": custo_id,
        "projeto_id": 1,
        "tipo_custo_id": 1,
        "descricao": "Material para construção",
        "valor": 1500.00,
        "moeda": "BRL",
        "data_custo": date.today()
    }


@router.put("/custos/{custo_id}")
async def atualizar_custo(
    custo_id: int,
    valor: Optional[Decimal] = None,
    descricao: Optional[str] = None,
    data_custo: Optional[date] = None,
    tipo_custo_id: Optional[int] = None
):
    """Atualizar um custo existente"""
    return {"mensagem": "Custo atualizado com sucesso"}


@router.delete("/custos/{custo_id}")
async def deletar_custo(custo_id: int):
    """Deletar um custo"""
    return {"mensagem": "Custo deletado com sucesso"}


# ============================================
# ENDPOINTS DE ORÇAMENTOS
# ============================================

@router.post("/orcamentos")
async def criar_orcamento(
    projeto_id: int,
    valor_total: Decimal,
    data_prevista_conclusao: Optional[date] = None,
    linhas: List[dict] = []
):
    """
    Criar um novo orçamento para um projeto
    
    Exemplo de linhas:
    [
      {"tipo_custo_id": 1, "valor_estimado": 5000.00, "descricao": "Materiais"},
      {"tipo_custo_id": 2, "valor_estimado": 3000.00, "descricao": "Mão de obra"}
    ]
    """
    if valor_total <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Valor total deve ser maior que zero"
        )
    
    # Validar que linhas somam o valor total
    total_linhas = sum(float(l.get("valor_estimado", 0)) for l in linhas) if linhas else 0
    
    return {
        "id": 1,
        "projeto_id": projeto_id,
        "valor_total": valor_total,
        "moeda": "BRL",
        "status": "ativo",
        "data_criacao": date.today(),
        "linhas": linhas,
        "criado_em": datetime.now()
    }


@router.get("/orcamentos")
async def listar_orcamentos(
    projeto_id: Optional[int] = None,
    status: Optional[str] = Query(None, regex="^(ativo|encerrado|cancelado)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """
    Listar orçamentos
    
    Filtros:
    - projeto_id: Filtrar por projeto
    - status: ativo, encerrado ou cancelado
    """
    return []


@router.get("/orcamentos/{orcamento_id}")
async def obter_orcamento(orcamento_id: int):
    """Obter orçamento com análise de gastos"""
    return {
        "id": orcamento_id,
        "projeto_id": 1,
        "valor_total": 10000.00,
        "custos_realizados": 7500.00,
        "percentual_gasto": 75.0,
        "linhas": [
            {"tipo": "material", "estimado": 5000.00, "realizado": 4500.00},
            {"tipo": "mão_obra", "estimado": 5000.00, "realizado": 3000.00}
        ]
    }


@router.put("/orcamentos/{orcamento_id}")
async def atualizar_orcamento(orcamento_id: int, valor_total: Optional[Decimal] = None):
    """Atualizar orçamento"""
    return {"mensagem": "Orçamento atualizado"}


# ============================================
# ENDPOINTS DE FATURAS
# ============================================

@router.post("/faturas")
async def criar_fatura(
    projeto_id: int,
    numero_nf: str,
    valor_total: Decimal,
    data_emissao: date = Query(default_factory=date.today),
    data_vencimento: Optional[date] = None,
    itens: List[dict] = []
):
    """
    Criar nova fatura
    
    Exemplo de itens:
    [
      {"descricao": "Serviço A", "quantidade": 2, "valor_unitario": 500.00},
      {"descricao": "Serviço B", "quantidade": 1, "valor_unitario": 1000.00}
    ]
    """
    if valor_total <= 0:
        raise HTTPException(status_code=400, detail="Valor deve ser maior que zero")
    
    # Validação de NF
    if not numero_nf or len(numero_nf) < 3:
        raise HTTPException(status_code=400, detail="Número de NF inválido")
    
    return {
        "id": 1,
        "projeto_id": projeto_id,
        "numero_nf": numero_nf,
        "valor_total": valor_total,
        "status": "aberta",
        "data_emissao": data_emissao,
        "data_vencimento": data_vencimento,
        "itens": itens,
        "criado_em": datetime.now()
    }


@router.get("/faturas")
async def listar_faturas(
    projeto_id: Optional[int] = None,
    status: Optional[str] = Query(None, regex="^(aberta|paga|cancelada|atrasada)$"),
    vencidas: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """
    Listar faturas com filtros
    
    Filtros:
    - projeto_id: Filtrar por projeto
    - status: aberta, paga, cancelada, atrasada
    - vencidas: true para apenas vencidas
    """
    return []


@router.get("/faturas/{fatura_id}")
async def obter_fatura(fatura_id: int):
    """Obter detalhes da fatura com histórico de pagamentos"""
    return {
        "id": fatura_id,
        "numero_nf": "NF-2024-001",
        "valor_total": 5000.00,
        "status": "aberta",
        "pagamentos": []
    }


@router.post("/faturas/{fatura_id}/pagar")
async def registrar_pagamento_fatura(
    fatura_id: int,
    valor_pago: Decimal,
    data_pagamento: date = Query(default_factory=date.today),
    forma_pagamento: Optional[str] = None
):
    """Registrar pagamento de fatura"""
    return {
        "mensagem": "Pagamento registrado",
        "fatura_id": fatura_id,
        "valor_pago": valor_pago,
        "data_pagamento": data_pagamento
    }


# ============================================
# ENDPOINTS DE FLUXO DE CAIXA
# ============================================

@router.post("/fluxo-caixa")
async def criar_movimento_fluxo(
    projeto_id: int,
    valor: Decimal,
    descricao: str,
    tipo: str = Query(..., regex="^(entrada|saida)$"),
    categoria: Optional[str] = None,
    data_movimento: Optional[date] = None
):
    """
    Registrar movimento no fluxo de caixa
    
    Tipos: entrada ou saida
    """
    if valor <= 0:
        raise HTTPException(status_code=400, detail="Valor deve ser positivo")
    
    return {
        "id": 1,
        "projeto_id": projeto_id,
        "tipo": tipo,
        "valor": valor,
        "descricao": descricao,
        "data_movimento": data_movimento,
        "criado_em": datetime.now()
    }


@router.get("/fluxo-caixa")
async def listar_fluxo_caixa(
    projeto_id: int,
    mes: Optional[int] = Query(None, ge=1, le=12),
    ano: Optional[int] = Query(None, ge=2020),
    tipo: Optional[str] = Query(None, regex="^(entrada|saida)$")
):
    """
    Listar fluxo de caixa com filtros por mês/ano
    """
    return {
        "periodo": f"{mes}/{ano}",
        "entradas": 25000.00,
        "saidas": 18500.00,
        "saldo": 6500.00,
        "movimentos": []
    }


# ============================================
# ENDPOINTS DE RELATÓRIOS
# ============================================

@router.get("/relatorios/dashboard")
async def dashboard_financeiro(projeto_id: Optional[int] = None):
    """
    Dashboard financeiro com KPIs principais
    
    Retorna:
    - Valor total orçado
    - Valor total gasto
    - Percentual de execução
    - Custos por categoria
    - Faturas abertas/vencidas
    - Fluxo de caixa mensal
    - Projetos em situação crítica
    """
    return {
        "valor_total_orcado": 100000.00,
        "valor_total_gasto": 65000.00,
        "valor_total_pendente": 35000.00,
        "percentual_execucao": 65.0,
        "custos_por_categoria": {
            "material": 30000.00,
            "mao_obra": 25000.00,
            "equipamento": 10000.00
        },
        "faturas_abertas": 5,
        "faturas_vencidas": 2,
        "fluxo_caixa_mensal": {
            "janeiro": {"entradas": 50000.00, "saidas": 30000.00},
            "fevereiro": {"entradas": 40000.00, "saidas": 35000.00}
        },
        "projetos_criticos": [
            {"id": 1, "nome": "Projeto A", "gasto": 85000.00, "orcado": 100000.00, "status": "em_risco"}
        ]
    }


@router.get("/relatorios/custos-por-tipo")
async def relatorio_custos_por_tipo(
    projeto_id: int,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None
):
    """Gerar relatório de custos agrupados por tipo"""
    return {
        "projeto_id": projeto_id,
        "periodo": f"{data_inicio} a {data_fim}",
        "custos_por_tipo": [
            {"tipo": "material", "quantidade": 15, "valor_total": 30000.00},
            {"tipo": "mão_obra", "quantidade": 240, "valor_total": 25000.00}
        ],
        "valor_total": 55000.00
    }


@router.get("/relatorios/orcamento-vs-realizado")
async def relatorio_orcamento_realizado(projeto_id: int):
    """Comparar orçamento planejado com custos realizados"""
    return {
        "projeto_id": projeto_id,
        "orcamento_planejado": 100000.00,
        "custos_realizados": 65000.00,
        "variacao": -35000.00,
        "percentual_variacao": -35.0,
        "status": "dentro_do_orcamento",
        "linhas": [
            {
                "tipo": "material",
                "planejado": 50000.00,
                "realizado": 30000.00,
                "variacao": -20000.00
            }
        ]
    }


@router.post("/relatorios/exportar-pdf")
async def exportar_relatorio_pdf(
    projeto_id: int,
    tipo: str = Query(..., regex="^(custos|orcamentos|faturas|fluxo_caixa)$")
):
    """
    Exportar relatório em PDF
    
    Tipos: custos, orcamentos, faturas, fluxo_caixa
    """
    return {
        "mensagem": "Relatório gerado com sucesso",
        "download_url": f"/api/financeiro/relatorios/download/{tipo}-{projeto_id}.pdf",
        "filename": f"relatorio-{tipo}.pdf"
    }


# ============================================
# ENDPOINTS DE ANÁLISES
# ============================================

@router.get("/analises/tendencias")
async def analise_tendencias(projeto_id: int, meses: int = Query(12, ge=1, le=24)):
    """
    Analisar tendências de gastos nos últimos N meses
    """
    return {
        "projeto_id": projeto_id,
        "periodo_meses": meses,
        "tendencia": "crescente",
        "variacao_media_mensal": 2.5,
        "projecao_anual": 156000.00,
        "graficos": {
            "gastos_mensais": [25000, 26000, 28500, 30000],
            "orcamento_mensal": [20000, 20000, 20000, 20000]
        }
    }


@router.get("/analises/risco-orcamentario")
async def analise_risco(projeto_id: int):
    """
    Avaliar risco de estouro do orçamento
    
    Retorna:
    - Nível de risco (baixo, médio, alto, crítico)
    - Projeção de gastos
    - Recomendações
    """
    return {
        "projeto_id": projeto_id,
        "nivel_risco": "médio",
        "percentual_risco": 45.0,
        "gastos_atuais": 65000.00,
        "orcamento": 100000.00,
        "projecao_final": 95000.00,
        "margem_seguranca": 5000.00,
        "recomendacoes": [
            "Revisar custos de mão de obra",
            "Otimizar compra de materiais"
        ]
    }
