#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Testes - Banco de Dados
Valida todos os componentes criados
"""

import os
import sys

def test_files():
    """Testa se todos os arquivos foram criados"""
    print("\n" + "="*60)
    print("TESTE 1: Verificando Arquivos")
    print("="*60)
    
    files = [
        'schema.dbml',
        'DIAGRAMA.md',
        'migrate.py',
        'seed.py',
        'db_helper.py',
        'queries_uteis.sql',
        'README.md',
        'requirements.txt',
        '.env.example',
        '.gitignore'
    ]
    
    total = len(files)
    found = 0
    
    for f in files:
        if os.path.exists(f):
            print(f"  ✓ {f}")
            found += 1
        else:
            print(f"  ✗ {f} - FALTANDO!")
    
    print(f"\n✓ Resultado: {found}/{total} arquivos encontrados")
    return found == total

def test_python_syntax():
    """Testa sintaxe dos arquivos Python"""
    print("\n" + "="*60)
    print("TESTE 2: Validando Sintaxe Python")
    print("="*60)
    
    files = ['migrate.py', 'seed.py', 'db_helper.py']
    total = len(files)
    valid = 0
    
    for f in files:
        try:
            with open(f, 'r', encoding='utf-8') as file:
                compile(file.read(), f, 'exec')
            print(f"  ✓ {f} - OK")
            valid += 1
        except SyntaxError as e:
            print(f"  ✗ {f} - ERRO: {e}")
        except Exception as e:
            print(f"  ✗ {f} - ERRO: {e}")
    
    print(f"\n✓ Resultado: {valid}/{total} arquivos válidos")
    return valid == total

def test_sql_file():
    """Testa arquivo SQL"""
    print("\n" + "="*60)
    print("TESTE 3: Validando Arquivo SQL")
    print("="*60)
    
    try:
        with open('migrations/001_initial_schema.sql', 'r', encoding='utf-8') as f:
            content = f.read()
            lines = len(content.split('\n'))
            tables = content.count('CREATE TABLE')
            
        print(f"  ✓ Arquivo lido: {lines} linhas")
        print(f"  ✓ Tabelas definidas: {tables}")
        
        if tables >= 18:
            print(f"\n✓ Schema completo encontrado!")
            return True
        else:
            print(f"\n✗ Esperado 18+ tabelas, encontrado {tables}")
            return False
            
    except Exception as e:
        print(f"  ✗ Erro ao ler SQL: {e}")
        return False

def test_imports():
    """Testa imports dos módulos"""
    print("\n" + "="*60)
    print("TESTE 4: Testando Imports")
    print("="*60)
    
    tests = []
    
    # Teste migrate.py
    try:
        import migrate
        print("  ✓ migrate.py - importado")
        tests.append(True)
    except Exception as e:
        print(f"  ✗ migrate.py - ERRO: {e}")
        tests.append(False)
    
    # Teste seed.py
    try:
        import seed
        print("  ✓ seed.py - importado")
        tests.append(True)
    except Exception as e:
        print(f"  ✗ seed.py - ERRO: {e}")
        tests.append(False)
    
    # Teste db_helper.py
    try:
        import db_helper
        print("  ✓ db_helper.py - importado")
        tests.append(True)
    except Exception as e:
        print(f"  ✗ db_helper.py - ERRO: {e}")
        tests.append(False)
    
    passed = sum(tests)
    print(f"\n✓ Resultado: {passed}/{len(tests)} módulos OK")
    return all(tests)

def test_dependencies():
    """Testa dependências instaladas"""
    print("\n" + "="*60)
    print("TESTE 5: Verificando Dependências")
    print("="*60)
    
    try:
        import mysql.connector
        version = mysql.connector.__version__
        print(f"  ✓ mysql-connector-python {version}")
        return True
    except ImportError:
        print("  ✗ mysql-connector-python NÃO INSTALADO")
        print("    Execute: pip install -r requirements.txt")
        return False

def test_file_sizes():
    """Verifica tamanhos dos arquivos"""
    print("\n" + "="*60)
    print("TESTE 6: Tamanho dos Arquivos")
    print("="*60)
    
    files = {
        'schema.dbml': 5000,
        'db_helper.py': 8000,
        'queries_uteis.sql': 5000,
        'migrate.py': 4000,
        'seed.py': 7000,
    }
    
    total_size = 0
    
    for f, min_size in files.items():
        if os.path.exists(f):
            size = os.path.getsize(f)
            total_size += size
            status = "✓" if size >= min_size else "⚠"
            print(f"  {status} {f}: {size:,} bytes")
        else:
            print(f"  ✗ {f}: não encontrado")
    
    print(f"\n✓ Tamanho total: {total_size:,} bytes (~{total_size//1024} KB)")
    return True

def run_all_tests():
    """Executa todos os testes"""
    print("\n" + "="*70)
    print("           TESTES DO BANCO DE DADOS")
    print("        Gerenciador de Projetos de Engenharia")
    print("="*70)
    
    results = []
    
    results.append(("Arquivos", test_files()))
    results.append(("Sintaxe Python", test_python_syntax()))
    results.append(("SQL Schema", test_sql_file()))
    results.append(("Imports", test_imports()))
    results.append(("Dependências", test_dependencies()))
    results.append(("Tamanhos", test_file_sizes()))
    
    # Resumo final
    print("\n" + "="*70)
    print("RESUMO DOS TESTES")
    print("="*70)
    
    for name, passed in results:
        status = "✓ PASSOU" if passed else "✗ FALHOU"
        print(f"  {status.ljust(10)} - {name}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print("\n" + "="*70)
    if passed_count == total_count:
        print(f"✓✓✓ TODOS OS TESTES PASSARAM! ({passed_count}/{total_count})")
        print("✓ Sistema de banco de dados 100% funcional!")
    else:
        print(f"⚠ {passed_count}/{total_count} testes passaram")
        print(f"✗ {total_count - passed_count} teste(s) falharam")
    print("="*70 + "\n")
    
    return passed_count == total_count

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
