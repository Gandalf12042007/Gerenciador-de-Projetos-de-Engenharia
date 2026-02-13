// ============================================
// THEME MANAGER - Gerenciador de Temas
// Controla alternância entre claro/escuro
// ============================================

class ThemeManager {
  constructor() {
    this.STORAGE_KEY = 'theme-preference';
    this.THEME_ATTRIBUTE = 'data-theme';
    this.THEMES = ['light', 'dark'];
    this.SYSTEM_THEME_QUERY = '(prefers-color-scheme: dark)';
    
    this.init();
  }

  /**
   * Inicializar gerenciador de tema
   */
  init() {
    const savedTheme = this.getSavedTheme();
    const systemTheme = this.getSystemTheme();
    const initialTheme = savedTheme || systemTheme || 'light';

    this.setTheme(initialTheme);
    this.setupSystemPreferenceListener();
  }

  /**
   * Obter tema salvo no localStorage
   */
  getSavedTheme() {
    return localStorage.getItem(this.STORAGE_KEY);
  }

  /**
   * Obter preferência do sistema
   */
  getSystemTheme() {
    if (window.matchMedia && window.matchMedia(this.SYSTEM_THEME_QUERY).matches) {
      return 'dark';
    }
    return 'light';
  }

  /**
   * Definir tema
   */
  setTheme(theme) {
    if (!this.THEMES.includes(theme)) {
      console.warn(`Tema inválido: ${theme}`);
      return;
    }

    // Aplicar tema no HTML
    document.documentElement.setAttribute(this.THEME_ATTRIBUTE, theme);
    
    // Salvar preferência
    localStorage.setItem(this.STORAGE_KEY, theme);
    
    // Atualizar meta tags de cor
    this.updateMetaTags(theme);
    
    // Disparar evento customizado
    this.dispatchThemeChangeEvent(theme);
    
    console.log(`✅ Tema alterado para: ${theme}`);
  }

  /**
   * Alternar entre temas
   */
  toggleTheme() {
    const currentTheme = document.documentElement.getAttribute(this.THEME_ATTRIBUTE) || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    this.setTheme(newTheme);
  }

  /**
   * Obter tema atual
   */
  getCurrentTheme() {
    return document.documentElement.getAttribute(this.THEME_ATTRIBUTE) || 'light';
  }

  /**
   * Verificar se está em modo escuro
   */
  isDarkMode() {
    return this.getCurrentTheme() === 'dark';
  }

  /**
   * Atualizar meta tags para PWA
   */
  updateMetaTags(theme) {
    const themeColor = theme === 'dark' ? '#111827' : '#ffffff';
    const backgroundColor = theme === 'dark' ? '#111827' : '#f9fafb';
    
    let themeColorMeta = document.querySelector('meta[name="theme-color"]');
    if (!themeColorMeta) {
      themeColorMeta = document.createElement('meta');
      themeColorMeta.name = 'theme-color';
      document.head.appendChild(themeColorMeta);
    }
    themeColorMeta.content = themeColor;

    let bgColorMeta = document.querySelector('meta[name="background-color"]');
    if (!bgColorMeta) {
      bgColorMeta = document.createElement('meta');
      bgColorMeta.name = 'background-color';
      document.head.appendChild(bgColorMeta);
    }
    bgColorMeta.content = backgroundColor;
  }

  /**
   * Escutar mudanças de preferência do sistema
   */
  setupSystemPreferenceListener() {
    if (window.matchMedia) {
      const mediaQuery = window.matchMedia(this.SYSTEM_THEME_QUERY);
      
      // Listener para mudanças de preferência
      const handleChange = (e) => {
        if (!this.getSavedTheme()) { // Apenas se não houver preferência salva
          const newTheme = e.matches ? 'dark' : 'light';
          this.setTheme(newTheme);
        }
      };

      // Método antigo (compatibilidade)
      if (mediaQuery.addListener) {
        mediaQuery.addListener(handleChange);
      }
      
      // Método novo
      if (mediaQuery.addEventListener) {
        mediaQuery.addEventListener('change', handleChange);
      }
    }
  }

  /**
   * Disparar evento customizado
   */
  dispatchThemeChangeEvent(theme) {
    const event = new CustomEvent('themechange', {
      detail: { theme, isDark: theme === 'dark' }
    });
    window.dispatchEvent(event);
  }

  /**
   * Resetar para preferência do sistema
   */
  resetToSystem() {
    localStorage.removeItem(this.STORAGE_KEY);
    const systemTheme = this.getSystemTheme();
    this.setTheme(systemTheme);
  }
}

// ============================================
// INICIALIZAR GERENCIADOR GLOBALMENTE
// ============================================

const themeManager = new ThemeManager();

// Expor globalmente para uso em HTML
window.themeManager = themeManager;

// Log inicial
console.log(`🎨 Theme Manager inicializado. Tema atual: ${themeManager.getCurrentTheme()}`);
