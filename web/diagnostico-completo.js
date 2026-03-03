/**
 * 🧪 TESTE DE DIAGNÓSTICO - Dashboard
 * Verifica todas as APIs que o dashboard usa
 */

console.log('🔍 Iniciando diagnóstico do sistema...\n');

// 1. Verificar token
const token = localStorage.getItem('access_token');
console.log(`📌 Token armazenado:`, token ? `✅ SIM (${token.substring(0, 20)}...)` : '❌ NÃO');

// 2. Verificar user
const user = JSON.parse(localStorage.getItem('user') || '{}');
console.log(`👤 Usuário armazenado:`, user.email ? `✅ ${user.email}` : '❌ NÃO');

// 3. Verificar Service Worker
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations().then(regs => {
    console.log(`🔧 Service Worker:`, regs.length > 0 ? `✅ Registrado (${regs.length})` : '❌ NÃO');
  });
}

// 4. Verificar localStorage
console.log(`💾 Storage disponível:`, localStorage ? '✅ SIM' : '❌ NÃO');
console.log(`💾 Itens em localStorage:`, localStorage.length);

// 5. Testar Fetch da API
async function testAPIs() {
  console.log('\n📡 Testando APIs...\n');
  
  const baseUrl = 'http://localhost:8000';
  const tests = [
    { name: 'Health Check', method: 'GET', url: '/health' },
    { name: 'Listar Projetos', method: 'GET', url: '/api/projects', needAuth: true },
    { name: 'Dashboard Data', method: 'GET', url: '/api/dashboard', needAuth: true },
    { name: 'Tarefas', method: 'GET', url: '/api/tasks', needAuth: true },
    { name: 'Usuário Atual', method: 'GET', url: '/api/auth/me', needAuth: true },
  ];
  
  for (const test of tests) {
    try {
      const headers = {
        'Content-Type': 'application/json'
      };
      
      if (test.needAuth && token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch(baseUrl + test.url, { 
        method: test.method,
        headers 
      });
      
      const statusColor = response.ok ? '✅' : response.status === 401 ? '🔐' : '❌';
      console.log(`${statusColor} ${test.name}: ${response.status} ${response.statusText}`);
      
      if (!response.ok && response.status !== 401) {
        const data = await response.text();
        console.log(`   └─ Resposta: ${data.substring(0, 100)}`);
      }
    } catch (error) {
      console.log(`❌ ${test.name}: ${error.message}`);
    }
  }
}

// 6. Testar API com credenciais viáveis
async function testLoginDirecto() {
  console.log('\n🔐 Testando login direto...\n');
  
  const credentials = {
    email: 'vicentedesouza762@gmail.com',
    password: 'Admin@2026'
  };
  
  try {
    const response = await fetch('http://localhost:8000/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials)
    });
    
    console.log(`Status: ${response.status}`);
    const data = await response.json();
    
    if (response.ok) {
      console.log('✅ Login bem-sucedido!');
      console.log(`Token: ${data.access_token?.substring(0, 30)}...`);
    } else {
      console.log('❌ Login falhou');
      console.log('Resposta:', data);
    }
  } catch (error) {
    console.log(`❌ Erro no login: ${error.message}`);
  }
}

// 7. Testar Security Manager
async function testSecurityManager() {
  console.log('\n🔒 TestSecurity Manager...\n');
  
  if (window.securityManager) {
    console.log('✅ SecurityManager carregado');
    const info = window.securityManager.getSecurityInfo();
    console.log('Info de segurança:', info);
  } else {
    console.log('❌ SecurityManager NÃO carregado');
  }
}

// 8. Testar Compatibilidade
async function testCompat() {
  console.log('\n🧪 Teste Compatibilidade...\n');
  
  if (window.compatibilityTester) {
    console.log('✅ Compatibility Tester carregado');
    const results = window.compatibilityTester.getResults();
    console.log('Dispositivo:', results.platform);
    console.log('Viewport:', results.viewport);
    console.log('Online:', results.connectivity.online);
  } else {
    console.log('❌ Compatibility Tester NÃO carregado');
  }
}

// Executar todos
setTimeout(async () => {
  await testAPIs();
  await testLoginDirecto();
  await testSecurityManager();
  await testCompat();
  
  console.log('\n' + '='.repeat(70));
  console.log('✅ DIAGNÓSTICO CONCLUÍDO');
  console.log('='.repeat(70));
}, 1000);
