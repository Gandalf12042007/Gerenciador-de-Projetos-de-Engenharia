"""
Script de Validacao das Correcoes (Windows-friendly)
Desenvolvido por: Sistema de correcoes automaticas
Data: 2026-02-13
"""

import os
import sys

def check_file_exists(filepath, description):
    """Verifica se arquivo existe"""
    if os.path.exists(filepath):
        print(f"[OK] {description}")
        return True
    else:
        print(f"[ERRO] {description}: FALTANDO")
        return False

def check_import_fixed(filepath, old_import, new_import):
    """Verifica se import foi corrigido"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if old_import in content:
                print(f"[ERRO] Import ainda incorreto em {os.path.basename(filepath)}")
                return False
            elif new_import in content:
                print(f"[OK] Import corrigido em {os.path.basename(filepath)}")
                return True
            else:
                print(f"[INFO] Import nao encontrado em {os.path.basename(filepath)}")
                return True
    except Exception as e:
        print(f"[ERRO] Erro ao verificar {filepath}: {e}")
        return False

def check_duplicated_code(filepath, duplicate_pattern):
    """Verifica se codigo duplicado foi removido"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            count = content.count(duplicate_pattern)
            if count > 1:
                print(f"[ERRO] Codigo duplicado ainda existe em {os.path.basename(filepath)} ({count}x)")
                return False
            else:
                print(f"[OK] Codigo duplicado removido em {os.path.basename(filepath)}")
                return True
    except Exception as e:
        print(f"[ERRO] Erro ao verificar {filepath}: {e}")
        return False

def check_placeholder_standardized(filepath):
    """Verifica se placeholders SQL foram padronizados"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Conta placeholders ? em queries SQL
            lines = content.split('\n')
            sql_question_marks = 0
            for line in lines:
                if 'SELECT' in line or 'INSERT' in line or 'UPDATE' in line or 'DELETE' in line or 'WHERE' in line:
                    sql_question_marks += line.count(' ?')
            
            if sql_question_marks > 0:
                print(f"[ERRO] Ainda ha {sql_question_marks} placeholders '?' em {os.path.basename(filepath)}")
                return False
            else:
                print(f"[OK] Placeholders padronizados em {os.path.basename(filepath)}")
                return True
    except Exception as e:
        print(f"[ERRO] Erro ao verificar {filepath}: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("VALIDACAO DAS CORRECOES - GERENCIADOR DE PROJETOS")
    print("="*60 + "\n")
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    backend_path = os.path.join(base_path, 'backend')
    database_path = os.path.join(base_path, 'database')
    
    results = []
    
    # 1. Verificar arquivos de migration criados
    print("\n[1] MIGRATIONS CRIADAS")
    results.append(check_file_exists(
        os.path.join(database_path, 'migrations', '004_tokens_reset_senha.sql'),
        "Migration 004 - tokens_reset_senha"
    ))
    results.append(check_file_exists(
        os.path.join(database_path, 'migrations', '005_modulo_financeiro.sql'),
        "Migration 005 - modulo_financeiro"
    ))
    
    # 2. Verificar imports corrigidos em tarefas.py
    print("\n[2] IMPORTS CORRIGIDOS")
    tarefas_path = os.path.join(backend_path, 'routes', 'tarefas.py')
    results.append(check_import_fixed(
        tarefas_path,
        'from backend.utils.audit import registrar_auditoria',
        'from utils.audit import registrar_auditoria'
    ))
    
    # 3. Verificar codigo duplicado removido
    print("\n[3] CODIGO DUPLICADO REMOVIDO")
    results.append(check_duplicated_code(
        tarefas_path,
        'db.execute_query("DELETE FROM tarefas WHERE id = %s", (tarefa_id,))'
    ))
    
    # 4. Verificar is_admin no token JWT
    print("\n[4] TOKEN JWT COM is_admin")
    auth_path = os.path.join(backend_path, 'routes', 'auth.py')
    try:
        with open(auth_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if '"is_admin": True' in content or "'is_admin': True" in content or '"is_admin": is_admin' in content:
                print("[OK] is_admin adicionado ao token JWT")
                results.append(True)
            else:
                print("[ERRO] is_admin nao encontrado no token JWT")
                results.append(False)
    except Exception as e:
        print(f"[ERRO] Erro ao verificar auth.py: {e}")
        results.append(False)
    
    # 5. Verificar placeholders padronizados
    print("\n[5] PLACEHOLDERS SQL PADRONIZADOS")
    results.append(check_placeholder_standardized(
        os.path.join(backend_path, 'routes', 'chat.py')
    ))
    results.append(check_placeholder_standardized(
        os.path.join(backend_path, 'routes', 'equipes.py')
    ))
    
    # Resumo final
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100
    
    if percentage == 100:
        print("RESULTADO: TODAS AS CORRECOES APLICADAS COM SUCESSO!")
    elif percentage >= 80:
        print(f"RESULTADO: MAIORIA DAS CORRECOES APLICADAS ({passed}/{total})")
    else:
        print(f"RESULTADO: ALGUMAS CORRECOES FALHARAM ({passed}/{total})")
    
    print(f"\nVerificacoes passaram: {passed}/{total} ({percentage:.1f}%)")
    print("="*60 + "\n")
    
    return 0 if percentage == 100 else 1

if __name__ == "__main__":
    sys.exit(main())
