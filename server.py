# -*- coding: utf-8 -*-
"""
V-GUARD Due Diligence Suite - Servidor Web & API REST
Sirve la interfaz gráfica Cyber-Obsidian Royal y los endpoints de auditoría en tiempo real.
"""
import sys
import os
import json
import socket
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

# Configurar encoding UTF-8 en Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
CORE_DIR = CURRENT_DIR / "core"
WEB_DIR = CURRENT_DIR / "web"
sys.path.insert(0, str(CORE_DIR))

from scanner import scan_project
from apps_registry import get_apps_list, ECOSYSTEM_APPS
from due_diligence_cli import save_to_obsidian

PORT = 7770
HOST = "0.0.0.0"

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

class DueDiligenceHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def _send_json(self, status_code, data_obj):
        payload = json.dumps(data_obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/apps":
            apps = get_apps_list()
            self._send_json(200, apps)
        elif parsed.path == "/api/health":
            self._send_json(200, {"status": "ok", "service": "V-GUARD Due Diligence Hub"})
        else:
            # Servir archivos estáticos desde WEB_DIR
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        
        try:
            data = json.loads(body)
        except Exception:
            data = {}

        if parsed.path == "/api/audit":
            app_key = data.get("key")
            custom_path = data.get("path")
            apps = get_apps_list()
            
            target_path = None
            target_name = None
            
            if app_key:
                matched = next((a for a in apps if a["key"] == app_key), None)
                if matched and matched["exists"]:
                    target_path = matched["path"]
                    target_name = matched["name"]
            elif custom_path:
                p = Path(custom_path)
                if p.exists():
                    target_path = str(p.resolve())
                    target_name = p.name

            if not target_path:
                self._send_json(400, {"error": "Ruta o aplicación no válida o no encontrada"})
                return

            result = scan_project(target_path, app_key=app_key, app_name=target_name)
            self._send_json(200, result)

        elif parsed.path == "/api/audit-all":
            apps = get_apps_list()
            results = []
            for a in apps:
                if a["exists"]:
                    res = scan_project(a["path"], app_key=a["key"], app_name=a["name"])
                    results.append(res)
            self._send_json(200, results)

        elif parsed.path == "/api/save-obsidian":
            app_key = data.get("key", "custom")
            app_name = data.get("name", "Proyecto")
            markdown = data.get("markdown", "")
            
            if not markdown:
                self._send_json(400, {"error": "Contenido markdown vacío"})
                return

            try:
                saved_file = save_to_obsidian(app_key, markdown, app_name)
                self._send_json(200, {"success": True, "saved_path": saved_file})
            except Exception as e:
                self._send_json(500, {"error": str(e)})
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

def run_server():
    global PORT
    local_ip = get_local_ip()
    server = None
    
    # Intento de bind con auto-búsqueda del siguiente puerto si estuviera ocupado
    for p in range(PORT, PORT + 20):
        try:
            server = HTTPServer((HOST, p), DueDiligenceHandler)
            PORT = p
            break
        except OSError:
            continue

    if not server:
        print("❌ No se pudo enlazar ningún puerto disponible.")
        sys.exit(1)

    print("=" * 70)
    print(" 🏛️  V-GUARD DUE DILIGENCE SUITE — SERVIDOR LOCAL ACTIVO")
    print("=" * 70)
    print(f" 🌐 Dashboard Local : http://localhost:{PORT}")
    print(f" 📱 Build Wi-Fi     : http://{local_ip}:{PORT}")
    print("=" * 70)
    print(" Presiona Ctrl+C para detener el servidor.\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario.")
        server.server_close()

if __name__ == "__main__":
    run_server()
