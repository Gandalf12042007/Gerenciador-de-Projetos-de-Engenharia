@echo off
echo ========================================
echo   Gerenciador de Projetos de Engenharia
echo ========================================
echo.
echo Iniciando o sistema...
echo.

cd backend
echo [1/2] Iniciando Backend (FastAPI)...
start "Backend - FastAPI" cmd /k "python app.py"

timeout /t 3 /nobreak > nul

echo [2/2] Abrindo navegador...
start http://localhost:8000/login.html

echo.
echo ========================================
echo   Sistema iniciado com sucesso!
echo ========================================
echo.
echo Backend (API):    http://localhost:8000
echo Documentacao:     http://localhost:8000/docs
echo Login:            http://localhost:8000/login.html
echo.
echo Pressione qualquer tecla para fechar esta janela...
pause > nul
