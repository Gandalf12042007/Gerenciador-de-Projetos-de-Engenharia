// Equipes JS - CRUD de equipes
let equipes = [];
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

document.addEventListener('DOMContentLoaded', () => {
  projectId = getProjectIdFromUrlOrStorage();
  if (!projectId) {
    localStorage.removeItem('current_project_id');
    alert('Selecione um projeto na tela inicial para acessar o sistema.');
    window.location.href = '../index.html';
    return;
  }
  localStorage.setItem('current_project_id', projectId);
  // ...existing code...
});

// ...existing code...