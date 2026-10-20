# -*- coding: utf-8 -*-
"""
V-GUARD Due Diligence Suite v2.4.0 - Módulo de Gobernanza, Git Hooks & Data Room (Pilar 8)
Analiza: Salud del repositorio Git, historial de commits, Shift-Left Pre-Push Gate,
sincronización con Cerebros Obsidian y preparación para inversores.
"""
import subprocess
from pathlib import Path
from audit_git_forensics import audit_git_forensics

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
    git_root = root if (root / ".git").exists() else (root / "ataraxia" if (root / "ataraxia" / ".git").exists() else root)
    is_git_repo = (git_root / ".git").exists()
    branch = "N/A"
    last_commit_hash = "N/A"
    last_commit_date = "N/A"
    last_commit_msg = "N/A"
    dirty_files_count = 0
    has_readme = (root / "README.md").exists() or (root / "ataraxia" / "README.md").exists()
    has_changelog = any((root / f).exists() for f in ["CHANGELOG.md", "CHANGELOG", "HISTORY.md"])
    obsidian_cerebro_found = False
    obsidian_cerebro_name = "N/A"

    forensics = audit_git_forensics(str(git_root))
    forensics_metrics = forensics.get("metrics", {})
    bus_factor = forensics_metrics.get("bus_factor", 1)
    concentration_pct = forensics_metrics.get("concentration_pct", 100.0)
    primary_author = forensics_metrics.get("primary_author", "N/A")
    total_commits = forensics_metrics.get("total_commits", 0)

    for f_find in forensics.get("findings", []):
        findings.append(f_find)

    if is_git_repo:
        b_res = run_git(["branch", "--show-current"], git_root)
        if b_res:
            branch = b_res

        commit_res = run_git(["log", "-1", "--format=%h|%an|%ad|%s", "--date=short"], git_root)
        if commit_res:
            parts = commit_res.split("|")
            if len(parts) >= 4:
                last_commit_hash = parts[0]
                last_commit_date = parts[2]
                last_commit_msg = parts[3]

        status_res = run_git(["status", "--porcelain"], git_root)
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
                "title": "Working tree limpio en Git",
                "detail": "El repositorio se encuentra 100% commiteado sin cambios pendientes."
            })
    else:
        findings.append({
            "severity": "HIGH",
            "title": "El proyecto no tiene repositorio Git inicializado (.git)",
            "detail": "El control de versiones es un requisito básico e innegociable en cualquier auditoría de adquisición o inversión."
        })

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
            "detail": "El proyecto cuenta con gemelo digital de documentación y MOCs en Obsidian."
        })
    else:
        findings.append({
            "severity": "MEDIUM",
            "title": "Sin bóveda Obsidian identificada",
            "detail": "No se localizó carpeta cerebro_* coincidente en Cerebros_Obsidian."
        })

    # Auditoría de Git Pre-Push Gate (Shift-Left Big Tech Standard)
    from audit_bigtech_gates import audit_git_hooks
    hook_res = audit_git_hooks(project_path)
    has_shift_left_hook = hook_res.get("has_shift_left_hook", False)
    for h_find in hook_res.get("findings", []):
        findings.append(h_find)

    score = 65
    if is_git_repo:
        score += 15
    if has_readme:
        score += 5
    if obsidian_cerebro_found:
        score += 10
    if forensics_metrics.get("turnkey_ready") or has_shift_left_hook:
        score += 5
    if dirty_files_count > 20:
        score -= 10

    score = max(0, min(100, score))
    status = "EXCELLENT" if score >= 85 else ("GOOD" if score >= 70 else ("WARNING" if score >= 50 else "DANGER"))

    return {
        "pilar": "Gobernanza & Data Room",
        "score": score,
        "status": status,
        "summary": f"Git: {'✅ Activo' if is_git_repo else '❌ Inactivo'} ({branch} • {last_commit_hash}). Pre-Push Gate: {'✅' if has_shift_left_hook else '⚠️'}. Obsidian: {'✅ ' + obsidian_cerebro_name if obsidian_cerebro_found else '⚠️ No vinculado'}.",
        "findings": findings,
        "metrics": {
            "is_git_repo": is_git_repo,
            "branch": branch,
            "last_commit_hash": last_commit_hash,
            "last_commit_date": last_commit_date,
            "last_commit_msg": last_commit_msg,
            "total_commits": total_commits,
            "bus_factor": bus_factor,
            "primary_author": primary_author,
            "concentration_pct": concentration_pct,
            "dirty_files_count": dirty_files_count,
            "has_readme": has_readme,
            "has_changelog": has_changelog,
            "has_shift_left_hook": has_shift_left_hook,
            "obsidian_cerebro_found": obsidian_cerebro_found,
            "obsidian_cerebro_name": obsidian_cerebro_name
        }
    }
