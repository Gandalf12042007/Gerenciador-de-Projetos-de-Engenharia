// Materials JS - CRUD de materiais
let materials = [];
let projectId = null;

function getProjectIdFromUrlOrStorage() {
  const params = new URLSearchParams(window.location.search);
  let pid = params.get('project');
  if (!pid) pid = localStorage.getItem('current_project_id');
  return pid || null;
}

async function loadMaterials() {
  if (!projectId) return;
  
  const categoria = document.getElementById('filterCategoria').value;
  
  try {
    const response = await API.Materiais.listarPorProjeto(projectId, categoria);
    const data = response.data || response;
    
    materials = data.materiais || [];
    
    // Atualizar sumário
    document.getElementById('totalMateriais').textContent = data.total_materiais || materials.length;
    document.getElementById('valorEstoque').textContent = formatMoney(data.total_estoque || 0);
    document.getElementById('valorUsado').textContent = formatMoney(data.total_usado || 0);
    
    renderMaterials();
  } catch (error) {
    console.error('Erro ao carregar materiais:', error);
    materials = [];
    renderMaterials();
  }
}

function formatMoney(value) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
}

function renderMaterials() {
  const tbody = document.getElementById('materialsTableBody');
  const emptyState = document.getElementById('emptyState');
  const searchTerm = document.getElementById('searchMaterial').value.toLowerCase();
  
  let filtered = materials;
  if (searchTerm) {
    filtered = materials.filter(m => 
      m.nome.toLowerCase().includes(searchTerm) || 
      (m.fornecedor && m.fornecedor.toLowerCase().includes(searchTerm))
    );
  }
  
  if (filtered.length === 0) {
    tbody.innerHTML = '';
    emptyState.style.display = 'block';
    document.querySelector('.materials-table').style.display = 'none';
    return;
  }
  
  emptyState.style.display = 'none';
  document.querySelector('.materials-table').style.display = 'block';
  
  tbody.innerHTML = filtered.map(m => `
    <tr>
      <td><strong>${escapeHtml(m.nome)}</strong></td>
      <td><span class="categoria-badge cat-${m.categoria}">${m.categoria}</span></td>
      <td>${m.unidade}</td>
      <td>${formatMoney(m.preco_unitario)}</td>
      <td>${m.quantidade_estoque || 0}</td>
      <td>${m.quantidade_usada || 0}</td>
      <td>${escapeHtml(m.fornecedor || '-')}</td>
      <td class="actions">
        <button class="btn-sm btn-stock" onclick="openStockModal(${m.id}, '${escapeHtml(m.nome)}')">📦</button>
        <button class="btn-sm btn-edit" onclick="editMaterial(${m.id})">✏️</button>
        <button class="btn-sm btn-delete" onclick="deleteMaterial(${m.id})">🗑️</button>
      </td>
    </tr>
  `).join('');
}

function escapeHtml(s) {
  return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// Modal Material
function openMaterialModal(title, material = null) {
  document.getElementById('modalMaterialTitle').textContent = title;
  document.getElementById('materialModal').style.display = 'flex';
  document.getElementById('materialId').value = material ? material.id : '';
  document.getElementById('materialNome').value = material ? material.nome : '';
  document.getElementById('materialCategoria').value = material ? material.categoria : 'cimento';
  document.getElementById('materialUnidade').value = material ? material.unidade : 'un';
  document.getElementById('materialPreco').value = material ? material.preco_unitario : '';
  document.getElementById('materialFornecedor').value = material ? (material.fornecedor || '') : '';
  document.getElementById('materialDescricao').value = material ? (material.descricao || '') : '';
}

function closeMaterialModal() {
  document.getElementById('materialModal').style.display = 'none';
}

// Modal Estoque
function openStockModal(materialId, materialName) {
  document.getElementById('stockModal').style.display = 'flex';
  document.getElementById('stockMaterialId').value = materialId;
  document.getElementById('stockMaterialName').textContent = materialName;
  document.getElementById('stockQuantidade').value = '';
  document.getElementById('stockOperacao').value = 'entrada';
}

function closeStockModal() {
  document.getElementById('stockModal').style.display = 'none';
}

async function editMaterial(id) {
  const material = materials.find(m => m.id === id);
  if (!material) return;
  openMaterialModal('Editar Material', material);
}

async function deleteMaterial(id) {
  if (!confirm('Tem certeza que deseja excluir este material?')) return;
  
  try {
    await API.Materiais.deletar(id);
    await loadMaterials();
  } catch (error) {
    alert('Erro ao excluir material: ' + error.message);
  }
}

async function saveMaterialHandler(e) {
  e.preventDefault();
  
  const id = document.getElementById('materialId').value;
  const data = {
    nome: document.getElementById('materialNome').value,
    categoria: document.getElementById('materialCategoria').value,
    unidade: document.getElementById('materialUnidade').value,
    preco_unitario: parseFloat(document.getElementById('materialPreco').value),
    fornecedor: document.getElementById('materialFornecedor').value || null,
    descricao: document.getElementById('materialDescricao').value || null
  };
  
  try {
    if (id) {
      await API.Materiais.atualizar(id, data);
    } else {
      await API.Materiais.criar(projectId, data);
    }
    closeMaterialModal();
    await loadMaterials();
  } catch (error) {
    alert('Erro ao salvar material: ' + error.message);
  }
}

async function updateStockHandler(e) {
  e.preventDefault();
  
  const materialId = document.getElementById('stockMaterialId').value;
  const quantidade = parseFloat(document.getElementById('stockQuantidade').value);
  const operacao = document.getElementById('stockOperacao').value;
  
  try {
    // Atualizar via API
    const material = materials.find(m => m.id == materialId);
    if (!material) return;
    
    let novoEstoque = material.quantidade_estoque || 0;
    let novoUsado = material.quantidade_usada || 0;
    
    if (operacao === 'entrada') {
      novoEstoque += quantidade;
    } else {
      novoEstoque -= quantidade;
      novoUsado += quantidade;
    }
    
    await API.Materiais.atualizar(materialId, {
      quantidade_estoque: novoEstoque,
      quantidade_usada: novoUsado
    });
    
    closeStockModal();
    await loadMaterials();
  } catch (error) {
    alert('Erro ao atualizar estoque: ' + error.message);
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
  document.getElementById('addMaterialBtn').onclick = () => openMaterialModal('Novo Material');
  document.getElementById('closeMaterialModal').onclick = closeMaterialModal;
  document.getElementById('closeStockModal').onclick = closeStockModal;
  
  // Fechar modal ao clicar fora
  document.getElementById('materialModal').onclick = (e) => {
    if (e.target === e.currentTarget) closeMaterialModal();
  };
  document.getElementById('stockModal').onclick = (e) => {
    if (e.target === e.currentTarget) closeStockModal();
  };
  
  // Forms
  document.getElementById('materialForm').onsubmit = saveMaterialHandler;
  document.getElementById('stockForm').onsubmit = updateStockHandler;
  
  // Filtros
  document.getElementById('filterCategoria').onchange = loadMaterials;
  document.getElementById('searchMaterial').oninput = renderMaterials;
  
  // Carregar dados
  loadMaterials();
});
