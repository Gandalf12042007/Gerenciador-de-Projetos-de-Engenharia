import io
import os
import tempfile
import unittest
from urllib.parse import urlencode

import app


class WsgiClient:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app
        self.cookie = ""

    def request(self, method, path, form=None):
        body = urlencode(form or {}).encode("utf-8")
        environ = {
            "REQUEST_METHOD": method,
            "PATH_INFO": path,
            "QUERY_STRING": "",
            "CONTENT_TYPE": "application/x-www-form-urlencoded",
            "CONTENT_LENGTH": str(len(body)),
            "wsgi.input": io.BytesIO(body),
            "wsgi.url_scheme": "http",
            "HTTP_COOKIE": self.cookie,
        }

        captured = {"status": "", "headers": []}

        def start_response(status, headers):
            captured["status"] = status
            captured["headers"] = headers

        body_bytes = b"".join(self.wsgi_app(environ, start_response))

        for header, value in captured["headers"]:
            if header.lower() == "set-cookie":
                self.cookie = value.split(";", 1)[0]

        return captured["status"], dict(captured["headers"]), body_bytes.decode("utf-8", errors="ignore")


class AppTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        app.DB_PATH = os.path.join(self.tmp.name, "test.db")
        app.init_db()
        self.client = WsgiClient(app.app)

    def tearDown(self):
        self.tmp.cleanup()

    def test_health_endpoint(self):
        status, _, body = self.client.request("GET", "/health")
        self.assertTrue(status.startswith("200"))
        self.assertEqual(body, "ok")

    def test_register_login_and_dashboard_access(self):
        status, headers, _ = self.client.request(
            "POST",
            "/register",
            {"name": "Vicente", "email": "vicente@mail.com", "password": "123456"},
        )
        self.assertTrue(status.startswith("302"))
        self.assertIn("Location", headers)

        status, headers, _ = self.client.request(
            "POST", "/login", {"email": "vicente@mail.com", "password": "123456"}
        )
        self.assertTrue(status.startswith("302"))
        self.assertIn("Set-Cookie", headers)

        status, _, body = self.client.request("GET", "/dashboard")
        self.assertTrue(status.startswith("200"))
        self.assertIn("Painel de Projetos", body)

    def test_project_crud_flow(self):
        self.client.request(
            "POST",
            "/register",
            {"name": "User", "email": "u@mail.com", "password": "abcdef"},
        )
        self.client.request("POST", "/login", {"email": "u@mail.com", "password": "abcdef"})

        status, _, _ = self.client.request(
            "POST",
            "/projects",
            {"name": "Obra Centro", "area": "Estrutural", "description": "Teste"},
        )
        self.assertTrue(status.startswith("302"))

        with app.get_conn() as conn:
            project = conn.execute("SELECT id FROM projects WHERE name='Obra Centro'").fetchone()
        self.assertIsNotNone(project)

        pid = project["id"]
        status, _, _ = self.client.request("POST", f"/projects/{pid}/status", {"status": "Concluido"})
        self.assertTrue(status.startswith("302"))

        status, _, _ = self.client.request("POST", f"/projects/{pid}/delete")
        self.assertTrue(status.startswith("302"))

        with app.get_conn() as conn:
            project = conn.execute("SELECT id FROM projects WHERE id=?", (pid,)).fetchone()
        self.assertIsNone(project)


if __name__ == "__main__":
    unittest.main()
