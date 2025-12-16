-- Migration 002: Triggers Automáticos
-- Triggers para automação de processos e validações
-- Data: 2025-12-12

-- ===== TRIGGER: Auto-atualizar progresso do projeto =====

DELIMITER $$

CREATE TRIGGER trg_atualizar_progresso_projeto_insert
AFTER INSERT ON tarefas
FOR EACH ROW
BEGIN
    DECLARE v_progresso DECIMAL(5,2);
    
    -- Calcula progresso médio das tarefas do projeto
    SELECT COALESCE(AVG(progresso_percentual), 0)
    INTO v_progresso
    FROM tarefas
    WHERE projeto_id = NEW.projeto_id;
    
    -- Atualiza o progresso do projeto
    UPDATE projetos
    SET progresso_percentual = v_progresso,
        atualizado_em = CURRENT_TIMESTAMP
    WHERE id = NEW.projeto_id;
END$$

CREATE TRIGGER trg_atualizar_progresso_projeto_update
AFTER UPDATE ON tarefas
FOR EACH ROW
BEGIN
    DECLARE v_progresso DECIMAL(5,2);
    
    -- Calcula progresso médio das tarefas do projeto
    SELECT COALESCE(AVG(progresso_percentual), 0)
    INTO v_progresso
    FROM tarefas
    WHERE projeto_id = NEW.projeto_id;
    
    -- Atualiza o progresso do projeto
    UPDATE projetos
    SET progresso_percentual = v_progresso,
        atualizado_em = CURRENT_TIMESTAMP
    WHERE id = NEW.projeto_id;
END$$

CREATE TRIGGER trg_atualizar_progresso_projeto_delete
AFTER DELETE ON tarefas
FOR EACH ROW
BEGIN
    DECLARE v_progresso DECIMAL(5,2);
    
    -- Calcula progresso médio das tarefas do projeto
    SELECT COALESCE(AVG(progresso_percentual), 0)
    INTO v_progresso
    FROM tarefas
    WHERE projeto_id = OLD.projeto_id;
    
    -- Atualiza o progresso do projeto
    UPDATE projetos
    SET progresso_percentual = v_progresso,
        atualizado_em = CURRENT_TIMESTAMP
    WHERE id = OLD.projeto_id;
END$$

DELIMITER ;

-- ===== TRIGGER: Notificação quando tarefa é atribuída =====

DELIMITER $$

CREATE TRIGGER trg_notificar_tarefa_atribuida
AFTER INSERT ON tarefas
FOR EACH ROW
BEGIN
    -- Se há um responsável, criar notificação
    IF NEW.responsavel_id IS NOT NULL THEN
        INSERT INTO notificacoes (usuario_id, tipo, titulo, mensagem, link)
        VALUES (
            NEW.responsavel_id,
            'tarefa',
            'Nova tarefa atribuída',
            CONCAT('Você foi atribuído à tarefa: ', NEW.titulo),
            CONCAT('/projetos/', NEW.projeto_id, '/tarefas/', NEW.id)
        );
    END IF;
END$$

CREATE TRIGGER trg_notificar_tarefa_reatribuida
AFTER UPDATE ON tarefas
FOR EACH ROW
BEGIN
    -- Se o responsável mudou, notificar o novo responsável
    IF NEW.responsavel_id IS NOT NULL AND (OLD.responsavel_id IS NULL OR NEW.responsavel_id != OLD.responsavel_id) THEN
        INSERT INTO notificacoes (usuario_id, tipo, titulo, mensagem, link)
        VALUES (
            NEW.responsavel_id,
            'tarefa',
            'Tarefa atribuída a você',
            CONCAT('Você foi atribuído à tarefa: ', NEW.titulo),
            CONCAT('/projetos/', NEW.projeto_id, '/tarefas/', NEW.id)
        );
    END IF;
END$$

DELIMITER ;

-- ===== TRIGGER: Notificação quando tarefa está atrasada =====

DELIMITER $$

CREATE TRIGGER trg_notificar_tarefa_atrasada
AFTER UPDATE ON tarefas
FOR EACH ROW
BEGIN
    -- Se a tarefa passou do prazo e não está concluída
    IF NEW.data_fim_prevista < CURDATE() 
       AND NEW.status != 'concluida' 
       AND (OLD.data_fim_prevista >= CURDATE() OR OLD.status = 'concluida')
       AND NEW.responsavel_id IS NOT NULL THEN
        
        INSERT INTO notificacoes (usuario_id, tipo, titulo, mensagem, link)
        VALUES (
            NEW.responsavel_id,
            'tarefa',
            '⚠️ Tarefa Atrasada',
            CONCAT('A tarefa "', NEW.titulo, '" está atrasada!'),
            CONCAT('/projetos/', NEW.projeto_id, '/tarefas/', NEW.id)
        );
    END IF;
