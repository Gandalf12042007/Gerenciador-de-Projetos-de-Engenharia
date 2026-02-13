// Estado global
let projects = [];
let loading = false;

// Carregar projetos da API
async function loadProjects() {
  // Verifica autenticação
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    window.location.href = '../login.html';
    return;
  }
  
  loading = true;
  showLoading(true);
  
  try {
    const response = await API.Projetos.listar();
    const projetosData = response.data || response || [];
    projects = projetosData.map(p => ({
      id: p.id,
      name: p.nome,
      city: p.localizacao || '',
      progress: p.progresso || p.progresso_percentual || 0,
      manager: p.cliente || '',
      start: p.data_inicio ? new Date(p.data_inicio).toLocaleDateString('pt-BR') : '',
      end: p.data_conclusao_prevista ? new Date(p.data_conclusao_prevista).toLocaleDateString('pt-BR') : '',
      status: p.status || 'planejamento',
      code: p.codigo_acesso || '',
      pendingTasks: 0,
      delayedTasks: 0
    }));
    applyFilters();
  } catch (error) {
    console.error('Erro ao carregar projetos:', error);
    showToast('Erro ao carregar projetos: ' + error.message, 'error');
  } finally {
    loading = false;
    showLoading(false);
  }
// ...existing code...

// Mostrar loading
function showLoading(show) {
  const container = document.getElementById('projectsGrid');
  const empty = document.getElementById('emptyState');
  if (!container) return;
  
  if (show) {
    container.innerHTML = `
      <div style="grid-column: 1/-1; text-align:center; padding:60px 20px;">
        <div class="loading-spinner" style="width:40px;height:40px;margin:0 auto 16px;"></div>
        <span style="color:var(--text-muted);">Carregando projetos...</span>
      </div>
    `;
    if (empty) empty.style.display = 'none';
  }
}

// render
function renderMetrics(list){
  const active = list.filter(p => p.status === 'em_andamento').length;
  const pending = list.reduce((m,p) => m + p.pendingTasks, 0);
  const delayed = list.reduce((m,p) => m + p.delayedTasks, 0);
  const avg = list.length ? Math.round(list.reduce((m,p) => m + p.progress, 0) / list.length) : 0;
  
  const statActive = document.getElementById('statActive');
  const statPending = document.getElementById('statPending');
  const statDelayed = document.getElementById('statDelayed');
  const statProgress = document.getElementById('statProgress');
  
  if (statActive) statActive.innerText = active;
  if (statPending) statPending.innerText = pending;
  if (statDelayed) statDelayed.innerText = delayed;
  if (statProgress) statProgress.innerText = avg + '%';
}

function getProgressColor(progress) {
  if (progress >= 80) return '#10b981'; // Verde
  if (progress >= 50) return '#f59e0b'; // Amarelo/Laranja
  if (progress >= 20) return '#3b82f6'; // Azul
  if (progress > 0) return '#ef4444'; // Vermelho
  return '#9ca3af'; // Cinza para 0%
}

function getStatusLabel(status) {
  const statusMap = {
    'planejamento': '📋 Planejamento',
    'em_andamento': '🚧 Em Andamento',
    'pausado': '⏸️ Pausado',
    'concluido': '✅ Concluído',
    'cancelado': '❌ Cancelado'
  };
  return statusMap[status] || status;
}

function projectCardHtml(p){
  const progressWidth = p.progress > 0 ? p.progress : 0;
  return `
    <article class="project-card" onclick="viewProject(${p.id})">
      <div class="project-header">
        <div class="project-icon">🏗️</div>
        <div class="project-actions">
          <button class="project-action-btn" onclick="event.stopPropagation(); editProject(${p.id})" title="Editar">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
          </button>
          <button class="project-action-btn delete" onclick="event.stopPropagation(); deleteProject(${p.id})" title="Excluir">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            </svg>
          </button>
        </div>
      </div>
      
      <h3 class="project-title">${escapeHtml(p.name)}</h3>
      
      ${p.city ? `<div class="project-location"><span>📍</span> ${escapeHtml(p.city)}</div>` : ''}
      
      <div class="project-meta">
        <span class="project-status ${p.status}">${getStatusLabel(p.status)}</span>
        ${p.end ? `<span class="project-date">📅 ${p.end}</span>` : ''}
      </div>
      
      <div class="project-progress">
        <div class="progress-header">
          <span class="progress-label">Progresso</span>
          <span class="progress-value">${progressWidth}%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-bar-fill" style="width: ${progressWidth}%;"></div>
        </div>
      </div>
      
      <div class="project-footer">
        ${p.code ? `
          <div class="project-code">
            <span>Código:</span>
            <span class="project-code-value">${p.code}</span>
          </div>
        ` : '<div></div>'}
        <div class="project-team">
          <div class="team-avatar">👤</div>
        </div>
      </div>
    </article>
  `;
}

