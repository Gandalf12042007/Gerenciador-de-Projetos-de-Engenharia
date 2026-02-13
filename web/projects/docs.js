// Documentos - JS CRUD
let docs = [];
let projectId = null;

function getProjectIdFromUrlOrStorage() {
  const params = new URLSearchParams(window.location.search);
  let pid = params.get('project');
  if (!pid) pid = localStorage.getItem('current_project_id');
  return pid || null;
}

async function loadDocs() {
  if (!projectId) return;
  try {
    const response = await API.Documentos.listar(projectId);
    // O backend retorna { success: true, total: N, documentos: [...] }
    const docsData = response.documentos || response.data || response || [];
    docs = docsData.map(d => ({
      id: d.id,
      nome: d.nome || d.nome_original,
      categoria: d.categoria || d.tipo || 'geral',
      versao: d.versao || '1.0',
      criado_por: d.uploaded_por_nome || d.criado_por_nome || d.usuario_nome || 'N/A',
      data: d.criado_em || d.data_criacao || d.created_at || '',
      url: d.caminho_arquivo || d.url || '',
      tamanho: d.tamanho_bytes || 0
    }));
    renderDocs();
  } catch (error) {
    console.error('Erro ao carregar documentos:', error);
    docs = [];
    renderDocs();
  }
}

