# -*- coding: utf-8 -*-
"""
V-GUARD Due Diligence Suite - Módulo de Gobernanza, Git & Data Room (Pilar 5)
Analiza: Salud del repositorio Git, historial de commits, sincronización con Cerebros Obsidian, documentación técnica (README/Changelog) y preparación para inversores.
"""
import os
import subprocess
from pathlib import Path

OBSIDIAN_BASE_PATH = Path(r"C:\Users\mauro\OneDrive\Desktop\Cerebros_Obsidian")

def run_git(cmd_args, cwd):
    try:
        res = subprocess.run(
            ["git"] + cmd_args,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        if res.returncode == 0:
            return res.stdout.strip()
        return None
    except Exception:
        return None

def audit_governance(project_path: str, app_key: str = None) -> dict:
    root = Path(project_path)
    if not root.exists():
        return {
            "pilar": "Gobernanza & Data Room",
            "score": 0,
            "status": "ERROR",
            "findings": [{"severity": "CRITICAL", "title": "Ruta no encontrada", "detail": str(project_path)}],
            "metrics": {}
        }

    findings = []
    is_git_repo = (root / ".git").exists()
    branch = "N/A"
    last_commit_hash = "N/A"
    last_commit_date = "N/A"
    last_commit_msg = "N/A"
    dirty_files_count = 0
    has_readme = (root / "README.md").exists()
    has_changelog = any((root / f).exists() for f in ["CHANGELOG.md", "CHANGELOG", "HISTORY.md"])
    obsidian_cerebro_found = False
    obsidian_cerebro_name = "N/A"

    # 1. Comprobar Git
    if is_git_repo:
        b_res = run_git(["branch", "--show-current"], root)
        if b_res:
            branch = b_res

        commit_res = run_git(["log", "-1", "--format=%h|%an|%ad|%s", "--date=short"], root)
        if commit_res:
            parts = commit_res.split("|")
            if len(parts) >= 4:
                last_commit_hash = parts[0]
                last_commit_date = parts[2]
                last_commit_msg = parts[3]

        status_res = run_git(["status", "--porcelain"], root)
        if status_res:
            dirty_files = [l for l in status_res.splitlines() if l.strip()]
            dirty_files_count = len(dirty_files)
            if dirty_files_count > 15:
                findings.append({
                    "severity": "MEDIUM",
                    "title": f"Árbol de trabajo con múltiples modificaciones sin commitear ({dirty_files_count} archivos)",
                    "detail": "Para una Due Diligence formal, el árbol de Git debe estar limpio y sincronizado con origin/main."
                })
            else:
                findings.append({
                    "severity": "LOW",
                    "title": f"Árbol de trabajo activo ({dirty_files_count} archivos modificados)",
                    "detail": "Modificaciones menores pendientes de checkpoint."
                })
        else:
            findings.append({
                "severity": "LOW",
                "title": "Working tree limpio en Git",
                "detail": "El repositorio se encuentra 100% commiteado sin cambios pendientes."
            })
    else:
        findings.append({
            "severity": "HIGH",
            "title": "El proyecto no tiene repositorio Git inicializado (.git)",
            "detail": "El control de versiones es un requisito básico e innegociable en cualquier auditoría de adquisición o inversión."
        })

    # 2. Comprobar documentación
    if has_readme:
        findings.append({
            "severity": "LOW",
            "title": "Documentación técnica README.md presente",
            "detail": "Existe documentación de arquitectura e instrucciones de despliegue."
        })
    else:
        findings.append({
            "severity": "MEDIUM",
            "title": "Falta README.md descriptivo",
            "detail": "Se recomienda documentar el propósito del proyecto, stack técnico y guía de despliegue."
        })

    # 3. Comprobar sincronización con Cerebros Obsidian
    if OBSIDIAN_BASE_PATH.exists():
        app_name_lower = root.name.lower().replace("-", "").replace("_", "").replace(" ", "")
        for d in OBSIDIAN_BASE_PATH.iterdir():
            if d.is_dir() and d.name.startswith("cerebro_"):
                clean_name = d.name.replace("cerebro_", "").replace("-", "").replace("_", "")
                if clean_name in app_name_lower or app_name_lower in clean_name or (app_key and app_key.lower() in clean_name):
                    obsidian_cerebro_found = True
                    obsidian_cerebro_name = d.name
                    break

    if obsidian_cerebro_found:
        findings.append({
            "severity": "LOW",
            "title": f"Bóveda Obsidian SSOT vinculada ({obsidian_cerebro_name})",
            "detail": f"El proyecto cuenta con gemelo digital de documentación y MOCs en Obsidian."
        })
    else:
        findings.append({
            "severity": "MEDIUM",
            "title": "Sin bóveda Obsidian identificada",
            "detail": "No se localizó carpeta cerebro_* coincidente en Cerebros_Obsidian."
        })

    # Cálculo del Score (Base 100)
    score = 70
    if is_git_repo:
        score += 15
    if has_readme:
        score += 5
    if obsidian_cerebro_found:
        score += 10
    if dirty_files_count > 20:
        score -= 10

    score = max(0, min(100, score))
    status = "EXCELLENT" if score >= 85 else ("GOOD" if score >= 70 else ("WARNING" if score >= 50 else "DANGER"))

    return {
        "pilar": "Gobernanza & Data Room",
        "score": score,
        "status": status,
        "summary": f"Git: {'✅ Activo' if is_git_repo else '❌ Inactivo'} ({branch} • {last_commit_hash}). Obsidian: {'✅ ' + obsidian_cerebro_name if obsidian_cerebro_found else '⚠️ No vinculado'}. README: {'✅' if has_readme else '❌'}.",
        "findings": findings,
        "metrics": {
            "is_git_repo": is_git_repo,
            "branch": branch,
            "last_commit_hash": last_commit_hash,
            "last_commit_date": last_commit_date,
            "last_commit_msg": last_commit_msg,
            "dirty_files_count": dirty_files_count,
            "has_readme": has_readme,
            "has_changelog": has_changelog,
            "obsidian_cerebro_found": obsidian_cerebro_found,
            "obsidian_cerebro_name": obsidian_cerebro_name
        }
    }
