# -*- coding: utf-8 -*-
"""
V-GUARD Due Diligence Suite - Módulo de Vendibilidad M&A & Viabilidad Comercial (Pilar 6)
Evalúa: Potencial de salida (Exit Readiness), modelo de monetización, Key-Person Risk,
barrera de entrada (Moat) y complejidad operativa para compradores en Acquire.com / Flippa / B2B.
"""
import os
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
        "model": "Diagnóstico Óptico Asistido por IA y Control de Moldería en Máquinas I.S. (B2B Industrial)",
        "market": "Plantas de Fabricación de Envases de Vidrio Hueco (Cristalerías / Botellas)",
        "salability": "ALTA (B2B Industrial Pesado)",
        "salability_score": 88,
        "take_rate_potential": "Licencia SaaS Industrial por planta/línea de producción ($500 - $2,500 USD/mes).",
        "key_person_risk": "BAJO (Catálogo multimodal de 111 defectos en caliente/frío con Gemini Vision y plomada digital láser).",
        "operational_moat": "Reducción de brecha de detección de 60 min a 30 seg a pie de máquina en línea caliente (Hot End) y catálogo de defectos especializado.",
        "exit_recommendation": "Venta directa de tecnología a fabricantes globales de maquinaria I.S. (Bucher Emhart Glass, Bottero) o plantas de vidrio (Owens-Illinois, Verallia, Vidrala)."
    },
    "nutralive": {
        "model": "Micro-SaaS Clínico & Nutrición Terapéutica (B2C Familias & B2B Centros Pediátricos)",
        "market": "Familias con niños con esteatosis (MASLD) / Centros Médicos Pediátricos / Nutricionistas",
        "salability": "ALTA (Vertical de Salud Metabólica Pediátrica)",
        "salability_score": 88,
        "take_rate_potential": "Suscripción B2C Guardián Familiar ($4.99/mes o $39.99/año) y Licencia B2B Institucional ($29/mes o $249/año).",
        "key_person_risk": "BAJO-MEDIO (Arquitectura desacoplada React 19 Vite PWA + Django REST, contratos Stripe y algoritmos de tamizaje formalizados).",
        "operational_moat": "Motor algorítmico de tamizaje de JMAF/fructosa oculta, normalización pediátrica ALT/AST (<25 U/L) y biblioteca de 50+ recetas familiares.",
        "exit_recommendation": "Publicar en Acquire.com / Flippa como Micro-SaaS de Nutrición Terapéutica o licenciar a aseguradoras y cadenas de salud pediátrica por $25k-$60k USD."
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
        "model": "Micro-SaaS LegalTech & GovTech (B2C Ciudadano & B2B Gestorías)",
        "market": "Ciudadanía España / Latam (Hacienda, Tráfico, Multas) & Gestorías / Asesorías",
        "salability": "ALTA (Micro-SaaS Turnkey para Acquire.com / Flippa)",
        "salability_score": 86,
        "take_rate_potential": "Pay-per-use por trámite ($1.99 USD), Suscripción Anual ($29.99 USD) y Licencia B2B Gestorías ($149.00 USD/año). Contratos Stripe verificados.",
        "key_person_risk": "BAJO (Arquitectura modular PWA Offline-First, suite de 28 tests automatizados, cero dependencias pesadas).",
        "operational_moat": "Motor OCR WebAssembly local (Tesseract.js v5), fundamentación jurídica real y catálogo de 8 plantillas oficiales.",
        "exit_recommendation": "Publicar en Acquire.com / Flippa como Micro-SaaS GovTech/LegalTech llave en mano o licenciar a cadenas de gestorías online por $18k-$35k USD."
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
        "model": "Micro-SaaS de Seguridad Personal & SOS PWA (B2C Familias & B2B Campus/Empresas)",
        "market": "Familias / Estudiantes / Trabajadores Nocturnos / Universidades & Empresas",
        "salability": "ALTA (Micro-SaaS Turnkey para Acquire.com / Flippa)",
        "salability_score": 86,
        "take_rate_potential": "Suscripción B2C Escudo Familiar ($3.99/mes o $29.99/año) y Campus/B2B ($299/año). Contratos Stripe verificados.",
        "key_person_risk": "BAJO (Arquitectura modular PWA Offline-First, suite de 18 tests automatizados, cero dependencias pesadas).",
        "operational_moat": "PWA Offline-First con geocercas inteligentes, botón SOS dual, linterna estroboscópica de auxilio y cifrado local de PIN.",
        "exit_recommendation": "Publicar en Acquire.com / Flippa como Micro-SaaS de Seguridad Personal llave en mano o licenciar a aseguradoras y campus universitarios por $15k-$35k USD."
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
    excluded_dirs = {'.git', 'node_modules', '.venv', 'venv', 'dist', '__pycache__', '.next', '.expo', 'scratch', 'build', '.cache'}
    payment_keywords = ["stripe", "mercadopago", "paypal", "lemonsqueezy", "paddle"]
    target_exts = {".js", ".jsx", ".ts", ".tsx", ".py", ".html"}

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in excluded_dirs and not d.startswith(".")]
        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext in target_exts and not fname.endswith(".min.js"):
                fpath = Path(dirpath) / fname
                try:
                    txt = fpath.read_text(encoding="utf-8", errors="ignore")
                    if any(k in txt.lower() for k in payment_keywords):
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
