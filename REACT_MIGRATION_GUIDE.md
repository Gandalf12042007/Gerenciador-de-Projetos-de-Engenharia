# ⚛️ Guia de Migração para React

**Transformar HTML+JS vanilla em aplicação React moderna**

---

## 📋 **Decisão: Por que React?**

| Aspecto | HTML+JS Vanilla | React |
|---------|-----------------|-------|
| **Componentes Reutilizáveis** | ❌ Manual | ✅ Automático |
| **Estado Gerenciado** | ❌ Complexo | ✅ Simples (hooks) |
| **Performance** | ⚠️ Lenta | ✅ Otimizada |
| **Desenvolvimento** | ⚠️ Lento | ✅ Rápido |
| **Testing** | ⚠️ Difícil | ✅ Fácil |
| **Deploy** | ✅ Simples | ✅ Simples |
| **Comunidade** | ❌ Pequena | ✅ Enorme |

**Decisão: Implementar AMBAS (fallback)**
- `/web` → HTML+JS (atual, mantém funcionando)
- `/web-react` → React (novo, quando pronto)

---

## 🚀 **Passo 1: Criar Projeto React**

```bash
# Nível workspace (raiz)
npx create-react-app web-react

# Isso cria:
# web-react/
# ├── public/
# ├── src/
# │   ├── App.js
# │   ├── App.css
# │   ├── index.js
# │   └── index.css
# ├── package.json
# └── ...

# Entrar na pasta
cd web-react

# Instalar dependências extras
npm install axios react-router-dom zustand
npm install -D tailwindcss postcss autoprefixer
```

---

## 📦 **Passo 2: Estrutura de Pastas Rekomendada**

```
web-react/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/          # Componentes reutilizáveis
│   │   ├── Header.js
│   │   ├── Sidebar.js
│   │   ├── LoadingSpinner.js
│   │   └── Alert.js
│   ├── pages/               # Páginas (rotas)
│   │   ├── LoginPage.js
│   │   ├── DashboardPage.js
│   │   ├── ProjetosPage.js
│   │   ├── TarefasPage.js
│   │   └── PaginaNaoEncontrada.js
│   ├── styles/              # CSS global
│   │   ├── globals.css
│   │   ├── variables.css
│   │   └── theme.css
│   ├── api/                 # Communicação com backend
│   │   ├── apiClient.js     # Reutilizar do HTML+JS
│   │   └── endpoints.js
│   ├── store/               # Estado global (Zustand)
│   │   ├── authStore.js
│   │   ├── projetosStore.js
│   │   └── uiStore.js
│   ├── utils/               # Funções auxiliares
│   │   ├── dateFormatter.js
│   │   ├── validators.js
│   │   └── constants.js
│   ├── App.js               # Componente raiz
│   ├── App.css              # Estilos principais
│   └── index.js             # Entry point
├── package.json
└── .env.local
```

---

## 🔧 **Passo 3: Configuração Inicial**

### .env.local

```env
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_API_TIMEOUT=30000
REACT_APP_ENVIRONMENT=development
```

### src/api/apiClient.js (Adaptar do HTML+JS)

```javascript
// Copiar lógica do web/api-client.js e adaptar para React

class ApiClient {
  constructor(baseURL = process.env.REACT_APP_API_URL) {
    this.baseURL = baseURL;
    this.timeout = parseInt(process.env.REACT_APP_API_TIMEOUT) || 30000;
  }

  async request(method, endpoint, data = null, token = null) {
    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json'
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const options = {
      method,
      headers,
      timeout: this.timeout
    };

    if (data && ['POST', 'PUT', 'PATCH'].includes(method)) {
      options.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(url, options);
      
      if (response.status === 401) {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Métodos de autenticação
  auth = {
    login: (email, password) => 
      this.request('POST', '/auth/login', { email, password }),
    
    register: (nome, email, password) =>
      this.request('POST', '/auth/register', { nome, email, password })
  };

  // Métodos de projetos
  projetos = {
    listar: (token) => 
      this.request('GET', '/projetos/', null, token),
    
    criar: (data, token) =>
      this.request('POST', '/projetos/', data, token),
    
    atualizar: (id, data, token) =>
      this.request('PUT', `/projetos/${id}`, data, token),
    
    deletar: (id, token) =>
      this.request('DELETE', `/projetos/${id}`, null, token)
  };

  // Adicionar demais métodos conforme necessário...
}

export default new ApiClient();
```

