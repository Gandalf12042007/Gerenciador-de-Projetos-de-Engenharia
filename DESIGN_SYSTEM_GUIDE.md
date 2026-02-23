# 🎨 Guia de Design System & UI/UX Melhorias

**Transformar interface em design profissional moderno**

---

## 📋 **Diagnóstico Atual**

**Problemas Identificados:**
- ❌ Sem design system consistente
- ❌ Sem modo escuro
- ❌ Sem responsividade mobile
- ❌ Cores sem documentação
- ❌ Tipografia inconsistente
- ❌ Sem componentes reutilizáveis
- ❌ Sem animações/feedback visual
- ❌ Accessibility (a11y) limitada

**Oportunidades:**
- ✅ Design tokens centralizados
- ✅ Modo claro/escuro
- ✅ Mobile-first responsive
- ✅ Sistema de cores harmonioso
- ✅ Componentes de UI reutilizáveis
- ✅ Animações suaves
- ✅ Acessibilidade melhorada

---

## 🎯 **Fase 1: Design Tokens (Variaveis CSS)**

### src/styles/tokens.css (ou tailwind.config.js)

```css
:root {
  /* === CORES === */
  /* Primária (Azul) */
  --color-primary-50: #f0f9ff;
  --color-primary-100: #e0f2fe;
  --color-primary-200: #bae6fd;
  --color-primary-300: #7dd3fc;
  --color-primary-400: #38bdf8;
  --color-primary-500: #0ea5e9;  /* Primary */
  --color-primary-600: #0284c7;
  --color-primary-700: #0369a1;
  --color-primary-800: #075985;
  --color-primary-900: #0c3d66;

  /* Secundária (Verde) */
  --color-success-50: #f0fdf4;
  --color-success-500: #10b981;
  --color-success-600: #059669;
  --color-success-700: #047857;

  /* Erro (Vermelho) */
  --color-error-50: #fef2f2;
  --color-error-500: #ef4444;
  --color-error-600: #dc2626;
  --color-error-700: #b91c1c;

  /* Aviso (Amarelo) */
  --color-warning-50: #fffbeb;
  --color-warning-500: #f59e0b;
  --color-warning-600: #d97706;
  --color-warning-700: #b45309;

  /* Neutras */
  --color-neutral-50: #f9fafb;
  --color-neutral-100: #f3f4f6;
  --color-neutral-200: #e5e7eb;
  --color-neutral-300: #d1d5db;
  --color-neutral-400: #9ca3af;
  --color-neutral-500: #6b7280;
  --color-neutral-600: #4b5563;
  --color-neutral-700: #374151;
  --color-neutral-800: #1f2937;
  --color-neutral-900: #111827;

  /* === TIPOGRAFIA === */
  --font-family-base: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  --font-family-mono: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;

  --font-size-xs: 0.75rem;    /* 12px */
  --font-size-sm: 0.875rem;   /* 14px */
  --font-size-base: 1rem;     /* 16px */
  --font-size-lg: 1.125rem;   /* 18px */
  --font-size-xl: 1.25rem;    /* 20px */
  --font-size-2xl: 1.5rem;    /* 24px */
  --font-size-3xl: 1.875rem;  /* 30px */
  --font-size-4xl: 2.25rem;   /* 36px */

  --font-weight-light: 300;
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  /* === ESPAÇAMENTO === */
  --spacing-1: 0.25rem;   /* 4px */
  --spacing-2: 0.5rem;    /* 8px */
  --spacing-3: 0.75rem;   /* 12px */
  --spacing-4: 1rem;      /* 16px */
  --spacing-5: 1.25rem;   /* 20px */
  --spacing-6: 1.5rem;    /* 24px */
  --spacing-8: 2rem;      /* 32px */
  --spacing-12: 3rem;     /* 48px */

  /* === BORDER RADIUS === */
  --radius-none: 0;
  --radius-sm: 0.25rem;
  --radius-base: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  --radius-2xl: 1.5rem;
  --radius-full: 9999px;

  /* === SOMBRAS === */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-base: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);

  /* === TRANSIÇÕES === */
  --transition-fast: 150ms ease-in-out;
  --transition-normal: 250ms ease-in-out;
  --transition-slow: 350ms ease-in-out;

  /* === BREAKPOINTS (Mobile-First) === */
  /* Variáveis usadas em media queries */
}

/* === DARK MODE === */
[data-theme="dark"] {
  --color-primary-50: #0c3d66;
  --color-primary-500: #38bdf8;
  --color-neutral-50: #111827;
  --color-neutral-900: #f9fafb;
  /* ... inversão de cores */
}
```

