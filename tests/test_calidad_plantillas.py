"""Formato y coherencia de los registros PSP de ambos integrantes (no exige que estén vacíos)."""
import csv
import re
from datetime import date
from pathlib import Path

import pytest

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
    e0 = [f for f in retro if f["fecha"] < "2026-11-13"]
    assert e0 and sum(int(f["minutos_estimados"]) for f in e0) == 750  # E0: 480 prototipo + 240 definitivo + 30 auditoria posterior al PR #1
    for f in retro:
        assert f["inicio"] == f["fin"] == f["interrupcion_min"] == "" and f["fecha"]


def test_tiempos_aceptados_de_e1_por_bloque_y_suma_coherente():
    """Los bloques aceptados (L0 y L1, L2 y L3) no cambian; el total de E1 puede crecer con el cierre documental."""
    _, filas = _leer("tiempo-integrante-a.csv")
    e1 = [f for f in filas if f["fecha"] >= "2026-11-13" and "RETROSPECTIVO" in f["actividad"]]
    def suma(fs):
        return sum(int(f["minutos_estimados"]) for f in fs)
    l2 = [f for f in e1 if f["actividad"].rstrip().endswith("(L2)")]
    l3 = [f for f in e1 if f["actividad"].rstrip().endswith("(L3)")]
    l0_l1 = [f for f in e1 if f not in l2 and f not in l3 and "(cierre documental)" not in f["actividad"]]
    cierre = [f for f in e1 if "(cierre documental)" in f["actividad"]]
    assert (suma(l0_l1), suma(l2), suma(l3)) == (240, 150, 270)  # estimaciones aceptadas por la integrante A (2026-11-13)
    assert (len(l0_l1), len(l2), len(l3)) == (8, 5, 8)
    assert (len(cierre), suma(cierre)) == (7, 720)  # cierre documental: 7 actividades, estimaciones retrospectivas aceptadas por la integrante A (2026-11-13)
    assert suma(e1) == suma(l0_l1) + suma(l2) + suma(l3) + suma(cierre) == 1380  # E1 = 240 + 150 + 270 + 720; con E0 (750): 2,130


def test_defectos_a_usan_tipos_psp_y_no_inventan_minutos():
    _, filas = _leer("defectos-integrante-a.csv")
    assert filas and all(f["tipo"] in TIPOS_PSP and f["minutos_correccion"] == "" for f in filas)
    assert not any("duplicad" in f["descripcion"].lower() and "fecha" in f["descripcion"].lower() for f in filas)
    assert not any("manova" in f["descripcion"].lower() for f in filas)  # MANOVA es riesgo, no defecto


FASES = {"planeacion", "diseno", "codigo", "revision", "pruebas", "documentacion", "entrevista"}
HORA = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


@pytest.mark.parametrize("nombre", ["a", "b"])
def test_registros_de_tiempo_tienen_formato_y_coherencia(nombre):
    """Valida estructura, no contenido: las filas retrospectivas no inventan horario; las medidas lo tienen completo."""
    _, filas = _leer(f"tiempo-integrante-{nombre}.csv")
    for f in filas:
        date.fromisoformat(f["fecha"])                      # fecha ISO válida
        assert f["fase"] in FASES and f["actividad"].strip()
        if "RETROSPECTIVO" in f["actividad"]:               # estimación: sin horarios, con minutos > 0
            assert f["inicio"] == f["fin"] == f["interrupcion_min"] == ""
            assert int(f["minutos_estimados"]) > 0
        else:                                               # medida: horario real y sin minutos estimados
            assert HORA.match(f["inicio"]) and HORA.match(f["fin"]) and f["minutos_estimados"] == ""
            assert f["interrupcion_min"].isdigit() or f["interrupcion_min"] == ""


@pytest.mark.parametrize("nombre", ["a", "b"])
def test_registros_de_defectos_tienen_formato_y_coherencia(nombre):
    """Cero defectos es válido (archivo solo con encabezado); si hay filas, deben ser coherentes."""
    _, filas = _leer(f"defectos-integrante-{nombre}.csv")
    assert [int(f["numero"]) for f in filas] == list(range(1, len(filas) + 1))
    for f in filas:
        date.fromisoformat(f["fecha"]) if f["fecha"] else None
        assert f["tipo"] in TIPOS_PSP and f["descripcion"].strip()
        assert f["fase_introducido"] in FASES
        assert f["fase_eliminado"] in FASES | {""}
        assert f["minutos_correccion"] == "" or int(f["minutos_correccion"]) > 0


def test_b_conserva_sus_registros_propios_sin_horarios_inventados():
    """B puede tener registros (ya no se exige que estén vacíos); sus estimaciones siguen sin horario."""
    _, filas = _leer("tiempo-integrante-b.csv")
    for f in filas:
        if "RETROSPECTIVO" in f["actividad"]:
            assert f["inicio"] == f["fin"] == ""


def test_totales_de_a_separan_prototipo_de_desarrollo_formal():
    _, filas = _leer("tiempo-integrante-a.csv")
    def suma(fs):
        return sum(int(f["minutos_estimados"]) for f in fs)
    proto = [f for f in filas if "[PROTOTIPO]" in f["actividad"]]
    formal = [f for f in filas if "[PROTOTIPO]" not in f["actividad"]]
    assert (suma(proto), suma(formal), suma(filas)) == (480, 1650, 2130)


def test_defectos_de_a_tienen_numeracion_continua_y_sin_duplicados():
    _, filas = _leer("defectos-integrante-a.csv")
    assert [int(f["numero"]) for f in filas] == list(range(1, len(filas) + 1)) and len(filas) == 28
    assert len({f["descripcion"] for f in filas}) == len(filas)
