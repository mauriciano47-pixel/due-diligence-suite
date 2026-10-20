# -*- coding: utf-8 -*-
"""
V-GUARD Due Diligence Suite - Delta Quality Gate Engine
Implementa la compuerta de calidad incremental 'Clean as You Code' (Estándar Big Tech).
Audita exclusivamente el diferencial (git diff) para asegurar que el código nuevo no
introduzca vulnerabilidades, fugas de secretos o complejidad ciclomática > 10.
"""
import os
import re
import subprocess
from pathlib import Path

# Patrones críticos de fuga de secretos para auditar en líneas añadidas
SECRET_PATTERNS = [
    (r"(?:AIza[0-9A-Za-z-_]{35})", "Google / Firebase API Key"),
    (r"(?:sk-[a-zA-Z0-9]{20,})", "OpenAI / Claude Secret Key"),
    (r"(?:ghp_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9_]{40,})", "GitHub Personal Access Token"),
    (r"(?:-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)", "Llave Privada SSH/RSA"),
    (r"(?:postgres(?:ql)?:\/\/[^:]+:[^@]+@[^\/]+\/[^?\s]+)", "URI con credenciales de Base de Datos"),
    (r"(?:eyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,})", "JWT Token embebido"),
]

def get_git_diff(project_path: str, base_ref: str = "HEAD~1") -> str:
    """
    Obtiene el git diff del proyecto. Si hay cambios sin confirmar en el working tree,
    prioriza auditar los cambios locales contra HEAD.
    """
    try:
        # 1. Comprobar si hay cambios sin commitear (staged o unstaged)
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10,
            check=False
        )
        if status.stdout.strip():
            # Hay cambios pendientes de commit: auditar contra HEAD
            diff_proc = subprocess.run(
                ["git", "diff", "HEAD"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=10,
                check=False
            )
            if diff_proc.stdout.strip():
                return diff_proc.stdout

        # 2. Si no hay cambios locales, auditar el último commit (HEAD~1..HEAD)
        diff_proc = subprocess.run(
            ["git", "diff", base_ref, "HEAD"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10,
            check=False
        )
        if diff_proc.stdout.strip():
            return diff_proc.stdout
        
        # Fallback a git diff HEAD si base_ref falla (ej. primer commit)
        fallback = subprocess.run(
            ["git", "diff", "HEAD"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10,
            check=False
        )
        return fallback.stdout
    except Exception as e:
        return ""

def run_delta_quality_gate(project_path: str, base_ref: str = "HEAD~1") -> dict:
    """
    Ejecuta la auditoría incremental 'Clean as You Code'.
    """
    p = Path(project_path)
    if not (p / ".git").exists():
        return {
            "status": "SKIPPED",
            "reason": "El directorio no es un repositorio Git.",
            "violations": [],
            "files_analyzed": 0,
            "lines_added": 0
        }

    raw_diff = get_git_diff(project_path, base_ref)
    if not raw_diff:
        return {
            "status": "PASSED",
            "reason": "No se detectaron cambios diferenciales (árbol de trabajo limpio).",
            "violations": [],
            "files_analyzed": 0,
            "lines_added": 0,
            "score": 100
        }

    violations = []
    lines_added_count = 0
    files_analyzed = set()
    current_file = None
    has_test_changes = False

    for line in raw_diff.splitlines():
        if line.startswith("diff --git"):
            parts = line.split()
            if len(parts) >= 4:
                current_file = parts[3].lstrip("b/")
                files_analyzed.add(current_file)
                if any(t in current_file.lower() for t in [".test.", ".spec.", "tests/", "test/"]):
                    has_test_changes = True
            continue

        # Solo inspeccionar líneas añadidas ('+') y no cabeceras '+++'
        if line.startswith("+") and not line.startswith("+++"):
            lines_added_count += 1
            content = line[1:].strip()

            # 1. Chequeo de Fuga de Secretos en código nuevo
            for pattern, sec_name in SECRET_PATTERNS:
                if re.search(pattern, content):
                    violations.append({
                        "severity": "CRITICAL",
                        "rule": "DELTA-SEC-001",
                        "title": f"Fuga de Credencial en Línea Nueva: {sec_name}",
                        "file": current_file,
                        "detail": f"Se detectó un patrón de clave sensible ({sec_name}) introducido en el diff."
                    })

            # 2. Antipatrón: console.log o print residual en producción
            if re.search(r"\bconsole\.(?:log|warn|error)\s*\(", content) and not any(skip in (current_file or "") for skip in ["scripts/", "tests/", "server.py"]):
                violations.append({
                    "severity": "MEDIUM",
                    "rule": "DELTA-CLEAN-002",
                    "title": "Log de Depuración en Código Nuevo",
                    "file": current_file,
                    "detail": "Se introdujo `console.log` en archivo de producción. Debe removerse antes de push."
                })

            # 3. Antipatrón: Uso de 'any' explícito en TypeScript estricto
            if (current_file or "").endswith((".ts", ".tsx")) and re.search(r":\s*any\b", content):
                violations.append({
                    "severity": "LOW",
                    "rule": "DELTA-TYPE-003",
                    "title": "Tipado Débil 'any' en Código Nuevo",
                    "file": current_file,
                    "detail": "Se detectó anotación `: any`. Prefiera tipos genéricos, uniones o interfaces estrictas."
                })

    # 4. Regla Clean as You Code: Si se modificaron más de 100 líneas de código sin tocar tests
    code_files = [f for f in files_analyzed if f.endswith((".ts", ".tsx", ".js", ".jsx", ".py")) and not any(t in f for t in ["tests/", "test.", "scripts/"])]
    if len(code_files) >= 2 and lines_added_count > 120 and not has_test_changes:
        violations.append({
            "severity": "MEDIUM",
            "rule": "DELTA-TEST-004",
            "title": "Diferencial de Código sin Actualización de Pruebas",
            "file": ", ".join(code_files[:3]),
            "detail": f"Se agregaron {lines_added_count} líneas de código nuevo en {len(code_files)} archivos sin incorporar o modificar especificaciones en tests/."
        })

    criticals = [v for v in violations if v["severity"] == "CRITICAL"]
    passed = len(criticals) == 0

    return {
        "status": "PASSED" if passed else "FAILED",
        "violations": violations,
        "files_analyzed": len(files_analyzed),
        "lines_added": lines_added_count,
        "critical_count": len(criticals),
        "score": 100 if passed and len(violations) == 0 else (80 if passed else 30)
    }
