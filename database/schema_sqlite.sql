-- =====================================================
-- SCHEMA SQLite - Gerenciador de Projetos de Engenharia
-- Desenvolvedor: Vicente de Souza
-- Versão SQLite do schema_completo.sql
-- =====================================================

-- ===== TABELA DE CONTROLE DE MIGRATIONS =====
CREATE TABLE IF NOT EXISTS _migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    versao TEXT UNIQUE NOT NULL,
    nome TEXT NOT NULL,
    executado_em TEXT DEFAULT (datetime('now', 'localtime'))
);

-- ===== USUÁRIOS E PERMISSÕES =====

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL,
    telefone TEXT,
    cargo TEXT,
    foto_perfil TEXT,
    ativo INTEGER DEFAULT 1,
    criado_em TEXT DEFAULT (datetime('now', 'localtime')),
    atualizado_em TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_usuarios_ativo ON usuarios(ativo);

CREATE TABLE IF NOT EXISTS permissoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE NOT NULL,
    descricao TEXT,
    criado_em TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS usuario_permissoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    permissao_id INTEGER NOT NULL,
    projeto_id INTEGER NULL,
    criado_em TEXT DEFAULT (datetime('now', 'localtime')),
    UNIQUE(usuario_id, permissao_id, projeto_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (permissao_id) REFERENCES permissoes(id) ON DELETE CASCADE,
    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE
);

-- ===== PROJETOS =====

CREATE TABLE IF NOT EXISTS projetos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    project_code TEXT UNIQUE,
    descricao TEXT,
    endereco TEXT,
    cliente TEXT,
    valor_total REAL,
    data_inicio TEXT,
    data_fim_prevista TEXT,
    data_fim_real TEXT,
    status TEXT DEFAULT 'planejamento' CHECK(status IN ('planejamento', 'em_andamento', 'pausado', 'concluido', 'cancelado')),
    progresso_percentual REAL DEFAULT 0,
    criador_id INTEGER NOT NULL,
    criado_em TEXT DEFAULT (datetime('now', 'localtime')),
    atualizado_em TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (criador_id) REFERENCES usuarios(id)
);

CREATE INDEX IF NOT EXISTS idx_projetos_status ON projetos(status);
CREATE INDEX IF NOT EXISTS idx_projetos_criador ON projetos(criador_id);
CREATE UNIQUE INDEX IF NOT EXISTS ux_projetos_project_code ON projetos(project_code);

-- ===== SEGURANCA DE AUTENTICACAO =====

CREATE TABLE IF NOT EXISTS auth_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    acao TEXT NOT NULL,
    ip_address TEXT,
    sucesso INTEGER,
    motivo TEXT,
    timestamp TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE INDEX IF NOT EXISTS idx_auth_logs_email_time ON auth_logs(email, timestamp);

CREATE TABLE IF NOT EXISTS failed_login_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    ip_address TEXT,
    timestamp TEXT DEFAULT (datetime('now', 'localtime')),
    bloqueado_ate TEXT
);

CREATE INDEX IF NOT EXISTS idx_failed_login_email_time ON failed_login_attempts(email, timestamp);

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    token_hash TEXT NOT NULL UNIQUE,
    expires_at TEXT NOT NULL,
    used INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    used_at TEXT,
    ip_address TEXT
);

CREATE INDEX IF NOT EXISTS idx_password_reset_email ON password_reset_tokens(email);
CREATE INDEX IF NOT EXISTS idx_password_reset_token_hash ON password_reset_tokens(token_hash);

CREATE TABLE IF NOT EXISTS equipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projeto_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    papel TEXT NOT NULL CHECK(papel IN ('gerente', 'engenheiro', 'tecnico', 'colaborador')),
    data_entrada TEXT NOT NULL,
    data_saida TEXT,
    ativo INTEGER DEFAULT 1,
    criado_em TEXT DEFAULT (datetime('now', 'localtime')),
    UNIQUE(projeto_id, usuario_id),
    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- ===== CONVITES DE EQUIPE =====
CREATE TABLE IF NOT EXISTS convites_equipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projeto_id INTEGER NOT NULL,
    email_convidado TEXT NOT NULL,
    papel TEXT NOT NULL CHECK(papel IN ('gerente', 'engenheiro', 'tecnico', 'colaborador')),
    token TEXT NOT NULL UNIQUE,
    expiracao TEXT NOT NULL,
    aceito INTEGER DEFAULT 0,
    criado_em TEXT DEFAULT (datetime('now', 'localtime')),
    aceito_em TEXT NULL,
    cancelado INTEGER DEFAULT 0,
    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE
);

-- ===== TAREFAS (KANBAN) =====

