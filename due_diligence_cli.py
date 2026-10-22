# -*- coding: utf-8 -*-
"""
V-GUARD Due Diligence Suite - CLI Runner (v3.1 Sovereign Institutional)
Plataforma Integral de Gobernanza, Delta Quality Gate, Auto-Remediación,
Telemetría de Series Temporales, Certificaciones Internacionales y Virtual Data Room (M&A).
"""
import sys
import os
import argparse
from pathlib import Path

# Configurar encoding UTF-8 seguro para Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Añadir el directorio core al path
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir / "core"))

from scanner import scan_project
from apps_registry import get_apps_list, ECOSYSTEM_APPS
from audit_delta import run_delta_quality_gate
from auto_remediator import run_auto_remediation
from audit_telemetry import record_audit_event, calculate_trend, get_app_history
from vdr_packager import export_vdr_package
from hook_orchestrator import install_fleet_hooks

OBSIDIAN_BASE_PATH = Path(r"C:\Users\mauro\OneDrive\Desktop\Cerebros_Obsidian")

def print_banner():
    print("=" * 70)
    print(" 🏛️  V-GUARD DUE DILIGENCE SUITE — Sovereign Institutional Platform")
    print(" Quality Gates, Auto-Remediation, Time-Series Telemetry & M&A Data Room")
    print("=" * 70)

def save_to_obsidian(app_key: str, markdown_content: str, app_name: str) -> str:
    vault_name = "cerebro_vguard_seguridad"
    for a in ECOSYSTEM_APPS:
        if a["key"] == app_key:
            vault_name = a["obsidian_vault"]
            break

    target_dir = OBSIDIAN_BASE_PATH / vault_name
    if not target_dir.exists():
        target_dir = OBSIDIAN_BASE_PATH / "cerebro_vguard_seguridad"
    
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = f"Dossier_Due_Diligence_{app_name.replace(' ', '_').replace('!', '')}.md"
    target_file = target_dir / filename
    
    target_file.write_text(markdown_content, encoding="utf-8")
    return str(target_file)

def run_single_audit(app_data: dict, save_obsidian: bool = False, export_vdr: bool = False):
    print(f"\n🔍 Auditando: {app_data['name']} [{app_data['role']}]")
    print(f"📁 Directorio: {app_data['path']}")
    print("-" * 70)

    result = scan_project(app_data["path"], app_key=app_data.get("key"), app_name=app_data["name"])

    # 1. Registrar evento en telemetría de series temporales
    record_audit_event(result)

    print(f"📊 VEREDICTO DUE DILIGENCE: {result['grade']} ({result['global_score']}/100)")
    print(f"   Calificación: {result['grade_label']}")
    print(f"   🚨 Deal Breakers / Alertas Críticas: {result['deal_breakers_count']}")

    val = result.get("valuation")
    if val:
        print("\n   [💎 Simulador de Valuación Institucional M&A]:")
        print(f"   🏛️  Madurez Institucional : {val['tier']}")
        print(f"   💰 Multiplicador Salida  : {val['arr_multiple']}")
        print(f"   ✂️  Haircut Deuda Técnica : {val['haircut_pct']}% ({val['turnkey_status']})")
        print(f"   🧬 Armas Élite Activas   : {val['elite_score_ratio']}")

        # 2. Análisis de tendencia histórica
        trend = calculate_trend(app_data.get("key", "custom"), result['global_score'], val['haircut_pct'])
        if trend.get("has_history"):
            print(f"   📈 Tendencia Telemetría  : {trend['summary']}")

    certs = result.get("certifications")
    if certs:
        openssf = certs.get("openssf", {})
        asvs = certs.get("owasp_asvs", {})
        slsa = certs.get("slsa_supply_chain", {})
        reg = certs.get("domain_regulatory", {})
        print("\n   [🎖️ Acreditaciones & Certificaciones Internacionales]:")
        print(f"   🥇 OpenSSF Best Practices : {openssf.get('badge_icon')} {openssf.get('badge')} ({openssf.get('score')}%)")
        print(f"   🛡️  OWASP ASVS v4.0.3      : {asvs.get('level')} (Score: {asvs.get('average_score')}/100)")
        print(f"   ⛓️  Google SLSA / NIST     : {slsa.get('level')}")
        print(f"   🏛️  Cumplimiento Sectorial : {reg.get('standard')} -> {reg.get('readiness_score')}% ({reg.get('status')})")

    print("\n   [Desglose por Pilares]:")
    for k, p in result["pillars"].items():
        icon = "✅" if p["score"] >= 80 else ("⚠️" if p["score"] >= 60 else "❌")
        print(f"   {icon} {p['pilar']:<35} : {p['score']:>3}/100 ({p['status']})")

    if result["deal_breakers"]:
        print("\n   ⚠️ ALERTA DE DEAL BREAKERS:")
        for db in result["deal_breakers"]:
            print(f"      - [{db['pilar']}] {db['title']}")

    if save_obsidian:
        saved_path = save_to_obsidian(app_data.get("key", "custom"), result["markdown_report"], app_data["name"])
        print(f"\n💾 Dossier guardado exitosamente en Obsidian:\n   -> {saved_path}")

    if export_vdr:
        vdr_path = export_vdr_package(app_data["path"], result)
        print(f"\n📦 Virtual Data Room (VDR) Sellado Generado:\n   -> {vdr_path}")

    return result

