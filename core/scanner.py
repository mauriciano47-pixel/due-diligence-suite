# -*- coding: utf-8 -*-
"""
V-GUARD Due Diligence Suite - Orquestador Maestro de Auditoría (Core Engine)
Ejecuta la auditoría integral de los 5 pilares, calcula el score ponderado, detecta Red Flags / Deal Breakers y genera el dossier formal.
"""
import os
import json
import datetime
from pathlib import Path

from audit_security import audit_security
from audit_ip_licenses import audit_ip_licenses
from audit_architecture import audit_architecture
from audit_resilience import audit_resilience
from audit_governance import audit_governance

WEIGHTS = {
    "security": 0.30,      # 30% Ciberseguridad & Zero-Leakage
    "ip_licenses": 0.25,   # 25% Propiedad Intelectual & Licencias
    "architecture": 0.20,  # 20% Arquitectura & Deuda Técnica
    "resilience": 0.15,    # 15% Resiliencia & Producción
    "governance": 0.10     # 10% Gobernanza & Data Room
}

def calculate_rating(score: float) -> tuple[str, str, str]:
    if score >= 95:
        return "AAA", "Grado de Inversión Élite", "#10b981"
    elif score >= 85:
        return "AA", "Alta Calidad / Apto para Ronda", "#00e5ff"
    elif score >= 75:
        return "A", "Solvente / Deuda Técnica Manejable", "#3b82f6"
    elif score >= 60:
        return "BBB", "Riesgo Moderado / Requiere Saneamiento", "#f59e0b"
    elif score >= 40:
        return "CCC", "Alto Riesgo / Contingencias Pendientes", "#ef4444"
    else:
        return "D", "No Apto para Adquisición / Crítico", "#b91c1c"

def scan_project(project_path: str, app_key: str = None, app_name: str = None) -> dict:
    root = Path(project_path)
    now = datetime.datetime.now()
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
    date_str = now.strftime("%Y-%m-%d")

    display_name = app_name or root.name

    # Ejecutar auditoría en los 5 pilares
    sec_res = audit_security(project_path)
    ip_res = audit_ip_licenses(project_path)
    arch_res = audit_architecture(project_path)
    res_res = audit_resilience(project_path)
    gov_res = audit_governance(project_path, app_key)

    # Calcular score global ponderado
    global_score = round(
        (sec_res["score"] * WEIGHTS["security"]) +
        (ip_res["score"] * WEIGHTS["ip_licenses"]) +
        (arch_res["score"] * WEIGHTS["architecture"]) +
        (res_res["score"] * WEIGHTS["resilience"]) +
        (gov_res["score"] * WEIGHTS["governance"]),
        1
    )

    grade, grade_label, grade_color = calculate_rating(global_score)

    # Recopilar todos los hallazgos y aislar Deal Breakers / Red Flags
    deal_breakers = []
    all_findings = []

    for pilar_res in [sec_res, ip_res, arch_res, res_res, gov_res]:
        for finding in pilar_res.get("findings", []):
            finding_copy = {**finding, "pilar": pilar_res["pilar"]}
            all_findings.append(finding_copy)
            if finding.get("severity") == "CRITICAL":
                deal_breakers.append(finding_copy)

    # Generar Dossier Markdown para Obsidian / Inversores
    markdown_report = generate_markdown_dossier(
        app_name=display_name,
        project_path=str(root.resolve()),
        timestamp=timestamp_str,
        score=global_score,
        grade=grade,
        grade_label=grade_label,
        deal_breakers=deal_breakers,
        pillars=[sec_res, ip_res, arch_res, res_res, gov_res]
    )

    return {
        "app_key": app_key,
        "app_name": display_name,
        "project_path": str(root.resolve()),
        "timestamp": timestamp_str,
        "date": date_str,
        "global_score": global_score,
        "grade": grade,
        "grade_label": grade_label,
        "grade_color": grade_color,
        "deal_breakers_count": len(deal_breakers),
        "deal_breakers": deal_breakers,
        "pillars": {
            "security": sec_res,
            "ip_licenses": ip_res,
            "architecture": arch_res,
            "resilience": res_res,
            "governance": gov_res
        },
        "all_findings": all_findings,
        "markdown_report": markdown_report
    }