function renderDocs() {
  const tbody = document.querySelector('#docsTable tbody');
  tbody.innerHTML = '';
  if (docs.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding: 20px;">Nenhum documento encontrado</td></tr>';
    return;
  }
  docs.forEach(doc => {
    const tamanhoFormatado = doc.tamanho ? formatBytes(doc.tamanho) : '-';
    const dataFormatada = doc.data ? new Date(doc.data).toLocaleDateString('pt-BR') : '-';
    const nomeDoc = doc.nome || 'documento';
    const nomeEscapado = escapeHtml(nomeDoc).replace(/'/g, "\\'");
    
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td title="${escapeHtml(nomeDoc)}">${escapeHtml(nomeDoc)}</td>
      <td><span class="categoria-badge ${doc.categoria}">${escapeHtml(doc.categoria)}</span></td>
      <td>${doc.versao}</td>
      <td>${escapeHtml(doc.criado_por)}</td>
      <td>${dataFormatada}</td>
      <td class="acoes-cell">
        <button class="btn btn-sm btn-view" onclick="viewDoc(${doc.id}, '${nomeEscapado}')">👁️ Ver</button>
        <button class="btn btn-sm btn-download" onclick="downloadDoc(${doc.id})">📥 Baixar</button>
        <button class="btn btn-sm btn-delete" onclick="deleteDoc(${doc.id})">🗑️ Excluir</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function escapeHtml(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;') }

function openDocModal(title, doc = null) {
  document.getElementById('modalDocTitle').innerText = title;
  document.getElementById('docModal').style.display = 'flex';
  document.getElementById('docId').value = doc ? doc.id : '';
  document.getElementById('docName').value = doc ? doc.nome : '';
  document.getElementById('docCategory').value = doc ? doc.categoria : 'plantas';
}

function closeDocModal() {
  document.getElementById('docModal').style.display = 'none';
}

document.addEventListener('DOMContentLoaded', () => {
  projectId = getProjectIdFromUrlOrStorage();
  if (!projectId) {
    localStorage.removeItem('current_project_id');
    alert('Selecione um projeto na tela inicial para acessar o sistema.');
    window.location.href = '../index.html';
    return;
  }
  localStorage.setItem('current_project_id', projectId);
  document.getElementById('addDocBtn').onclick = () => openDocModal('Novo Documento');
  document.getElementById('closeDocModal').onclick = closeDocModal;
  document.getElementById('docModal').onclick = (e) => { if (e.target === e.currentTarget) closeDocModal(); };
  document.getElementById('docForm').onsubmit = saveDocHandler;
  document.getElementById('backBtn').onclick = () => window.location.href = 'index.html';
  loadDocs();
});

async function saveDocHandler(e) {
  e.preventDefault();
  const id = document.getElementById('docId').value;
  const formData = new FormData();
  formData.append('nome', document.getElementById('docName').value);
  formData.append('categoria', document.getElementById('docCategory').value);
  formData.append('descricao', document.getElementById('docName').value);
  const fileInput = document.getElementById('docFile');
  if (fileInput.files[0]) formData.append('file', fileInput.files[0]);
  try {
    if (id) {
      await API.Documentos.atualizar(id, formData);
      alert('Documento atualizado com sucesso!');
    } else {
      if (!fileInput.files[0]) {
        alert('Por favor, selecione um arquivo!');
        return;
      }
      await API.Documentos.criar(projectId, formData);
      alert('Documento enviado com sucesso!');
    }
    closeDocModal();
    await loadDocs();
  } catch (error) {
    alert('Erro ao salvar documento: ' + error.message);
  }
}

async function editDoc(id) {
  const doc = docs.find(d => d.id == id);
  if (!doc) return;
  openDocModal('Editar Documento', doc);
}

async function deleteDoc(id) {
  if (!confirm('Tem certeza que deseja excluir este documento?')) return;
  try {
    await API.Documentos.deletar(id);
    await loadDocs();
  } catch (error) {
    alert('Erro ao excluir documento: ' + error.message);
  }
}

async function downloadDoc(id) {
  try {
    const url = await API.Documentos.download(id);
    // Abrir URL de download com token de autenticação
    const token = localStorage.getItem('access_token');
    const link = document.createElement('a');
    link.href = url;
    link.target = '_blank';
    link.click();
  } catch (error) {
    alert('Erro ao baixar documento: ' + error.message);
  }
}

// Função para visualizar documento em modal
function viewDoc(id, nome) {
  const token = localStorage.getItem('access_token');
  const url = `http://localhost:8000/documentos/${id}/visualizar`;
  
  // Criar modal de visualização se não existir
  let viewModal = document.getElementById('viewModal');
  if (!viewModal) {
    viewModal = document.createElement('div');
    viewModal.id = 'viewModal';
    viewModal.className = 'modal view-modal';
    viewModal.innerHTML = `
      <div class="view-modal-content">
        <div class="view-modal-header">
          <h3 id="viewModalTitle">Visualizar Documento</h3>
          <div class="view-modal-actions">
            <button class="btn btn-sm" onclick="downloadFromView()">📥 Baixar</button>
            <button class="btn btn-sm" onclick="openInNewTab()">🔗 Nova Aba</button>
            <span class="close-view" onclick="closeViewModal()">&times;</span>
          </div>
        </div>
        <div class="view-modal-body">
          <iframe id="viewFrame" src="" frameborder="0"></iframe>
        </div>
      </div>
    `;
    document.body.appendChild(viewModal);
    
    // Fechar ao clicar fora
    viewModal.onclick = (e) => { if (e.target === viewModal) closeViewModal(); };
  }
  
  // Configurar e mostrar modal
  document.getElementById('viewModalTitle').textContent = nome || 'Visualizar Documento';
  document.getElementById('viewFrame').src = url;
  viewModal.dataset.docId = id;
  viewModal.style.display = 'flex';
}

function closeViewModal() {
  const viewModal = document.getElementById('viewModal');
  if (viewModal) {
    viewModal.style.display = 'none';
    document.getElementById('viewFrame').src = '';
  }
}

function downloadFromView() {
  const viewModal = document.getElementById('viewModal');
  if (viewModal && viewModal.dataset.docId) {
    downloadDoc(viewModal.dataset.docId);
  }
}

function openInNewTab() {
  const viewModal = document.getElementById('viewModal');
  if (viewModal && viewModal.dataset.docId) {
    const url = `http://localhost:8000/documentos/${viewModal.dataset.docId}/visualizar`;
    window.open(url, '_blank');
  }
}
