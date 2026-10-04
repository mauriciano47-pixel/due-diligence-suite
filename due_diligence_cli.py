# -*- coding: utf-8 -*-
"""
V-GUARD Due Diligence Suite - CLI Runner
Ejecuta auditorías de Due Diligence desde la terminal de forma rápida y automatizada.
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

OBSIDIAN_BASE_PATH = Path(r"C:\Users\mauro\OneDrive\Desktop\Cerebros_Obsidian")

def print_banner():
    print("=" * 70)
    print(" 🏛️  V-GUARD DUE DILIGENCE SUITE — Tech & Corporate Audit Hub")
    print(" Auditoría de Inversión, Ciberseguridad, Licencias y Arquitectura")
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

def run_single_audit(app_data: dict, save_obsidian: bool = False):
    print(f"\n🔍 Auditando: {app_data['name']} [{app_data['role']}]")
    print(f"📁 Directorio: {app_data['path']}")
    print("-" * 70)

    result = scan_project(app_data["path"], app_key=app_data.get("key"), app_name=app_data["name"])

    print(f"📊 VEREDICTO DUE DILIGENCE: {result['grade']} ({result['global_score']}/100)")
    print(f"   Calificación: {result['grade_label']}")
    print(f"   🚨 Deal Breakers / Alertas Críticas: {result['deal_breakers_count']}")

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

    return result

def main():
    parser = argparse.ArgumentParser(description="V-GUARD Due Diligence CLI Runner")
    parser.add_argument("--list", action="store_true", help="Listar aplicaciones registradas en el ecosistema")
    parser.add_argument("--app", type=str, help="Clave de la aplicación a auditar (ej. cambioya, ataraxia, hidoctor, faro)")
    parser.add_argument("--all", action="store_true", help="Auditar toda la flota de aplicaciones del ecosistema")
    parser.add_argument("--path", type=str, help="Auditar una ruta de carpeta personalizada")
    parser.add_argument("--save-obsidian", action="store_true", help="Guardar dossier generado en Cerebros Obsidian")

    args = parser.parse_args()
    print_banner()

    apps = get_apps_list()

    if args.list:
        print("\n📦 APLICACIONES REGISTRADAS EN EL ECOSISTEMA:")
        for a in apps:
            status_str = "🟢 Lista" if a["exists"] else "🔴 No encontrada"
            print(f" - [{a['key']}] {a['name']:<22} | {status_str} | {a['path']}")
        return

    if args.all:
        print(f"\n🚀 Iniciando escaneo masivo de la flota ({len(apps)} aplicaciones)...")
        results = []
        for a in apps:
            if a["exists"]:
                res = run_single_audit(a, save_obsidian=args.save_obsidian)
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

    if args.app:
        matched = next((a for a in apps if a["key"].lower() == args.app.lower()), None)
        if not matched:
            print(f"❌ Aplicación '{args.app}' no encontrada en el catálogo. Usa --list para ver las disponibles.")
            return
        if not matched["exists"]:
            print(f"❌ La ruta configurada para '{matched['name']}' no existe: {matched['path']}")
            return
        run_single_audit(matched, save_obsidian=args.save_obsidian)
        return

    if args.path:
        custom_path = Path(args.path)
        if not custom_path.exists():
            print(f"❌ La ruta especificada no existe: {args.path}")
            return
        app_data = {
            "key": "custom",
            "name": custom_path.name,
            "role": "Auditoría de Directorio Personalizado",
            "path": str(custom_path.resolve())
        }
        run_single_audit(app_data, save_obsidian=args.save_obsidian)
        return

    # Si no se pasó argumento, mostrar ayuda
    parser.print_help()

if __name__ == "__main__":
    main()
