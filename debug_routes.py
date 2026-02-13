#!/usr/bin/env python
"""
Script de debug das rotas
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import app

print("=" * 60)
print("ROTAS REGISTRADAS NA APLICAÇÃO")
print("=" * 60)

for route in app.routes:
    print(f"\n{route}")
    if hasattr(route, 'path'):
        print(f"  Path: {route.path}")
    if hasattr(route, 'methods'):
        print(f"  Methods: {route.methods}")
    if hasattr(route, 'tags'):
        print(f"  Tags: {route.tags}")

print("\n" + "=" * 60)
print(f"Total de rotas: {len(app.routes)}")
print("=" * 60)
