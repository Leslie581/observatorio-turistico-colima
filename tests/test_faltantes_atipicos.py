"""Valores faltantes (diagnóstico y tratamientos) y atípicos (IQR frente a z robusto) de laboratorio/exploracion/.

Las series fabricadas son SINTÉTICAS y lo declaran; el resto usa el bronce real del repositorio, procesado por el pipeline en una
carpeta temporal (la plata no está versionada: no se puede suponer que exista en el momento de las pruebas).
"""
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from laboratorio.exploracion import atipicos as at
from laboratorio.exploracion import faltantes as fa
from pipeline.ejecutar import ejecutar

RAIZ = Path(__file__).resolve().parent.parent
BRONCE = RAIZ / "data" / "bronce"
ORO = RAIZ / "data" / "oro" / "manzanillo_ocupacion_mensual.csv"
pytestmark = pytest.mark.skipif(not (BRONCE / "datatur" / "Base70centros.csv").exists(), reason="sin bronce")


@pytest.fixture(scope="module")
def plata(tmp_path_factory):
    raiz = tmp_path_factory.mktemp("faltantes")
    shutil.copytree(BRONCE, raiz / "data" / "bronce")
    assert ejecutar(raiz, ahora="2026-11-14T00:00:00+00:00")["estado"] == "ok"
    return raiz / "data" / "plata" / "datatur_base70.csv"


# ------------------------------------------------------------------ lo que realmente falta
def test_el_inventario_encuentra_lo_que_realmente_falta(plata):
    inv, _, resumen = fa.calcular(ORO, plata)
    celdas = inv[inv.tipo == "celda_vacia"]
    assert len(celdas) == 1 and celdas.iloc[0].centro == "Mexicali" and "2020-03" in celdas.iloc[0].detalle and celdas.iloc[0].n == 1
    ausentes = inv[inv.tipo == "periodos_ausentes"]
    assert list(ausentes.centro) == ["El Fuerte"] and ausentes.iloc[0].n == 12 and "2024-01 a 2024-12" in ausentes.iloc[0].detalle
    assert resumen["faltantes_en_manzanillo"] == 0


def test_el_diagnostico_no_afirma_lo_que_no_se_puede_probar(plata):
    _, _, resumen = fa.calcular(ORO, plata)
    por_caso = {d["caso"].split(",")[0].split(" (")[0]: d for d in resumen["diagnostico"]}
    assert "no aplica" in por_caso["Manzanillo"]["mecanismo"] and "ninguno" in por_caso["Manzanillo"]["tratamiento"]
    assert por_caso["Mexicali"]["mecanismo"].startswith("INDETERMINADO") and "no se imputa" in por_caso["Mexicali"]["tratamiento"]
    assert por_caso["El Fuerte"]["mecanismo"].startswith("NO AL AZAR") and "no se imputa" in por_caso["El Fuerte"]["tratamiento"]


# ------------------------------------------------------------------ tratamientos (SINTÉTICAS)
def _mes(n=48):
    return np.asarray(pd.period_range("2016-01", periods=n, freq="M").month)


def _falta(n, posiciones):
    f = np.zeros(n, dtype=bool)
    f[list(posiciones)] = True
    return f


def test_una_serie_constante_se_reconstruye_exacta_con_todos_los_metodos():
    x, f = np.full(48, 50.0), _falta(48, [5, 20, 33])
    for m in fa.METODOS:
        assert np.allclose(fa.imputar(x, f, m, _mes())[f], 50.0), m


def test_la_interpolacion_lineal_es_exacta_en_una_recta_y_la_estacional_en_un_patron_anual():
    recta, f = np.arange(48, dtype=float), _falta(48, [10, 11, 30])
    assert np.allclose(fa.imputar(recta, f, "interpolacion_lineal", _mes())[f], recta[f])
    patron = np.tile(np.arange(12, dtype=float) * 3, 4)
    assert np.allclose(fa.imputar(patron, f, "interpolacion_estacional", _mes())[f], patron[f])