---

## 🎣 **Passo 4: Estado Global com Zustand**

### src/store/authStore.js

```javascript
import create from 'zustand';
import api from '../api/apiClient';

export const useAuthStore = create((set) => ({
  // Estado
  user: null,
  token: localStorage.getItem('token') || null,
  loading: false,
  error: null,

  // Ações
  login: async (email, password) => {
    set({ loading: true, error: null });
    try {
      const response = await api.auth.login(email, password);
      const { access_token, user_id, nome, email: userEmail, role } = response;

      localStorage.setItem('token', access_token);
      
      set({
        user: { user_id, nome, email: userEmail, role },
        token: access_token,
        loading: false
      });

      return true;
    } catch (error) {
      set({ 
        error: error.message,
        loading: false 
      });
      return false;
    }
  },

  logout: () => {
    localStorage.removeItem('token');
    set({ 
      user: null, 
      token: null 
    });
  },

  setUser: (user) => set({ user }),
  setError: (error) => set({ error })
}));
```

### src/store/projetosStore.js

```javascript
import create from 'zustand';
import api from '../api/apiClient';
import { useAuthStore } from './authStore';

export const useProjetosStore = create((set, get) => ({
  // Estado
  projetos: [],
  loading: false,
  error: null,
  filtroStatus: 'todos',

  // Ações
  fetchProjetos: async () => {
    set({ loading: true });
    const token = useAuthStore.getState().token;
    
    try {
      const data = await api.projetos.listar(token);
      set({ projetos: data, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  criarProjeto: async (nomeProjeto) => {
    const token = useAuthStore.getState().token;
    try {
      const novoProjeto = await api.projetos.criar(
        { nome: nomeProjeto, status: 'em_planejamento' },
        token
      );
      set((state) => ({
        projetos: [...state.projetos, novoProjeto]
      }));
      return novoProjeto;
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },

  deletarProjeto: async (id) => {
    const token = useAuthStore.getState().token;
    try {
      await api.projetos.deletar(id, token);
      set((state) => ({
        projetos: state.projetos.filter(p => p.id !== id)
      }));
    } catch (error) {
      set({ error: error.message });
      throw error;
    }
  },

  setFiltroStatus: (status) => set({ filtroStatus: status })
}));
```

---

## 🎨 **Passo 5: Componentes Principais**

### src/components/Header.js

```javascript
import React from 'react';
import { useAuthStore } from '../store/authStore';
import '../styles/components/header.css';

function Header() {
  const { user, logout } = useAuthStore();

  return (
    <header className="header">
      <div className="header-content">
        <h1>Gerenciador de Projetos</h1>
        <div className="user-menu">
          <span>Olá, {user?.nome}!</span>
          <button onClick={logout}>Logout</button>
        </div>
      </div>
    </header>
  );
}

export default Header;
```

### src/pages/LoginPage.js

```javascript
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import '../styles/pages/login.css';

function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();
  const { login, loading, error } = useAuthStore();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const success = await login(email, password);
    
    if (success) {
      navigate('/dashboard');
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h2>Login</h2>
        
        {error && <div className="alert alert-error">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          
          <input
            type="password"
            placeholder="Senha"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          
          <button type="submit" disabled={loading}>
            {loading ? 'Entrando...' : 'Entrar'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default LoginPage;
```

### src/pages/DashboardPage.js

```javascript
import React, { useEffect } from 'react';
import { useProjetosStore } from '../store/projetosStore';
import Header from '../components/Header';
import LoadingSpinner from '../components/LoadingSpinner';
import '../styles/pages/dashboard.css';

function DashboardPage() {
  const { projetos, loading, error, fetchProjetos } = useProjetosStore();

  useEffect(() => {
    fetchProjetos();
  }, []);

  if (loading) return <LoadingSpinner />;

  return (
    <>
      <Header />
      <div className="dashboard">
        <h1>Meus Projetos</h1>
        
        {error && <div className="alert alert-error">{error}</div>}
        
        <div className="projetos-grid">
          {projetos.map(projeto => (
            <div key={projeto.id} className="projeto-card">
              <h3>{projeto.nome}</h3>
              <p>{projeto.descricao}</p>
              <span className={`badge badge-${projeto.status}`}>
                {projeto.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

export default DashboardPage;
```

