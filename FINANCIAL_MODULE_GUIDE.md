# 💰 Guia de Desenvolvimento - Módulo Financeiro

**Implementar gestão de custos, orçamentos e relatórios financeiros**

---

## 📋 **Escopo do Módulo Financeiro**

### Funcionalidades Principais:

1. **Gestão de Custos**
   - Registrar custos por projeto
   - Categorizar (material, mão de obra, equipamento, etc)
   - Associar a tarefas/equipes

2. **Orçamento**
   - Criar orçamentos por projeto
   - Comparar realizado vs. orçado
   - Alertas de extrapolação

3. **Relatórios Financeiros**
   - Dashboard financeiro
   - Gráficos de custos
   - Previsões

4. **Faturamento**
   - Gerar faturas
   - Rastrear pagamentos
   - Emissão de recibos

---

## 🗄️ **Passo 1: Schema do Banco de Dados**

### Tabelas necessárias:

```sql
-- Tipos de custos (enumeração)
CREATE TABLE tipos_custo (
  id INTEGER PRIMARY KEY,
  nome TEXT UNIQUE NOT NULL,  -- 'material', 'mão_obra', 'equipamento', etc
  descricao TEXT
);

-- Custos por projeto
CREATE TABLE custos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  projeto_id INTEGER NOT NULL,
  tarefa_id INTEGER,  -- Opcional, pode ser associado a tarefa
  tipo_custo_id INTEGER NOT NULL,
  descricao TEXT NOT NULL,
  valor DECIMAL(10, 2) NOT NULL,
  data_custo DATE NOT NULL,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(projeto_id) REFERENCES projetos(id),
  FOREIGN KEY(tarefa_id) REFERENCES tarefas(id),
  FOREIGN KEY(tipo_custo_id) REFERENCES tipos_custo(id)
);

-- Orçamentos por projeto
CREATE TABLE orcamentos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  projeto_id INTEGER NOT NULL UNIQUE,
  valor_total DECIMAL(10, 2) NOT NULL,
  data_criacao DATE DEFAULT CURRENT_DATE,
  data_prevista_conclusao DATE,
  status TEXT DEFAULT 'ativo',  -- 'ativo', 'finalizado', 'cancelado'
  notas TEXT,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(projeto_id) REFERENCES projetos(id)
);

-- Linhas do orçamento (detalhamento)
CREATE TABLE linhas_orcamento (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  orcamento_id INTEGER NOT NULL,
  tipo_custo_id INTEGER NOT NULL,
  valor_estimado DECIMAL(10, 2) NOT NULL,
  percentual_alocado DECIMAL(5, 2),  -- % do orçamento
  descricao TEXT,
  FOREIGN KEY(orcamento_id) REFERENCES orcamentos(id),
  FOREIGN KEY(tipo_custo_id) REFERENCES tipos_custo(id)
);

-- Faturas
CREATE TABLE faturas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  projeto_id INTEGER NOT NULL,
  numero_nf TEXT UNIQUE,
  data_emissao DATE DEFAULT CURRENT_DATE,
  valor_total DECIMAL(10, 2) NOT NULL,
  status TEXT DEFAULT 'aberta',  -- 'aberta', 'paga', 'vencida', 'cancelada'
  data_vencimento DATE,
  data_pagamento DATE,
  descricao TEXT,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(projeto_id) REFERENCES projetos(id)
);

-- Itens das faturas
CREATE TABLE itens_nf (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nf_id INTEGER NOT NULL,
  descricao TEXT NOT NULL,
  quantidade DECIMAL(10, 2),
  valor_unitario DECIMAL(10, 2) NOT NULL,
  valor_total DECIMAL(10, 2) NOT NULL,
  FOREIGN KEY(nf_id) REFERENCES faturas(id)
);

-- Índices para performance
CREATE INDEX idx_custos_projeto ON custos(projeto_id);
CREATE INDEX idx_custos_tarefa ON custos(tarefa_id);
CREATE INDEX idx_custos_data ON custos(data_custo);
CREATE INDEX idx_faturas_projeto ON faturas(projeto_id);
CREATE INDEX idx_faturas_status ON faturas(status);
```

---

## 🔌 **Passo 2: Rotas da API**

Criar `backend/routes/financeiro.py`:

