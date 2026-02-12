-- ============================================
-- SCHEMA DE FINANCEIRO
-- Para ser executado após criar o banco PostgreSQL
-- ============================================

-- Tipos de custos
CREATE TABLE IF NOT EXISTS tipos_custo (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  nome VARCHAR(50) UNIQUE NOT NULL,
  descricao TEXT,
  cor_hex VARCHAR(7) DEFAULT '#3B82F6',
  ativo BOOLEAN DEFAULT true,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Custos por projeto
CREATE TABLE IF NOT EXISTS custos (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  projeto_id INTEGER NOT NULL,
  tarefa_id INTEGER,
  tipo_custo_id INTEGER NOT NULL,
  descricao TEXT NOT NULL,
  valor DECIMAL(10, 2) NOT NULL,
  moeda VARCHAR(3) DEFAULT 'BRL',
  data_custo DATE NOT NULL,
  responsavel_id INTEGER,
  notas TEXT,
  comprovante_url VARCHAR(255),
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(projeto_id) REFERENCES projetos(id) ON DELETE CASCADE,
  FOREIGN KEY(tarefa_id) REFERENCES tarefas(id) ON DELETE SET NULL,
  FOREIGN KEY(tipo_custo_id) REFERENCES tipos_custo(id),
  FOREIGN KEY(responsavel_id) REFERENCES usuarios(id),
  INDEX idx_projeto (projeto_id),
  INDEX idx_data (data_custo),
  INDEX idx_tipo (tipo_custo_id)
);

-- Orçamentos por projeto
CREATE TABLE IF NOT EXISTS orcamentos (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  projeto_id INTEGER NOT NULL UNIQUE,
  valor_total DECIMAL(10, 2) NOT NULL,
  moeda VARCHAR(3) DEFAULT 'BRL',
  data_criacao DATE DEFAULT CURRENT_DATE,
  data_prevista_conclusao DATE,
  status VARCHAR(20) DEFAULT 'ativo',
  notas TEXT,
  criado_por INTEGER,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(projeto_id) REFERENCES projetos(id) ON DELETE CASCADE,
  FOREIGN KEY(criado_por) REFERENCES usuarios(id),
  INDEX idx_status (status)
);

-- Linhas detalhadas do orçamento
CREATE TABLE IF NOT EXISTS linhas_orcamento (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  orcamento_id INTEGER NOT NULL,
  tipo_custo_id INTEGER NOT NULL,
  valor_estimado DECIMAL(10, 2) NOT NULL,
  percentual_alocado DECIMAL(5, 2),
  descricao TEXT,
  orderm INT DEFAULT 0,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(orcamento_id) REFERENCES orcamentos(id) ON DELETE CASCADE,
  FOREIGN KEY(tipo_custo_id) REFERENCES tipos_custo(id),
  INDEX idx_orcamento (orcamento_id)
);

-- Faturas
CREATE TABLE IF NOT EXISTS faturas (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  projeto_id INTEGER NOT NULL,
  numero_nf VARCHAR(50) UNIQUE,
  serie_nf VARCHAR(10),
  cnpj_emitente VARCHAR(20),
  data_emissao DATE DEFAULT CURRENT_DATE,
  valor_total DECIMAL(10, 2) NOT NULL,
  moeda VARCHAR(3) DEFAULT 'BRL',
  status VARCHAR(20) DEFAULT 'aberta',
  data_vencimento DATE,
  data_pagamento DATE,
  forma_pagamento VARCHAR(50),
  descricao TEXT,
  arquivo_nf_url VARCHAR(255),
  criado_por INTEGER,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(projeto_id) REFERENCES projetos(id) ON DELETE CASCADE,
  FOREIGN KEY(criado_por) REFERENCES usuarios(id),
  INDEX idx_projeto (projeto_id),
  INDEX idx_status (status),
  INDEX idx_data_emissao (data_emissao)
);

-- Itens das faturas
CREATE TABLE IF NOT EXISTS itens_faturas (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  fatura_id INTEGER NOT NULL,
  descricao TEXT NOT NULL,
  quantidade DECIMAL(10, 2),
  unidade VARCHAR(20),
  valor_unitario DECIMAL(10, 2) NOT NULL,
  valor_total DECIMAL(10, 2) NOT NULL,
  ncm VARCHAR(10),
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(fatura_id) REFERENCES faturas(id) ON DELETE CASCADE,
  INDEX idx_fatura (fatura_id)
);

-- Pagamentos de faturas
CREATE TABLE IF NOT EXISTS pagamentos_faturas (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  fatura_id INTEGER NOT NULL,
  valor_pago DECIMAL(10, 2) NOT NULL,
  moeda VARCHAR(3) DEFAULT 'BRL',
  data_pagamento DATE NOT NULL,
  forma_pagamento VARCHAR(50),
  referencia_pagamento VARCHAR(100),
  comprovante_url VARCHAR(255),
  notas TEXT,
  criado_por INTEGER,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(fatura_id) REFERENCES faturas(id) ON DELETE CASCADE,
  FOREIGN KEY(criado_por) REFERENCES usuarios(id),
  INDEX idx_data (data_pagamento)
);

-- Fluxo de caixa
CREATE TABLE IF NOT EXISTS fluxo_caixa (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  projeto_id INTEGER NOT NULL,
  tipo VARCHAR(20),
  descricao TEXT NOT NULL,
  valor DECIMAL(10, 2) NOT NULL,
  moeda VARCHAR(3) DEFAULT 'BRL',
  data_movimento DATE NOT NULL,
  categoria VARCHAR(50),
  referencia_id INTEGER,
  referencia_tipo VARCHAR(50),
  criado_por INTEGER,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(projeto_id) REFERENCES projetos(id) ON DELETE CASCADE,
  FOREIGN KEY(criado_por) REFERENCES usuarios(id),
  INDEX idx_projeto (projeto_id),
  INDEX idx_data (data_movimento),
  INDEX idx_tipo (tipo)
);

-- Relatórios financeiros
CREATE TABLE IF NOT EXISTS relatorios_financeiros (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  projeto_id INTEGER NOT NULL,
  titulo VARCHAR(255) NOT NULL,
  tipo VARCHAR(50),
  periodo_inicio DATE,
  periodo_fim DATE,
  dados_json LONGTEXT,
  criado_por INTEGER,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY(projeto_id) REFERENCES projetos(id) ON DELETE CASCADE,
  FOREIGN KEY(criado_por) REFERENCES usuarios(id),
  INDEX idx_projeto (projeto_id),
  INDEX idx_periodo (periodo_inicio, periodo_fim)
);

-- ============================================
-- INSERIR TIPOS DE CUSTO PADRÃO
-- ============================================

INSERT INTO tipos_custo (nome, descricao, cor_hex) VALUES
('material', 'Materiais e insumos', '#3B82F6'),
('mao_obra', 'Custo de mão de obra', '#10B981'),
('equipamento', 'Aluguel/compra de equipamentos', '#F59E0B'),
('transporte', 'Custos de transporte', '#8B5CF6'),
('outros', 'Outros custos', '#EF4444')
ON DUPLICATE KEY UPDATE descricao=descricao;

-- ============================================
-- CRIAR ÍNDICES ADICIONAIS PARA PERFORMANCE
-- ============================================

CREATE INDEX IF NOT EXISTS idx_custos_valor ON custos(valor);
CREATE INDEX IF NOT EXISTS idx_custos_data_range ON custos(data_custo, projeto_id);
CREATE INDEX IF NOT EXISTS idx_orcamentos_valor ON orcamentos(valor_total);
CREATE INDEX IF NOT EXISTS idx_faturas_valor ON faturas(valor_total);
CREATE INDEX IF NOT EXISTS idx_faturas_vencimento ON faturas(data_vencimento, status);
CREATE INDEX IF NOT EXISTS idx_fluxo_caixa_mes ON fluxo_caixa(YEAR(data_movimento), MONTH(data_movimento));
