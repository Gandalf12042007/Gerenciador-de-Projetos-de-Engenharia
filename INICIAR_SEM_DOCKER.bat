@echo off
chcp 65001 >nul
echo ============================================================
echo   GERENCIADOR DE PROJETOS - MODO DESENVOLVIMENTO
echo   (Sem Docker - Usando SQLite)
echo ============================================================
echo.

echo [1/4] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado!
    echo Por favor, instale Python 3.11+ em: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python instalado

echo.
echo [2/4] Instalando dependencias do backend...
cd backend
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt
if %errorlevel% neq 0 (
    echo [AVISO] Algumas dependencias podem nao ter sido instaladas
)
echo [OK] Dependencias instaladas

echo.
echo [3/4] Configurando banco de dados SQLite...
cd ..\database
if not exist "gerenciador.db" (
    echo Criando banco de dados...
    python init_sqlite.py
)
echo [OK] Banco configurado

echo.
echo [4/4] Iniciando servidor backend...
cd ..\backend
echo.
echo ============================================================
echo   SISTEMA INICIADO!
echo ============================================================
echo.
echo   Backend API:     http://localhost:8000
echo   Documentacao:    http://localhost:8000/docs
echo   Frontend:        Abra: web\login.html
echo.
echo   Credenciais de teste:
echo   Email: vicentedesouza762@gmail.com
echo   Senha: Abacaxi371
echo.
echo ============================================================
echo.
echo [INFO] Servidor rodando... (Pressione Ctrl+C para parar)
echo.

python app.py
