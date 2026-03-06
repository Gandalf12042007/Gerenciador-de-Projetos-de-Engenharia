# Script PowerShell para iniciar o sistema
# Salve como: iniciar.ps1

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  GERENCIADOR DE PROJETOS DE ENGENHARIA" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

Set-Location -Path "$PSScriptRoot\backend"

Write-Host "[1/2] Verificando sistema..." -ForegroundColor Yellow
python teste_iniciar.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERRO: Verificacao falhou!" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Host ""
Write-Host "[2/2] Iniciando servidor..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Servidor rodando em: http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Abra seu navegador e acesse:" -ForegroundColor White
Write-Host "  http://localhost:8000/login.html" -ForegroundColor Green
Write-Host ""
Write-Host "Documentacao da API:" -ForegroundColor White
Write-Host "  http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Pressione Ctrl+C para parar o servidor" -ForegroundColor Yellow
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

# Abrir navegador automaticamente
Start-Sleep -Seconds 3
Start-Process "http://localhost:8000/login.html"

# Iniciar servidor
python app.py
