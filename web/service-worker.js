// Service Worker para PWA - Gerenciador de Projetos de Engenharia
const CACHE_NAME = 'gpe-v1.0.0';
const STATIC_ASSETS = [
  '/',
  '/login.html',
  '/index.html',
  '/change-password.html',
  '/forgot-password.html',
  '/register.html',
  '/profile.html',
  '/notifications.html',
  '/chat.html',
  '/styles/styles.css',
  '/styles.css',
  '/js/app.js',
  '/api-client.js',
  '/app.js'
];

// Instalar Service Worker
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Instalando...');
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[Service Worker] Cache aberto');
      return cache.addAll(STATIC_ASSETS).catch((err) => {
        console.warn('[Service Worker] Algunos assets no pudieron ser cacheados:', err);
        // Continuar mesmo se alguns não conseguirem cachear
        return Promise.resolve();
      });
    })
  );
  self.skipWaiting();
});

// Ativar Service Worker
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Ativando...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('[Service Worker] Deletando cache antigo:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Estratégia de Fetch: Network First com fallback para Cache
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Não cachear requisições de API ou authenticated
  if (url.pathname.includes('/api/') || url.pathname.includes('/auth/')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Verificar se a resposta é válida
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }
          // Clonear resposta
          const responseToCache = response.clone();
          // Cache apenas respostas bem-sucedidas
          if (response.status === 200) {
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, responseToCache);
            });
          }
          return response;
        })
        .catch(() => {
          // Offline - tentar do cache
          return caches.match(request).then((response) => {
            return response || createOfflineResponse();
          });
        })
    );
    return;
  }

  // Para assets estáticos: Cache First
  event.respondWith(
    caches.match(request).then((response) => {
      if (response) {
        return response;
      }
      return fetch(request)
        .then((response) => {
          if (!response || response.status !== 200) {
            return response;
          }
          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, responseToCache);
          });
          return response;
        })
        .catch(() => {
          // Offline
          return createOfflineResponse();
        });
    })
  );
});

// Resposta padrão quando offline
function createOfflineResponse() {
  return new Response(
    `<!DOCTYPE html>
    <html lang="pt-BR">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Offline</title>
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          display: flex;
          justify-content: center;
          align-items: center;
          height: 100vh;
          margin: 0;
          background: linear-gradient(135deg, #1E3A5F 0%, #0F2744 100%);
          color: #fff;
        }
        .container {
          text-align: center;
          padding: 20px;
        }
        h1 { font-size: 2.5em; margin: 0 0 10px 0; }
        p { font-size: 1.1em; margin: 10px 0; }
        .icon { font-size: 4em; margin-bottom: 20px; }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="icon">📡</div>
        <h1>Você está offline</h1>
        <p>Não há conexão com a internet no momento.</p>
        <p>Os dados em cache continuam disponíveis para consulta.</p>
      </div>
    </body>
    </html>`,
    {
      headers: {
        'Content-Type': 'text/html; charset=utf-8',
        'Cache-Control': 'no-cache, no-store, must-revalidate'
      }
    }
  );
}

// Sincronização em background
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-data') {
    event.waitUntil(
      fetch('/api/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
        .then(() => console.log('[Service Worker] Sincronização concluída'))
        .catch((err) => console.error('[Service Worker] Erro de sincronização:', err))
    );
  }
});

// Notificações Push
self.addEventListener('push', (event) => {
  if (!event.data) return;

  const data = event.data.json();
  const options = {
    body: data.body || 'Você tem uma nova notificação',
    icon: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 192 192"><rect fill="%231E3A5F" width="192" height="192"/><text x="50%" y="50%" font-size="120" fill="%23fff" text-anchor="middle" dominant-baseline="central" font-weight="bold">GPE</text></svg>',
    badge: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96"><rect fill="%234CAF50" width="96" height="96"/><text x="50%" y="50%" font-size="60" fill="%23fff" text-anchor="middle" dominant-baseline="central">🔔</text></svg>',
    tag: data.id || 'notification',
    requireInteraction: data.important || false,
    data: data
  };

  event.waitUntil(self.registration.showNotification(data.title || 'Gerenciador de Projetos', options));
});

// Clique em notificação
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  const urlToOpen = event.notification.data.url || '/projects/index.html';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((windowClients) => {
      // Procura se a URL já está aberta
      for (let i = 0; i < windowClients.length; i++) {
        if (windowClients[i].url === urlToOpen) {
          return windowClients[i].focus();
        }
      }
      // Se não estiver aberta, abre uma nova janela
      return clients.openWindow(urlToOpen);
    })
  );
});

// Ativar cliente quando se reconnecta online
self.addEventListener('controllerchange', () => {
  // Notificar cliente que voltou online
  self.clients.matchAll().then((clients) => {
    clients.forEach((client) => {
      client.postMessage({ type: 'CONTROLLER_CHANGED' });
    });
  });
});

console.log('[Service Worker] Carregado com sucesso');
