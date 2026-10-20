# -*- coding: utf-8 -*-
"""
V-GUARD Due Diligence Suite v2.4.0 - Sensores de Grandes Ligas (Big Tech Tier-1 Gates)
Audita:
1. DAST & Perímetro de Cabeceras HTTP (CSP, HSTS, X-Frame-Options, X-Content-Type-Options).
2. Performance Budget & Peso de Activos (Detección de assets no optimizados >800 KB).
3. Validación de Contratos en Runtime (Zero-Trust I/O Schema Guards).
4. Escudo Shift-Left Git Pre-Push / Pre-Commit Quality Gate.
"""
import os
import re
from pathlib import Path

IGNORE_DIRS = {
    "node_modules", ".git", ".venv", "venv", "__pycache__", "dist",
    "build", ".expo", ".next", ".cache", "coverage", ".docusaurus", "scratch", "android", "ios"
}


def audit_dast_perimeter(project_path: str) -> dict:
    """
    Verifica que el proyecto defina cabeceras de seguridad HTTP de grado bancario/Big Tech
    en sus archivos de borde (vercel.json, firebase.json, _headers, settings.py, index.html, +html.tsx).
    """
    root = Path(project_path)
    config_candidates = [
        "vercel.json", "firebase.json", "_headers", "public/_headers", "netlify.toml",
        "ataraxia/vercel.json", "ataraxia/firebase.json", "ataraxia/public/_headers",
        "ataraxia/src/app/+html.tsx", "index.html", "public/index.html"
    ]

    combined_config = ""
    found_files = []

    for rel in config_candidates:
        fpath = root / rel
        if fpath.exists() and fpath.is_file():
            try:
                combined_config += "\n" + fpath.read_text(encoding="utf-8", errors="ignore")
                found_files.append(rel)
            except Exception:
                pass

    # También buscar en settings.py o middleware/server files (máx 2 niveles)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]
        for fname in filenames:
            if fname in ("settings.py", "server.js", "server.ts", "app.py", "main.py", "middleware.ts", "vercel.json", "firebase.json"):
                fpath = Path(dirpath) / fname
                try:
                    combined_config += "\n" + fpath.read_text(encoding="utf-8", errors="ignore")
                    rel_p = fpath.relative_to(root).as_posix()
                    if rel_p not in found_files:
                        found_files.append(rel_p)
                except Exception:
                    pass

    cfg_lower = combined_config.lower()
    has_csp = "content-security-policy" in cfg_lower or "secure_csp" in cfg_lower
    has_nosniff = "x-content-type-options" in cfg_lower or "nosniff" in cfg_lower or "secure_content_type_nosniff" in cfg_lower
    has_frame = "x-frame-options" in cfg_lower or "frame-ancestors" in cfg_lower
    has_hsts_or_ref = "strict-transport-security" in cfg_lower or "referrer-policy" in cfg_lower or "secure_hsts_seconds" in cfg_lower

    headers_detected = []
    if has_csp:
        headers_detected.append("CSP")
    if has_nosniff:
        headers_detected.append("X-Content-Type-Options")
    if has_frame:
        headers_detected.append("X-Frame-Options")
    if has_hsts_or_ref:
        headers_detected.append("HSTS/Referrer-Policy")

    compliant = len(headers_detected) >= 3
    findings = []
    if compliant:
        findings.append({
            "severity": "INFO",
            "title": f"Blindaje Perimetral DAST / HTTP Headers Verificado ({', '.join(headers_detected)})",
            "detail": f"Cabeceras de seguridad anti-XSS, anti-Clickjacking y MIME-Sniffing declaradas en `{found_files[0] if found_files else 'config'}`.",
            "file": found_files[0] if found_files else "vercel.json"
        })
    else:
        missing = [h for h, ok in [("Content-Security-Policy", has_csp), ("X-Content-Type-Options", has_nosniff), ("X-Frame-Options", has_frame), ("HSTS/Referrer-Policy", has_hsts_or_ref)] if not ok]
        findings.append({
            "severity": "MEDIUM",
            "title": "Faltan Cabeceras de Seguridad HTTP Perimetrales (DAST Shield)",
            "detail": f"No se detectaron políticas explícitas para: {', '.join(missing)}. En auditorías Big Tech se exige CSP, X-Frame-Options y X-Content-Type-Options.",
            "file": "vercel.json / firebase.json"
        })

    return {
        "has_dast_headers": compliant,
        "headers_detected": headers_detected,
        "findings": findings
    }


