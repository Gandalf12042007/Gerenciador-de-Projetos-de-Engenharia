// Timeline JS - Cronograma
let timelineItems = [];
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
  // ...existing code...
});

// ...existing code...