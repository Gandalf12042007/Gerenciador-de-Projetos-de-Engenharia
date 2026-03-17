import html
import os
import secrets
import sqlite3
import time
from hashlib import pbkdf2_hmac, sha256
from hmac import compare_digest, new as hmac_new
from http import cookies
from urllib.parse import parse_qs, quote_plus
from wsgiref.simple_server import make_server

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
STATIC_DIR = os.path.join(BASE_DIR, "static")
SECRET_KEY = os.environ.get("APP_SECRET_KEY", "trocar-em-producao-chave-forte")
SESSION_TTL = 60 * 60 * 12
PBKDF2_ROUNDS = 120_000


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at INTEGER NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                area TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Planejamento',
                description TEXT,
                created_at INTEGER NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )


def hash_password(password, salt=None):
    salt_bytes = salt if isinstance(salt, bytes) else secrets.token_bytes(16)
    derived = pbkdf2_hmac("sha256", password.encode("utf-8"), salt_bytes, PBKDF2_ROUNDS)
    return f"{salt_bytes.hex()}${derived.hex()}"


def verify_password(password, encoded):
    try:
        salt_hex, digest_hex = encoded.split("$", 1)
        salt_bytes = bytes.fromhex(salt_hex)
    except ValueError:
        return False
    except TypeError:
        return False
    check = pbkdf2_hmac("sha256", password.encode("utf-8"), salt_bytes, PBKDF2_ROUNDS).hex()
    return compare_digest(check, digest_hex)


def sign_session(user_id, expires_at):
    payload = f"{user_id}:{expires_at}"
    signature = hmac_new(SECRET_KEY.encode("utf-8"), payload.encode("utf-8"), sha256).hexdigest()
    return f"{payload}:{signature}"


def parse_session(value):
    parts = value.split(":")
    if len(parts) != 3:
        return None
    user_id, expires_at, signature = parts
    payload = f"{user_id}:{expires_at}"
    expected = hmac_new(SECRET_KEY.encode("utf-8"), payload.encode("utf-8"), sha256).hexdigest()
    if not compare_digest(signature, expected):
        return None
    try:
        uid = int(user_id)
        exp = int(expires_at)
    except ValueError:
        return None
    if exp < int(time.time()):
        return None
    return uid


def get_request_cookies(environ):
    jar = cookies.SimpleCookie()
    jar.load(environ.get("HTTP_COOKIE", ""))
    return jar


def get_logged_user_id(environ):
    jar = get_request_cookies(environ)
    token = jar.get("session")
    if not token:
        return None
    return parse_session(token.value)


def parse_form(environ):
    content_type = (environ.get("CONTENT_TYPE") or "").lower()
    if "application/x-www-form-urlencoded" not in content_type:
        return {}
    length = int(environ.get("CONTENT_LENGTH") or 0)
    body = environ["wsgi.input"].read(length).decode("utf-8") if length > 0 else ""
    return {k: v[0] for k, v in parse_qs(body).items()}


def with_msg(path, message):
    return f"{path}?msg={quote_plus(message)}"


def response(start_response, body, status="200 OK", headers=None):
    headers = headers or []
    headers = [("Content-Type", "text/html; charset=utf-8"), *headers]
    start_response(status, headers)
    return [body.encode("utf-8")]


def redirect(start_response, to, headers=None):
    headers = headers or []
    start_response("302 Found", [("Location", to), *headers])
    return [b""]


def render_page(title, content, flash=""):
    message_html = f'<div class="flash">{html.escape(flash)}</div>' if flash else ""
    return f"""
<!DOCTYPE html>
<html lang=\"pt-BR\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>{html.escape(title)}</title>
  <link rel=\"stylesheet\" href=\"/static/style.css\" />
</head>
<body>
  <main class=\"page\">{message_html}{content}</main>
</body>
</html>
"""