CREATE TABLE IF NOT EXISTS tarefas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projeto_id INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    descricao TEXT,
    status TEXT DEFAULT 'a_fazer' CHECK(status IN ('a_fazer', 'em_andamento', 'em_revisao', 'concluida')),
    prioridade TEXT DEFAULT 'media' CHECK(prioridade IN ('baixa', 'media', 'alta', 'urgente')),
    data_inicio TEXT,
    data_fim_prevista TEXT,
    data_fim_real TEXT,
    responsavel_id INTEGER,
    criador_id INTEGER NOT NULL,
    ordem INTEGER DEFAULT 0,
    progresso_percentual REAL DEFAULT 0,
    criado_em TEXT DEFAULT (datetime('now', 'localtime')),
    atualizado_em TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE,
    FOREIGN KEY (responsavel_id) REFERENCES usuarios(id),
    FOREIGN KEY (criador_id) REFERENCES usuarios(id)
);

CREATE INDEX IF NOT EXISTS idx_tarefas_projeto_status ON tarefas(projeto_id, status);
CREATE INDEX IF NOT EXISTS idx_tarefas_responsavel ON tarefas(responsavel_id);

CREATE TABLE IF NOT EXISTS tarefa_dependencias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tarefa_id INTEGER NOT NULL,
    tarefa_dependente_id INTEGER NOT NULL,
    tipo TEXT DEFAULT 'termino_inicio' CHECK(tipo IN ('termino_inicio', 'inicio_inicio', 'termino_termino')),
    criado_em TEXT DEFAULT (datetime('now', 'localtime')),
    UNIQUE(tarefa_id, tarefa_dependente_id),
    FOREIGN KEY (tarefa_id) REFERENCES tarefas(id) ON DELETE CASCADE,
    FOREIGN KEY (tarefa_dependente_id) REFERENCES tarefas(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS comentarios_tarefa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tarefa_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    comentario TEXT NOT NULL,
    criado_em TEXT DEFAULT (datetime('now', 'localtime')),
    atualizado_em TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (tarefa_id) REFERENCES tarefas(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

CREATE INDEX IF NOT EXISTS idx_comentarios_tarefa ON comentarios_tarefa(tarefa_id);

-- ===== DOCUMENTOS =====

CREATE TABLE IF NOT EXISTS documentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projeto_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    descricao TEXT,
    categoria TEXT,
    caminho_arquivo TEXT,
    tamanho_bytes INTEGER,
    tipo TEXT NOT NULL CHECK(tipo IN ('contrato', 'projeto', 'laudo', 'orcamento', 'nota_fiscal', 'outro', 'plantas', 'rrt', 'diario', 'medicoes', 'fotos', 'relatorios', 'outros')),
    arquivo_url TEXT,
    tamanho_kb INTEGER,
    versao TEXT DEFAULT '1.0',
    usuario_upload_id INTEGER,
    uploaded_por INTEGER,
    data_upload TEXT,
    criado_em TEXT DEFAULT (datetime('now', 'localtime')),
    atualizado_em TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_upload_id) REFERENCES usuarios(id),
    FOREIGN KEY (uploaded_por) REFERENCES usuarios(id)
);

CREATE INDEX IF NOT EXISTS idx_documentos_projeto ON documentos(projeto_id);
CREATE INDEX IF NOT EXISTS idx_documentos_tipo ON documentos(tipo);

CREATE TABLE IF NOT EXISTS versoes_documento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    documento_id INTEGER NOT NULL,
    numero_versao INTEGER,
    versao TEXT,
    caminho_arquivo TEXT,
    arquivo_url TEXT,
    tamanho_bytes INTEGER,
    alteracoes TEXT,
    comentario TEXT,
    usuario_id INTEGER,
    criado_por INTEGER,
    data_criacao TEXT,
    criado_em TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (documento_id) REFERENCES documentos(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (criado_por) REFERENCES usuarios(id)
);

CREATE INDEX IF NOT EXISTS idx_versoes_documento ON versoes_documento(documento_id);

-- ===== CHAT/MENSAGENS =====

CREATE TABLE IF NOT EXISTS chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projeto_id INTEGER NOT NULL,
    nome TEXT,
    tipo TEXT DEFAULT 'geral' CHECK(tipo IN ('geral', 'equipe', 'privado')),
    criado_em TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_chats_projeto ON chats(projeto_id);

CREATE TABLE IF NOT EXISTS chat_participantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    juntou_em TEXT,
    data_entrada TEXT DEFAULT (datetime('now', 'localtime')),
    ultima_leitura TEXT NULL,
    UNIQUE(chat_id, usuario_id),
    FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mensagens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    usuario_id INTEGER,
    autor_id INTEGER,
    mensagem TEXT,
    conteudo TEXT,
    arquivo_url TEXT,
    lida INTEGER DEFAULT 0,
    enviada_em TEXT,
    criado_em TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (autor_id) REFERENCES usuarios(id)
);

