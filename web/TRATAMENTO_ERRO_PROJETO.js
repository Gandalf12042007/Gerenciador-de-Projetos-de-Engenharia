"""
EXEMPLO DE TRATAMENTO DE ERROS NO CLIENTE (JavaScript)

Mostra como o frontend deve tratar os diferentes tipos de erro
"""

# ============ OPÇÃO 1: API Cliente Estruturada ============

# Arquivo: web/api-client.js (atualizado)

const API = {
  /**
   * Wrapper para requisições com tratamento de erro de projeto
   */
  async _fetch(url, options = {}) {
    try {
      const response = await fetch(url, options);
      
      if (!response.ok) {
        // Verificar tipo de erro
        const errorType = response.headers.get('X-Error-Type');
        const errorData = await response.json();
        
        // Criar objeto de erro customizado
        const error = new ProjectAPIError(
          errorData.detail || 'Erro desconhecido',
          response.status,
          errorType
        );
        
        throw error;
      }
      
      return await response.json();
    } catch (error) {
      throw error;
    }
  },
  
  Tarefas: {
    async listar(projectId) {
      try {
        if (!projectId) {
          throw new ProjectAPIError(
            'Projeto não selecionado',
            400,
            'NO_PROJECT_SELECTED'
          );
        }
        
        return await API._fetch(`/api/tarefas/projeto/${projectId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
      } catch (error) {
        if (error instanceof ProjectAPIError) {
          error.handle();
        }
        throw error;
      }
    }
  }
};


// ============ CLASSE DE ERRO CUSTOMIZADO ============

class ProjectAPIError extends Error {
  constructor(message, statusCode, errorType) {
    super(message);
    this.name = 'ProjectAPIError';
    this.statusCode = statusCode;
    this.errorType = errorType;
  }
  
  /**
   * Trata o erro apropriadamente baseado no tipo
   */
  handle() {
    switch(this.errorType) {
      case 'NO_PROJECT_SELECTED':
        this._handleNoProjectSelected();
        break;
      case 'INVALID_PROJECT':
        this._handleInvalidProject();
        break;
      case 'PROJECT_ACCESS_DENIED':
        this._handleAccessDenied();
        break;
      default:
        this._handleGenericError();
    }
  }
  
  _handleNoProjectSelected() {
    console.warn('Nenhum projeto selecionado:', this.message);
    
    showNotification({
      type: 'warning',
      title: '⚠️ Projeto Não Selecionado',
      message: 'Você precisa selecionar um projeto para continuar.',
      action: {
        label: 'Ir para Projetos',
        callback: () => window.location.href = '/projetos'
      }
    });
  }
  
  _handleInvalidProject() {
    console.error('Projeto inválido:', this.message);
    
    showNotification({
      type: 'error',
      title: '❌ Projeto Não Encontrado',
      message: 'O projeto que você procura não existe ou foi deletado.',
      action: {
        label: 'Voltar',
        callback: () => window.history.back()
      }
    });
  }
  
  _handleAccessDenied() {
    console.warn('Acesso negado:', this.message);
    
    showNotification({
      type: 'error',
      title: '🔒 Acesso Negado',
      message: 'Você não tem permissão para acessar este projeto.',
      duration: 5000
    });
  }
  
  _handleGenericError() {
    console.error('Erro na API:', this.message);
    
    showNotification({
      type: 'error',
      title: '❌ Erro',
      message: this.message
    });
  }
}


// ============ HELPER: Função para mostrar notificações ============

function showNotification(config = {}) {
  const {
    type = 'info',      // 'info', 'success', 'warning', 'error'
    title = 'Notificação',
    message = '',
    duration = 3000,   // em ms, 0 = infinito
    action = null      // { label: string, callback: function }
  } = config;
  
  // Criar elemento de notificação
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.innerHTML = `
    <div class="notification-content">
      <div class="notification-title">${escapeHtml(title)}</div>
      <div class="notification-message">${escapeHtml(message)}</div>
      ${action ? `
        <div class="notification-action">
          <button class="btn-small">${escapeHtml(action.label)}</button>
        </div>
      ` : ''}
    </div>
    <button class="notification-close">&times;</button>
  `;
  
  // Adicionar ao DOM
  const container = document.getElementById('notifications-container') || 
                   document.body.appendChild(document.createElement('div'));
  container.id = 'notifications-container';
  container.appendChild(notification);
  
  // Eventos
  const closeBtn = notification.querySelector('.notification-close');
  closeBtn.addEventListener('click', () => notification.remove());
  
  if (action) {
    notification.querySelector('button.btn-small').addEventListener('click', () => {
      action.callback();
      notification.remove();
    });
  }
  
  // Auto-fechar após duração
  if (duration > 0) {
    setTimeout(() => notification.remove(), duration);
  }
  
  return notification;
}


// ============ EXEMPLO DE USO EM COMPONENTE ============

// arquivo: web/projects/docs.js (atualizado)

let projectId = null;

function getProjectIdFromUrlOrStorage() {
  // Tentar URL
  const params = new URLSearchParams(window.location.search);
  if (params.has('project_id')) {
    return parseInt(params.get('project_id'));
  }
  
  // Tentar localStorage
  const stored = localStorage.getItem('current_project_id');
  return stored ? parseInt(stored) : null;
}

async function loadDocuments() {
  projectId = getProjectIdFromUrlOrStorage();
  
  try {
    if (!projectId) {
      throw new ProjectAPIError(
        'Nenhum projeto selecionado',
        400,
        'NO_PROJECT_SELECTED'
      );
    }
    
    const response = await fetch(`/api/documentos/projeto/${projectId}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    
    if (!response.ok) {
      const errorType = response.headers.get('X-Error-Type');
      const error = await response.json();
      throw new ProjectAPIError(error.detail, response.status, errorType);
    }
    
    const data = await response.json();
    renderDocuments(data.documents);
    
  } catch (error) {
    if (error instanceof ProjectAPIError) {
      error.handle();
    } else {
      showNotification({
        type: 'error',
        message: 'Erro ao carregar documentos'
      });
    }
  }
}


// ============ VALIDAÇÃO NO CLIENTE ANTES DE ENVIAR ============

/**
 * Validação simples no cliente antes de chamar a API
 */
async function acessarProjeto(projectId) {
  // Validar localmente
  if (!projectId || projectId <= 0) {
    showNotification({
      type: 'warning',
      title: 'Selecione um projeto',
      message: 'Você precisa selecionar um projeto primeiro',
      action: {
        label: 'Selecionar Projeto',
        callback: () => window.location.href = '/projetos'
      }
    });
    return false;
  }
  
  // Chamar a API
  try {
    const response = await fetch(`/api/projetos/${projectId}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });
    
    if (!response.ok) {
      const errorType = response.headers.get('X-Error-Type');
      throw new ProjectAPIError(
        await response.text(),
        response.status,
        errorType
      );
    }
    
    // Guardar no localStorage
    localStorage.setItem('current_project_id', projectId);
    
    // Redirecionar
    window.location.href = `/projetos/${projectId}/tarefas`;
    return true;
    
  } catch (error) {
    if (error instanceof ProjectAPIError) {
      error.handle();
    }
    return false;
  }
}


// ============ CSS PARA NOTIFICAÇÕES ============

CSS = `
.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  max-width: 400px;
  padding: 16px 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  animation: slideIn 0.3s ease-out;
  z-index: 10000;
}

@keyframes slideIn {
  from {
    transform: translateX(400px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.notification-info {
  background: #e3f2fd;
  border-left: 4px solid #2196f3;
  color: #1976d2;
}

.notification-success {
  background: #e8f5e9;
  border-left: 4px solid #4caf50;
  color: #2e7d32;
}

.notification-warning {
  background: #fff3e0;
  border-left: 4px solid #ff9800;
  color: #e65100;
}

.notification-error {
  background: #ffebee;
  border-left: 4px solid #f44336;
  color: #c62828;
}

.notification-content {
  flex: 1;
}

.notification-title {
  font-weight: 600;
  margin-bottom: 4px;
}

.notification-message {
  font-size: 14px;
  opacity: 0.9;
}

.notification-action {
  margin-top: 8px;
}

.notification-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: currentColor;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.notification-close:hover {
  opacity: 0.7;
}

#notifications-container {
  position: fixed;
  top: 0;
  right: 0;
  pointer-events: none;
  z-index: 10000;
}

#notifications-container > * {
  pointer-events: auto;
}
`


// ============ FUNÇÃO AUXILIAR ============

function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}
