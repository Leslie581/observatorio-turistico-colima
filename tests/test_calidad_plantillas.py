"""Compatibilidad de las plantillas PSP de ambos integrantes (no valida contenido de B)."""
import csv
from pathlib import Path

CAL = Path(__file__).resolve().parent.parent / "calidad"
KIT_TIEMPO = ["fecha", "inicio", "fin", "interrupcion_min", "fase", "actividad"]
KIT_DEFECTOS = ["numero", "fecha", "tipo", "fase_introducido", "fase_eliminado", "minutos_correccion",
                "defecto_origen", "descripcion"]
TIPOS_PSP = {"documentacion", "sintaxis", "construccion", "asignacion", "interfaz", "verificacion",
             "datos", "funcion", "sistema", "entorno"}


def _leer(nombre):
    with open(CAL / nombre, encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def test_las_plantillas_de_tiempo_de_ambos_son_compatibles_y_conservan_las_columnas_del_kit():
    ha, _ = _leer("tiempo-integrante-a.csv")
    hb, _ = _leer("tiempo-integrante-b.csv")
    assert ha == hb == KIT_TIEMPO + ["minutos_estimados"]


def test_las_plantillas_de_defectos_conservan_las_columnas_del_kit():
    for n in ("a", "b"):
        assert _leer(f"defectos-integrante-{n}.csv")[0] == KIT_DEFECTOS


def test_tiempos_retrospectivos_no_inventan_horarios():
    _, filas = _leer("tiempo-integrante-a.csv")
    retro = [f for f in filas if "RETROSPECTIVO" in f["actividad"]]
    assert retro and sum(int(f["minutos_estimados"]) for f in retro) == 720
    for f in retro:
        assert f["inicio"] == f["fin"] == f["interrupcion_min"] == "" and f["fecha"]


def test_defectos_a_usan_tipos_psp_y_no_inventan_minutos():
    _, filas = _leer("defectos-integrante-a.csv")
    assert filas and all(f["tipo"] in TIPOS_PSP and f["minutos_correccion"] == "" for f in filas)
    assert not any("duplicad" in f["descripcion"].lower() and "fecha" in f["descripcion"].lower() for f in filas)
    assert not any("manova" in f["descripcion"].lower() for f in filas)  # MANOVA es riesgo, no defecto


def test_b_no_tiene_datos_precargados():
    assert _leer("tiempo-integrante-b.csv")[1] == [] and _leer("defectos-integrante-b.csv")[1] == []
