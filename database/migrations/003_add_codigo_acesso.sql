-- =====================================================
-- MIGRATION: Adicionar código de acesso aos projetos
-- Data: 2026-02-10
-- =====================================================

-- Adiciona coluna codigo_acesso à tabela projetos
ALTER TABLE projetos ADD COLUMN codigo_acesso TEXT UNIQUE;

-- Cria índice para busca rápida por código
CREATE INDEX IF NOT EXISTS idx_projetos_codigo ON projetos(codigo_acesso);

-- Adiciona coluna role aos usuários para controle de acesso
ALTER TABLE usuarios ADD COLUMN role TEXT DEFAULT 'usuario' CHECK(role IN ('admin', 'gerente', 'engenheiro', 'tecnico', 'cliente', 'usuario'));

-- Adiciona coluna funcao às equipes (diferente de papel - funcao é mais flexível)
ALTER TABLE equipes ADD COLUMN funcao TEXT DEFAULT 'membro';

-- Registra a migração
INSERT INTO _migrations (versao, nome) VALUES ('003', 'add_codigo_acesso_projetos');
