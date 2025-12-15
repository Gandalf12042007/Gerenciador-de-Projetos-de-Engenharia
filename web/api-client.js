/**
 * API CLIENT - Gerenciador de Projetos
 * Comunica com o backend FastAPI
 */

const API_URL = 'http://localhost:8000/api'; // Ajuste conforme necessário

class ApiClient {
    constructor() {
        this.token = localStorage.getItem('access_token');
        this.user = JSON.parse(localStorage.getItem('user') || '{}');
    }

    /**
     * Faz requisição GET
     */
    async get(endpoint) {
        return this._request('GET', endpoint);
    }

    /**
     * Faz requisição POST
     */
    async post(endpoint, data) {
        return this._request('POST', endpoint, data);
    }

    /**
     * Faz requisição PUT
     */
    async put(endpoint, data) {
        return this._request('PUT', endpoint, data);
    }

    /**
     * Faz requisição DELETE
     */
    async delete(endpoint) {
        return this._request('DELETE', endpoint);
    }

    /**
     * Requisição genérica com tratamento de erro
     */
    async _request(method, endpoint, data = null) {
        try {
            const options = {
                method,
                headers: {
                    'Content-Type': 'application/json',
                },
            };

            // Adiciona token JWT se existe
            if (this.token) {
                options.headers['Authorization'] = `Bearer ${this.token}`;
            }

            // Adiciona body para POST/PUT
            if (data && (method === 'POST' || method === 'PUT')) {
                options.body = JSON.stringify(data);
            }

            const response = await fetch(`${API_URL}${endpoint}`, options);

            // Trata resposta não-JSON
            const contentType = response.headers.get('content-type');
            let responseData;

            if (contentType && contentType.includes('application/json')) {
                responseData = await response.json();
            } else {
                responseData = await response.text();
            }

            // Trata erro de autenticação
            if (response.status === 401) {
                this.logout();
                throw new Error('Sessão expirada. Faça login novamente.');
            }

            // Trata outros erros HTTP
            if (!response.ok) {
                throw new Error(responseData.detail || responseData.message || 'Erro na requisição');
            }

            return responseData;
        } catch (error) {
            console.error(`Erro em ${method} ${endpoint}:`, error);
            throw error;
        }
    }