---

## 🌓 **Fase 2: Dark Mode Implementation**

### src/utils/themeManager.js

```javascript
class ThemeManager {
  constructor() {
    this.currentTheme = localStorage.getItem('theme') || 'light';
    this.applyTheme();
  }

  applyTheme() {
    const isDark = this.currentTheme === 'dark';
    document.documentElement.setAttribute('data-theme', this.currentTheme);
    localStorage.setItem('theme', this.currentTheme);
    
    // Notificar listeners
    window.dispatchEvent(new CustomEvent('themeChange', { 
      detail: { theme: this.currentTheme } 
    }));
  }

  toggle() {
    this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
    this.applyTheme();
  }

  setTheme(theme) {
    if (['light', 'dark'].includes(theme)) {
      this.currentTheme = theme;
      this.applyTheme();
    }
  }

  getTheme() {
    return this.currentTheme;
  }

  // Detectar preferência do sistema
  detectSystemPreference() {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  }
}

export default new ThemeManager();
```

### React Hook para Dark Mode

```javascript
// src/hooks/useTheme.js
import { useEffect, useState } from 'react';
import themeManager from '../utils/themeManager';

export function useTheme() {
  const [theme, setTheme] = useState(themeManager.getTheme());

  useEffect(() => {
    const handleThemeChange = (e) => setTheme(e.detail.theme);
    window.addEventListener('themeChange', handleThemeChange);
    return () => window.removeEventListener('themeChange', handleThemeChange);
  }, []);

  return {
    theme,
    isDark: theme === 'dark',
    toggle: () => themeManager.toggle(),
    setTheme: (t) => themeManager.setTheme(t)
  };
}
```

### Componente Theme Toggle

```javascript
// src/components/ThemeToggle.js
import React from 'react';
import { useTheme } from '../hooks/useTheme';
import '../styles/components/theme-toggle.css';

function ThemeToggle() {
  const { isDark, toggle } = useTheme();

  return (
    <button 
      className="theme-toggle"
      onClick={toggle}
      aria-label="Alternar modo escuro/claro"
      title={isDark ? 'Modo claro' : 'Modo escuro'}
    >
      {isDark ? '☀️' : '🌙'}
    </button>
  );
}

export default ThemeToggle;
```

---

## 📱 **Fase 3: Responsividade Mobile-First**

### src/styles/breakpoints.css

```css
/* Mobile-First Approach */

/* 320px - 480px */
@media screen and (max-width: 480px) {
  :root {
    --font-size-base: 14px;
    --spacing-4: 0.75rem;
  }
  
  .header { padding: var(--spacing-2); }
  .main-content { padding: var(--spacing-3); }
  .grid { grid-template-columns: 1fr; }
}

/* 481px - 768px (Tablets) */
@media screen and (min-width: 481px) and (max-width: 768px) {
  .header { padding: var(--spacing-3); }
  .grid { grid-template-columns: repeat(2, 1fr); }
}

/* 769px - 1024px (Desktops pequenos) */
@media screen and (min-width: 769px) {
  .grid { grid-template-columns: repeat(3, 1fr); }
  .sidebar { width: 250px; }
}

/* 1025px+ (Large Desktops) */
@media screen and (min-width: 1025px) {
  .grid { grid-template-columns: repeat(4, 1fr); }
  .container { max-width: 1200px; }
}
```

### Componentes Responsivos

```javascript
// src/components/ResponsiveGrid.js
import React from 'react';
import '../styles/components/responsive-grid.css';

function ResponsiveGrid({ children, columns = 3 }) {
  return (
    <div className={`grid grid-cols-${columns}`}>
      {children}
    </div>
  );
}

export default ResponsiveGrid;
```

### CSS do Grid

```css
.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-4);
  width: 100%;
}

@media (max-width: 1024px) {
  .grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
  .grid { grid-template-columns: 1fr; }
}
```

---

## 🧩 **Fase 4: Componentes UI Reutilizáveis**

### src/components/Button.js

```javascript
import React from 'react';
import '../styles/components/button.css';

function Button({
  children,
  variant = 'primary',    // primary, secondary, danger, ghost
  size = 'md',            // sm, md, lg
  disabled = false,
  onClick,
  fullWidth = false,
  ...props
}) {
  return (
    <button
      className={`btn btn--${variant} btn--${size} ${fullWidth ? 'btn--full' : ''}`}
      disabled={disabled}
      onClick={onClick}
      {...props}
    >
      {children}
    </button>
  );
}

export default Button;
```

