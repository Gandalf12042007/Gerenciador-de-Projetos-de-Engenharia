// Estado global
let projects = [];
let loading = false;

// Carregar projetos da API
async function loadProjects() {
  if (!API.Auth.isAuthenticated()) {
    window.location.href = '../login.html';
    return;
  }
  
  loading = true;
  showLoading(true);
  
  try {
    const response = await API.Projetos.listar();
    projects = response.map(p => ({
      id: p.id,
      name: p.nome,
      city: p.localizacao || 'N/A',
      progress: p.progresso || 0,
      manager: p.cliente || 'N/A',
      start: p.data_inicio ? new Date(p.data_inicio).toLocaleDateString('pt-BR') : 'N/A',
      end: p.data_conclusao_prevista ? new Date(p.data_conclusao_prevista).toLocaleDateString('pt-BR') : 'N/A',
      status: p.status,
      pendingTasks: 0,
      delayedTasks: 0
    }));
    applyFilters();
  } catch (error) {
    console.error('Erro ao carregar projetos:', error);
    showAlert('Erro ao carregar projetos: ' + error.message, 'error');
  } finally {
    loading = false;
    showLoading(false);
  }
}

// Mostrar loading
function showLoading(show) {
  const container = document.getElementById('projectList');
  if (show) {
    container.innerHTML = '<div style="text-align:center;padding:40px;color:#666;">Carregando projetos...</div>';
  }
}

// Mostrar alerta
function showAlert(message, type = 'info') {
  const alert = document.createElement('div');
  alert.className = `alert alert-${type}`;
  alert.textContent = message;
  alert.style.cssText = 'position:fixed;top:20px;right:20px;padding:15px 20px;background:#fff;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.15);z-index:9999;';
  if (type === 'error') alert.style.background = '#fee';
  if (type === 'success') alert.style.background = '#efe';
  document.body.appendChild(alert);
  setTimeout(() => alert.remove(), 5000);
}

// render
function renderMetrics(list){
  const active = list.filter(p=>p.status==='active').length;
  const pending = list.reduce((m,p)=>m+p.pendingTasks,0);
  const delayed = list.reduce((m,p)=>m+p.delayedTasks,0);
  const avg = list.length ? Math.round(list.reduce((m,p)=>m+p.progress,0)/list.length) : 0;
  document.getElementById('count-active').innerText = active;
  document.getElementById('count-pending').innerText = pending;
  document.getElementById('count-delayed').innerText = delayed;
  document.getElementById('avg-progress').innerText = avg + '%';
}

function projectCardHtml(p){
  return `
    <article class="card">
      <h3>${escapeHtml(p.name)}</h3>
      <div class="meta">${escapeHtml(p.city)} • ${escapeHtml(p.manager)}</div>
      <div class="meta">De ${p.start} até ${p.end}</div>
      <div class="progress-wrap" aria-hidden="true">
        <div class="progress" style="width: ${p.progress}%"></div>
      </div>
      <div style="margin-top:8px">Progresso: <strong>${p.progress}%</strong></div>
      <div class="links">
        <button class="btn" onclick="viewProject(${p.id})">Abrir</button>
        <button class="btn" onclick="editProject(${p.id})">Editar</button>
      </div>
    </article>
  `;
}

function escapeHtml(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;') }

function renderList(list){
  const container = document.getElementById('projectList');
  container.innerHTML = list.map(projectCardHtml).join('\n');
  // animate progress
  setTimeout(()=>{ document.querySelectorAll('.progress').forEach(p=>p.style.width = p.style.width); }, 50);
}

function applyFilters(){
  const status = document.getElementById('filter-status').value;
  const q = document.getElementById('filter-q').value.toLowerCase().trim();
  let list = projects.slice();
  if(status !== 'all') list = list.filter(p=>p.status===status);
  if(q) list = list.filter(p=> (p.name+p.city+p.manager).toLowerCase().includes(q));
  renderMetrics(list);
  renderList(list);
}

// actions
function viewProject(id){ 
  window.location.href = `details.html?id=${id}`;
}

async function editProject(id){ 
  // TODO: Implementar modal de edição
  alert('Editar projeto: '+id);
}

async function deleteProject(id) {
  if (!confirm('Tem certeza que deseja excluir este projeto?')) return;
  
  try {
    await API.Projetos.deletar(id);
    showAlert('Projeto excluído com sucesso!', 'success');
    await loadProjects();
  } catch (error) {
    showAlert('Erro ao excluir projeto: ' + error.message, 'error');
  }
}

async function createNewProject() {
  // TODO: Implementar modal de criação
  alert('Criar novo projeto - Em desenvolvimento');
}

function logout() {
  API.Auth.logout();
  window.location.href = '../login.html';
}

// wire events
window.addEventListener('DOMContentLoaded', ()=>{
  document.getElementById('filter-status').addEventListener('change', applyFilters);
  document.getElementById('filter-q').addEventListener('input', applyFilters);
  document.getElementById('clearFilters').addEventListener('click', ()=>{ 
    document.getElementById('filter-q').value=''; 
    document.getElementById('filter-status').value='all'; 
    applyFilters(); 
  });
  document.getElementById('newProjectBtn').addEventListener('click', createNewProject);
  
  // Botão de logout se existir
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', logout);
  }
  
  // Carregar projetos da API
  loadProjects();
});
