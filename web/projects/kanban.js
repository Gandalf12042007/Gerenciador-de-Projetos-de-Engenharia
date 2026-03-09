// Kanban Board JS - CRUD de tarefas
let tasks = [];
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

// Backend usa: a_fazer, em_andamento, em_revisao, concluida
const columns = [
  { key: 'a_fazer', label: 'A Fazer' },
  { key: 'em_andamento', label: 'Em Andamento' },
  { key: 'em_revisao', label: 'Em Revisão' },
  { key: 'concluida', label: 'Concluída' }
];

async function loadTasks() {
  if (!projectId) return;
  try {
    const response = await API.Tarefas.listar(projectId);
    const tarefasData = response.data || response || [];
    tasks = tarefasData.map(t => ({
      id: t.id,
      title: t.titulo,
      desc: t.descricao,
      status: t.status,
      prioridade: t.prioridade,
      data_inicio: t.data_inicio,
      data_fim_prevista: t.data_fim_prevista,
      etapa_tipo: t.etapa_tipo,
      responsavel_tecnico: t.responsavel_tecnico,
      numero_art: t.numero_art,
      observacoes_tecnicas: t.observacoes_tecnicas,
      responsavel_nome: t.responsavel_nome
    }));
    renderKanban();
  } catch (error) {
    alert('Erro ao carregar tarefas: ' + error.message);
  }
}

function renderKanban() {
  const board = document.getElementById('kanbanBoard');
  board.innerHTML = '';
  board.className = 'jira-kanban-board';
  
  const columnClasses = ['todo', 'progress', 'review', 'done'];
  
  columns.forEach((col, idx) => {
    const colTasks = tasks.filter(t => t.status === col.key);
    const colDiv = document.createElement('div');
    colDiv.className = 'jira-kanban-column';
    colDiv.dataset.status = col.key;
    colDiv.innerHTML = `
      <div class="column-header ${columnClasses[idx]}">
        <span class="column-title">${col.label}</span>
        <span class="column-count">${colTasks.length}</span>
      </div>
      <div class="column-tasks" id="col-${col.key}" data-status="${col.key}"></div>
    `;
    board.appendChild(colDiv);
    
    // Configurar drag and drop na área de tarefas
    const tasksArea = colDiv.querySelector('.column-tasks');
    tasksArea.addEventListener('dragover', (e) => {
      e.preventDefault();
      tasksArea.classList.add('drag-over');
    });
    tasksArea.addEventListener('dragleave', (e) => {
      tasksArea.classList.remove('drag-over');
    });
    tasksArea.addEventListener('drop', async (e) => {
      e.preventDefault();
      tasksArea.classList.remove('drag-over');
      const taskId = e.dataTransfer.getData('text/plain');
      if (taskId) {
        await moveTask(taskId, col.key);
      }
    });
  });
  
  columns.forEach(col => {
    const colTasks = tasks.filter(t => t.status === col.key);
    const colDiv = document.getElementById('col-' + col.key);
    colTasks.forEach(task => {
      colDiv.appendChild(taskCard(task));
    });
  });
}

function taskCard(task) {
  const div = document.createElement('div');
  div.className = `jira-task-card priority-${task.prioridade || 'media'}`;
  div.draggable = true;
  div.ondragstart = e => {
    div.classList.add('dragging');
    e.dataTransfer.setData('text/plain', task.id);
  };
  div.ondragend = () => div.classList.remove('dragging');
  
  // Ícones de etapa
  const etapaIcons = {
    'fundacao': '🏗️',
    'estrutura': '🔩',
    'alvenaria': '🧱',
    'cobertura': '🏠',
    'eletrica': '⚡',
    'hidraulica': '🚰',
    'revestimento': '🎨',
    'acabamento': '✨',
    'pintura': '🖌️',
    'paisagismo': '🌳',
    'limpeza': '🧹',
    'outro': '📋'
  };
  
  // Prioridade labels
  const prioridadeLabels = {
    'urgente': 'URGENTE',
    'alta': 'ALTA',
    'media': 'MÉDIA',
    'baixa': 'BAIXA'
  };
  
  div.innerHTML = `
    <div class="task-card-header">
      <span class="task-card-title">${escapeHtml(task.title)}</span>
      <div class="task-card-menu">
        <button class="btn-jira-icon" onclick="event.stopPropagation(); editTask(${task.id})" title="Editar">✏️</button>
      </div>
    </div>
    ${task.desc ? `<div class="task-card-desc">${escapeHtml(task.desc)}</div>` : ''}
    <div class="task-card-footer">
      <div class="task-badges">
        ${task.prioridade ? `<span class="task-badge badge-priority-${task.prioridade}">${prioridadeLabels[task.prioridade] || task.prioridade}</span>` : ''}
        ${task.etapa_tipo ? `<span class="task-badge badge-etapa">${etapaIcons[task.etapa_tipo] || '📋'} ${task.etapa_tipo}</span>` : ''}
      </div>
      ${task.responsavel_nome ? `<div class="task-assignee" title="${escapeHtml(task.responsavel_nome)}">${task.responsavel_nome.charAt(0).toUpperCase()}</div>` : ''}
    </div>
    ${task.data_fim_prevista ? `<div style="font-size:0.75rem;color:#6B778C;margin-top:8px;">📅 ${formatDate(task.data_fim_prevista)}</div>` : ''}
    <div class="task-card-actions">
      <button class="task-action-btn" onclick="event.stopPropagation(); editTask(${task.id})">✏️ Editar</button>
      <button class="task-action-btn danger" onclick="event.stopPropagation(); deleteTask(${task.id})">🗑️ Excluir</button>
    </div>
  `;
  return div;
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleDateString('pt-BR');
}

