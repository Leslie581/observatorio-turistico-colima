"""Esquema pandera de la plata de DENUE (R-E07): la plata real lo cumple y cada violación sintética lo detiene."""
from pathlib import Path

import pandas as pd
import pytest

from pipeline.calidad import reglas_denue as re_
from pipeline.calidad.cuarentena import ErrorPuertaCalidad  # noqa: F401  (misma clase que usa validar_plata)

PLATA = Path(__file__).resolve().parents[1] / "data" / "plata" / "denue_establecimientos.csv"
TIPOS = {c: str for c in ("clee", "id", "scian_clase", "cp", "ageb", "manzana", "municipio_clave", "sha256_bronce")}


@pytest.fixture()
def plata():
    df = pd.read_csv(PLATA, dtype=TIPOS)
    for c in ("personal_min", "personal_max"):
        df[c] = df[c].astype("Int64")
    return df


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
