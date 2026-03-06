// src/store/projetosStore.js
// Store de projetos usando Zustand

import create from 'zustand';

const useProjetosStore = create((set) => ({
  // Estado
  projetos: [],
  projetoSelecionado: null,
  loading: false,
  error: null,
  filtros: {
    status: null,
    busca: '',
    ordenar: 'data_atualizacao'
  },

  // Ações
  setProjetos: (projetos) => set({ projetos }),
  setProjetoSelecionado: (projeto) => set({ projetoSelecionado: projeto }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  fetchProjetos: async (token, filtros = {}) => {
    set({ loading: true, error: null });
    try {
      const params = new URLSearchParams();
      if (filtros.status) params.append('status', filtros.status);
      if (filtros.busca) params.append('search', filtros.busca);

      const response = await fetch(`/api/projetos?${params}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) throw new Error('Falha ao buscar projetos');

      const projetos = await response.json();
      set({ projetos, error: null });
      return projetos;
    } catch (err) {
      set({ error: err.message });
      throw err;
    } finally {
      set({ loading: false });
    }
  },

  criarProjeto: async (token, dadosProjeto) => {
    set({ loading: true, error: null });
    try {
      const response = await fetch('/api/projetos', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(dadosProjeto)
      });

      if (!response.ok) throw new Error('Falha ao criar projeto');

      const novoProjeto = await response.json();
      set((state) => ({
        projetos: [...state.projetos, novoProjeto],
        error: null
      }));
      return novoProjeto;
    } catch (err) {
      set({ error: err.message });
      throw err;
    } finally {
      set({ loading: false });
    }
  },

  setFiltros: (filtros) => set((state) => ({
    filtros: { ...state.filtros, ...filtros }
  })),

  clearError: () => set({ error: null })
}));

export default useProjetosStore;