function escapeHtml(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;') }

// Drag and drop - configurado no renderKanban()

async function moveTask(id, newStatus) {
  const task = tasks.find(t => t.id == id);
  if (!task || task.status === newStatus) return;
  try {
    await API.Tarefas.atualizar(id, { status: newStatus });
    task.status = newStatus;
    renderKanban();
  } catch (error) {
    alert('Erro ao mover tarefa: ' + error.message);
  }
}

function openTaskModal(title, task = null) {
  document.getElementById('modalTaskTitle').innerText = title;
  document.getElementById('taskModal').style.display = 'flex';
  document.getElementById('taskId').value = task ? task.id : '';
  document.getElementById('taskTitle').value = task ? task.title : '';
  document.getElementById('taskDesc').value = task ? task.desc : '';
  document.getElementById('taskStatus').value = task ? task.status : 'a_fazer';
  document.getElementById('taskPrioridade').value = task ? (task.prioridade || 'media') : 'media';
  document.getElementById('taskDataInicio').value = task ? (task.data_inicio || '') : '';
  document.getElementById('taskDataFim').value = task ? (task.data_fim_prevista || '') : '';
  document.getElementById('taskEtapaTipo').value = task ? (task.etapa_tipo || '') : '';
  document.getElementById('taskNumeroArt').value = task ? (task.numero_art || '') : '';
  document.getElementById('taskResponsavelTecnico').value = task ? (task.responsavel_tecnico || '') : '';
  document.getElementById('taskObsTecnicas').value = task ? (task.observacoes_tecnicas || '') : '';
}

function closeTaskModal() {
  document.getElementById('taskModal').style.display = 'none';
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
  document.getElementById('addTaskBtn').onclick = () => openTaskModal('Nova Tarefa');
  document.getElementById('closeTaskModal').onclick = closeTaskModal;
  document.getElementById('taskModal').onclick = (e) => { if (e.target === e.currentTarget) closeTaskModal(); };
  document.getElementById('taskForm').onsubmit = saveTaskHandler;
  document.getElementById('backBtn').onclick = () => window.location.href = 'index.html';
  loadTasks();
});

async function saveTaskHandler(e) {
  e.preventDefault();
  const id = document.getElementById('taskId').value;
  const data = {
    titulo: document.getElementById('taskTitle').value,
    descricao: document.getElementById('taskDesc').value,
    status: document.getElementById('taskStatus').value,
    prioridade: document.getElementById('taskPrioridade').value,
    data_inicio: document.getElementById('taskDataInicio').value || null,
    data_fim_prevista: document.getElementById('taskDataFim').value || null,
    etapa_tipo: document.getElementById('taskEtapaTipo').value || null,
    numero_art: document.getElementById('taskNumeroArt').value || null,
    responsavel_tecnico: document.getElementById('taskResponsavelTecnico').value || null,
    observacoes_tecnicas: document.getElementById('taskObsTecnicas').value || null
  };
  try {
    if (id) {
      await API.Tarefas.atualizar(id, data);
    } else {
      await API.Tarefas.criar(projectId, data);
    }
    closeTaskModal();
    await loadTasks();
  } catch (error) {
    alert('Erro ao salvar tarefa: ' + error.message);
  }
}

async function editTask(id) {
  const task = tasks.find(t => t.id == id);
  if (!task) return;
  openTaskModal('Editar Tarefa', task);
}

async function deleteTask(id) {
  if (!confirm('Tem certeza que deseja excluir esta tarefa?')) return;
  try {
    await API.Tarefas.deletar(id);
    await loadTasks();
  } catch (error) {
    alert('Erro ao excluir tarefa: ' + error.message);
  }
}
