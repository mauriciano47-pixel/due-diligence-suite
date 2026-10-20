# -*- coding: utf-8 -*-
"""
V-GUARD Due Diligence Suite - Time-Series Telemetry & Trend Tracker
Registra el historial continuo de auditorías para detectar regresiones y
demostrar la evolución técnica y de valuación M&A a lo largo del tiempo.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
HISTORY_FILE = DATA_DIR / "audit_history.jsonl"

def record_audit_event(audit_result: Dict[str, Any]) -> None:
    """
    Registra un evento de auditoría en el archivo de series temporales (append-only).
    """
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        val = audit_result.get("valuation", {})
        arch_metrics = audit_result.get("pillars", {}).get("architecture", {}).get("metrics", {})
        gov_metrics = audit_result.get("pillars", {}).get("governance", {}).get("metrics", {})

        event = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "app_key": audit_result.get("app_key", "custom"),
            "app_name": audit_result.get("app_name", "Unknown"),
            "global_score": audit_result.get("global_score", 0),
            "grade": audit_result.get("grade", "N/A"),
            "tier": val.get("tier", "N/A"),
            "arr_multiple": val.get("arr_multiple", "N/A"),
            "haircut_pct": val.get("haircut_pct", 0.0),
            "elite_weapons": val.get("elite_score_ratio", "N/A"),
            "deal_breakers": audit_result.get("deal_breakers_count", 0),
            "sloc": arch_metrics.get("total_code_lines", 0),
            "tests_pass_pct": arch_metrics.get("tests_pass_pct", 0.0),
            "commit_hash": gov_metrics.get("last_commit_hash", "N/A")
        }

        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        pass

def get_app_history(app_key: str, limit: int = 15) -> List[Dict[str, Any]]:
    """
    Obtiene los últimos N registros históricos de una aplicación.
    """
    if not HISTORY_FILE.exists():
        return []

    records = []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                    if ev.get("app_key") == app_key:
                        records.append(ev)
                except Exception:
                    continue
    except Exception:
        return []

    return records[-limit:]

def calculate_trend(app_key: str, current_score: float, current_haircut: float) -> Dict[str, Any]:
    """
    Compara el escaneo actual con el último escaneo previo para calcular el delta de tendencia.
    """
    history = get_app_history(app_key)
    if len(history) < 2:
        return {
            "has_history": False,
            "score_delta": 0.0,
            "haircut_delta": 0.0,
            "trend_symbol": "✨",
            "summary": "Primer registro histórico verificado en telemetría."
        }

    prev = history[-2] # El penúltimo evento
    score_delta = round(current_score - prev.get("global_score", current_score), 1)
    haircut_delta = round(current_haircut - prev.get("haircut_pct", current_haircut), 1)

    trend_symbol = "🟢 ↗" if score_delta > 0 else ("🟡 →" if score_delta == 0 else "🔴 ↘")
    score_sign = f"+{score_delta}" if score_delta > 0 else f"{score_delta}"
    haircut_sign = f"+{haircut_delta}" if haircut_delta > 0 else f"{haircut_delta}"

    return {
        "has_history": True,
        "score_delta": score_delta,
        "haircut_delta": haircut_delta,
        "trend_symbol": trend_symbol,
        "previous_date": prev.get("timestamp", "Desconocida"),
        "summary": f"{trend_symbol} Score: {score_sign} pts | Haircut Deuda: {haircut_sign}% (vs {prev.get('timestamp')})"
    }
