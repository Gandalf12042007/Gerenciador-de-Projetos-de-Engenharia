/**
 * Dashboard - Gerenciador de Projetos de Engenharia
 * Visualização de métricas e gráficos
 */

// Verificar autenticação
if (!api.isAuthenticated()) {
    window.location.href = '../login.html';
}

// Variáveis globais
let projects = [];
let tasks = [];
let chartInstances = {};

// Inicialização
document.addEventListener('DOMContentLoaded', async () => {
    // Exibir nome do usuário
    const user = api.user;
    if (user && user.nome) {
        document.getElementById('userName').textContent = user.nome.split(' ')[0];
    }

    // Handlers
    document.getElementById('logoutBtn').addEventListener('click', () => {
        api.logout();
        window.location.href = '../login.html';
    });

    document.getElementById('profileBtn').addEventListener('click', () => {
        window.location.href = '../profile.html';
    });

    // Carregar dados
    await loadDashboardData();
});

/**
 * Carregar todos os dados do dashboard
 */
async function loadDashboardData() {
    try {
        // Carregar projetos
        const projectsResponse = await api.get('/projetos/');
        projects = projectsResponse || [];

        // Carregar tarefas de todos os projetos
        tasks = [];
        for (const project of projects) {
            try {
                const projectTasks = await api.get(`/tarefas/?projeto_id=${project.id}`);
                if (Array.isArray(projectTasks)) {
                    tasks.push(...projectTasks.map(t => ({ ...t, projeto_nome: project.nome })));
                }
            } catch (e) {
                console.warn(`Erro ao carregar tarefas do projeto ${project.id}:`, e);
            }
        }

        // Atualizar UI
        updateSummaryCards();
        updateCharts();
        updateLists();

    } catch (error) {
        console.error('Erro ao carregar dashboard:', error);
    }
}

/**
 * Atualizar cards de resumo
 */
function updateSummaryCards() {
    const totalProjects = projects.length;
    const completedProjects = projects.filter(p => p.status === 'concluido').length;
    const activeProjects = projects.filter(p => p.status === 'em_andamento').length;
    
    // Tarefas atrasadas (data_fim_prevista < hoje e status != concluida)
    const today = new Date().toISOString().split('T')[0];
    const overdueTasks = tasks.filter(t => 
        t.data_fim_prevista && 
        t.data_fim_prevista < today && 
        t.status !== 'concluida'
    ).length;

    // Progresso médio
    const avgProgress = projects.length > 0 
        ? Math.round(projects.reduce((sum, p) => sum + (p.progresso_percentual || 0), 0) / projects.length)
        : 0;

    // Atualizar elementos
    document.getElementById('totalProjects').textContent = totalProjects;
    document.getElementById('completedProjects').textContent = completedProjects;
    document.getElementById('activeProjects').textContent = activeProjects;
    document.getElementById('overdueTasks').textContent = overdueTasks;
    document.getElementById('avgProgress').textContent = `${avgProgress}%`;
}

/**
 * Atualizar gráficos
 */
function updateCharts() {
    // Destruir gráficos existentes
    Object.values(chartInstances).forEach(chart => chart.destroy());
    chartInstances = {};

    // Gráfico: Tarefas por Status
    createTasksByStatusChart();
    
    // Gráfico: Projetos por Status
    createProjectsByStatusChart();
    
    // Gráfico: Tarefas por Responsável
    createTasksByResponsibleChart();
    
    // Gráfico: Timeline de Tarefas
    createTasksTimelineChart();
}

/**
 * Gráfico de Tarefas por Status
 */