---

## 🛣️ **Passo 6: Roteamento (React Router)**

### src/App.js

```javascript
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';

// Pages
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import ProjetosPage from './pages/ProjetosPage';
import NotFoundPage from './pages/NotFoundPage';

// Componente protegido
function ProtectedRoute({ children }) {
  const { token } = useAuthStore();
  
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="/projetos" 
          element={
            <ProtectedRoute>
              <ProjetosPage />
            </ProtectedRoute>
          } 
        />
        
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Router>
  );
}

export default App;
```

---

## 🎯 **Passo 7: Executar React**

```bash
cd web-react

# Desenvolvimento (hot reload)
npm start

# Vai abrir em: http://localhost:3000

# Build para produção
npm run build

# Isso cria a pasta 'build/' pronta para deploy
```

---

## 🚄 **Passo 8: Performance - Code Splitting**

```javascript
import React, { lazy, Suspense } from 'react';

// Carregamento lazy de páginas
const ProjetosPage = lazy(() => import('./pages/ProjetosPage'));
const TarefasPage = lazy(() => import('./pages/TarefasPage'));

function App() {
  return (
    <Routes>
      <Route 
        path="/projetos" 
        element={
          <Suspense fallback={<LoadingSpinner />}>
            <ProjetosPage />
          </Suspense>
        } 
      />
      {/* ... */}
    </Routes>
  );
}
```

---

## 🎨 **Passo 9: Estilos com Tailwind CSS (Opcional)**

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### tailwind.config.js

```javascript
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

### src/index.css

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### Usar no componente

```javascript
function Button() {
  return (
    <button className="bg-blue-500 hover:bg-blue-700 text-white px-4 py-2 rounded">
      Clique aqui
    </button>
  );
}
```

---

## 🧪 **Passo 10: Testes com Jest**

```bash
# Já vem com create-react-app
npm test
```

### src/__tests__/LoginPage.test.js

```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import LoginPage from '../pages/LoginPage';

test('renderiza form de login', () => {
  render(<LoginPage />);
  expect(screen.getByPlaceholderText('Email')).toBeInTheDocument();
});

test('faz login com credenciais válidas', async () => {
  render(<LoginPage />);
  
  fireEvent.change(screen.getByPlaceholderText('Email'), {
    target: { value: 'vicentedesouza762@gmail.com' }
  });
  
  fireEvent.change(screen.getByPlaceholderText('Senha'), {
    target: { value: 'Abc123456' }
  });
  
  fireEvent.click(screen.getByText('Entrar'));
  
  // Verificar se redirecionou para dashboard
  await screen.findByText('Meus Projetos');
});
```

---

## 📦 **Passo 11: Build e Deploy**

```bash
# Gerar build otimizado
npm run build

# Local testing com o build
npm install -g serve
serve -s build

# Isso vai listar: "Accepting connections at http://localhost:3000"
```

---

## 🔄 **Passo 12: Integração com Backend**

```bash
# Terminal 1: Backend
cd backend
python app.py

# Terminal 2: Frontend React
cd web-react
npm start

# Terminal 3 (opcional): HTML+JS antigo (fallback)
cd web
python -m http.server 3001
```

**Acessar:**
- React (novo): http://localhost:3000
- HTML+JS (antigo): http://localhost:3001

---

## ⚡ **Próximas Melhorias**

- [ ] TypeScript (segurança de tipos)
- [ ] Redux Toolkit (estado avançado)
- [ ] React Query (cache de dados)
- [ ] PWA (offline support)
- [ ] E2E tests (Cypress/Playwright)
- [ ] Storybook (UI component library)
- [ ] i18n (Internacionalização)

---

## 📋 **Migration Checklist**

- [ ] Create React App criado em `/web-react`
- [ ] Dependências instaladas (axios, react-router-dom, zustand)
- [ ] Estrutura de pastas organizada
- [ ] API Client adaptado
- [ ] Zustand stores criados
- [ ] Login Page funcional
- [ ] Dashboard Page funcional
- [ ] Roteamento protegido implementado
- [ ] Estilos CSS aplicados
- [ ] Testes básicos funcionando
- [ ] Build gerado e testado
- [ ] Git commit com nova estrutura React

---

**Boa sorte com React! 🎉**

Próximo passo seria começar a portar componentes do HTML+JS vanilla para React componentes reutilizáveis.