def landing_page(flash=""):
    content = """
<section class=\"hero\">
  <h1>Gerenciador de Projetos de Engenharia</h1>
  <p>Versao nova, leve e funcional para organizar projetos, etapas e andamento.</p>
</section>
<section class=\"cards\">
  <article class=\"card\">
    <h2>Entrar</h2>
    <form method=\"post\" action=\"/login\">
      <label>Email<input type=\"email\" name=\"email\" required /></label>
      <label>Senha<input type=\"password\" name=\"password\" required /></label>
      <button type=\"submit\">Login</button>
    </form>
  </article>
  <article class=\"card\">
    <h2>Criar conta</h2>
    <form method=\"post\" action=\"/register\">
      <label>Nome<input type=\"text\" name=\"name\" required /></label>
      <label>Email<input type=\"email\" name=\"email\" required /></label>
      <label>Senha<input type=\"password\" name=\"password\" minlength=\"6\" required /></label>
      <button type=\"submit\">Cadastrar</button>
    </form>
  </article>
</section>
"""
    return render_page("Inicio", content, flash)


def dashboard_page(user, projects, flash=""):
    rows = ""
    for project in projects:
        rows += f"""
<tr>
  <td>{html.escape(project['name'])}</td>
  <td>{html.escape(project['area'])}</td>
  <td>{html.escape(project['status'])}</td>
  <td>{html.escape(project['description'] or '')}</td>
  <td>
    <form class=\"inline\" method=\"post\" action=\"/projects/{project['id']}/status\">
      <select name=\"status\">
        <option {'selected' if project['status']=='Planejamento' else ''}>Planejamento</option>
        <option {'selected' if project['status']=='Em execucao' else ''}>Em execucao</option>
        <option {'selected' if project['status']=='Concluido' else ''}>Concluido</option>
      </select>
      <button>Salvar</button>
    </form>
    <form class=\"inline\" method=\"post\" action=\"/projects/{project['id']}/delete\">
      <button class=\"danger\">Excluir</button>
    </form>
  </td>
</tr>
"""

    content = f"""
<header class=\"top\">
  <div>
    <h1>Painel de Projetos</h1>
    <p>Usuario: {html.escape(user['name'])} ({html.escape(user['email'])})</p>
  </div>
  <form method=\"post\" action=\"/logout\"><button>Sair</button></form>
</header>
<section class=\"card\">
  <h2>Novo projeto</h2>
  <form class=\"grid\" method=\"post\" action=\"/projects\">
    <label>Nome<input type=\"text\" name=\"name\" required /></label>
    <label>Area<input type=\"text\" name=\"area\" required /></label>
    <label class=\"full\">Descricao<textarea name=\"description\" rows=\"3\"></textarea></label>
    <button type=\"submit\">Salvar projeto</button>
  </form>
</section>
<section class=\"card\">
  <h2>Projetos cadastrados</h2>
  <table>
    <thead><tr><th>Nome</th><th>Area</th><th>Status</th><th>Descricao</th><th>Acoes</th></tr></thead>
    <tbody>{rows or '<tr><td colspan="5">Nenhum projeto ainda.</td></tr>'}</tbody>
  </table>
</section>
"""
    return render_page("Dashboard", content, flash)


