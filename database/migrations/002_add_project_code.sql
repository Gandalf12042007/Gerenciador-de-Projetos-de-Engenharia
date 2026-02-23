-- Migration 002: Add unique project_code to projetos
-- Data: 2026-02-23

ALTER TABLE projetos
    ADD COLUMN project_code VARCHAR(8) NULL AFTER nome;

-- Ensure code is unique
CREATE UNIQUE INDEX ux_projetos_project_code ON projetos(project_code);

-- Populate code for existing projects if missing (simple random, may be replaced manually later)
UPDATE projetos
SET project_code = LPAD(HEX(FLOOR(RAND()*0xFFFFFF)), 4, '0')
WHERE project_code IS NULL;
