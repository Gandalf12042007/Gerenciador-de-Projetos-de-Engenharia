#!/bin/bash
# start.sh - Script de inicialização para produção
# Gerenciador de Projetos de Engenharia Civil
# Desenvolvido por: Vicente de Souza

set -e

echo "🚀 Iniciando aplicação em modo PRODUÇÃO..."

# Detectar porta (Railway/Render usa variável PORT)
export PORT=${PORT:-8000}

echo "📡 Porta configurada: $PORT"
echo "🔧 Ambiente: ${ENVIRONMENT:-production}"

# Verificar variáveis essenciais
if [ -z "$DB_HOST" ]; then
    echo "❌ ERRO: DB_HOST não configurado!"
    exit 1
fi

if [ -z "$SECRET_KEY" ]; then
    echo "⚠️  AVISO: SECRET_KEY não configurado! Use uma chave segura em produção."
fi

# Aguardar banco de dados estar disponível (opcional)
echo "⏳ Aguardando banco de dados..."
sleep 5

# Iniciar aplicação com Uvicorn
# Produção: sem --reload, com workers, log JSON
exec uvicorn app:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers 4 \
    --log-level info \
    --no-access-log \
    --proxy-headers \
    --forwarded-allow-ips='*'