### src/styles/components/button.css

```css
.btn {
  padding: var(--spacing-3) var(--spacing-4);
  border: none;
  border-radius: var(--radius-lg);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-normal);
  font-family: var(--font-family-base);
}

/* Variants */
.btn--primary {
  background-color: var(--color-primary-500);
  color: white;
}

.btn--primary:hover:not(:disabled) {
  background-color: var(--color-primary-600);
  box-shadow: var(--shadow-md);
}

.btn--secondary {
  background-color: var(--color-neutral-200);
  color: var(--color-neutral-900);
}

.btn--secondary:hover:not(:disabled) {
  background-color: var(--color-neutral-300);
}

.btn--danger {
  background-color: var(--color-error-500);
  color: white;
}

.btn--danger:hover:not(:disabled) {
  background-color: var(--color-error-600);
}

.btn--ghost {
  background-color: transparent;
  color: var(--color-primary-500);
  border: 1px solid var(--color-primary-500);
}

.btn--ghost:hover:not(:disabled) {
  background-color: var(--color-primary-50);
}

/* Sizes */
.btn--sm {
  padding: var(--spacing-2) var(--spacing-3);
  font-size: var(--font-size-sm);
}

.btn--lg {
  padding: var(--spacing-4) var(--spacing-6);
  font-size: var(--font-size-lg);
}

/* States */
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn--full {
  width: 100%;
}
```

### src/components/Card.js

```javascript
import React from 'react';
import '../styles/components/card.css';

function Card({ children, className = '', ...props }) {
  return (
    <div className={`card ${className}`} {...props}>
      {children}
    </div>
  );
}

export default Card;
```

### src/styles/components/card.css

```css
.card {
  background-color: var(--color-neutral-50);
  border-radius: var(--radius-lg);
  padding: var(--spacing-6);
  box-shadow: var(--shadow-base);
  transition: all var(--transition-normal);
  border: 1px solid var(--color-neutral-200);
}

.card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

[data-theme="dark"] .card {
  background-color: var(--color-neutral-800);
  border-color: var(--color-neutral-700);
}
```

### src/components/Input.js

```javascript
import React, { forwardRef } from 'react';
import '../styles/components/input.css';

const Input = forwardRef(
  ({ label, error, helperText, ...props }, ref) => {
    return (
      <div className="input-group">
        {label && <label className="input-label">{label}</label>}
        <input
          ref={ref}
          className={`input ${error ? 'input--error' : ''}`}
          {...props}
        />
        {(error || helperText) && (
          <span className={`input-help ${error ? 'text-error' : ''}`}>
            {error || helperText}
          </span>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
export default Input;
```

### src/styles/components/input.css

```css
.input-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
  margin-bottom: var(--spacing-4);
}

.input-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-neutral-700);
}

[data-theme="dark"] .input-label {
  color: var(--color-neutral-300);
}

.input {
  padding: var(--spacing-3) var(--spacing-4);
  border: 1px solid var(--color-neutral-300);
  border-radius: var(--radius-lg);
  font-size: var(--font-size-base);
  font-family: var(--font-family-base);
  transition: border-color var(--transition-fast);
}

.input:focus {
  outline: none;
  border-color: var(--color-primary-500);
  box-shadow: 0 0 0 3px var(--color-primary-50);
}

.input--error {
  border-color: var(--color-error-500);
}

.input--error:focus {
  box-shadow: 0 0 0 3px var(--color-error-50);
}

.input-help {
  font-size: var(--font-size-xs);
  color: var(--color-neutral-500);
}

.text-error {
  color: var(--color-error-500);
}

[data-theme="dark"] .input {
  background-color: var(--color-neutral-800);
  border-color: var(--color-neutral-600);
  color: var(--color-neutral-50);
}

[data-theme="dark"] .input:focus {
  border-color: var(--color-primary-400);
  box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.1);
}
```

---

## ✨ **Fase 5: Animações & Transições**

### src/styles/animations.css

```css
/* Fade In */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Slide Down */
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Scale Up */
@keyframes scaleUp {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Loading Spinner */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Aplicar animações */
.fade-in { animation: fadeIn var(--transition-normal); }
.slide-down { animation: slideDown var(--transition-fast); }
.scale-up { animation: scaleUp var(--transition-normal); }

/* Loading Spinner */
.spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid var(--color-neutral-200);
  border-top-color: var(--color-primary-500);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
```

