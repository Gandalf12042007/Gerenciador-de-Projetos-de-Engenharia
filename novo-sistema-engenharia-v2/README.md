# Novo Gerenciador de Projetos de Engenharia (v2)

Sistema novo, separado do legado, focado em estabilidade no login e na tela inicial.

## O que este sistema tem

- Cadastro e login de usuario
- Sessao por cookie assinado (sem perder dados no fluxo)
- Dashboard protegido
- CRUD de projetos (criar, listar, atualizar status, excluir)
- Banco SQLite local
- Interface responsiva para desktop e celular

## Requisitos

- Python 3.10+

## Como rodar

1. Entre na pasta:

```bash
cd novo-sistema-engenharia-v2
```

2. Execute:

```bash
python3 app.py
```

3. Abra no navegador:

```text
http://127.0.0.1:8080
```

## Testes automatizados

Execute:

```bash
python3 -m unittest discover -s tests -v
```

## Estrutura

- `app.py`: servidor web e regras de negocio
- `static/style.css`: visual da aplicacao
- `database.db`: criado automaticamente na primeira execucao

## Publicar no GitHub (seu usuario)

Depois de testar localmente:

```bash
git add novo-sistema-engenharia-v2
git commit -m "feat: novo sistema de gerenciador de engenharia v2"
```

Criando repo no seu perfil `Souza371` (nome sugerido: `gerenciador-engenharia-v2`) e conectando:

```bash
git remote add novo https://github.com/Souza371/gerenciador-engenharia-v2.git
git push -u novo main
```

## Observacao de seguranca

Para producao, defina variavel de ambiente forte:

```bash
export APP_SECRET_KEY="uma-chave-bem-forte-e-unica"
```

Opcional para producao atras de proxy HTTPS:

- defina `APP_SECRET_KEY` forte e unica
- rode com servidor WSGI adequado (gunicorn/uwsgi)
- force HTTPS no proxy para habilitar cookie `secure`
