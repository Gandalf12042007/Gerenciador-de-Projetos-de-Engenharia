-- Migration 003: Índices de Performance
-- Índices adicionais para otimizar queries frequentes
-- Data: 2025-12-12

-- ===== ÍNDICES PARA PROJETOS =====

-- Busca por status e data de início (dashboard, filtros)
CREATE INDEX idx_projetos_status_data_inicio ON projetos(status, data_inicio);

-- Busca por status e progresso (relatórios)
CREATE INDEX idx_projetos_status_progresso ON projetos(status, progresso_percentual);

-- Busca por criador e status (meus projetos)
CREATE INDEX idx_projetos_criador_status ON projetos(criador_id, status);

-- Busca por data de fim prevista (alertas de prazo)
CREATE INDEX idx_projetos_data_fim_prevista ON projetos(data_fim_prevista);

-- ===== ÍNDICES PARA TAREFAS =====

-- Busca por projeto, status e prioridade (Kanban, filtros)
CREATE INDEX idx_tarefas_projeto_status_prioridade ON tarefas(projeto_id, status, prioridade);

-- Busca por responsável e status (minhas tarefas)
CREATE INDEX idx_tarefas_responsavel_status ON tarefas(responsavel_id, status);

-- Busca por data de fim e status (tarefas atrasadas)
CREATE INDEX idx_tarefas_data_fim_status ON tarefas(data_fim_prevista, status);

-- Busca por projeto e data de criação (timeline)
CREATE INDEX idx_tarefas_projeto_criado ON tarefas(projeto_id, criado_em);

-- Busca por prioridade e data (urgências)
CREATE INDEX idx_tarefas_prioridade_data ON tarefas(prioridade, data_fim_prevista);

-- ===== ÍNDICES PARA EQUIPES =====

-- Busca por usuário e status ativo (projetos do usuário)
CREATE INDEX idx_equipes_usuario_ativo ON equipes(usuario_id, ativo);

-- Busca por projeto e papel (membros por papel)
CREATE INDEX idx_equipes_projeto_papel ON equipes(projeto_id, papel);

-- Busca por projeto, usuário e status (verificação de acesso)
CREATE INDEX idx_equipes_projeto_usuario_ativo ON equipes(projeto_id, usuario_id, ativo);

-- ===== ÍNDICES PARA DOCUMENTOS =====

-- Busca por projeto e tipo (categorias)
CREATE INDEX idx_documentos_projeto_tipo ON documentos(projeto_id, tipo);

-- Busca por projeto e data (documentos recentes)
CREATE INDEX idx_documentos_projeto_criado ON documentos(projeto_id, criado_em);

-- Busca por usuário que fez upload (meus uploads)
CREATE INDEX idx_documentos_usuario_upload ON documentos(usuario_upload_id, criado_em);

-- ===== ÍNDICES PARA CHAT E MENSAGENS =====

-- Busca por projeto (chats do projeto)
CREATE INDEX idx_chats_projeto_tipo ON chats(projeto_id, tipo);

-- Busca por chat e data (mensagens ordenadas)
CREATE INDEX idx_mensagens_chat_criado ON mensagens(chat_id, criado_em DESC);

-- Busca por usuário remetente (minhas mensagens)
CREATE INDEX idx_mensagens_usuario_criado ON mensagens(usuario_id, criado_em);

-- Busca por mensagens não lidas
CREATE INDEX idx_mensagens_chat_lida ON mensagens(chat_id, lida);

-- ===== ÍNDICES PARA MATERIAIS E ORÇAMENTO =====

-- Busca por projeto e fornecedor (materiais por fornecedor)
CREATE INDEX idx_materiais_projeto_fornecedor ON materiais(projeto_id, fornecedor);

-- Busca por projeto e data de compra (histórico)
CREATE INDEX idx_materiais_projeto_data_compra ON materiais(projeto_id, data_compra);

-- Busca por orçamento: projeto, categoria e status
CREATE INDEX idx_orcamentos_projeto_categoria_status ON orcamentos(projeto_id, categoria, status);

-- Busca por orçamento: status e data de pagamento
CREATE INDEX idx_orcamentos_status_data_pagamento ON orcamentos(status, data_pagamento);

-- Busca por orçamento: projeto e data prevista (alertas de pagamento)
CREATE INDEX idx_orcamentos_projeto_data_prevista ON orcamentos(projeto_id, data_prevista);

-- ===== ÍNDICES PARA NOTIFICAÇÕES =====

-- Busca por usuário, status de leitura e data (notificações não lidas)
CREATE INDEX idx_notificacoes_usuario_lida_criado ON notificacoes(usuario_id, lida, criado_em DESC);

-- Busca por tipo e data (notificações por tipo)
CREATE INDEX idx_notificacoes_tipo_criado ON notificacoes(tipo, criado_em);

-- ===== ÍNDICES PARA MÉTRICAS =====

-- Busca por projeto e período (gráficos de progresso)
CREATE INDEX idx_metricas_projeto_data ON metricas_projeto(projeto_id, data_registro DESC);

-- ===== ÍNDICES PARA COMENTÁRIOS =====

-- Busca por tarefa e data (comentários ordenados)
CREATE INDEX idx_comentarios_tarefa_criado ON comentarios_tarefa(tarefa_id, criado_em DESC);

-- Busca por usuário (meus comentários)
CREATE INDEX idx_comentarios_usuario_criado ON comentarios_tarefa(usuario_id, criado_em);

-- ===== ÍNDICES PARA VERSÕES DE DOCUMENTOS =====

-- Busca por documento e versão (histórico)
CREATE INDEX idx_versoes_documento_versao ON versoes_documento(documento_id, numero_versao DESC);

-- Busca por documento e data (timeline de versões)
CREATE INDEX idx_versoes_documento_criado ON versoes_documento(documento_id, criado_em DESC);

-- ===== ÍNDICES PARA PERMISSÕES =====

-- Busca por usuário e projeto (verificação de permissões)
CREATE INDEX idx_usuario_permissoes_usuario_projeto ON usuario_permissoes(usuario_id, projeto_id);

-- Busca por permissão (usuários com determinada permissão)
CREATE INDEX idx_usuario_permissoes_permissao ON usuario_permissoes(permissao_id);

-- ===== ÍNDICES PARA DEPENDÊNCIAS DE TAREFAS =====

-- Busca por tarefa dependente (quem depende de mim)
CREATE INDEX idx_tarefa_dependencias_dependente ON tarefa_dependencias(tarefa_dependente_id);

-- Busca por tarefa e tipo (tipos de dependência)
CREATE INDEX idx_tarefa_dependencias_tarefa_tipo ON tarefa_dependencias(tarefa_id, tipo);

-- ===== ÍNDICES FULL-TEXT PARA BUSCA =====

-- Busca textual em projetos
CREATE FULLTEXT INDEX idx_ft_projetos_nome_descricao ON projetos(nome, descricao);

-- Busca textual em tarefas
CREATE FULLTEXT INDEX idx_ft_tarefas_titulo_descricao ON tarefas(titulo, descricao);

-- Busca textual em documentos
CREATE FULLTEXT INDEX idx_ft_documentos_nome_descricao ON documentos(nome, descricao);

-- Busca textual em materiais
CREATE FULLTEXT INDEX idx_ft_materiais_nome_descricao ON materiais(nome, descricao);

-- Registrar execução da migration
INSERT INTO _migrations (versao, nome) VALUES ('003', 'Índices de Performance');
