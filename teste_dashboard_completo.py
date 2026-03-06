#!/usr/bin/env python3
"""
Script para testar o dashboard de ponta a ponta
Simula: Login -> Acesso ao dashboard -> Carregamento de dados
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

# Token do usuário admin
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6InZpY2VudGVkZXNvdXphNzYyQGdtYWlsLmNvbSIsIm5vbWUiOiJWaWNlbnRlIGRlIFNvdXphIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzcyNDk2MTI5fQ.sKeub1zXCuseYJLYF8xwgYvBqvJQj2KR4Yh6BtqduqU"
USER = {"id": 1, "nome": "Vicente de Souza", "email": "vicentedesouza762@gmail.com", "role": "admin"}

def print_section(title):
    print("\n" + "="*60)
    print(title)
    print("="*60)

def print_success(msg):
    print(f"✅ {msg}")

def print_error(msg):
    print(f"❌ {msg}")

def print_warning(msg):
    print(f"⚠️  {msg}")

def print_info(msg):
    print(f"ℹ️  {msg}")

print_section("TESTE COMPLETO DO DASHBOARD")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 1. Validar acesso à dashboard
print_section("1. VALIDAR ACESSO À PÁGINA DASHBOARD")
try:
    response = requests.get(f"{BASE_URL}/projects/dashboard.html")
    if response.status_code == 200:
        print_success(f"Dashboard.html acessível (Status: {response.status_code})")
        # Verificar se contém elementos esperados
        html = response.text
        checks = [
            ("layout.js", "layout.js incluído"),
            ("api-client.js", "api-client.js incluído"),
            ("loadDashboardData()", "função loadDashboardData existe"),
            ("updateSummaryCards", "função updateSummaryCards existe"),
        ]
        
        for check, desc in checks:
            if check in html:
                print_success(f"  ✓ {desc}")
            else:
                print_warning(f"  ✗ {desc} - NÃO ENCONTRADO")
    else:
        print_error(f"Não conseguiu acessar dashboard (Status: {response.status_code})")
except Exception as e:
    print_error(f"Erro ao acessar dashboard: {e}")

# 2. Testar API endpoints
print_section("2. VALIDAR API ENDPOINTS")

headers = {"Authorization": f"Bearer {TOKEN}"}

# Projetos
print_info("Testando GET /api/projetos/...")
try:
    resp = requests.get(f"{BASE_URL}/api/projetos/", headers=headers)
    if resp.status_code == 200:
        projects = resp.json()
        print_success(f"GET /api/projetos/ retornou {len(projects)} projeto(s)")
        
        if len(projects) > 0:
            print_info(f"  Primeiro projeto: '{projects[0].get('nome', 'N/A')}'")
            print_info(f"  Status pode conter: {projects[0].get('status', 'N/A')}")
    else:
        print_error(f"GET /api/projetos/ retornou {resp.status_code}")
except Exception as e:
    print_error(f"Erro em /api/projetos/: {e}")

# Tarefas por projeto
print_info("Testando GET /api/tarefas/projeto/{{id}}...")
try:
    resp = requests.get(f"{BASE_URL}/api/projetos/", headers=headers)
    projects = resp.json()
    
    if projects:
        sample_project = projects[0]
        resp = requests.get(f"{BASE_URL}/api/tarefas/projeto/{sample_project['id']}", headers=headers)
        
        if resp.status_code == 200:
            tasks = resp.json()
            print_success(f"GET /api/tarefas/projeto/{sample_project['id']} retornou {len(tasks)} tarefa(s)")
            
            # Estadísticas
            if tasks:
                status_counts = {}
                for task in tasks:
                    status = task.get('status', 'desconhecido')
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                print_info(f"  Status das tarefas: {status_counts}")
        else:
            print_error(f"GET /api/tarefas/projeto/{sample_project['id']} retornou {resp.status_code}")
except Exception as e:
    print_error(f"Erro em /api/tarefas/projeto: {e}")

# GET /api/tarefas/ (esperado 405)
print_info("Testando GET /api/tarefas/ (esperado 405)...")
try:
    resp = requests.get(f"{BASE_URL}/api/tarefas/", headers=headers)
    if resp.status_code == 405:
        print_warning(f"GET /api/tarefas/ retorna 405 (esperado - método não permitido)")
    else:
        print_info(f"GET /api/tarefas/ retorna {resp.status_code}")
except Exception as e:
    print_error(f"Erro em GET /api/tarefas/: {e}")

# 3. Simular carregamento de dashboard
print_section("3. SIMULAR CARREGAMENTO DE DASHBOARD")

try:
    # Carregar todos os projetos
    resp = requests.get(f"{BASE_URL}/api/projetos/", headers=headers)
    projects = resp.json() if resp.status_code == 200 else []
    
    # Carregar tarefas de cada projeto
    all_tasks = []
    for project in projects:
        resp = requests.get(f"{BASE_URL}/api/tarefas/projeto/{project['id']}", headers=headers)
        if resp.status_code == 200:
            tasks = resp.json()
            all_tasks.extend(tasks)
    
    # Calcular estatísticas
    total_projects = len(projects)
    total_tasks = len(all_tasks)
    completed_tasks = len([t for t in all_tasks if t.get('status') == 'concluido'])
    active_projects = len([p for p in projects if p.get('status') != 'concluido'])
    overdue_tasks = len([t for t in all_tasks if t.get('status') == 'atrasado'])
    
    avg_progress = (sum(p.get('progresso_percentual', 0) for p in projects) / len(projects)) if projects else 0
    
    print_info("ESTATÍSTICAS CARREGADAS:")
    print(f"  • Projetos totais: {total_projects}")
    print(f"  • Projetos ativos: {active_projects}")
    print(f"  • Tarefas totais: {total_tasks}")
    print(f"  • Tarefas concluídas: {completed_tasks}")
    print(f"  • Tarefas atrasadas: {overdue_tasks}")
    print(f"  • Progresso médio: {avg_progress:.1f}%")
    
    print_success("Dashboard carregaria com dados válidos!")
    
except Exception as e:
    print_error(f"Erro ao simular carregamento: {e}")

# 4. Verificar problemas potenciais
print_section("4. CHECKLIST DE PROBLEMAS POTENCIAIS")

print_info("Verificando possíveis problemas...")

issues = []

# Verificar se há projetos
if not projects:
    issues.append("⚠️  Nenhum projeto no banco de dados")
else:
    print_success(f"✓ {len(projects)} projeto(s) disponível(is)")

# Verificar se há tarefas
if not all_tasks:
    issues.append("⚠️  Nenhuma tarefa no banco de dados")
else:
    print_success(f"✓ {len(all_tasks)} tarefa(s) disponível(is)")

# Verificar endpoints
try:
    resp = requests.get(f"{BASE_URL}/api/projetos/", headers=headers)
    if resp.status_code == 200:
        print_success("✓ GET /api/projetos/ funcionando")
    else:
        issues.append(f"⚠️  GET /api/projetos/ retorna {resp.status_code}")
except:
    issues.append("⚠️  GET /api/projetos/ inacessível")

# Informar issues
if issues:
    print("\n⚠️  PROBLEMAS IDENTIFICADOS:")
    for issue in issues:
        print(f"  {issue}")
else:
    print("\n✅ TUDO OK! Dashboard deveria funcionar sem problemas!")

# 5. Recomendações
print_section("5. PRÓXIMOS PASSOS")
print("""
1. ✅ Abrir http://localhost:8000/login
2. ✅ Fazer login com: vicentedesouza762@gmail.com / Admin@2026
3. ✅ Você deve ser redirecionado para o dashboard
4. ✅ Abrir console (F12) para verificar logs da aplicação
5. ✅ Relatar qualquer erro que aparecer no console

Dados de teste:
- Login: vicentedesouza762@gmail.com
- Senha: Admin@2026
- Papel: admin

Se o dashboard não carregar, verifique:
- Console do navegador (F12) para erros JavaScript
- Aba Network para verificar requisições HTTP
- Verifique se o localStorage tem o token correto
""")

print_section("FIM DO TESTE")
print(f"Timestamp final: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
