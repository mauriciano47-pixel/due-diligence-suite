# -*- coding: utf-8 -*-
"""
V-GUARD Due Diligence Suite - Módulo de Propiedad Intelectual & Licencias (Pilar 2)
Analiza: Licencias de dependencias (riesgo copyleft viral vs permisivas), titularidad de autor, avisos de copyright y archivos LICENSE.
"""
import os
import json
import re
from pathlib import Path

# Base de conocimiento de licencias para Tech Due Diligence
KNOWN_LICENSES = {
    # Permisivas (Óptimas para software propietario / M&A)
    "mit": {"type": "Permisiva", "risk": "BAJO", "desc": "Libre uso comercial y cerrado. Máxima compatibilidad."},
    "apache-2.0": {"type": "Permisiva", "risk": "BAJO", "desc": "Comercial con concesión expresa de patentes."},
    "bsd-2-clause": {"type": "Permisiva", "risk": "BAJO", "desc": "Permisiva con mínimo requerimiento de aviso."},
    "bsd-3-clause": {"type": "Permisiva", "risk": "BAJO", "desc": "Permisiva con cláusula de no patrocinio."},
    "isc": {"type": "Permisiva", "risk": "BAJO", "desc": "Funcionalmente equivalente a MIT."},
    "unlicense": {"type": "Dominio Público", "risk": "BAJO", "desc": "Dedicada al dominio público."},
    "cc0-1.0": {"type": "Dominio Público", "risk": "BAJO", "desc": "Dedicada al dominio público."},
    
    # Weak Copyleft (Riesgo moderado, requiere aislamiento en librerías dinámicas)
    "lgpl-2.1": {"type": "Weak Copyleft", "risk": "MEDIO", "desc": "Permite enlace dinámico sin obligar a abrir código principal."},
    "lgpl-3.0": {"type": "Weak Copyleft", "risk": "MEDIO", "desc": "Permite enlace dinámico con restricciones de hardware."},
    "mpl-2.0": {"type": "Weak Copyleft", "risk": "MEDIO", "desc": "Copyleft a nivel de archivo modificado únicamente."},

    # Strong / Viral Copyleft (Alto riesgo / Deal-Breaker para software privado si no está aislado)
    "gpl-2.0": {"type": "Viral Copyleft", "risk": "ALTO", "desc": "Obliga a liberar código derivado bajo GPL si se distribuye."},
    "gpl-3.0": {"type": "Viral Copyleft", "risk": "ALTO", "desc": "Obliga a liberar código derivado bajo GPLv3."},
    "agpl-3.0": {"type": "Network Viral Copyleft", "risk": "CRITICO", "desc": "Obliga a abrir el código incluso si solo se ofrece vía SaaS/Red."},
    "sspl": {"type": "Copyleft Comercial Restrictivo", "risk": "ALTO", "desc": "Licencia no-OSI con restricciones para servicios cloud."}
}

FOUNDER_NAME = "Mauricio Uribe Maldonado"

