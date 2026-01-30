/**
 * APP.JS - Lógica da Aplicação
 * Controla navegação, eventos e comunicação com API
 */

// ============ STATE GLOBAL ============
let currentUser = null;
let projetos = [];
let tarefas = [];
let documentos = [];

// ============ INICIALIZAÇÃO ============
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

function initializeApp() {
    // Verificar se usuário está logado
    const token = localStorage.getItem('access_token');
    const userStr = localStorage.getItem('user');

    if (token && userStr) {
        try {
            currentUser = JSON.parse(userStr);
            showMainScreen();
        } catch (e) {
            localStorage.clear();
            showLoginScreen();
        }
    } else {
        showLoginScreen();
    }

    // Eventos de formulário
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('register-form').addEventListener('submit', handleRegister);
    document.getElementById('project-form').addEventListener('submit', handleCreateProject);
    document.getElementById('task-form').addEventListener('submit', handleCreateTask);
    document.getElementById('upload-form').addEventListener('submit', handleUploadDocument);

    // Eventos de navegação
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
    document.getElementById('menu-toggle').addEventListener('click', toggleSidebar);

    // Fechar sidebar ao clicar em um link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            const sidebar = document.getElementById('sidebar');
            if (sidebar.classList.contains('active')) {
                sidebar.classList.remove('active');
                document.getElementById('menu-toggle').classList.remove('active');
            }
        });
    });

    // Filtros
    document.getElementById('status-filter').addEventListener('change', filterTasks);
    document.getElementById('project-filter').addEventListener('change', filterTasks);
}

// ============ TELAS ============
function showLoginScreen(event) {
    if (event) event.preventDefault();
    document.getElementById('login-screen').classList.add('active');
    document.getElementById('register-screen').classList.remove('active');
    document.getElementById('main-screen').classList.remove('active');
}

function showRegisterScreen(event) {
    event.preventDefault();
    document.getElementById('login-screen').classList.remove('active');
    document.getElementById('register-screen').classList.add('active');
    document.getElementById('main-screen').classList.remove('active');
}

function showMainScreen() {
    document.getElementById('login-screen').classList.remove('active');
    document.getElementById('register-screen').classList.remove('active');
    document.getElementById('main-screen').classList.add('active');

    // Atualizar informações do usuário
    document.getElementById('user-name').textContent = currentUser.nome || currentUser.email;

    // Carregar dashboard
    showDashboard();
    loadDashboardData();
}

// ============ NAVEGAÇÃO ============
function showPage(pageId) {
    // Remover 'active' de todas as páginas
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });

    // Adicionar 'active' na página selecionada
    document.getElementById(pageId).classList.add('active');

    // Atualizar nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.page === pageId.replace('-page', '')) {
            link.classList.add('active');
        }
    });
}

function showDashboard(event) {
    if (event) event.preventDefault();
    showPage('dashboard-page');
    loadDashboardData();
}

function showProjects(event) {
    if (event) event.preventDefault();
    showPage('projects-page');
    loadProjects();
}

function showTasks(event) {
    if (event) event.preventDefault();
    showPage('tasks-page');
    loadTasks();
    loadProjectsForFilters();
}

function showDocuments(event) {
    if (event) event.preventDefault();
    showPage('documents-page');
    loadDocuments();
}

function showTeam(event) {
    if (event) event.preventDefault();
    showPage('team-page');
    loadTeams();
}

function showMetrics(event) {
    if (event) event.preventDefault();
    showPage('metrics-page');
    loadMetrics();
}

function toggleSidebar(event) {
    event.preventDefault();
    const sidebar = document.getElementById('sidebar');
    const toggle = document.getElementById('menu-toggle');
    sidebar.classList.toggle('active');
    toggle.classList.toggle('active');
}

