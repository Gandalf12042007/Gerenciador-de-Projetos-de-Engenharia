-- =====================================================
-- SCHEMA COMPLETO - Gerenciador de Projetos de Engenharia
-- Desenvolvedor: Vicente de Souza
-- Data: 03/12/2025
-- MySQL 8.0+ | UTF8MB4 | InnoDB
-- =====================================================

-- Criar database
CREATE DATABASE IF NOT EXISTS gerenciador_projetos 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE gerenciador_projetos;

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

-- FK de usuario_permissoes para projetos
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

-- =====================================================
-- DADOS DE EXEMPLO (INSERTS)
-- =====================================================

-- Usuários de exemplo
INSERT INTO usuarios (nome, email, senha_hash, telefone, cargo, ativo) VALUES
('Administrador Sistema', 'admin@empresa.com', 'c1c224b03cd9bc7b6a86d77f5dace40191766c485cd55dc48caf9ac873335d6f', '(11) 98765-4321', 'Administrador', TRUE),
('João Silva', 'joao.silva@empresa.com', 'c1c224b03cd9bc7b6a86d77f5dace40191766c485cd55dc48caf9ac873335d6f', '(11) 91234-5678', 'Engenheiro Civil', TRUE),
('Maria Santos', 'maria.santos@empresa.com', 'c1c224b03cd9bc7b6a86d77f5dace40191766c485cd55dc48caf9ac873335d6f', '(11) 92345-6789', 'Arquiteta', TRUE),
('Pedro Costa', 'pedro.costa@empresa.com', 'c1c224b03cd9bc7b6a86d77f5dace40191766c485cd55dc48caf9ac873335d6f', '(11) 93456-7890', 'Técnico em Edificações', TRUE),
('Ana Oliveira', 'ana.oliveira@empresa.com', 'c1c224b03cd9bc7b6a86d77f5dace40191766c485cd55dc48caf9ac873335d6f', '(11) 94567-8901', 'Engenheira', TRUE);

-- Permissões do sistema
INSERT INTO permissoes (nome, descricao) VALUES
('admin', 'Administrador completo do sistema'),
('gerenciar_projetos', 'Criar, editar e excluir projetos'),
('gerenciar_equipes', 'Adicionar e remover membros de equipes'),
('gerenciar_tarefas', 'Criar, editar e excluir tarefas'),
('visualizar_relatorios', 'Acesso aos relatórios e métricas'),
('gerenciar_documentos', 'Upload e gerenciamento de documentos'),
('gerenciar_orcamentos', 'Controle de materiais e orçamentos'),
('visualizar_apenas', 'Acesso somente leitura ao sistema');

-- Projetos de exemplo
INSERT INTO projetos (nome, descricao, endereco, cliente, valor_total, data_inicio, data_fim_prevista, status, progresso_percentual, criador_id) VALUES
('Residencial Vista Verde', 'Construção de condomínio residencial com 200 unidades', 'Av. Principal, 1000 - São Paulo/SP', 'Construtora XYZ Ltda', 15000000.00, '2024-01-15', '2025-12-30', 'em_andamento', 45.50, 1),
('Reforma Hospital Central', 'Reforma completa da ala cirúrgica', 'Rua da Saúde, 500 - Belo Horizonte/MG', 'Hospital Central BH', 2500000.00, '2024-06-01', '2025-03-31', 'em_andamento', 72.30, 2),
('Ponte Rio Verde', 'Construção de ponte de concreto sobre o Rio Verde', 'Rodovia BR-101, KM 325', 'Governo do Estado', 8000000.00, '2024-03-10', '2026-06-30', 'planejamento', 15.00, 1),
('Escola Municipal Esperança', 'Construção de escola com 12 salas de aula', 'Bairro Esperança - Curitiba/PR', 'Prefeitura Municipal', 3200000.00, '2023-08-01', '2024-11-30', 'concluido', 100.00, 3),
('Shopping Center Norte', 'Ampliação de shopping existente - nova ala', 'Av. Comercial, 2500 - Campinas/SP', 'Shopping Norte S.A.', 25000000.00, '2024-09-01', '2026-12-31', 'em_andamento', 28.70, 2);

-- Equipes (membros dos projetos)
INSERT INTO equipes (projeto_id, usuario_id, papel, data_entrada, ativo) VALUES
(1, 1, 'gerente', '2024-01-15', TRUE),
(1, 2, 'engenheiro', '2024-01-15', TRUE),
(1, 4, 'tecnico', '2024-02-01', TRUE),
(2, 2, 'gerente', '2024-06-01', TRUE),
(2, 3, 'engenheiro', '2024-06-01', TRUE),
(3, 1, 'gerente', '2024-03-10', TRUE),
(3, 2, 'engenheiro', '2024-03-10', TRUE),
(4, 3, 'gerente', '2023-08-01', FALSE),
(5, 2, 'gerente', '2024-09-01', TRUE),
(5, 5, 'engenheiro', '2024-09-01', TRUE);

