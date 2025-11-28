-- Queries SQL Úteis - Gerenciador de Projetos
-- Views, procedures e queries comuns para o sistema

-- ===== VIEWS =====

-- View: Projetos com estatísticas completas
CREATE OR REPLACE VIEW vw_projetos_completo AS
SELECT 
    p.*,
    u.nome AS criador_nome,
    u.email AS criador_email,
    COUNT(DISTINCT t.id) AS total_tarefas,
    COUNT(DISTINCT CASE WHEN t.status = 'concluida' THEN t.id END) AS tarefas_concluidas,
    COUNT(DISTINCT CASE WHEN t.status = 'a_fazer' THEN t.id END) AS tarefas_pendentes,
    COUNT(DISTINCT CASE WHEN t.data_fim_prevista < CURDATE() AND t.status != 'concluida' THEN t.id END) AS tarefas_atrasadas,
    COUNT(DISTINCT e.usuario_id) AS total_membros,
    COALESCE(SUM(m.quantidade_utilizada * m.preco_unitario), 0) AS valor_gasto_materiais,
    COALESCE(SUM(o.valor_real), 0) AS valor_gasto_total,
    ROUND(p.progresso_percentual, 2) AS progresso
FROM projetos p
LEFT JOIN usuarios u ON p.criador_id = u.id
LEFT JOIN tarefas t ON p.id = t.projeto_id
LEFT JOIN equipes e ON p.id = e.projeto_id AND e.ativo = TRUE
LEFT JOIN materiais m ON p.id = m.projeto_id
LEFT JOIN orcamentos o ON p.id = o.projeto_id AND o.status = 'pago'
GROUP BY p.id, u.nome, u.email;

-- View: Dashboard de tarefas por usuário
CREATE OR REPLACE VIEW vw_tarefas_usuario AS
SELECT 
    u.id AS usuario_id,
    u.nome AS usuario_nome,
    COUNT(t.id) AS total_tarefas,
    COUNT(CASE WHEN t.status = 'concluida' THEN 1 END) AS tarefas_concluidas,
    COUNT(CASE WHEN t.status IN ('a_fazer', 'em_andamento') THEN 1 END) AS tarefas_pendentes,
    COUNT(CASE WHEN t.data_fim_prevista < CURDATE() AND t.status != 'concluida' THEN 1 END) AS tarefas_atrasadas,
    ROUND(AVG(CASE WHEN t.status = 'concluida' THEN t.progresso_percentual END), 2) AS media_progresso
FROM usuarios u
LEFT JOIN tarefas t ON u.id = t.responsavel_id
WHERE u.ativo = TRUE
GROUP BY u.id, u.nome;

-- View: Relatório de orçamento por projeto
CREATE OR REPLACE VIEW vw_orcamento_projeto AS
SELECT 
    p.id AS projeto_id,
    p.nome AS projeto_nome,
    p.valor_total AS valor_total_projeto,
    COALESCE(SUM(o.valor_previsto), 0) AS valor_orcado,
    COALESCE(SUM(o.valor_real), 0) AS valor_gasto,
    COALESCE(SUM(o.valor_previsto) - SUM(o.valor_real), 0) AS saldo,
    ROUND((COALESCE(SUM(o.valor_real), 0) / NULLIF(SUM(o.valor_previsto), 0)) * 100, 2) AS percentual_gasto
FROM projetos p
LEFT JOIN orcamentos o ON p.id = o.projeto_id
GROUP BY p.id, p.nome, p.valor_total;

-- View: Chat com última mensagem
CREATE OR REPLACE VIEW vw_chats_resumo AS
SELECT 
    c.id AS chat_id,
    c.projeto_id,
    c.nome AS chat_nome,
    c.tipo,
    p.nome AS projeto_nome,
    COUNT(DISTINCT cp.usuario_id) AS total_participantes,
    COUNT(m.id) AS total_mensagens,
    MAX(m.criado_em) AS ultima_mensagem_data,
    (SELECT mensagem FROM mensagens WHERE chat_id = c.id ORDER BY criado_em DESC LIMIT 1) AS ultima_mensagem,
    (SELECT u.nome FROM mensagens mm JOIN usuarios u ON mm.usuario_id = u.id WHERE mm.chat_id = c.id ORDER BY mm.criado_em DESC LIMIT 1) AS ultimo_usuario
FROM chats c
JOIN projetos p ON c.projeto_id = p.id
LEFT JOIN chat_participantes cp ON c.id = cp.chat_id
LEFT JOIN mensagens m ON c.id = m.chat_id
GROUP BY c.id, c.projeto_id, c.nome, c.tipo, p.nome;