```python
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from utils.auth import get_current_user

router = APIRouter(prefix="/financeiro", tags=["financeiro"])

# ============ MODELOS ============

class CustoCreate(BaseModel):
    projeto_id: int
    tarefa_id: Optional[int] = None
    tipo_custo_id: int
    descricao: str
    valor: float
    data_custo: str  # "YYYY-MM-DD"

class CustoResponse(CustoCreate):
    id: int
    criado_em: str

class OrcamentoCreate(BaseModel):
    projeto_id: int
    valor_total: float
    data_prevista_conclusao: Optional[str] = None
    notas: Optional[str] = None

class OrcamentoResponse(OrcamentoCreate):
    id: int
    status: str
    data_criacao: str
    custos_atuais: float

class FaturaCreate(BaseModel):
    projeto_id: int
    numero_nf: str
    valor_total: float
    data_vencimento: Optional[str] = None
    descricao: Optional[str] = None

class FaturaResponse(FaturaCreate):
    id: int
    status: str
    data_emissao: str

# ============ CUSTOS ============

@router.post("/custos/")
async def criar_custo(
    custo: CustoCreate,
    usuario_atual = Depends(get_current_user)
):
    """Registrar novo custo"""
    # Verificar se projeto existe e usuário tem acesso
    # Inserir no banco de dados
    # Retornar custo criado com ID
    pass

@router.get("/custos/")
async def listar_custos(
    projeto_id: int,
    tipo_custo_id: Optional[int] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    usuario_atual = Depends(get_current_user)
):
    """Listar custos com filtros"""
    pass

@router.get("/custos/{custo_id}")
async def obter_custo(
    custo_id: int,
    usuario_atual = Depends(get_current_user)
):
    """Obter detalhes de um custo"""
    pass

@router.put("/custos/{custo_id}")
async def atualizar_custo(
    custo_id: int,
    custo: CustoCreate,
    usuario_atual = Depends(get_current_user)
):
    """Atualizar custo existente"""
    pass

@router.delete("/custos/{custo_id}")
async def deletar_custo(
    custo_id: int,
    usuario_atual = Depends(get_current_user)
):
    """Deletar custo"""
    pass

# ============ ORÇAMENTOS ============

@router.post("/orcamentos/")
async def criar_orcamento(
    orcamento: OrcamentoCreate,
    usuario_atual = Depends(get_current_user)
):
    """Criar orçamento para projeto"""
    pass

@router.get("/orcamentos/{projeto_id}")
async def obter_orcamento(
    projeto_id: int,
    usuario_atual = Depends(get_current_user)
):
    """Obter orçamento de um projeto"""
    pass

@router.get("/orcamentos/{projeto_id}/resumo")
async def resumo_financeiro(
    projeto_id: int,
    usuario_atual = Depends(get_current_user)
):
    """Resumo financeiro: orçado vs realizado"""
    # SELECT
    # orcamentos.valor_total as valor_orcado,
    # COALESCE(SUM(custos.valor), 0) as valor_gasto,
    # FROM orcamentos
    # LEFT JOIN custos ON orcamentos.projeto_id = custos.projeto_id
    # WHERE orcamentos.projeto_id = ?
    
    return {
        "projeto_id": projeto_id,
        "valor_orcado": 50000,
        "valor_gasto": 32500,
        "valor_restante": 17500,
        "percentual_gasto": 65,
        "status": "ok",  # OK, AVISO, CRITICO
        "custos_por_tipo": {
            "material": 15000,
            "mao_obra": 15000,
            "equipamento": 2500
        }
    }

@router.put("/orcamentos/{projeto_id}")
async def atualizar_orcamento(
    projeto_id: int,
    orcamento: OrcamentoCreate,
    usuario_atual = Depends(get_current_user)
):
    """Atualizar orçamento"""
    pass

# ============ FATURAS ============

@router.post("/faturas/")
async def criar_fatura(
    fatura: FaturaCreate,
    usuario_atual = Depends(get_current_user)
):
    """Criar nova fatura"""
    pass

@router.get("/faturas/")
async def listar_faturas(
    projeto_id: Optional[int] = None,
    status: Optional[str] = None,
    usuario_atual = Depends(get_current_user)
):
    """Listar faturas com filtros"""
    pass

@router.get("/faturas/{fatura_id}/pdf")
async def baixar_fatura_pdf(
    fatura_id: int,
    usuario_atual = Depends(get_current_user)
):
    """Baixar fatura em PDF"""
    # Gerar PDF usando reportlab ou similar
    pass

@router.patch("/faturas/{fatura_id}/pagar")
async def marcar_fatura_paga(
    fatura_id: int,
    data_pagamento: Optional[str] = None,
    usuario_atual = Depends(get_current_user)
):
    """Marcar fatura como paga"""
    pass

# ============ RELATÓRIOS ============

@router.get("/relatorios/dashboard")
async def dashboard_financeiro(
    data_inicio: str,
    data_fim: str,
    usuario_atual = Depends(get_current_user)
):
    """Dashboard financeiro geral"""
    return {
        "receita_total": 150000,
        "custos_totais": 85000,
        "lucro_bruto": 65000,
        "margem_lucro": 43.3,
        "projetos_em_dia": 8,
        "projetos_atrasados": 2,
        "faturas_pendentes": 5,
        "valor_pendente": 28500
    }

@router.get("/relatorios/projeto/{projeto_id}")
async def relatorio_financeiro_projeto(
    projeto_id: int,
    usuario_atual = Depends(get_current_user)
):
    """Relatório detalhado de um projeto"""
    pass

@router.get("/relatorios/custos/analise")
async def analise_custos(
    data_inicio: str,
    data_fim: str,
    agrupar_por: str = "tipo",  # 'tipo', 'projeto', 'mes'
    usuario_atual = Depends(get_current_user)
):
    """Análise de custos com agrupamento"""
    pass

# ============ TIPOS DE CUSTO ============

@router.get("/tipos-custo/")
async def listar_tipos_custo():
    """Listar tipos de custo disponíveis"""
    return [
        {"id": 1, "nome": "material", "descricao": "Materiais e insumos"},
        {"id": 2, "nome": "mao_obra", "descricao": "Custo de mão de obra"},
        {"id": 3, "nome": "equipamento", "descricao": "Aluguel/compra de equipamentos"},
        {"id": 4, "nome": "transporte", "descricao": "Custos de transporte"},
        {"id": 5, "nome": "outros", "descricao": "Outros custos"}
    ]
```