    /**
     * Upload de arquivo
     */
    async uploadFile(endpoint, file) {
        try {
            const formData = new FormData();
            formData.append('file', file);

            const options = {
                method: 'POST',
                headers: {},
            };

            if (this.token) {
                options.headers['Authorization'] = `Bearer ${this.token}`;
            }

            options.body = formData;

            const response = await fetch(`${API_URL}${endpoint}`, options);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Erro ao fazer upload');
            }

            return data;
        } catch (error) {
            console.error('Erro no upload:', error);
            throw error;
        }
    }

    /**
     * Salva token e usuário
     */
    setAuth(token, user) {
        this.token = token;
        this.user = user;
        localStorage.setItem('access_token', token);
        localStorage.setItem('user', JSON.stringify(user));
    }

    /**
     * Remove autenticação
     */
    logout() {
        this.token = null;
        this.user = {};
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
    }

    /**
     * Verifica se usuário está autenticado
     */
    isAuthenticated() {
        return !!this.token;
    }

    // ============ AUTENTICAÇÃO ============

    async register(nome, email, senha, cargo) {
        return this.post('/auth/register', {
            nome,
            email,
            senha,
            cargo,
        });
    }

    async login(email, senha) {
        return this.post('/auth/login', {
            email,
            senha,
        });
    }

    async verify2FA(email, codigo_otp) {
        return this.post('/auth/verify-2fa', {
            email,
            codigo_otp,
        });
    }

    async resendOTP(email) {
        return this.post('/auth/resend-otp', {
            email,
        });
    }

    // ============ PROJETOS ============

    async getProjetos(skip = 0, limit = 100) {
        return this.get(`/projetos?skip=${skip}&limit=${limit}`);
    }

    async getProjetoById(id) {
        return this.get(`/projetos/${id}`);
    }

    async createProjeto(dados) {
        return this.post('/projetos', dados);
    }

    async updateProjeto(id, dados) {
        return this.put(`/projetos/${id}`, dados);
    }

    async deleteProjeto(id) {
        return this.delete(`/projetos/${id}`);
    }

    // ============ TAREFAS ============

    async getTarefas(skip = 0, limit = 100) {
        return this.get(`/tarefas?skip=${skip}&limit=${limit}`);
    }

    async getTarefaById(id) {
        return this.get(`/tarefas/${id}`);
    }

    async createTarefa(dados) {
        return this.post('/tarefas', dados);
    }

    async updateTarefa(id, dados) {
        return this.put(`/tarefas/${id}`, dados);
    }

    async deleteTarefa(id) {
        return this.delete(`/tarefas/${id}`);
    }

    async getTarefasByProjeto(projeto_id) {
        return this.get(`/projetos/${projeto_id}/tarefas`);
    }

    // ============ DOCUMENTOS ============

    async getDocumentos(skip = 0, limit = 100) {
        return this.get(`/documentos?skip=${skip}&limit=${limit}`);
    }

    async getDocumentosByProjeto(projeto_id) {
        return this.get(`/projetos/${projeto_id}/documentos`);
    }

    async uploadDocumento(projeto_id, file) {
        return this.uploadFile(`/documentos/${projeto_id}/upload`, file);
    }

    async deleteDocumento(id) {
        return this.delete(`/documentos/${id}`);
    }

    async downloadDocumento(id) {
        return `${API_URL}/documentos/${id}/download`;
    }

    // ============ EQUIPES ============

    async getEquipes(skip = 0, limit = 100) {
        return this.get(`/equipes?skip=${skip}&limit=${limit}`);
    }

    async getEquipeById(id) {
        return this.get(`/equipes/${id}`);
    }

    async addMemberToTeam(equipe_id, usuario_id, funcao) {
        return this.post(`/equipes/${equipe_id}/members`, {
            usuario_id,
            funcao,
        });
    }

    async removeMemberFromTeam(equipe_id, usuario_id) {
        return this.delete(`/equipes/${equipe_id}/members/${usuario_id}`);
    }

    // ============ MATERIAIS ============

    async getMateriais(skip = 0, limit = 100) {
        return this.get(`/materiais?skip=${skip}&limit=${limit}`);
    }

    async createMaterial(dados) {
        return this.post('/materiais', dados);
    }

    async updateMaterial(id, dados) {
        return this.put(`/materiais/${id}`, dados);
    }

    async deleteMaterial(id) {
        return this.delete(`/materiais/${id}`);
    }

    // ============ ORÇAMENTOS ============

    async getOrcamentos(skip = 0, limit = 100) {
        return this.get(`/orcamentos?skip=${skip}&limit=${limit}`);
    }

    async createOrcamento(dados) {
        return this.post('/orcamentos', dados);
    }

    async updateOrcamento(id, dados) {
        return this.put(`/orcamentos/${id}`, dados);
    }

    async deleteOrcamento(id) {
        return this.delete(`/orcamentos/${id}`);
    }

    // ============ CHAT ============

    async sendMessage(projeto_id, conteudo) {
        return this.post(`/chat/${projeto_id}/messages`, {
            conteudo,
        });
    }

    async getMessages(projeto_id, skip = 0, limit = 50) {
        return this.get(`/chat/${projeto_id}/messages?skip=${skip}&limit=${limit}`);
    }

    // ============ MÉTRICAS ============

    async getMetricas() {
        return this.get('/metricas');
    }

    async getMetricasTimeline() {
        return this.get('/metricas/timeline');
    }

    // ============ HEALTH CHECK ============

    async healthCheck() {
        return this.get('/health');
    }
}

// Instância global do cliente API
const api = new ApiClient();
    
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