// ============ AUTENTICAÇÃO ============
async function handleLogin(event) {
    event.preventDefault();

    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorDiv = document.getElementById('login-error');

    try {
        showLoading(true);
        const response = await api.login(email, password);

        // Backend retorna: { access_token, token_type, user_id, nome, email }
        const user = {
            id: response.user_id,
            nome: response.nome,
            email: response.email
        };

        // Salvar autenticação
        api.setAuth(response.access_token, user);
        currentUser = user;

        // Limpar formulário
        document.getElementById('login-form').reset();
        errorDiv.style.display = 'none';

        // Ir para dashboard
        showMainScreen();
        showToast('Bem-vindo!', 'success');
    } catch (error) {
        errorDiv.textContent = error.message || 'Erro ao fazer login';
        errorDiv.style.display = 'block';
    } finally {
        showLoading(false);
    }
}

async function handleRegister(event) {
    event.preventDefault();

    const nome = document.getElementById('register-name').value;
    const email = document.getElementById('register-email').value;
    const senha = document.getElementById('register-password').value;
    const cargo = document.getElementById('register-cargo').value;
    const errorDiv = document.getElementById('register-error');

    try {
        showLoading(true);
        const response = await api.register(nome, email, senha, cargo);

        // Limpar formulário
        document.getElementById('register-form').reset();
        errorDiv.style.display = 'none';

        // Mensagem e voltar para login
        showToast('Conta criada com sucesso! Faça login.', 'success');
        setTimeout(() => showLoginScreen(), 1500);
    } catch (error) {
        errorDiv.textContent = error.message || 'Erro ao criar conta';
        errorDiv.style.display = 'block';
    } finally {
        showLoading(false);
    }
}

function handleLogout(event) {
    event.preventDefault();
    api.logout();
    localStorage.clear();
    currentUser = null;
    showLoginScreen();
    showToast('Você foi desconectado', 'info');
}

