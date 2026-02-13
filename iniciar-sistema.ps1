# Gerenciador de Projetos de Engenharia
# Script para iniciar o sistema localmente
# Criado: 10/02/2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Gerenciador de Projetos de Engenharia" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$rootPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# Iniciar Backend
Write-Host "[1/3] Iniciando Backend API..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    param($path)
    Set-Location "$path\backend"
    python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
} -ArgumentList $rootPath

Start-Sleep -Seconds 2

# Iniciar Frontend
Write-Host "[2/3] Iniciando Frontend Web..." -ForegroundColor Yellow
$frontendJob = Start-Job -ScriptBlock {
    param($path)
    Set-Location "$path\web"
    python -m http.server 3000
} -ArgumentList $rootPath

Start-Sleep -Seconds 2

# Abrir navegador
Write-Host "[3/3] Abrindo navegador..." -ForegroundColor Yellow
Start-Process "http://localhost:3000/login.html"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " Sistema iniciado com sucesso!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "  Frontend:    http://localhost:3000" -ForegroundColor White
Write-Host "  Swagger:     http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Pressione Ctrl+C para parar os servidores..." -ForegroundColor Gray

try {
    while ($true) {
        Start-Sleep -Seconds 5
    }
} finally {
    Write-Host "Parando servidores..." -ForegroundColor Yellow
    Stop-Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob, $frontendJob -Force -ErrorAction SilentlyContinue
    Write-Host "Servidores parados." -ForegroundColor Green
}
