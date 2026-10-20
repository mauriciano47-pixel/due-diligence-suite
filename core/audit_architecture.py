# -*- coding: utf-8 -*-
"""
V-GUARD Due Diligence Suite v2.4.0 - Módulo de Arquitectura, Deuda Técnica & Calidad de Código (Pilar 4)
Analiza: SLOC, God Files (>800 líneas), Complejidad Ciclomática Estricta (V(G)<=20),
Contratos en Runtime, Fuzzing, Chaos, Mutation y Cobertura de Tests.
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

    has_typescript = (root / "tsconfig.json").exists() or any((root / d / "tsconfig.json").exists() for d in ["ataraxia", "crypto-frontend", "frontend", "client", "src", "web"])
    has_linter = any((root / f).exists() for f in [".eslintrc", ".eslintrc.json", ".eslintrc.js", "eslint.config.js", ".hintrc"]) or any(
        (root / d / f).exists() for d in ["ataraxia", "crypto-frontend", "frontend", "client", "src", "web"] for f in [".eslintrc", ".eslintrc.json", ".eslintrc.js", "eslint.config.js", ".hintrc"]
    )
    has_tests_dir = (root / "tests").exists() or (root / "test").exists() or (root / "__tests__").exists() or (root / "ataraxia" / "tests").exists()

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]

        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in CODE_EXT_MAP:
                continue

            full_path = Path(dirpath) / fname
            if fname in ["package-lock.json", "yarn.lock", "pnpm-lock.yaml", "sbom.cdx.json"] or ".min." in fname:
                continue

            rel_path = full_path.relative_to(root).as_posix()
            total_files += 1
            lang = CODE_EXT_MAP[ext]
            language_breakdown[lang] = language_breakdown.get(lang, 0) + 1

            if "test" in fname.lower() or "spec" in fname.lower():
                test_files_count += 1

            try:
                content = full_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            lines = content.splitlines()
            line_count = len(lines)
            total_lines += line_count

            code_lines = [l for l in lines if l.strip()]
            total_code_lines += len(code_lines)

            if line_count > GOD_FILE_THRESHOLD and ext in [".py", ".js", ".jsx", ".ts", ".tsx"]:
                god_files.append({"file": rel_path, "lines": line_count})
                findings.append({
                    "severity": "MEDIUM",
                    "title": f"Archivo sobredimensionado (God File): {fname} ({line_count} líneas)",
                    "detail": f"Supera el umbral de {GOD_FILE_THRESHOLD} líneas. En Due Diligence de M&A se recomienda modularizar para facilitar el mantenimiento y reducir deuda técnica.",
                    "file": rel_path
                })

            for idx, line in enumerate(lines, 1):
                clean_l = line.strip()
                if re.search(r"\b(TODO|FIXME|HACK|XXX|BUG)\b", clean_l):
                    todos_count += 1
                    if todos_count <= 8:
                        findings.append({
                            "severity": "LOW",
                            "title": f"Deuda técnica detectada ({clean_l[:35]}...)",
                            "detail": f"Marcador de pendiente en línea {idx}",
                            "file": rel_path,
                            "line": idx
                        })

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

    score = 100

    # 1. Auditoría Dinámica de Pruebas Automatizadas
    from audit_test_runner import audit_test_runner
    test_run_res = audit_test_runner(project_path)
    for t_find in test_run_res.get("findings", []):
        findings.append(t_find)

    if test_run_res.get("executed"):
        if test_run_res.get("failed_count", 0) > 0:
            score -= 30
        elif test_run_res.get("pass_rate") == 100.0:
            if test_run_res.get("total_tests", 0) < 5:
                score -= 6
                findings.append({
                    "severity": "LOW",
                    "title": "Suite de tests reducida (<5 aserciones)",
                    "detail": f"Solo se ejecutan {test_run_res.get('total_tests')} pruebas automáticas. Recomendado expandir cobertura.",
                    "file": "tests/"
                })
    else:
        if test_files_count == 0 and not has_tests_dir:
            score -= 28
            findings.append({
                "severity": "HIGH",
                "title": "Ausencia total de pruebas automatizadas (Zero-Test Codebase)",
                "detail": "No se detectaron archivos de prueba ni runner ejecutable. En Tech Due Diligence institucional, un comprador descuenta entre 20% y 40% de la valoración por el riesgo crítico de regresiones.",
                "file": "tests/"
            })
        else:
            score -= 12
            findings.append({
                "severity": "MEDIUM",
                "title": "Archivos de prueba detectados pero sin runner dinámico verificado",
                "detail": "Existen archivos de test pero no se ejecutó una suite automatizada vía 'npm test' o 'pytest'.",
                "file": "package.json"
            })

    # 2. Penalización por monolitos (God Files >800 líneas)
    god_file_penalty = min(35, len(god_files) * 8)
    score -= god_file_penalty

    # 3. Penalización por deuda técnica acumulada (TODOs/FIXMEs)
    if todos_count > 15:
        score -= 10
    elif todos_count > 5:
        score -= 5

    # 4. Debug calls residuales (console.log)
    if debug_calls_count > 15:
        score -= 8
    elif debug_calls_count > 5:
        score -= 4

    # 5. Tipado estricto vs JS dinámico
    has_js_ts = any(l in language_breakdown for l in ["JavaScript", "TypeScript", "React JSX", "React TSX"])
    if has_js_ts and not has_typescript:
        score -= 10
        findings.append({
            "severity": "MEDIUM",
            "title": "Código en JavaScript dinámico sin TypeScript estricto",
            "detail": "Falta de tipado estático en tiempo de compilación. En auditorías de gran escala incrementa la tasa de errores en runtime.",
            "file": "tsconfig.json"
        })

    # 6. Auditoría de Complejidad Ciclomática Estricta (McCabe AST / Big Tech Standard V(G) <= 20)
    from audit_complexity import audit_complexity
    comp_res = audit_complexity(project_path)
    comp_metrics = comp_res.get("metrics", {})
    max_complexity = comp_metrics.get("max_complexity", 1)
    avg_complexity = comp_metrics.get("avg_complexity", 1.0)
    critical_funcs_count = comp_metrics.get("critical_functions_count", 0)

    for c_find in comp_res.get("findings", []):
        findings.append(c_find)

    if max_complexity > 30:
        score -= 12
    elif max_complexity > 20:
        score -= 6

    # 7. Auditoría de Contratos en Runtime (Zero-Trust I/O)
    from audit_bigtech_gates import audit_runtime_contracts
    contract_res = audit_runtime_contracts(project_path)
    has_runtime_contracts = contract_res.get("has_runtime_contracts", False)
    for ct_find in contract_res.get("findings", []):
        findings.append(ct_find)

    # 8. Bonificación por Ingeniería de Testing de Grado Aeroespacial/Institucional
    # REGLA DE GRANDES LIGAS: Ningún proyecto con funciones críticas V(G) > 20 puede obtener 100/100 en Arquitectura.
    if critical_funcs_count == 0:
        if (test_run_res.get("coverage_pct") or 0) >= 90.0:
            score += 4
        if test_run_res.get("has_pbt_fuzzing"):
            score += 3
        if test_run_res.get("has_chaos"):
            score += 3
        if test_run_res.get("has_mutation"):
            score += 3
        if has_runtime_contracts:
            score += 2
    else:
        score = min(score, max(70, 94 - (critical_funcs_count * 2)))

    score = max(0, min(100, score))
    status = "EXCELLENT" if score >= 85 else ("GOOD" if score >= 70 else ("WARNING" if score >= 50 else "DANGER"))

    cov_str = f" Cobertura: {test_run_res['coverage_pct']}%." if test_run_res.get("coverage_pct") else ""
    e2e_str = f" E2E Playwright: {test_run_res['e2e_files_count']} specs." if test_run_res.get("has_e2e") else ""
    elite_tags = []
    if test_run_res.get("has_pbt_fuzzing"):
        elite_tags.append("PBT-Fuzzing")
    if test_run_res.get("has_chaos"):
        elite_tags.append("Chaos")
    if test_run_res.get("has_mutation"):
        elite_tags.append("Mutation-100%")
    if has_runtime_contracts:
        elite_tags.append("Runtime-Contracts")
    if critical_funcs_count == 0:
        elite_tags.append("McCabe-Clean")
    elite_str = f" Élite: [{', '.join(elite_tags)}]." if elite_tags else ""

    return {
        "pilar": "Arquitectura & Deuda Técnica",
        "score": score,
        "status": status,
        "summary": f"{total_files} archivos ({total_code_lines:,} SLOC). {len(god_files)} monolitos. V(G) máx: {max_complexity} ({critical_funcs_count} críticas). Tests: {test_run_res.get('total_tests', test_files_count)} (Pass: {test_run_res.get('pass_rate', 0)}%).{cov_str}{e2e_str}{elite_str}",
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
            "has_linter": has_linter,
            "max_complexity": max_complexity,
            "avg_complexity": avg_complexity,
            "critical_functions_count": critical_funcs_count,
            "has_runtime_contracts": has_runtime_contracts,
            "test_run": test_run_res
        }
    }
