/**
 * Teste de Compatibilidade Multiplataforma - Fase 5
 * Validar funcionamento em: Windows, Mac, Linux, Android, iOS
 */

class CompatibilityTester {
  constructor() {
    this.results = {
      browser: {},
      platform: navigator.platform,
      userAgent: navigator.userAgent,
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight
      },
      features: {},
      performance: {},
      connectivity: {},
      timestamp: new Date().toISOString()
    };
    this.init();
  }

  init() {
    console.log('🧪 Iniciando testes de compatibilidade...');
    this.runAllTests();
  }

  async runAllTests() {
    await Promise.all([
      this.testBrowserFeatures(),
      this.testStorage(),
      this.testServiceWorker(),
      this.testIndexedDB(),
      this.testNotifications(),
      this.testGeolocation(),
      this.testCamera(),
      this.testMicrophone(),
      this.testNetwork(),
      this.testPerformance(),
      this.testCSS(),
      this.testTouch()
    ]);

    this.generateReport();
  }

  // ============================================
  // TESTES DE RECURSOS DO NAVEGADOR
  // ============================================

  testBrowserFeatures() {
    const features = {
      serviceWorker: 'serviceWorker' in navigator,
      localStorage: this.testFeature('localStorage'),
      sessionStorage: this.testFeature('sessionStorage'),
      indexedDB: 'indexedDB' in window,
      fetch: 'fetch' in window,
      promises: 'Promise' in window,
      async: true,
      classes: true,
      proxy: 'Proxy' in window,
      proxy: 'Proxy' in window,
      webWorker: typeof Worker !== 'undefined',
      sharedArrayBuffer: typeof SharedArrayBuffer !== 'undefined',
      webAssembly: typeof WebAssembly !== 'undefined',
      vibration: 'vibrate' in navigator,
      battery: 'getBattery' in navigator,
      requestIdleCallback: 'requestIdleCallback' in window,
      intersectionObserver: 'IntersectionObserver' in window,
      mutationObserver: 'MutationObserver' in window
    };

    this.results.features.browser = features;
    console.log('✅ Browser features:', features);
  }

  testFeature(feature) {
    try {
      const test = window[feature];
      test.setItem('test', 'test');
      test.removeItem('test');
      return true;
    } catch {
      return false;
    }
  }

  // ============================================
  // TESTES DE STORAGE
  // ============================================

  testStorage() {
    const storage = {
      localStorage: this.testStorageAPI('localStorage'),
      sessionStorage: this.testStorageAPI('sessionStorage'),
      quota: this.getStorageQuota()
    };

    this.results.features.storage = storage;
    console.log('✅ Storage:', storage);
  }

  testStorageAPI(type) {
    try {
      const api = type === 'localStorage' ? window.localStorage : window.sessionStorage;
      const testKey = 'test-' + Date.now();
      api.setItem(testKey, 'test-value');
      const value = api.getItem(testKey);
      api.removeItem(testKey);
      return value === 'test-value';
    } catch {
      return false;
    }
  }

  async getStorageQuota() {
    if ('storage' in navigator && 'estimate' in navigator.storage) {
      try {
        const estimate = await navigator.storage.estimate();
        return {
          usage: Math.round(estimate.usage / 1024 / 1024) + ' MB',
          quota: Math.round(estimate.quota / 1024 / 1024) + ' MB'
        };
      } catch (err) {
        return { error: err.message };
      }
    }
    return { available: false };
  }

  // ============================================
  // TESTES DE SERVICE WORKER
  // ============================================

  async testServiceWorker() {
    const sw = {
      supported: 'serviceWorker' in navigator,
      registered: false,
      status: 'not-checked'
    };

    if (sw.supported) {
      try {
        const registrations = await navigator.serviceWorker.getRegistrations();
        sw.registered = registrations.length > 0;
        sw.status = 'active';
        sw.registrations = registrations.length;
      } catch (err) {
        sw.error = err.message;
        sw.status = 'error';
      }
    }

    this.results.features.serviceWorker = sw;
    console.log('✅ Service Worker:', sw);
  }

  // ============================================
  // TESTES DE INDEXEDDB
  // ============================================

  async testIndexedDB() {
    const indexeddb = {
      supported: 'indexedDB' in window,
      functional: false
    };

    if (indexeddb.supported) {
      try {
        const request = indexedDB.open('test-db', 1);
        
        request.onupgradeneeded = (event) => {
          const db = event.target.result;
          if (!db.objectStoreNames.contains('test')) {
            db.createObjectStore('test');
          }
        };

        request.onsuccess = () => {
          indexeddb.functional = true;
          request.result.close();
        };

        request.onerror = () => {
          indexeddb.error = 'Falha ao abrir IndexedDB';
        };
      } catch (err) {
        indexeddb.error = err.message;
      }
    }

    this.results.features.indexedDB = indexeddb;
    console.log('✅ IndexedDB:', indexeddb);
  }

  // ============================================
  // TESTES DE NOTIFICAÇÕES
  // ============================================

  testNotifications() {
    const notifications = {
      supported: 'Notification' in window,
      permission: Notification?.permission || 'denied'
    };

    this.results.features.notifications = notifications;
    console.log('✅ Notifications:', notifications);
  }

  // ============================================
  // TESTES DE GEOLOCALIZAÇÃO
  // ============================================

  testGeolocation() {
    const geolocation = {
      supported: 'geolocation' in navigator
    };

    if (geolocation.supported) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          geolocation.functional = true;
          geolocation.coords = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          };
        },
        (error) => {
          geolocation.error = error.message;
          geolocation.functional = false;
        },
        { timeout: 5000 }
      );
    }

    this.results.features.geolocation = geolocation;
    console.log('✅ Geolocation:', geolocation);
  }

  // ============================================
  // TESTES DE CÂMERA
  // ============================================

  async testCamera() {
    const camera = {
      supported: !!navigator.mediaDevices?.getUserMedia
    };

    if (camera.supported) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 100 } });
        camera.functional = true;
        stream.getTracks().forEach((track) => track.stop());
      } catch (err) {
        camera.error = err.name;
        camera.functional = false;
      }
    }

    this.results.features.camera = camera;
    console.log('✅ Camera:', camera);
  }

  // ============================================
  // TESTES DE MICROFONE
  // ============================================

  async testMicrophone() {
    const microphone = {
      supported: !!navigator.mediaDevices?.getUserMedia
    };

    if (microphone.supported) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        microphone.functional = true;
        stream.getTracks().forEach((track) => track.stop());
      } catch (err) {
        microphone.error = err.name;
        microphone.functional = false;
      }
    }

    this.results.features.microphone = microphone;
    console.log('✅ Microphone:', microphone);
  }

  // ============================================
  // TESTES DE REDE
  // ============================================

  testNetwork() {
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    const network = {
      online: navigator.onLine,
      effectiveType: connection?.effectiveType || 'unknown',
      downlink: connection?.downlink || 'unknown',
      rtt: connection?.rtt || 'unknown',
      saveData: connection?.saveData || false
    };

    this.results.connectivity = network;
    console.log('✅ Network:', network);
  }

  // ============================================
  // TESTES DE PERFORMANCE
  // ============================================

  testPerformance() {
    const performance = {
      navigation: performance.navigation.type,
      timing: {
        domContentLoaded: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
        loadComplete: performance.timing.loadEventEnd - performance.timing.navigationStart,
        domInteractive: performance.timing.domInteractive - performance.timing.navigationStart
      }
    };

    // Testes de renderização
    const start = performance.now();
    for (let i = 0; i < 1000; i++) {
      document.createElement('div');
    }
    performance.domCreation = performance.now() - start;

    this.results.performance = performance;
    console.log('✅ Performance:', performance);
  }

  // ============================================
  // TESTES DE CSS
  // ============================================

  testCSS() {
    const css = {
      css3: this.checkCSSProperty('transform'),
      flexbox: this.checkCSSProperty('display', 'flex'),
      grid: this.checkCSSProperty('display', 'grid'),
      customProperties: this.checkCSSProperty('--test'),
      aspectRatio: this.checkCSSProperty('aspect-ratio'),
      clamp: this.supportsClamp(),
      mediaQueries: window.matchMedia('(prefers-color-scheme: dark)').matches !== undefined
    };

    this.results.features.css = css;
    console.log('✅ CSS:', css);
  }

  checkCSSProperty(property, value = '') {
    const element = document.createElement('div');
    if (value) {
      element.style[property] = value;
      return element.style[property] !== '';
    } else {
      element.style[property] = 'test';
      return element.style[property] !== '';
    }
  }

  supportsClamp() {
    const element = document.createElement('div');
    element.style.width = 'clamp(10px, 50%, 100px)';
    return element.style.width !== '';
  }

  // ============================================
  // TESTES DE TOUCH
  // ============================================

  testTouch() {
    const touch = {
      supported: 'ontouchstart' in window || navigator.maxTouchPoints > 0,
      maxTouchPoints: navigator.maxTouchPoints || 0,
      pointerEvents: 'PointerEvent' in window,
      touchAction: this.checkCSSProperty('touch-action')
    };

    this.results.features.touch = touch;
    console.log('✅ Touch:', touch);
  }

  // ============================================
  // GERAÇÃO DE RELATÓRIO
  // ============================================

  generateReport() {
    console.log('\n==============================================');
    console.log('📊 RELATÓRIO DE COMPATIBILIDADE MULTIPLATAFORMA');
    console.log('==============================================\n');

    console.table({
      'Navegador': this.getBrowserInfo(),
      'Plataforma': this.results.platform,
      'Viewport': `${this.results.viewport.width}x${this.results.viewport.height}`,
      'Online': this.results.connectivity.online ? '✅' : '❌',
      'Tipo Conexão': this.results.connectivity.effectiveType || 'N/A',
      'Service Worker': this.results.features.serviceWorker.supported ? '✅' : '❌',
      'IndexedDB': this.results.features.indexedDB.supported ? '✅' : '❌',
      'Notificações': this.results.features.notifications.supported ? '✅' : '❌',
      'Geolocalização': this.results.features.geolocation.supported ? '✅' : '❌',
      'Câmera': this.results.features.camera.supported ? '✅' : '❌',
      'Microfone': this.results.features.microphone.supported ? '✅' : '❌',
      'Dark Mode': document.documentElement.style.colorScheme === 'dark' ? '✅' : '⚪',
      'Touch': this.results.features.touch.supported ? '✅' : '❌'
    });

    this.saveReport();
  }

  getBrowserInfo() {
    const ua = navigator.userAgent;
    if (ua.includes('Chrome') && !ua.includes('Chromium')) return 'Chrome';
    if (ua.includes('Safari')) return 'Safari';
    if (ua.includes('Firefox')) return 'Firefox';
    if (ua.includes('Edge')) return 'Edge';
    if (ua.includes('Opera')) return 'Opera';
    return 'Desconhecido';
  }

  async saveReport() {
    try {
      const response = await fetch('http://localhost:8000/api/compatibility/report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(this.results)
      });

      if (response.ok) {
        console.log('✅ Relatório salvo com sucesso');
      }
    } catch (err) {
      console.warn('Não foi possível salvar o relatório:', err);
    }
  }

  getResults() {
    return this.results;
  }

  printJSON() {
    console.log(JSON.stringify(this.results, null, 2));
  }
}

// Inicializar quando documento carrega
document.addEventListener('DOMContentLoaded', () => {
  const tester = new CompatibilityTester();
  window.compatibilityTester = tester;

  // Mostrar botão para usuários avançados
  if (localStorage.getItem('dev-mode')) {
    const btn = document.createElement('button');
    btn.textContent = '🧪 Teste de Compatibilidade';
    btn.onclick = () => console.log(tester.getResults());
    btn.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      padding: 10px 15px;
      background: #2196F3;
      color: white;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      z-index: 10000;
    `;
    document.body.appendChild(btn);
  }
});
