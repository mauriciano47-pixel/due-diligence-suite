# -*- coding: utf-8 -*-
"""
V-GUARD Due Diligence Suite - Catálogo Canónico de Aplicaciones del Ecosistema
Registro de rutas oficiales, descripciones SSOT y vinculación con Cerebros Obsidian.
"""
from pathlib import Path

ECOSYSTEM_APPS = [
    {
        "key": "cambioya",
        "name": "CAMBIOYA!",
        "role": "Plataforma Comunitaria de Trueque Directo & Economía Circular",
        "primary_path": r"C:\Users\mauro\OneDrive\Documentos\CAMBIOYA!",
        "fallback_path": r"C:\Users\mauro\cambioya",
        "obsidian_vault": "cerebro_cambioya",
        "icon": "🔄",
        "category": "Economía Colaborativa"
    },
    {
        "key": "ataraxia",
        "name": "Ataraxia",
        "role": "Coach Integral de Fitness, Nutrición y Rendimiento Estoico",
        "primary_path": r"C:\Users\mauro\OneDrive\Documentos\ATARAXIA_APP",
        "fallback_path": None,
        "obsidian_vault": "cerebro_ataraxia",
        "icon": "⚡",
        "category": "HealthTech & Stoic Coaching"
    },
    {
        "key": "hidoctor",
        "name": "HiDoctor (HiDoc)",
        "role": "Bitácora Clínica Pediátrica Inteligente con Triaje por IA",
        "primary_path": r"C:\Users\mauro\OneDrive\Documentos\hi-doctor",
        "fallback_path": None,
        "obsidian_vault": "cerebro_hidoctor",
        "icon": "🩺",
        "category": "HealthTech Pediátrico"
    },
    {
        "key": "faro",
        "name": "Faro",
        "role": "Sistema de Seguridad Personal, Alerta SOS y Geolocalización",
        "primary_path": r"C:\Users\mauro\OneDrive\Documentos\app_faro",
        "fallback_path": None,
        "obsidian_vault": "cerebro_faro",
        "icon": "🚨",
        "category": "Seguridad Personal & SOS"
    },
    {
        "key": "vitrodiag",
        "name": "VitroDiag",
        "role": "Plataforma de Diagnóstico In-Vitro & Asistente Clínico IA",
        "primary_path": r"C:\Users\mauro\vitrodiag",
        "fallback_path": None,
        "obsidian_vault": "cerebro_vitrodiag",
        "icon": "🔬",
        "category": "Diagnóstico In-Vitro"
    },
    {
        "key": "sentinel",
        "name": "SENTINEL",
        "role": "Guardián de Privacidad, Brechas (HIBP) y Derecho al Olvido",
        "primary_path": r"C:\Users\mauro\sentinel",
        "fallback_path": None,
        "obsidian_vault": "cerebro_sentinel",
        "icon": "🛡️",
        "category": "Ciberseguridad & RGPD"
    },
    {
        "key": "tramitefacil",
        "name": "TrámiteFácil",
        "role": "Asistente de Gestión de Trámites y Documentación Burocrática",
        "primary_path": r"C:\Users\mauro\OneDrive\Documentos\TRAMITE FACIL APP",
        "fallback_path": None,
        "obsidian_vault": "cerebro_tramitefacil",
        "icon": "📑",
        "category": "GovTech & Ciudadanía"
    },
    {
        "key": "vitrina",
        "name": "Vitrina & Launchpad",
        "role": "Portal Showcase Oficial de Inversores & Telemetría en Vivo",
        "primary_path": r"C:\Users\mauro\OneDrive\Documentos\vitrina_apps",
        "fallback_path": None,
        "obsidian_vault": "cerebro_vitrina",
        "icon": "🚀",
        "category": "Showcase & Hub de Inversión"
    },
    {
        "key": "crypto_analyzer",
        "name": "Crypto Pattern Analyzer",
        "role": "Analizador Cuantitativo de Order Flow, CVD & Radar MTF",
        "primary_path": r"C:\Users\mauro\OneDrive\Documentos\crypto_analizer",
        "fallback_path": None,
        "obsidian_vault": "cerebro_crypto_analyzer",
        "icon": "📈",
        "category": "Fintech & Trading Cuantitativo"
    }
]

def get_apps_list():
    result = []
    for app in ECOSYSTEM_APPS:
        p_path = Path(app["primary_path"])
        f_path = Path(app["fallback_path"]) if app["fallback_path"] else None
        
        active_path = None
        if p_path.exists():
            active_path = str(p_path.resolve())
        elif f_path and f_path.exists():
            active_path = str(f_path.resolve())

        result.append({
            "key": app["key"],
            "name": app["name"],
            "role": app["role"],
            "path": active_path,
            "exists": active_path is not None,
            "obsidian_vault": app["obsidian_vault"],
            "icon": app["icon"],
            "category": app["category"]
        })
    return result
