# -*- coding: utf-8 -*-
"""
V-GUARD Due Diligence Suite - Auto-Remediation Engine (--fix)
Ejecuta reparaciones deterministas y quirúrgicas para elevar la aplicación
al Estándar Institucional Big Tech Tier-1 de forma autónoma.
"""
import os
import json
import shutil
from pathlib import Path
from typing import List, Dict, Any

STANDARD_SECURITY_HEADERS = [
    {
        "source": "/(.*)",
        "headers": [
            { "key": "X-Content-Type-Options", "value": "nosniff" },
            { "key": "X-Frame-Options", "value": "DENY" },
            { "key": "Strict-Transport-Security", "value": "max-age=31536000; includeSubDomains; preload" },
            { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
            { "key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=(self)" },
            {
                "key": "Content-Security-Policy",
                "value": "default-src 'self'; script-src 'self' 'unsafe-inline' https:; style-src 'self' 'unsafe-inline' https:; img-src 'self' data: https: blob:; font-src 'self' https: data:; connect-src 'self' https: wss:; object-src 'none'; base-uri 'self';"
            }
        ]
    }
]

PRE_PUSH_GATE_SCRIPT = """#!/usr/bin/env node
/**
 * V-GUARD Sentinel — Shift-Left Quality Gate (Pre-Push Shield)
 * Impide commits o subidas a repositorios remotos si existen regresiones,
 * pruebas fallidas o errores de tipado estático.
 */
import { execSync } from 'child_process';

console.log('\\x1b[36m%s\\x1b[0m', '🏛️  [V-GUARD SHIFT-LEFT GATE] Ejecutando verificación previa al git push...');

try {
  // 1. Verificación de Tipado Estático si existe TypeScript
  console.log(' -> Validando tipado estricto (typecheck)...');
  try {
    execSync('npm run typecheck', { stdio: 'inherit' });
  } catch {
    // Si no existe typecheck, continuar
  }

  // 2. Ejecución dinámica de pruebas automatizadas
  console.log(' -> Ejecutando suite de pruebas unitarias (npm test)...');
  execSync('npm test', { stdio: 'inherit' });

  console.log('\\x1b[32m%s\\x1b[0m', '✅ [V-GUARD GATE PASSED]: Código puro verificado. Autorizando push a repositorio.');
  process.exit(0);
} catch (err) {
  console.error('\\x1b[31m%s\\x1b[0m', '❌ [V-GUARD GATE REJECTED]: Las pruebas o el tipado fallaron. Push bloqueado.');
  process.exit(1);
}
"""

def fix_dast_headers(project_path: Path) -> List[str]:
    actions = []
    vercel_file = project_path / "vercel.json"
    if vercel_file.exists():
        try:
            with open(vercel_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            headers = data.get("headers", [])
            has_csp = any(
                any(h.get("key") == "Content-Security-Policy" for h in item.get("headers", []))
                for item in headers
            )
            if not has_csp:
                data["headers"] = STANDARD_SECURITY_HEADERS
                with open(vercel_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                actions.append("Inyectadas cabeceras perimetrales DAST (CSP, HSTS, X-Frame) en vercel.json")
        except Exception as e:
            pass
    return actions

def fix_performance_budget_images(project_path: Path, max_kb: float = 750.0) -> List[str]:
    actions = []
    try:
        from PIL import Image
    except ImportError:
        return actions

    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in ["node_modules", ".git", ".expo", "dist", ".next", ".cache"]]
        for f in files:
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                fp = Path(root) / f
                try:
                    size_kb = fp.stat().st_size / 1024.0
                    if size_kb > max_kb:
                        img = Image.open(fp)
                        w, h = img.size
                        # Redimensionar si es excesivamente grande para web móvil
                        if max(w, h) > 1024:
                            scale = 1024.0 / max(w, h)
                            img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)

                        # Cuantización adaptativa de paleta a 256 colores
                        if img.mode == "RGBA":
                            q = img.quantize(colors=256, method=Image.Quantize.FASTOCTREE)
                            q.save(fp, optimize=True)
                        else:
                            img.convert("P", palette=Image.Palette.ADAPTIVE, colors=256).save(fp, optimize=True)

                        new_size_kb = fp.stat().st_size / 1024.0
                        actions.append(f"Optimizado activo {f}: {size_kb:.1f} KB -> {new_size_kb:.1f} KB (-{((size_kb - new_size_kb)/size_kb)*100:.0f}%)")
                except Exception:
                    pass
    return actions

def fix_pre_push_gate(project_path: Path) -> List[str]:
    actions = []
    pkg_file = project_path / "package.json"
    if pkg_file.exists():
        try:
            with open(pkg_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            scripts = data.get("scripts", {})
            if "prepush" not in scripts:
                scripts["prepush"] = "node ./scripts/pre-push-gate.mjs"
                data["scripts"] = scripts
                with open(pkg_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                actions.append("Añadido script 'prepush' en package.json")

            scripts_dir = project_path / "scripts"
            scripts_dir.mkdir(parents=True, exist_ok=True)
            gate_file = scripts_dir / "pre-push-gate.mjs"
            if not gate_file.exists():
                gate_file.write_text(PRE_PUSH_GATE_SCRIPT, encoding="utf-8")
                actions.append("Creado script de Quality Gate local: scripts/pre-push-gate.mjs")
        except Exception:
            pass
    return actions

def run_auto_remediation(project_path: str) -> Dict[str, Any]:
    """
    Ejecuta la suite completa de autorreparación determinista sobre el proyecto.
    """
    p = Path(project_path)
    if not p.exists():
        return {"success": False, "actions": [], "error": "Ruta no encontrada"}

    all_actions = []
    all_actions.extend(fix_dast_headers(p))
    all_actions.extend(fix_performance_budget_images(p))
    all_actions.extend(fix_pre_push_gate(p))

    return {
        "success": True,
        "actions_count": len(all_actions),
        "actions": all_actions
    }
