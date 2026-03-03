@echo off
chcp 65001 > nul
color 0A

echo.
echo ============================================================
echo   GERENCIADOR DE PROJETOS DE ENGENHARIA
echo ============================================================
echo.

echo [1/3] Verificando sistema...
cd backend
python teste_iniciar.py

if errorlevel 1 (
    echo.
    echo ERRO: Verificacao falhou!
    pause
    exit /b 1
)

echo.
echo [2/3] Iniciando servidor backend...
echo.
echo SERVIDOR RODANDO EM: http://localhost:8000
echo.
echo Para acessar o sistema, abra seu navegador e va para:
echo   http://localhost:8000/login.html
echo.
echo Documentacao da API:
echo   http://localhost:8000/docs
echo.
echo Pressione Ctrl+C para parar o servidor
echo.
echo ============================================================
echo.

python app.py

pause