def main():
    parser = argparse.ArgumentParser(description="V-GUARD Due Diligence Suite (v3.1)")
    parser.add_argument("--list", action="store_true", help="Listar aplicaciones registradas en el ecosistema")
    parser.add_argument("--app", type=str, help="Clave de la aplicación a auditar (ej. ataraxia, cambioya, hidoctor, faro)")
    parser.add_argument("--all", action="store_true", help="Auditar toda la flota de aplicaciones del ecosistema")
    parser.add_argument("--path", type=str, help="Auditar una ruta de carpeta personalizada")
    parser.add_argument("--save-obsidian", action="store_true", help="Guardar dossier generado en Cerebros Obsidian")
    parser.add_argument("--diff", action="store_true", help="Ejecutar Delta Quality Gate (auditoría incremental sobre git diff)")
    parser.add_argument("--fix", action="store_true", help="Ejecutar suite de Auto-Remediación determinista (--fix)")
    parser.add_argument("--export-vdr", action="store_true", help="Generar paquete sellado Virtual Data Room (M&A .zip)")
    parser.add_argument("--install-hooks", action="store_true", help="Instalar hooks de Git pre-push en toda la flota")
    parser.add_argument("--history", action="store_true", help="Ver historial de telemetría de series temporales")

    args = parser.parse_args()
    print_banner()

    apps = get_apps_list()

    # Opción: Instalar Hooks en toda la flota
    if args.install_hooks:
        print("\n⚓ Instalando Shift-Left Git Hooks en la flota de aplicaciones...")
        res = install_fleet_hooks()
        print(f"✅ Hooks instalados exitosamente en {res['installed_count']}/{res['total_apps']} repositorios.")
        for d in res["details"]:
            status_icon = "🟢" if d["status"] == "INSTALLED" else "⚠️"
            print(f"   {status_icon} {d['app']:<24}: {d['status']} {d.get('path') or d.get('reason')}")
        return

    # Opción: Listar Apps
    if args.list:
        print("\n📦 APLICACIONES REGISTRADAS EN EL ECOSISTEMA:")
        for a in apps:
            status_str = "🟢 Lista" if a["exists"] else "🔴 No encontrada"
            print(f" - [{a['key']}] {a['name']:<22} | {status_str} | {a['path']}")
        return

    # Opción: Ver Historial de Telemetría
    if args.history:
        target_key = args.app or "ataraxia"
        print(f"\n📈 HISTORIAL DE TELEMETRÍA DE SERIES TEMPORALES ({target_key}):")
        events = get_app_history(target_key)
        if not events:
            print(f"   No se registran eventos previos para '{target_key}'.")
        else:
            print(f"{'Fecha y Hora':<20} | {'Score':<8} | {'Grado':<6} | {'Haircut':<8} | {'Armas':<6} | {'SLOC':<7} | {'Commit'}")
            print("-" * 75)
            for ev in events:
                print(f"{ev['timestamp']:<20} | {ev['global_score']:>5}/100 | {ev['grade']:<6} | {ev['haircut_pct']:>5}% | {ev['elite_weapons']:<6} | {ev['sloc']:<7} | {ev['commit_hash']}")
        return

    # Determinar aplicación objetivo
    target_app = None
    if args.app:
        target_app = next((a for a in apps if a["key"].lower() == args.app.lower()), None)
        if not target_app:
            print(f"❌ Aplicación '{args.app}' no encontrada en el catálogo. Usa --list para ver las disponibles.")
            return
        if not target_app["exists"]:
            print(f"❌ La ruta configurada para '{target_app['name']}' no existe: {target_app['path']}")
            return
    elif args.path:
        p = Path(args.path)
        if not p.exists():
            print(f"❌ La ruta especificada no existe: {args.path}")
            return
        target_app = {
            "key": "custom",
            "name": p.name,
            "role": "Auditoría de Directorio Personalizado",
            "path": str(p.resolve())
        }

    # Opción: Delta Quality Gate (--diff)
    if args.diff:
        if not target_app:
            print("❌ Debes especificar una aplicación con --app <nombre> o una ruta con --path <ruta>.")
            return
        print(f"\n🔬 EJECUTANDO DELTA QUALITY GATE (Clean as You Code) en: {target_app['name']}")
        print(f"📁 Directorio: {target_app['path']}")
        delta_res = run_delta_quality_gate(target_app["path"])
        status_icon = "🟢" if delta_res["status"] == "PASSED" else "🔴"
        print(f"\n{status_icon} ESTADO DELTA QUALITY GATE: {delta_res['status']} (Score: {delta_res.get('score', 100)}/100)")
        print(f"   Líneas nuevas analizadas : {delta_res.get('lines_added', 0)}")
        print(f"   Archivos modificados     : {delta_res.get('files_analyzed', 0)}")
        print(f"   Infracciones críticas    : {delta_res.get('critical_count', 0)}")

        if delta_res.get("violations"):
            print("\n   [Detalle de Infracciones en Código Nuevo]:")
            for v in delta_res["violations"]:
                v_icon = "🚨" if v["severity"] == "CRITICAL" else "⚠️"
                print(f"   {v_icon} [{v['rule']}] {v['title']} ({v.get('file', 'N/A')})")
                print(f"      -> {v['detail']}")
        else:
            print("   ✨ Código nuevo 100% puro. Cumple con la directiva 'Clean as You Code'.")
        return

    # Opción: Auto-Remediación (--fix)
    if args.fix:
        if not target_app:
            print("❌ Debes especificar una aplicación con --app <nombre> o una ruta con --path <ruta>.")
            return
        print(f"\n🛠️ EJECUTANDO AUTO-REMEDIACIÓN QUIRÚRGICA en: {target_app['name']}")
        print(f"📁 Directorio: {target_app['path']}")
        fix_res = run_auto_remediation(target_app["path"])
        if fix_res["actions_count"] == 0:
            print("✅ El proyecto ya cumple con el estándar. No se requirieron parches automáticos.")
        else:
            print(f"🎉 Se aplicaron exitosamente {fix_res['actions_count']} correcciones automáticas:")
            for a in fix_res["actions"]:
                print(f"   -> {a}")
        return

    # Opción: Auditoría masiva de toda la flota
    if args.all:
        print(f"\n🚀 Iniciando escaneo masivo de la flota ({len(apps)} aplicaciones)...")
        results = []
        for a in apps:
            if a["exists"]:
                res = run_single_audit(a, save_obsidian=args.save_obsidian, export_vdr=args.export_vdr)
                results.append(res)
            else:
                print(f"\n⚠️ Saltando {a['name']} (Directorio no accesible en esta ruta).")

        print("\n" + "=" * 70)
        print(" 🏁 RESUMEN COMPARATIVO DE DUE DILIGENCE DE LA FLOTA")
        print("=" * 70)
        print(f"{'Aplicación':<24} | {'Score':<7} | {'Grado':<6} | {'Deal Breakers':<14} | {'Estado':<10}")
        print("-" * 70)
        for r in results:
            print(f"{r['app_name']:<24} | {r['global_score']:>5}/100 | {r['grade']:<6} | {r['deal_breakers_count']:<14} | {r['grade_label'][:10]}")
        return

    # Opción: Auditoría individual por app o ruta
    if target_app:
        run_single_audit(target_app, save_obsidian=args.save_obsidian, export_vdr=args.export_vdr)
        return

    parser.print_help()

if __name__ == "__main__":
    main()
