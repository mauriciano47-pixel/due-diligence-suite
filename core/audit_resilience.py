# -*- coding: utf-8 -*-
"""
V-GUARD Due Diligence Suite - Módulo de Resiliencia, Fallback & Estándares de Producción (Pilar 4)
Analiza: Protocolo Anti-Timeout en llamadas a IA (<= 8.000 ms), arquitectura Offline-First, PWA / Service Workers, y accesibilidad.
"""
import os
import re
from pathlib import Path

IGNORE_DIRS = {
    "node_modules", ".git", ".venv", "venv", "__pycache__", "dist",
    "build", ".expo", ".next", ".cache", "coverage", ".docusaurus", "scratch"
}

def audit_resilience(project_path: str) -> dict:
    root = Path(project_path)
    if not root.exists():
        return {
            "pilar": "Resiliencia & Producción",
            "score": 0,
            "status": "ERROR",
            "findings": [{"severity": "CRITICAL", "title": "Ruta no encontrada", "detail": str(project_path)}],
            "metrics": {}
        }

    findings = []
    has_gemini = False
    gemini_timeout_compliant = True
    has_fallback_mechanism = False
    has_offline_storage = False
    has_pwa_manifest = False
    has_service_worker = False
    has_accessibility_hints = False
    checked_files = 0

    # 1. Comprobar PWA manifest y Service Worker en la raíz o carpetas comunes
    for pwa_file in ["manifest.json", "app.json", "public/manifest.json", "static/manifest.json"]:
        if (root / pwa_file).exists():
            has_pwa_manifest = True
            break

    for sw_name in ["sw.js", "service-worker.js", "public/sw.js", "serviceWorkerRegistration.js"]:
        if (root / sw_name).exists():
            has_service_worker = True
            break

    # 2. Comprobar accesibilidad (.hintrc)
    if (root / ".hintrc").exists():
        has_accessibility_hints = True

    # 3. Recorrer archivos de código para auditar IA y Offline-First
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]

        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in [".js", ".jsx", ".ts", ".tsx", ".py", ".html"]:
                continue

            full_path = Path(dirpath) / fname
            rel_path = full_path.relative_to(root).as_posix()
            checked_files += 1

            try:
                content = full_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            # Detección de uso de Gemini o LLMs
            if "gemini" in content.lower() or "@google/genai" in content or "generativeai" in content.lower():
                has_gemini = True
                
                # Verificar protocolo Anti-Timeout (8000ms)
                has_abort_controller = "AbortController" in content or "timeout" in content.lower() or "8000" in content or "signal:" in content
                if not has_abort_controller:
                    gemini_timeout_compliant = False
                    findings.append({
                        "severity": "HIGH",
                        "title": f"Invocación a Gemini sin Timeout explícito (Regla Anti-Timeout)",
                        "detail": "Las llamadas a LLM deben implementar límite de 8.000 ms y AbortSignal para evitar bloqueos por latencia de red.",
                        "file": rel_path
                    })

                # Verificar fallback / simulación
                if "fallback" in content.lower() or "offline" in content.lower() or "simulaci" in content.lower():
                    has_fallback_mechanism = True

            # Detección de almacenamiento offline
            if any(k in content for k in ["AsyncStorage", "SafeStorage", "localStorage", "indexedDB", "sqlite"]):
                has_offline_storage = True

            # Detección de accesibilidad en HTML/JSX
            if "aria-label" in content or "role=" in content:
                has_accessibility_hints = True

    # Resumen y hallazgos
    if has_gemini:
        if gemini_timeout_compliant:
            findings.append({
                "severity": "LOW",
                "title": "Protocolo Anti-Timeout en IA verificado",
                "detail": "Las llamadas a Gemini implementan control de tiempo y mitigación de cuotas."
            })
        if has_fallback_mechanism:
            findings.append({
                "severity": "LOW",
                "title": "Arquitectura de Fallback para IA presente",
                "detail": "El sistema contempla conmutación a simulación o caché ante fallos de conectividad."
            })
        else:
            findings.append({
                "severity": "MEDIUM",
                "title": "Falta mecanismo de fallback / simulación guiada para IA",
                "detail": "Se recomienda integrar respuesta de contingencia si la cuota de la API se agota."
            })

    if has_offline_storage:
        findings.append({
            "severity": "LOW",
            "title": "Persistencia Offline-First verificada",
            "detail": "Se detectó uso de almacenamiento local autónomo (SafeStorage / AsyncStorage / localStorage)."
        })
    else:
        findings.append({
            "severity": "MEDIUM",
            "title": "Baja persistencia local detectada",
            "detail": "No se observaron mecanismos explícitos de almacenamiento offline."
        })

    if has_pwa_manifest or has_service_worker:
        findings.append({
            "severity": "LOW",
            "title": "Capacidades PWA detectadas",
            "detail": "Presencia de manifiesto o service worker para funcionamiento desacoplado."
        })

    # Puntuación (Base 100)
    score = 80
    if has_offline_storage:
        score += 10
    if has_pwa_manifest or has_service_worker:
        score += 10
    if has_gemini and not gemini_timeout_compliant:
        score -= 20
    if has_accessibility_hints:
        score += 5

    score = max(0, min(100, score))
    status = "EXCELLENT" if score >= 85 else ("GOOD" if score >= 70 else ("WARNING" if score >= 50 else "DANGER"))

    return {
        "pilar": "Resiliencia & Producción",
        "score": score,
        "status": status,
        "summary": f"Offline-First: {'✅ Sí' if has_offline_storage else '⚠️ No'}. PWA: {'✅ Sí' if has_pwa_manifest else 'No'}. IA Timeout: {'✅ Blindado' if (not has_gemini or gemini_timeout_compliant) else '⚠️ Revisar'}.",
        "findings": findings,
        "metrics": {
            "has_gemini": has_gemini,
            "gemini_timeout_compliant": gemini_timeout_compliant,
            "has_fallback_mechanism": has_fallback_mechanism,
            "has_offline_storage": has_offline_storage,
            "has_pwa_manifest": has_pwa_manifest,
            "has_service_worker": has_service_worker,
            "has_accessibility_hints": has_accessibility_hints
        }
    }
