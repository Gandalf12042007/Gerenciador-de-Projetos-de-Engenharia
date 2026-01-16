// Documentos - JS CRUD
let docs = [];
let projectId = null;

function getProjectIdFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return params.get('project') || null;
}

async function loadDocs() {
  if (!projectId) return;
  try {
    const response = await API.Documentos.listar(projectId);
    docs = response.map(d => ({
      id: d.id,
      nome: d.nome,
      categoria: d.categoria,
      versao: d.versao || 1,
      criado_por: d.criado_por_nome || 'N/A',
      data: d.data_criacao || '',
      url: d.url || '',
    }));
    renderDocs();
  } catch (error) {
    alert('Erro ao carregar documentos: ' + error.message);
  }
}

function renderDocs() {
  const tbody = document.querySelector('#docsTable tbody');
  tbody.innerHTML = '';
  docs.forEach(doc => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${escapeHtml(doc.nome)}</td>
      <td>${escapeHtml(doc.categoria)}</td>
      <td>${doc.versao}</td>
      <td>${escapeHtml(doc.criado_por)}</td>
      <td>${escapeHtml(doc.data)}</td>
      <td>
        <button class="btn" onclick="downloadDoc(${doc.id})">Baixar</button>
        <button class="btn" onclick="editDoc(${doc.id})">Editar</button>
        <button class="btn" onclick="deleteDoc(${doc.id})">Excluir</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
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
  projectId = getProjectIdFromUrl();
  if (!projectId) {
    alert('Projeto não especificado!');
    window.location.href = 'index.html';
    return;
  }
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
  const fileInput = document.getElementById('docFile');
  if (fileInput.files[0]) formData.append('file', fileInput.files[0]);
  try {
    if (id) {
      await API.Documentos.atualizar(id, formData);
    } else {
      await API.Documentos.criar(projectId, formData);
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
    window.open(url, '_blank');
  } catch (error) {
    alert('Erro ao baixar documento: ' + error.message);
  }
}