def app(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET")
    flash = parse_qs(environ.get("QUERY_STRING", "")).get("msg", [""])[0]

    if path == "/health" and method == "GET":
        start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
        return [b"ok"]

    if path.startswith("/static/"):
        requested = path.removeprefix("/static/")
        normalized = os.path.normpath(requested).lstrip("/")
        file_path = os.path.abspath(os.path.join(STATIC_DIR, normalized))
        if not file_path.startswith(os.path.abspath(STATIC_DIR) + os.sep):
            start_response("403 Forbidden", [("Content-Type", "text/plain")])
            return [b"Acesso negado"]
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                data = f.read()
            content_type = "text/css" if file_path.endswith(".css") else "text/plain"
            start_response("200 OK", [("Content-Type", content_type)])
            return [data]
        start_response("404 Not Found", [("Content-Type", "text/plain")])
        return [b"Arquivo nao encontrado"]

    user_id = get_logged_user_id(environ)

    if path == "/" and method == "GET":
        if user_id:
            return redirect(start_response, "/dashboard")
        return response(start_response, landing_page(flash))

    if path == "/register" and method == "POST":
        data = parse_form(environ)
        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""
        if not name or not email or len(password) < 6:
            return redirect(start_response, with_msg("/", "Dados invalidos"))

        with get_conn() as conn:
            exists = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
            if exists:
                return redirect(start_response, with_msg("/", "Email ja cadastrado"))
            conn.execute(
                "INSERT INTO users(name,email,password_hash,created_at) VALUES(?,?,?,?)",
                (name, email, hash_password(password), int(time.time())),
            )
        return redirect(start_response, with_msg("/", "Conta criada com sucesso"))

    if path == "/login" and method == "POST":
        data = parse_form(environ)
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""
        with get_conn() as conn:
            user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if not user or not verify_password(password, user["password_hash"]):
            return redirect(start_response, with_msg("/", "Credenciais invalidas"))

        expires_at = int(time.time()) + SESSION_TTL
        token = sign_session(user["id"], expires_at)
        cookie = cookies.SimpleCookie()
        cookie["session"] = token
        cookie["session"]["path"] = "/"
        cookie["session"]["httponly"] = True
        cookie["session"]["samesite"] = "Lax"
        cookie["session"]["max-age"] = str(SESSION_TTL)
        if environ.get("wsgi.url_scheme") == "https":
            cookie["session"]["secure"] = True
        return redirect(start_response, "/dashboard", headers=[("Set-Cookie", cookie.output(header="").strip())])

    if path == "/logout" and method == "POST":
        cookie = cookies.SimpleCookie()
        cookie["session"] = ""
        cookie["session"]["path"] = "/"
        cookie["session"]["samesite"] = "Lax"
        cookie["session"]["expires"] = "Thu, 01 Jan 1970 00:00:00 GMT"
        return redirect(start_response, with_msg("/", "Sessao encerrada"), headers=[("Set-Cookie", cookie.output(header="").strip())])

    if path == "/dashboard" and method == "GET":
        if not user_id:
            return redirect(start_response, with_msg("/", "Faca login primeiro"))
        with get_conn() as conn:
            user = conn.execute("SELECT id,name,email FROM users WHERE id=?", (user_id,)).fetchone()
            if not user:
                return redirect(start_response, with_msg("/", "Sessao invalida"))
            projects = conn.execute(
                "SELECT id,name,area,status,description FROM projects WHERE user_id=? ORDER BY id DESC",
                (user_id,),
            ).fetchall()
        return response(start_response, dashboard_page(user, projects, flash))

    if path == "/projects" and method == "POST":
        if not user_id:
            return redirect(start_response, with_msg("/", "Faca login primeiro"))
        data = parse_form(environ)
        name = (data.get("name") or "").strip()
        area = (data.get("area") or "").strip()
        description = (data.get("description") or "").strip()
        if not name or not area:
            return redirect(start_response, with_msg("/dashboard", "Preencha nome e area"))
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO projects(user_id,name,area,status,description,created_at) VALUES(?,?,?,?,?,?)",
                (user_id, name, area, "Planejamento", description, int(time.time())),
            )
        return redirect(start_response, with_msg("/dashboard", "Projeto criado"))

    if path.startswith("/projects/") and method == "POST":
        if not user_id:
            return redirect(start_response, with_msg("/", "Faca login primeiro"))

        parts = path.strip("/").split("/")
        if len(parts) != 3:
            return response(start_response, "Rota invalida", status="404 Not Found")

        _, project_id, action = parts
        if not project_id.isdigit():
            return response(start_response, "ID invalido", status="400 Bad Request")

        with get_conn() as conn:
            project = conn.execute(
                "SELECT id FROM projects WHERE id=? AND user_id=?", (int(project_id), user_id)
            ).fetchone()
            if not project:
                return redirect(start_response, with_msg("/dashboard", "Projeto nao encontrado"))

            if action == "status":
                data = parse_form(environ)
                status_value = (data.get("status") or "").strip()
                allowed = {"Planejamento", "Em execucao", "Concluido"}
                if status_value not in allowed:
                    return redirect(start_response, with_msg("/dashboard", "Status invalido"))
                conn.execute(
                    "UPDATE projects SET status=? WHERE id=? AND user_id=?",
                    (status_value, int(project_id), user_id),
                )
                return redirect(start_response, with_msg("/dashboard", "Status atualizado"))

            if action == "delete":
                conn.execute("DELETE FROM projects WHERE id=? AND user_id=?", (int(project_id), user_id))
                return redirect(start_response, with_msg("/dashboard", "Projeto excluido"))

        return response(start_response, "Acao invalida", status="404 Not Found")

    return response(start_response, "Pagina nao encontrada", status="404 Not Found")


if __name__ == "__main__":
    init_db()
    host = "127.0.0.1"
    port = 8080
    print(f"Servidor rodando em http://{host}:{port}")
    with make_server(host, port, app) as server:
        server.serve_forever()
