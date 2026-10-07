# -*- coding: utf-8 -*-
"""
V-GUARD Due Diligence Suite - Módulo de Vendibilidad M&A & Viabilidad Comercial (Pilar 6)
Evalúa: Potencial de salida (Exit Readiness), modelo de monetización, Key-Person Risk,
barrera de entrada (Moat) y complejidad operativa para compradores en Acquire.com / Flippa / B2B.
"""
from pathlib import Path

# Catálogo de inteligencia comercial de la flota
COMMERCIAL_PROFILES = {
    "cambioya": {
        "model": "Economía Circular / Trueque Comunitario",
        "market": "B2C Masivo / Comunidades Locales",
        "salability": "COMPLEJA",
        "salability_score": 52,
        "take_rate_potential": "Nulo directo (Trueque sin dinero). Requiere membresías premium o patrocinios locales.",
        "key_person_risk": "ALTO (Arquitectura Django Channels + WebSockets monolítica con alta dependencia del creador).",
        "operational_moat": "Efecto de red hiperlocal y mapa semántico. Si no hay masa crítica de vecinos, el valor cae a cero.",
        "exit_recommendation": "Empaquetar como solución B2G/Municipal para gestión de residuos y economía circular comunitaria, o licenciar a ONGs."
    },
    "hidoctor": {
        "model": "Micro-SaaS Pediátrico / B2C & B2B White-Label",
        "market": "Familias / Clínicas Pediátricas / Aseguradoras",
        "salability": "ALTA (Ideal para Acquire.com / Flippa)",
        "salability_score": 88,
        "take_rate_potential": "Suscripción mensual ($4.99 - $9.99/mes) o pago B2B por clínica.",
        "key_person_risk": "BAJO-MEDIO (Frontend limpio PWA, fácil de traspasar a otro desarrollador frontend).",
        "operational_moat": "Curva térmica vectorial SVG + Triaje dual IA y directorio offline multi-país.",
        "exit_recommendation": "Integrar pasarela Stripe, añadir disclaimer legal médico reforzado y publicar como Micro-SaaS llave en mano en Acquire.com por $15k-$35k USD."
    },
    "ataraxia": {
        "model": "SaaS Fitness & Coaching Estoico",
        "market": "B2C Fitness & Biohacking",
        "salability": "MEDIA",
        "salability_score": 68,
        "take_rate_potential": "Suscripción mensual/anual ($9.99/mes o $59/año).",
        "key_person_risk": "MEDIO (React Native / Expo requiere mantenimiento continuo de dependencias nativas).",
        "operational_moat": "Algoritmo PPG de contacto físico + Arquetipos estoicos. Mercado saturado con alto churn (>12%).",
        "exit_recommendation": "Venta en Flippa orientada a influencers fitness o comunidades de desarrollo personal estoico."
    },
    "vitrodiag": {
        "model": "SaaS B2B Catálogo Clínico & Diagnóstico IA",
        "market": "Laboratorios Clínicos / Distribuidores de Reactivos",
        "salability": "ALTA (B2B Nicho)",
        "salability_score": 84,
        "take_rate_potential": "Suscripción institucional ($99 - $299/mes por laboratorio).",
        "key_person_risk": "BAJO (Base de datos curada de 100+ reactivos y arquitectura frontend modular).",
        "operational_moat": "Base de datos propietaria de analizadores y reactivos con Gemini Vision especializado.",
        "exit_recommendation": "Venta directa B2B a un distribuidor médico regional o venta en MicroAcquire como herramienta B2B vertical."
    },
    "sentinel": {
        "model": "B2B Privacy & Compliance / Micro-SaaS RGPD",
        "market": "Pymes / Profesionales con obligaciones RGPD / Consumidores",
        "salability": "MEDIA-ALTA",
        "salability_score": 75,
        "take_rate_potential": "Suscripción o pago por solicitud de olvido ($15 - $50/caso).",
        "key_person_risk": "MEDIO (Requiere mantenimiento de proxies y endpoints k-anonymity).",
        "operational_moat": "Orquestación automatizada del Art. 17 RGPD y verificación sin almacenar datos.",
        "exit_recommendation": "Comercializar a agencias de marketing o despachos legales como addon de cumplimiento de privacidad."
    },
    "tramitefacil": {
        "model": "Pay-per-use LegalTech / Gestoría B2C",
        "market": "Ciudadanía España / Latam (Hacienda, Tráfico, Multas)",
        "salability": "ALTA (Excelente Product-Market Fit local)",
        "salability_score": 82,
        "take_rate_potential": "Micropago por escrito oficial generado (€4.99 - €9.99 por carta/alegación).",
        "key_person_risk": "BAJO (Arquitectura basada en plantillas legales estandarizadas y Gemini Flash).",
        "operational_moat": "Fundamentación jurídica real (Ley 39/2015) y modo de impresión oficial A4 sin fricción.",
        "exit_recommendation": "Instalar cobro por Bizum/Stripe y publicitar en foros de trámites burocráticos o vender a una gestoría online."
    },
    "crypto_analyzer": {
        "model": "Fintech SaaS Trading Cuantitativo",
        "market": "Traders Cripto / Comunidades de Análisis Técnico",
        "salability": "MEDIA-ALTA",
        "salability_score": 76,
        "take_rate_potential": "Membresía premium ($19 - $49/mes) o acceso por referidos de exchanges.",
        "key_person_risk": "MEDIO (Mantenimiento de WebSockets Binance y cálculo matemático de Order Flow).",
        "operational_moat": "Motor CVD tiempo real en navegador sin backend pesado de servidores.",
        "exit_recommendation": "Monetizar con programa de afiliados Binance/Bybit o vender acceso a comunidades privadas de trading en Telegram/Discord."
    },
    "faro": {
        "model": "Seguridad Personal & SOS PWA",
        "market": "Familias / Estudiantes / Turnos Nocturnos",
        "salability": "MEDIA",
        "salability_score": 64,
        "take_rate_potential": "Complejo en B2C directo sin alto gasto en ads. Mejor modelo: B2G (acuerdos universitarios/municipales).",
        "key_person_risk": "BAJO (Frontend ligero PWA).",
        "operational_moat": "PWA offline-first con linterna estroboscópica y geocercas sin dependencia de servidores caros.",
        "exit_recommendation": "Presentar como proyecto de licitación municipal para ciudades seguras o protección universitaria."
    },
    "vitrina": {
        "model": "Hub Showcase / Portfolio Inversor",
        "market": "Inversores / Partners / Ecosistema",
        "salability": "ACTIVO DE SOPORTE",
        "salability_score": 70,
        "take_rate_potential": "No monetizable por sí misma; es la vitrina de conversión del resto de la flota.",
        "key_person_risk": "BAJO.",
        "operational_moat": "Simulador en vivo iPhone/Tablet integrado a telemetría.",
        "exit_recommendation": "Mantener como cuartel general de demostración de activos."
    }
}

