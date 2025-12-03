/**
 * Cliente API - Integração Frontend
 * Funções para consumir a API REST
 */

const API_BASE_URL = 'http://localhost:8000';

// Gerenciador de Token
const TokenManager = {
    set: (token) => localStorage.setItem('auth_token', token),
    get: () => localStorage.getItem('auth_token'),
    remove: () => localStorage.removeItem('auth_token'),
    isValid: () => !!localStorage.getItem('auth_token')
};

// Gerenciador de Usuário
const UserManager = {
    set: (user) => localStorage.setItem('current_user', JSON.stringify(user)),
    get: () => {
        const user = localStorage.getItem('current_user');
        return user ? JSON.parse(user) : null;
    },
    remove: () => localStorage.removeItem('current_user')
};

// Cliente HTTP
class APIClient {
    constructor(baseURL = API_BASE_URL) {
        this.baseURL = baseURL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const config = {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };

        // Adicionar token se existir
        const token = TokenManager.get();
        if (token && !options.skipAuth) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, config);
            
            // Se não autorizado, limpar token e redirecionar
            if (response.status === 401) {
                TokenManager.remove();
                UserManager.remove();
                window.location.href = '/login.html';
                throw new Error('Sessão expirada. Faça login novamente.');
            }

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Erro na requisição');
            }

            return data;
        } catch (error) {
            console.error('Erro na requisição:', error);
            throw error;
        }
    }

    // Métodos HTTP
    get(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'GET' });
    }

    post(endpoint, data, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    put(endpoint, data, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    delete(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'DELETE' });
    }
}

// Instância global do cliente
const api = new APIClient();

// API de Autenticação
const AuthAPI = {
    async login(email, senha) {
        const response = await api.post('/auth/login', { email, senha }, { skipAuth: true });
        
        // Salvar token e usuário
        TokenManager.set(response.access_token);
        UserManager.set(response.user);
        
        return response;
    },

    async register(nome, email, senha, telefone = null, cargo = null) {
        return await api.post('/auth/register', {
            nome,
            email,
            senha,
            telefone,
            cargo
        }, { skipAuth: true });
    },

    logout() {
        TokenManager.remove();
        UserManager.remove();
        window.location.href = '/login.html';
    },

    isAuthenticated() {
        return TokenManager.isValid();
    },

    getCurrentUser() {
        return UserManager.get();
    }
};

// API de Projetos
const ProjetosAPI = {
    async listar(status = null) {
        const params = status ? `?status=${status}` : '';
        return await api.get(`/projetos/${params}`);
    },

    async buscar(id) {
        return await api.get(`/projetos/${id}`);
    },

    async criar(projeto) {
        return await api.post('/projetos/', projeto);
    },

    async atualizar(id, projeto) {
        return await api.put(`/projetos/${id}`, projeto);
    },

    async deletar(id) {
        return await api.delete(`/projetos/${id}`);
    }
};

// API de Tarefas
const TarefasAPI = {
    async listarPorProjeto(projetoId, status = null) {
        const params = status ? `?status=${status}` : '';
        return await api.get(`/tarefas/projeto/${projetoId}${params}`);
    },

    async criar(tarefa) {
        return await api.post('/tarefas/', tarefa);
    },

    async atualizar(id, tarefa) {
        return await api.put(`/tarefas/${id}`, tarefa);
    },

    async deletar(id) {
        return await api.delete(`/tarefas/${id}`);
    }
};

// Verificar autenticação ao carregar
document.addEventListener('DOMContentLoaded', () => {
    // Não verificar nas páginas públicas
    const publicPages = ['/login.html', '/register.html', '/'];
    const currentPath = window.location.pathname;
    
    if (!publicPages.includes(currentPath) && !AuthAPI.isAuthenticated()) {
        window.location.href = '/login.html';
    }
});

// Exportar APIs
window.API = {
    Auth: AuthAPI,
    Projetos: ProjetosAPI,
    Tarefas: TarefasAPI,
    TokenManager,
    UserManager
};
