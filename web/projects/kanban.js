// Kanban Board JS - CRUD de tarefas
let tasks = [];
let projectId = null;

function getProjectIdFromUrlOrStorage() {
  const params = new URLSearchParams(window.location.search);
  let pid = params.get('project');
  if (!pid) pid = localStorage.getItem('current_project_id');
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
  
  columns.forEach(col => {
    const colDiv = document.createElement('div');
    colDiv.className = 'kanban-column';
    colDiv.dataset.status = col.key;
    colDiv.innerHTML = `<h3>${col.label}</h3><div class="kanban-tasks" id="col-${col.key}" data-status="${col.key}"></div>`;
    board.appendChild(colDiv);
    
    // Configurar drag and drop na área de tarefas
    const tasksArea = colDiv.querySelector('.kanban-tasks');
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
  div.className = 'kanban-task';
  div.draggable = true;
  div.ondragstart = e => {
    div.classList.add('dragging');
    e.dataTransfer.setData('text/plain', task.id);
  };
  div.ondragend = () => div.classList.remove('dragging');
  
  // Badge de prioridade
  const prioridadeColors = {
    'urgente': '#c53030',
    'alta': '#c05621',
    'media': '#2b6cb0',
    'baixa': '#276749'
  };
  const prioridadeBg = {
    'urgente': '#fed7d7',
    'alta': '#feebc8',
    'media': '#bee3f8',
    'baixa': '#c6f6d5'
  };
  
  // Badge de etapa
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
  
  div.innerHTML = `
    <div class="task-title">${escapeHtml(task.title)}</div>
    ${task.prioridade ? `<span style="display:inline-block; padding:2px 8px; border-radius:10px; font-size:0.7rem; background:${prioridadeBg[task.prioridade]}; color:${prioridadeColors[task.prioridade]}; font-weight:600; margin:4px 0;">${task.prioridade.toUpperCase()}</span>` : ''}
    ${task.etapa_tipo ? `<span style="display:inline-block; margin-left:5px; font-size:0.8rem;">${etapaIcons[task.etapa_tipo] || '📋'} ${task.etapa_tipo}</span>` : ''}
    <div class="task-desc" style="font-size:0.85rem; color:#718096; margin:5px 0;">${escapeHtml(task.desc || '')}</div>
    ${task.responsavel_nome ? `<div style="font-size:0.75rem; color:#a0aec0;">👤 ${escapeHtml(task.responsavel_nome)}</div>` : ''}
    ${task.data_fim_prevista ? `<div style="font-size:0.75rem; color:#a0aec0;">📅 ${formatDate(task.data_fim_prevista)}</div>` : ''}
    <div class="task-actions" style="margin-top:8px;">
      <button class="btn" onclick="editTask(${task.id})">✏️</button>
      <button class="btn" onclick="deleteTask(${task.id})">🗑️</button>
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
    alert('Projeto não especificado!');
    window.location.href = 'index.html';
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
