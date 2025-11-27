// sample data
const projects = [
  { id: 1, name: 'Residencial Jardim', city: 'São Paulo, SP', progress: 58, manager: 'Eng. Joao', start: '2024-09-01', end: '2025-01-30', status: 'active', pendingTasks: 12, delayedTasks: 3 },
  { id: 2, name: 'Prédio Comercial Alpha', city: 'Belo Horizonte, MG', progress: 72, manager: 'Eng. Maria', start: '2024-06-01', end: '2024-12-12', status: 'active', pendingTasks: 4, delayedTasks: 1 },
  { id: 3, name: 'Pavimentação BR-99', city: 'Curitiba, PR', progress: 22, manager: 'Eng. Paulo', start: '2024-11-01', end: '2025-10-01', status: 'active', pendingTasks: 45, delayedTasks: 15 },
  { id: 4, name: 'Reforma Escola Municipal', city: 'Campinas, SP', progress: 100, manager: 'Eng. Pedro', start: '2023-01-15', end: '2023-05-10', status: 'completed', pendingTasks: 0, delayedTasks: 0 }
];

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
function viewProject(id){ alert('Abrir projeto: '+id); }
function editProject(id){ alert('Editar projeto: '+id); }

// wire events
window.addEventListener('DOMContentLoaded', ()=>{
  document.getElementById('filter-status').addEventListener('change', applyFilters);
  document.getElementById('filter-q').addEventListener('input', applyFilters);
  document.getElementById('clearFilters').addEventListener('click', ()=>{ document.getElementById('filter-q').value=''; document.getElementById('filter-status').value='all'; applyFilters(); });
  document.getElementById('newProjectBtn').addEventListener('click', ()=>alert('Criar novo projeto'));
  applyFilters();
});
