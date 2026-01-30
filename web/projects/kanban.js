// Kanban Board JS - CRUD de tarefas
let tasks = [];
let projectId = null;

// Backend usa: a_fazer, em_execucao, concluida
const columns = [
  { key: 'a_fazer', label: 'A Fazer' },
  { key: 'em_execucao', label: 'Em Andamento' },
  { key: 'concluida', label: 'Concluída' }
];

function getProjectIdFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return params.get('project') || null;
}

async function loadTasks() {
  if (!projectId) return;
  try {
    const response = await API.Tarefas.listar(projectId);
    const tarefasData = response.data || response || [];
    tasks = tarefasData.map(t => ({
      id: t.id,
      title: t.titulo,
      desc: t.descricao,
      status: t.status
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
    colDiv.innerHTML = `<h3>${col.label}</h3><div class="kanban-tasks" id="col-${col.key}"></div>`;
    board.appendChild(colDiv);
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
  div.innerHTML = `
    <div class="task-title">${escapeHtml(task.title)}</div>
    <div class="task-desc">${escapeHtml(task.desc || '')}</div>
    <div class="task-actions">
      <button class="btn" onclick="editTask(${task.id})">Editar</button>
      <button class="btn" onclick="deleteTask(${task.id})">Excluir</button>
    </div>
  `;
  return div;
}

function escapeHtml(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;') }

// Drag and drop
columns.forEach(col => {
  document.addEventListener('dragover', function(e) {
    if (e.target.id === 'col-' + col.key) {
      e.preventDefault();
    }
  });
  document.addEventListener('drop', async function(e) {
    if (e.target.id === 'col-' + col.key) {
      e.preventDefault();
      const taskId = e.dataTransfer.getData('text/plain');
      await moveTask(taskId, col.key);
    }
  });
});

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
}

function closeTaskModal() {
  document.getElementById('taskModal').style.display = 'none';
}

document.addEventListener('DOMContentLoaded', () => {
  projectId = getProjectIdFromUrl();
  if (!projectId) {
    alert('Projeto não especificado!');
    window.location.href = 'index.html';
    return;
  }
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
    status: document.getElementById('taskStatus').value
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
