/**
 * API CLIENT - Gerenciador de Projetos
 * Comunica com o backend FastAPI
 */

const API_URL = 'http://localhost:8000'; // Sem prefixo /api - backend não usa

class ApiClient {
    constructor() {
        this.token = localStorage.getItem('access_token');
        this.user = JSON.parse(localStorage.getItem('user') || '{}');
        
        // Se não marcou "manter conectado" e é uma nova sessão, limpa dados
        const keepLoggedIn = localStorage.getItem('keep_logged_in');
        const sessionOnly = sessionStorage.getItem('session_only');
        
        // Se a sessão anterior era "session_only" e estamos em uma nova aba/sessão
        if (!keepLoggedIn && !sessionOnly && this.token) {
            // Verifica se é uma nova sessão do navegador
            // Se não há sessionStorage marcada, é uma nova sessão
            sessionStorage.setItem('current_session', 'true');
        }
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
        localStorage.removeItem('keep_logged_in');
        sessionStorage.removeItem('session_only');
        sessionStorage.removeItem('current_session');
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

    // ============ GERENCIAMENTO DE SENHA ============

    /**
     * Solicita reset de senha (esqueci minha senha)
     */
    async forgotPassword(email) {
        return this.post('/auth/forgot-password', { email });
    }

    /**
     * Redefine senha usando token
     */
    async resetPassword(token, nova_senha) {
        return this.post('/auth/reset-password', { token, nova_senha });
    }

    /**
     * Altera senha do usuário logado
     */
    async changePassword(senha_atual, nova_senha) {
        return this.put('/auth/change-password', { senha_atual, nova_senha });
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

    async getTarefasByProjeto(projeto_id, status = null) {
        let url = `/tarefas/projeto/${projeto_id}`;
        if (status) url += `?status=${status}`;
        return this.get(url);
    }

    async createTarefa(dados) {
        return this.post('/tarefas/', dados);
    }

    async updateTarefa(id, dados) {
        return this.put(`/tarefas/${id}`, dados);
    }

    async deleteTarefa(id) {
        return this.delete(`/tarefas/${id}`);
    }

    // ============ DOCUMENTOS ============

    async getDocumentosByProjeto(projeto_id) {
        return this.get(`/documentos/${projeto_id}`);
    }

    async uploadDocumento(projeto_id, file) {
        return this.uploadFile(`/documentos/${projeto_id}/upload`, file);
    }

    async deleteDocumento(id) {
        return this.delete(`/documentos/${id}`);
    }

    async getVersoes(documento_id) {
        return this.get(`/documentos/${documento_id}/versoes`);
    }

    downloadDocumentoUrl(id) {
        return `${API_URL}/documentos/${id}/download`;
    }

    // ============ EQUIPES ============

    async getEquipesByProjeto(projeto_id) {
        return this.get(`/equipes/projeto/${projeto_id}`);
    }

    async addMemberToTeam(dados) {
        // dados: { projeto_id, usuario_id, papel, data_entrada }
        return this.post('/equipes/', dados);
    }

    async updateMember(membro_id, dados) {
        return this.put(`/equipes/${membro_id}`, dados);
    }

    async removeMemberFromTeam(membro_id) {
        return this.delete(`/equipes/${membro_id}`);
    }

    async enviarConvite(dados) {
        // dados: { projeto_id, email_convidado, papel }
        return this.post('/equipes/convite', dados);
    }

    // ============ MATERIAIS ============

    async getMateriaisByProjeto(projeto_id) {
        return this.get(`/materiais/${projeto_id}`);
    }

    async createMaterial(projeto_id, dados) {
        return this.post(`/materiais/${projeto_id}`, dados);
    }

    async updateMaterial(id, dados) {
        return this.put(`/materiais/${id}`, dados);
    }

    async deleteMaterial(id) {
        return this.delete(`/materiais/${id}`);
    }

    // ============ ORÇAMENTOS ============

    async getOrcamentosByProjeto(projeto_id) {
        return this.get(`/orcamentos/${projeto_id}`);
    }

    async getResumoOrcamento(projeto_id) {
        return this.get(`/orcamentos/${projeto_id}/resumo`);
    }

    async createOrcamento(projeto_id, dados) {
        return this.post(`/orcamentos/${projeto_id}`, dados);
    }

    async updateOrcamento(id, dados) {
        return this.put(`/orcamentos/${id}`, dados);
    }

    async deleteOrcamento(id) {
        return this.delete(`/orcamentos/${id}`);
    }

    async registrarPagamento(orcamento_id, dados) {
        return this.post(`/orcamentos/${orcamento_id}/registrar-pagamento`, dados);
    }

    // ============ CHAT ============

    async sendMessage(projeto_id, conteudo) {
        return this.post(`/chat/${projeto_id}/mensagens`, {
            conteudo,
        });
    }

    async getMessages(projeto_id, skip = 0, limit = 50) {
        return this.get(`/chat/${projeto_id}/mensagens?skip=${skip}&limit=${limit}`);
    }

    // ============ MÉTRICAS ============

    async getMetricas(projeto_id) {
        return this.get(`/metricas/${projeto_id}/dashboard`);
    }

    async getMetricasTimeline(projeto_id) {
        return this.get(`/metricas/${projeto_id}/timeline`);
    }

    // ============ COMENTÁRIOS DE TAREFAS ============

    async getComentariosTarefa(tarefa_id) {
        return this.get(`/tarefas/${tarefa_id}/comentarios`);
    }

    async addComentarioTarefa(tarefa_id, comentario) {
        return this.post(`/tarefas/${tarefa_id}/comentarios`, { comentario });
    }

    async updateComentarioTarefa(tarefa_id, comentario_id, comentario) {
        return this.put(`/tarefas/${tarefa_id}/comentarios/${comentario_id}`, { comentario });
    }

    async deleteComentarioTarefa(tarefa_id, comentario_id) {
        return this.delete(`/tarefas/${tarefa_id}/comentarios/${comentario_id}`);
    }

    // ============ NOTIFICAÇÕES ============

    async getNotificacoes(apenas_nao_lidas = false, limite = 50) {
        return this.get(`/notificacoes/?apenas_nao_lidas=${apenas_nao_lidas}&limite=${limite}`);
    }

    async getNotificacoesNaoLidasCount() {
        return this.get('/notificacoes/nao-lidas/contagem');
    }

    async marcarNotificacaoLida(notificacao_id) {
        return this.put(`/notificacoes/${notificacao_id}/marcar-lida`, {});
    }

    async marcarTodasNotificacoesLidas() {
        return this.put('/notificacoes/marcar-todas-lidas', {});
    }

    async deleteNotificacao(notificacao_id) {
        return this.delete(`/notificacoes/${notificacao_id}`);
    }

    // ============ HEALTH CHECK ============

    async healthCheck() {
        return this.get('/health');
    }
}

// Instância global do cliente API
const api = new ApiClient();

// ============ CAMADA DE COMPATIBILIDADE ============
// Para manter compatibilidade com os arquivos em projects/
// que usam API.Auth, API.Projetos, API.Tarefas, API.Documentos

const API = {
    Auth: {
        isAuthenticated: () => api.isAuthenticated(),
        login: (email, senha) => api.login(email, senha),
        logout: () => api.logout(),
        getUser: () => api.user,
        getToken: () => api.token
    },
    Projetos: {
        listar: () => api.getProjetos(),
        obter: (id) => api.getProjetoById(id),
        criar: (dados) => api.createProjeto(dados),
        atualizar: (id, dados) => api.updateProjeto(id, dados),
        deletar: (id) => api.deleteProjeto(id)
    },
    Tarefas: {
        listar: (projeto_id) => api.getTarefasByProjeto(projeto_id),
        criar: (projeto_id, dados) => api.createTarefa({ ...dados, projeto_id }),
        atualizar: (id, dados) => api.updateTarefa(id, dados),
        deletar: (id) => api.deleteTarefa(id)
    },
    Documentos: {
        listar: (projeto_id) => api.getDocumentosByProjeto(projeto_id),
        criar: (projeto_id, formData) => api.uploadDocumento(projeto_id, formData.get('file')),
        atualizar: (id, formData) => api.put(`/documentos/${id}`, formData),
        deletar: (id) => api.deleteDocumento(id),
        download: (id) => Promise.resolve(api.downloadDocumentoUrl(id))
    },
    Equipes: {
        listarPorProjeto: (projeto_id) => api.getEquipesByProjeto(projeto_id),
        adicionar: (dados) => api.addMemberToTeam(dados),
        atualizar: (id, dados) => api.updateMember(id, dados),
        remover: (id) => api.removeMemberFromTeam(id)
    },
    Materiais: {
        listarPorProjeto: (projeto_id) => api.getMateriaisByProjeto(projeto_id),
        criar: (projeto_id, dados) => api.createMaterial(projeto_id, dados),
        atualizar: (id, dados) => api.updateMaterial(id, dados),
        deletar: (id) => api.deleteMaterial(id)
    },
    Orcamentos: {
        listarPorProjeto: (projeto_id) => api.getOrcamentosByProjeto(projeto_id),
        criar: (projeto_id, dados) => api.createOrcamento(projeto_id, dados),
        atualizar: (id, dados) => api.updateOrcamento(id, dados),
        deletar: (id) => api.deleteOrcamento(id)
    },
    Chat: {
        enviar: (projeto_id, conteudo) => api.sendMessage(projeto_id, conteudo),
        listar: (projeto_id, skip, limit) => api.getMessages(projeto_id, skip, limit)
    },
    Metricas: {
        dashboard: (projeto_id) => api.getMetricas(projeto_id)
    }
};

// Exportar para uso global
window.api = api;
window.API = API;
