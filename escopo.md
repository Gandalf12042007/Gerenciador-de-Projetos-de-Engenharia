# Escopo do Projeto – Gerenciador de Projetos de Engenharia Civil

## 1. Objetivos

- Desenvolver uma plataforma completa e integrada para planejamento e controle de obras civis, permitindo acompanhamento técnico, administrativo e operacional.
- Implementar ferramentas para gestão quantitativa do avanço da obra, incluindo progresso percentual por atividade, curvas de avanço planejado vs. realizado e relatórios de inconsistências.
- Criar um ambiente seguro para armazenamento e versionamento de documentos técnicos (plantas, memoriais, relatórios, ARTs), com histórico completo.
- Disponibilizar a solução em Web responsiva e aplicativo Mobile (Flutter), sincronizados em tempo real via API Python.
- Suportar operações multiusuário com níveis de permissão, garantindo controle sobre ações críticas.

## 2. Diferenciais (Principais)

- Permissões avançadas: níveis hierárquicos (Engenheiro Responsável, Gestor, Técnico, Visitante), com acesso seletivo a tarefas, chat, relatórios e documentos.
- Métricas e indicadores automáticos, como índice de produtividade, tarefas atrasadas, consumo de materiais vs. previsto.
- Chat interno com tópicos por projeto e mensagens arquivadas para auditoria.
- Gestão documental completa com categorias (plantas, RRT/ART, diário de obra, medições, relatórios fotográficos).
- Dashboard inicial com dados agregados: número de obras ativas, tarefas pendentes, atividades atrasadas, custo previsto vs. gasto até o momento.
- Foco visual estético voltado à engenharia civil (layouts limpos, cores técnicas, estruturas tabulares).

## 3. Justificativa

Obras civis enfrentam problemas recorrentes como comunicação truncada, perda de dados em campo, ferramentas dispersas e ausência de monitoramento em tempo real. Um sistema específico para engenharia civil reduz retrabalhos, melhora eficiência e cria rastreabilidade — essencial em auditorias, fiscalização e certificações. A solução atende tanto empresas quanto profissionais autônomos, ampliando o potencial de uso no mercado.

## 4. Tecnologias Pretendidas

- **Back-end:** Python (FastAPI ou Flask) com autenticação segura (JWT) e documentação via OpenAPI/Swagger.
- **Front-end Web:** HTML, CSS e JavaScript (componentes dinâmicos conforme necessário).
- **Mobile:** Flutter, com navegação modular e suporte a storage local para modo offline.
- **Banco de Dados:** MySQL (estrutura relacional: usuários, permissões, projetos, tarefas, equipes, documentos, mensagens, materiais, orçamentos).
- **Autenticação:** Email + senha, Login via Google e tokens JWT. Uso de Personal Access Tokens para ações administrativas quando necessário.
- **Hospedagem / Infraestrutura:** AWS / Render / Railway, deploy da API e banco em nuvem, uso de S3 ou armazenamento equivalente para arquivos.

## 5. Modelos das Abas (Estrutura Detalhada de Telas)

### 5.1 Página de Login

Elementos:
- Campo email, campo senha;
- Botão “Entrar” e “Entrar com Google”;
- Checkbox “Manter conectado”; Link “Esqueci minha senha”;
- Mensagens de erro (credenciais inválidas / conta desativada).

### 5.2 Página de Administração de Perfil

Elementos:
- Foto de perfil (upload + pré-visualização);
- Dados editáveis: Nome completo, Cargo/Função, Telefone, Especialidade, Mini biografia;
- Informações somente leitura: Email cadastrado, Data de criação da conta;
- Botões: “Salvar alterações”, “Alterar senha”, “Excluir conta” (com proteção/aviso).

### 5.3 Página Inicial – Projetos (Dashboard)

