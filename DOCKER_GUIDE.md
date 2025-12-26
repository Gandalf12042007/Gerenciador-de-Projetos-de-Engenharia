# 🐳 Docker Quick Start Guide

## Gerenciador de Projetos de Engenharia Civil
**Desenvolvido por:** Vicente de Souza

---

## 📋 O que o Docker faz?

Este projeto usa **Docker Compose** para criar 3 serviços automaticamente:

1. **MySQL 8.0** - Banco de dados (porta 3306)
2. **Backend FastAPI** - API REST (porta 8000)
3. **PhpMyAdmin** - Interface web para gerenciar MySQL (porta 8080)

---

## 🚀 Como Usar

### 1. **Instalar Docker Desktop**
- **Windows/Mac:** https://www.docker.com/products/docker-desktop
- **Linux:** `sudo apt install docker.io docker-compose`

### 2. **Iniciar o Sistema**
```bash
# No diretório raiz do projeto
docker-compose up -d
```

**O que acontece:**
- ✅ Baixa imagens do MySQL e Python
- ✅ Cria containers isolados
- ✅ Importa schema do banco automaticamente
- ✅ Inicia backend na porta 8000
- ✅ Configura rede entre containers

**Tempo:** ~2-3 minutos na primeira vez

### 3. **Verificar se está rodando**
```bash
docker-compose ps
```

Você deve ver:
```
NAME                  STATUS    PORTS
projetos_db           Up        0.0.0.0:3306->3306/tcp
projetos_backend      Up        0.0.0.0:8000->8000/tcp
projetos_phpmyadmin   Up        0.0.0.0:8080->80/tcp
```

### 4. **Acessar o Sistema**
- **Backend API:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs
- **PhpMyAdmin:** http://localhost:8080
  - Server: `db`
  - User: `root`
  - Password: `root_password_123`

### 5. **Ver Logs**
```bash
# Logs de todos os serviços
docker-compose logs -f

# Logs apenas do backend
docker-compose logs -f backend

# Logs apenas do MySQL
docker-compose logs -f db
```

### 6. **Parar o Sistema**
```bash
# Parar containers (dados permanecem)
docker-compose stop

# Parar e remover containers (dados permanecem nos volumes)
docker-compose down

# CUIDADO: Remover containers E volumes (apaga dados)
docker-compose down -v
```

---

## 🔧 Comandos Úteis

### Reiniciar apenas o backend
```bash
docker-compose restart backend
```

### Reconstruir backend após mudanças no código
```bash
docker-compose up -d --build backend
```

### Acessar terminal do backend
```bash
docker-compose exec backend bash
```

### Acessar MySQL via linha de comando
```bash
docker-compose exec db mysql -u root -proot_password_123 gerenciador_projetos
```

### Ver uso de recursos
```bash
docker stats
```

### Limpar tudo (CUIDADO)
```bash
docker-compose down -v
docker system prune -a
```

---

## 📂 Volumes (Persistência de Dados)

Os dados são salvos em volumes Docker:

- **mysql_data:** Banco de dados completo
- **uploads_data:** Arquivos enviados (documentos)
- **logs_data:** Logs da aplicação

Mesmo parando os containers, os dados permanecem!

---

## 🔐 Variáveis de Ambiente

Configuradas no `docker-compose.yml`:

### MySQL
- `MYSQL_ROOT_PASSWORD`: root_password_123
- `MYSQL_DATABASE`: gerenciador_projetos
- `MYSQL_USER`: projeto_user
- `MYSQL_PASSWORD`: projeto_pass_123

### Backend
- `DB_HOST`: db (nome do container)
- `SECRET_KEY`: (mude em produção!)
- `DEBUG`: True

**⚠️ PRODUÇÃO:** Nunca use essas senhas em produção! Use `.env` file ou secrets.

---

## 🐛 Troubleshooting

### Erro: "Port is already allocated"
```bash
# Porta 3306, 8000 ou 8080 já está em uso
# Pare o MySQL/serviço local primeiro
sudo service mysql stop  # Linux
net stop MySQL  # Windows (Admin)
```

### Backend não conecta no MySQL
```bash
# Verifique logs
docker-compose logs db
docker-compose logs backend

# Recrie os containers
docker-compose down
docker-compose up -d
```

### Mudanças no código não aparecem
```bash
# Hot reload está ativado, mas se não funcionar:
docker-compose restart backend
```

### MySQL não importa schema
```bash
# Remova o volume e recrie
docker-compose down -v
docker-compose up -d
```

### Performance lenta
```bash
# Aumente memória do Docker Desktop:
# Settings > Resources > Memory: 4GB+
```

---

## 📖 Arquitetura Docker

```
┌─────────────────────────────────────────┐
│         docker-compose.yml              │
│  (Orquestra todos os serviços)          │
└─────────────────────────────────────────┘
              │
    ┌─────────┼──────────┐
    │         │          │
    ▼         ▼          ▼
┌───────┐ ┌─────────┐ ┌──────────┐
│ MySQL │ │ Backend │ │PhpMyAdmin│
│  :3306│ │  :8000  │ │  :8080   │
└───────┘ └─────────┘ └──────────┘
    │         │
    │    ┌────┴─────┐
    │    │          │
    ▼    ▼          ▼
 [mysql] [uploads] [logs]
 volume   volume   volume
```

---

## 🎓 Próximos Passos

1. ✅ Sistema rodando local com Docker
2. 🔲 Deploy no Railway/Render (próxima tarefa)
3. 🔲 CI/CD com GitHub Actions
4. 🔲 Monitoramento e logs

---

## 📞 Suporte

Dúvidas? Veja:
- [`README.md`](../README.md) - Documentação geral
- [`COMO_RODAR.md`](../COMO_RODAR.md) - Guia completo
- [`docker-compose.yml`](../docker-compose.yml) - Configuração

**Desenvolvedor:** Vicente de Souza  
**Data:** Dezembro 2025
