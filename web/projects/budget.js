// Budget JS - CRUD de orçamentos
let budgetItems = [];
let projectId = null;

function getProjectIdFromUrlOrStorage() {
  const params = new URLSearchParams(window.location.search);
  // Aceita 'project' ou 'projeto' na URL
  let pid = params.get('project') || params.get('projeto');
  if (!pid) pid = localStorage.getItem('current_project_id');
  // Fallback: extrair de projeto_atual
  if (!pid) {
    try {
      const projetoAtual = JSON.parse(localStorage.getItem('projeto_atual') || '{}');
      pid = projetoAtual.id;
    } catch (e) { /* ignore */ }
  }
  return pid || null;
}

async function loadBudget() {
  if (!projectId) return;
  
  const categoria = document.getElementById('filterCategoria').value;
  const status = document.getElementById('filterStatus').value;
  
  try {
    const response = await API.Orcamentos.listarPorProjeto(projectId, categoria, status);
    const data = response.data || response;
    
    budgetItems = data.orcamentos || [];
    
    // Atualizar sumário
    const totalPrevisto = data.total_previsto || 0;
    const totalGasto = data.total_gasto || 0;
    const saldo = totalPrevisto - totalGasto;
    const percentGasto = totalPrevisto > 0 ? (totalGasto / totalPrevisto) * 100 : 0;
    const atrasados = budgetItems.filter(b => b.status_calculado === 'atrasado').length;
    
    document.getElementById('totalPrevisto').textContent = formatMoney(totalPrevisto);
    document.getElementById('totalGasto').textContent = formatMoney(totalGasto);
    document.getElementById('saldoDisponivel').textContent = formatMoney(saldo);
    document.getElementById('itensAtrasados').textContent = atrasados;
    
    // Atualizar barra de progresso
    const progressFill = document.getElementById('progressFill');
    progressFill.style.width = Math.min(percentGasto, 100) + '%';
    if (percentGasto > 100) {
      progressFill.classList.add('over-budget');
    } else {
      progressFill.classList.remove('over-budget');
    }
    
    // Atualizar classe do saldo
    const saldoEl = document.getElementById('saldoDisponivel');
    saldoEl.className = 'value ' + (saldo >= 0 ? 'positive' : 'negative');
    
    renderBudget();
  } catch (error) {
    console.error('Erro ao carregar orçamento:', error);
    budgetItems = [];
    renderBudget();
  }
}

function formatMoney(value) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
}

function formatDate(dateStr) {
  if (!dateStr) return '-';
  const date = new Date(dateStr);
  return date.toLocaleDateString('pt-BR');
}

function getCategoriaLabel(cat) {
  const labels = {
    'mao_de_obra': 'Mão de Obra',
    'materiais': 'Materiais',
    'equipamentos': 'Equipamentos',
    'servicos': 'Serviços',
    'impostos': 'Impostos',
    'outros': 'Outros'
  };
  return labels[cat] || cat;
}

function renderBudget() {
  const tbody = document.getElementById('budgetTableBody');
  const emptyState = document.getElementById('emptyState');
  
  if (budgetItems.length === 0) {
    tbody.innerHTML = '';
    emptyState.style.display = 'block';
    document.querySelector('.budget-table').style.display = 'none';
    return;
  }
  
  emptyState.style.display = 'none';
  document.querySelector('.budget-table').style.display = 'block';
  
  tbody.innerHTML = budgetItems.map(b => {
    const diferenca = b.valor_previsto - b.valor_gasto;
    const diferencaClass = diferenca >= 0 ? 'positive' : 'negative';
    const status = b.status_calculado || b.status || 'previsto';
    
    return `
    <tr>
      <td><strong>${escapeHtml(b.descricao)}</strong></td>
      <td><span class="categoria-badge cat-${b.categoria}">${getCategoriaLabel(b.categoria)}</span></td>
      <td>${formatMoney(b.valor_previsto)}</td>
      <td>${formatMoney(b.valor_gasto || 0)}</td>
      <td class="${diferencaClass}">${formatMoney(diferenca)}</td>
      <td>${formatDate(b.data_prevista)}</td>
      <td><span class="status-badge status-${status}">${status}</span></td>
      <td class="actions">
        <button class="btn-sm btn-pay" onclick="markAsPaid(${b.id})" title="Marcar como pago">💵</button>
        <button class="btn-sm btn-edit" onclick="editBudgetItem(${b.id})">✏️</button>
        <button class="btn-sm btn-delete" onclick="deleteBudgetItem(${b.id})">🗑️</button>
      </td>
    </tr>
  `}).join('');
}

