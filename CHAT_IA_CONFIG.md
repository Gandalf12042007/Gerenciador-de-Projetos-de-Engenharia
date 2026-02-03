# 🤖 Configuração do Chat com IA (ChatGPT)

## Visão Geral

O sistema de chat agora possui integração com IA para ajudar os usuários com questões de engenharia civil e gestão de projetos.

## Funcionalidades

### 1. 🤖 Assistente IA
- Responde perguntas sobre engenharia civil
- Ajuda com orçamentos, cronogramas, materiais
- Orientações sobre segurança do trabalho
- Dicas sobre documentação técnica

### 2. 👥 Chat entre Usuários
- Conversa direta entre membros da equipe
- Histórico de mensagens
- Notificações de novas mensagens

## Configuração da API OpenAI (Opcional)

Para usar o ChatGPT real em vez das respostas simuladas:

### 1. Obter API Key

1. Acesse: https://platform.openai.com/api-keys
2. Crie uma conta ou faça login
3. Gere uma nova API Key
4. Copie a chave (começa com `sk-...`)

### 2. Configurar no Sistema

Crie ou edite o arquivo `.env` na pasta `backend/`:

```bash
# Arquivo: backend/.env

OPENAI_API_KEY=sk-sua-chave-aqui
```

### 3. Reiniciar o Backend

```bash
cd backend
python app.py
```

## Modo Offline

Se a API Key não estiver configurada, o sistema usa respostas inteligentes simuladas que cobrem temas como:

- 📊 Orçamentos e custos
- 📅 Cronogramas e prazos
- 🧱 Materiais de construção
- 🦺 Segurança do trabalho
- 👷 Gestão de equipes
- 📄 Documentação técnica

## Acessando o Chat

1. Faça login no sistema
2. Clique no botão **💬 Chat** no menu superior
3. Escolha entre:
   - **🤖 Assistente IA** - Para dúvidas de engenharia
   - **👥 Usuários** - Para conversar com outros membros

## Endpoints da API

### Chat com IA
```
POST /chat/assistente-ia
{
    "mensagem": "Como calcular orçamento de obra?",
    "contexto_projeto": "Edifício residencial 10 andares"
}
```

### Listar Usuários para Chat
```
GET /chat/usuarios-disponiveis
```

### Enviar Mensagem Direta
```
POST /chat/mensagem-direta
{
    "destinatario_id": 2,
    "conteudo": "Olá, podemos conversar sobre o projeto?"
}
```

### Histórico de Mensagens
```
GET /chat/mensagens-diretas/{usuario_id}
```

## Dicas de Uso

1. **Seja específico**: Perguntas detalhadas geram respostas melhores
2. **Contexto**: Informe detalhes do projeto quando relevante
3. **Temas**: Foque em engenharia civil, construção e gestão

## Custos (ChatGPT Real)

- GPT-3.5-turbo: ~$0.002 por 1000 tokens
- Média por pergunta: ~500 tokens = ~$0.001
- 1000 perguntas ≈ $1.00

## Suporte

Em caso de problemas:
1. Verifique se a API Key está correta
2. Confira o saldo na conta OpenAI
3. Teste sem API Key (modo simulado)
