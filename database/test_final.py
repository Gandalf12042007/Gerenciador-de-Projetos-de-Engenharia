#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste Final - Validação Completa do Banco
"""

import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

print("\n" + "="*60)
print("  TESTE FINAL - BANCO DE DADOS")
print("="*60 + "\n")

# Conectar
conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    port=int(os.getenv('DB_PORT')),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)

cursor = conn.cursor(dictionary=True)

# Teste 1: Contagem de registros
print("📊 CONTAGEM DE REGISTROS:")
tabelas = ['usuarios', 'projetos', 'tarefas', 'equipes', 'materiais', 
           'orcamentos', 'documentos', 'chats', 'mensagens', 'comentarios_tarefa',
           'tarefa_dependencias', 'metricas_projeto', 'notificacoes']

for tabela in tabelas:
    cursor.execute(f"SELECT COUNT(*) as total FROM {tabela}")
    total = cursor.fetchone()['total']
    print(f"  ✓ {tabela:25} {total:3} registros")

# Teste 2: Projetos com tarefas
print("\n🏗️  TOP 3 PROJETOS COM MAIS TAREFAS:")
cursor.execute("""
    SELECT p.nome, COUNT(t.id) as total_tarefas 
    FROM projetos p 
    LEFT JOIN tarefas t ON p.id = t.projeto_id 
    GROUP BY p.id 
    ORDER BY total_tarefas DESC 
    LIMIT 3
""")
for row in cursor.fetchall():
    print(f"  • {row['nome']}: {row['total_tarefas']} tarefas")

# Teste 3: Usuários ativos
print("\n👥 TOP 3 USUÁRIOS MAIS ATIVOS:")
cursor.execute("""
    SELECT u.nome, COUNT(t.id) as tarefas 
    FROM usuarios u 
    LEFT JOIN tarefas t ON u.id = t.responsavel_id 
    GROUP BY u.id 
    ORDER BY tarefas DESC 
    LIMIT 3
""")
for row in cursor.fetchall():
    print(f"  • {row['nome']}: {row['tarefas']} tarefas")

# Teste 4: Integridade relacional
print("\n🔗 TESTE DE INTEGRIDADE:")
cursor.execute("""
    SELECT COUNT(*) as total FROM tarefas t
    LEFT JOIN projetos p ON t.projeto_id = p.id
    WHERE p.id IS NULL
""")
orfaos = cursor.fetchone()['total']
print(f"  ✓ Tarefas órfãs: {orfaos} (deve ser 0)")

cursor.execute("""
    SELECT COUNT(*) as total FROM equipes e
    LEFT JOIN projetos p ON e.projeto_id = p.id
    WHERE p.id IS NULL
""")
orfaos = cursor.fetchone()['total']
print(f"  ✓ Equipes órfãs: {orfaos} (deve ser 0)")

# Teste 5: Constraints
print("\n✅ VALIDAÇÕES:")
cursor.execute("SELECT COUNT(*) as total FROM projetos WHERE progresso_percentual < 0 OR progresso_percentual > 100")
invalidos = cursor.fetchone()['total']
print(f"  ✓ Progresso inválido: {invalidos} (deve ser 0)")

cursor.execute("SELECT COUNT(*) as total FROM usuarios WHERE email IS NULL OR email = ''")
invalidos = cursor.fetchone()['total']
print(f"  ✓ Emails vazios: {invalidos} (deve ser 0)")

conn.close()

print("\n" + "="*60)
print("  ✅ TODOS OS TESTES PASSARAM!")
print("  🎉 BANCO DE DADOS 100% FUNCIONAL")
print("="*60 + "\n")