function escapeHtml(s){ return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;') }

function renderList(list){
  const container = document.getElementById('projectsGrid');
  const empty = document.getElementById('emptyState');
  
  if (!container) return;
  
  if (list.length === 0) {
    container.innerHTML = '';
    if (empty) empty.style.display = 'block';
  } else {
    container.innerHTML = list.map(projectCardHtml).join('\n');
    if (empty) empty.style.display = 'none';
  }
}

function applyFilters(){
  const statusEl = document.getElementById('filterStatus');
  const searchEl = document.getElementById('searchInput');
  
  const status = statusEl ? statusEl.value : 'all';
  const q = searchEl ? searchEl.value.toLowerCase().trim() : '';
  
  let list = projects.slice();
  if(status !== 'all') list = list.filter(p => p.status === status);
  if(q) list = list.filter(p => (p.name + p.city + p.manager).toLowerCase().includes(q));
  
  renderMetrics(list);
  renderList(list);
}
  renderMetrics(list);
  renderList(list);
}

// actions
function viewProject(id){
  localStorage.setItem('current_project_id', id);
  window.location.href = `kanban.html?project=${id}`;
}

function viewDocs(id){
  localStorage.setItem('current_project_id', id);
  window.location.href = `docs.html?project=${id}`;
}

function viewTeam(id){
  localStorage.setItem('current_project_id', id);
  window.location.href = `equipes.html?project=${id}`;
}

function viewMaterials(id){
  localStorage.setItem('current_project_id', id);
  window.location.href = `materials.html?project=${id}`;
}

function viewBudget(id){
  localStorage.setItem('current_project_id', id);
  window.location.href = `budget.html?project=${id}`;
}


async function editProject(id){
  const project = projects.find(p => p.id === id);
  if (!project) return;
  openProjectModal('Editar Projeto', project);
}

function openProjectModal(title, project = null) {
  const modal = document.getElementById('projectModal');
  const modalTitle = document.getElementById('modalTitle');
  const codeGroup = document.getElementById('codeGroup');
  const projectCode = document.getElementById('projectCode');
  const saveBtnText = document.getElementById('saveBtnText');
  
  if (modalTitle) modalTitle.innerText = title;
  if (modal) modal.classList.add('active');
  
  document.getElementById('projectId').value = project ? project.id : '';
  document.getElementById('projectName').value = project ? project.name : '';
  document.getElementById('projectCity').value = project && project.city ? project.city : '';
  document.getElementById('projectManager').value = project && project.manager ? project.manager : '';
  document.getElementById('projectStart').value = project && project.start ? formatDateForInput(project.start) : '';
  document.getElementById('projectEnd').value = project && project.end ? formatDateForInput(project.end) : '';
  document.getElementById('projectStatus').value = project ? project.status : 'planejamento';
  
  const progressValue = project ? project.progress : 0;
  document.getElementById('projectProgress').value = progressValue;
  const progressLabel = document.getElementById('progressValue');
  if (progressLabel) progressLabel.textContent = progressValue;
  
  // Mostrar código de acesso apenas na edição
  if (codeGroup && projectCode) {
    if (project && project.code) {
      codeGroup.style.display = 'block';
      projectCode.textContent = project.code;
    } else {
      codeGroup.style.display = 'none';
    }
  }
  
  // Texto do botão
  if (saveBtnText) {
    saveBtnText.textContent = project ? 'Salvar Alterações' : 'Criar Projeto';
  }
}

function closeProjectModal() {
  const modal = document.getElementById('projectModal');
  if (modal) modal.classList.remove('active');
}

function formatDateForInput(dateStr) {
  // Converte dd/mm/yyyy para yyyy-mm-dd
  const [d, m, y] = dateStr.split('/');
  return `${y}-${m.padStart(2,'0')}-${d.padStart(2,'0')}`;
}

document.addEventListener('DOMContentLoaded', () => {
  const closeModalBtn = document.getElementById('closeModal');
  const cancelBtn = document.getElementById('cancelBtn');
  const projectModal = document.getElementById('projectModal');
  const projectForm = document.getElementById('projectForm');
  const progressSlider = document.getElementById('projectProgress');
  const copyCodeBtn = document.getElementById('copyCode');
  
  if (closeModalBtn) closeModalBtn.onclick = closeProjectModal;
  if (cancelBtn) cancelBtn.onclick = closeProjectModal;
  if (projectModal) projectModal.onclick = (e) => { if (e.target === e.currentTarget) closeProjectModal(); };
  if (projectForm) projectForm.onsubmit = saveProjectHandler;
  
  // Progress slider
  if (progressSlider) {
    progressSlider.oninput = function() {
      const label = document.getElementById('progressValue');
      if (label) label.textContent = this.value;
    };
  }
  
  // Copy code button
  if (copyCodeBtn) {
    copyCodeBtn.onclick = function() {
      const code = document.getElementById('projectCode')?.textContent;
      if (code && code !== '-') {
        navigator.clipboard.writeText(code).then(() => {
          showToast('Código copiado!', 'success');
        });
      }
    };
  }
});

