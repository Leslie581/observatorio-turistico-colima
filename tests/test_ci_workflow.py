"""Estructura de ci.yml y garantía de que la captura diaria NO depende de las librerías opcionales del laboratorio.

Comprueba la ESTRUCTURA de los archivos; no demuestra que el flujo funcione en GitHub (eso exige una ejecución real).
"""
from pathlib import Path

import pytest
import yaml

RAIZ = Path(__file__).resolve().parent.parent
CI = RAIZ / ".github" / "workflows" / "ci.yml"
CAPTURA = RAIZ / ".github" / "workflows" / "captura-diaria.yml"


def _carga(ruta):
    return yaml.safe_load(ruta.read_text(encoding="utf-8"))


def _comandos(wf, job):
    return "\n".join(p.get("run", "") for p in wf["jobs"][job]["steps"])


def test_ci_corre_en_cada_push_y_pull_request_con_permisos_minimos():
    wf = _carga(CI)
    assert set(wf.get("on", wf.get(True))) == {"push", "pull_request"}
    assert wf["permissions"] == {"contents": "read"}
    assert "secrets." not in CI.read_text(encoding="utf-8").replace("# ", "")  # sin secretos


def test_ci_exige_las_pruebas_de_pronosticos_y_corre_linter_pruebas_y_puerta_de_datos():
    wf = _carga(CI)
    assert wf["jobs"]["calidad"]["env"]["TDL_EXIGIR_PRONOSTICOS"] == "1"
    cmd = _comandos(wf, "calidad")
    for esperado in ("-r requirements-lab.txt", "ruff check", "pytest -q -rs", "pipeline.ejecutar", "pipeline.verificar_e0"):
        assert esperado in cmd, esperado
    assert cmd.index("ruff check") < cmd.index("pytest") < cmd.index("pipeline.ejecutar")
    assert not any(p.get("continue-on-error") for p in wf["jobs"]["calidad"]["steps"])  # un cambio que rompe algo no entra


def test_la_auditoria_de_dependencias_va_aparte_y_no_bloquea_el_job_de_calidad():
    wf = _carga(CI)
    assert "pip_audit" in _comandos(wf, "auditoria-dependencias") and "pip_audit" not in _comandos(wf, "calidad")


def test_ci_declara_que_esta_sin_ejecutar():
    assert "SIN EJECUTAR" in CI.read_text(encoding="utf-8")


def test_la_captura_diaria_no_instala_las_dependencias_opcionales_del_laboratorio():
    wf = _carga(CAPTURA)
    cmd = _comandos(wf, "capturar")
    assert "-r requirements.txt" in cmd
    assert "requirements-lab" not in cmd and "requirements-dev" not in cmd and "TDL_EXIGIR_PRONOSTICOS" not in str(wf)


def test_el_nucleo_de_requirements_no_incluye_librerias_del_laboratorio():
    nucleo = (RAIZ / "requirements.txt").read_text(encoding="utf-8").lower()
    for opcional in ("statsmodels", "scipy", "matplotlib", "ruff", "pip-audit"):
        assert f"\n{opcional}==" not in nucleo
    assert "\npandera==" in nucleo and "\npandas==" in nucleo


@pytest.mark.parametrize("archivo", ["requirements-lab.txt", "requirements-dev.txt"])
def test_dependencias_opcionales_estan_fijadas_con_version_exacta(archivo):
    lineas = [x for x in (RAIZ / archivo).read_text(encoding="utf-8").splitlines() if x and not x.startswith("#")]
    assert lineas and all("==" in x for x in lineas)
