#!/usr/bin/env python3
import requests
import json

resp = requests.post("http://localhost:8000/api/auth/login", json={
    "email": "vicentedesouza762@gmail.com",
    "senha": "Admin@2026"
})

print(f"Status: {resp.status_code}")
print(f"Response: {json.dumps(resp.json(), indent=2)}")
