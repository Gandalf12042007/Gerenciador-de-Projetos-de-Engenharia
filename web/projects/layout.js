/**
 * Layout Manager - Jira-like Professional Theme
 * Gerenciador de Projetos de Engenharia
 */

document.addEventListener('DOMContentLoaded', () => {
    initJiraLayout();
});

function initJiraLayout() {
    // Add Jira theme class to body
    document.body.classList.add('jira-theme');
    
    // Add page loader
    const loader = document.createElement('div');
    loader.className = 'page-loader';
    loader.innerHTML = '<div class="jira-spinner"></div>';
    document.body.appendChild(loader);
    
    // Hide loader after a short delay
    setTimeout(() => {
        loader.classList.add('hidden');
        loader.style.display = 'none';
    }, 400);

    const body = document.body;
    const currentPath = window.location.pathname;
    
    // Detectar se estamos em uma página que não precisa de layout (login, register, etc)
    const noLayoutPages = ['login.html', 'register.html', 'forgot-password.html', 'reset-password.html'];
    const isNoLayoutPage = noLayoutPages.some(page => currentPath.includes(page));
    
    if (isNoLayoutPage) {
        loader.classList.add('hidden');
        return;
    }
    
    // Create the Jira-like layout wrapper
    const appLayout = document.createElement('div');
    appLayout.className = 'jira-layout';
    
    // Detectar se estamos na pasta projects ou na raiz
    const isInProjectsFolder = currentPath.includes('/projects/');
    const pathPrefix = isInProjectsFolder ? '../' : '';
    const projectsPrefix = isInProjectsFolder ? '' : 'projects/';
    
    // Create the Jira-style sidebar
    const sidebar = document.createElement('aside');
    sidebar.className = 'jira-sidebar';
    sidebar.innerHTML = `
        <div class="sidebar-logo">
            <div class="sidebar-logo-icon">🏗️</div>
            <span class="sidebar-logo-text">EngenhariaPro</span>
        </div>
        <nav class="sidebar-nav">
            <span class="nav-section-title">Navegação</span>
            <a href="${projectsPrefix}index.html" class="jira-nav-item ${currentPath.includes('index.html') || currentPath.endsWith('/projects/') ? 'active' : ''}">
                <span class="nav-icon">📊</span>
                <span class="nav-label">Projetos</span>
            </a>
            <a href="${projectsPrefix}dashboard.html" class="jira-nav-item ${currentPath.includes('dashboard.html') ? 'active' : ''}">
                <span class="nav-icon">📈</span>
                <span class="nav-label">Dashboard</span>
            </a>
            <a href="${projectsPrefix}kanban.html" class="jira-nav-item ${currentPath.includes('kanban.html') ? 'active' : ''}">
                <span class="nav-icon">📋</span>
                <span class="nav-label">Quadro Kanban</span>
            </a>
            
            <span class="nav-section-title">Gestão</span>
            <a href="${projectsPrefix}docs.html" class="jira-nav-item ${currentPath.includes('docs.html') ? 'active' : ''}">
                <span class="nav-icon">📄</span>
                <span class="nav-label">Documentos</span>
            </a>
            <a href="${projectsPrefix}equipes.html" class="jira-nav-item ${currentPath.includes('equipes.html') ? 'active' : ''}">
                <span class="nav-icon">👥</span>
                <span class="nav-label">Equipe</span>
            </a>
            <a href="${projectsPrefix}timeline.html" class="jira-nav-item ${currentPath.includes('timeline.html') ? 'active' : ''}">
                <span class="nav-icon">📅</span>
                <span class="nav-label">Cronograma</span>
            </a>
            
            <span class="nav-section-title">Financeiro</span>
            <a href="${projectsPrefix}budget.html" class="jira-nav-item ${currentPath.includes('budget.html') ? 'active' : ''}">
                <span class="nav-icon">💰</span>
                <span class="nav-label">Orçamentos</span>
            </a>
            <a href="${projectsPrefix}materials.html" class="jira-nav-item ${currentPath.includes('materials.html') ? 'active' : ''}">
                <span class="nav-icon">📦</span>
                <span class="nav-label">Materiais</span>
            </a>
            
            <span class="nav-section-title">Comunicação</span>
            <a href="${projectsPrefix}chat.html" class="jira-nav-item ${currentPath.includes('chat.html') ? 'active' : ''}">
                <span class="nav-icon">💬</span>
                <span class="nav-label">Chat IA</span>
            </a>
        </nav>
        <div class="sidebar-footer">
            <div class="sidebar-user" id="sidebarProfile">
                <div class="user-avatar-jira" id="sidebarAvatar">U</div>
                <div class="user-info-jira">
                    <span class="user-name-jira" id="sidebarUserName">Usuário</span>
                    <span class="user-role-jira" id="sidebarUserRole">Engenheiro</span>
                </div>
            </div>
        </div>
    `;
    
    // Create sidebar overlay for mobile
    const sidebarOverlay = document.createElement('div');
    sidebarOverlay.className = 'sidebar-overlay';
    sidebarOverlay.addEventListener('click', () => {
        sidebar.classList.remove('mobile-open');
    });
    
    // Create the Jira-style main content area
    const mainContent = document.createElement('main');
    mainContent.className = 'jira-main';
    
    // Create the Jira-style header
    const topBar = document.createElement('header');
    topBar.className = 'jira-header';
    
    const pageTitleText = document.title.split('—')[0].split('-')[0].trim();
    
    topBar.innerHTML = `
        <div class="header-left">
            <button class="btn-jira-icon menu-toggle" id="menuToggle">☰</button>
            <h1 class="page-title-jira">${pageTitleText}</h1>
        </div>
        <div class="header-right">
            <div class="header-search">
                <input type="text" placeholder="Buscar..." id="globalSearch">
            </div>
            <button id="layoutNotifications" class="btn-jira-icon" title="Notificações">🔔</button>
            <button id="layoutProfile" class="btn-jira-icon" title="Perfil">👤</button>
            <button id="layoutLogout" class="btn-jira-icon btn-jira-danger" title="Sair" style="background:#DE350B;color:white;">🚪</button>
        </div>
    `;
    
    // Get existing body content
    const originalContent = Array.from(body.childNodes);
    
    // Filter out scripts, links, and old headers we want to replace
    const contentToMove = originalContent.filter(node => {
        if (node.tagName === 'SCRIPT' || node.tagName === 'LINK' || node.tagName === 'STYLE') return false;
        if (node.classList && (node.classList.contains('topbar') || node.classList.contains('navbar') || node.classList.contains('top-bar'))) return false;
        if (node.tagName === 'HEADER') return false;
        return true;
    });
    
    // Assemble the Jira layout
    mainContent.appendChild(topBar);
    
    const contentWrapper = document.createElement('div');
    contentWrapper.className = 'jira-content';
    contentToMove.forEach(node => contentWrapper.appendChild(node));
    mainContent.appendChild(contentWrapper);
    
    appLayout.appendChild(sidebar);
    appLayout.appendChild(sidebarOverlay);
    appLayout.appendChild(mainContent);
    
    // Clear body and append layout (keeping scripts and styles)
    const scripts = Array.from(document.querySelectorAll('script, link, style'));
    body.innerHTML = '';
    scripts.forEach(s => body.appendChild(s));
    body.appendChild(appLayout);
    
    // Add Event Listeners
    document.getElementById('menuToggle')?.addEventListener('click', () => {
        sidebar.classList.toggle('mobile-open');
    });
    
    document.getElementById('layoutLogout')?.addEventListener('click', () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_data');
        window.location.href = pathPrefix + 'login.html';
    });
    
    document.getElementById('layoutNotifications')?.addEventListener('click', () => {
        window.location.href = pathPrefix + 'notifications.html';
    });
    
    document.getElementById('layoutProfile')?.addEventListener('click', () => {
        window.location.href = pathPrefix + 'profile.html';
    });
    
    // Update user info if available
    updateUserInfo();
}

