// Chat do Projeto - WebSocket + Log com persistência
let projectId = null;
let user = null;
let ws = null;
const API_BASE = 'http://localhost:8000';

function getUser() {
  const userStr = localStorage.getItem('user');
  if (userStr) {
    try {
      return JSON.parse(userStr);
    } catch (e) {
      return { nome: 'Você', id: 0 };
    }
  }
  return { nome: 'Você', id: 0 };
}

function getProjectIdFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return params.get('project') || null;
}

function connectWebSocket() {
  if (!projectId) return;
  try {
    ws = new WebSocket(`ws://localhost:8000/chat/ws/${projectId}`);
    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.autor_id !== user.id) {
        addMessage({
          usuario: msg.autor_nome || 'Usuário',
          texto: msg.conteudo
        }, false);
      }
      logAction('mensagem_recebida', msg.conteudo);
    };
    ws.onopen = () => {
      console.log('WebSocket conectado');
      logAction('conexao_chat', 'Conectado ao chat');
    };
    ws.onclose = () => {
      console.log('WebSocket desconectado');
      logAction('desconexao_chat', 'Desconectado do chat');
      // Reconectar após 3 segundos
      setTimeout(connectWebSocket, 3000);
    };
    ws.onerror = (err) => console.error('WebSocket error:', err);
  } catch (e) {
    console.error('Erro ao conectar WebSocket:', e);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  user = getUser();
  projectId = getProjectIdFromUrl();
  if (!projectId) {
    alert('Projeto não especificado!');
    window.location.href = 'index.html';
    return;
  }
  loadMessages();
  connectWebSocket();
  document.getElementById('chatForm').onsubmit = sendMessageHandler;
});

async function loadMessages() {
  try {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE}/chat/projeto/${projectId}/mensagens?limit=50`, {
      headers: { 'Authorization': 'Bearer ' + token }
    });
    
    if (response.ok) {
      const data = await response.json();
      const messagesData = data.mensagens || [];
      // Limpar mensagens anteriores
      document.getElementById('chatMessages').innerHTML = '';
      // Ordenar por data (mais antigas primeiro)
      messagesData.reverse().forEach(msg => {
        addMessage({
          usuario: msg.autor_nome || 'Anônimo',
          texto: msg.conteudo || msg.mensagem,
          data: msg.enviada_em
        }, msg.autor_id === user.id);
      });
    }
  } catch (e) {
    console.warn('Erro ao carregar mensagens:', e);
  }
}

function addMessage(msg, isMe) {
  const div = document.createElement('div');
  div.className = 'chat-message' + (isMe ? ' me' : '');
  const tempo = msg.data ? new Date(msg.data).toLocaleTimeString('pt-BR', {hour: '2-digit', minute: '2-digit'}) : '';
  div.innerHTML = `
    <div class="msg-header">
      <strong>${escapeHtml(msg.usuario)}</strong>
      ${tempo ? '<span class="msg-time">' + tempo + '</span>' : ''}
    </div>
    <div class="msg-content">${escapeHtml(msg.texto)}</div>
  `;
  document.getElementById('chatMessages').appendChild(div);
  document.getElementById('chatMessages').scrollTop = 99999;
}

function escapeHtml(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;') }

async function sendMessageHandler(e) {
  e.preventDefault();
  const input = document.getElementById('chatInput');
  const texto = input.value.trim();
  if (!texto) return;
  
  try {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE}/chat/projeto/${projectId}/mensagens`, {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ conteudo: texto })
    });
    
    if (response.ok) {
      addMessage({ usuario: user.nome, texto, data: new Date().toISOString() }, true);
      input.value = '';
      logAction('mensagem_enviada', texto);
    } else {
      alert('Erro ao enviar mensagem');
    }
  } catch (e) {
    console.error('Erro ao enviar mensagem:', e);
    alert('Erro ao enviar mensagem');
  }
}

// Log de ações do usuário (frontend)
function logAction(acao, detalhes) {
  if (!window.localStorage) return;
  const logs = JSON.parse(localStorage.getItem('user_logs') || '[]');
  logs.push({ acao, detalhes, data: new Date().toISOString() });
  // Manter apenas últimas 100 entradas
  if (logs.length > 100) logs.shift();
  localStorage.setItem('user_logs', JSON.stringify(logs));
}