Elementos:
- Dashboard com indicadores: obras ativas, tarefas pendentes, tarefas atrasadas, % média de progresso, custo previsto vs. gasto;
- Filtros: por status (ativo/concluído) e período;
- Cards de projetos com informações e atalhos: Nome, Local, Progresso (barra), Engenheiro Responsável, Data de início / previsão de conclusão, Acessos rápidos para Tarefas, Equipe, Documentos, Materiais;
- Botão “Criar novo projeto”.

### 5.4 Página de Equipe

Elementos:
- Lista de membros com foto, nome, função, status;
- Permissões configuráveis (criar/editar tarefas, documentos, acessar orçamento, administrar equipe);
- Ações: “Convidar membro” (por email), “Alterar função”, “Remover membro”;
- Destaque do Engenheiro Responsável.

### 5.5 Página de Tarefas

Elementos:
- Kanban com colunas “A Fazer”, “Em Execução”, “Concluídas”;
- Cada tarefa exibe: título, descrição, responsável, prioridade, data de criação, prazo, anexos, comentários;
- Filtros por responsável, prioridade, status e data de entrega;
- Botão “Criar nova tarefa”.

### 5.6 Documentos e Arquivos

Elementos:
- Upload, versionamento e histórico de alterações;
- Categorias e tags (plantas, RRT/ART, diário, medições, fotos);
- Permissões finas para leitura/edição/exclusão;
- Visualizador de arquivos integrado (se aplicável).

### 5.7 Chat Interno

Elementos:
- Tópicos por projeto, busca por mensagens, armazenamento e exportação para auditoria;
- Recurso de menção (@usuario) e anexar fotos/arquivos;
- Mensagens arquivadas e logs de auditoria para rastreabilidade.

## 6. Métricas e Relatórios

- Avanço físico por atividade (percentual);
- Curvas de avanço planejado vs. realizado;
- Índice de produtividade e tarefas atrasadas por responsável;
- Consumo de materiais (real vs. previsto);
- Relatórios de inconsistências e audit trail (alterações e comentários).

## 7. Esquema Básico de Desenvolvimento (60 dias)

**Dias 1–10 — Planejamento e Design**
- Finalização do escopo técnico detalhado;
- Criação de protótipos no Figma (web + mobile);
- Modelagem do banco de dados (entidades, relacionamentos, índices);
- Definição da arquitetura da API (camadas, endpoints, segurança);
- Setup do repositório e ambiente de desenvolvimento.

**Dias 11–25 — Back-end (API Python)**
- CRUD de usuários + autenticação JWT;
- CRUD de projetos, equipes e permissões;
- CRUD de tarefas (com filtros e estados);
- Sistema de upload de arquivos (plantas, relatórios);
- CRUD de materiais e orçamentos;
- Implementação do chat interno (estrutura inicial);
- Testes unitários iniciais + documentação Swagger.

**Dias 26–40 — Front-end Web**
- Implementação das páginas estruturais (login, perfil, dashboard);
- Tela de projetos + integração API;
- Tela de tarefas com Kanban;
- Tela de equipe com permissões;
- Tela de documentos;
- Ajustes de responsividade e UX.

**Dias 41–55 — Aplicativo Mobile (Flutter)**
- Estrutura de navegação completa;
- Telas equivalentes ao Web;
- Integração total com API;
- Armazenamento local para cache / modo offline;
- Testes em dispositivos físicos.

**Dias 56–60 — Revisões e Entregas**
- Correções gerais e otimizações;
- Melhorias de performance e segurança;
- Documentação técnica completa;
- Preparação para apresentação final (demo e entrega).

## 8. Observações e Próximos Passos

- Validar requisitos com stakeholders e priorizar features do MVP;
- Criar JIRA / GitHub Issues para as sprints iniciais;
- Definir critérios de aceite e plano de testes para cada entrega;
- Confirmar infraestrutura de hospedagem e estratégia de deploy (CI/CD);
- Planejar revisão de segurança (autenticação, autorização, proteção de arquivos) antes do lançamento em produção.

---

_Este documento apresenta o escopo inicial do projeto e pode ser atualizado conforme definição de prioridades, feedback de usuários e evolução das necessidades do cliente._

