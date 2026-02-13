-- Migration: Adicionar tabela tokens_reset_senha
-- Data: 2026-02-13
-- Desenvolvedor: Sistema de correções

CREATE TABLE IF NOT EXISTS tokens_reset_senha (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    usado BOOLEAN DEFAULT FALSE,
    expira_em TIMESTAMP NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_token (token),
    INDEX idx_usuario (usuario_id),
    INDEX idx_expira (expira_em),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Registrar migration
INSERT INTO _migrations (versao, nome) VALUES ('004', 'tokens_reset_senha');