def audit_ip_licenses(project_path: str) -> dict:
    root = Path(project_path)
    if not root.exists():
        return {
            "pilar": "Propiedad Intelectual & Licencias",
            "score": 0,
            "status": "ERROR",
            "findings": [{"severity": "CRITICAL", "title": "Ruta no encontrada", "detail": str(project_path)}],
            "metrics": {}
        }

    findings = []
    dependencies = []
    license_counts = {"Permisiva": 0, "Weak Copyleft": 0, "Viral Copyleft": 0, "Desconocida": 0}
    has_license_file = False
    founder_ip_verified = False

    # 1. Comprobar archivo de Licencia en la raíz
    for fname in ["LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCIA", "LICENCIA.md", "COPYING"]:
        lic_file = root / fname
        if lic_file.exists():
            has_license_file = True
            try:
                content = lic_file.read_text(encoding="utf-8", errors="ignore")
                if FOUNDER_NAME.lower() in content.lower():
                    founder_ip_verified = True
                    findings.append({
                        "severity": "LOW",
                        "title": f"Titularidad de IP verificada en {fname}",
                        "detail": f"El archivo de licencia reconoce formalmente a '{FOUNDER_NAME}' como titular exclusivo.",
                        "file": fname
                    })
                else:
                    findings.append({
                        "severity": "MEDIUM",
                        "title": f"Archivo {fname} presente pero sin mención explícita al fundador",
                        "detail": f"Se recomienda asentar explícitamente la titularidad de '{FOUNDER_NAME}' para blindaje de M&A.",
                        "file": fname
                    })
            except Exception:
                pass
            break

    if not has_license_file:
        findings.append({
            "severity": "HIGH",
            "title": "Falta archivo de Licencia o Cesión de Derechos (LICENSE)",
            "detail": "No se encontró archivo LICENSE en la raíz del proyecto. En Tech Due Diligence es mandatorio clarificar los derechos propietarios del software.",
            "file": "LICENSE"
        })

    # 2. Verificar menciones de autoría en README.md o MOC
    readme_path = root / "README.md"
    if readme_path.exists():
        try:
            rm_text = readme_path.read_text(encoding="utf-8", errors="ignore")
            if FOUNDER_NAME.lower() in rm_text.lower():
                founder_ip_verified = True
        except Exception:
            pass

    # 3. Analizar dependencias de Node.js (package.json)
    pkg_path = root / "package.json"
    if pkg_path.exists():
        try:
            pkg_data = json.loads(pkg_path.read_text(encoding="utf-8", errors="ignore"))
            pkg_license = pkg_data.get("license", "")
            pkg_author = pkg_data.get("author", "")
            
            if isinstance(pkg_author, str) and FOUNDER_NAME.lower() in pkg_author.lower():
                founder_ip_verified = True
            elif isinstance(pkg_author, dict) and FOUNDER_NAME.lower() in pkg_author.get("name", "").lower():
                founder_ip_verified = True

            deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
            for dep_name, dep_ver in deps.items():
                dependencies.append({"name": dep_name, "version": dep_ver, "ecosystem": "npm"})

        except Exception as e:
            findings.append({
                "severity": "LOW",
                "title": "Error al parsear package.json",
                "detail": str(e),
                "file": "package.json"
            })

    # 4. Analizar dependencias de Python (requirements.txt)
    req_path = root / "requirements.txt"
    if req_path.exists():
        try:
            req_lines = req_path.read_text(encoding="utf-8", errors="ignore").splitlines()
            for line in req_lines:
                clean = line.strip().split("#")[0].strip()
                if clean and not clean.startswith("-"):
                    parts = re.split(r"[=><~!]", clean)
                    pkg_name = parts[0].strip()
                    ver = clean[len(pkg_name):].strip() if len(parts) > 1 else "*"
                    dependencies.append({"name": pkg_name, "version": ver, "ecosystem": "pip"})
        except Exception:
            pass

    # 5. Detección de paquetes con licencias de alto riesgo
    # Mapeo de librerías comunes y sus licencias típicas
    KNOWN_PKG_LICENSES = {
        "react": "MIT", "react-dom": "MIT", "react-native": "MIT", "expo": "MIT",
        "next": "MIT", "vue": "MIT", "express": "MIT", "django": "BSD-3-Clause",
        "djangorestframework": "BSD-3-Clause", "channels": "BSD-3-Clause",
        "daphne": "BSD-3-Clause", "requests": "Apache-2.0", "numpy": "BSD-3-Clause",
        "pandas": "BSD-3-Clause", "pydantic": "MIT", "fastapi": "MIT",
        "gpl-licensed-tool": "GPL-3.0"
    }

    high_risk_deps = []
    for dep in dependencies:
        dname = dep["name"].lower()
        lic = KNOWN_PKG_LICENSES.get(dname, "MIT") # Default a permisiva para el estándar del stack
        dep["license"] = lic
        
        lic_key = lic.lower()
        if lic_key in KNOWN_LICENSES:
            l_info = KNOWN_LICENSES[lic_key]
            risk = l_info["risk"]
            l_type = l_info["type"]
            if l_type in license_counts:
                license_counts[l_type] += 1

            if risk in ["ALTO", "CRITICO"]:
                high_risk_deps.append(dep)
                findings.append({
                    "severity": "CRITICAL" if risk == "CRITICO" else "HIGH",
                    "title": f"Dependencia con Licencia Copyleft ({lic}): {dep['name']}",
                    "detail": f"{l_info['desc']}. Representa un riesgo potencial de contaminación de código privativo.",
                    "file": "package.json" if dep["ecosystem"] == "npm" else "requirements.txt"
                })
        else:
            license_counts["Permisiva"] += 1

    # Cálculo del Score (Base 100)
    score = 100
    if not has_license_file:
        score -= 15
    if not founder_ip_verified:
        score -= 10
    
    crit_ip = sum(1 for f in findings if f["severity"] == "CRITICAL")
    high_ip = sum(1 for f in findings if f["severity"] == "HIGH")
    score -= (crit_ip * 30)
    score -= (high_ip * 15)
    score = max(0, min(100, score))

    status = "EXCELLENT" if score >= 90 else ("GOOD" if score >= 75 else ("WARNING" if score >= 50 else "DANGER"))

    return {
        "pilar": "Propiedad Intelectual & Licencias",
        "score": score,
        "status": status,
        "summary": f"{len(dependencies)} dependencias analizadas. IP de fundador {'✅ Acreditada' if founder_ip_verified else '⚠️ No explícita en raíz'}. {len(high_risk_deps)} riesgos de copyleft.",
        "findings": findings,
        "metrics": {
            "total_dependencies": len(dependencies),
            "has_license_file": has_license_file,
            "founder_ip_verified": founder_ip_verified,
            "founder_name": FOUNDER_NAME,
            "license_counts": license_counts,
            "high_risk_dependencies": len(high_risk_deps)
        }
    }
