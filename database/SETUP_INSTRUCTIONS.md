# 🗄️ Instruções de Setup do Banco de Dados MySQL

## Pré-requisitos

1. **Instalar MySQL 8.0+**
   - Download: https://dev.mysql.com/downloads/installer/
   - Durante instalação, definir senha root
   - Marcar opção "MySQL Server" e "MySQL Workbench" (opcional)

## Passo a Passo

### 1. Criar o Banco de Dados

```bash
# Abrir MySQL como root
mysql -u root -p

# Criar banco e usuário
CREATE DATABASE gerenciador_projetos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'senha_forte_aqui';
GRANT ALL PRIVILEGES ON gerenciador_projetos.* TO 'app_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 2. Configurar Variáveis de Ambiente

Criar arquivo `.env` na pasta `backend/`:

```env
# Database
DB_HOST=localhost
DB_PORT=3306
DB_NAME=gerenciador_projetos
DB_USER=app_user
DB_PASSWORD=senha_forte_aqui

# JWT
JWT_SECRET_KEY=sua_chave_secreta_muito_longa_e_aleatoria_aqui_123456
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 3. Importar Schema e Executar Migrations

```bash
# Voltar para pasta raiz do projeto
cd c:\Users\VICENTEDESOUZA\Gerenciador-de-Projetos-de-Engenharia

# Importar schema inicial
mysql -u app_user -p gerenciador_projetos < database/schema_completo.sql

# Executar migrations
python database/migrate.py

# Popular com dados de teste
python database/seed.py

# Testar conexão
python database/test_database.py
```

### 4. Verificar Instalação

Se tudo deu certo, você verá:

```
✅ Conexão estabelecida com sucesso!
✅ 18 tabelas encontradas
✅ Todos os testes passaram!
```

## Troubleshooting

### Erro: "Access denied for user"
- Verificar senha no .env
- Recriar usuário no MySQL

### Erro: "Can't connect to MySQL server"
- Verificar se MySQL está rodando: `net start MySQL80`
- Verificar firewall na porta 3306

### Erro: "Table already exists"
- Dropar banco: `DROP DATABASE gerenciador_projetos;`
- Recriar do zero

## Próximos Passos

Após setup completo:
1. Marcar tasks #4 e #5 como "Done" no GitHub Projects
2. Iniciar sistema: `.\start-sistema.bat`
3. Acessar: http://localhost:8000/docs
