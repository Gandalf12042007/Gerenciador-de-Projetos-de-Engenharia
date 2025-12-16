# 📊 Diagrama ER - Banco de Dados

## Visualização Online

Para ver o diagrama interativo completo:

1. Acesse: https://dbdiagram.io/
2. Clique em "Import" ou cole o código
3. Cole o conteúdo do arquivo `schema.dbml`
4. Visualize o diagrama com todos os relacionamentos

## Estrutura Resumida

```
┌─────────────────────────────────────────────────────────────┐
│                    SISTEMA DE GERENCIAMENTO                  │
│                   DE PROJETOS DE ENGENHARIA                  │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│    USUÁRIOS      │────>│    PROJETOS      │────>│     TAREFAS      │
│                  │     │                  │     │                  │
│ • id (PK)        │     │ • id (PK)        │     │ • id (PK)        │
│ • nome           │     │ • nome           │     │ • titulo         │
│ • email          │     │ • status         │     │ • status         │
│ • senha_hash     │     │ • valor_total    │     │ • prioridade     │
│ • cargo          │     │ • progresso      │     │ • responsavel_id │
│ • ativo          │     │ • criador_id(FK) │     │ • projeto_id(FK) │
└──────────────────┘     └──────────────────┘     └──────────────────┘
        │                         │                         │
        │                         │                         │
        v                         v                         v
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   PERMISSÕES     │     │     EQUIPES      │     │   COMENTÁRIOS    │
│                  │     │                  │     │                  │
│ • id (PK)        │     │ • id (PK)        │     │ • id (PK)        │
│ • nome           │     │ • projeto_id(FK) │     │ • tarefa_id (FK) │
│ • descricao      │     │ • usuario_id(FK) │     │ • usuario_id(FK) │
│                  │     │ • papel          │     │ • comentario     │
└──────────────────┘     │ • ativo          │     └──────────────────┘
        │                └──────────────────┘              
        │                         
        v                         
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ USUARIO_PERMISS. │     │   DOCUMENTOS     │     │      CHATS       │
│                  │     │                  │     │                  │
│ • id (PK)        │     │ • id (PK)        │     │ • id (PK)        │
│ • usuario_id(FK) │     │ • projeto_id(FK) │     │ • projeto_id(FK) │
│ • permissao_id   │     │ • nome           │     │ • nome           │
│ • projeto_id(FK) │     │ • tipo           │     │ • tipo           │
└──────────────────┘     │ • arquivo_url    │     └──────────────────┘
                         │ • versao         │              │
                         └──────────────────┘              │
                                  │                        v
                                  │               ┌──────────────────┐
                                  v               │    MENSAGENS     │
                         ┌──────────────────┐     │                  │
                         │ VERSOES_DOC      │     │ • id (PK)        │
                         │                  │     │ • chat_id (FK)   │
                         │ • id (PK)        │     │ • usuario_id(FK) │
                         │ • documento_id   │     │ • mensagem       │
                         │ • versao         │     │ • criado_em      │
                         │ • arquivo_url    │     └──────────────────┘
                         └──────────────────┘     
                         
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│    MATERIAIS     │     │    ORÇAMENTOS    │     │    MÉTRICAS      │
│                  │     │                  │     │                  │
│ • id (PK)        │     │ • id (PK)        │     │ • id (PK)        │
│ • projeto_id(FK) │     │ • projeto_id(FK) │     │ • projeto_id(FK) │
│ • nome           │     │ • descricao      │     │ • data_registro  │
│ • unidade        │     │ • categoria      │     │ • tarefas_concl. │
│ • qtd_prevista   │     │ • valor_previsto │     │ • progresso      │
│ • qtd_utilizada  │     │ • valor_real     │     │ • horas_trab.    │
│ • preco_unit.    │     │ • status         │     │ • valor_gasto    │
└──────────────────┘     └──────────────────┘     └──────────────────┘

                    ┌──────────────────┐
                    │  NOTIFICAÇÕES    │
                    │                  │
                    │ • id (PK)        │
                    │ • usuario_id(FK) │
                    │ • tipo           │
                    │ • titulo         │
                    │ • mensagem       │
                    │ • lida           │
                    └──────────────────┘
```

## Relacionamentos Principais

### 1:N (Um para Muitos)
- 1 Usuário → N Projetos (como criador)
- 1 Projeto → N Tarefas
- 1 Projeto → N Documentos
- 1 Projeto → N Chats
- 1 Projeto → N Materiais
- 1 Projeto → N Orçamentos
- 1 Chat → N Mensagens
- 1 Tarefa → N Comentários

### N:M (Muitos para Muitos)
- Usuários ←→ Projetos (via Equipes)
- Usuários ←→ Permissões (via Usuario_Permissoes)
- Usuários ←→ Chats (via Chat_Participantes)
- Tarefas ←→ Tarefas (via Tarefa_Dependencias)

## Tipos ENUM

### Status de Projeto
- `planejamento`
- `em_andamento`
- `pausado`
- `concluido`
- `cancelado`

### Status de Tarefa
- `a_fazer`
- `em_andamento`
- `em_revisao`
- `concluida`

### Prioridade de Tarefa
- `baixa`
- `media`
- `alta`
- `urgente`

### Tipos de Documento
- `contrato`
- `projeto`
- `laudo`
- `orcamento`
- `nota_fiscal`
- `outro`

### Categorias de Orçamento
- `material`
- `mao_obra`
- `equipamento`
- `servico`
- `outro`

## Índices Importantes

```sql
-- Performance em queries frequentes
CREATE INDEX idx_projetos_status ON projetos(status);
CREATE INDEX idx_tarefas_projeto_status ON tarefas(projeto_id, status);
CREATE INDEX idx_mensagens_chat_data ON mensagens(chat_id, criado_em DESC);
CREATE INDEX idx_documentos_projeto ON documentos(projeto_id);
CREATE INDEX idx_notificacoes_usuario ON notificacoes(usuario_id, lida);
```

## Constraints de Integridade

- ✅ **Foreign Keys**: Todas as relações têm FKs definidas
- ✅ **ON DELETE CASCADE**: Cascatas apropriadas (ex: deletar projeto → deletar tarefas)
- ✅ **UNIQUE Constraints**: Em combinações críticas (email, usuario+permissao+projeto)
- ✅ **NOT NULL**: Campos obrigatórios marcados
- ✅ **DEFAULT Values**: Valores padrão sensatos (status, progresso, ativo)

## Características Técnicas

- **Engine**: InnoDB (suporte a transações e FKs)
- **Charset**: UTF8MB4 (emojis e caracteres especiais)
- **Collation**: utf8mb4_unicode_ci (ordenação correta de português)
- **Timestamps**: Automáticos (CURRENT_TIMESTAMP, ON UPDATE)
- **Auditoria**: Campos created_at e updated_at em todas as tabelas

---

**Total**: 18 tabelas | 70+ campos | 25+ relacionamentos
