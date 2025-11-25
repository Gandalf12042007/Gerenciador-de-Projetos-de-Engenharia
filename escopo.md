# Escopo do Projeto – Gerenciador de Projetos de Engenharia Civil

## Objetivos

* Desenvolver uma plataforma completa e integrada para **planejamento e controle de obras civis**, permitindo acompanhamento técnico, administrativo e operacional.

- Implementar ferramentas para **gestão quantitativa** do avanço da obra, incluindo: progresso percentual por atividade, curvas de avanço planejado vs. realizado e relatório de inconsistências.
- Criar um ambiente seguro para armazenamento e versionamento de documentos técnicos (plantas, memoriais, relatórios, ARTs), com histórico completo.
- Disponibilizar a solução em **Web responsiva** e **aplicativo Mobile** (Flutter), sincronizados em tempo real via API Python.
- Suportar operações multiusuário com níveis de permissão, garantindo controle sobre ações críticas.

## Diferenciais

* **Permissões avançadas**: níveis hierárquicos (Engenheiro Responsável, Gestor, Técnico, Visitante), com acesso seletivo a tarefas, chat, relatórios e documentos.
* **Métricas e indicadores automáticos**, como: índice de produtividade, tarefas atrasadas, consumo de materiais vs. previsto.
* **Chat interno** com tópicos por projeto e mensagens arquivadas para auditoria.
* **Gestão documental completa** com categorias (plantas, RRT/ART, diário de obra, medições, relatórios fotográficos).
* **Dashboard inicial** com dados agregados: número de obras ativas, tarefas pendentes, atividades atrasadas, custo previsto vs. gasto até o momento.
* Foco visual estético voltado à engenharia civil (layouts limpos, cores técnicas, estruturas tabulares).

## Justificativa

* Obras civis enfrentam problemas recorrentes como comunicação truncada, perda de dados em campo, ferramentas dispersas e ausência de monitoramento em tempo real.
* Um sistema específico para engenharia civil reduz retrabalhos, melhora eficiência e cria rastreabilidade — essencial em auditorias, fiscalização e certificações.
* A solução atende tanto empresas quanto profissionais autônomos, ampliando o potencial de uso no mercado.

## Tecnologias Pretendidas

* **Back-end:** Python (FastAPI ou Flask), com autenticação segura (JWT), documentação via Swagger/OpenAPI.
* **Front-end Web:** HTML, CSS e JavaScript (possível uso moderado de componentes dinâmicos).
* **Mobile:** Flutter, com navegação estruturada por módulos e armazenamento local para modo offline.
* **Banco de Dados:** MySQL, com estrutura relacional completa: tabelas para usuários, permissões, projetos, tarefas, equipes, documentos, mensagens, materiais e orçamento.
* **Autenticação:** Email + senha / Login Google.
* **Hospedagem:** AWS/Render/Railway, utilizando deploy da API e banco em nuvem.

---

# Modelos das Abas (Estrutura Detalhada)

## Página de Login

**Elementos:**

* Campo *email*
* Campo *senha*
* Botão “Entrar”
* Botão “Entrar com Google”
* Checkbox “Manter conectado”
* Link “Esqueci minha senha”
* Mensagens de erro (credenciais inválidas / conta desativada)

---

## Página de Administração de Perfil

**Elementos:**

* Foto de perfil (upload + pré-visualização)
* Dados editáveis:

  * Nome completo
  * Cargo / função
  * Telefone
  * Especialidade (ex.: Engenheiro Civil, Mestre de Obra, Técnico)
  * Mini biografia
* Informações somente leitura:

  * Email cadastrado
  * Data de criação da conta
* Botões:

  * “Salvar alterações”
  * “Alterar senha”
  * “Excluir conta” (protegido)

---

## Página Inicial – Projetos

**Elementos:**

* **Dashboard** com números:

  * Obras ativas
  * Tarefas pendentes
  * Tarefas atrasadas
  * Porcentagem média de progresso das obras
* **Filtros:** Projeto ativo / concluído / por período
* **Cards de projetos:**

  * Nome do projeto
  * Local (cidade/estado)
  * Progresso visual (barra de progresso)
  * Engenheiro responsável
  * Data de início / previsão de conclusão
  * Acessos rápidos: Tarefas, Equipe, Documentos, Materiais
* Botão “Criar novo projeto”

---

## Página de Equipe

**Elementos:**

* Lista de membros:

  * Foto
  * Nome
  * Função
  * Status (ativo/inativo)
* **Permissões configuráveis**:

  * Ver tarefas / criar tarefas
  * Criar e excluir documentos
  * Acessar orçamento
  * Administrar equipe
* Ações:

  * “Convidar membro” (por email)
  * “Alterar função”
  * “Remover membro”
* Destaque visual do Engenheiro Responsável

---

## Página de Tarefas

**Elementos:**

* Kanban com 3 colunas:

  * **A Fazer**
  * **Em Execução**
  * **Concluídas**
* Dentro de cada tarefa:

  * Título
  * Descrição
  * Responsável
  * Prioridade (baixa, média, alta)
  * Data de criação
  * Prazo final
  * Anexos
  * Comentários
* Filtros: por responsável, prioridade, status e data de entrega
* Botão “Criar nova tarefa”

---

# Esquema Básico de Desenvolvimento (60 dias)

## **Dias 1–10 — Planejamento e Design**

* Finalização do escopo técnico detalhado
* Criação dos protótipos no Figma (web + mobile)
* Modelagem do banco de dados: entidades, relacionamentos, índices
* Definição da arquitetura da API (camadas, endpoints, segurança)
* Setup do repositório e ambiente de desenvolvimento

## **Dias 11–25 — Back-end (API Python)**

* CRUD de usuários + autenticação JWT
* CRUD de projetos, equipes e permissões
* CRUD de tarefas (com filtros e estados)
* Sistema de upload de arquivos (plantas, relatórios)
* CRUD de materiais e orçamentos
* Implementação do chat interno (estrutura inicial)
* Testes unitários iniciais + documentação Swagger

## **Dias 26–40 — Front-end Web**

* Implementação das páginas estruturais (login, perfil, dashboard)
* Tela de projetos + integração API
* Tela de tarefas com kanban
* Tela de equipe com permissões
* Tela de documentos
* Ajustes de responsividade e UX

## **Dias 41–55 — Aplicativo Mobile (Flutter)**

* Estrutura de navegação completa
* Telas equivalentes ao Web
* Integração total com API
* Armazenamento local para cache
* Testes em dispositivos físicos

## **Dias 56–60 — Revisões e Entregas**

* Correções gerais
* Otimizações finais de API e front-end
* Documentação técnica completa
* Preparação para apresentação final