def audit_commercial(project_path: str, app_key: str = None) -> dict:
    root = Path(project_path)
    findings = []
    
    profile = COMMERCIAL_PROFILES.get(app_key, {
        "model": "Software Propietario / Sin perfil comercial asignado",
        "market": "General",
        "salability": "PENDIENTE EVALUACIÓN",
        "salability_score": 50,
        "take_rate_potential": "Sin modelo de monetización configurado.",
        "key_person_risk": "ALTO (Dependencia total del desarrollador en código no documentado).",
        "operational_moat": "Genérico.",
        "exit_recommendation": "Definir pasarela de pago (Stripe) y embudo de conversión."
    })

    score = profile["salability_score"]

    # Detección de pasarela de pago (Stripe / PayPal / MercadoPago) en el código
    has_payment_gateway = False
    for ext in [".js", ".jsx", ".ts", ".tsx", ".py", ".html"]:
        for f in root.glob(f"*{ext}"):
            try:
                txt = f.read_text(encoding="utf-8", errors="ignore")
                if any(k in txt.lower() for k in ["stripe", "mercadopago", "paypal", "lemonsqueezy", "paddle"]):
                    has_payment_gateway = True
                    break
            except Exception:
                pass
        if has_payment_gateway:
            break

    if has_payment_gateway:
        findings.append({
            "severity": "LOW",
            "title": "Pasarela de pago detectada en código",
            "detail": "El proyecto cuenta con integraciones o referencias para monetización directa."
        })
        score = min(100, score + 10)
    else:
        findings.append({
            "severity": "HIGH",
            "title": "Ausencia de pasarela de pago activa (Zero-Billing Infrastructure)",
            "detail": "No se detectaron integraciones con Stripe, PayPal ni LemonSqueezy. En una auditoría de M&A, un software sin sistema de cobro activo requiere inversión previa del comprador antes de generar el primer dólar.",
            "file": "billing"
        })
        score = max(30, score - 15)

    status = "HIGH POTENTIAL" if score >= 80 else ("MODERATE" if score >= 60 else "LOW POTENTIAL")

    return {
        "pilar": "Vendibilidad M&A & Viabilidad Comercial",
        "score": score,
        "status": status,
        "summary": f"Vendibilidad: {profile['salability']} ({score}/100). Modelo: {profile['model']}. Key-Person Risk: {profile['key_person_risk'][:40]}...",
        "findings": findings,
        "metrics": {
            "business_model": profile["model"],
            "target_market": profile["market"],
            "salability_rating": profile["salability"],
            "take_rate_potential": profile["take_rate_potential"],
            "key_person_risk": profile["key_person_risk"],
            "operational_moat": profile["operational_moat"],
            "exit_recommendation": profile["exit_recommendation"],
            "has_payment_gateway": has_payment_gateway
        }
    }
