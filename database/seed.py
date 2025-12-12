"""
Seeds - Dados iniciais para o banco de dados
Popula o sistema com dados de exemplo para desenvolvimento e testes
"""

import os
import sys
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
import hashlib
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

class Seeder:
    def __init__(self, db_config):
        """Inicializa o seeder"""
        self.db_config = db_config
        self.connection = None
        
    def connect(self):
        """Conecta ao banco de dados"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            if self.connection.is_connected():
                print(f"✓ Conectado ao MySQL - {self.db_config['database']}")
                return True
        except Error as e:
            print(f"✗ Erro ao conectar: {e}")
            return False
    
    def disconnect(self):
        """Desconecta do banco"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✓ Desconectado do MySQL")
    
    def hash_password(self, password):
        """Gera hash SHA-256 da senha"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def clear_all_data(self):
        """Limpa todos os dados das tabelas (mantém estrutura)"""
        print("\n🗑️  Limpando dados existentes...")
        
        cursor = self.connection.cursor()
        
        # Desabilita verificação de FK temporariamente
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        tables = [
            'notificacoes', 'metricas_projeto', 'orcamentos', 'materiais',
            'mensagens', 'chat_participantes', 'chats',
            'versoes_documento', 'documentos',
            'comentarios_tarefa', 'tarefa_dependencias', 'tarefas',
            'equipes', 'projetos',
            'usuario_permissoes', 'permissoes', 'usuarios'
        ]
        
        for table in tables:
            cursor.execute(f"TRUNCATE TABLE {table}")
            print(f"  ✓ {table}")
        
        # Reabilita verificação de FK
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        self.connection.commit()
        cursor.close()
        
        print("✓ Dados limpos com sucesso!\n")
    
    def seed_usuarios(self):
        """Cria usuários de exemplo"""
        print("👥 Criando usuários...")
        
        usuarios = [
            ('João Silva', 'joao.silva@exemplo.com', 'senha123', '11 98765-4321', 'Engenheiro Civil', True),
            ('Maria Santos', 'maria.santos@exemplo.com', 'senha123', '11 98765-1234', 'Gerente de Projetos', True),
            ('Pedro Oliveira', 'pedro.oliveira@exemplo.com', 'senha123', '11 98765-5678', 'Técnico em Edificações', True),
            ('Ana Costa', 'ana.costa@exemplo.com', 'senha123', '11 98765-9012', 'Arquiteta', True),
            ('Carlos Souza', 'carlos.souza@exemplo.com', 'senha123', '11 98765-3456', 'Engenheiro Estrutural', True),
        ]
        
        cursor = self.connection.cursor()
        
        for nome, email, senha, telefone, cargo, ativo in usuarios:
            senha_hash = self.hash_password(senha)
            cursor.execute("""
                INSERT INTO usuarios (nome, email, senha_hash, telefone, cargo, ativo)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (nome, email, senha_hash, telefone, cargo, ativo))
            print(f"  ✓ {nome} ({email})")
        
        self.connection.commit()
        cursor.close()
        
        print(f"✓ {len(usuarios)} usuários criados\n")
    
    def seed_permissoes(self):
        """Cria permissões do sistema"""
        print("🔐 Criando permissões...")
        
        permissoes = [
            ('admin', 'Administrador com acesso total ao sistema'),
            ('gerente', 'Gerente de projetos - pode criar e gerenciar projetos'),
            ('engenheiro', 'Engenheiro - pode editar tarefas e documentos'),
            ('tecnico', 'Técnico - pode visualizar e atualizar tarefas'),
            ('cliente', 'Cliente - visualização limitada do projeto'),
            ('visualizador', 'Apenas visualização de projetos'),
        ]
        
        cursor = self.connection.cursor()
        
        for nome, descricao in permissoes:
            cursor.execute("""
                INSERT INTO permissoes (nome, descricao)
                VALUES (%s, %s)
            """, (nome, descricao))
            print(f"  ✓ {nome}")
        
        self.connection.commit()
        cursor.close()
        
        print(f"✓ {len(permissoes)} permissões criadas\n")
    
    def seed_projetos(self):
        """Cria projetos de exemplo"""
        print("🏗️  Criando projetos...")
        
        hoje = datetime.now().date()
        
        projetos = [
            (
                'Edifício Residencial Portal das Acácias',
                'Construção de edifício residencial com 12 pavimentos, 48 apartamentos, área de lazer completa',
                'Rua das Acácias, 123 - Jardim Primavera',
                'Construtora Prime Ltda',
                2500000.00,
                hoje - timedelta(days=60),
                hoje + timedelta(days=480),
                None,
                'em_andamento',
                35.50,
                1  # criador_id
            ),
            (
                'Reforma Shopping Center Norte',
                'Reforma e modernização de 3 pisos do shopping, incluindo novo sistema de climatização',
                'Av. Shopping, 1000 - Centro',
                'Shopping Center Norte SA',
                850000.00,
                hoje - timedelta(days=30),
                hoje + timedelta(days=120),
                None,
                'em_andamento',
                45.00,
                2
            ),
            (
                'Ponte sobre o Rio Verde',
                'Construção de ponte de concreto armado com 180m de extensão',
                'Rodovia BR-101, km 245',
                'Prefeitura Municipal',
                5200000.00,
                hoje - timedelta(days=90),
                hoje + timedelta(days=540),
                None,
                'em_andamento',
                22.30,
                1
            ),
            (
                'Residência Unifamiliar Alto Padrão',
                'Construção de casa de alto padrão com 450m², piscina, churrasqueira e automação',
                'Condomínio Alphaville, lote 42',
                'Sr. Roberto Almeida',
                1200000.00,
                hoje + timedelta(days=15),
                hoje + timedelta(days=280),
                None,
                'planejamento',
                0.00,
                3
            ),
        ]
        
        cursor = self.connection.cursor()
        
        for projeto in projetos:
            cursor.execute("""
                INSERT INTO projetos (
                    nome, descricao, endereco, cliente, valor_total,
                    data_inicio, data_fim_prevista, data_fim_real,
                    status, progresso_percentual, criador_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, projeto)
            print(f"  ✓ {projeto[0]}")
        
        self.connection.commit()
        cursor.close()
        
        print(f"✓ {len(projetos)} projetos criados\n")
    
    def seed_equipes(self):
        """Atribui usuários às equipes dos projetos"""
        print("👥 Criando equipes dos projetos...")
        
        hoje = datetime.now().date()
        
        equipes = [
            # Projeto 1 - Edifício Residencial
            (1, 1, 'gerente', hoje - timedelta(days=60), None, True),
            (1, 3, 'engenheiro', hoje - timedelta(days=55), None, True),
            (1, 4, 'tecnico', hoje - timedelta(days=50), None, True),
            
            # Projeto 2 - Shopping
            (2, 2, 'gerente', hoje - timedelta(days=30), None, True),
            (2, 5, 'engenheiro', hoje - timedelta(days=28), None, True),
            
            # Projeto 3 - Ponte
            (3, 1, 'gerente', hoje - timedelta(days=90), None, True),
            (3, 5, 'engenheiro', hoje - timedelta(days=85), None, True),
            (3, 3, 'engenheiro', hoje - timedelta(days=80), None, True),
            
            # Projeto 4 - Residência
            (4, 3, 'gerente', hoje + timedelta(days=15), None, False),
            (4, 4, 'engenheiro', hoje + timedelta(days=15), None, False),
        ]
        
        cursor = self.connection.cursor()
        
        for equipe in equipes:
            cursor.execute("""
                INSERT INTO equipes (
                    projeto_id, usuario_id, papel, data_entrada, data_saida, ativo
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, equipe)
        
        self.connection.commit()
        cursor.close()
        
        print(f"✓ {len(equipes)} membros de equipe adicionados\n")
    
    def seed_tarefas(self):
        """Cria tarefas de exemplo"""
        print("✅ Criando tarefas...")
        
        hoje = datetime.now().date()
        
        tarefas = [
            # Projeto 1
            (1, 'Fundação - Escavação', 'Escavação do terreno para fundação profunda', 'concluida', 'alta', 
             hoje - timedelta(days=50), hoje - timedelta(days=40), hoje - timedelta(days=38), 1, 1, 1, 100.00),
            (1, 'Fundação - Estacas', 'Instalação de estacas de fundação', 'concluida', 'alta',
             hoje - timedelta(days=38), hoje - timedelta(days=28), hoje - timedelta(days=27), 1, 1, 2, 100.00),
            (1, 'Estrutura 1º ao 4º pavimento', 'Execução da estrutura de concreto', 'concluida', 'alta',
             hoje - timedelta(days=27), hoje - timedelta(days=10), hoje - timedelta(days=8), 3, 1, 3, 100.00),
            (1, 'Estrutura 5º ao 8º pavimento', 'Continuação da estrutura de concreto', 'em_andamento', 'alta',
             hoje - timedelta(days=8), hoje + timedelta(days=10), None, 3, 1, 4, 65.00),
            (1, 'Instalações hidráulicas', 'Instalação de tubulações e reservatórios', 'a_fazer', 'media',
             hoje + timedelta(days=12), hoje + timedelta(days=30), None, 4, 1, 5, 0.00),
            
            # Projeto 2
            (2, 'Demolição áreas antigas', 'Demolição controlada de estruturas antigas', 'concluida', 'alta',
             hoje - timedelta(days=25), hoje - timedelta(days=15), hoje - timedelta(days=14), 2, 2, 1, 100.00),
            (2, 'Instalação novo sistema climatização', 'Instalação de ar condicionado central', 'em_andamento', 'alta',
             hoje - timedelta(days=10), hoje + timedelta(days=20), None, 5, 2, 2, 40.00),
            (2, 'Acabamento e pintura', 'Acabamento final e pintura das áreas', 'a_fazer', 'media',
             hoje + timedelta(days=25), hoje + timedelta(days=40), None, 5, 2, 3, 0.00),
            
            # Projeto 3
            (3, 'Sondagem do terreno', 'Estudo geotécnico do solo', 'concluida', 'urgente',
             hoje - timedelta(days=85), hoje - timedelta(days=75), hoje - timedelta(days=74), 5, 1, 1, 100.00),
            (3, 'Projeto estrutural detalhado', 'Elaboração do projeto estrutural completo', 'concluida', 'urgente',
             hoje - timedelta(days=70), hoje - timedelta(days=50), hoje - timedelta(days=48), 5, 1, 2, 100.00),
            (3, 'Pilares e blocos de fundação', 'Execução dos pilares da ponte', 'em_andamento', 'alta',
             hoje - timedelta(days=45), hoje + timedelta(days=30), None, 3, 1, 3, 55.00),
        ]
        
        cursor = self.connection.cursor()
        
        for tarefa in tarefas:
            cursor.execute("""
                INSERT INTO tarefas (
                    projeto_id, titulo, descricao, status, prioridade,
                    data_inicio, data_fim_prevista, data_fim_real,
                    responsavel_id, criador_id, ordem, progresso_percentual
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, tarefa)
        
        self.connection.commit()
        cursor.close()
        
        print(f"✓ {len(tarefas)} tarefas criadas\n")
    
    def seed_materiais(self):
        """Cria materiais de exemplo"""
        print("📦 Criando materiais...")
        
        hoje = datetime.now().date()
        
        materiais = [
            (1, 'Cimento CP-II 50kg', 'Cimento Portland tipo II', 'sc', 2000.00, 1450.00, 32.50, 'CimentoBras', hoje - timedelta(days=55)),
            (1, 'Areia média lavada', 'Areia para concreto e argamassa', 'm3', 450.00, 385.00, 85.00, 'Areião Center', hoje - timedelta(days=50)),
            (1, 'Brita 1', 'Pedra britada para concreto', 'm3', 380.00, 320.00, 92.00, 'Pedreira Sul', hoje - timedelta(days=50)),
            (1, 'Aço CA-50 12mm', 'Vergalhão de aço para estrutura', 'kg', 8500.00, 6200.00, 6.80, 'Gerdau', hoje - timedelta(days=45)),
            (2, 'Tinta acrílica branca', 'Tinta para acabamento interno', 'l', 850.00, 320.00, 78.50, 'Tintas Coral', hoje - timedelta(days=20)),
            (3, 'Concreto usinado FCK 40', 'Concreto de alta resistência', 'm3', 1200.00, 450.00, 385.00, 'Concremaster', hoje - timedelta(days=60)),
        ]
        
        cursor = self.connection.cursor()
        
        for material in materiais:
            cursor.execute("""
                INSERT INTO materiais (
                    projeto_id, nome, descricao, unidade,
                    quantidade_prevista, quantidade_utilizada, preco_unitario,
                    fornecedor, data_compra
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, material)
        
        self.connection.commit()
        cursor.close()
        
        print(f"✓ {len(materiais)} materiais criados\n")
    
    def seed_orcamentos(self):
        """Cria itens de orçamento"""
        print("💰 Criando orçamentos...")
        
        hoje = datetime.now().date()
        
        orcamentos = [
            (1, 'Fundação e estacas', 'material', 450000.00, 445000.00, hoje - timedelta(days=50), hoje - timedelta(days=48), 'pago'),
            (1, 'Mão de obra estrutura', 'mao_obra', 850000.00, 520000.00, hoje - timedelta(days=30), hoje - timedelta(days=10), 'pago'),
            (1, 'Materiais acabamento', 'material', 380000.00, 0.00, hoje + timedelta(days=30), None, 'previsto'),
            (2, 'Equipamentos climatização', 'equipamento', 520000.00, 520000.00, hoje - timedelta(days=20), hoje - timedelta(days=18), 'pago'),
            (2, 'Serviços elétricos', 'servico', 180000.00, 95000.00, hoje - timedelta(days=15), None, 'aprovado'),
            (3, 'Projeto estrutural', 'servico', 420000.00, 420000.00, hoje - timedelta(days=70), hoje - timedelta(days=68), 'pago'),
            (3, 'Concreto estrutural', 'material', 2800000.00, 1540000.00, hoje - timedelta(days=45), hoje - timedelta(days=10), 'pago'),
        ]
        
        cursor = self.connection.cursor()
        
        for orc in orcamentos:
            cursor.execute("""
                INSERT INTO orcamentos (
                    projeto_id, descricao, categoria, valor_previsto, valor_real,
                    data_prevista, data_pagamento, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, orc)
        
        self.connection.commit()
        cursor.close()
        
        print(f"✓ {len(orcamentos)} itens de orçamento criados\n")
    
    def seed_documentos(self):
        """Cria documentos de exemplo"""
        print("📄 Criando documentos...")
        
        documentos = [
            (1, 'Projeto Arquitetônico - Plantas Baixas', 'Plantas de todos os pavimentos', 'projeto', '/docs/proj1_plantas.pdf', 2548, '1.0', 1),
            (1, 'Memorial Descritivo', 'Memorial técnico da obra', 'projeto', '/docs/proj1_memorial.pdf', 1850, '1.0', 1),
            (1, 'ART - Execução de Estrutura', 'ART do engenheiro responsável', 'laudo', '/docs/proj1_art_estrutura.pdf', 245, '1.0', 3),
            (2, 'Contrato de Reforma', 'Contrato assinado com o cliente', 'contrato', '/docs/proj2_contrato.pdf', 580, '1.0', 2),
            (2, 'Orçamento Detalhado', 'Planilha orçamentária completa', 'orcamento', '/docs/proj2_orcamento.xlsx', 125, '2.1', 2),
            (3, 'Estudo Geotécnico', 'Relatório de sondagem do terreno', 'laudo', '/docs/proj3_geotecnico.pdf', 4850, '1.0', 5),
            (3, 'Projeto Estrutural', 'Projeto completo da ponte', 'projeto', '/docs/proj3_estrutural.pdf', 8950, '1.0', 5),
        ]
        
        cursor = self.connection.cursor()
        
        for doc in documentos:
            cursor.execute("""
                INSERT INTO documentos (
                    projeto_id, nome, descricao, tipo, arquivo_url,
                    tamanho_kb, versao, usuario_upload_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, doc)
        
        self.connection.commit()
        cursor.close()
        
        print(f"✓ {len(documentos)} documentos criados\n")
    
    def seed_chats(self):
        """Cria chats e mensagens"""
        print("💬 Criando chats e mensagens...")
        
        hoje = datetime.now()
        
        # Criar chats
        chats = [
            (1, 'Discussão Geral - Edifício Portal', 'geral'),
            (2, 'Equipe Reforma Shopping', 'geral'),
            (3, 'Coordenação Ponte Rio Verde', 'geral'),
        ]
        
        cursor = self.connection.cursor()
        
        for chat in chats:
            cursor.execute("""
                INSERT INTO chats (projeto_id, nome, tipo)
                VALUES (%s, %s, %s)
            """, chat)
        
        self.connection.commit()
        
        # Adicionar participantes
        participantes = [
            (1, 1), (1, 3), (1, 4),  # Chat 1
            (2, 2), (2, 5),          # Chat 2
            (3, 1), (3, 3), (3, 5),  # Chat 3
        ]
        
        for chat_id, usuario_id in participantes:
            cursor.execute("""
                INSERT INTO chat_participantes (chat_id, usuario_id)
                VALUES (%s, %s)
            """, (chat_id, usuario_id))
        
        self.connection.commit()
        
        # Criar mensagens
        mensagens = [
            (1, 1, 'Bom dia equipe! Hoje vamos iniciar a concretagem do 5º pavimento.', None, hoje - timedelta(hours=8)),
            (1, 3, 'Ok João, já estou no canteiro verificando as formas.', None, hoje - timedelta(hours=7, minutes=45)),
            (1, 4, 'O caminhão betoneira está confirmado para 9h.', None, hoje - timedelta(hours=7, minutes=30)),
            (1, 1, '@Pedro, não esqueça de verificar o nível das formas antes de concretar.', None, hoje - timedelta(hours=6)),
            (2, 2, 'Pessoal, o sistema de climatização chegou. Podemos iniciar a instalação amanhã.', None, hoje - timedelta(hours=10)),
            (2, 5, 'Perfeito Maria! Vou separar a equipe para montagem.', None, hoje - timedelta(hours=9, minutes=30)),
            (3, 1, 'Recebemos aprovação do projeto estrutural! 🎉', None, hoje - timedelta(days=2)),
            (3, 5, 'Ótima notícia! Vou revisar os detalhes de armação.', None, hoje - timedelta(days=2, hours=2)),
            (3, 3, 'Já podemos solicitar os materiais então?', None, hoje - timedelta(days=1, hours=22)),
        ]
        
        for msg in mensagens:
            cursor.execute("""
                INSERT INTO mensagens (chat_id, usuario_id, mensagem, arquivo_url, criado_em)
                VALUES (%s, %s, %s, %s, %s)
            """, msg)
        
        self.connection.commit()
        cursor.close()
        
        print(f"✓ {len(chats)} chats, {len(participantes)} participantes e {len(mensagens)} mensagens criados\n")
    
    def seed_comentarios(self):
        """Cria comentários nas tarefas"""
        print("💭 Criando comentários...")
        
        hoje = datetime.now()
        
        comentarios = [
            (1, 1, 'Escavação concluída sem problemas. Encontramos solo firme.', hoje - timedelta(days=38)),
            (2, 3, 'Estacas instaladas conforme projeto. Tudo dentro do prazo.', hoje - timedelta(days=27)),
            (4, 3, 'Estamos com 65% concluído. Previsão de terminar em 10 dias.', hoje - timedelta(hours=5)),
            (4, 1, 'Ótimo ritmo Pedro! Vamos manter assim.', hoje - timedelta(hours=4)),
            (7, 5, 'Sistema central já está 40% instalado. Aguardando peças.', hoje - timedelta(hours=12)),
            (11, 5, 'Pilares P1 a P4 concluídos. Iniciando P5 amanhã.', hoje - timedelta(days=1)),
        ]
        
        cursor = self.connection.cursor()
        
        for com in comentarios:
            cursor.execute("""
                INSERT INTO comentarios_tarefa (tarefa_id, usuario_id, comentario, criado_em)
                VALUES (%s, %s, %s, %s)
            """, com)
        
        self.connection.commit()
        cursor.close()
        
        print(f"✓ {len(comentarios)} comentários criados\n")
    
    def seed_dependencias(self):
        """Cria dependências entre tarefas"""
        print("🔗 Criando dependências entre tarefas...")
        
        dependencias = [
            (2, 1, 'termino_inicio'),  # Estacas dependem da escavação
            (3, 2, 'termino_inicio'),  # Estrutura 1-4 depende das estacas
            (4, 3, 'termino_inicio'),  # Estrutura 5-8 depende da 1-4
            (5, 4, 'termino_inicio'),  # Instalações dependem da estrutura
            (8, 7, 'termino_inicio'),  # Acabamento depende da climatização
            (11, 10, 'termino_inicio'), # Pilares dependem do projeto
        ]
        
        cursor = self.connection.cursor()
        
        for dep in dependencias:
            cursor.execute("""
                INSERT INTO tarefa_dependencias (tarefa_id, tarefa_dependente_id, tipo)
                VALUES (%s, %s, %s)
            """, dep)
        
        self.connection.commit()
        cursor.close()
        
        print(f"✓ {len(dependencias)} dependências criadas\n")
    
    def seed_metricas(self):
        """Cria métricas históricas dos projetos"""
        print("📊 Criando métricas históricas...")
        
        hoje = datetime.now().date()
        
        metricas = []
        
        # Projeto 1 - últimos 30 dias
        for i in range(30):
            data = hoje - timedelta(days=29-i)
            progresso = 10 + (i * 0.85)  # Progresso gradual
            metricas.append((
                1, data, 
                int(i * 0.2), int(i * 0.05),  # tarefas concluídas e atrasadas
                round(progresso, 2), round(progresso * 0.9, 2),  # progresso físico e financeiro
                8.5 * (i+1), 15000.00 * (i+1)  # horas e valor gasto
            ))
        
        # Projeto 2 - últimos 20 dias
        for i in range(20):
            data = hoje - timedelta(days=19-i)
            progresso = 20 + (i * 1.25)
            metricas.append((
                2, data,
                int(i * 0.15), int(i * 0.03),
                round(progresso, 2), round(progresso * 0.95, 2),
                6.0 * (i+1), 12000.00 * (i+1)
            ))
        
        # Projeto 3 - últimos 40 dias
        for i in range(40):
            data = hoje - timedelta(days=39-i)
            progresso = 5 + (i * 0.45)
            metricas.append((
                3, data,
                int(i * 0.1), int(i * 0.02),
                round(progresso, 2), round(progresso * 0.85, 2),
                10.0 * (i+1), 25000.00 * (i+1)
            ))
        
        cursor = self.connection.cursor()
        
        for metrica in metricas:
            cursor.execute("""
                INSERT INTO metricas_projeto (
                    projeto_id, data_registro, tarefas_concluidas, tarefas_atrasadas,
                    progresso_fisico, progresso_financeiro, horas_trabalhadas, valor_gasto
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, metrica)
        
        self.connection.commit()
        cursor.close()
        
        print(f"✓ {len(metricas)} registros de métricas criados\n")
    
    def seed_notificacoes(self):
        """Cria notificações de exemplo"""
        print("🔔 Criando notificações...")
        
        hoje = datetime.now()
        
        notificacoes = [
            (1, 'tarefa', 'Nova tarefa atribuída', 'Você foi atribuído à tarefa: Estrutura 5º ao 8º pavimento', '/projetos/1/tarefas/4', False, hoje - timedelta(hours=3)),
            (3, 'mensagem', 'Nova mensagem em Discussão Geral', 'O caminhão betoneira está confirmado para 9h.', '/chats/1', False, hoje - timedelta(hours=7, minutes=30)),
            (2, 'documento', 'Novo documento adicionado', 'Documento "Orçamento Detalhado" foi adicionado', '/projetos/2/documentos/5', True, hoje - timedelta(days=1)),
            (5, 'projeto', 'Adicionado a um projeto', 'Você foi adicionado ao projeto: Reforma Shopping Center Norte como engenheiro', '/projetos/2', True, hoje - timedelta(days=28)),
            (4, 'tarefa', 'Tarefa atribuída a você', 'Você foi atribuído à tarefa: Instalações hidráulicas', '/projetos/1/tarefas/5', False, hoje - timedelta(hours=2)),
        ]
        
        cursor = self.connection.cursor()
        
        for notif in notificacoes:
            cursor.execute("""
                INSERT INTO notificacoes (usuario_id, tipo, titulo, mensagem, link, lida, criado_em)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, notif)
        
        self.connection.commit()
        cursor.close()
        
        print(f"✓ {len(notificacoes)} notificações criadas\n")
    
    def run(self, clear_first=False):
        """Executa todos os seeds"""
        if not self.connect():
            return False
        
        print("\n" + "="*60)
        print("POPULANDO BANCO DE DADOS - SEEDS")
        print("="*60 + "\n")
        
        try:
            if clear_first:
                self.clear_all_data()
            
            self.seed_usuarios()
            self.seed_permissoes()
            self.seed_projetos()
            self.seed_equipes()
            self.seed_tarefas()
            self.seed_materiais()
            self.seed_orcamentos()
            self.seed_documentos()
            self.seed_chats()
            self.seed_comentarios()
            self.seed_dependencias()
            self.seed_metricas()
            self.seed_notificacoes()
            
            print("="*60)
            print("✓ SEEDS EXECUTADOS COM SUCESSO!")
            print("="*60)
            print("\n📊 Dados de exemplo criados:")
            print("  • 5 usuários (senha padrão: senha123)")
            print("  • 6 permissões")
            print("  • 4 projetos")
            print("  • 10 membros de equipe")
            print("  • 11 tarefas")
            print("  • 6 dependências entre tarefas")
            print("  • 6 materiais")
            print("  • 7 itens de orçamento")
            print("  • 7 documentos")
            print("  • 3 chats com 9 mensagens")
            print("  • 6 comentários")
            print("  • 90 registros de métricas históricas")
            print("  • 5 notificações")
            print("\n💡 Use estes dados para testar o sistema!\n")
            
            return True
            
        except Error as e:
            print(f"\n✗ Erro ao executar seeds: {e}")
            return False
        finally:
            self.disconnect()


def main():
    """Função principal"""
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'gerenciador_projetos'),
        'port': int(os.getenv('DB_PORT', 3306))
    }
    
    seeder = Seeder(db_config)
    
    # Verifica se deve limpar dados antes
    clear_first = '--clear' in sys.argv or '-c' in sys.argv
    
    if clear_first:
        print("\n⚠️  ATENÇÃO: Todos os dados existentes serão removidos!")
        resposta = input("Deseja continuar? (s/N): ")
        if resposta.lower() != 's':
            print("Operação cancelada.")
            return
    
    seeder.run(clear_first=clear_first)


if __name__ == '__main__':
    main()
