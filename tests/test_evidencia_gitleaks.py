"""Evidencia versionada del escaneo de gitleaks (calidad/evidencia/): coherencia interna y ausencia de datos privados.

No ejecuta gitleaks (es un binario externo); comprueba que el resumen y los reportes versionados sean coherentes entre sí, que
no contengan rutas privadas ni valores, y que la documentación no afirme que gitleaks corre en CI mientras no lo haga.
"""
import hashlib
import json
import re
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
EVID = RAIZ / "calidad" / "evidencia"
RESUMEN = EVID / "gitleaks-8.30.1-resumen.json"


def _resumen():
    return json.loads(RESUMEN.read_text(encoding="utf-8"))


def test_el_resumen_tiene_version_comandos_alcance_fecha_resultado_y_limitaciones():
    r = _resumen()
    for clave in ("herramienta", "version", "origen", "binario", "fecha_utc", "reglas", "escaneos", "resultado", "no_escaneado", "limitaciones", "como_reproducir"):
        assert r.get(clave), clave
    assert r["herramienta"] == "gitleaks" and r["version"] == "8.30.1"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", r["fecha_utc"])
    assert r["binario"]["coincide"] is True and r["binario"]["sha256_zip"] == r["binario"]["sha256_publicado_en_checksums_txt"]
    assert re.fullmatch(r"[0-9a-f]{64}", r["binario"]["sha256_zip"]) and re.fullmatch(r"[0-9a-f]{64}", r["binario"]["sha256_gitleaks_exe"])
    for e in r["escaneos"]:
        assert e["comando"].startswith("gitleaks git .") and "--redact" in e["comando"]  # los valores nunca se imprimen
        assert 0 < e["confirmaciones_escaneadas"] <= e["confirmaciones_en_el_alcance"]
        assert e["bytes_escaneados_aprox"] > 0 and isinstance(e["codigo_de_salida"], int)


def test_el_resultado_global_es_coherente_con_los_escaneos_y_los_reportes():
    r = _resumen()
    for e in r["escaneos"]:
        reporte = EVID / f"gitleaks-8.30.1-reporte-{e['nombre']}.json"
        datos = reporte.read_bytes()
        assert hashlib.sha256(datos).hexdigest() == e["sha256_del_reporte"], "el reporte versionado no es el que describe el resumen"
        assert len(json.loads(datos)) == e["hallazgos"]
    limpio = all(e["hallazgos"] == 0 and e["codigo_de_salida"] == 0 for e in r["escaneos"])
    assert (r["resultado"] == "SIN HALLAZGOS") == limpio


def test_la_evidencia_no_contiene_rutas_privadas_nombres_ni_correos():
    for archivo in EVID.glob("gitleaks-8.30.1-*"):
        t = archivo.read_text(encoding="utf-8")
        assert not re.search(r"(?i)(C:\\\\|C:/|/Users/|\\\\Users\\\\|AppData|scratchpad|LESLIE~1|Leslie Valadez)", t), archivo.name
        assert not re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", t), archivo.name
        assert "Secret" not in t or archivo.name.endswith("resumen.json")  # un reporte con hallazgos traería el campo Secret (aunque redactado)


def test_la_integracion_en_ci_esta_declarada_y_coincide_con_ci_yml():
    """El resumen y seguridad.md declaran el trabajo de CI; deben coincidir con ci.yml (versión y hash) y no afirmar una ejecución real."""
    r = _resumen()
    ci_info = r["integracion_ci"]
    assert ci_info["ejecucion_en_github"] == "pendiente" or ci_info["ejecucion_en_github"].startswith("http")
    ci = yaml.safe_load((RAIZ / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8"))
    assert ci_info["trabajo"] in ci["jobs"]
    comandos = " ".join(p.get("run", "") for p in ci["jobs"][ci_info["trabajo"]]["steps"])
    assert ci_info["sha256_binario"] in comandos and f"v{ci_info['version_gitleaks']}/" in comandos
    assert not any("NO está integrado en CI" in x for x in r["limitaciones"])           # ya lo está: el resumen no puede decir lo contrario
    seguridad = (RAIZ / "docs" / "E1" / "seguridad.md").read_text(encoding="utf-8")
    assert ci_info["sha256_binario"] in seguridad and "trabajo `secretos`" in seguridad
