-- Migration 001: Initial Schema
-- Criação das tabelas principais do sistema de gerenciamento de projetos
-- Data: 2025-11-27

-- ===== TABELA DE CONTROLE DE MIGRATIONS =====
CREATE TABLE IF NOT EXISTS _migrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    versao VARCHAR(50) UNIQUE NOT NULL,
    nome VARCHAR(150) NOT NULL,
    executado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_versao (versao)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===== USUÁRIOS E PERMISSÕES =====

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    cargo VARCHAR(50),
    foto_perfil VARCHAR(255),
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_ativo (ativo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE permissoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) UNIQUE NOT NULL,
    descricao TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE usuario_permissoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    permissao_id INT NOT NULL,
    projeto_id INT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_usuario_permissao_projeto (usuario_id, permissao_id, projeto_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (permissao_id) REFERENCES permissoes(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===== PROJETOS =====

CREATE TABLE projetos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    descricao TEXT,
    endereco VARCHAR(255),
    cliente VARCHAR(100),
    valor_total DECIMAL(15,2),
    data_inicio DATE,
    data_fim_prevista DATE,
    data_fim_real DATE,
    status ENUM('planejamento', 'em_andamento', 'pausado', 'concluido', 'cancelado') DEFAULT 'planejamento',
    progresso_percentual DECIMAL(5,2) DEFAULT 0,
    criador_id INT NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_criador (criador_id),
    FOREIGN KEY (criador_id) REFERENCES usuarios(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Adicionar FK de usuario_permissoes para projetos (depois que projetos existe)
ALTER TABLE usuario_permissoes 
    ADD FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE;

CREATE TABLE equipes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    projeto_id INT NOT NULL,
    usuario_id INT NOT NULL,
    papel ENUM('gerente', 'engenheiro', 'tecnico', 'colaborador') NOT NULL,
    data_entrada DATE NOT NULL,
    data_saida DATE,
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_projeto_usuario (projeto_id, usuario_id),
    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===== TAREFAS (KANBAN) =====

CREATE TABLE tarefas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    projeto_id INT NOT NULL,
    titulo VARCHAR(150) NOT NULL,
    descricao TEXT,
    status ENUM('a_fazer', 'em_andamento', 'em_revisao', 'concluida') DEFAULT 'a_fazer',
    prioridade ENUM('baixa', 'media', 'alta', 'urgente') DEFAULT 'media',
    data_inicio DATE,
    data_fim_prevista DATE,
    data_fim_real DATE,
    responsavel_id INT,
    criador_id INT NOT NULL,
    ordem INT DEFAULT 0,
    progresso_percentual DECIMAL(5,2) DEFAULT 0,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_projeto_status (projeto_id, status),
    INDEX idx_responsavel (responsavel_id),
    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE,
    FOREIGN KEY (responsavel_id) REFERENCES usuarios(id),
    FOREIGN KEY (criador_id) REFERENCES usuarios(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE tarefa_dependencias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tarefa_id INT NOT NULL,
    tarefa_dependente_id INT NOT NULL,
    tipo ENUM('termino_inicio', 'inicio_inicio', 'termino_termino') DEFAULT 'termino_inicio',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_tarefa_dependencia (tarefa_id, tarefa_dependente_id),
    FOREIGN KEY (tarefa_id) REFERENCES tarefas(id) ON DELETE CASCADE,
    FOREIGN KEY (tarefa_dependente_id) REFERENCES tarefas(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE comentarios_tarefa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tarefa_id INT NOT NULL,
    usuario_id INT NOT NULL,
    comentario TEXT NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_tarefa (tarefa_id),
    FOREIGN KEY (tarefa_id) REFERENCES tarefas(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===== DOCUMENTOS =====

CREATE TABLE documentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    projeto_id INT NOT NULL,
    nome VARCHAR(150) NOT NULL,
    descricao TEXT,
    tipo ENUM('contrato', 'projeto', 'laudo', 'orcamento', 'nota_fiscal', 'outro') NOT NULL,
    arquivo_url VARCHAR(255) NOT NULL,
    tamanho_kb INT,
    versao VARCHAR(20) DEFAULT '1.0',
    usuario_upload_id INT NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_projeto (projeto_id),
    INDEX idx_tipo (tipo),
    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_upload_id) REFERENCES usuarios(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE versoes_documento (
    id INT AUTO_INCREMENT PRIMARY KEY,
    documento_id INT NOT NULL,
    versao VARCHAR(20) NOT NULL,
    arquivo_url VARCHAR(255) NOT NULL,
    alteracoes TEXT,
    usuario_id INT NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_documento (documento_id),
    FOREIGN KEY (documento_id) REFERENCES documentos(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===== CHAT/MENSAGENS =====

CREATE TABLE chats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    projeto_id INT NOT NULL,
    nome VARCHAR(100),
    tipo ENUM('geral', 'equipe', 'privado') DEFAULT 'geral',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_projeto (projeto_id),
    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE chat_participantes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chat_id INT NOT NULL,
    usuario_id INT NOT NULL,
    data_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultima_leitura TIMESTAMP NULL,
    UNIQUE KEY uk_chat_usuario (chat_id, usuario_id),
    FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE mensagens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chat_id INT NOT NULL,
    usuario_id INT NOT NULL,
    mensagem TEXT NOT NULL,
    arquivo_url VARCHAR(255),
    lida BOOLEAN DEFAULT FALSE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_chat (chat_id),
    INDEX idx_chat_data (chat_id, criado_em),
    FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===== MATERIAIS E ORÇAMENTO =====

CREATE TABLE materiais (
    id INT AUTO_INCREMENT PRIMARY KEY,
    projeto_id INT NOT NULL,
    nome VARCHAR(150) NOT NULL,
    descricao TEXT,
    unidade VARCHAR(20) NOT NULL COMMENT 'm, m2, m3, kg, ton, un, etc',
    quantidade_prevista DECIMAL(10,2),
    quantidade_utilizada DECIMAL(10,2) DEFAULT 0,
    preco_unitario DECIMAL(10,2),
    fornecedor VARCHAR(100),
    data_compra DATE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_projeto (projeto_id),
    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE orcamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    projeto_id INT NOT NULL,
    descricao VARCHAR(150) NOT NULL,
    categoria ENUM('material', 'mao_obra', 'equipamento', 'servico', 'outro') NOT NULL,
    valor_previsto DECIMAL(15,2) NOT NULL,
    valor_real DECIMAL(15,2) DEFAULT 0,
    data_prevista DATE,
    data_pagamento DATE,
    status ENUM('previsto', 'aprovado', 'pago', 'cancelado') DEFAULT 'previsto',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_projeto (projeto_id),
    INDEX idx_categoria (categoria),
    INDEX idx_status (status),
    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===== MÉTRICAS E NOTIFICAÇÕES =====

CREATE TABLE metricas_projeto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    projeto_id INT NOT NULL,
    data_registro DATE NOT NULL,
    tarefas_concluidas INT DEFAULT 0,
    tarefas_atrasadas INT DEFAULT 0,
    progresso_fisico DECIMAL(5,2) DEFAULT 0,
    progresso_financeiro DECIMAL(5,2) DEFAULT 0,
    horas_trabalhadas DECIMAL(10,2) DEFAULT 0,
    valor_gasto DECIMAL(15,2) DEFAULT 0,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_projeto_data (projeto_id, data_registro),
    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE notificacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    tipo ENUM('tarefa', 'mensagem', 'documento', 'projeto', 'sistema') NOT NULL,
    titulo VARCHAR(150) NOT NULL,
    mensagem TEXT,
    link VARCHAR(255),
    lida BOOLEAN DEFAULT FALSE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_usuario_lida (usuario_id, lida),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Registrar execução da migration
INSERT INTO _migrations (versao, nome) VALUES ('001', 'Initial Schema');