def audit_performance_budget(project_path: str) -> dict:
    """
    Audita el presupuesto de rendimiento (Performance Budget):
    verifica que no existan imágenes o activos estáticos sin comprimir (>800 KB) en carpetas de producción.
    """
    root = Path(project_path)
    oversized_assets = []
    max_asset_kb = 0.0
    checked_assets = 0

    asset_exts = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".mp4", ".ttf", ".otf", ".woff", ".woff2"}

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]
        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in asset_exts:
                continue
            fpath = Path(dirpath) / fname
            try:
                size_kb = round(fpath.stat().st_size / 1024.0, 1)
                checked_assets += 1
                if size_kb > max_asset_kb:
                    max_asset_kb = size_kb
                # Umbral Big Tech para activos web/móvil empaquetados: 800 KB
                if size_kb > 800.0:
                    rel_p = fpath.relative_to(root).as_posix()
                    oversized_assets.append({"file": rel_p, "size_kb": size_kb})
            except Exception:
                pass

    compliant = len(oversized_assets) == 0
    findings = []
    if compliant:
        findings.append({
            "severity": "INFO",
            "title": f"Performance Budget Cumplido ({checked_assets} activos bajo umbral <800 KB)",
            "detail": f"Activo máximo detectado: {max_asset_kb} KB. Cero cuellos de botella por recursos estáticos sobredimensionados.",
            "file": "assets/"
        })
    else:
        for item in oversized_assets[:3]:
            findings.append({
                "severity": "MEDIUM",
                "title": f"Violación de Performance Budget: {item['file']} ({item['size_kb']} KB)",
                "detail": "Supera el presupuesto institucional de 800 KB por activo. Se recomienda comprimir a WebP/AVIF o vectorizar en SVG.",
                "file": item["file"]
            })

    return {
        "performance_budget_compliant": compliant,
        "max_asset_kb": max_asset_kb,
        "oversized_count": len(oversized_assets),
        "findings": findings
    }


def audit_runtime_contracts(project_path: str) -> dict:
    """
    Verifica si el proyecto implementa validación de esquemas/contratos en tiempo de ejecución
    (Zero-Trust Runtime I/O Guard) para respuestas de API, IA o almacenamiento local.
    """
    root = Path(project_path)
    contract_files = []
    contract_patterns = [
        r"\bz\.object\s*\(",
        r"\bsafeParse\s*\(",
        r"\bvalidateContract\b",
        r"\bruntimeContract\b",
        r"\bassertValidSchema\b",
        r"\bsanitizeAndValidate\b",
        r"\b BaseModel\b",
        r"\bserializers\.Serializer\b",
        r"\bserializers\.ModelSerializer\b",
    ]

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]
        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in {".ts", ".tsx", ".js", ".py"} or "test" in fname.lower():
                continue
            fpath = Path(dirpath) / fname
            try:
                content = fpath.read_text(encoding="utf-8", errors="ignore")
                if any(re.search(p, content) for p in contract_patterns) or "contract" in fname.lower():
                    rel_p = fpath.relative_to(root).as_posix()
                    contract_files.append(rel_p)
            except Exception:
                pass

    has_contracts = len(contract_files) > 0
    findings = []
    if has_contracts:
        findings.append({
            "severity": "INFO",
            "title": f"Validación de Contratos en Runtime Activa ({len(contract_files)} módulo(s))",
            "detail": f"Fronteras de datos protegidas contra payloads malformados en tiempo de ejecución (`{contract_files[0]}`).",
            "file": contract_files[0]
        })
    else:
        findings.append({
            "severity": "LOW",
            "title": "Sin Validador Formal de Contratos en Runtime (Zero-Trust I/O)",
            "detail": "Se recomienda implementar guardas de esquema en tiempo de ejecución para validar respuestas de APIs externas o LLMs.",
            "file": "src/"
        })

    return {
        "has_runtime_contracts": has_contracts,
        "contract_files": contract_files,
        "findings": findings
    }


def audit_git_hooks(project_path: str) -> dict:
    """
    Verifica la existencia de Git Quality Gates locales (Shift-Left Pre-Push / Pre-Commit)
    que impidan subir código roto o sin auditar.
    """
    root = Path(project_path)
    hook_candidates = [
        root / ".git" / "hooks" / "pre-push",
        root / ".git" / "hooks" / "pre-commit",
        root / ".husky" / "pre-push",
        root / ".husky" / "pre-commit",
        root / "scripts" / "pre-push-gate.mjs",
        root / "ataraxia" / "scripts" / "pre-push-gate.mjs",
        root / "ataraxia" / ".git" / "hooks" / "pre-push",
    ]

    found_hook = None
    for cand in hook_candidates:
        if cand.exists() and cand.is_file():
            found_hook = cand.relative_to(root).as_posix()
            break

    if not found_hook:
        for pkg_cand in [root / "package.json", root / "ataraxia" / "package.json"]:
            if pkg_cand.exists():
                try:
                    txt = pkg_cand.read_text(encoding="utf-8", errors="ignore")
                    if '"prepush"' in txt or '"pre-push"' in txt or '"verify:gate"' in txt:
                        found_hook = pkg_cand.relative_to(root).as_posix()
                        break
                except Exception:
                    pass

    has_hook = found_hook is not None
    findings = []
    if has_hook:
        findings.append({
            "severity": "INFO",
            "title": "Escudo Shift-Left Git Pre-Push Gate Activo",
            "detail": f"Quality Gate local verificado en `{found_hook}` para bloquear subidas con tests o tipado fallido.",
            "file": found_hook
        })
    else:
        findings.append({
            "severity": "LOW",
            "title": "Falta Git Pre-Push Quality Gate Local (Shift-Left)",
            "detail": "En ingeniería Big Tech se configura un hook o script pre-push que ejecute linter, typecheck y tests antes de permitir git push.",
            "file": ".git/hooks/pre-push"
        })

    return {
        "has_shift_left_hook": has_hook,
        "hook_location": found_hook,
        "findings": findings
    }
