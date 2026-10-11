# -*- coding: utf-8 -*-
"""
V-GUARD Due Diligence Suite - Módulo de Ergonomía de Formularios, Accesibilidad & UX Móvil (Pilar 7)
Analiza componentes frontend (.jsx, .tsx, .html, .vue) para detectar barreras de usabilidad móvil:
- Inputs de email sin autocomplete, name o autoCapitalize='none'.
- Inputs de contraseña sin autocomplete compatible con Google/Apple Password Manager.
- Modales fijos bloqueantes sin botón de escape o sin modo invitado.
- Falta de sanitización .trim() en captura de credenciales.
- Problemas de accesibilidad (labels, aria-label, ids) y contraste de autofill.
"""
import os
import re
from pathlib import Path

IGNORE_DIRS = {
    "node_modules", ".git", ".venv", "venv", "__pycache__", "dist",
    "build", ".expo", ".next", ".cache", "coverage", "scratch"
}

FRONTEND_EXTS = {".jsx", ".tsx", ".html", ".htm", ".vue"}

def audit_frontend_forms(project_path: str) -> dict:
    root = Path(project_path)
    if not root.exists():
        return {
            "pilar": "Ergonomía de Formularios & UX Móvil",
            "score": 0,
            "status": "ERROR",
            "findings": [{"severity": "CRITICAL", "title": "Ruta no encontrada", "detail": str(project_path)}],
            "metrics": {}
        }

    findings = []
    total_form_files = 0
    total_inputs_checked = 0
    flaws_count = 0

    has_autofill_css = False

    # Revisar si hay reglas de autofill en CSS/SCSS
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]
        for fname in filenames:
            if fname.endswith((".css", ".scss", ".pcss", ".sass")):
                fpath = Path(dirpath) / fname
                try:
                    content = fpath.read_text(encoding="utf-8", errors="ignore")
                    if "-webkit-autofill" in content:
                        has_autofill_css = True
                        break
                except Exception:
                    pass
        if has_autofill_css:
            break

    # Escanear archivos frontend
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]

        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in FRONTEND_EXTS:
                continue

            full_path = Path(dirpath) / fname
            if ".min." in fname or "test" in fname.lower() or "spec" in fname.lower():
                continue

            try:
                content = full_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            rel_path = full_path.relative_to(root).as_posix()
            lines = content.splitlines()

            # Detectar si el archivo contiene inputs
            has_inputs = "<input" in content or "TextInput" in content
            if not has_inputs:
                continue

            total_form_files += 1

            # 1. Analizar cada tag <input ...>
            input_tags = re.finditer(r'<input\b([^>]*)>', content, flags=re.IGNORECASE)
            file_has_email_input = False
            file_has_password_input = False

            for match in input_tags:
                total_inputs_checked += 1
                tag_attrs = match.group(1)
                match_start = match.start()
                line_no = content[:match_start].count("\n") + 1

                # Tipo de input
                type_match = re.search(r'type=["\']([^"\']+)["\']', tag_attrs, re.IGNORECASE)
                input_type = type_match.group(1).lower() if type_match else "text"

                is_email = (input_type == "email") or ("email" in tag_attrs.lower() and input_type == "text")
                is_password = (input_type == "password")

                if is_email:
                    file_has_email_input = True
                    # Check autoComplete
                    if not re.search(r'autocomplete=["\']email["\']', tag_attrs, re.IGNORECASE):
                        findings.append({
                            "severity": "HIGH",
                            "title": "Input de Email sin autoComplete='email'",
                            "detail": f"En {rel_path}, el campo de correo carece de autoComplete='email'. Esto impide que los teclados móviles y gestores del navegador sugieran la cuenta del usuario en 1 clic.",
                            "file": rel_path,
                            "line": line_no
                        })
                        flaws_count += 1

                    # Check name attribute
                    if not re.search(r'name=["\']email["\']', tag_attrs, re.IGNORECASE) and not re.search(r'name=["\'][^"\']*email[^"\']*["\']', tag_attrs, re.IGNORECASE):
                        findings.append({
                            "severity": "HIGH",
                            "title": "Input de Email sin atributo name",
                            "detail": f"En {rel_path}, el input no declara name='email'. Vital para el guardado nativo de contraseñas de Android/iOS.",
                            "file": rel_path,
                            "line": line_no
                        })
                        flaws_count += 1

                    # Check autoCapitalize
                    if not re.search(r'autocapitalize=["\']none["\']', tag_attrs, re.IGNORECASE):
                        findings.append({
                            "severity": "MEDIUM",
                            "title": "Input de Email sin autoCapitalize='none'",
                            "detail": f"En {rel_path}, el campo de correo no desactiva la autocapitalización. Los teclados móviles capitalizarán la primera letra por defecto, causando rechazos de autenticación.",
                            "file": rel_path,
                            "line": line_no
                        })
                        flaws_count += 1

                if is_password:
                    file_has_password_input = True
                    # Check autoComplete
                    if not re.search(r'autocomplete=["\'](current-password|new-password)["\']', tag_attrs, re.IGNORECASE):
                        findings.append({
                            "severity": "HIGH",
                            "title": "Input de Contraseña sin autoComplete estándar",
                            "detail": f"En {rel_path}, el campo de password carece de autoComplete='current-password' o 'new-password'. Bloquea la inserción automática desde Google Passwords / Apple Keychain.",
                            "file": rel_path,
                            "line": line_no
                        })
                        flaws_count += 1

                # Check accessibility: label / aria-label / id
                has_aria = "aria-label" in tag_attrs or "aria-labelledby" in tag_attrs
                has_id = re.search(r'id=["\']([^"\']+)["\']', tag_attrs) is not None
                has_placeholder = re.search(r'placeholder=["\']([^"\']+)["\']', tag_attrs) is not None

                if not has_aria and not has_id and not has_placeholder:
                    findings.append({
                        "severity": "MEDIUM",
                        "title": "Input sin etiqueta accesible (a11y)",
                        "detail": f"En {rel_path}, el input carece de id para asociar <label>, aria-label o placeholder informativo.",
                        "file": rel_path,
                        "line": line_no
                    })
                    flaws_count += 1

            # 2. Check sanitización con .trim() si maneja emails
            if file_has_email_input:
                has_trim_in_project = ".trim()" in content
                if not has_trim_in_project and ext in [".html", ".htm"]:
                    has_trim_in_project = any(
                        ".trim()" in (Path(dp) / fn).read_text(encoding="utf-8", errors="ignore")
                        for dp, _, fns in os.walk(root)
                        for fn in fns if fn.endswith((".js", ".ts")) and not fn.startswith(".") and "node_modules" not in dp and "scratch" not in dp
                    )
                if not has_trim_in_project:
                    findings.append({
                        "severity": "HIGH",
                        "title": "Captura de credenciales sin sanitización .trim()",
                        "detail": f"En {rel_path}, el componente maneja campos de correo pero no ejecuta .trim() al procesar el estado o el envío. Los teclados móviles añaden espacios finales invisibles que rompen la autenticación.",
                        "file": rel_path
                    })
                    flaws_count += 1

            # 3. Check modales bloqueantes de inicio/login
            is_login_modal = ("login" in fname.lower() or "auth" in fname.lower() or "lobby" in fname.lower()) and ("modal" in content.lower() or "fixed" in content or "absolute" in content)
            if is_login_modal:
                # Comprobar si hay forma de cerrar o continuar como invitado
                has_close_btn = bool(re.search(r'(✕|&times;|Cerrar|Salir|close|onClose|handleCerrar|dismiss)', content, re.IGNORECASE))
                has_guest_mode = bool(re.search(r'(invitado|guest|demo|omitir|explorar|continuar sin cuenta)', content, re.IGNORECASE))

                if not has_close_btn and not has_guest_mode:
                    findings.append({
                        "severity": "CRITICAL",
                        "title": "Modal de Autenticación Bloqueante ('Modal Jail')",
                        "detail": f"En {rel_path}, el modal de autenticación no ofrece botón de cierre ni opción de explorar como invitado. Si el usuario no tiene cuenta o falla la red, queda atrapado con pantalla bloqueada.",
                        "file": rel_path
                    })
                    flaws_count += 2

                # Comprobar si tiene overflow para teclados móviles
                if "overflow-y-auto" not in content and "overflow: auto" not in content and "overflowY" not in content:
                    findings.append({
                        "severity": "MEDIUM",
                        "title": "Modal con overlay sin overflow de desplazamiento",
                        "detail": f"En {rel_path}, el modal no define scroll vertical explícito. Al abrir el teclado virtual en smartphones compactos, los botones de acción quedarán fuera del viewport inaccesibles.",
                        "file": rel_path
                    })
                    flaws_count += 1

    # Si hay formularios pero no hay soporte CSS para autofill
    if total_form_files > 0 and not has_autofill_css:
        findings.append({
            "severity": "LOW",
            "title": "Ausencia de reglas CSS para :-webkit-autofill",
            "detail": "El proyecto contiene formularios interactivos pero no anula los estilos por defecto del navegador para :-webkit-autofill. Esto suele causar fondos blancos con texto ilegible en temas oscuros.",
            "file": "Global CSS"
        })
        flaws_count += 0.5

    # Si no hay archivos frontend con formularios
    if total_form_files == 0:
        return {
            "pilar": "Ergonomía de Formularios & UX Móvil",
            "score": 100,
            "status": "APROBADO (N/A)",
            "summary": "No se detectaron formularios interactivos ni componentes frontend en este proyecto.",
            "findings": [],
            "metrics": {
                "total_form_files": 0,
                "total_inputs_checked": 0,
                "flaws_count": 0
            }
        }

    # Calcular score
    penalty = flaws_count * 8
    score = max(0, min(100, round(100 - penalty, 1)))

    status = "EXCELENTE" if score >= 90 else ("ACEPTABLE" if score >= 70 else ("DEFICIENTE" if score >= 50 else "CRÍTICO"))

    summary = f"Auditados {total_form_files} archivos frontend y {total_inputs_checked} campos de entrada. Se detectaron {len(findings)} observaciones ergonómicas."
    if score >= 90:
        summary += " Los formularios implementan estándares modernos de UX móvil y autocompletado nativo."
    else:
        summary += " Requiere corrección de atributos móviles (autocomplete, autoCapitalize, sanitización .trim y modales con escape)."

    return {
        "pilar": "Ergonomía de Formularios & UX Móvil",
        "score": score,
        "status": status,
        "summary": summary,
        "findings": findings,
        "metrics": {
            "total_form_files": total_form_files,
            "total_inputs_checked": total_inputs_checked,
            "flaws_count": flaws_count,
            "has_autofill_css": has_autofill_css
        }
    }
