# 🗄️ Banco de Dados - Gerenciador de Projetos de Engenharia

Sistema completo de gerenciamento de banco de dados MySQL com migrations e seeds automatizados.

## 📋 Estrutura

```
database/
├── schema.dbml              # Diagrama do banco (visualizar em dbdiagram.io)
├── migrate.py              # Sistema de migrations
├── seed.py                 # Populador de dados de exemplo
├── migrations/
│   └── 001_initial_schema.sql  # Schema inicial completo
└── README.md               # Esta documentação
```

## 🎯 Tabelas do Sistema

### Usuários e Permissões
- `usuarios` - Dados dos usuários do sistema
- `permissoes` - Tipos de permissões (admin, gerente, engenheiro, etc)
- `usuario_permissoes` - Relacionamento usuário-permissão-projeto

### Projetos
- `projetos` - Obras de engenharia
- `equipes` - Membros da equipe por projeto
- `metricas_projeto` - Métricas diárias de progresso

### Tarefas (Kanban)
- `tarefas` - Tarefas do projeto
- `tarefa_dependencias` - Dependências entre tarefas
- `comentarios_tarefa` - Comentários nas tarefas

### Documentos
- `documentos` - Arquivos do projeto
- `versoes_documento` - Histórico de versões

### Comunicação
- `chats` - Salas de chat do projeto
- `chat_participantes` - Membros dos chats
- `mensagens` - Mensagens enviadas
- `notificacoes` - Notificações do sistema

### Orçamento
- `materiais` - Materiais e insumos
- `orcamentos` - Itens orçamentários

## 🚀 Como Usar

### 1. Visualizar Diagrama do Banco

1. Acesse: https://dbdiagram.io/
2. Cole o conteúdo do arquivo `schema.dbml`
3. Veja o diagrama visual completo com relacionamentos

### 2. Configurar MySQL

```bash
# Instalar MySQL (se necessário)
# Windows: baixe em https://dev.mysql.com/downloads/mysql/

# Criar usuário (opcional)
mysql -u root -p
CREATE USER 'gerenciador'@'localhost' IDENTIFIED BY 'senha123';
GRANT ALL PRIVILEGES ON gerenciador_projetos.* TO 'gerenciador'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Instalar Dependências Python

```bash
# Instalar conector MySQL
pip install mysql-connector-python
```

### 4. Configurar Variáveis de Ambiente (opcional)

```bash
# Windows PowerShell
$env:DB_HOST="localhost"
$env:DB_USER="root"
$env:DB_PASSWORD="suasenha"
$env:DB_NAME="gerenciador_projetos"
$env:DB_PORT="3306"

# Linux/Mac
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=suasenha
export DB_NAME=gerenciador_projetos
export DB_PORT=3306
```

### 5. Executar Migrations

```bash
# Navegar até a pasta database
cd database

# Ver status das migrations
python migrate.py status

# Executar migrations pendentes
python migrate.py run

# Ver ajuda
python migrate.py help
```

Saída esperada:
```
============================================================
GERENCIADOR DE MIGRATIONS - Projetos de Engenharia
============================================================
✓ Database 'gerenciador_projetos' verificado/criado
✓ Conectado ao MySQL - gerenciador_projetos

📦 1 migration(s) pendente(s):

  • 001_initial_schema.sql

============================================================

→ Executando: 001_initial_schema.sql
  ✓ Migration 001_initial_schema.sql executada com sucesso!

============================================================

✓ 1/1 migration(s) executada(s) com sucesso!
```

### 6. Popular com Dados de Exemplo (Seeds)

```bash
# Popular o banco (dados de exemplo)
python seed.py

# Limpar e repopular (CUIDADO: apaga todos os dados!)
python seed.py --clear
```

Saída esperada:
```
============================================================
POPULANDO BANCO DE DADOS - SEEDS
============================================================

👥 Criando usuários...
  ✓ João Silva (joao.silva@exemplo.com)
  ✓ Maria Santos (maria.santos@exemplo.com)
  ...