function updateUserInfo() {
    const userData = JSON.parse(localStorage.getItem('user_data') || '{}');
    const userName = document.getElementById('sidebarUserName');
    const userAvatar = document.getElementById('sidebarAvatar');
    const userRole = document.getElementById('sidebarUserRole');
    
    if (userData.nome && userName) {
        userName.textContent = userData.nome;
    }
    
    if (userData.nome && userAvatar) {
        userAvatar.textContent = userData.nome.charAt(0).toUpperCase();
        // Adicionar estilo especial para admin
        if (userData.is_admin) {
            userAvatar.style.background = 'linear-gradient(135deg, #FFAB00, #FF8B00)';
        }
    }
    
    if (userRole) {
        // Se é admin, mostrar badge especial
        if (userData.is_admin) {
            userRole.innerHTML = '<span style="color: #FFAB00;">👑 Admin</span>';
        } else if (userData.cargo) {
            const cargoMap = {
                'admin': 'Administrador',
                'gerente': 'Gerente',
                'engenheiro': 'Engenheiro',
                'tecnico': 'Técnico',
                'colaborador': 'Colaborador'
            };
            userRole.textContent = cargoMap[userData.cargo] || userData.cargo;
        }
    }
}

// Função para mostrar toast notifications - Jira style
function showToast(message, type = 'info') {
    let container = document.querySelector('.jira-toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'jira-toast-container';
        document.body.appendChild(container);
    }
    
    const icons = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    };
    
    const toast = document.createElement('div');
    toast.className = `jira-toast ${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span class="toast-message">${message}</span>
        <button class="btn-jira-icon" onclick="this.parentElement.remove()" style="width:24px;height:24px;">✕</button>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.style.animation = 'fadeOut 200ms ease-out forwards';
        setTimeout(() => toast.remove(), 200);
    }, 5000);
}

// Expor função globalmente
window.showToast = showToast;
