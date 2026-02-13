"""
Script para popular banco SQLite com dados de teste
"""

import os
import sys
import sqlite3
from datetime import datetime, timedelta

def seed_sqlite():
    """Popula o banco SQLite com dados de teste"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'gerenciador.db')
    
    print("\n" + "="*60)
    print("POPULANDO BANCO DE DADOS SQLite COM DADOS DE TESTE")
    print("="*60 + "\n")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Limpar dados existentes (opcional - comentar se quiser manter)
        # cursor.execute("DELETE FROM usuarios")
        # cursor.execute("DELETE FROM projetos")
        # cursor.execute("DELETE FROM equipes")
        # cursor.execute("DELETE FROM tarefas")
        # conn.commit()
        
        # Inserir usuários
        print("📝 Inserindo usuários...")
        usuarios = [
            ("Vicente de Souza", "vicente@test.com", "hashed_senha_123", "engenheiro"),
            ("Maria Silva", "maria@test.com", "hashed_senha_456", "gerente"),
            ("João Santos", "joao@test.com", "hashed_senha_789", "técnico"),
            ("Ana Costa", "ana@test.com", "hashed_senha_abc", "arquiteto"),
        ]
        
        for nome, email, senha, cargo in usuarios:
            try:
                cursor.execute(
                    "INSERT INTO usuarios (nome, email, senha_hash, cargo, ativo) VALUES (?, ?, ?, ?, 1)",
                    (nome, email, senha, cargo)
                )
                print(f"   ✓ {nome}")
            except sqlite3.IntegrityError:
                print(f"   ⚠ {nome} já existe")
        
        conn.commit()
        
        # Inserir projetos
        print("\n📝 Inserindo projetos...")
        projetos = [
            ("Prédio Comercial Centro", "Construção de prédio comercial", "Av. Principal, 100", "Cliente A", 1000000.00, "2025-01-01", "2026-06-30", 1),
            ("Residência Bairro Sul", "Casa residencial moderna", "Rua das Flores, 50", "Cliente B", 500000.00, "2025-02-15", "2025-12-31", 1),
            ("Obra Reforma", "Reforma completa de estrutura", "Av. Secundária, 200", "Cliente C", 300000.00, "2025-03-01", "2025-09-30", 1),
        ]
        
        projeto_ids = []
        for nome, desc, endereco, cliente, valor, inicio, fim, criador_id in projetos:
            try:
                cursor.execute(
                    "INSERT INTO projetos (nome, descricao, endereco, cliente, valor_total, data_inicio, data_fim_prevista, status, progresso_percentual, criador_id) VALUES (?, ?, ?, ?, ?, ?, ?, 'em_andamento', 45, ?)",
                    (nome, desc, endereco, cliente, valor, inicio, fim, criador_id)
                )
                projeto_ids.append(cursor.lastrowid)
                print(f"   ✓ {nome} (ID: {cursor.lastrowid})")
            except sqlite3.IntegrityError:
                print(f"   ⚠ {nome} já existe")
        
        conn.commit()
        
        # Inserir equipes
        print("\n📝 Inserindo equipes...")
        if projeto_ids:
            for projeto_id in projeto_ids[:2]:  # Para os primeiros 2 projetos
                equipes = [
                    (projeto_id, 1, "gerente"),
                    (projeto_id, 2, "engenheiro"),
                    (projeto_id, 3, "tecnico"),
                ]
                
                for proj_id, user_id, papel in equipes:
                    try:
                        cursor.execute(
                            "INSERT INTO equipes (projeto_id, usuario_id, papel, data_entrada, ativo) VALUES (?, ?, ?, date('now'), 1)",
                            (proj_id, user_id, papel)
                        )
                        print(f"   ✓ Projeto {proj_id} - Usuário {user_id} ({papel})")
                    except sqlite3.IntegrityError:
                        print(f"   ⚠ Equipe já existe")
            
            conn.commit()
        
        # Inserir tarefas
        print("\n📝 Inserindo tarefas...")
        if projeto_ids:
            for projeto_id in projeto_ids[:2]:
                tarefas = [
                    (projeto_id, "Escavação e fundação", "Escavar e preparar fundações", 1, "alta", "em_andamento", "2025-03-15", 1),
                    (projeto_id, "Estrutura de aço", "Montar estrutura principal", 2, "alta", "a_fazer", "2025-05-15", 1),
                    (projeto_id, "Alvenaria", "Construir paredes e vedações", 3, "media", "a_fazer", "2025-07-15", 1),
                    (projeto_id, "Acabamentos", "Pintura, piso e acabamentos", 1, "media", "a_fazer", "2025-09-15", 1),
                ]
                
                for proj_id, titulo, desc, responsavel, prioridade, status, data_fim, criador in tarefas:
                    try:
                        cursor.execute(
                            """INSERT INTO tarefas 
                            (projeto_id, titulo, descricao, responsavel_id, prioridade, status, data_fim_prevista, criador_id)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                            (proj_id, titulo, desc, responsavel, prioridade, status, data_fim, criador)
                        )
                        print(f"   ✓ {titulo}")
                    except sqlite3.IntegrityError as e:
                        print(f"   ⚠ Tarefa não inserida")
            
            conn.commit()
        
        # Contar registros
        print("\n📊 Resumo de dados:")
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        print(f"   • Usuários: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM projetos")
        print(f"   • Projetos: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM equipes")
        print(f"   • Equipes: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM tarefas")
        print(f"   • Tarefas: {cursor.fetchone()[0]}")
        
        conn.close()
        print("\n✅ Banco populado com sucesso!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao popular banco: {e}\n")
        return False


if __name__ == '__main__':
    seed_sqlite()
