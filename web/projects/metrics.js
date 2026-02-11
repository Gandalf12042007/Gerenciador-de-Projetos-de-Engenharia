// Métricas do Projeto + Exportação de Logs
let projectId = null;

function getProjectIdFromUrlOrStorage() {
  const params = new URLSearchParams(window.location.search);
  let pid = params.get('project');
  if (!pid) pid = localStorage.getItem('current_project_id');
  return pid || null;
}

document.addEventListener('DOMContentLoaded', () => {
  projectId = getProjectIdFromUrlOrStorage();
  if (!projectId) {
    alert('Projeto não especificado!');
    window.location.href = 'index.html';
    return;
  }
  localStorage.setItem('current_project_id', projectId);
  loadMetrics();
});

async function loadMetrics() {
  // Simulação: substitua por integração real com API se desejar
  const progresso = Math.floor(Math.random() * 100);
  const tarefas = { todo: 5, doing: 3, done: 8 };
  const docs = { plantas: 2, rrt: 1, diario: 1, fotos: 3, relatorios: 1 };

  renderProgressChart(progresso);
  renderTasksChart(tarefas);
  renderDocsChart(docs);
}

function renderProgressChart(progresso) {
  new Chart(document.getElementById('progressChart').getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: ['Progresso', 'Restante'],
      datasets: [{
        data: [progresso, 100-progresso],
        backgroundColor: ['#4A90E2', '#eee']
      }]
    },
    options: {
      plugins: { legend: { display: true } },
      cutout: '70%',
      responsive: false,
      plugins: { title: { display: true, text: 'Progresso do Projeto (%)' } }
    }
  });
}

function renderTasksChart(tarefas) {
  new Chart(document.getElementById('tasksChart').getContext('2d'), {
    type: 'bar',
    data: {
      labels: ['A Fazer', 'Em Andamento', 'Concluída'],
      datasets: [{
        label: 'Tarefas',
        data: [tarefas.todo, tarefas.doing, tarefas.done],
        backgroundColor: ['#f39c12', '#3578e5', '#27ae60']
      }]
    },
    options: {
      plugins: { title: { display: true, text: 'Tarefas por Status' } },
      responsive: false
    }
  });
}

function renderDocsChart(docs) {
  new Chart(document.getElementById('docsChart').getContext('2d'), {
    type: 'pie',
    data: {
      labels: Object.keys(docs),
      datasets: [{
        data: Object.values(docs),
        backgroundColor: ['#4A90E2', '#f39c12', '#27ae60', '#e74c3c', '#8e44ad', '#16a085']
      }]
    },
    options: {
      plugins: { title: { display: true, text: 'Documentos por Categoria' } },
      responsive: false
    }
  });
}

function exportUserLogs() {
  const logs = JSON.parse(localStorage.getItem('user_logs') || '[]');
  if (!logs.length) {
    alert('Nenhum log encontrado!');
    return;
  }
  const csv = 'Ação,Detalhes,Data\n' + logs.map(l => `${l.acao},"${l.detalhes}",${l.data}`).join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'user_logs.csv';
  a.click();
  URL.revokeObjectURL(url);
}
