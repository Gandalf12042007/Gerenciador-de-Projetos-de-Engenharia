-- Migration: Módulo Financeiro Completo
-- Data: 2026-02-13
-- Desenvolvedor: Sistema de correções

-- Tipos de custo
CREATE TABLE IF NOT EXISTS tipos_custo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) UNIQUE NOT NULL,
    descricao TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Custos do projeto
CREATE TABLE IF NOT EXISTS custos_financeiro (
    id INT AUTO_INCREMENT PRIMARY KEY,
    projeto_id INT NOT NULL,
    tipo_custo_id INT NOT NULL,
    descricao VARCHAR(200) NOT NULL,
    valor DECIMAL(15,2) NOT NULL,
    data_lancamento DATE NOT NULL,
    status ENUM('planejado', 'realizado', 'cancelado') DEFAULT 'planejado',
    observacoes TEXT,
    criado_por INT NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_projeto (projeto_id),
    INDEX idx_tipo (tipo_custo_id),
    INDEX idx_data (data_lancamento),
    INDEX idx_status (status),
    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE,
    FOREIGN KEY (tipo_custo_id) REFERENCES tipos_custo(id) ON DELETE RESTRICT,
    FOREIGN KEY (criado_por) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Orçamentos detalhados
CREATE TABLE IF NOT EXISTS orcamentos_financeiro (
    id INT AUTO_INCREMENT PRIMARY KEY,
    projeto_id INT NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    item VARCHAR(200) NOT NULL,
    quantidade DECIMAL(10,2) NOT NULL,
    unidade VARCHAR(20) NOT NULL,
    valor_unitario DECIMAL(15,2) NOT NULL,
    valor_total DECIMAL(15,2) GENERATED ALWAYS AS (quantidade * valor_unitario) STORED,
    observacoes TEXT,
    criado_por INT NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_projeto (projeto_id),
    INDEX idx_categoria (categoria),
    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE,
    FOREIGN KEY (criado_por) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Faturas
CREATE TABLE IF NOT EXISTS faturas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    projeto_id INT NOT NULL,
    numero_fatura VARCHAR(50) UNIQUE NOT NULL,
    fornecedor VARCHAR(150) NOT NULL,
    descricao TEXT,
    valor DECIMAL(15,2) NOT NULL,
    data_emissao DATE NOT NULL,
    data_vencimento DATE NOT NULL,
    data_pagamento DATE,
    status ENUM('pendente', 'paga', 'vencida', 'cancelada') DEFAULT 'pendente',
    forma_pagamento VARCHAR(50),
    observacoes TEXT,
    criado_por INT NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_projeto (projeto_id),
    INDEX idx_status (status),
    INDEX idx_vencimento (data_vencimento),
    INDEX idx_numero (numero_fatura),
    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE,
    FOREIGN KEY (criado_por) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Fluxo de caixa
CREATE TABLE IF NOT EXISTS fluxo_caixa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    projeto_id INT NOT NULL,
    tipo ENUM('entrada', 'saida') NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    descricao VARCHAR(200) NOT NULL,
    valor DECIMAL(15,2) NOT NULL,
    data_movimento DATE NOT NULL,
    forma_pagamento VARCHAR(50),
    referencia_id INT,
    referencia_tipo VARCHAR(30),
    observacoes TEXT,
    criado_por INT NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_projeto (projeto_id),
    INDEX idx_tipo (tipo),
    INDEX idx_data (data_movimento),
    INDEX idx_referencia (referencia_tipo, referencia_id),
    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE,
    FOREIGN KEY (criado_por) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Popular tipos de custo padrão
INSERT INTO tipos_custo (nome, descricao) VALUES
('Mão de Obra', 'Custos com pessoal e serviços'),
('Materiais', 'Materiais de construção'),
('Equipamentos', 'Aluguel e compra de equipamentos'),
('Transporte', 'Logística e frete'),
('Administrativo', 'Custos administrativos e overhead'),
('Outros', 'Outros custos diversos')
ON DUPLICATE KEY UPDATE nome = nome;

-- Registrar migration
INSERT INTO _migrations (versao, nome) VALUES ('005', 'modulo_financeiro');
