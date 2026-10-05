# -*- coding: utf-8 -*-
"""
V-GUARD Due Diligence Suite - Módulo de Auditoría de Ciberseguridad & Zero-Leakage (Pilar 1)
Analiza: Fuga de secretos, claves hardcodeadas, .gitignore, patrones inseguros (OWASP) y configuraciones de producción.
"""
import os
import re
from pathlib import Path

# Extensiones auditables para código y configuración
CODE_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".html", ".htm", ".json",
    ".yaml", ".yml", ".env", ".toml", ".ini", ".cfg", ".sh", ".ps1"
}

# Carpetas a ignorar en el escaneo profundo
IGNORE_DIRS = {
    "node_modules", ".git", ".venv", "venv", "__pycache__", "dist",
    "build", ".expo", ".next", ".cache", "coverage", ".docusaurus", "scratch"
}

# Patrones de secretos conocidos
SECRET_PATTERNS = [
    (r"AIza[0-9A-Za-z-_]{35}", "Gemini / Google Cloud API Key expuesta", "CRITICAL"),
    (r"sk-[a-zA-Z0-9]{32,64}", "OpenAI API Key expuesta", "CRITICAL"),
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token expuesto", "CRITICAL"),
    (r"github_pat_[a-zA-Z0-9_]{82}", "GitHub Fine-Grained PAT expuesto", "CRITICAL"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID expuesta", "HIGH"),
    (r"-----BEGIN (RSA|EC|OPENSSH|PGP|PRIVATE) KEY-----", "Clave privada criptográfica embebida en código", "CRITICAL"),
    (r"ey[A-Za-z0-9_-]{10,}\.ey[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}", "JSON Web Token (JWT) hardcodeado", "HIGH"),
    (r"(?:postgres|mysql|mongodb|redis):\/\/[a-zA-Z0-9_]+:[a-zA-Z0-9_!@#$%^&*()+=]+@[a-zA-Z0-9._-]+:[0-9]+", "Cadena de conexión de BD con credenciales", "CRITICAL"),
    (r"railway_[a-zA-Z0-9_-]{24,}", "Railway Token expuesto", "CRITICAL"),
    (r"vercel_[a-zA-Z0-9_-]{24,}", "Vercel Token expuesto", "CRITICAL"),
]

# Patrones de código peligroso (OWASP)
DANGEROUS_PATTERNS = [
    (r"\beval\s*\(", "Uso de eval() (Riesgo crítico de ejecución arbitraria de código)", "HIGH", (".js", ".jsx", ".ts", ".tsx", ".py")),
    (r"dangerouslySetInnerHTML\s*=", "Uso de dangerouslySetInnerHTML (Riesgo XSS)", "MEDIUM", (".jsx", ".tsx")),
    (r"\.innerHTML\s*=(?!\s*[\"'])", "Asignación directa a innerHTML con variables dinámicas (Riesgo XSS)", "MEDIUM", (".js", ".ts")),
    (r"cursor\.execute\s*\(\s*f[\"']", "Consulta SQL dinámica con f-string (Riesgo SQL Injection)", "CRITICAL", (".py",)),
    (r"cursor\.execute\s*\(\s*[\"'].*%\s*\(?", "Consulta SQL dinámica con interpolación % (Riesgo SQL Injection)", "CRITICAL", (".py",)),
    (r"DEBUG\s*=\s*True", "DEBUG = True detectado (Debe ser False en entornos de producción)", "HIGH", (".py",)),
    (r"CORS_ALLOW_ALL_ORIGINS\s*=\s*True", "CORS abierto indiscriminadamente (CORS_ALLOW_ALL_ORIGINS = True)", "HIGH", (".py",)),
]

def audit_security(project_path: str) -> dict:
    root = Path(project_path)
    if not root.exists():
        return {
            "pilar": "Ciberseguridad & Zero-Leakage",
            "score": 0,
            "status": "ERROR",
            "findings": [{"severity": "CRITICAL", "title": "Ruta de proyecto no encontrada", "detail": str(project_path)}],
            "metrics": {}
        }

    findings = []
    scanned_files_count = 0
    clean_files_count = 0

    # 1. Verificación de .gitignore y archivos sensibles
    gitignore_path = root / ".gitignore"
    has_gitignore = gitignore_path.exists()
    gitignore_content = ""
    if has_gitignore:
        try:
            gitignore_content = gitignore_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            pass
    else:
        findings.append({
            "severity": "HIGH",
            "title": "Falta archivo .gitignore en la raíz",
            "detail": "El repositorio no posee un .gitignore, aumentando el riesgo de subir credenciales o dependencias.",
            "file": ".gitignore"
        })

    # Verificar presencia de archivos de secretos
    sensitive_file_names = [".env", ".env.local", ".env.production", "serviceAccountKey.json", "credentials.json", "id_rsa"]
    for sf in sensitive_file_names:
        sf_path = root / sf
        if sf_path.exists():
            # Verificar si está cubierto en gitignore
            if not has_gitignore or sf not in gitignore_content:
                findings.append({
                    "severity": "CRITICAL",
                    "title": f"Archivo sensible expuesto sin protección en .gitignore: {sf}",
                    "detail": f"El archivo {sf} existe pero no está explícitamente ignorado en .gitignore.",
                    "file": sf
                })
            else:
                findings.append({
                    "severity": "LOW",
                    "title": f"Archivo sensible {sf} protegido localmente",
                    "detail": f"El archivo existe localmente y está listado en .gitignore (buena práctica).",
                    "file": sf
                })

    # 2. Escaneo profundo de archivos
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]

        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in CODE_EXTENSIONS:
                continue

            full_path = Path(dirpath) / fname
            # Omitir archivos lock y minificados
            if fname in ["package-lock.json", "yarn.lock", "pnpm-lock.yaml"] or ".min." in fname:
                continue

            scanned_files_count += 1
            rel_path = full_path.relative_to(root).as_posix()

            try:
                content = full_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            file_has_issue = False
            lines = content.splitlines()

            # Escaneo de secretos
            for pattern, title, severity in SECRET_PATTERNS:
                # No alertar si es un archivo .env.example o plantilla
                if "example" in fname.lower() or "template" in fname.lower():
                    continue

                for line_idx, line in enumerate(lines, 1):
                    # Ignorar comentarios explicativos o regexes
                    if line.strip().startswith("//") or line.strip().startswith("#") or line.strip().startswith("/*"):
                        if "example" in line.lower() or "your_" in line.lower() or "fake" in line.lower():
                            continue

                    matches = re.finditer(pattern, line)
                    for m in matches:
                        secret_val = m.group(0)
                        # Omitir placeholders obvios
                        if any(p in secret_val.lower() for p in ["your", "placeholder", "demo", "xxx", "000000"]):
                            continue

                        file_has_issue = True
                        masked_val = secret_val[:6] + "..." + secret_val[-4:] if len(secret_val) > 10 else "***"
                        findings.append({
                            "severity": severity,
                            "title": title,
                            "detail": f"Detectado valor sospechoso `{masked_val}` en línea {line_idx}",
                            "file": rel_path,
                            "line": line_idx
                        })

            # Escaneo de patrones de código peligroso
            for pattern, title, severity, target_exts in DANGEROUS_PATTERNS:
                if ext not in target_exts:
                    continue

                for line_idx, line in enumerate(lines, 1):
                    # Ignorar comentarios
                    stripped = line.strip()
                    if stripped.startswith("//") or stripped.startswith("#") or stripped.startswith("/*"):
                        continue

                    # Si es DEBUG = True, omitir si tiene comentario explicitando test o override
                    if "DEBUG" in pattern and "test" in rel_path.lower():
                        continue

                    if re.search(pattern, line):
                        file_has_issue = True
                        findings.append({
                            "severity": severity,
                            "title": title,
                            "detail": f"Código observado: `{stripped[:80]}` (Línea {line_idx})",
                            "file": rel_path,
                            "line": line_idx
                        })

            if not file_has_issue:
                clean_files_count += 1

    # Cálculo del Score (Base 100)
    score = 100
    crit_count = sum(1 for f in findings if f["severity"] == "CRITICAL")
    high_count = sum(1 for f in findings if f["severity"] == "HIGH")
    med_count = sum(1 for f in findings if f["severity"] == "MEDIUM")
    low_count = sum(1 for f in findings if f["severity"] == "LOW")

    score -= (crit_count * 25)
    score -= (high_count * 12)
    score -= (med_count * 5)
    score -= (low_count * 1)
    score = max(0, min(100, score))

    status = "EXCELLENT" if score >= 90 else ("GOOD" if score >= 75 else ("WARNING" if score >= 50 else "DANGER"))

    return {
        "pilar": "Ciberseguridad & Zero-Leakage",
        "score": score,
        "status": status,
        "summary": f"{crit_count} críticos, {high_count} altos, {med_count} medios en {scanned_files_count} archivos inspeccionados.",
        "findings": findings,
        "metrics": {
            "scanned_files": scanned_files_count,
            "clean_files": clean_files_count,
            "critical_issues": crit_count,
            "high_issues": high_count,
            "medium_issues": med_count,
            "low_issues": low_count
        }
    }
