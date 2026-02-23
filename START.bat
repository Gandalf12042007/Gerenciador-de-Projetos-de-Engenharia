@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"

echo ============================================================
echo   GERENCIADOR DE PROJETOS - INICIANDO
echo ============================================================
echo.

echo [1/2] Configurando ambiente...
set DB_TYPE=sqlite
cd backend

echo [2/2] Iniciando servidor...
echo.
echo Backend API:     http://localhost:8000
echo Documentacao:    http://localhost:8000/docs
echo.
echo Credenciais:
echo   Email: vicentedesouza762@gmail.com  
echo   Senha: Abacaxi371
echo.
echo ============================================================
echo   SERVIDOR RODANDO
echo ============================================================
echo.

python app.py
