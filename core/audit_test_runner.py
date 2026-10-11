# -*- coding: utf-8 -*-
"""
V-GUARD Due Diligence Suite - Verificador Dinámico de Pruebas (Test Execution Engine)
Ejecuta suites de test en tiempo real (npm test, node --test, pytest, unittest),
mide la tasa de éxito (Pass Rate), fallos y tiempo de ejecución.
Estándar M&A: Elimina la evaluación ciega basada en nombres de archivo y comprueba
la integridad operativa real del software.
"""
import os
import re
import sys
import json
import time
import subprocess
from pathlib import Path

def audit_test_runner(project_path: str) -> dict:
    root = Path(project_path)
    if not root.exists():
        return {
            "status": "ERROR",
            "executed": False,
            "pass_rate": 0.0,
            "findings": [{"severity": "CRITICAL", "title": "Ruta no encontrada", "detail": str(project_path)}],
            "metrics": {}
        }

    findings = []
    executed = False
    passed_count = 0
    failed_count = 0
    total_tests = 0
    suites_count = 0
    duration_s = 0.0
    runner_type = "None"
    raw_output = ""

    # 1. Detectar Node.js package.json con script 'test'
    pkg_file = root / "package.json"
    has_npm_test = False
    npm_test_cmd = None

    if pkg_file.exists():
        try:
            pkg_data = json.loads(pkg_file.read_text(encoding="utf-8", errors="ignore"))
            scripts = pkg_data.get("scripts", {})
            test_script = scripts.get("test", "")
            if test_script and "no test specified" not in test_script.lower():
                has_npm_test = True
                npm_test_cmd = test_script
        except Exception:
            pass

    # 2. Detectar Python tests (tests/ o test_*.py)
    has_python_tests = False
    py_files = list(root.glob("tests/test_*.py")) + list(root.glob("test_*.py"))
    if py_files:
        has_python_tests = True

    # 3. Ejecución dinámica
    npm_bin = "npm.cmd" if sys.platform == "win32" else "npm"

    if has_npm_test:
        runner_type = "Node.js Test Runner"
        start_t = time.time()
        try:
            proc = subprocess.run(
                [npm_bin, "test"],
                cwd=str(root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=25
            )
            duration_s = round(time.time() - start_t, 2)
            executed = True
            raw_output = (proc.stdout or "") + "\n" + (proc.stderr or "")

            # Parsing Node Test Runner nativo (node --test)
            # Ej: ℹ pass 20 / ℹ fail 0 / ℹ tests 20
            pass_m = re.search(r"ℹ\s*pass\s+(\d+)", raw_output)
            fail_m = re.search(r"ℹ\s*fail\s+(\d+)", raw_output)
            tests_m = re.search(r"ℹ\s*tests\s+(\d+)", raw_output)
            suites_m = re.search(r"ℹ\s*suites\s+(\d+)", raw_output)

            # Parsing Jest / Vitest
            # Ej: Tests:  20 passed, 20 total
            jest_pass = re.search(r"Tests:\s+(\d+)\s+passed", raw_output)
            jest_fail = re.search(r"Tests:\s+(\d+)\s+failed", raw_output)

            if pass_m:
                passed_count = int(pass_m.group(1))
                failed_count = int(fail_m.group(1)) if fail_m else 0
                total_tests = int(tests_m.group(1)) if tests_m else (passed_count + failed_count)
                suites_count = int(suites_m.group(1)) if suites_m else 1
            elif jest_pass:
                passed_count = int(jest_pass.group(1))
                failed_count = int(jest_fail.group(1)) if jest_fail else 0
                total_tests = passed_count + failed_count
                suites_count = 1
            else:
                # Si salió con código 0 y no hubo match específico
                if proc.returncode == 0:
                    # Contar checks o asserciones si existen
                    checks_m = re.findall(r"[✔√]\s+(.+)", raw_output)
                    if checks_m:
                        passed_count = len(checks_m)
                        total_tests = passed_count
                    else:
                        passed_count = 1
                        total_tests = 1
                else:
                    failed_count = 1
                    total_tests = 1

            if proc.returncode != 0 or failed_count > 0:
                findings.append({
                    "severity": "CRITICAL",
                    "title": f"Fallo en Suite de Pruebas ({failed_count} pruebas fallidas)",
                    "detail": f"La ejecución de `npm test` finalizó con código de error {proc.returncode}. El código presenta regresiones activas.",
                    "file": "package.json"
                })
            else:
                findings.append({
                    "severity": "INFO",
                    "title": f"Suite de Pruebas Verificada ({passed_count}/{total_tests} exitosas)",
                    "detail": f"Ejecución dinámica exitosa en {duration_s}s ({suites_count} suites, {passed_count} aserciones aprobadas al 100%).",
                    "file": "package.json"
                })

        except subprocess.TimeoutExpired:
            duration_s = 25.0
            findings.append({
                "severity": "HIGH",
                "title": "Timeout en Suite de Pruebas (>25s)",
                "detail": "La ejecución de `npm test` excedió el tiempo límite. Posible bucle infinito o tests asíncronos sin cierre de conexiones.",
                "file": "package.json"
            })
        except Exception as e:
            findings.append({
                "severity": "MEDIUM",
                "title": "Error al ejecutar runner de pruebas",
                "detail": str(e),
                "file": "package.json"
            })

    elif has_python_tests:
        runner_type = "Python Unittest / Pytest"
        start_t = time.time()
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
                cwd=str(root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=20
            )
            duration_s = round(time.time() - start_t, 2)
            executed = True
            raw_output = (proc.stdout or "") + "\n" + (proc.stderr or "")

            ran_m = re.search(r"Ran\s+(\d+)\s+tests?", raw_output)
            if ran_m:
                total_tests = int(ran_m.group(1))
                if proc.returncode == 0 and "OK" in raw_output:
                    passed_count = total_tests
                    failed_count = 0
                else:
                    # Parsear fallos
                    fails_m = re.search(r"FAILED\s+\((?:failures=(\d+))?(?:,?\s*errors=(\d+))?\)", raw_output)
                    if fails_m:
                        f1 = int(fails_m.group(1) or 0)
                        f2 = int(fails_m.group(2) or 0)
                        failed_count = f1 + f2
                        passed_count = max(0, total_tests - failed_count)
                    else:
                        failed_count = 1
                        passed_count = max(0, total_tests - 1)
            else:
                if proc.returncode == 0:
                    passed_count = 1
                    total_tests = 1
                else:
                    failed_count = 1
                    total_tests = 1

            if proc.returncode != 0 or failed_count > 0:
                findings.append({
                    "severity": "CRITICAL",
                    "title": f"Fallo en pruebas Python ({failed_count} fallos)",
                    "detail": f"Unittest reportó fallos en tiempo de ejecución. Código de salida: {proc.returncode}.",
                    "file": "tests/"
                })
            else:
                findings.append({
                    "severity": "INFO",
                    "title": f"Suite de Pruebas Python Verificada ({passed_count}/{total_tests} exitosas)",
                    "detail": f"Pruebas unitarias ejecutadas con éxito en {duration_s}s sin fallos.",
                    "file": "tests/"
                })

        except subprocess.TimeoutExpired:
            duration_s = 20.0
            findings.append({
                "severity": "HIGH",
                "title": "Timeout en pruebas Python (>20s)",
                "detail": "La ejecución de pruebas unitarias excedió el tiempo límite.",
                "file": "tests/"
            })
        except Exception as e:
            findings.append({
                "severity": "MEDIUM",
                "title": "Error al invocar pruebas Python",
                "detail": str(e),
                "file": "tests/"
            })

    pass_rate = 100.0 if (total_tests > 0 and failed_count == 0) else (round((passed_count / total_tests) * 100, 1) if total_tests > 0 else 0.0)

    return {
        "executed": executed,
        "runner_type": runner_type,
        "total_tests": total_tests,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "pass_rate": pass_rate,
        "suites_count": suites_count,
        "duration_s": duration_s,
        "findings": findings
    }
