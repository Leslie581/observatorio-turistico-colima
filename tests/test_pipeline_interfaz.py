"""Interfaz estadística (contrato §7): lectura validada, partición 96 + 12 y ausencia de fuga (datos SINTÉTICOS)."""
import pandas as pd
import pytest

from pipeline.calidad.cuarentena import ErrorPuertaCalidad
from pipeline.ejecutar import ejecutar
from pipeline.interfaz import cargar_oro_mensual, partir_entrenamiento_prueba, serie_objetivo
from tests.pipeline_helpers import arbol_completo


@pytest.fixture()
def oro_csv(tmp_path):
    res = ejecutar(arbol_completo(tmp_path), ahora="2026-11-13T00:00:00+00:00")
    assert res["estado"] == "ok", res
    return tmp_path / "data" / "oro" / "manzanillo_ocupacion_mensual.csv"


def test_cargar_oro_devuelve_indice_mensual_y_las_19_columnas(oro_csv):
    df = cargar_oro_mensual(oro_csv)
    assert isinstance(df.index, pd.PeriodIndex) and df.index.freqstr == "M" and df.index.name == "periodo"
    assert len(df) == 108 and df.shape[1] == 19 and "periodo" not in df.columns
    assert df.index[0] == pd.Period("2016-01", "M") and df.index[-1] == pd.Period("2024-12", "M")
    assert (df.version_contrato == "1.0.0").all()


def test_serie_objetivo_es_ocupacion_pct(oro_csv):
    df = cargar_oro_mensual(oro_csv)
    s = serie_objetivo(df)
    assert s.name == "ocupacion_pct" and s.dtype == float and s.between(0, 100).all() and len(s) == 108


def test_particion_96_mas_12_sin_traslape(oro_csv):
    s = serie_objetivo(cargar_oro_mensual(oro_csv))
    ent, pru = partir_entrenamiento_prueba(s)
    assert (len(ent), len(pru)) == (96, 12)
    assert ent.index[0] == pd.Period("2016-01", "M") and ent.index[-1] == pd.Period("2023-12", "M")
    assert pru.index[0] == pd.Period("2024-01", "M") and pru.index[-1] == pd.Period("2024-12", "M")
    assert set(ent.index).isdisjoint(pru.index) and ent.index.max() < pru.index.min()


def test_sin_fuga_cambiar_la_prueba_no_cambia_el_entrenamiento(oro_csv):
    s = serie_objetivo(cargar_oro_mensual(oro_csv))
    ent1, _ = partir_entrenamiento_prueba(s)
    s2 = s.copy()
    s2[s2.index > pd.Period("2023-12", "M")] += 25
    ent2, pru2 = partir_entrenamiento_prueba(s2)
    pd.testing.assert_series_equal(ent1, ent2)
    assert not pru2.equals(s[s.index > pd.Period("2023-12", "M")])


def test_la_particion_esta_fijada_por_el_contrato(oro_csv):
    s = serie_objetivo(cargar_oro_mensual(oro_csv))
    with pytest.raises(ValueError, match="fijada por el contrato"):
        partir_entrenamiento_prueba(s, h=6)


def test_particion_rechaza_indices_que_no_son_mensuales_o_estan_desordenados(oro_csv):
    s = serie_objetivo(cargar_oro_mensual(oro_csv))
    with pytest.raises(ValueError, match="PeriodIndex mensual"):
        partir_entrenamiento_prueba(pd.Series(s.values, index=s.index.to_timestamp()))
    with pytest.raises(ValueError, match="ascendente"):
        partir_entrenamiento_prueba(s.iloc[::-1])
    with pytest.raises(ValueError, match="prueba debe tener"):
        partir_entrenamiento_prueba(s.iloc[:-3])


def test_cargar_oro_rechaza_un_archivo_alterado(oro_csv):
    df = pd.read_csv(oro_csv, dtype=str)
    df.loc[3, "ocupacion_pct"] = "99.0"  # no coincide con el cociente de sumas
    df.to_csv(oro_csv, index=False, lineterminator="\n")
    with pytest.raises(ErrorPuertaCalidad):
        cargar_oro_mensual(oro_csv)


def test_cargar_oro_sin_archivo_da_un_error_claro(tmp_path):
    with pytest.raises(FileNotFoundError, match="pipeline.ejecutar"):
        cargar_oro_mensual(tmp_path / "no_existe.csv")
