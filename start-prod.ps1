# Script para iniciar ambiente de produção
# Gerenciador de Projetos de Engenharia Civil

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Gerenciador de Projetos - Producao" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Docker
$dockerPath = "C:\Program Files\Docker\Docker\resources\bin\docker.exe"
$composePath = "C:\Program Files\Docker\Docker\resources\cli-plugins\docker-compose.exe"

Write-Host "Verificando Docker..." -ForegroundColor Yellow

# Testar conexao com Docker daemon
$dockerReady = $false
for ($i = 1; $i -le 10; $i++) {
    $result = & $dockerPath info 2>&1
    if ($LASTEXITCODE -eq 0) {
        $dockerReady = $true
        break
    }
    Write-Host "Aguardando Docker Desktop... ($i/10)" -ForegroundColor Gray
    Start-Sleep -Seconds 3
}

if (-not $dockerReady) {
    Write-Host ""
    Write-Host "ERRO: Docker Desktop nao esta pronto!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor:" -ForegroundColor Yellow
    Write-Host "1. Abra o Docker Desktop manualmente" -ForegroundColor White
    Write-Host "2. Aguarde o icone ficar verde na barra de tarefas" -ForegroundColor White
    Write-Host "3. Execute este script novamente" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "Docker pronto!" -ForegroundColor Green
Write-Host ""

# Iniciar containers
Write-Host "Iniciando containers de producao..." -ForegroundColor Yellow
Set-Location $PSScriptRoot

& $composePath -f docker-compose.prod.yml up -d --build

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host " Ambiente iniciado com sucesso!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Servicos disponiveis:" -ForegroundColor Cyan
    Write-Host "  - API Backend: http://localhost:8000" -ForegroundColor White
    Write-Host "  - Web (Nginx): http://localhost:80" -ForegroundColor White
    Write-Host ""
    Write-Host "Comandos uteis:" -ForegroundColor Cyan
    Write-Host "  Ver logs: docker-compose -f docker-compose.prod.yml logs -f" -ForegroundColor Gray
    Write-Host "  Parar: docker-compose -f docker-compose.prod.yml down" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "ERRO ao iniciar containers!" -ForegroundColor Red
    exit 1
}
