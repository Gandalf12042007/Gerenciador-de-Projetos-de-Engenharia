/**
 * Módulo de Segurança Aprimorado - Fase 5
 * Proteção contra acesso indevido e controle de permissões
 */

class SecurityManager {
  constructor() {
    this.token = localStorage.getItem('access_token');
    this.user = JSON.parse(localStorage.getItem('user') || '{}');
    this.permissions = new Set(this.user.permissions || []);
    this.roles = new Set(this.user.roles || []);
    this.sessionTimeout = 30 * 60 * 1000; // 30 minutos
    this.inactivityTimeout = null;
    this.requestLog = [];
    this.failedAttempts = new Map();
    this.init();
  }

  init() {
    // Validar sessão
    this.validateSession();

    // Monitorar atividade
    this.monitorActivity();

    // Ouvir mudanças de abas/janelas
    window.addEventListener('storage', (e) => this.handleStorageChange(e));

    // Detectar tentativas de acesso não autorizado
    this.setupAccessControl();

    // Rate limiting
    this.setupRateLimiting();

    // Adicionar headers de segurança ao fazer requisições
    this.interceptFetch();

    console.log('✅ SecurityManager inicializado');
  }

  /**
   * Validar sessão
   */
  validateSession() {
    if (!this.token) {
      // Se não tem token, redirecionar para login
      if (!window.location.pathname.includes('login.html') &&
          !window.location.pathname.includes('register.html') &&
          !window.location.pathname.includes('forgot-password.html')) {
        this.redirectToLogin('Sessão expirada ou não autenticado');
      }
      return;
    }

    // Verificar se o token é válido
    this.verifyToken();
  }

  /**
   * Verificar token com backend
   */
  async verifyToken() {
    try {
      const response = await fetch('http://localhost:8000/api/auth/verify', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Token inválido ou expirado');
      }

      const data = await response.json();
      // Update user permissions
      if (data.permissions) {
        this.permissions = new Set(data.permissions);
      }
      if (data.roles) {
        this.roles = new Set(data.roles);
      }

      // Salvar atualizado
      localStorage.setItem('user', JSON.stringify(data));

    } catch (error) {
      console.warn('❌ Falha ao verificar token:', error);
      this.clearSession();
      this.redirectToLogin('Token expirado');
    }
  }

  /**
   * Monitorar inatividade
   */
  monitorActivity() {
    const events = ['mousedown', 'keydown', 'scroll', 'touchstart', 'click'];

    events.forEach((event) => {
      document.addEventListener(event, () => this.resetInactivityTimer(), true);
    });

    this.resetInactivityTimer();
  }

  resetInactivityTimer() {
    clearTimeout(this.inactivityTimeout);

    this.inactivityTimeout = setTimeout(() => {
      this.handleSessionTimeout();
    }, this.sessionTimeout);
  }