// ============ DASHBOARD ============
async function loadDashboardData() {
    try {
        showLoading(true);

        // Carregar projetos
        const projetosResponse = await api.getProjetos();
        projetos = projetosResponse.data || projetosResponse || [];

        // Inicializar contadores
        let totalTarefas = 0;
        let totalDocumentos = 0;
        tarefas = [];
        documentos = [];

        // Carregar tarefas e documentos de cada projeto
        for (const projeto of projetos.slice(0, 5)) {
            try {
                const tarefasProjeto = await api.getTarefasByProjeto(projeto.id);
                const tarefasData = tarefasProjeto.data || tarefasProjeto || [];
                tarefas = tarefas.concat(tarefasData);
                totalTarefas += tarefasData.length;
            } catch (e) {
                console.warn(`Erro ao carregar tarefas do projeto ${projeto.id}`);
            }

            try {
                const docsProjeto = await api.getDocumentosByProjeto(projeto.id);
                const docsData = docsProjeto.data || docsProjeto || [];
                documentos = documentos.concat(docsData);
                totalDocumentos += docsData.length;
            } catch (e) {
                console.warn(`Erro ao carregar documentos do projeto ${projeto.id}`);
            }
        }

        // Atualizar estatísticas
        document.getElementById('stat-projects').textContent = projetos.length;
        document.getElementById('stat-tasks').textContent = totalTarefas;
        document.getElementById('stat-documents').textContent = totalDocumentos;

        // Calcular progresso médio
        const progresso = projetos.length > 0
            ? Math.round(projetos.reduce((sum, p) => sum + (p.progresso || 0), 0) / projetos.length)
            : 0;
        document.getElementById('stat-progress').textContent = progresso + '%';

        // Mostrar projetos recentes
        const recentProjects = projetos.slice(0, 5);
        const recentList = document.getElementById('recent-projects');
        recentList.innerHTML = recentProjects.map(p => `
            <div class="list-item">
                <strong>${p.nome}</strong>
                <span>${p.status} • ${p.progresso || 0}%</span>
            </div>
        `).join('');

        // Mostrar tarefas pendentes
        const pendingTasks = tarefas.filter(t => t.status !== 'Concluído').slice(0, 5);
        const pendingList = document.getElementById('pending-tasks');
        pendingList.innerHTML = pendingTasks.map(t => `
            <div class="list-item">
                <strong>${t.titulo}</strong>
                <span>${t.prioridade} • ${t.status}</span>
            </div>
        `).join('');
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// ============ PROJETOS ============
async function loadProjects() {
    try {
        showLoading(true);
        const response = await api.getProjetos();
        projetos = response.data || response;

        const grid = document.getElementById('projects-list');
        grid.innerHTML = projetos.map(projeto => `
            <div class="project-card">
                <div class="project-header">
                    <div class="project-title">${projeto.nome}</div>
                    <span class="project-status">${projeto.status || 'Planejamento'}</span>
                </div>
                <div class="project-client">${projeto.cliente || 'Sem cliente'}</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${projeto.progresso || 0}%"></div>
                </div>
                <div class="project-footer">
                    <span>R$ ${(projeto.orcamento || 0).toLocaleString('pt-BR')}</span>
                    <div>
                        <button class="btn btn-small" onclick="editProject(${projeto.id})">Editar</button>
                        <button class="btn btn-danger btn-small" onclick="deleteProject(${projeto.id})">Deletar</button>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        showLoading(false);
    }
}

function showNewProjectModal() {
    document.getElementById('project-modal').classList.add('active');
}

async function handleCreateProject(event) {
    event.preventDefault();

    const nome = document.getElementById('project-name').value;
    const descricao = document.getElementById('project-description').value;
    const cliente = document.getElementById('project-cliente').value;
    const orcamento = parseFloat(document.getElementById('project-orcamento').value) || 0;

    try {
        showLoading(true);
        await api.createProjeto({
            nome,
            descricao,
            cliente,
            orcamento,
            status: 'Planejamento',
            progresso: 0,
        });

        document.getElementById('project-form').reset();
        closeModal('project-modal');
        loadProjects();
        showToast('Projeto criado com sucesso!', 'success');
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        showLoading(false);
    }
}

async function deleteProject(id) {
    if (!confirm('Tem certeza que deseja deletar este projeto?')) return;

    try {
        showLoading(true);
        await api.deleteProjeto(id);
        loadProjects();
        showToast('Projeto deletado', 'success');
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        showLoading(false);
    }
}

function editProject(id) {
    showToast('Função de edição em desenvolvimento', 'info');
}

// ============ TAREFAS ============
async function loadTasks() {
    try {
        showLoading(true);
        
        // Carregar projetos primeiro
        const projetosResponse = await api.getProjetos();
        const projetosData = projetosResponse.data || projetosResponse || [];
        
        // Carregar tarefas de todos os projetos
        tarefas = [];
        for (const projeto of projetosData) {
            try {
                const tarefasProjeto = await api.getTarefasByProjeto(projeto.id);
                const tarefasData = tarefasProjeto.data || tarefasProjeto || [];
                // Adicionar nome do projeto para referência
                tarefasData.forEach(t => t.projeto_nome = projeto.nome);
                tarefas = tarefas.concat(tarefasData);
            } catch (e) {
                console.warn(`Erro ao carregar tarefas do projeto ${projeto.id}`);
            }
        }
        
        renderKanbanBoard();
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        showLoading(false);
    }
}

async function loadProjectsForFilters() {
    try {
        const response = await api.getProjetos();
        const projetosData = response.data || response;

        // Preencher selects de projetos
        const selects = ['task-projeto', 'upload-projeto'];
        selects.forEach(selectId => {
            const select = document.getElementById(selectId);
            select.innerHTML = '<option value="">Selecione um projeto</option>' +
                projetosData.map(p => `<option value="${p.id}">${p.nome}</option>`).join('');
        });

        // Filtro de projetos
        document.getElementById('project-filter').innerHTML =
            '<option value="">Todos os Projetos</option>' +
            projetosData.map(p => `<option value="${p.id}">${p.nome}</option>`).join('');
    } catch (error) {
        console.error('Erro ao carregar projetos:', error);
    }
}

function renderKanbanBoard() {
    // Backend usa: a_fazer, em_execucao, concluida
    const todoTasks = tarefas.filter(t => t.status === 'a_fazer' || t.status === 'A fazer');
    const doingTasks = tarefas.filter(t => t.status === 'em_execucao' || t.status === 'Em andamento');
    const doneTasks = tarefas.filter(t => t.status === 'concluida' || t.status === 'Concluído');

    document.getElementById('tasks-todo').innerHTML = todoTasks.map(renderTaskCard).join('');
    document.getElementById('tasks-doing').innerHTML = doingTasks.map(renderTaskCard).join('');
    document.getElementById('tasks-done').innerHTML = doneTasks.map(renderTaskCard).join('');
}

function renderTaskCard(tarefa) {
    const priorityClass = `priority-${tarefa.prioridade?.toLowerCase() || 'medium'}`;
    return `
        <div class="task-card">
            <div class="task-title">${tarefa.titulo}</div>
            <div class="task-meta">
                <span class="${priorityClass}">${tarefa.prioridade || 'Média'}</span>
                <span>${tarefa.data_vencimento ? new Date(tarefa.data_vencimento).toLocaleDateString('pt-BR') : ''}</span>
            </div>
        </div>
    `;
}

function filterTasks() {
    const projectId = document.getElementById('project-filter').value;
    const status = document.getElementById('status-filter').value;

    let filtered = tarefas;

    if (projectId) {
        filtered = filtered.filter(t => t.projeto_id === parseInt(projectId));
    }

    if (status) {
        filtered = filtered.filter(t => t.status === status);
    }

    tarefas = filtered;
    renderKanbanBoard();
}

function showNewTaskModal() {
    loadProjectsForFilters();
    document.getElementById('task-modal').classList.add('active');
}

async function handleCreateTask(event) {
    event.preventDefault();

    const titulo = document.getElementById('task-title').value;
    const projeto_id = parseInt(document.getElementById('task-projeto').value);
    const descricao = document.getElementById('task-description').value;
    const prioridade = document.getElementById('task-priority').value;

    try {
        showLoading(true);
        await api.createTarefa({
            titulo,
            projeto_id,
            descricao,
            prioridade: prioridade.toLowerCase(), // backend usa minusculo
            status: 'a_fazer', // backend usa a_fazer
        });

        document.getElementById('task-form').reset();
        closeModal('task-modal');
        loadTasks();
        showToast('Tarefa criada com sucesso!', 'success');
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// ============ DOCUMENTOS ============
async function loadDocuments() {
    try {
        showLoading(true);
        
        // Carregar projetos primeiro
        const projetosResponse = await api.getProjetos();
        const projetosData = projetosResponse.data || projetosResponse || [];
        
        // Carregar documentos de todos os projetos
        documentos = [];
        for (const projeto of projetosData) {
            try {
                const docsProjeto = await api.getDocumentosByProjeto(projeto.id);
                const docsData = docsProjeto.data || docsProjeto || [];
                docsData.forEach(d => d.projeto_nome = projeto.nome);
                documentos = documentos.concat(docsData);
            } catch (e) {
                console.warn(`Erro ao carregar documentos do projeto ${projeto.id}`);
            }
        }

        const tbody = document.getElementById('documents-tbody');
        tbody.innerHTML = documentos.map(doc => `
            <tr>
                <td>
                    <strong>${doc.nome_original || doc.nome}</strong>
                </td>
                <td>${doc.projeto_nome || doc.projeto_id || '-'}</td>
                <td>${formatBytes(doc.tamanho || 0)}</td>
                <td>${new Date(doc.data_criacao || doc.created_at).toLocaleDateString('pt-BR')}</td>
                <td>
                    <div class="table-actions">
                        <a href="${api.downloadDocumentoUrl(doc.id)}" class="btn btn-small" download>Download</a>
                        <button class="btn btn-danger btn-small" onclick="deleteDocument(${doc.id})">Deletar</button>
                    </div>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        showLoading(false);
    }
}

function showUploadModal() {
    loadProjectsForFilters();
    document.getElementById('upload-modal').classList.add('active');
}

async function handleUploadDocument(event) {
    event.preventDefault();

    const projeto_id = parseInt(document.getElementById('upload-projeto').value);
    const file = document.getElementById('upload-file').files[0];

    if (!file) {
        showToast('Selecione um arquivo', 'error');
        return;
    }

    try {
        showLoading(true);
        await api.uploadDocumento(projeto_id, file);

        document.getElementById('upload-form').reset();
        closeModal('upload-modal');
        loadDocuments();
        showToast('Documento enviado com sucesso!', 'success');
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        showLoading(false);
    }
}

async function deleteDocument(id) {
    if (!confirm('Tem certeza que deseja deletar este documento?')) return;

    try {
        showLoading(true);
        await api.deleteDocumento(id);
        loadDocuments();
        showToast('Documento deletado', 'success');
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// ============ EQUIPES ============
async function loadTeams() {
    try {
        showLoading(true);
        
        // Carregar projetos primeiro
        const projetosResponse = await api.getProjetos();
        const projetosData = projetosResponse.data || projetosResponse || [];

        const grid = document.getElementById('teams-list');
        let teamsHtml = '';
        
        // Carregar membros de cada projeto
        for (const projeto of projetosData) {
            try {
                const membros = await api.getEquipesByProjeto(projeto.id);
                const membrosData = membros.data || membros || [];
                
                if (membrosData.length > 0) {
                    teamsHtml += `
                        <div class="team-card">
                            <div class="team-name">👥 ${projeto.nome}</div>
                            <div class="team-members">
                                ${membrosData.map(membro => `
                                    <div class="member-item">
                                        <div class="member-avatar">${(membro.usuario_nome || 'U')[0].toUpperCase()}</div>
                                        <div>
                                            <strong>${membro.usuario_nome || 'Usuário'}</strong>
                                            <div style="font-size: 0.8rem; color: #999;">${membro.papel || 'Membro'}</div>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `;
                }
            } catch (e) {
                console.warn(`Erro ao carregar equipe do projeto ${projeto.id}`);
            }
        }
        
        grid.innerHTML = teamsHtml || '<p>Nenhuma equipe encontrada</p>';
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// ============ MÉTRICAS ============
async function loadMetrics() {
    try {
        showLoading(true);

        // Dados básicos do dashboard
        const projetosResponse = await api.getProjetos();
        const projetosData = projetosResponse.data || projetosResponse || [];

        // Carregar tarefas de todos os projetos
        let tarefasData = [];
        for (const projeto of projetosData) {
            try {
                const tarefasProjeto = await api.getTarefasByProjeto(projeto.id);
                const dados = tarefasProjeto.data || tarefasProjeto || [];
                tarefasData = tarefasData.concat(dados);
            } catch (e) {
                console.warn(`Erro ao carregar tarefas do projeto ${projeto.id}`);
            }
        }

        // Calcular métricas
        const totalTarefas = tarefasData.length;
        const tarefasConcluidas = tarefasData.filter(t => t.status === 'concluida' || t.status === 'Concluído').length;
        const taxaConclusao = totalTarefas > 0 ? Math.round((tarefasConcluidas / totalTarefas) * 100) : 0;

        // Tempo médio (simulado)
        const tempoMedio = '12.5 dias';

        // Membros
        let totalMembros = 0;
        for (const projeto of projetosData.slice(0, 5)) {
            try {
                const membros = await api.getEquipesByProjeto(projeto.id);
                const membrosData = membros.data || membros || [];
                totalMembros += membrosData.length;
            } catch (e) {
                console.warn(`Erro ao carregar equipe do projeto ${projeto.id}`);
            }
        }

        document.getElementById('metric-time').textContent = tempoMedio;
        document.getElementById('metric-completion').textContent = taxaConclusao + '%';
        document.getElementById('metric-members').textContent = totalMembros || '0';
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// ============ UTILITÁRIOS ============
function showLoading(show) {
    const spinner = document.getElementById('loading-spinner');
    if (show) {
        spinner.classList.add('active');
    } else {
        spinner.classList.remove('active');
    }
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Fechar modais ao clicar fora
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('active');
    }
});
