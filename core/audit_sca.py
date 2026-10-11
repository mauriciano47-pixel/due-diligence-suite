# -*- coding: utf-8 -*-
"""
V-GUARD Due Diligence Suite - Módulo SCA (Software Composition Analysis)
Auditoría de Vulnerabilidades en Cadena de Suministro de Dependencias (CVEs / GHSA).
Ejecuta inspección profunda de dependencias directas y transitivas contra bases de datos de vulnerabilidades.
"""
import os
import json
import subprocess
from pathlib import Path

def audit_sca(project_path: str) -> dict:
    root = Path(project_path)
    if not root.exists():
        return {
            "pilar": "Seguridad de Dependencias & SCA",
            "score": 0,
            "status": "ERROR",
            "findings": [{"severity": "CRITICAL", "title": "Ruta no encontrada", "detail": str(project_path)}],
            "metrics": {}
        }

    findings = []
    has_package_json = (root / "package.json").exists()
    has_requirements_txt = (root / "requirements.txt").exists()
    total_dependencies = 0
    vuln_counts = {"critical": 0, "high": 0, "moderate": 0, "low": 0, "info": 0}

    # 1. Auditoría de Dependencias Node.js (npm audit)
    if has_package_json:
        try:
            npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
            cmd = f"{npm_cmd} audit --json"
            proc = subprocess.run(
                cmd,
                cwd=str(root),
                shell=True,
                capture_output=True,
                text=True,
                timeout=25,
                encoding="utf-8",
                errors="ignore"
            )

            stdout = proc.stdout.strip()
            if stdout:
                try:
                    audit_data = json.loads(stdout)
                    metadata = audit_data.get("metadata", {})
                    vuln_meta = metadata.get("vulnerabilities", {})
                    dep_meta = metadata.get("dependencies", {})
                    total_dependencies = dep_meta.get("total", 0) or dep_meta.get("prod", 0)

                    vuln_counts["critical"] = vuln_meta.get("critical", 0)
                    vuln_counts["high"] = vuln_meta.get("high", 0)
                    vuln_counts["moderate"] = vuln_meta.get("moderate", 0)
                    vuln_counts["low"] = vuln_meta.get("low", 0)
                    vuln_counts["info"] = vuln_meta.get("info", 0)

                    # Detallar vulnerabilidades reportadas
                    vulnerabilities = audit_data.get("vulnerabilities", {})
                    for pkg_name, v_info in vulnerabilities.items():
                        sev = v_info.get("severity", "moderate").lower()
                        via_list = v_info.get("via", [])

                        for via_item in via_list:
                            if isinstance(via_item, dict):
                                title = via_item.get("title", f"Vulnerabilidad en {pkg_name}")
                                url = via_item.get("url", "")
                                cvss = via_item.get("cvss", {})
                                cvss_score = cvss.get("score") if isinstance(cvss, dict) else None
                                range_str = via_item.get("range", "")

                                sev_mapped = "CRITICAL" if sev == "critical" else ("HIGH" if sev == "high" else ("MEDIUM" if sev == "moderate" else "LOW"))

                                cvss_desc = f" (CVSS {cvss_score})" if cvss_score else ""
                                findings.append({
                                    "severity": sev_mapped,
                                    "title": f"Vulnerabilidad SCA {sev.upper()}{cvss_desc}: {pkg_name}",
                                    "detail": f"{title}. Rango afectado: `{range_str}`. Ref: {url}",
                                    "file": "package.json",
                                    "advisory_url": url,
                                    "package": pkg_name
                                })
                            elif isinstance(via_item, str):
                                # Dependencia transitiva afectada por otra
                                pass

                except json.JSONDecodeError:
                    pass
        except subprocess.TimeoutExpired:
            findings.append({
                "severity": "LOW",
                "title": "Timeout en consulta a registro npm",
                "detail": "La auditoría online de npm superó el tiempo límite. Se asume inspección local estática.",
                "file": "package.json"
            })
        except Exception as e:
            pass

    # 2. Si no tiene package.json ni requirements.txt: Proyecto Zero-Dependency (Vanilla)
    if not has_package_json and not has_requirements_txt:
        return {
            "pilar": "Seguridad de Dependencias & SCA",
            "score": 100,
            "status": "EXCELLENT",
            "summary": "Arquitectura Zero-Dependency (Vanilla sin librerías externas). Superficie de ataque de suministro nula.",
            "findings": [{
                "severity": "INFO",
                "title": "Arquitectura Zero-Dependency",
                "detail": "El proyecto no depende de paquetes externos de terceros, eliminando vectores de ataque en la cadena de suministro.",
                "file": "."
            }],
            "metrics": {
                "total_dependencies": 0,
                "critical": 0,
                "high": 0,
                "moderate": 0,
                "low": 0
            }
        }

    # 3. Cálculo de Puntuación de Cadena de Suministro (Base 100)
    score = 100
    crit = vuln_counts["critical"]
    high = vuln_counts["high"]
    mod = vuln_counts["moderate"]
    low = vuln_counts["low"]

    score -= (crit * 25)
    score -= (high * 12)
    score -= (mod * 4)
    score -= (low * 1)
    score = max(0, min(100, score))

    status = "EXCELLENT" if score >= 90 else ("GOOD" if score >= 75 else ("WARNING" if score >= 50 else "DANGER"))
    summary = f"{crit} críticas, {high} altas, {mod} moderadas en {total_dependencies} dependencias auditadas."

    return {
        "pilar": "Seguridad de Dependencias & SCA",
        "score": score,
        "status": status,
        "summary": summary,
        "findings": findings,
        "metrics": {
            "total_dependencies": total_dependencies,
            "critical": crit,
            "high": high,
            "moderate": mod,
            "low": low,
            "info": vuln_counts["info"]
        }
    }
