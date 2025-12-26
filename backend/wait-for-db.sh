#!/bin/bash
# wait-for-db.sh
# Script para aguardar o MySQL estar pronto antes de iniciar o backend
# Desenvolvido por: Vicente de Souza

set -e

host="$1"
shift
cmd="$@"

echo "⏳ Aguardando MySQL estar disponível em $host..."

until mysql -h"$host" -u"${DB_USER}" -p"${DB_PASSWORD}" -e "SELECT 1" &> /dev/null
do
  echo "MySQL ainda não está pronto - aguardando..."
  sleep 2
done

echo "✅ MySQL está pronto! Iniciando aplicação..."
exec $cmd
