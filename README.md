# Gerenciador de Projetos de Engenharia

Descrição

Este repositório contém a especificação e os materiais iniciais para o desenvolvimento de uma plataforma
voltada ao planejamento e controle de obras civis. A solução tem foco em controle quantitativo do avanço da
obra, gestão documental e suporte a níveis de permissão entre membros da equipe.

1) Documentação do projeto (README)

O `README.md` serve como documento principal de apresentação do projeto. Ele descreve o problema a ser
resolvido, as funcionalidades propostas, a estrutura de pastas do repositório e instruções rápidas para
avaliação e contribuição.

2) Problema que o projeto resolve

Obras civis frequentemente sofrem com: comunicação fragmentada entre escritório e campo, perda ou má
organização de documentos técnicos (plantas, memoriais, medições), ausência de métricas claras de
avançamento e dificuldade em auditar o histórico de decisões. Esta plataforma propõe centralizar:

- Registro versionado de documentos técnicos;
- Monitoramento do progresso por atividades com curvas planejado x realizado;
- Controle de permissões para proteger ações críticas;
- Comunicação interna por projeto (mensagens/threads) com histórico para auditoria.

3) Estrutura de pastas (documentada)

- `escopo.md` — documento de escopo e cronograma do projeto (este arquivo);
- `projetos/` — modelos e exemplos para criação e gerenciamento de projetos (templates, cronogramas,
	relatórios e exemplos de payloads);
- `.git/` — metadados do repositório (mantido automaticamente pelo Git);

Observação: arquivos auxiliares temporários foram removidos para manter o repositório limpo para avaliação.

4) Escopo resumido (visão para a entrega de avaliação)

- Módulos mínimos para entrega: autenticação básica, CRUD de projetos, CRUD de tarefas (kanban), upload
	de documentos, e dashboard com indicadores principais (obras ativas, tarefas atrasadas, progresso médio).
- Tecnologias recomendadas: FastAPI (Python) para API, front-end web leve (HTML/CSS/JS) e app mobile em
	Flutter opcional.

5) Instruções para o professor — verificação e avaliação

O aluno realizou alterações neste branch (`feat/projetos-templates`) e configurou os commits com os dados
abaixo para fins de avaliação. Para verificar autoria e quantidade de commits, o professor pode inspecionar o
histórico de commits do branch e confirmar o nome/e-mail do autor.

- Aluno: Vicente
- Perfil GitHub: https://github.com/Souza371
- E-mail de commit esperado: vicentedesouza762@gmail.com

6) Como contribuir

1. Faça fork do repositório ou aponte `origin` para seu fork.
2. Crie um branch com nome descritivo (ex.: `feat/nome-da-feature`).
3. Configure `user.name` e `user.email` localmente antes de commitar (ou use `--author`).
4. Abra Pull Request a partir do seu fork contra o repositório principal.

---

Arquivo de escopo: `escopo.md` — contém o escopo detalhado para continuidade do desenvolvimento.