function createTasksByStatusChart() {
    const ctx = document.getElementById('tasksByStatusChart').getContext('2d');
    
    const statusCounts = {
        'a_fazer': tasks.filter(t => t.status === 'a_fazer').length,
        'em_andamento': tasks.filter(t => t.status === 'em_andamento').length,
        'em_revisao': tasks.filter(t => t.status === 'em_revisao').length,
        'concluida': tasks.filter(t => t.status === 'concluida').length
    };

    chartInstances.tasksByStatus = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['A Fazer', 'Em Andamento', 'Em Revisão', 'Concluída'],
            datasets: [{
                data: Object.values(statusCounts),
                backgroundColor: ['#e2e8f0', '#63b3ed', '#faf089', '#68d391'],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

/**
 * Gráfico de Projetos por Status
 */
function createProjectsByStatusChart() {
    const ctx = document.getElementById('projectsByStatusChart').getContext('2d');
    
    const statusCounts = {
        'planejamento': projects.filter(p => p.status === 'planejamento').length,
        'em_andamento': projects.filter(p => p.status === 'em_andamento').length,
        'pausado': projects.filter(p => p.status === 'pausado').length,
        'concluido': projects.filter(p => p.status === 'concluido').length,
        'cancelado': projects.filter(p => p.status === 'cancelado').length
    };

    chartInstances.projectsByStatus = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Planejamento', 'Em Andamento', 'Pausado', 'Concluído', 'Cancelado'],
            datasets: [{
                label: 'Projetos',
                data: Object.values(statusCounts),
                backgroundColor: ['#90cdf4', '#68d391', '#fbd38d', '#9ae6b4', '#fc8181'],
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

/**
 * Gráfico de Tarefas por Responsável
 */
function createTasksByResponsibleChart() {
    const ctx = document.getElementById('tasksByResponsibleChart').getContext('2d');
    
    // Agrupar tarefas por responsável
    const responsibleCounts = {};
    tasks.forEach(task => {
        const responsible = task.responsavel_nome || 'Não atribuído';
        responsibleCounts[responsible] = (responsibleCounts[responsible] || 0) + 1;
    });

    const labels = Object.keys(responsibleCounts);
    const data = Object.values(responsibleCounts);
    
    // Cores dinâmicas
    const colors = labels.map((_, i) => {
        const hue = (i * 137.5) % 360;
        return `hsl(${hue}, 70%, 60%)`;
    });

    chartInstances.tasksByResponsible = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        }
    });
}

/**
 * Gráfico de Timeline de Tarefas
 */
function createTasksTimelineChart() {
    const ctx = document.getElementById('tasksTimelineChart').getContext('2d');
    
    // Últimos 7 dias
    const days = [];
    const counts = [];
    
    for (let i = 6; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        const dateStr = date.toISOString().split('T')[0];
        
        days.push(date.toLocaleDateString('pt-BR', { weekday: 'short', day: 'numeric' }));
        
        // Contar tarefas criadas nesse dia
        const count = tasks.filter(t => {
            if (!t.criado_em) return false;
            return t.criado_em.startsWith(dateStr);
        }).length;
        
        counts.push(count);
    }

    chartInstances.tasksTimeline = new Chart(ctx, {
        type: 'line',
        data: {
            labels: days,
            datasets: [{
                label: 'Tarefas Criadas',
                data: counts,
                borderColor: '#3182ce',
                backgroundColor: 'rgba(49, 130, 206, 0.1)',
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#3182ce',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

/**
 * Atualizar listas
 */
function updateLists() {
    updateOverdueTasksList();
    updateUpcomingTasksList();
    updateProjectsProgressList();
}

/**
 * Lista de Tarefas Atrasadas
 */
function updateOverdueTasksList() {
    const container = document.getElementById('overdueTasksList');
    const today = new Date().toISOString().split('T')[0];
    
    const overdueTasks = tasks.filter(t => 
        t.data_fim_prevista && 
        t.data_fim_prevista < today && 
        t.status !== 'concluida'
    ).sort((a, b) => a.data_fim_prevista.localeCompare(b.data_fim_prevista));

    if (overdueTasks.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🎉</div>
                <p>Nenhuma tarefa atrasada!</p>
            </div>
        `;
        return;
    }

    container.innerHTML = overdueTasks.map(task => {
        const daysOverdue = Math.ceil((new Date() - new Date(task.data_fim_prevista)) / (1000 * 60 * 60 * 24));
        return `
            <div class="list-item overdue">
                <div class="list-item-info">
                    <div class="list-item-title">
                        ${task.titulo}
                        <span class="priority-badge ${task.prioridade}">${task.prioridade}</span>
                    </div>
                    <div class="list-item-meta">
                        📁 ${task.projeto_nome || 'Projeto'} • ⏰ ${daysOverdue} dia(s) de atraso
                    </div>
                </div>
                <span class="status-badge ${task.status}">${formatStatus(task.status)}</span>
            </div>
        `;
    }).join('');
}

/**
 * Lista de Tarefas Próximas a Vencer
 */
function updateUpcomingTasksList() {
    const container = document.getElementById('upcomingTasksList');
    const today = new Date();
    const nextWeek = new Date();
    nextWeek.setDate(today.getDate() + 7);
    
    const todayStr = today.toISOString().split('T')[0];
    const nextWeekStr = nextWeek.toISOString().split('T')[0];
    
    const upcomingTasks = tasks.filter(t => 
        t.data_fim_prevista && 
        t.data_fim_prevista >= todayStr && 
        t.data_fim_prevista <= nextWeekStr && 
        t.status !== 'concluida'
    ).sort((a, b) => a.data_fim_prevista.localeCompare(b.data_fim_prevista));

    if (upcomingTasks.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📅</div>
                <p>Nenhuma tarefa para os próximos 7 dias</p>
            </div>
        `;
        return;
    }

    container.innerHTML = upcomingTasks.map(task => {
        const daysUntil = Math.ceil((new Date(task.data_fim_prevista) - new Date()) / (1000 * 60 * 60 * 24));
        const isUrgent = daysUntil <= 2;
        return `
            <div class="list-item ${isUrgent ? 'urgent' : ''}">
                <div class="list-item-info">
                    <div class="list-item-title">
                        ${task.titulo}
                        <span class="priority-badge ${task.prioridade}">${task.prioridade}</span>
                    </div>
                    <div class="list-item-meta">
                        📁 ${task.projeto_nome || 'Projeto'} • 📅 ${daysUntil === 0 ? 'Hoje' : daysUntil === 1 ? 'Amanhã' : `Em ${daysUntil} dias`}
                    </div>
                </div>
                <span class="status-badge ${task.status}">${formatStatus(task.status)}</span>
            </div>
        `;
    }).join('');
}

/**
 * Lista de Progresso dos Projetos
 */
function updateProjectsProgressList() {
    const container = document.getElementById('projectsProgressList');
    
    const activeProjects = projects.filter(p => 
        p.status === 'em_andamento' || p.status === 'planejamento'
    ).sort((a, b) => (b.progresso_percentual || 0) - (a.progresso_percentual || 0));

    if (activeProjects.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📁</div>
                <p>Nenhum projeto ativo</p>
            </div>
        `;
        return;
    }

    container.innerHTML = activeProjects.map(project => {
        const progress = project.progresso_percentual || 0;
        const progressColor = progress >= 80 ? '#38a169' : progress >= 50 ? '#d69e2e' : '#3182ce';
        return `
            <div class="project-progress-item">
                <div class="project-progress-header">
                    <span class="project-progress-name">${project.nome}</span>
                    <span class="project-progress-percent" style="color:${progressColor}">${progress}%</span>
                </div>
                <div class="progress-bar">
                    <div class="fill" style="width:${progress}%; background:${progressColor}"></div>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Formatar status para exibição
 */
function formatStatus(status) {
    const statusMap = {
        'a_fazer': 'A Fazer',
        'em_andamento': 'Em Andamento',
        'em_revisao': 'Em Revisão',
        'concluida': 'Concluída'
    };
    return statusMap[status] || status;
}
