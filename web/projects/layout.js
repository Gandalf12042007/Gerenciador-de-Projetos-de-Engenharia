/**
 * Layout Manager - Injects the sidebar and handles global UI state
 * Gerenciador de Projetos de Engenharia
 */

document.addEventListener('DOMContentLoaded', () => {
    initLayout();
});

function initLayout() {
    // Add page loader
    const loader = document.createElement('div');
    loader.className = 'page-loader';
    loader.innerHTML = '<div class="spinner"></div>';
    document.body.appendChild(loader);
    
    // Hide loader after a short delay
    setTimeout(() => {
        loader.classList.add('hidden');
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
    
    // Create the app-layout wrapper
    const appLayout = document.createElement('div');
    appLayout.className = 'app-layout';
    
    // Detectar se estamos na pasta projects ou na raiz
    const isInProjectsFolder = currentPath.includes('/projects/');
    const pathPrefix = isInProjectsFolder ? '../' : '';
    const projectsPrefix = isInProjectsFolder ? '' : 'projects/';
    
    // Create the sidebar
    const sidebar = document.createElement('aside');
    sidebar.className = 'sidebar';
    sidebar.innerHTML = `
        <div class="sidebar-header">
            <span class="sidebar-logo">🏗️</span>
            <span class="sidebar-title">EngenhariaPro</span>
        </div>
        <nav class="sidebar-nav">
            <a href="${projectsPrefix}index.html" class="nav-item ${currentPath.includes('index.html') || currentPath.endsWith('/projects/') ? 'active' : ''}">
                <span class="nav-icon">�</span>
                <span>Dashboard</span>
            </a>
            <a href="${projectsPrefix}kanban.html" class="nav-item ${currentPath.includes('kanban.html') ? 'active' : ''}">
                <span class="nav-icon">📋</span>
                <span>Tarefas</span>
            </a>
            <a href="${projectsPrefix}docs.html" class="nav-item ${currentPath.includes('docs.html') ? 'active' : ''}">
                <span class="nav-icon">📄</span>
                <span>Documentos</span>
            </a>
            <a href="${projectsPrefix}equipes.html" class="nav-item ${currentPath.includes('equipes.html') ? 'active' : ''}">
                <span class="nav-icon">👥</span>
                <span>Equipe</span>
            </a>
            <a href="${projectsPrefix}chat.html" class="nav-item ${currentPath.includes('chat.html') ? 'active' : ''}">
                <span class="nav-icon">💬</span>
                <span>Chat</span>
            </a>
            <a href="${projectsPrefix}timeline.html" class="nav-item ${currentPath.includes('timeline.html') ? 'active' : ''}">
                <span class="nav-icon">📅</span>
                <span>Cronograma</span>
            </a>
            <a href="${projectsPrefix}budget.html" class="nav-item ${currentPath.includes('budget.html') ? 'active' : ''}">
                <span class="nav-icon">💰</span>
                <span>Orçamentos</span>
            </a>
            <a href="${projectsPrefix}materials.html" class="nav-item ${currentPath.includes('materials.html') ? 'active' : ''}">
                <span class="nav-icon">📦</span>
                <span>Materiais</span>
            </a>
            <a href="${projectsPrefix}metrics.html" class="nav-item ${currentPath.includes('metrics.html') ? 'active' : ''}">
                <span class="nav-icon">📈</span>
                <span>Métricas</span>
            </a>
        </nav>
        <div class="sidebar-footer">
            <div class="user-profile" id="sidebarProfile">
                <div class="user-avatar" id="sidebarAvatar">U</div>
                <div class="user-info">
                    <span class="user-name" id="sidebarUserName">Usuário</span>
                    <span class="user-role" id="sidebarUserRole">Engenheiro</span>
                </div>
            </div>
        </div>
    `;
    
    // Create sidebar overlay for mobile
    const sidebarOverlay = document.createElement('div');
    sidebarOverlay.className = 'sidebar-overlay';
    sidebarOverlay.addEventListener('click', () => {
        sidebar.classList.remove('open');
    });
    
    // Create the main content area
    const mainContent = document.createElement('main');
    mainContent.className = 'main-content';
    
    // Create the top bar
    const topBar = document.createElement('header');
    topBar.className = 'top-bar';
    
    const pageTitleText = document.title.split('—')[0].split('-')[0].trim();
    
    topBar.innerHTML = `
        <button class="menu-toggle" id="menuToggle">☰</button>
        <h1 class="page-title">${pageTitleText}</h1>
        <div class="top-actions">
            <button id="layoutNotifications" class="btn-icon" title="Notificações">🔔</button>
            <button id="layoutProfile" class="btn-icon" title="Perfil">👤</button>
            <button id="layoutLogout" class="btn-icon" title="Sair">🚪</button>
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
    
    // Assemble the layout
    mainContent.appendChild(topBar);
    
    const contentWrapper = document.createElement('div');
    contentWrapper.className = 'content-wrapper animate-fade-in';
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
        sidebar.classList.toggle('open');
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
            userAvatar.style.background = 'linear-gradient(135deg, #F59E0B, #D97706)';
            userAvatar.style.border = '2px solid #FCD34D';
        }
    }
    
    if (userRole) {
        // Se é admin, mostrar badge especial
        if (userData.is_admin) {
            userRole.innerHTML = '<span style="color: #F59E0B; font-weight: 600;">👑 Administrador</span>';
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

// Função para mostrar toast notifications
function showToast(message, type = 'info') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span>${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">✕</button>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

// Expor função globalmente
window.showToast = showToast;
