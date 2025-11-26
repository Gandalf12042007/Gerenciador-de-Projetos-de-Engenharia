# Escopo do Projeto – Gerenciador de Projetos de Engenharia Civil

## Objetivos

* Desenvolver uma plataforma completa e integrada para **planejamento e controle de obras civis**, permitindo acompanhamento técnico, administrativo e operacional.

- Implementar ferramentas para **gestão quantitativa** do avanço da obra, incluindo: progresso percentual por atividade, curvas de avanço planejado vs. realizado e relatório de inconsistências.
- Criar um ambiente seguro para armazenamento e versionamento de documentos técnicos (plantas, memoriais, relatórios, ARTs), com histórico completo.
- Disponibilizar a solução em **Web responsiva** e **aplicativo Mobile** (Flutter), sincronizados em tempo real via API Python.
- Suportar operações multiusuário com níveis de permissão, garantindo controle sobre ações críticas.
## Escopo resumido

Objetivo: entregar uma base mínima funcional para avaliação que inclui autenticação básica, CRUD de
projetos, CRUD de tarefas (kanban), upload de documentos e um dashboard com indicadores essenciais.

Entregáveis para avaliação:

- Estrutura de banco de dados sugerida (tabelas para usuários, projetos, tarefas, documentos, permissões);
- Endpoints básicos da API (autenticação, projetos, tarefas, documentos);
- Templates e exemplos em `projetos/` para demonstrar uso de API e estrutura de dados;
- Documentação mínima (README e `escopo.md`) explicando como avaliar o projeto.

Tecnologias recomendadas: FastAPI (Python) para backend; front-end leve (HTML/CSS/JS); banco MySQL. Autenticação
JWT para controle de sessões.

Observação: este arquivo contém o escopo consolidado para a entrega de avaliação; detalhes de UI/fluxo podem ser
desenvolvidos posteriormente conforme cronograma.

