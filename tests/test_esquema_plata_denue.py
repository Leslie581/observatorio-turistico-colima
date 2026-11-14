"""Esquema pandera de la plata de DENUE (R-E07): la plata real lo cumple y cada violación sintética lo detiene."""
from pathlib import Path

import pandas as pd
import pytest

from pipeline.calidad import reglas_denue as re_
from pipeline.calidad.cuarentena import Cuarentena
from pipeline.plata_denue import procesar_capturas

BRONCE = Path(__file__).resolve().parents[1] / "data" / "bronce" / "denue"   # versionado; la plata se regenera (no está en Git)


@pytest.fixture(scope="module")
def _plata_real():
    return procesar_capturas(BRONCE, Cuarentena("2026-11-13T00:00:00+00:00"))   # ya pasa por validar_plata


@pytest.fixture()
def plata(_plata_real):
    return _plata_real.copy()


def test_plata_real_cumple_el_esquema(plata):
    re_.validar_plata(plata)


@pytest.mark.parametrize("col,valor", [
    ("latitud", 25.0), ("longitud", -100.0), ("scian_clase", "722511"), ("municipio_clave", "06002"),
    ("fecha_alta", "2020-13-01"), ("sha256_bronce", "xyz"), ("capturas_del_dia", 0),
])
def test_violaciones_se_detienen(plata, col, valor):
    plata.loc[0, col] = valor
    with pytest.raises(Exception) as e:
        re_.validar_plata(plata)
    assert "R-E07" in str(e.value) or "esquema" in str(e.value)


def test_duplicado_y_personal_invertido(plata):
    with pytest.raises(Exception):
        re_.validar_plata(pd.concat([plata, plata.iloc[[0]]], ignore_index=True))
    plata.loc[0, ["personal_min", "personal_max"]] = [50, 10]
    with pytest.raises(Exception):
        re_.validar_plata(plata)
