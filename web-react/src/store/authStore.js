// src/store/authStore.js
// Store de autenticação usando Zustand

import create from 'zustand';
import { persist } from 'zustand/middleware';

const useAuthStore = create(
  persist((set) => ({
    // Estado
    user: null,
    token: null,
    isAuthenticated: false,
    loading: false,
    error: null,

    // Ações
    setUser: (user) => set({ user }),
    setToken: (token) => set({ token }),
    setLoading: (loading) => set({ loading }),
    setError: (error) => set({ error }),

    login: async (email, senha) => {
      set({ loading: true, error: null });
      try {
        const response = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, senha })
        });

        if (!response.ok) {
          throw new Error('Falha na autenticação');
        }

        const data = await response.json();
        set({
          user: data.usuario || { email },
          token: data.token,
          isAuthenticated: true,
          error: null
        });

        return data;
      } catch (err) {
        set({
          error: err.message,
          isAuthenticated: false,
          token: null,
          user: null
        });
        throw err;
      } finally {
        set({ loading: false });
      }
    },

    logout: () => {
      set({
        user: null,
        token: null,
        isAuthenticated: false,
        error: null
      });
    },

    clearError: () => set({ error: null })
  }),
  {
    name: 'auth-store',
    partialize: (state) => ({
      token: state.token,
      user: state.user,
      isAuthenticated: state.isAuthenticated
    })
  })
);

export default useAuthStore;