def test_media_y_mediana_usan_solo_valores_observados():
    x = np.array([10.0, 20.0, 30.0, 1000.0, 50.0])
    f = _falta(5, [3])
    assert fa.imputar(x, f, "media", np.arange(5))[3] == pytest.approx(27.5)
    assert fa.imputar(x, f, "mediana", np.arange(5))[3] == pytest.approx(25.0)               # el valor oculto no influye


def test_un_metodo_desconocido_se_rechaza():
    with pytest.raises(ValueError, match="desconocido"):
        fa.imputar(np.ones(5), _falta(5, [2]), "magia", np.arange(5))


# ------------------------------------------------------------------ simulación
def test_la_simulacion_solo_usa_el_entrenamiento_y_es_reproducible():
    from pipeline.interfaz import cargar_oro_mensual, partir_entrenamiento_prueba, serie_objetivo
    tr, te = partir_entrenamiento_prueba(serie_objetivo(cargar_oro_mensual(ORO)))
    a, b = fa.simular(tr, replicas=20), fa.simular(tr, replicas=20)
    assert a.equals(b)
    with pytest.raises(ValueError, match="2016-2023"):
        fa.simular(pd.concat([tr, te]), replicas=2)


def test_la_simulacion_muestra_el_sesgo_de_lo_que_falta_no_al_azar():
    from pipeline.interfaz import cargar_oro_mensual, partir_entrenamiento_prueba, serie_objetivo
    tr, _ = partir_entrenamiento_prueba(serie_objetivo(cargar_oro_mensual(ORO)))
    s = fa.simular(tr, replicas=30)
    alto = s[s.mecanismo == "no_al_azar_valores_altos"]
    assert (alto.sesgo < -5).all()                                     # ningún tratamiento corrige que falten justo los valores altos
    azar = s[s.mecanismo == "completamente_al_azar"]
    assert azar.loc[azar.rmse.idxmin(), "metodo"] == "interpolacion_lineal" and (azar.sesgo.abs() < 5).all()


def test_los_resultados_versionados_estan_al_dia(plata, tmp_path):
    fa.ejecutar(tmp_path, ORO, plata)
    for n in ("inventario_faltantes.csv", "imputacion_comparacion.csv", "resumen.json"):
        assert (tmp_path / n).read_bytes().replace(b"\r\n", b"\n") == (fa.SALIDA / n).read_bytes().replace(b"\r\n", b"\n"), n


# ------------------------------------------------------------------ atípicos
def test_el_z_robusto_coincide_con_la_formula_y_rechaza_un_mad_nulo():
    y = pd.Series([10.0, 12.0, 11.0, 13.0, 50.0])
    z = at.z_robusto(y)
    assert z.iloc[0] == pytest.approx(0.6745 * (10 - 12) / 1.0)                  # mediana 12, MAD 1
    assert z.iloc[4] == pytest.approx(0.6745 * 38 / 1.0) and z.abs().idxmax() == 4
    with pytest.raises(ValueError, match="MAD"):
        at.z_robusto(pd.Series([5.0, 5.0, 5.0, 5.0, 9.0]))


def test_iqr_y_z_robusto_coinciden_en_los_tres_meses_de_covid_y_ninguno_se_elimina():
    tabla, resumen = at.calcular(ORO)
    assert list(tabla.periodo) == ["2020-04", "2020-05", "2020-06"]
    assert resumen["senalados_iqr"] == resumen["senalados_z_robusto"] == resumen["senalados_por_ambos"] == 3
    assert resumen["solo_iqr"] == [] and resumen["solo_z_robusto"] == [] and resumen["senalados_fuera_de_covid"] == 0
    assert tabla.decision.str.startswith("MARCAR y conservar").all()
    assert len(pd.read_csv(ORO)) == 108                                        # el oro conserva los 108 meses


def test_los_resultados_de_atipicos_estan_al_dia(tmp_path):
    at.ejecutar(tmp_path, ORO)
    for n in ("comparacion_metodos.csv", "resumen.json"):
        assert (tmp_path / n).read_bytes().replace(b"\r\n", b"\n") == (at.SALIDA / n).read_bytes().replace(b"\r\n", b"\n"), n
