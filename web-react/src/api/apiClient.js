// src/api/apiClient.js
// Cliente centralizado para chamadas à API

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Criar instância do axios com configurações padrão
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptador para adicionar token de autenticação
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth-store');
  if (token) {
    try {
      const authStore = JSON.parse(token);
      if (authStore.state && authStore.state.token) {
        config.headers.Authorization = `Bearer ${authStore.state.token}`;
      }
    } catch (e) {
      // Token inválido, ignorar
    }
  }
  return config;
});

// Interceptador para tratamento de erros
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado, limpar localStorage
      localStorage.removeItem('auth-store');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============================================
// MÉTODOS DE AUTENTICAÇÃO
// ============================================

export const authAPI = {
  login: (email, senha) =>
    apiClient.post('/auth/login', { email, senha }),

  logout: () =>
    apiClient.post('/auth/logout'),

  refreshToken: (token) =>
    apiClient.post('/auth/refresh', { token })
};

// ============================================
// MÉTODOS DE PROJETOS
// ============================================

export const projetosAPI = {
  listar: (filtros = {}) =>
    apiClient.get('/projetos', { params: filtros }),

  obter: (id) =>
    apiClient.get(`/projetos/${id}`),

  criar: (dados) =>
    apiClient.post('/projetos', dados),

  atualizar: (id, dados) =>
    apiClient.put(`/projetos/${id}`, dados),

  deletar: (id) =>
    apiClient.delete(`/projetos/${id}`),

  listarTarefas: (projetoId) =>
    apiClient.get(`/tarefas?projeto_id=${projetoId}`),

  obterEstatisticas: (id) =>
    apiClient.get(`/projetos/${id}/estatisticas`)
};

// ============================================
// MÉTODOS DE TAREFAS
// ============================================

export const tarefasAPI = {
  listar: (filtros = {}) =>
    apiClient.get('/tarefas', { params: filtros }),

  obter: (id) =>
    apiClient.get(`/tarefas/${id}`),

  criar: (dados) =>
    apiClient.post('/tarefas', dados),

  atualizar: (id, dados) =>
    apiClient.put(`/tarefas/${id}`, dados),

  deletar: (id) =>
    apiClient.delete(`/tarefas/${id}`),

  mudarStatus: (id, status) =>
    apiClient.patch(`/tarefas/${id}`, { status })
};

// ============================================
// MÉTODOS DE FINANCEIRO
// ============================================

export const financeiroAPI = {
  // Custos
  listarCustos: (filtros = {}) =>
    apiClient.get('/financeiro/custos', { params: filtros }),

  criarCusto: (dados) =>
    apiClient.post('/financeiro/custos', dados),

  // Orçamentos
  listarOrcamentos: (filtros = {}) =>
    apiClient.get('/financeiro/orcamentos', { params: filtros }),

  obterOrcamento: (id) =>
    apiClient.get(`/financeiro/orcamentos/${id}`),

  criarOrcamento: (dados) =>
    apiClient.post('/financeiro/orcamentos', dados),

  // Faturas
  listarFaturas: (filtros = {}) =>
    apiClient.get('/financeiro/faturas', { params: filtros }),

  obterFatura: (id) =>
    apiClient.get(`/financeiro/faturas/${id}`),

  criarFatura: (dados) =>
    apiClient.post('/financeiro/faturas', dados),

  pagarFatura: (id, dados) =>
    apiClient.post(`/financeiro/faturas/${id}/pagar`, dados),

  // Relatórios
  dashboardFinanceiro: (projetoId) =>
    apiClient.get('/financeiro/relatorios/dashboard', {
      params: { projeto_id: projetoId }
    }),

  relatorioCustosVsOrcado: (projetoId) =>
    apiClient.get('/financeiro/relatorios/orcamento-vs-realizado', {
      params: { projeto_id: projetoId }
    })
};

// ============================================
// MÉTODOS DE USUÁRIOS
// ============================================

export const usuariosAPI = {
  listar: () =>
    apiClient.get('/usuarios'),

  obter: (id) =>
    apiClient.get(`/usuarios/${id}`),

  obterPerfil: () =>
    apiClient.get('/usuarios/profile'),

  atualizar: (id, dados) =>
    apiClient.put(`/usuarios/${id}`, dados)
};

export default apiClient;
