# -*- coding: utf-8 -*-
"""
Genera el dataset estático de auditoría de la flota para despliegue en la nube (GitHub Pages).
"""
import sys
import json
from pathlib import Path

# Configurar encoding UTF-8 en Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
CORE_DIR = CURRENT_DIR / "core"
sys.path.insert(0, str(CORE_DIR))

from scanner import scan_project
from apps_registry import get_apps_list

def generate():
    apps = get_apps_list()
    results = []
    print("🚀 Generando dataset de Due Diligence de la flota...")
    for a in apps:
        if a["exists"]:
            print(f" -> Auditando {a['name']} ({a['path']})...")
            res = scan_project(a["path"], app_key=a["key"], app_name=a["name"])
            results.append(res)
        else:
            print(f" -> Omitiendo {a['name']} (no disponible)")

    out_file = CURRENT_DIR / "web" / "fleet_data.json"
    out_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Archivo generado: {out_file} ({len(results)} aplicaciones auditadas)")

if __name__ == "__main__":
    generate()