END$$

DELIMITER ;

-- ===== TRIGGER: Notificação ao adicionar membro na equipe =====

DELIMITER $$

CREATE TRIGGER trg_notificar_membro_adicionado
AFTER INSERT ON equipes
FOR EACH ROW
BEGIN
    DECLARE v_projeto_nome VARCHAR(150);
    
    -- Buscar nome do projeto
    SELECT nome INTO v_projeto_nome FROM projetos WHERE id = NEW.projeto_id;
    
    -- Criar notificação para o novo membro
    INSERT INTO notificacoes (usuario_id, tipo, titulo, mensagem, link)
    VALUES (
        NEW.usuario_id,
        'projeto',
        'Adicionado a um projeto',
        CONCAT('Você foi adicionado ao projeto: ', v_projeto_nome, ' como ', NEW.papel),
        CONCAT('/projetos/', NEW.projeto_id)
    );
END$$

DELIMITER ;

-- ===== TRIGGER: Notificação de nova mensagem no chat =====

DELIMITER $$

CREATE TRIGGER trg_notificar_nova_mensagem
AFTER INSERT ON mensagens
FOR EACH ROW
BEGIN
    DECLARE v_chat_nome VARCHAR(100);
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_usuario_id INT;
    
    -- Cursor para todos os participantes do chat exceto quem enviou
    DECLARE cur_participantes CURSOR FOR 
        SELECT usuario_id 
        FROM chat_participantes 
        WHERE chat_id = NEW.chat_id AND usuario_id != NEW.usuario_id;
    
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    -- Buscar nome do chat
    SELECT nome INTO v_chat_nome FROM chats WHERE id = NEW.chat_id;
    
    -- Notificar todos os participantes
    OPEN cur_participantes;
    
    read_loop: LOOP
        FETCH cur_participantes INTO v_usuario_id;
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        INSERT INTO notificacoes (usuario_id, tipo, titulo, mensagem, link)
        VALUES (
            v_usuario_id,
            'mensagem',
            CONCAT('Nova mensagem em ', v_chat_nome),
            LEFT(NEW.mensagem, 100),
            CONCAT('/chats/', NEW.chat_id)
        );
    END LOOP;
    
    CLOSE cur_participantes;
END$$

DELIMITER ;

-- ===== TRIGGER: Notificação de novo documento =====

DELIMITER $$

CREATE TRIGGER trg_notificar_novo_documento
AFTER INSERT ON documentos
FOR EACH ROW
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_usuario_id INT;
    DECLARE v_projeto_nome VARCHAR(150);
    
    -- Cursor para todos os membros ativos da equipe do projeto
    DECLARE cur_equipe CURSOR FOR 
        SELECT usuario_id 
        FROM equipes 
        WHERE projeto_id = NEW.projeto_id 
        AND ativo = TRUE 
        AND usuario_id != NEW.usuario_upload_id;
    
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    -- Buscar nome do projeto
    SELECT nome INTO v_projeto_nome FROM projetos WHERE id = NEW.projeto_id;
    
    -- Notificar toda a equipe
    OPEN cur_equipe;
    
    read_loop: LOOP
        FETCH cur_equipe INTO v_usuario_id;
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        INSERT INTO notificacoes (usuario_id, tipo, titulo, mensagem, link)
        VALUES (
            v_usuario_id,
            'documento',
            'Novo documento adicionado',
            CONCAT('Documento "', NEW.nome, '" foi adicionado ao projeto ', v_projeto_nome),
            CONCAT('/projetos/', NEW.projeto_id, '/documentos/', NEW.id)
        );
    END LOOP;
    
    CLOSE cur_equipe;
END$$

DELIMITER ;

-- ===== TRIGGER: Validar datas do projeto =====

DELIMITER $$

CREATE TRIGGER trg_validar_datas_projeto_insert
BEFORE INSERT ON projetos
FOR EACH ROW
BEGIN
    -- Validar que data_fim_prevista >= data_inicio
    IF NEW.data_fim_prevista IS NOT NULL AND NEW.data_inicio IS NOT NULL THEN
        IF NEW.data_fim_prevista < NEW.data_inicio THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Data de fim prevista não pode ser anterior à data de início';
        END IF;
    END IF;
    
    -- Validar progresso entre 0 e 100
    IF NEW.progresso_percentual < 0 OR NEW.progresso_percentual > 100 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Progresso percentual deve estar entre 0 e 100';
    END IF;
END$$