-- ===== STORED PROCEDURES =====

-- Procedure: Atualizar progresso do projeto baseado nas tarefas
DELIMITER $$

CREATE PROCEDURE sp_atualizar_progresso_projeto(IN p_projeto_id INT)
BEGIN
    DECLARE v_progresso DECIMAL(5,2);
    
    -- Calcula progresso baseado nas tarefas
    SELECT 
        COALESCE(AVG(progresso_percentual), 0)
    INTO v_progresso
    FROM tarefas
    WHERE projeto_id = p_projeto_id;
    
    -- Atualiza projeto
    UPDATE projetos
    SET progresso_percentual = v_progresso,
        atualizado_em = CURRENT_TIMESTAMP
    WHERE id = p_projeto_id;
    
    SELECT CONCAT('Progresso atualizado: ', v_progresso, '%') AS resultado;
END$$

DELIMITER ;

-- Procedure: Criar notificação para usuário
DELIMITER $$

CREATE PROCEDURE sp_criar_notificacao(
    IN p_usuario_id INT,
    IN p_tipo ENUM('tarefa', 'mensagem', 'documento', 'projeto', 'sistema'),
    IN p_titulo VARCHAR(150),
    IN p_mensagem TEXT,
    IN p_link VARCHAR(255)
)
BEGIN
    INSERT INTO notificacoes (usuario_id, tipo, titulo, mensagem, link)
    VALUES (p_usuario_id, p_tipo, p_titulo, p_mensagem, p_link);
    
    SELECT LAST_INSERT_ID() AS notificacao_id;
END$$

DELIMITER ;

-- Procedure: Atribuir tarefa e notificar responsável
DELIMITER $$

CREATE PROCEDURE sp_atribuir_tarefa(
    IN p_tarefa_id INT,
    IN p_responsavel_id INT
)
BEGIN
    DECLARE v_titulo VARCHAR(150);
    DECLARE v_projeto_id INT;
    
    -- Busca dados da tarefa
    SELECT titulo, projeto_id INTO v_titulo, v_projeto_id
    FROM tarefas
    WHERE id = p_tarefa_id;
    
    -- Atualiza responsável
    UPDATE tarefas
    SET responsavel_id = p_responsavel_id,
        atualizado_em = CURRENT_TIMESTAMP
    WHERE id = p_tarefa_id;
    
    -- Cria notificação
    INSERT INTO notificacoes (usuario_id, tipo, titulo, mensagem, link)
    VALUES (
        p_responsavel_id,
        'tarefa',
        'Nova tarefa atribuída',
        CONCAT('Você foi atribuído à tarefa: ', v_titulo),
        CONCAT('/projetos/', v_projeto_id, '/tarefas/', p_tarefa_id)
    );
    
    SELECT 'Tarefa atribuída e notificação enviada' AS resultado;
END$$

DELIMITER ;

-- ===== QUERIES ÚTEIS =====

-- Query: Top 5 projetos com mais tarefas atrasadas
SELECT 
    p.nome,
    COUNT(t.id) AS tarefas_atrasadas,
    p.status,
    p.progresso_percentual
FROM projetos p
JOIN tarefas t ON p.id = t.projeto_id
WHERE t.data_fim_prevista < CURDATE()
    AND t.status != 'concluida'
    AND p.status != 'cancelado'
GROUP BY p.id, p.nome, p.status, p.progresso_percentual
ORDER BY tarefas_atrasadas DESC
LIMIT 5;

-- Query: Usuários mais produtivos (tarefas concluídas no mês)
SELECT 
    u.nome,
    u.cargo,
    COUNT(t.id) AS tarefas_concluidas,
    ROUND(AVG(DATEDIFF(t.data_fim_real, t.data_inicio)), 1) AS tempo_medio_dias
FROM usuarios u
JOIN tarefas t ON u.id = t.responsavel_id
WHERE t.status = 'concluida'
    AND MONTH(t.data_fim_real) = MONTH(CURRENT_DATE)
    AND YEAR(t.data_fim_real) = YEAR(CURRENT_DATE)
GROUP BY u.id, u.nome, u.cargo
ORDER BY tarefas_concluidas DESC
LIMIT 10;

-- Query: Análise de custos por categoria
SELECT 
    categoria,
    COUNT(*) AS total_itens,
    SUM(valor_previsto) AS valor_previsto,
    SUM(valor_real) AS valor_real,
    SUM(valor_previsto) - SUM(valor_real) AS economia,
    ROUND((SUM(valor_real) / SUM(valor_previsto)) * 100, 2) AS percentual_execucao