---

## 🎨 **Passo 3: Frontend - Dashboard Financeiro**

Criar `web-react/src/pages/FinanceiroDashboard.js`:

```javascript
import React, { useEffect, useState } from 'react';
import { useProjetosStore } from '../store/projetosStore';
import api from '../api/apiClient';
import Header from '../components/Header';
import Card from '../components/Card';
import Button from '../components/Button';
import Chart from 'chart.js';
import '../styles/pages/financeiro-dashboard.css';

function FinanceiroDashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [projetos, setProjetos] = useState([]);
  const [filtroMes, setFiltroMes] = useState(new Date().toISOString().slice(0, 7));
  const { token } = useProjetosStore();

  useEffect(() => {
    fetchDashboard();
    fetchProjetos();
  }, [filtroMes]);

  const fetchDashboard = async () => {
    try {
      const [inicio, fim] = obterIntervaloMes(filtroMes);
      const data = await api.financeiro.relatorios.dashboard(inicio, fim, token);
      setDashboard(data);
    } catch (error) {
      console.error('Erro ao carregar dashboard:', error);
    }
  };

  const fetchProjetos = async () => {
    try {
      const data = await api.projetos.listar(token);
      setProjetos(data);
    } catch (error) {
      console.error('Erro ao carregar projetos:', error);
    }
  };

  const obterIntervaloMes = (mes) => {
    const [ano, mês] = mes.split('-');
    const inicio = `${ano}-${mês}-01`;
    const fim = new Date(ano, mês, 0).toISOString().split('T')[0];
    return [inicio, fim];
  };

  if (!dashboard) return <div>Carregando...</div>;

  return (
    <>
      <Header />
      <div className="financeiro-container">
        <h1>Financeiro</h1>

        {/* Filtro de período */}
        <div className="filtro-periodo">
          <input
            type="month"
            value={filtroMes}
            onChange={(e) => setFiltroMes(e.target.value)}
          />
        </div>

        {/* KPIs Principais */}
        <div className="kpi-grid">
          <Card>
            <h3>Receita Total</h3>
            <p className="kpi-valor">R$ {dashboard.receita_total.toLocaleString('pt-BR')}</p>
            <span className="kpi-status positive">↑ 12% vs última semana</span>
          </Card>

          <Card>
            <h3>Custos</h3>
            <p className="kpi-valor">R$ {dashboard.custos_totais.toLocaleString('pt-BR')}</p>
            <span className="kpi-status">↑ 5% vs última semana</span>
          </Card>

          <Card>
            <h3>Lucro</h3>
            <p className="kpi-valor positive">R$ {dashboard.lucro_bruto.toLocaleString('pt-BR')}</p>
            <span className="kpi-margem">{dashboard.margem_lucro}% de margem</span>
          </Card>

          <Card>
            <h3>Faturas Pendentes</h3>
            <p className="kpi-valor warning">{dashboard.faturas_pendentes}</p>
            <p className="kpi-subtexto">R$ {dashboard.valor_pendente.toLocaleString('pt-BR')}</p>
          </Card>
        </div>

        {/* Gráficos */}
        <div className="graficos-grid">
          <Card>
            <h3>Custos por Tipo</h3>
            <canvas id="grafico-custos-tipo"></canvas>
          </Card>

          <Card>
            <h3>Receita vs Custos</h3>
            <canvas id="grafico-receita-custos"></canvas>
          </Card>
        </div>

        {/* Tabela de Projetos */}
        <Card>
          <h3>Status dos Projetos</h3>
          <table className="tabela-financeira">
            <thead>
              <tr>
                <th>Projeto</th>
                <th>Orçado</th>
                <th>Gasto</th>
                <th>Restante</th>
                <th>%Gasto</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {projetos.map(projeto => (
                <tr key={projeto.id}>
                  <td>{projeto.nome}</td>
                  <td>R$ {projeto.valor_orcado}</td>
                  <td>R$ {projeto.valor_gasto}</td>
                  <td>R$ {projeto.valor_restante}</td>
                  <td>
                    <div className="barra-progresso">
                      <div 
                        className={`progresso ${projeto.status}`}
                        style={{ width: `${projeto.percentual_gasto}%` }}
                      />
                    </div>
                  </td>
                  <td>
                    <span className={`badge badge-${projeto.status}`}>
                      {projeto.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>

        {/* Botões de Ação */}
        <div className="acoes">
          <Button variant="primary">+ Novo Custo</Button>
          <Button variant="secondary">Gerar Relatório</Button>
          <Button variant="secondary">Exportar CSV</Button>
        </div>
      </div>
    </>
  );
}

export default FinanceiroDashboard;
```