---

## ♿ **Fase 6: Acessibilidade (a11y)**

### Componente Accessible Modal

```javascript
import React, { useEffect, useRef } from 'react';
import '../styles/components/modal.css';

function Modal({ isOpen, onClose, title, children }) {
  const modalRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      // Tratar foco
      modalRef.current?.focus();
      // Desabilitar scroll
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'auto';
    }

    return () => {
      document.body.style.overflow = 'auto';
    };
  }, [isOpen]);

  const handleKeyDown = (e) => {
    if (e.key === 'Escape') onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        ref={modalRef}
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        onKeyDown={handleKeyDown}
        onClick={(e) => e.stopPropagation()}
        tabIndex={-1}
      >
        <h2 id="modal-title" className="modal-title">{title}</h2>
        {children}
      </div>
    </div>
  );
}

export default Modal;
```

### Boas Práticas a11y

```javascript
// Usar semantic HTML
<button>❌ <div onClick={...}>Click me</div>
<button>✅ <button onClick={...}>Click me</button>

// ARIA Labels
<button aria-label="Fechar modal">✕</button>

// Contraste de cores
// Verificar em: https://www.contrast-ratio.com/

// Focus management
<input autoFocus />

// Screen reader text
<span class="sr-only">texto para screen readers</span>
```

---

## 🎬 **Fase 7: Componentes de Feedback**

### src/components/Alert.js

```javascript
import React from 'react';
import '../styles/components/alert.css';

function Alert({ type = 'info', title, message, onClose }) {
  const icons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ'
  };

  return (
    <div className={`alert alert--${type}`} role="alert">
      <span className="alert-icon">{icons[type]}</span>
      <div className="alert-content">
        {title && <strong>{title}</strong>}
        <p>{message}</p>
      </div>
      {onClose && (
        <button 
          className="alert-close" 
          onClick={onClose}
          aria-label="Fechar alerta"
        >
          ×
        </button>
      )}
    </div>
  );
}

export default Alert;
```

### src/styles/components/alert.css

```css
.alert {
  display: flex;
  gap: var(--spacing-4);
  padding: var(--spacing-4);
  border-radius: var(--radius-lg);
  border-left: 4px solid;
  background-color: var(--color-neutral-50);
}

.alert--success {
  border-color: var(--color-success-500);
  background-color: var(--color-success-50);
}

.alert--error {
  border-color: var(--color-error-500);
  background-color: var(--color-error-50);
}

.alert--warning {
  border-color: var(--color-warning-500);
  background-color: var(--color-warning-50);
}

.alert--info {
  border-color: var(--color-primary-500);
  background-color: var(--color-primary-50);
}

.alert-content { flex: 1; }

.alert-close {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.5rem;
  opacity: 0.5;
  transition: opacity var(--transition-fast);
}

.alert-close:hover {
  opacity: 1;
}
```

---

## 📚 **Storybook (Documentação de Componentes)**

```bash
# Instalar Storybook
npx storybook@latest init

# Criar histórias
# src/components/Button.stories.js
export default {
  title: 'Components/Button',
  component: Button,
};

export const Primary = () => <Button variant="primary">Click me</Button>;
export const Secondary = () => <Button variant="secondary">Click me</Button>;
export const Disabled = () => <Button disabled>Disabled</Button>;

# Executar Storybook
npm run storybook

# Acessa em http://localhost:6006
```

---

## 📋 **Checklist de Design System**

- [ ] Design tokens (cores, tipos, espaçamento)
- [ ] Dark mode totalmente funcional
- [ ] Responsividade testada em 3+ dispositivos
- [ ] Componentes UI básicos criados (Button, Input, Card, Alert)
- [ ] Animações suaves sem performance issues
- [ ] Acessibilidade verificada (a11y audit)
- [ ] Storybook documentando componentes
- [ ] Guia de estilo criado e compartilhado

---

## 🎨 **Inspirações de Design**

- **Tailwind UI**: https://tailwindui.com/
- **Material Design**: https://material.io/design
- **Ant Design**: https://ant.design/
- **Chakra UI**: https://chakra-ui.com/

---

## 🚀 **Próximas Etapas**

1. Implementar Design Tokens (variáveis CSS)
2. Ativar Dark Mode
3. Testar Responsividade
4. Criar biblioteca de componentes
5. Documentar no Storybook
6. Auditar acessibilidade
7. Otimizar performance

**Boa sorte com o design! 🎉**
