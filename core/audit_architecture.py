# -*- coding: utf-8 -*-
"""
V-GUARD Due Diligence Suite - Módulo de Arquitectura, Deuda Técnica & Calidad de Código (Pilar 3)
Analiza: SLOC, distribución por lenguajes, God Files (>800 líneas), deuda técnica (TODOs/FIXMEs), código residual de depuración y cobertura de tests.
"""
import os
import re
from pathlib import Path

CODE_EXT_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "React JSX",
    ".ts": "TypeScript",
    ".tsx": "React TSX",
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".sh": "Shell",
    ".ps1": "PowerShell",
    ".sql": "SQL"
}

IGNORE_DIRS = {
    "node_modules", ".git", ".venv", "venv", "__pycache__", "dist",
    "build", ".expo", ".next", ".cache", "coverage", "scratch"
}

GOD_FILE_THRESHOLD = 800

def audit_architecture(project_path: str) -> dict:
    root = Path(project_path)
    if not root.exists():
        return {
            "pilar": "Arquitectura & Deuda Técnica",
            "score": 0,
            "status": "ERROR",
            "findings": [{"severity": "CRITICAL", "title": "Ruta no encontrada", "detail": str(project_path)}],
            "metrics": {}
        }

    findings = []
    total_files = 0
    total_lines = 0
    total_code_lines = 0
    language_breakdown = {}
    god_files = []
    todos_count = 0
    debug_calls_count = 0
    test_files_count = 0

    has_typescript = (root / "tsconfig.json").exists()
    has_linter = any((root / f).exists() for f in [".eslintrc", ".eslintrc.json", ".eslintrc.js", "eslint.config.js", ".hintrc"])
    has_tests_dir = (root / "tests").exists() or (root / "test").exists() or (root / "__tests__").exists()

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]

        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in CODE_EXT_MAP:
                continue

            full_path = Path(dirpath) / fname
            if fname in ["package-lock.json", "yarn.lock", "pnpm-lock.yaml"] or ".min." in fname:
                continue

            rel_path = full_path.relative_to(root).as_posix()
            total_files += 1
            lang = CODE_EXT_MAP[ext]
            language_breakdown[lang] = language_breakdown.get(lang, 0) + 1

            # Chequeo de tests
            if "test" in fname.lower() or "spec" in fname.lower():
                test_files_count += 1

            try:
                content = full_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            lines = content.splitlines()
            line_count = len(lines)
            total_lines += line_count

            # Contar líneas reales de código (no vacías)
            code_lines = [l for l in lines if l.strip()]
            total_code_lines += len(code_lines)

            # Detectar God Files (>800 líneas)
            if line_count > GOD_FILE_THRESHOLD and ext in [".py", ".js", ".jsx", ".ts", ".tsx"]:
                god_files.append({"file": rel_path, "lines": line_count})
                findings.append({
                    "severity": "MEDIUM",
                    "title": f"Archivo sobredimensionado (God File): {fname} ({line_count} líneas)",
                    "detail": f"Supera el umbral de {GOD_FILE_THRESHOLD} líneas. En Due Diligence de M&A se recomienda modularizar para facilitar el mantenimiento y reducir deuda técnica.",
                    "file": rel_path
                })

            # Detectar deuda técnica (TODO, FIXME, HACK) y console.log
            for idx, line in enumerate(lines, 1):
                clean_l = line.strip()
                if re.search(r"\b(TODO|FIXME|HACK|XXX|BUG)\b", clean_l):
                    todos_count += 1
                    if todos_count <= 8:  # Reportar los primeros 8 para no saturar
                        findings.append({
                            "severity": "LOW",
                            "title": f"Deuda técnica detectada ({clean_l[:35]}...)",
                            "detail": f"Marcador de pendiente en línea {idx}",
                            "file": rel_path,
                            "line": idx
                        })

                # Debug calls en JS/TS
                if ext in [".js", ".jsx", ".ts", ".tsx"] and "test" not in fname.lower():
                    if re.search(r"\bconsole\.(log|debug|warn)\s*\(", clean_l):
                        debug_calls_count += 1
                        if debug_calls_count <= 5:
                            findings.append({
                                "severity": "LOW",
                                "title": "Llamada de depuración residual (console.log)",
                                "detail": f"Línea {idx}: `{clean_l[:60]}`",
                                "file": rel_path,
                                "line": idx
                            })

    # Resumen de tests
    if test_files_count == 0 and not has_tests_dir:
        findings.append({
            "severity": "MEDIUM",
            "title": "Ausencia de suite de pruebas unitarias automatizadas",
            "detail": "No se detectaron archivos de prueba (*.test.*, test_*.py). Una suite de tests formal incrementa significativamente la valoración en Tech Due Diligence.",
            "file": "tests/"
        })

    # Cálculo del Score (Base 100)
    score = 100
    score -= len(god_files) * 6
    if todos_count > 10:
        score -= 5
    elif todos_count > 20:
        score -= 10
    if debug_calls_count > 20:
        score -= 5
    if test_files_count == 0 and not has_tests_dir:
        score -= 10
    if has_typescript:
        score += 5 # Bonificación por tipado estricto

    score = max(0, min(100, score))
    status = "EXCELLENT" if score >= 85 else ("GOOD" if score >= 70 else ("WARNING" if score >= 50 else "DANGER"))

    return {
        "pilar": "Arquitectura & Deuda Técnica",
        "score": score,
        "status": status,
        "summary": f"{total_files} archivos ({total_code_lines:,} SLOC). {len(god_files)} archivos >{GOD_FILE_THRESHOLD} líneas. {todos_count} marcadores TODO/FIXME. {test_files_count} archivos de test.",
        "findings": findings,
        "metrics": {
            "total_files": total_files,
            "total_lines": total_lines,
            "total_code_lines": total_code_lines,
            "languages": language_breakdown,
            "god_files_count": len(god_files),
            "god_files": god_files[:5],
            "todos_count": todos_count,
            "debug_calls_count": debug_calls_count,
            "test_files_count": test_files_count,
            "has_typescript": has_typescript,
            "has_linter": has_linter
        }
    }