CREATE TRIGGER trg_validar_datas_projeto_update
BEFORE UPDATE ON projetos
FOR EACH ROW
BEGIN
    -- Validar que data_fim_prevista >= data_inicio
    IF NEW.data_fim_prevista IS NOT NULL AND NEW.data_inicio IS NOT NULL THEN
        IF NEW.data_fim_prevista < NEW.data_inicio THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Data de fim prevista não pode ser anterior à data de início';
        END IF;
    END IF;
    
    -- Validar progresso entre 0 e 100
    IF NEW.progresso_percentual < 0 OR NEW.progresso_percentual > 100 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Progresso percentual deve estar entre 0 e 100';
    END IF;
END$$

DELIMITER ;

-- ===== TRIGGER: Validar datas das tarefas =====

DELIMITER $$

CREATE TRIGGER trg_validar_datas_tarefa_insert
BEFORE INSERT ON tarefas
FOR EACH ROW
BEGIN
    -- Validar que data_fim_prevista >= data_inicio
    IF NEW.data_fim_prevista IS NOT NULL AND NEW.data_inicio IS NOT NULL THEN
        IF NEW.data_fim_prevista < NEW.data_inicio THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Data de fim prevista não pode ser anterior à data de início da tarefa';
        END IF;
    END IF;
    
    -- Validar progresso entre 0 e 100
    IF NEW.progresso_percentual < 0 OR NEW.progresso_percentual > 100 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Progresso percentual da tarefa deve estar entre 0 e 100';
    END IF;
END$$

CREATE TRIGGER trg_validar_datas_tarefa_update
BEFORE UPDATE ON tarefas
FOR EACH ROW
BEGIN
    -- Validar que data_fim_prevista >= data_inicio
    IF NEW.data_fim_prevista IS NOT NULL AND NEW.data_inicio IS NOT NULL THEN
        IF NEW.data_fim_prevista < NEW.data_inicio THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Data de fim prevista não pode ser anterior à data de início da tarefa';
        END IF;
    END IF;
    
    -- Validar progresso entre 0 e 100
    IF NEW.progresso_percentual < 0 OR NEW.progresso_percentual > 100 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Progresso percentual da tarefa deve estar entre 0 e 100';
    END IF;
END$$

DELIMITER ;

-- ===== TRIGGER: Auto-completar tarefa quando progresso = 100 =====

DELIMITER $$

CREATE TRIGGER trg_auto_completar_tarefa
BEFORE UPDATE ON tarefas
FOR EACH ROW
BEGIN
    -- Se progresso chegou a 100%, marcar como concluída
    IF NEW.progresso_percentual >= 100 AND NEW.status != 'concluida' THEN
        SET NEW.status = 'concluida';
        SET NEW.data_fim_real = CURDATE();
    END IF;
END$$

DELIMITER ;

-- ===== TRIGGER: Registrar métricas diárias automaticamente =====

DELIMITER $$

CREATE TRIGGER trg_registrar_metricas_projeto
AFTER UPDATE ON projetos
FOR EACH ROW
BEGIN
    DECLARE v_tarefas_concluidas INT;
    DECLARE v_tarefas_atrasadas INT;
    DECLARE v_valor_gasto DECIMAL(15,2);
    
    -- Contar tarefas
    SELECT 
        COUNT(CASE WHEN status = 'concluida' THEN 1 END),
        COUNT(CASE WHEN data_fim_prevista < CURDATE() AND status != 'concluida' THEN 1 END)
    INTO v_tarefas_concluidas, v_tarefas_atrasadas
    FROM tarefas
    WHERE projeto_id = NEW.id;
    
    -- Calcular valor gasto
    SELECT COALESCE(SUM(valor_real), 0)
    INTO v_valor_gasto
    FROM orcamentos
    WHERE projeto_id = NEW.id AND status = 'pago';
    
    -- Inserir ou atualizar métrica do dia
    INSERT INTO metricas_projeto (
        projeto_id, data_registro, tarefas_concluidas, tarefas_atrasadas,
        progresso_fisico, valor_gasto
    ) VALUES (
        NEW.id, CURDATE(), v_tarefas_concluidas, v_tarefas_atrasadas,
        NEW.progresso_percentual, v_valor_gasto
    )
    ON DUPLICATE KEY UPDATE
        tarefas_concluidas = v_tarefas_concluidas,
        tarefas_atrasadas = v_tarefas_atrasadas,
        progresso_fisico = NEW.progresso_percentual,
        valor_gasto = v_valor_gasto;
END$$

DELIMITER ;

-- Registrar execução da migration
INSERT INTO _migrations (versao, nome) VALUES ('002', 'Triggers Automáticos');