// Validar data (só permitir anos entre 2000 e 2100)
function isValidDate(dateStr) {
  if (!dateStr) return true; // Data opcional
  const date = new Date(dateStr);
  const year = date.getFullYear();
  return year >= 2000 && year <= 2100;
}

// Validar formulário
function validateProjectForm() {
  const startDate = document.getElementById('projectStart').value;
  const endDate = document.getElementById('projectEnd').value;
  const nome = document.getElementById('projectName').value.trim();
  
  if (!nome) {
    showToast('O nome do projeto é obrigatório!', 'error');
    return false;
  }
  
  if (startDate && !isValidDate(startDate)) {
    showToast('Data de início inválida! Use uma data entre 2000 e 2100.', 'error');
    return false;
  }
  
  if (endDate && !isValidDate(endDate)) {
    showToast('Data de conclusão inválida! Use uma data entre 2000 e 2100.', 'error');
    return false;
  }
  
  if (startDate && endDate && new Date(startDate) > new Date(endDate)) {
    showToast('A data de início não pode ser maior que a data de conclusão!', 'error');
    return false;
  }
  
  return true;
}

async function saveProjectHandler(e) {
  e.preventDefault();
  
  // Validar antes de enviar
  if (!validateProjectForm()) return;
  
  const id = document.getElementById('projectId').value;
  const saveBtnText = document.getElementById('saveBtnText');
  const saveBtnLoading = document.getElementById('saveBtnLoading');
  const saveBtn = document.getElementById('saveBtn');
  
  // Loading state
  if (saveBtn) saveBtn.disabled = true;
  if (saveBtnText) saveBtnText.style.display = 'none';
  if (saveBtnLoading) saveBtnLoading.style.display = 'inline-block';
  
  const data = {
    nome: document.getElementById('projectName').value.trim(),
    localizacao: document.getElementById('projectCity').value.trim(),
    cliente: document.getElementById('projectManager').value.trim(),
    data_inicio: document.getElementById('projectStart').value || null,
    data_conclusao_prevista: document.getElementById('projectEnd').value || null,
    status: document.getElementById('projectStatus').value,
    progresso_percentual: parseInt(document.getElementById('projectProgress').value) || 0
  };
  
  try {
    if (id) {
      await API.Projetos.atualizar(id, data);
      showToast('Projeto atualizado com sucesso!', 'success');
    } else {
      await API.Projetos.criar(data);
      showToast('Projeto criado com sucesso!', 'success');
    }
    closeProjectModal();
    await loadProjects();
  } catch (error) {
    showToast('Erro ao salvar projeto: ' + error.message, 'error');
    console.error('Erro detalhado ao criar/atualizar projeto:', error);
    if (error.response) {
      console.error('Resposta da API:', error.response);
      showToast('Detalhes: ' + JSON.stringify(error.response), 'error');
    }
  } finally {
    if (saveBtn) saveBtn.disabled = false;
    if (saveBtnText) saveBtnText.style.display = 'inline';
    if (saveBtnLoading) saveBtnLoading.style.display = 'none';
  }
}

async function deleteProject(id) {
  if (!confirm('Tem certeza que deseja excluir este projeto?')) return;
  
  try {
    await API.Projetos.deletar(id);
    showToast('Projeto excluído com sucesso!', 'success');
    await loadProjects();
  } catch (error) {
    showToast('Erro ao excluir projeto: ' + error.message, 'error');
  }
}

async function createNewProject() {
  openProjectModal('Novo Projeto');
}

function logout() {
  API.Auth.logout();
  window.location.href = '../login.html';
}

// wire events
window.addEventListener('DOMContentLoaded', ()=>{
  const filterStatus = document.getElementById('filterStatus');
  const searchInput = document.getElementById('searchInput');
  const clearFilters = document.getElementById('clearFilters');
  const newProjectBtn = document.getElementById('newProjectBtn');
  
  if (filterStatus && typeof applyFilters === 'function') filterStatus.addEventListener('change', applyFilters);
  if (searchInput && typeof applyFilters === 'function') searchInput.addEventListener('input', applyFilters);
  if (clearFilters) {
    clearFilters.addEventListener('click', ()=>{ 
      if (searchInput) searchInput.value = ''; 
      if (filterStatus) filterStatus.value = 'all'; 
      if (typeof applyFilters === 'function') applyFilters(); 
    });
  }
  if (newProjectBtn) {
    newProjectBtn.addEventListener('click', () => {
      // Forçar exibição do modal
      const modal = document.getElementById('projectModal');
      if (modal) modal.classList.add('active');
      openProjectModal('Novo Projeto');
    });
  }
  
  // Botão de logout se existir
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', logout);
  }
  
  // Carregar projetos da API
  loadProjects();
    // Corrigir navegação: se houver apenas um projeto, selecionar automaticamente
    setTimeout(() => {
      const list = projects;
      if (list.length === 1) {
        localStorage.setItem('current_project_id', list[0].id);
        window.location.href = `kanban.html?project=${list[0].id}`;
      }
    }, 1500);
});