CREATE INDEX IF NOT EXISTS idx_mensagens_chat ON mensagens(chat_id);
CREATE INDEX IF NOT EXISTS idx_mensagens_chat_data ON mensagens(chat_id, criado_em);

-- ===== MATERIAIS E ORÇAMENTO =====

CREATE TABLE IF NOT EXISTS materiais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projeto_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    descricao TEXT,
    unidade TEXT NOT NULL,
    quantidade_prevista REAL,
    quantidade_utilizada REAL DEFAULT 0,
    preco_unitario REAL,
    fornecedor TEXT,
    data_compra TEXT,
    criado_em TEXT DEFAULT (datetime('now', 'localtime')),
    atualizado_em TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_materiais_projeto ON materiais(projeto_id);

CREATE TABLE IF NOT EXISTS orcamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projeto_id INTEGER NOT NULL,
    descricao TEXT NOT NULL,
    categoria TEXT NOT NULL CHECK(categoria IN ('material', 'mao_obra', 'equipamento', 'servico', 'outro')),
    valor_previsto REAL NOT NULL,
    valor_real REAL DEFAULT 0,
    data_prevista TEXT,
    data_pagamento TEXT,
    status TEXT DEFAULT 'previsto' CHECK(status IN ('previsto', 'aprovado', 'pago', 'cancelado')),
    criado_em TEXT DEFAULT (datetime('now', 'localtime')),
    atualizado_em TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_orcamentos_projeto ON orcamentos(projeto_id);
CREATE INDEX IF NOT EXISTS idx_orcamentos_categoria ON orcamentos(categoria);
CREATE INDEX IF NOT EXISTS idx_orcamentos_status ON orcamentos(status);

-- ===== MÉTRICAS E NOTIFICAÇÕES =====

CREATE TABLE IF NOT EXISTS metricas_projeto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projeto_id INTEGER NOT NULL,
    data_registro TEXT NOT NULL,
    tarefas_concluidas INTEGER DEFAULT 0,
    tarefas_atrasadas INTEGER DEFAULT 0,
    progresso_fisico REAL DEFAULT 0,
    progresso_financeiro REAL DEFAULT 0,
    horas_trabalhadas REAL DEFAULT 0,
    valor_gasto REAL DEFAULT 0,
    criado_em TEXT DEFAULT (datetime('now', 'localtime')),
    UNIQUE(projeto_id, data_registro),
    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notificacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    tipo TEXT NOT NULL CHECK(tipo IN ('tarefa', 'mensagem', 'documento', 'projeto', 'sistema', 'mencao')),
    titulo TEXT,
    conteudo TEXT,
    mensagem TEXT,
    link TEXT,
    lida INTEGER DEFAULT 0,
    criada_em TEXT,
    criado_em TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_notificacoes_usuario_lida ON notificacoes(usuario_id, lida);

-- ===== AUDIT TRAIL =====
CREATE TABLE IF NOT EXISTS audit_trail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    entidade TEXT NOT NULL,
    entidade_id INTEGER,
    acao TEXT NOT NULL,
    detalhes TEXT,
    ip TEXT,
    user_agent TEXT,
    criado_em TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_usuario ON audit_trail(usuario_id);
CREATE INDEX IF NOT EXISTS idx_audit_entidade ON audit_trail(entidade, entidade_id);

-- =====================================================
-- DADOS INICIAIS
-- =====================================================

-- Permissões do sistema
INSERT OR IGNORE INTO permissoes (nome, descricao) VALUES
('admin', 'Administrador completo do sistema'),
('gerenciar_projetos', 'Criar, editar e excluir projetos'),
('gerenciar_equipes', 'Adicionar e remover membros de equipes'),
('gerenciar_tarefas', 'Criar, editar e excluir tarefas'),
('visualizar_relatorios', 'Acesso aos relatórios e métricas'),
('gerenciar_documentos', 'Upload e gerenciamento de documentos'),
('gerenciar_orcamentos', 'Controle de materiais e orçamentos'),
('visualizar_apenas', 'Acesso somente leitura ao sistema');

-- Usuários de teste (senha: Teste123@)
INSERT OR IGNORE INTO usuarios (id, nome, email, senha_hash, telefone, cargo, ativo) VALUES
(1, 'Vicente de Souza', 'teste01@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uO.G', '11 99999-0001', 'Administrador', 1),
(2, 'Francisco', 'francisco@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uO.G', '11 99999-0002', 'Desenvolvedor', 1);

-- Registrar migration
INSERT OR IGNORE INTO _migrations (versao, nome) VALUES ('001', 'Initial Schema SQLite');

-- =====================================================
-- FIM DO SCRIPT
-- =====================================================
