#!/bin/bash
# Script para configurar a aplicação React
# Cria estrutura de pasta e arquivos base para o frontend React

echo "🚀 Iniciando setup do React App..."

# Criar diretório web-react se não existir
mkdir -p web-react
cd web-react

# Estrutura de pastas
mkdir -p src/components/{common,layout,pages}
mkdir -p src/pages/{auth,dashboard,projetos,tarefas,financeiro}
mkdir -p src/store
mkdir -p src/api
mkdir -p src/styles
mkdir -p src/utils
mkdir -p src/hooks
mkdir -p public

echo "📁 Estrutura de pastas criada"

# Criar package.json
cat > package.json << 'EOFPKG'
{
  "name": "gerenciador-projetos",
  "version": "1.0.0",
  "description": "Gerenciador de Projetos de Engenharia Civil - Frontend React",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.11.0",
    "zustand": "^4.3.9",
    "axios": "^1.4.0",
    "chart.js": "^4.3.0",
    "react-chartjs-2": "^5.2.0",
    "phosphor-react": "^1.4.12"
  },
  "devDependencies": {
    "react-scripts": "5.0.1",
    "tailwindcss": "^3.3.2",
    "postcss": "^8.4.24",
    "autoprefixer": "^10.4.14"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
EOFPKG

echo "✅ package.json criado"