---

## 📊 **Passo 4: Gráficos com Chart.js**

```javascript
// Exemplo de gráfico de custos por tipo
const ctx = document.getElementById('grafico-custos-tipo').getContext('2d');
const chart = new Chart(ctx, {
  type: 'doughnut',
  data: {
    labels: ['Material', 'Mão de Obra', 'Equipamento', 'Transporte'],
    datasets: [{
      data: [15000, 25000, 8000, 5000],
      backgroundColor: [
        'rgba(56, 189, 248, 1)',
        'rgba(16, 185, 129, 1)',
        'rgba(249, 115, 22, 1)',
        'rgba(239, 68, 68, 1)'
      ]
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { position: 'bottom' }
    }
  }
});
```

---

## 📄 **Passo 5: Geração de Faturas em PDF**

```bash
pip install reportlab
```

```python
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

def gerar_fatura_pdf(fatura_id):
    # Buscar dados da fatura no banco
    fatura = obter_fatura(fatura_id)
    
    # Criar PDF
    doc = SimpleDocTemplate(f"fatura_{fatura_id}.pdf", pagesize=letter)
    elements = []
    
    # Título
    styles = getSampleStyleSheet()
    titulo = Paragraph(f"FATURA #{fatura['numero_nf']}", styles['Heading1'])
    elements.append(titulo)
    elements.append(Spacer(1, 12))
    
    # Dados
    data = [
        ['Campo', 'Valor'],
        ['Data Emissão', fatura['data_emissao']],
        ['Vencimento', fatura['data_vencimento']],
        ['Status', fatura['status']],
        ['Valor Total', f"R$ {fatura['valor_total']:.2f}"],
    ]
    
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t)
    
    # Gerar PDF
    doc.build(elements)
    return f"fatura_{fatura_id}.pdf"
```

---

## 🔔 **Passo 6: Alertas Financeiros**

```python
# backend/utils/alertas_financeiros.py

def verificar_extrapolacao_orcamento(projeto_id):
    """Verificar se projeto está extrapolando orçamento"""
    orcamento = obter_orcamento(projeto_id)
    custos = obter_custos_totais(projeto_id)
    
    percentual_gasto = (custos / orcamento.valor_total) * 100
    
    if percentual_gasto > 100:
        return {
            "tipo": "erro",
            "mensagem": f"Projeto extrapolou orçamento em {percentual_gasto - 100:.1f}%",
            "severidade": "critico"
        }
    elif percentual_gasto > 90:
        return {
            "tipo": "aviso",
            "mensagem": f"Projeto atingiu {percentual_gasto:.1f}% do orçamento",
            "severidade": "aviso"
        }
    
    return None

def verificar_faturas_vencidas():
    """Verificar faturas vencidas"""
    faturas_vencidas = db.execute("""
        SELECT * FROM faturas 
        WHERE status = 'aberta' 
        AND data_vencimento < DATE('now')
    """).fetchall()
    
    return faturas_vencidas
```

---

## 📋 **Checklist - Módulo Financeiro**

- [ ] Tabelas de banco de dados criadas
- [ ] Rotas da API implementadas
- [ ] Autenticação e autorização configurada
- [ ] Dashboard financeiro funcional
- [ ] Gráficos com Chart.js integrados
- [ ] Geração de PDF para faturas
- [ ] Alertas de extrapolação de orçamento
- [ ] Relatórios export para CSV/Excel
- [ ] Testes unitários (pytest)
- [ ] Documentação completa (Swagger)

---

## 💡 **Expansões Futuras**

- Integração com gateway de pagamento (Stripe, PayPal)
- Emissão de recibos eletrônicos (NFe)
- Previsões com ML (Machine Learning)
- Análise de lucratividade por cliente
- Comparação com projetos similares históricos
- APIs de sincronização com contabilidade (ERP)

---

**O módulo financeiro é essencial para profissionalizar a plataforma! 💰**
