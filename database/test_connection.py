#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para testar conexão com MySQL
Ajuda a diagnosticar problemas de conexão
"""

import os
import mysql.connector
from mysql.connector import Error

def test_connection():
    """Testa conexão com MySQL"""
    
    print("\n" + "="*60)
    print("  TESTE DE CONEXÃO COM MYSQL")
    print("="*60 + "\n")
    
    # Configurações
    configs_to_try = [
        {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'port': 3306
        },
        {
            'host': '127.0.0.1',
            'user': 'root',
            'password': '',
            'port': 3306
        },
        {
            'host': 'localhost',
            'user': 'root',
            'password': 'root',
            'port': 3306
        },
        {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'port': 3307
        }
    ]
    
    print("Tentando conectar com diferentes configurações...\n")
    
    for i, config in enumerate(configs_to_try, 1):
        print(f"Tentativa {i}:")
        print(f"  Host: {config['host']}")
        print(f"  Porta: {config['port']}")
        print(f"  Usuário: {config['user']}")
        print(f"  Senha: {'(vazia)' if config['password'] == '' else '***'}")
        
        try:
            connection = mysql.connector.connect(**config)
            
            if connection.is_connected():
                db_info = connection.get_server_info()
                print(f"  ✓ CONEXÃO BEM-SUCEDIDA!")
                print(f"  ✓ MySQL versão: {db_info}")
                
                cursor = connection.cursor()
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()
                print(f"  ✓ Versão do banco: {version[0]}")
                
                cursor.close()
                connection.close()
                
                print("\n" + "="*60)
                print("✓ MySQL está funcionando!")
                print("="*60)
                print("\nUse esta configuração no arquivo .env:")
                print(f"DB_HOST={config['host']}")
                print(f"DB_USER={config['user']}")
                print(f"DB_PASSWORD={config['password']}")
                print(f"DB_PORT={config['port']}")
                print(f"DB_NAME=gerenciador_projetos")
                
                return True
                
        except Error as e:
            if e.errno == 2003:
                print(f"  ✗ Erro: MySQL não está rodando na porta {config['port']}")
            elif e.errno == 1045:
                print(f"  ✗ Erro: Senha incorreta")
            else:
                print(f"  ✗ Erro: {e}")
        
        print()
    
    print("="*60)
    print("✗ Não foi possível conectar ao MySQL")
    print("="*60)
    print("\nVerifique:")
    print("1. O MySQL está instalado?")
    print("2. O serviço MySQL está rodando?")
    print("3. A senha do root está correta?")
    print("\nComo iniciar o MySQL:")
    print("- XAMPP: Abra o painel e clique em 'Start' no MySQL")
    print("- MySQL Server: Execute 'net start MySQL80' como admin")
    
    return False


if __name__ == '__main__':
    test_connection()