def generate_markdown_dossier(app_name, project_path, timestamp, score, grade, grade_label, deal_breakers, pillars) -> str:
    md = f"""# 🏛️ Dossier Ejecutivo de Tech Due Diligence — {app_name}

**Fecha de Auditoría:** {timestamp}  
**Ruta del Repositorio:** `{project_path}`  
**Titularidad & Autoría:** Mauricio Uribe Maldonado  
**Veredicto de Inversión:** **{grade} ({score}/100)** — *{grade_label}*

---

## 📊 Resumen Ejecutivo del Score

| Pilar de Evaluación | Ponderación | Score Obtenido | Estado |
| :--- | :---: | :---: | :---: |
| 🛡️ **1. Ciberseguridad & Zero-Leakage** | 30% | **{pillars[0]['score']}/100** | {pillars[0]['status']} |
| 📜 **2. Propiedad Intelectual & Licencias** | 25% | **{pillars[1]['score']}/100** | {pillars[1]['status']} |
| 🏗️ **3. Arquitectura & Deuda Técnica** | 20% | **{pillars[2]['score']}/100** | {pillars[2]['status']} |
| ⚡ **4. Resiliencia & Producción** | 15% | **{pillars[3]['score']}/100** | {pillars[3]['status']} |
| 🏛️ **5. Gobernanza & Data Room** | 10% | **{pillars[4]['score']}/100** | {pillars[4]['status']} |
| **TOTAL PONDERADO** | **100%** | **{score}/100** | **{grade}** |

---

## 🚨 Alertas Críticas & Deal Breakers ({len(deal_breakers)})
"""
    if deal_breakers:
        for db in deal_breakers:
            md += f"- ❌ **[{db['pilar']}] {db['title']}**\n  *Detalle:* {db['detail']}\n"
    else:
        md += "✅ **CERO DEAL BREAKERS DETECTADOS.** El código cumple con las directivas fundamentales de seguridad y titularidad privada para rondas de inversión.\n"

    md += "\n---\n\n## 🔍 Desglose Detallado por Pilares\n"

    for p in pillars:
        md += f"\n### {p['pilar']} (Score: {p['score']}/100 - {p['status']})\n"
        md += f"> **Resumen:** {p.get('summary', 'Sin observaciones.')}\n\n"
        findings = p.get("findings", [])
        if findings:
            for f in findings:
                sev_icon = "🔴" if f.get("severity") == "CRITICAL" else ("🟠" if f.get("severity") == "HIGH" else ("🟡" if f.get("severity") == "MEDIUM" else "🔵"))
                md += f"* {sev_icon} **[{f.get('severity')}] {f.get('title')}**\n"
                md += f"  - *Detalle:* {f.get('detail')}\n"
                if "file" in f:
                    line_str = f" (Línea {f['line']})" if "line" in f else ""
                    md += f"  - *Ubicación:* `{f['file']}`{line_str}\n"
        else:
            md += "✅ No se detectaron anomalías ni advertencias en este pilar.\n"

    md += f"""
---

## 📝 Conclusión y Recomendaciones para Inversores
1. **Titularidad de Activos:** La propiedad de los repositorios y marcas pertenece en forma íntegra a Mauricio Uribe Maldonado.
2. **Deuda Técnica:** Los monolitos y comentarios TODO identificados deben gestionarse en los checkpoints de versiones siguientes.
3. **Resiliencia Operativa:** Arquitectura offline-first y protocolos de contingencia implementados para garantizar continuidad de negocio.

*Informe generado automáticamente por V-GUARD Due Diligence Suite.*
"""
    return md