function escapeHtml(s) {
  return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// Modal
function openBudgetModal(title, item = null) {
  document.getElementById('modalBudgetTitle').textContent = title;
  document.getElementById('budgetModal').style.display = 'flex';
  document.getElementById('budgetId').value = item ? item.id : '';
  document.getElementById('budgetDescricao').value = item ? item.descricao : '';
  document.getElementById('budgetCategoria').value = item ? item.categoria : 'materiais';
  document.getElementById('budgetValorPrevisto').value = item ? item.valor_previsto : '';
  document.getElementById('budgetValorGasto').value = item ? (item.valor_gasto || '') : '';
  document.getElementById('budgetDataPrevista').value = item && item.data_prevista ? item.data_prevista.split('T')[0] : '';
  document.getElementById('budgetDataPagamento').value = item && item.data_pagamento ? item.data_pagamento.split('T')[0] : '';
}

function closeBudgetModal() {
  document.getElementById('budgetModal').style.display = 'none';
}

async function editBudgetItem(id) {
  const item = budgetItems.find(b => b.id === id);
  if (!item) return;
  openBudgetModal('Editar Item', item);
}

async function deleteBudgetItem(id) {
  if (!confirm('Tem certeza que deseja excluir este item?')) return;
  
  try {
    await API.Orcamentos.deletar(id);
    await loadBudget();
  } catch (error) {
    alert('Erro ao excluir item: ' + error.message);
  }
}

async function markAsPaid(id) {
  const item = budgetItems.find(b => b.id === id);
  if (!item) return;
  
  const valorGasto = prompt('Valor gasto (R$):', item.valor_previsto);
  if (valorGasto === null) return;
  
  try {
    await API.Orcamentos.atualizar(id, {
      valor_gasto: parseFloat(valorGasto),
      data_pagamento: new Date().toISOString().split('T')[0],
      status: 'pago'
    });
    await loadBudget();
  } catch (error) {
    alert('Erro ao atualizar pagamento: ' + error.message);
  }
}

async function saveBudgetHandler(e) {
  e.preventDefault();
  
  const id = document.getElementById('budgetId').value;
  const data = {
    descricao: document.getElementById('budgetDescricao').value,
    categoria: document.getElementById('budgetCategoria').value,
    valor_previsto: parseFloat(document.getElementById('budgetValorPrevisto').value),
    valor_gasto: parseFloat(document.getElementById('budgetValorGasto').value) || 0,
    data_prevista: document.getElementById('budgetDataPrevista').value || null,
    data_pagamento: document.getElementById('budgetDataPagamento').value || null
  };
  
  try {
    if (id) {
      await API.Orcamentos.atualizar(id, data);
    } else {
      await API.Orcamentos.criar(projectId, data);
    }
    closeBudgetModal();
    await loadBudget();
  } catch (error) {
    alert('Erro ao salvar item: ' + error.message);
  }
}

// Events
document.addEventListener('DOMContentLoaded', () => {
  projectId = getProjectIdFromUrlOrStorage();
  if (!projectId) {
    localStorage.removeItem('current_project_id');
    alert('Selecione um projeto na tela inicial para acessar o sistema.');
    window.location.href = '../index.html';
    return;
  }
  localStorage.setItem('current_project_id', projectId);
  
  // Verificar autenticação
  if (!API.Auth.isAuthenticated()) {
    window.location.href = '../login.html';
    return;
  }
  
  // Botões
  document.getElementById('addBudgetBtn').onclick = () => openBudgetModal('Novo Item');
  document.getElementById('closeBudgetModal').onclick = closeBudgetModal;
  
  // Fechar modal ao clicar fora
  document.getElementById('budgetModal').onclick = (e) => {
    if (e.target === e.currentTarget) closeBudgetModal();
  };
  
  // Form
  document.getElementById('budgetForm').onsubmit = saveBudgetHandler;
  
  // Filtros
  document.getElementById('filterCategoria').onchange = loadBudget;
  document.getElementById('filterStatus').onchange = loadBudget;
  
  // Carregar dados
  loadBudget();
});
