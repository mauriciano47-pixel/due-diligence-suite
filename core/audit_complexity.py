# -*- coding: utf-8 -*-
"""
V-GUARD Due Diligence Suite - Módulo de Complejidad Ciclomática (McCabe AST)
Auditoría de mantenibilidad, densidad lógica y caminos independientes por función.
Estándar IEEE 1061 / SonarQube para evaluación de transferibilidad y deuda técnica.
"""
import os
import re
import ast
from pathlib import Path

IGNORE_DIRS = {
    "node_modules", ".git", ".venv", "venv", "__pycache__", "dist",
    "build", ".expo", ".next", ".cache", "coverage", "scratch", "android"
}

def calculate_python_complexity(file_path: Path) -> list:
    """Calcula complejidad ciclomática exacta en Python usando AST nativo."""
    results = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(content, filename=str(file_path))
    except Exception:
        return results

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            complexity = 1  # Base V(G) = 1
            for child in ast.walk(node):
                if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                    complexity += 1
                elif isinstance(child, ast.ExceptHandler):
                    complexity += 1
                elif isinstance(child, ast.BoolOp):
                    # Cada operador booleano (and, or) suma caminos
                    complexity += max(1, len(child.values) - 1)
                elif isinstance(child, ast.IfExp):  # Ternario
                    complexity += 1

            results.append({
                "function": node.name,
                "line": node.lineno,
                "complexity": complexity,
                "file": file_path.name
            })
    return results

def calculate_js_complexity(file_path: Path) -> list:
    """Calcula complejidad ciclomática heurística en JS/TS por bloques funcionales."""
    results = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return results

    lines = content.splitlines()
    # Buscar firmas de función en JS/TS
    func_pattern = re.compile(r'(?:function\s+([a-zA-Z0-9_$]+)|(?:const|let|var)\s+([a-zA-Z0-9_$]+)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[a-zA-Z0-9_$]+)\s*=>|([a-zA-Z0-9_$]+)\s*\([^)]*\)\s*\{)')

    current_func = None
    func_complexity = 1
    func_line = 1
    brace_depth = 0
    func_depth = 0

    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
            continue

        match = func_pattern.search(line)
        if match and not current_func:
            name = match.group(1) or match.group(2) or match.group(3) or "anonymous"
            if name not in ["if", "for", "while", "switch", "catch"]:
                current_func = name
                func_complexity = 1
                func_line = idx
                func_depth = brace_depth

        if current_func:
            # Puntos de decisión
            decisions = len(re.findall(r'\b(if|else\s+if|while|for|catch|case)\b', line))
            decisions += line.count("&&")
            decisions += line.count("||")
            decisions += line.count("??")
            decisions += len(re.findall(r'\?[^:]+:', line))  # Ternario
            func_complexity += decisions

        # Conteo de llaves
        brace_depth += line.count("{") - line.count("}")

        if current_func and brace_depth <= func_depth and "}" in line:
            results.append({
                "function": current_func,
                "line": func_line,
                "complexity": func_complexity,
                "file": file_path.name
            })
            current_func = None

    return results

def audit_complexity(project_path: str) -> dict:
    root = Path(project_path)
    if not root.exists():
        return {
            "pilar": "Complejidad Ciclomática & Mantenibilidad",
            "score": 0,
            "status": "ERROR",
            "findings": [{"severity": "CRITICAL", "title": "Ruta no encontrada", "detail": str(project_path)}],
            "metrics": {}
        }

    findings = []
    all_functions = []

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]

        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ".min." in fname or "test" in fname.lower() or "spec" in fname.lower():
                continue

            fpath = Path(dirpath) / fname
            rel_path = fpath.relative_to(root).as_posix()

            if ext == ".py":
                funcs = calculate_python_complexity(fpath)
                for f in funcs:
                    f["rel_path"] = rel_path
                all_functions.extend(funcs)
            elif ext in [".js", ".jsx", ".ts", ".tsx"]:
                funcs = calculate_js_complexity(fpath)
                for f in funcs:
                    f["rel_path"] = rel_path
                all_functions.extend(funcs)

    if not all_functions:
        return {
            "pilar": "Complejidad Ciclomática & Mantenibilidad",
            "score": 100,
            "status": "EXCELLENT",
            "summary": "No se detectaron funciones con ramas complejas. Código lineal y modular.",
            "findings": [],
            "metrics": {"total_functions": 0, "max_complexity": 1, "avg_complexity": 1.0}
        }

    # Ordenar por complejidad descendente
    all_functions.sort(key=lambda x: x["complexity"], reverse=True)
    max_complexity = all_functions[0]["complexity"]
    avg_complexity = round(sum(f["complexity"] for f in all_functions) / len(all_functions), 1)

    critical_funcs = [f for f in all_functions if f["complexity"] > 20]
    high_funcs = [f for f in all_functions if 12 < f["complexity"] <= 20]

    for f in critical_funcs[:5]:  # Reportar top 5
        findings.append({
            "severity": "HIGH",
            "title": f"Complejidad Ciclomática Crítica en `{f['function']}()` (V(G) = {f['complexity']})",
            "detail": f"La función `{f['function']}` supera el umbral máximo de 20 caminos independientes. Requiere desacople y modularización para asegurar testeabilidad y evitar regresiones.",
            "file": f["rel_path"],
            "line": f["line"]
        })

    for f in high_funcs[:3]:
        findings.append({
            "severity": "LOW",
            "title": f"Complejidad Lógica Moderada en `{f['function']}()` (V(G) = {f['complexity']})",
            "detail": f"Función con {f['complexity']} caminos de decisión lógica. Mantenible pero candidata a simplificación.",
            "file": f["rel_path"],
            "line": f["line"]
        })

    # Puntuación basada en pico máximo y promedio
    score = 100
    if max_complexity > 30:
        score -= 30
    elif max_complexity > 20:
        score -= 15
    elif max_complexity > 12:
        score -= 5

    if avg_complexity > 8:
        score -= 15
    elif avg_complexity > 5:
        score -= 5

    score = max(0, min(100, score))
    status = "EXCELLENT" if score >= 85 else ("GOOD" if score >= 70 else ("WARNING" if score >= 50 else "DANGER"))
    summary = f"Analizadas {len(all_functions)} funciones. Complejidad Máxima: V(G)={max_complexity} ({all_functions[0]['function']}). Promedio: V(G)={avg_complexity}."

    return {
        "pilar": "Complejidad Ciclomática & Mantenibilidad",
        "score": score,
        "status": status,
        "summary": summary,
        "findings": findings,
        "metrics": {
            "total_functions": len(all_functions),
            "max_complexity": max_complexity,
            "max_func_name": all_functions[0]["function"],
            "avg_complexity": avg_complexity,
            "critical_functions_count": len(critical_funcs),
            "high_functions_count": len(high_funcs)
        }
    }
