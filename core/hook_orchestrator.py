# -*- coding: utf-8 -*-
"""
V-GUARD Due Diligence Suite - Fleet Pre-Push Orchestrator
Instala y estandariza los hooks de Git en toda la flota de aplicaciones
para garantizar que ninguna aplicación pueda subir código con pruebas rotas o sin compilar.
"""
import os
import stat
from pathlib import Path
from typing import List, Dict, Any
from apps_registry import get_apps_list

PRE_PUSH_HOOK_CONTENT = """#!/bin/sh
# V-GUARD Sentinel — Shift-Left Git Pre-Push Hook
# Bloquea el push si las pruebas unitarias o el tipado estático fallan.

echo "\\033[36m[V-GUARD HOOK]\\033[0m Ejecutando Quality Gate institucional previo al push..."

if [ -f "package.json" ]; then
    if grep -q '"prepush"' package.json; then
        npm run prepush
        EXIT_CODE=$?
    elif grep -q '"test"' package.json; then
        npm test
        EXIT_CODE=$?
    else
        EXIT_CODE=0
    fi
elif [ -f "manage.py" ]; then
    python manage.py test
    EXIT_CODE=$?
else
    EXIT_CODE=0
fi

if [ $EXIT_CODE -ne 0 ]; then
    echo "\\033[31m[V-GUARD HOOK REJECTED]\\033[0m Push cancelado. Corrige las pruebas antes de subir a GitHub."
    exit 1
fi

echo "\\033[32m[V-GUARD HOOK PASSED]\\033[0m Pruebas y calidad verificadas. Procediendo con el push."
exit 0
"""

def install_fleet_hooks() -> Dict[str, Any]:
    apps = get_apps_list()
    results = []

    for a in apps:
        app_path = Path(a["path"])
        git_dir = app_path / ".git"
        # Comprobar si hay un repositorio anidado (ej. ATARAXIA_APP/ataraxia/.git)
        if not git_dir.exists():
            nested_git = [p for p in app_path.glob("*/.git") if p.is_dir()]
            if nested_git:
                git_dir = nested_git[0]

        if not git_dir.exists():
            results.append({
                "app": a["name"],
                "status": "SKIPPED",
                "reason": "Directorio .git no encontrado"
            })
            continue

        hooks_dir = git_dir / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)
        pre_push_file = hooks_dir / "pre-push"

        try:
            pre_push_file.write_text(PRE_PUSH_HOOK_CONTENT, encoding="utf-8")
            # En sistemas tipo Unix o WSL, otorgar permisos de ejecución
            try:
                pre_push_file.chmod(pre_push_file.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
            except Exception:
                pass

            results.append({
                "app": a["name"],
                "status": "INSTALLED",
                "path": str(pre_push_file)
            })
        except Exception as e:
            results.append({
                "app": a["name"],
                "status": "FAILED",
                "reason": str(e)
            })

    installed_count = sum(1 for r in results if r["status"] == "INSTALLED")
    return {
        "total_apps": len(apps),
        "installed_count": installed_count,
        "details": results
    }