FROM orcamentos
WHERE status IN ('aprovado', 'pago')
GROUP BY categoria
ORDER BY valor_real DESC;

-- Query: Documentos mais recentes por projeto
SELECT 
    p.nome AS projeto,
    d.nome AS documento,
    d.tipo,
    u.nome AS upload_por,
    d.criado_em,
    ROUND(d.tamanho_kb / 1024, 2) AS tamanho_mb
FROM documentos d
JOIN projetos p ON d.projeto_id = p.id
JOIN usuarios u ON d.usuario_upload_id = u.id
ORDER BY d.criado_em DESC
LIMIT 20;

-- Query: Atividade no chat por projeto
SELECT 
    p.nome AS projeto,
    c.nome AS chat,
    COUNT(DISTINCT m.usuario_id) AS usuarios_ativos,
    COUNT(m.id) AS total_mensagens,
    DATE(MAX(m.criado_em)) AS ultima_atividade
FROM chats c
JOIN projetos p ON c.projeto_id = p.id
LEFT JOIN mensagens m ON c.id = m.chat_id
WHERE m.criado_em >= DATE_SUB(CURRENT_DATE, INTERVAL 7 DAY)
GROUP BY p.id, p.nome, c.id, c.nome
ORDER BY total_mensagens DESC;

-- Query: Materiais com estoque baixo (menos de 10% restante)
SELECT 
    p.nome AS projeto,
    m.nome AS material,
    m.unidade,
    m.quantidade_prevista,
    m.quantidade_utilizada,
    (m.quantidade_prevista - m.quantidade_utilizada) AS quantidade_restante,
    ROUND(((m.quantidade_prevista - m.quantidade_utilizada) / m.quantidade_prevista) * 100, 2) AS percentual_restante
FROM materiais m
JOIN projetos p ON m.projeto_id = p.id
WHERE (m.quantidade_prevista - m.quantidade_utilizada) > 0
    AND ((m.quantidade_prevista - m.quantidade_utilizada) / m.quantidade_prevista) < 0.1
ORDER BY percentual_restante ASC;

-- Query: Resumo mensal de conclusões
SELECT 
    DATE_FORMAT(t.data_fim_real, '%Y-%m') AS mes_ano,
    COUNT(*) AS tarefas_concluidas,
    COUNT(DISTINCT t.projeto_id) AS projetos_ativos,
    COUNT(DISTINCT t.responsavel_id) AS usuarios_envolvidos,
    ROUND(AVG(DATEDIFF(t.data_fim_real, t.data_inicio)), 1) AS tempo_medio_dias
FROM tarefas t
WHERE t.status = 'concluida'
    AND t.data_fim_real >= DATE_SUB(CURRENT_DATE, INTERVAL 12 MONTH)
GROUP BY DATE_FORMAT(t.data_fim_real, '%Y-%m')
ORDER BY mes_ano DESC;

-- ===== ÍNDICES ADICIONAIS (opcional - melhorar performance) =====

-- Índices para queries de dashboard
CREATE INDEX idx_tarefas_data_status ON tarefas(data_fim_prevista, status);
CREATE INDEX idx_mensagens_chat_data ON mensagens(chat_id, criado_em DESC);
CREATE INDEX idx_documentos_projeto_data ON documentos(projeto_id, criado_em DESC);
CREATE INDEX idx_orcamentos_status_categoria ON orcamentos(status, categoria);

-- ===== TRIGGERS =====

-- Trigger: Atualizar timestamp de atualização do projeto quando tarefa mudar
DELIMITER $$

CREATE TRIGGER trg_tarefa_atualiza_projeto
AFTER UPDATE ON tarefas
FOR EACH ROW
BEGIN
    IF OLD.status != NEW.status OR OLD.progresso_percentual != NEW.progresso_percentual THEN
        UPDATE projetos 
        SET atualizado_em = CURRENT_TIMESTAMP 
        WHERE id = NEW.projeto_id;
    END IF;
END$$

DELIMITER ;

-- Trigger: Criar métrica diária quando projeto é atualizado
DELIMITER $$

CREATE TRIGGER trg_projeto_cria_metrica
AFTER UPDATE ON projetos
FOR EACH ROW
BEGIN
    IF OLD.progresso_percentual != NEW.progresso_percentual THEN
        INSERT INTO metricas_projeto (
            projeto_id, 
            data_registro, 
            progresso_fisico
        ) VALUES (
            NEW.id,
            CURRENT_DATE,
            NEW.progresso_percentual
        )
        ON DUPLICATE KEY UPDATE 
            progresso_fisico = NEW.progresso_percentual;
    END IF;
END$$

DELIMITER ;
