@echo off
echo ============================================
echo  Iniciando Sistema Gerenciador de Projetos
echo ============================================
echo.

REM Iniciar Backend API
echo [1/2] Iniciando Backend API (porta 8000)...
start "Backend API" cmd /k "cd backend && python app.py"
timeout /t 3 /nobreak >nul

REM Iniciar Frontend
echo [2/2] Iniciando Frontend (porta 3000)...
start "Frontend Web" cmd /k "cd web && python -m http.server 3000"
timeout /t 2 /nobreak >nul

echo.
echo ============================================
echo  Sistema Iniciado com Sucesso!
echo ============================================
echo.
echo  Backend API: http://localhost:8000
echo  Documentacao: http://localhost:8000/docs
echo  Frontend: http://localhost:3000/login.html
echo.
echo  Pressione qualquer tecla para abrir o navegador...
pause >nul

REM Abrir navegador
start http://localhost:8000/docs
start http://localhost:3000/login.html

echo.
echo Sistema rodando! Nao feche estas janelas.
