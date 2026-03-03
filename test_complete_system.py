#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 TESTE COMPLETO DO SISTEMA - Diagnóstico Fase 5
Verifica todas as conexões: Backend, BD, APIs, Frontend
"""

import requests
import json
import sys
from datetime import datetime

class SystemTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "errors": [],
            "summary": {}
        }
        self.passed = 0
        self.failed = 0

    def log(self, level, message):
        """Log com cores"""
        colors = {
            "✅": "\033[92m",
            "❌": "\033[91m",
            "⚠️": "\033[93m",
            "ℹ️": "\033[94m",
            "🔍": "\033[95m"
        }
        reset = "\033[0m"
        
        if level in colors:
            print(f"{level} {colors[level]}{message}{reset}")
        else:
            print(f"{level} {message}")

    def test_backend_connection(self):
        """Teste 1: Conexão com backend"""
        self.log("🔍", "Testando conexão com backend...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.log("✅", f"Backend respondendo: {response.json()}")
                self.passed += 1
                self.results["tests"].append({"name": "Backend Connection", "status": "PASS", "data": response.json()})
                return True
            else:
                self.log("❌", f"Backend retornou código {response.status_code}")
                self.failed += 1
                self.results["tests"].append({"name": "Backend Connection", "status": "FAIL", "code": response.status_code})
                return False
        except Exception as e:
            self.log("❌", f"Erro ao conectar com backend: {str(e)}")
            self.results["errors"].append({"test": "Backend Connection", "error": str(e)})
            self.failed += 1
            return False

    def test_database_connection(self):
        """Teste 2: Conexão com banco de dados"""
        self.log("🔍", "Testando conexão com banco de dados...")
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={"email": "test@test.com", "password": "test"},
                timeout=5
            )
            # Mesmo que falhe login, a resposta mostra que BD está acessível
            if response.status_code in [200, 401, 422]:
                self.log("✅", f"Banco de dados acessível (Status: {response.status_code})")
                self.passed += 1
                self.results["tests"].append({"name": "Database Connection", "status": "PASS", "code": response.status_code})
                return True
            else:
                self.log("❌", f"Banco de dados não respondeu corretamente")
                self.failed += 1
                self.results["tests"].append({"name": "Database Connection", "status": "FAIL"})
                return False
        except Exception as e:
            self.log("🔍", f"Teste de BD com erro: {str(e)}")
            self.results["errors"].append({"test": "Database Connection", "error": str(e)})
            self.failed += 1
            return False

    def test_auth_endpoints(self):
        """Teste 3: Endpoints de autenticação"""
        self.log("🔍", "Testando endpoints de autenticação...")
        
        endpoints = [
            ("POST", "/api/auth/login", {"email": "test@test.com", "password": "test"}),
            ("POST", "/api/auth/register", {"email": "test@test.com", "password": "test", "name": "Test"}),
            ("POST", "/api/auth/verify", None),
        ]
        
        for method, endpoint, data in endpoints:
            try:
                if method == "POST":
                    response = requests.post(f"{self.base_url}{endpoint}", json=data, timeout=5)
                else:
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                
                status = "PASS" if response.status_code < 500 else "FAIL"
                if status == "PASS":
                    self.log("✅", f"{endpoint}: {response.status_code}")
                    self.passed += 1
                else:
                    self.log("❌", f"{endpoint}: {response.status_code}")
                    self.failed += 1
                
                self.results["tests"].append({
                    "name": f"Auth Endpoint: {endpoint}",
                    "status": status,
                    "code": response.status_code
                })
            except Exception as e:
                self.log("❌", f"{endpoint}: {str(e)}")
                self.failed += 1
                self.results["errors"].append({"endpoint": endpoint, "error": str(e)})

    def test_project_endpoints(self):
        """Teste 4: Endpoints de projetos"""
        self.log("🔍", "Testando endpoints de projetos...")
        
        headers = {"Authorization": "Bearer test-token"}
        endpoints = [
            ("GET", "/api/projects"),
            ("GET", "/api/projects/1"),
        ]
        
        for method, endpoint in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", headers=headers, timeout=5)
                
                # 401 é esperado sem token válido
                status = "PASS" if response.status_code < 500 else "FAIL"
                if status == "PASS":
                    self.log("✅", f"{endpoint}: {response.status_code}")
                    self.passed += 1
                else:
                    self.log("❌", f"{endpoint}: {response.status_code}")
                    self.failed += 1
                
                self.results["tests"].append({
                    "name": f"Project Endpoint: {endpoint}",
                    "status": status,
                    "code": response.status_code
                })
            except Exception as e:
                self.log("❌", f"{endpoint}: {str(e)}")
                self.failed += 1
                self.results["errors"].append({"endpoint": endpoint, "error": str(e)})

    def test_cors_headers(self):
        """Teste 5: Headers CORS"""
        self.log("🔍", "Testando CORS headers...")
        try:
            response = requests.options(
                f"{self.base_url}/api/projects",
                headers={"Origin": "http://localhost:3000"},
                timeout=5
            )
            
            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
            }
            
            if cors_headers["Access-Control-Allow-Origin"]:
                self.log("✅", f"CORS configurado: {cors_headers}")
                self.passed += 1
                self.results["tests"].append({"name": "CORS Headers", "status": "PASS", "headers": cors_headers})
                return True
            else:
                self.log("⚠️", "CORS não detectado ou não configurado")
                self.failed += 1
                self.results["tests"].append({"name": "CORS Headers", "status": "WARN"})
                return False
        except Exception as e:
            self.log("❌", f"Erro ao testar CORS: {str(e)}")
            self.failed += 1
            self.results["errors"].append({"test": "CORS", "error": str(e)})
            return False

    def test_frontend_files(self):
        """Teste 6: Arquivos do frontend"""
        self.log("🔍", "Testando arquivos do frontend...")
        
        files = [
            "/login.html",
            "/manifest.json",
            "/service-worker.js",
            "/pwa-installer.js",
            "/projects/index.html",
        ]
        
        for file_path in files:
            try:
                response = requests.get(f"{self.base_url}{file_path}", timeout=5)
                if response.status_code == 200:
                    self.log("✅", f"{file_path}: OK")
                    self.passed += 1
                    self.results["tests"].append({"name": f"Frontend File: {file_path}", "status": "PASS"})
                else:
                    self.log("⚠️", f"{file_path}: {response.status_code}")
                    self.failed += 1
                    self.results["tests"].append({"name": f"Frontend File: {file_path}", "status": "WARN", "code": response.status_code})
            except Exception as e:
                self.log("❌", f"{file_path}: {str(e)}")
                self.failed += 1
                self.results["errors"].append({"file": file_path, "error": str(e)})

    def test_api_documentation(self):
        """Teste 7: Documentação da API"""
        self.log("🔍", "Testando documentação da API...")
        
        docs_endpoints = [
            "/docs",
            "/redoc",
            "/openapi.json",
        ]
        
        for endpoint in docs_endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    self.log("✅", f"{endpoint}: OK")
                    self.passed += 1
                    self.results["tests"].append({"name": f"API Docs: {endpoint}", "status": "PASS"})
                else:
                    self.log("⚠️", f"{endpoint}: {response.status_code}")
                    self.failed += 1
                    self.results["tests"].append({"name": f"API Docs: {endpoint}", "status": "WARN"})
            except Exception as e:
                self.log("❌", f"{endpoint}: {str(e)}")
                self.failed += 1

    def test_response_times(self):
        """Teste 8: Tempos de resposta"""
        self.log("🔍", "Testando tempos de resposta...")
        
        import time
        endpoints = [
            "/health",
            "/api/projects",
            "/login.html",
        ]
        
        times = {}
        for endpoint in endpoints:
            try:
                start = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                elapsed = (time.time() - start) * 1000  # em ms
                times[endpoint] = elapsed
                
                if elapsed < 1000:
                    self.log("✅", f"{endpoint}: {elapsed:.0f}ms")
                    self.passed += 1
                else:
                    self.log("⚠️", f"{endpoint}: {elapsed:.0f}ms (lento)")
                    self.failed += 1
                
                self.results["tests"].append({
                    "name": f"Response Time: {endpoint}",
                    "status": "PASS" if elapsed < 1000 else "WARN",
                    "time_ms": elapsed
                })
            except Exception as e:
                self.log("❌", f"{endpoint}: {str(e)}")
                self.failed += 1

    def run_all_tests(self):
        """Executar todos os testes"""
        print("\n" + "="*70)
        print("🧪 TESTE COMPLETO DO SISTEMA - FASE 5")
        print("="*70 + "\n")
        
        self.test_backend_connection()
        self.test_database_connection()
        self.test_auth_endpoints()
        self.test_project_endpoints()
        self.test_cors_headers()
        self.test_frontend_files()
        self.test_api_documentation()
        self.test_response_times()
        
        self.print_summary()

    def print_summary(self):
        """Exibir resumo dos testes"""
        print("\n" + "="*70)
        print("📊 RESUMO DOS TESTES")
        print("="*70)
        
        self.log("✅", f"Testes Passaram: {self.passed}")
        self.log("❌", f"Testes Falharam: {self.failed}")
        
        total = self.passed + self.failed
        percentage = (self.passed / total * 100) if total > 0 else 0
        
        if percentage == 100:
            self.log("🎉", f"Taxa de sucesso: {percentage:.0f}% - TUDO PERFEITO!")
        elif percentage >= 80:
            self.log("⚠️", f"Taxa de sucesso: {percentage:.0f}% - Bom, mas com problemas")
        else:
            self.log("❌", f"Taxa de sucesso: {percentage:.0f}% - Crítico")
        
        if self.results["errors"]:
            print("\n" + "="*70)
            print("🔴 ERROS ENCONTRADOS:")
            print("="*70)
            for error in self.results["errors"]:
                self.log("❌", json.dumps(error, indent=2, ensure_ascii=False))
        
        print("\n" + "="*70)
        print("💾 RELATÓRIO SALVO: test_report.json")
        print("="*70 + "\n")
        
        # Salvar relatório
        with open("test_report.json", "w", encoding="utf-8") as f:
            self.results["summary"] = {
                "passed": self.passed,
                "failed": self.failed,
                "total": self.passed + self.failed,
                "success_rate": f"{percentage:.1f}%"
            }
            json.dump(self.results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    tester = SystemTester()
    tester.run_all_tests()
