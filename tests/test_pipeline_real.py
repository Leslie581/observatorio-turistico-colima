"""El pipeline sobre el BRONCE REAL del repositorio (se copia a una carpeta temporal: no se escribe en data/).

Cifras de Base70 estables (archivo congelado, SHA-256 a8ca3f9b…). DENUE crece con cada captura del bot,
por eso solo se comprueban invariantes, no totales.
"""
import shutil
from pathlib import Path

import pandas as pd
import pytest

from extractores.datatur import leer_base70
from pipeline.ejecutar import ejecutar
from pipeline.interfaz import cargar_oro_mensual, partir_entrenamiento_prueba, serie_objetivo
from pipeline.verificar_e0 import integridad

RAIZ = Path(__file__).resolve().parent.parent
BRONCE = RAIZ / "data" / "bronce"
pytestmark = [pytest.mark.datos, pytest.mark.skipif(not (BRONCE / "datatur" / "Base70centros.csv").exists(), reason="sin bronce")]


@pytest.fixture(scope="module")
def corrida(tmp_path_factory):
    raiz = tmp_path_factory.mktemp("real")
    shutil.copytree(BRONCE, raiz / "data" / "bronce")
    res = ejecutar(raiz, ahora="2026-11-13T00:00:00+00:00")
    return raiz, res


def test_integridad_del_bronce_real_segun_sus_fichas():
    r = integridad(BRONCE)
    assert r["ok"] is True and r["fallos"] == [] and r["archivos_sin_ficha"] == []


def test_corrida_real_ok_y_cuentas_de_base70(corrida):
    _, res = corrida
    assert res["estado"] == "ok", res
    d = res["calidad"]["datatur_base70"]
    assert d["leidos"] == 31147 and d["rechazados"] == 2 and d["aceptados"] == 31145
    assert d["rechazos_por_regla"] == {"R-D06": 2}                          # Ciudad Juárez 2021-07 y 2022-06
    assert d["marcados"] == {"R-D07_faltante_turistas_noche": 1}           # Mexicali 2020-03
    assert res["plata"]["datatur_base70"] == 31145


def test_cuarentena_real_identifica_los_dos_registros_de_ciudad_juarez(corrida):
    raiz, res = corrida
    rech = pd.read_csv(next((raiz / "data/cuarentena/datatur_base70").glob("*/rechazados.csv")), dtype=str)
    assert set(rech.centro) == {"Ciudad Juárez"} and sorted(zip(rech.anio, rech.mes)) == [("2021", "07"), ("2022", "06")]
    assert set(rech.regla_id) == {"R-D06"} and rech.fila_origen.notna().all() and rech.sha256_bronce.nunique() == 1


def test_oro_real_108_meses_y_cifras_del_contrato(corrida):
    raiz, _ = corrida
    df = cargar_oro_mensual(raiz / "data/oro/manzanillo_ocupacion_mensual.csv")
    s = serie_objetivo(df)
    assert len(s) == 108 and s.index[0] == pd.Period("2016-01", "M") and s.index[-1] == pd.Period("2024-12", "M")
    assert round(s.min(), 2) == 1.46 and s.idxmin() == pd.Period("2020-04", "M")
    assert round(s.max(), 2) == 66.34 and round(s.mean(), 2) == 45.86
    assert df.index[df.diag_atipico_iqr == 1].astype(str).tolist() == ["2020-04", "2020-05", "2020-06"]
    ent, pru = partir_entrenamiento_prueba(s)
    assert (len(ent), len(pru)) == (96, 12)


def test_oro_real_coincide_con_una_derivacion_independiente_desde_bronce(corrida):
    raiz, _ = corrida
    s = serie_objetivo(cargar_oro_mensual(raiz / "data/oro/manzanillo_ocupacion_mensual.csv"))
    d = leer_base70(BRONCE / "datatur" / "Base70centros.csv")
    m = d[(d.centro == "Manzanillo") & d.categoria.isin(["2 estrellas", "3 estrellas", "4 estrellas", "5 estrellas"])]
    g = m.groupby("periodo")[["cuartos_disponibles", "cuartos_ocupados_residentes", "cuartos_ocupados_no_residentes"]].sum().astype(float)
    ref = 100 * (g.cuartos_ocupados_residentes + g.cuartos_ocupados_no_residentes) / g.cuartos_disponibles
    ref.index = ref.index.to_period("M")
    assert float((s - ref).abs().max()) < 1e-5  # el oro redondea a 6 decimales


def test_denue_real_invariantes(corrida):
    raiz, res = corrida
    plata = pd.read_csv(raiz / "data/plata/denue_establecimientos.csv", dtype=str)
    assert plata.groupby("fecha_captura_local").clee.nunique().eq(plata.groupby("fecha_captura_local").size()).all()  # sin duplicados por día
    assert plata.municipio_clave.eq("06007").all()
    oferta = pd.read_csv(raiz / "data/oro/manzanillo_oferta_hospedaje.csv")
    assert not ({"clee", "latitud", "longitud"} & set(oferta.columns))
    por_dia = oferta.groupby("fecha_captura_local").establecimientos.sum()
    assert (por_dia == plata.groupby("fecha_captura_local").size()).all()
    d = res["calidad"]["denue_establecimientos"]
    assert d["leidos"] == d["aceptados"] + d["rechazados"]