✓ 5 usuários criados

🔐 Criando permissões...
✓ 6 permissões criadas

🏗️  Criando projetos...
✓ 4 projetos criados

✅ Criando tarefas...
✓ 11 tarefas criadas

============================================================
✓ SEEDS EXECUTADOS COM SUCESSO!
============================================================

📊 Dados de exemplo criados:
  • 5 usuários (senha padrão: senha123)
  • 6 permissões
  • 4 projetos
  • 10 membros de equipe
  • 11 tarefas
  • 6 materiais

💡 Use estes dados para testar o sistema!
```

## 📊 Dados de Exemplo Criados

### Usuários (senha padrão: `senha123`)
- `joao.silva@exemplo.com` - Engenheiro Civil
- `maria.santos@exemplo.com` - Gerente de Projetos
- `pedro.oliveira@exemplo.com` - Técnico em Edificações
- `ana.costa@exemplo.com` - Arquiteta
- `carlos.souza@exemplo.com` - Engenheiro Estrutural

### Projetos
1. **Edifício Residencial Portal das Acácias** - 35.5% concluído
2. **Reforma Shopping Center Norte** - 45% concluído
3. **Ponte sobre o Rio Verde** - 22.3% concluído
4. **Residência Unifamiliar Alto Padrão** - Em planejamento

## 🔧 Troubleshooting

### Erro: "Access denied for user"
```bash
# Verifique suas credenciais do MySQL
mysql -u root -p

# Ou defina a senha nas variáveis de ambiente
$env:DB_PASSWORD="suasenha"
python migrate.py run
```

### Erro: "Can't connect to MySQL server"
```bash
# Verifique se o MySQL está rodando
# Windows: Services -> MySQL
# Linux: sudo service mysql status

# Verifique a porta
netstat -an | Select-String 3306
```

### Erro: "Database does not exist"
```bash
# O migrate.py cria o database automaticamente
# Mas você pode criar manualmente:
mysql -u root -p
CREATE DATABASE gerenciador_projetos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Limpar completamente e recomeçar
```bash
# Via MySQL
mysql -u root -p
DROP DATABASE gerenciador_projetos;

# Depois execute novamente
python migrate.py run
python seed.py
```

## 🎨 Características do Schema

### ✅ Integridade Referencial
- Todas as FKs com `ON DELETE CASCADE` apropriado
- Constraints UNIQUE onde necessário
- Índices em campos frequentemente consultados

### 🔒 Segurança
- Senhas com hash SHA-256
- Sistema de permissões granular (por usuário e por projeto)

### 📈 Escalabilidade
- Índices compostos para queries complexas
- Normalização adequada (3FN)
- UTF8MB4 para suporte completo a caracteres

### 📊 Auditoria
- Timestamps automáticos (created_at, updated_at)
- Versionamento de documentos
- Histórico de alterações

## 🔄 Próximos Passos

1. **Criar nova migration**
   - Crie arquivo `database/migrations/002_nome_da_migration.sql`
   - Execute `python migrate.py run`

2. **Integrar com Backend**
   - Use as credenciais configuradas
   - Implemente ORM (SQLAlchemy) ou queries diretas
   - Utilize as tabelas criadas

3. **Adicionar mais seeds**
   - Edite `seed.py`
   - Adicione mais dados de exemplo conforme necessário

## 📝 Notas Importantes

- ⚠️ **Nunca execute `seed.py --clear` em produção!**
- 🔐 **Altere as senhas padrão em produção**
- 📦 **Faça backup antes de executar migrations em produção**
- 🧪 **Use seeds apenas em desenvolvimento/testes**

## 🤝 Contribuindo

Para adicionar novas tabelas ou modificar o schema:

1. Crie uma nova migration numerada sequencialmente
2. Atualize o arquivo `schema.dbml`
3. Atualize os seeds se necessário
4. Documente as mudanças neste README

---

**Desenvolvido por:** Vicente  
**Data:** Novembro 2025  
**Projeto:** Gerenciador de Projetos de Engenharia Civil
