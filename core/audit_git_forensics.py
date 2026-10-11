# -*- coding: utf-8 -*-
"""
V-GUARD Due Diligence Suite - Módulo Forense de Git & Key-Person Risk (Bus Factor)
Auditoría de concentración de autoría, historial de control de versiones y transferibilidad M&A (Turnkey Readiness).
"""
import os
import subprocess
from pathlib import Path

def audit_git_forensics(project_path: str) -> dict:
    root = Path(project_path)
    if not root.exists():
        return {
            "pilar": "Forense Git & Key-Person Risk",
            "score": 0,
            "status": "ERROR",
            "findings": [{"severity": "CRITICAL", "title": "Ruta no encontrada", "detail": str(project_path)}],
            "metrics": {}
        }

    findings = []
    git_dir = root / ".git"
    has_git = git_dir.exists()

    if not has_git:
        return {
            "pilar": "Forense Git & Key-Person Risk",
            "score": 30,
            "status": "DANGER",
            "summary": "Repositorio sin control de versiones Git. Riesgo crítico de trazabilidad e integridad del historial.",
            "findings": [{
                "severity": "HIGH",
                "title": "Ausencia de repositorio Git (.git)",
                "detail": "El proyecto no opera bajo control de versiones Git, impidiendo auditar autoría, ramas y rollbacks.",
                "file": "."
            }],
            "metrics": {"has_git": False, "bus_factor": 0}
        }

    # 1. Extraer autores y concentración de commits
    authors_data = []
    total_commits = 0
    try:
        proc = subprocess.run(
            "git shortlog -sn --all",
            cwd=str(root),
            shell=True,
            capture_output=True,
            text=True,
            timeout=8,
            encoding="utf-8",
            errors="ignore"
        )
        for line in proc.stdout.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                count = int(parts[0].strip())
                author_name = parts[1].strip()
                authors_data.append({"name": author_name, "commits": count})
                total_commits += count
    except Exception:
        pass

    # Si shortlog falló, intentar git rev-list
    if total_commits == 0:
        try:
            proc2 = subprocess.run(
                "git rev-list --count HEAD",
                cwd=str(root),
                shell=True,
                capture_output=True,
                text=True,
                timeout=6,
                encoding="utf-8",
                errors="ignore"
            )
            count_str = proc2.stdout.strip()
            if count_str.isdigit():
                total_commits = int(count_str)
                authors_data.append({"name": "Autor Principal", "commits": total_commits})
        except Exception:
            total_commits = 1
            authors_data.append({"name": "Autor", "commits": 1})

    primary_author = authors_data[0]["name"] if authors_data else "Desconocido"
    primary_commits = authors_data[0]["commits"] if authors_data else total_commits
    concentration_pct = round((primary_commits / max(1, total_commits)) * 100, 1)

    # 2. Calcular Bus Factor
    # Si el 85%+ de los commits pertenecen a 1 persona, Bus Factor = 1
    bus_factor = 1 if concentration_pct >= 85 else min(len(authors_data), 3)

    # 3. Evaluar Turnkey Readiness (Transferibilidad a un comprador en 48h)
    has_readme = (root / "README.md").exists()
    has_env_example = any((root / f).exists() for f in [".env.example", ".env.template", ".env.sample"])
    has_deploy_docs = (root / "DEPLOY.md").exists() or (root / "Procfile").exists() or (root / "Dockerfile").exists()
    has_package_json = (root / "package.json").exists()

    score = 100

    # Evaluación de Key-Person Risk
    if bus_factor == 1:
        if has_readme and (has_env_example or not (root / ".env").exists()):
            score -= 8
            findings.append({
                "severity": "LOW",
                "title": f"Key-Person Dependency (Bus Factor = 1 • {concentration_pct}%) Mitigada",
                "detail": f"El autor principal `{primary_author}` concentra el {concentration_pct}% de los commits ({primary_commits}/{total_commits}). Riesgo mitigado por documentación de arranque (README + variables de entorno reproducibles).",
                "file": ".git"
            })
        else:
            score -= 18
            findings.append({
                "severity": "MEDIUM",
                "title": f"Riesgo de Hombre Clave Activo (Bus Factor = 1 • {concentration_pct}%)",
                "detail": f"El activo depende en un {concentration_pct}% de `{primary_author}` y carece de .env.example o guía completa de transferencia. En M&A institucional esto exige retención obligatoria del fundador por 6-12 meses.",
                "file": ".git"
            })
    else:
        findings.append({
            "severity": "INFO",
            "title": f"Equipo Distribuido (Bus Factor = {bus_factor})",
            "detail": f"El código tiene historial colaborativo con {len(authors_data)} autores activos.",
            "file": ".git"
        })

    # Verificar si el repo tiene historial mínimo (>10 commits para madurez)
    if total_commits < 5:
        score -= 10
        findings.append({
            "severity": "LOW",
            "title": f"Historial Git incipiente ({total_commits} commits)",
            "detail": "El repositorio tiene muy pocos commits registrados para auditar madurez y patrones de regresión.",
            "file": ".git"
        })

    score = max(0, min(100, score))
    status = "EXCELLENT" if score >= 85 else ("GOOD" if score >= 70 else ("WARNING" if score >= 50 else "DANGER"))
    summary = f"Bus Factor = {bus_factor} ({concentration_pct}% concentración en {primary_author}). {total_commits} commits en historial."

    return {
        "pilar": "Forense Git & Key-Person Risk",
        "score": score,
        "status": status,
        "summary": summary,
        "findings": findings,
        "metrics": {
            "total_commits": total_commits,
            "authors_count": len(authors_data),
            "primary_author": primary_author,
            "primary_author_commits": primary_commits,
            "concentration_pct": concentration_pct,
            "bus_factor": bus_factor,
            "has_readme": has_readme,
            "has_env_example": has_env_example,
            "turnkey_ready": has_readme and has_env_example
        }
    }
