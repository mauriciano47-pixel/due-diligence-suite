# -*- coding: utf-8 -*-
"""
V-GUARD Due Diligence Suite v2.4.0 - Motor de Valuación M&A, Haircut Técnico & Tier Institucional (Big Tech Standard)
Calcula el multiplicador de valuación (ARR Multiple), el descuento por deuda técnica (Haircut %)
y el Nivel de Madurez Institucional (Tier 1 a Tier 5) con las 14 Armas Institucionales de Grandes Ligas.
"""

def calculate_ma_valuation(global_score: float, pillars: dict, deal_breakers_count: int) -> dict:
    arch = pillars.get("architecture", {})
    arch_metrics = arch.get("metrics", {})
    test_run = arch_metrics.get("test_run", {})
    sca = pillars.get("sca", {})
    sca_metrics = sca.get("metrics", {})
    comm = pillars.get("commercial", {})
    comm_metrics = comm.get("metrics", {})
    sec = pillars.get("security", {})
    sec_metrics = sec.get("metrics", {})
    res = pillars.get("resilience", {})
    res_metrics = res.get("metrics", {})
    gov = pillars.get("governance", {})
    gov_metrics = gov.get("metrics", {})

    # 1. Checklist de 14 Armas de Ingeniería Institucional (Big Tech Tier-1 Standard)
    has_unit_tests = bool(test_run.get("executed") and test_run.get("pass_rate", 0) == 100.0 and test_run.get("total_tests", 0) >= 10)
    coverage_pct = test_run.get("coverage_pct") or 0.0
    has_coverage_gate = coverage_pct >= 80.0
    has_e2e = bool(test_run.get("has_e2e"))
    has_pbt_fuzzing = bool(test_run.get("has_pbt_fuzzing"))
    has_chaos = bool(test_run.get("has_chaos"))
    has_mutation = bool(test_run.get("has_mutation"))
    has_ci = bool(test_run.get("has_ci"))
    has_sbom = bool(sca_metrics.get("sbom_generated"))
    has_billing = bool(comm_metrics.get("has_payment_gateway"))
    zero_god_files = arch_metrics.get("god_files_count", 0) == 0

    # Nuevas 4 Armas de Grandes Ligas (v2.4.0)
    crit_funcs = arch_metrics.get("critical_functions_count", 0)
    zero_critical_complexity = (crit_funcs == 0)
    has_dast_headers = bool(sec_metrics.get("has_dast_headers"))
    has_runtime_contracts = bool(arch_metrics.get("has_runtime_contracts"))
    has_shift_left_and_perf = bool(gov_metrics.get("has_shift_left_hook")) and bool(res_metrics.get("performance_budget_compliant", True))

    elite_capabilities = {
        "unit_tests_100": has_unit_tests,
        "coverage_gate_80": has_coverage_gate,
        "e2e_playwright": has_e2e,
        "property_based_fuzzing": has_pbt_fuzzing,
        "chaos_engineering": has_chaos,
        "mutation_testing": has_mutation,
        "sbom_cyclonedx": has_sbom,
        "ci_cd_quality_gates": has_ci,
        "zero_god_files": zero_god_files,
        "active_billing_gateway": has_billing,
        "zero_critical_complexity": zero_critical_complexity,
        "dast_http_headers": has_dast_headers,
        "runtime_contract_guard": has_runtime_contracts,
        "shift_left_git_gate": has_shift_left_and_perf,
    }
    elite_count = sum(1 for v in elite_capabilities.values() if v)
    total_elite = len(elite_capabilities)

    # 2. Cálculo de Technical Debt Haircut (% de descuento que aplica un comprador en M&A)
    haircut_pct = 0.0
    haircut_reasons = []

    if deal_breakers_count > 0:
        haircut_pct += min(50.0, deal_breakers_count * 25.0)
        haircut_reasons.append(f"-{min(50, deal_breakers_count * 25)}% por {deal_breakers_count} Deal Breaker(s) Crítico(s)")

    if not has_unit_tests:
        haircut_pct += 25.0
        haircut_reasons.append("-25% por ausencia de suite de tests verificada (Caja Negra)")
    elif not has_coverage_gate:
        haircut_pct += 8.0
        haircut_reasons.append("-8% por cobertura formal no certificada (>80% Line Coverage)")

    god_count = arch_metrics.get("god_files_count", 0)
    if god_count > 0:
        pen = min(20.0, god_count * 5.0)
        haircut_pct += pen
        haircut_reasons.append(f"-{int(pen)}% por {god_count} archivo(s) monolítico(s) (>800 líneas)")

    if crit_funcs > 0:
        comp_pen = min(10.0, crit_funcs * 2.0)
        haircut_pct += comp_pen
        haircut_reasons.append(f"-{int(comp_pen)}% por {crit_funcs} función(es) con complejidad ciclomática crítica V(G)>20")

    if not has_billing:
        haircut_pct += 15.0
        haircut_reasons.append("-15% por ausencia de pasarela de cobro integrada (Turnkey Billing)")

    if sca.get("score", 100) < 90:
        haircut_pct += 10.0
        haircut_reasons.append("-10% por vulnerabilidades abiertas en cadena de suministro (SCA)")

    if not has_dast_headers:
        haircut_pct += 3.0
        haircut_reasons.append("-3% por ausencia de cabeceras de blindaje HTTP DAST (CSP / HSTS / X-Frame-Options)")

    # Bonificación de compresión de riesgo por capacidades Élite (Fuzzing, Chaos, Mutation, E2E, Runtime Contracts)
    if has_pbt_fuzzing and has_chaos and has_mutation and has_e2e and zero_critical_complexity and has_dast_headers:
        haircut_pct = max(0.0, haircut_pct - 8.0)

    haircut_pct = min(75.0, round(haircut_pct, 1))

    # 3. Determinación de Tier Institucional y Multiplicador ARR
    if global_score >= 92 and haircut_pct == 0.0 and elite_count >= 13 and zero_critical_complexity:
        tier = "Tier 1 — Sovereign Institutional (Big Tech Golden Path)"
        arr_multiple = "4.8x – 6.5x ARR"
        turnkey_status = "LISTO PARA ADQUISICIÓN INMEDIATA (0% Haircut Técnico • Estándar Grandes Ligas)"
    elif global_score >= 90 and haircut_pct <= 15.0:
        tier = "Tier 2 — Institutional Grade (M&A Ready)"
        arr_multiple = "3.8x – 5.0x ARR"
        turnkey_status = "APTO PARA DATA ROOM DE INVERSIÓN"
    elif global_score >= 80:
        tier = "Tier 3 — Commercial Grade (Scale-Up)"
        arr_multiple = "2.8x – 3.7x ARR"
        turnkey_status = "APTO CON SANEAMIENTO MENOR"
    elif global_score >= 65:
        tier = "Tier 4 — Solo-Founder MVP"
        arr_multiple = "1.5x – 2.5x ARR"
        turnkey_status = "REQUIERE FORTIFICACIÓN PREVIA A M&A"
    else:
        tier = "Tier 5 — Experimental / High Technical Debt"
        arr_multiple = "0.5x – 1.2x ARR (Valor de Activo Base)"
        turnkey_status = "NO APTO PARA COMPRAVENTA INSTITUCIONAL"

    return {
        "tier": tier,
        "haircut_pct": haircut_pct,
        "haircut_reasons": haircut_reasons,
        "arr_multiple": arr_multiple,
        "turnkey_status": turnkey_status,
        "elite_capabilities": elite_capabilities,
        "elite_score_ratio": f"{elite_count}/{total_elite}",
    }
