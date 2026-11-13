"""Reproducibilidad, integridad de bronce y fallo controlado del orquestador (datos SINTÉTICOS)."""
import hashlib
import json
from pathlib import Path

from pipeline.ejecutar import ejecutar
from tests.pipeline_helpers import arbol_completo, escribir_base70, filas_manzanillo

AHORA = "2026-11-13T00:00:00+00:00"


def _huellas(carpeta: Path) -> dict:
    return {p.relative_to(carpeta).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(carpeta.rglob("*")) if p.is_file()}


def test_dos_ejecuciones_con_la_misma_entrada_dan_archivos_identicos_byte_a_byte(tmp_path):
    arbol_completo(tmp_path)
    ejecutar(tmp_path, ahora=AHORA)
    antes = {k: v for k, v in _huellas(tmp_path / "data").items() if not k.startswith("bronce/")}
    ejecutar(tmp_path, ahora=AHORA)
    despues = {k: v for k, v in _huellas(tmp_path / "data").items() if not k.startswith("bronce/")}
    assert antes == despues and "oro/manzanillo_ocupacion_mensual.csv" in antes


def test_otra_hora_de_proceso_solo_cambia_las_marcas_de_tiempo(tmp_path):
    arbol_completo(tmp_path)
    ejecutar(tmp_path, ahora=AHORA)
    csv1 = (tmp_path / "data/oro/manzanillo_ocupacion_mensual.csv").read_bytes()
    m1 = json.loads((tmp_path / "data/oro/manzanillo_ocupacion_mensual.meta.json").read_text(encoding="utf-8"))
    ejecutar(tmp_path, ahora="2026-12-01T10:00:00+00:00")
    assert (tmp_path / "data/oro/manzanillo_ocupacion_mensual.csv").read_bytes() == csv1  # el oro no depende de la hora
    m2 = json.loads((tmp_path / "data/oro/manzanillo_ocupacion_mensual.meta.json").read_text(encoding="utf-8"))
    assert {k for k in m1 if m1[k] != m2[k]} == {"fecha_proceso_utc"}


def test_el_pipeline_no_modifica_el_bronce(tmp_path):
    arbol_completo(tmp_path)
    antes = _huellas(tmp_path / "data" / "bronce")
    res = ejecutar(tmp_path, ahora=AHORA)
    assert res["estado"] == "ok" and _huellas(tmp_path / "data" / "bronce") == antes


def test_salidas_con_lf_y_sin_archivos_temporales(tmp_path):
    arbol_completo(tmp_path)
    ejecutar(tmp_path, ahora=AHORA)
    for p in (tmp_path / "data").rglob("*"):
        if p.is_file() and "bronce" not in p.parts:
            assert not p.name.endswith(".tmp") and b"\r" not in p.read_bytes(), p


def test_resumen_de_cuarentena_cuadra_y_se_escribe(tmp_path):
    arbol_completo(tmp_path)
    res = ejecutar(tmp_path, ahora=AHORA)
    resumen = json.loads(next((tmp_path / "data/cuarentena").glob("resumen_*.json")).read_text(encoding="utf-8"))
    for nombre, f in resumen["fuentes"].items():
        assert f["leidos"] == f["aceptados"] + f["rechazados"], nombre
    assert res["oro"]["manzanillo_ocupacion_mensual"] == 108


def test_fallo_controlado_no_escribe_plata_ni_oro_y_deja_evidencia(tmp_path):
    arbol_completo(tmp_path)
    base = tmp_path / "data/bronce/datatur/Base70centros.csv"
    base.write_bytes(base.read_bytes() + b"x")  # ya no coincide con su ficha
    res = ejecutar(tmp_path, ahora=AHORA)
    assert res["estado"] == "error_controlado" and res["regla"] == "INTEGRIDAD"
    assert not (tmp_path / "data/oro").exists() and not (tmp_path / "data/plata").exists()
    resumen = json.loads(next((tmp_path / "data/cuarentena").glob("resumen_fallida-*.json")).read_text(encoding="utf-8"))
    assert resumen["informativo"]["error_controlado"]["regla"] == "INTEGRIDAD"


def test_oro_incompleto_falla_en_lugar_de_publicar_una_serie_corta(tmp_path):
    escribir_base70(tmp_path, [f for f in filas_manzanillo() if f[0] != 2024])
    res = ejecutar(tmp_path, ahora=AHORA)
    assert res["estado"] == "error_controlado" and not (tmp_path / "data/oro").exists()
