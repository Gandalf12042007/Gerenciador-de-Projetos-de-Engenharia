// Chat do Projeto - WebSocket + Log
let projectId = null;
let user = API.Auth.getUser ? API.Auth.getUser() : { nome: 'Você' };
let ws = null;

function getProjectIdFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return params.get('project') || null;
}

function connectWebSocket() {
  if (!projectId) return;
  ws = new WebSocket(`ws://localhost:8000/api/chat/${projectId}`);
  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    addMessage(msg, msg.usuario === user.nome);
    logAction('mensagem_recebida', msg.texto);
  };
  ws.onopen = () => logAction('conexao_chat', 'Conectado ao chat');
  ws.onclose = () => logAction('desconexao_chat', 'Desconectado do chat');
}

document.addEventListener('DOMContentLoaded', () => {
  projectId = getProjectIdFromUrl();
  if (!projectId) {
    alert('Projeto não especificado!');
    window.location.href = 'index.html';
    return;
  }
  connectWebSocket();
  document.getElementById('chatForm').onsubmit = sendMessageHandler;
});

function addMessage(msg, isMe) {
  const div = document.createElement('div');
  div.className = 'chat-message' + (isMe ? ' me' : '');
  div.innerHTML = `<strong>${escapeHtml(msg.usuario)}:</strong> ${escapeHtml(msg.texto)}`;
  document.getElementById('chatMessages').appendChild(div);
  document.getElementById('chatMessages').scrollTop = 99999;
}

function escapeHtml(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;') }

function sendMessageHandler(e) {
  e.preventDefault();
  const input = document.getElementById('chatInput');
  const texto = input.value.trim();
  if (!texto) return;
  const msg = { usuario: user.nome, texto };
  ws.send(JSON.stringify(msg));
  addMessage(msg, true);
  logAction('mensagem_enviada', texto);
  input.value = '';
}

// Log de ações do usuário (frontend)
function logAction(acao, detalhes) {
  if (!window.localStorage) return;
  const logs = JSON.parse(localStorage.getItem('user_logs') || '[]');
  logs.push({ acao, detalhes, data: new Date().toISOString() });
  localStorage.setItem('user_logs', JSON.stringify(logs));
}
