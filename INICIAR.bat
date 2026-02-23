@echo off
echo ============================================================
echo   INICIANDO GERENCIADOR DE PROJETOS DE ENGENHARIA
echo ============================================================
echo.

REM Verificar se Docker Desktop esta rodando
echo [1/4] Verificando Docker Desktop...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo [AVISO] Docker Desktop nao esta rodando!
    echo.
    echo Por favor:
    echo   1. Abra o Docker Desktop
    echo   2. Aguarde ele inicializar completamente
    echo   3. Execute este script novamente
    echo.
    pause
    exit /b 1
)

echo [OK] Docker Desktop esta rodando
echo.

REM Parar containers antigos
echo [2/4] Parando containers antigos...
docker-compose down >nul 2>&1
echo [OK] Containers antigos removidos
echo.

REM Iniciar containers
echo [3/4] Iniciando containers (aguarde 30-60 segundos)...
docker-compose up -d
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao iniciar containers!
    pause
    exit /b 1
)

echo.
echo [4/4] Aguardando servicos iniciarem...
timeout /t 10 /nobreak >nul

echo.
echo ============================================================
echo   SISTEMA INICIADO COM SUCESSO!
echo ============================================================
echo.
echo Servicos disponiveis:
echo   - Backend API:    http://localhost:8000
echo   - Swagger Docs:   http://localhost:8000/docs
echo   - PhpMyAdmin:     http://localhost:8080
echo   - Frontend:       Abra: web\login.html
echo.
echo Credenciais de teste:
echo   Email: vicentedesouza762@gmail.com
echo   Senha: Abacaxi371
echo.
echo ============================================================
echo.

REM Perguntar se deseja abrir o navegador
set /p ABRIR="Deseja abrir o frontend no navegador? (S/N): "
if /i "%ABRIR%"=="S" (
    start "" "%CD%\web\login.html"
    start "" "http://localhost:8000/docs"
)

echo.
echo Para ver logs do backend:
echo   docker logs -f projetos_backend
echo.
echo Para parar o sistema:
echo   docker-compose down
echo.
pause