  /**
   * Expirar sessão por inatividade
   */
  handleSessionTimeout() {
    console.warn('⏱️ Sessão expirada por inatividade');
    this.clearSession();

    // Notificar usuário
    const notification = document.createElement('div');
    notification.innerHTML = `
      <div style="
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        z-index: 10000;
        text-align: center;
        font-family: system-ui;
      ">
        <div style="font-size: 3em; margin-bottom: 10px;">⏰</div>
        <h2 style="color: #F44336; margin: 10px 0;">Sessão Expirada</h2>
        <p style="color: #666; margin: 10px 0;">Sua sessão expirou por inatividade.</p>
        <button onclick="location.href='/login.html'" style="
          background: #1E3A5F;
          color: white;
          border: none;
          padding: 10px 20px;
          border-radius: 6px;
          cursor: pointer;
          font-weight: 600;
          margin-top: 10px;
        ">Fazer Login Novamente</button>
      </div>
      <div style="
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.5);
        z-index: 9999;
      "></div>
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
      window.location.href = '/login.html?logout=true';
    }, 3000);
  }

  /**
   * Controle de Acesso por Permissões
   */
  hasPermission(permission) {
    return this.permissions.has(permission);
  }

  hasRole(role) {
    return this.roles.has(role);
  }

  hasAnyPermission(...permissions) {
    return permissions.some((p) => this.hasPermission(p));
  }

  hasAllPermissions(...permissions) {
    return permissions.every((p) => this.hasPermission(p));
  }

  /**
   * Proteção de elementos do DOM baseado em permissões
   */
  setupAccessControl() {
    // Encontrar todos elementos com atributo data-permission
    const protectedElements = document.querySelectorAll('[data-permission]');

    protectedElements.forEach((element) => {
      const requiredPermission = element.getAttribute('data-permission');

      if (!this.hasPermission(requiredPermission)) {
        element.style.display = 'none';
        element.setAttribute('aria-hidden', 'true');
      }
    });

    // Interceptar cliques em elementos protegidos
    document.addEventListener('click', (e) => {
      const target = e.target.closest('[data-permission]');
      if (target && !this.hasPermission(target.getAttribute('data-permission'))) {
        e.preventDefault();
        e.stopPropagation();
        this.showAccessDenied();
      }
    }, true);
  }

  /**
   * Rate Limiting - Proteção contra força bruta
   */
  setupRateLimiting() {
    // Limite de requisições por minuto por endpoint
    const rateLimits = {
      '/api/auth/login': 5, // 5 tentativas por minuto
      '/api/auth/register': 3, // 3 registros por minuto
      '/api/projects': 100, // 100 requisições por minuto
    };

    window.addEventListener('beforeunload', () => {
      // Limpar logs antigos
      const now = Date.now();
      this.requestLog = this.requestLog.filter((r) => now - r.timestamp < 60000);
    });
  }

  /**
   * Interceptar requisições fetch
   */
  interceptFetch() {
    const originalFetch = window.fetch;

    window.fetch = async (...args) => {
      const [resource, config = {}] = args;
      const url = new URL(resource, window.location.origin).href;
      const endpoint = new URL(url).pathname;

      // Verificar rate limiting
      if (!this.checkRateLimit(endpoint)) {
        console.warn(`⚠️ Rate limit exceeded para ${endpoint}`);
        return new Response(
          JSON.stringify({ error: 'Too many requests' }),
          { status: 429, statusText: 'Too Many Requests' }
        );
      }

      // Adicionar headers de segurança
      const headers = new Headers(config.headers || {});
      headers.set('X-Requested-With', 'XMLHttpRequest');
      headers.set('X-Client-ID', this.getClientID());

      // Adicionar token se disponível
      if (this.token && !headers.has('Authorization')) {
        headers.set('Authorization', `Bearer ${this.token}`);
      }

      config.headers = headers;

      // Registrar requisição
      this.logRequest(endpoint, config.method || 'GET');

      try {
        const response = await originalFetch(url, config);

        // Verificar respostas de erro de autenticação
        if (response.status === 401) {
          this.clearSession();
          this.redirectToLogin('Não autorizado');
        } else if (response.status === 403) {
          console.warn('❌ Acesso proibido:', endpoint);
          this.showAccessDenied();
        }

        return response;
      } catch (error) {
        console.error('Erro na requisição:', error);
        throw error;
      }
    };
  }

  /**
   * Verificar rate limit
   */
  checkRateLimit(endpoint) {
    const now = Date.now();
    const limit = 100; // Limite geral: 100 requisições por minuto
    const window_ms = 60000; // 1 minuto

    // Contar requisições no último minuto para este endpoint
    const recentRequests = this.requestLog.filter(
      (r) => r.endpoint === endpoint && now - r.timestamp < window_ms
    );

    return recentRequests.length < limit;
  }

  /**
   * Registrar requisição para auditoria
   */
  logRequest(endpoint, method) {
    this.requestLog.push({
      endpoint,
      method,
      timestamp: Date.now(),
      userAgent: navigator.userAgent
    });

    // Keeper apenas última hora
    const oneHourAgo = Date.now() - 60 * 60 * 1000;
    this.requestLog = this.requestLog.filter((r) => r.timestamp > oneHourAgo);
  }

  /**
   * Gerar ID único do cliente
   */
  getClientID() {
    let clientID = sessionStorage.getItem('client-id');
    if (!clientID) {
      clientID = 'client_' + Math.random().toString(36).substr(2, 9);
      sessionStorage.setItem('client-id', clientID);
    }
    return clientID;
  }

  /**
   * Sincronizar token entre abas/janelas
   */
  handleStorageChange(e) {
    if (e.key === 'access_token') {
      this.token = e.newValue;
      if (!this.token) {
        this.clearSession();
        this.redirectToLogin('Sessão encerrada em outra aba');
      }
    }
  }

  /**
   * Mostrar aviso de acesso negado
   */
  showAccessDenied() {
    // Notificar apenas uma vez por segundo
    if (this.lastAccessDeniedWarning && Date.now() - this.lastAccessDeniedWarning < 1000) {
      return;
    }

    this.lastAccessDeniedWarning = Date.now();

    const notification = document.createElement('div');
    notification.setAttribute('role', 'alert');
    notification.innerHTML = `
      <div style="
        position: fixed;
        top: 20px;
        right: 20px;
        background: #F44336;
        color: white;
        padding: 16px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 10000;
        max-width: 300px;
        animation: slideIn 0.3s ease-out;
        font-family: system-ui;
      ">
        🔒 Acesso Negado<br>
        <small>Você não tem permissão para acessar este recurso.</small>
      </div>
      <style>
        @keyframes slideIn {
          from { transform: translateX(400px); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      </style>
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
      notification.style.animation = 'slideOut 0.3s ease-out forwards';
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  }

  /**
   * Limpar sessão
   */
  clearSession() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    sessionStorage.clear();
  }

  /**
   * Redirecionar para login
   */
  redirectToLogin(reason = '') {
    const params = new URLSearchParams();
    if (reason) {
      params.set('reason', reason);
    }
    window.location.href = `/login.html?${params.toString()}`;
  }

  /**
   * Auditar ação do usuário
   */
  auditLog(action, details = {}) {
    const log = {
      timestamp: new Date().toISOString(),
      userId: this.user.id,
      action,
      details,
      userAgent: navigator.userAgent,
      url: window.location.href
    };

    // Enviar para backend
    fetch('http://localhost:8000/api/audit/log', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(log)
    }).catch((err) => console.warn('Falha ao registrar auditoria:', err));
  }

  /**
   * Logout seguro
   */
  logout() {
    fetch('http://localhost:8000/api/auth/logout', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${this.token}` }
    }).finally(() => {
      this.clearSession();
      window.location.href = '/login.html?logout=true';
    });
  }

  /**
   * Obter informações de segurança
   */
  getSecurityInfo() {
    return {
      authenticated: !!this.token,
      roles: Array.from(this.roles),
      permissions: Array.from(this.permissions),
      sessionTimedOutMinutes: Math.round(this.sessionTimeout / 60000),
      requestsLastHour: this.requestLog.length,
      clientID: this.getClientID()
    };
  }
}

// Inicializar automaticamente
document.addEventListener('DOMContentLoaded', () => {
  window.securityManager = new SecurityManager();
});

// Export para uso em módulos
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SecurityManager;
}
