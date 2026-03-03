/**
 * PWA Installer - Gerenciar instalação do aplicativo
 * Compatível com Windows, Mac, Linux, Android, iOS
 */

class PWAInstaller {
  constructor() {
    this.deferredPrompt = null;
    this.isInstalled = false;
    this.init();
  }

  async init() {
    // Verificar se o app já está instalado
    this.isInstalled = await this.checkInstalled();

    // Event: antes de exibir o prompt de instalação
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      this.deferredPrompt = e;
      this.showInstallPrompt();
    });

    // Event: app foi instalado
    window.addEventListener('appinstalled', () => {
      console.log('✅ PWA instalado com sucesso');
      this.isInstalled = true;
      this.hideInstallPrompt();
      this.trackEvent('pwa_installed');
    });

    // Registrar Service Worker
    this.registerServiceWorker();

    // Detecção de Online/Offline
    window.addEventListener('online', () => this.handleOnline());
    window.addEventListener('offline', () => this.handleOffline());
  }

  async registerServiceWorker() {
    if (!('serviceWorker' in navigator)) {
      console.warn('Service Workers não suportados');
      return;
    }

    try {
      const registration = await navigator.serviceWorker.register('/service-worker.js', {
        scope: '/'
      });
      console.log('✅ Service Worker registrado:', registration);

      // Verificar atualizações
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;
        newWorker.addEventListener('statechange', () => {
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
            this.notifyUpdate();
          }
        });
      });

      // Ouvir mensagens do Service Worker
      navigator.serviceWorker.addEventListener('message', (event) => {
        if (event.data.type === 'CONTROLLER_CHANGED') {
          console.log('✅ Reconectado online');
        }
      });

    } catch (err) {
      console.error('❌ Erro ao registrar Service Worker:', err);
    }
  }

  showInstallPrompt() {
    // Criar banner de instalação customizado
    const banner = document.createElement('div');
    banner.id = 'pwa-install-banner';
    banner.innerHTML = `
      <div style="
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(135deg, #1E3A5F 0%, #0F2744 100%);
        color: white;
        padding: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.3);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        z-index: 10000;
        animation: slideUp 0.3s ease-out;
      ">
        <div style="flex: 1;">
          <div style="font-weight: 600; margin-bottom: 4px;">📱 Instalar Gerenciador de Projetos</div>
          <div style="font-size: 0.9em; opacity: 0.9;">Acesse como um app nativo em seu dispositivo</div>
        </div>
        <div style="display: flex; gap: 8px;">
          <button id="pwa-install-btn" style="
            background: #4CAF50;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
          ">Instalar</button>
          <button id="pwa-close-btn" style="
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.2s;
          ">Depois</button>
        </div>
      </div>
      <style>
        @keyframes slideUp {
          from { transform: translateY(100%); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }
        #pwa-install-banner button:hover {
          opacity: 0.9;
        }
      </style>
    `;

    document.body.appendChild(banner);

    document.getElementById('pwa-install-btn').addEventListener('click', () => {
      this.installApp();
    });

    document.getElementById('pwa-close-btn').addEventListener('click', () => {
      this.hideInstallPrompt();
    });
  }

  hideInstallPrompt() {
    const banner = document.getElementById('pwa-install-banner');
    if (banner) {
      banner.style.animation = 'slideDown 0.3s ease-out forwards';
      setTimeout(() => banner.remove(), 300);
    }
  }

  async installApp() {
    if (!this.deferredPrompt) return;

    this.deferredPrompt.prompt();
    const choiceResult = await this.deferredPrompt.userChoice;

    if (choiceResult.outcome === 'accepted') {
      console.log('✅ Usuário aceitou instalar o PWA');
      this.trackEvent('pwa_install_accepted');
    } else {
      console.log('❌ Usuário rejeitou instalar o PWA');
      this.trackEvent('pwa_install_rejected');
    }

    this.deferredPrompt = null;
  }

  async checkInstalled() {
    // PWA instalado em standalone
    if (window.navigator.standalone === true) {
      return true;
    }

    // Detectar em display-mode
    if (window.matchMedia('(display-mode: standalone)').matches) {
      return true;
    }

    // Detectar em fullscreen
    if (window.matchMedia('(display-mode: fullscreen)').matches) {
      return true;
    }

    return false;
  }

  handleOnline() {
    console.log('📡 Sistema online');
    const offlineIndicator = document.getElementById('offline-indicator');
    if (offlineIndicator) {
      offlineIndicator.style.display = 'none';
    }
    // Sincronizar dados
    this.syncData();
  }

  handleOffline() {
    console.log('📡 Sistema offline');
    const offlineIndicator = document.getElementById('offline-indicator');
    if (!offlineIndicator) {
      const indicator = document.createElement('div');
      indicator.id = 'offline-indicator';
      indicator.innerHTML = `
        <div style="
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          background: #FF9800;
          color: white;
          padding: 10px;
          text-align: center;
          font-weight: 600;
          z-index: 9999;
        ">
          ⚠️ Você está offline - Os dados em cache estão disponíveis
        </div>
      `;
      document.body.insertBefore(indicator, document.body.firstChild);
      document.body.style.paddingTop = '40px';
    } else {
      offlineIndicator.style.display = 'block';
    }
  }

  async syncData() {
    if (!navigator.serviceWorker.controller) return;

    try {
      const response = await fetch('/api/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ timestamp: new Date().toISOString() })
      });

      if (response.ok) {
        console.log('✅ Dados sincronizados');
      }
    } catch (err) {
      console.warn('Sincronização falhada:', err);
    }
  }

  notifyUpdate() {
    const notification = document.createElement('div');
    notification.innerHTML = `
      <div style="
        position: fixed;
        bottom: 80px;
        right: 20px;
        background: #2196F3;
        color: white;
        padding: 16px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        max-width: 300px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        z-index: 9999;
      ">
        <div style="font-weight: 600; margin-bottom: 8px;">🔄 Atualização Disponível</div>
        <p style="margin: 0 0 12px 0; font-size: 0.9em;">Uma nova versão está disponível.</p>
        <button onclick="location.reload()" style="
          background: white;
          color: #2196F3;
          border: none;
          padding: 6px 12px;
          border-radius: 4px;
          font-weight: 600;
          cursor: pointer;
        ">Atualizar Agora</button>
      </div>
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
      notification.style.opacity = '0';
      notification.style.transition = 'opacity 0.3s';
      setTimeout(() => notification.remove(), 300);
    }, 10000);
  }

  trackEvent(eventName) {
    if (window.gtag) {
      gtag('event', eventName);
    }
    console.log(`📊 Event tracked: ${eventName}`);
  }

  getInfo() {
    return {
      installed: this.isInstalled,
      standalone: window.navigator.standalone === true,
      online: navigator.onLine,
      userAgent: navigator.userAgent,
      platform: navigator.platform
    };
  }
}

// Inicializar automaticamente
document.addEventListener('DOMContentLoaded', () => {
  window.pwaInstaller = new PWAInstaller();
});