-- Tarefas de exemplo
INSERT INTO tarefas (projeto_id, titulo, descricao, status, prioridade, data_inicio, data_fim_prevista, responsavel_id, criador_id, progresso_percentual) VALUES
(1, 'Fundações Torre A', 'Execução das fundações da Torre A (estacas)', 'concluida', 'alta', '2024-01-20', '2024-03-15', 2, 1, 100.00),
(1, 'Estrutura Andar Térreo', 'Execução da estrutura de concreto do térreo', 'em_andamento', 'alta', '2024-03-20', '2024-05-30', 2, 1, 75.00),
(1, 'Instalações Hidráulicas', 'Instalações hidráulicas dos 5 primeiros andares', 'a_fazer', 'media', '2024-06-01', '2024-08-30', 4, 1, 0.00),
(2, 'Demolição Ala Antiga', 'Demolição controlada da ala cirúrgica antiga', 'concluida', 'urgente', '2024-06-05', '2024-07-15', 2, 2, 100.00),
(2, 'Instalações Elétricas', 'Nova instalação elétrica conforme NR-13', 'em_andamento', 'alta', '2024-08-01', '2024-11-30', 3, 2, 85.00),
(3, 'Levantamento Topográfico', 'Estudo topográfico completo da região', 'concluida', 'urgente', '2024-03-15', '2024-04-30', 2, 1, 100.00),
(3, 'Projeto Estrutural', 'Desenvolvimento do projeto estrutural da ponte', 'em_revisao', 'alta', '2024-05-01', '2024-07-31', 2, 1, 90.00),
(5, 'Terraplanagem', 'Terraplanagem do terreno para nova ala', 'em_andamento', 'alta', '2024-09-10', '2024-11-30', 5, 2, 60.00);

-- Materiais de exemplo
INSERT INTO materiais (projeto_id, nome, descricao, unidade, quantidade_prevista, quantidade_utilizada, preco_unitario, fornecedor) VALUES
(1, 'Cimento CP-II', 'Cimento Portland CP-II 50kg', 'sc', 5000.00, 2250.00, 32.50, 'Votorantim'),
(1, 'Aço CA-50', 'Barra de aço CA-50 12mm', 'kg', 50000.00, 22500.00, 5.80, 'Gerdau'),
(1, 'Brita 1', 'Brita 1 para concreto', 'm3', 800.00, 360.00, 85.00, 'Pedreira Central'),
(2, 'Fio Elétrico 2.5mm', 'Fio de cobre flexível 2.5mm', 'm', 2000.00, 1500.00, 2.80, 'Prysmian'),
(2, 'Disjuntor 20A', 'Disjuntor termomagnético 20A', 'un', 50.00, 42.00, 18.50, 'Schneider'),
(5, 'Concreto Usinado', 'Concreto FCK 25 MPa', 'm3', 1200.00, 350.00, 420.00, 'ConcreBras');

-- Orçamentos de exemplo
INSERT INTO orcamentos (projeto_id, descricao, categoria, valor_previsto, valor_real, status) VALUES
(1, 'Materiais para Fundação', 'material', 850000.00, 823500.00, 'pago'),
(1, 'Mão de Obra - Estrutura', 'mao_obra', 2500000.00, 1125000.00, 'aprovado'),
(1, 'Locação de Grua', 'equipamento', 180000.00, 0.00, 'previsto'),
(2, 'Materiais Elétricos', 'material', 320000.00, 285000.00, 'pago'),
(2, 'Instalações Especiais', 'servico', 450000.00, 320000.00, 'aprovado'),
(5, 'Terraplanagem e Contenção', 'servico', 680000.00, 410000.00, 'aprovado');

-- Registrar migration
INSERT INTO _migrations (versao, nome) VALUES ('001', 'Initial Schema with Sample Data');

-- =====================================================
-- FIM DO SCRIPT
-- =====================================================

-- Verificar criação
SELECT 'Schema criado com sucesso!' as status;
SELECT COUNT(*) as total_tabelas FROM information_schema.tables WHERE table_schema = 'gerenciador_projetos';
SELECT COUNT(*) as total_usuarios FROM usuarios;
SELECT COUNT(*) as total_projetos FROM projetos;
SELECT COUNT(*) as total_tarefas FROM tarefas;
