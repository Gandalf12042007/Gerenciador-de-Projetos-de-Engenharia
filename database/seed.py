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
            
            print("="*60)
            print("✓ SEEDS EXECUTADOS COM SUCESSO!")
            print("="*60)
            print("\n📊 Dados de exemplo criados:")
            print("  • 5 usuários (senha padrão: senha123)")
            print("  • 6 permissões")
            print("  • 4 projetos")
            print("  • 10 membros de equipe")
            print("  • 11 tarefas")
            print("  • 6 materiais")
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
