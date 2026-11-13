"""Interfaz entre el módulo de datos y el laboratorio estadístico (contrato §7).

El laboratorio SOLO lee la capa oro mediante estas funciones. La partición es la aprobada en D2:
entrenamiento 2016-01 a 2023-12 (96 meses) y prueba 2024-01 a 2024-12 (12 meses).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import FIN_ENTRENAMIENTO, H_PRUEBA, RAIZ
from .oro import COLUMNAS_ORO, validar_oro_mensual

RUTA_ORO = RAIZ / "data" / "oro" / "manzanillo_ocupacion_mensual.csv"
_TEXTO = {c: str for c in ("periodo", "fecha_inicio", "categorias_incluidas", "sha256_bronce", "ejecucion", "version_contrato")}


def cargar_oro_mensual(ruta: "Path | str | None" = None) -> pd.DataFrame:
    """Lee y VALIDA el oro mensual. Devuelve un DataFrame indexado por ``PeriodIndex`` mensual (``periodo``),
    ascendente, con las 19 columnas restantes del contrato §4.1 (``periodo`` es el índice)."""
    ruta = Path(ruta) if ruta else RUTA_ORO
    if not ruta.is_file():
        raise FileNotFoundError(f"no existe la capa oro: {ruta} (ejecute `python -m pipeline.ejecutar`)")
    df = pd.read_csv(ruta, dtype=_TEXTO)
    if list(df.columns) != COLUMNAS_ORO:
        raise ValueError(f"columnas del oro distintas al contrato: {list(df.columns)}")
    validar_oro_mensual(df)  # 108 meses, sin huecos, orden, rangos y fórmula (ErrorPuertaCalidad si falla)
    df.index = pd.PeriodIndex(df.pop("periodo"), freq="M")
    df.index.name = "periodo"
    return df


def serie_objetivo(df: "pd.DataFrame | None" = None) -> pd.Series:
    """Variable objetivo ``ocupacion_pct`` con ``PeriodIndex`` mensual."""
    if df is None:
        df = cargar_oro_mensual()
    return df["ocupacion_pct"].astype(float).rename("ocupacion_pct")


def partir_entrenamiento_prueba(serie: "pd.Series | pd.DataFrame", h: int = H_PRUEBA):
    """(entrenamiento, prueba). La partición está fijada por el contrato (D2): ``h`` solo puede ser 12.

    Sin fuga: todo el entrenamiento es anterior a la prueba; no se ajusta nada con la prueba."""
    if h != H_PRUEBA:
        raise ValueError(f"la partición está fijada por el contrato D2 (h={H_PRUEBA}); no se admite h={h}")
    idx = serie.index
    if not isinstance(idx, pd.PeriodIndex) or idx.freqstr != "M":
        raise ValueError("la serie debe tener un PeriodIndex mensual")
    if not idx.is_monotonic_increasing or idx.has_duplicates:
        raise ValueError("el índice debe ser ascendente y sin periodos repetidos")
    corte = pd.Period(FIN_ENTRENAMIENTO, "M")
    ent, pru = serie[idx <= corte], serie[idx > corte]
    if len(pru) != h:
        raise ValueError(f"la prueba debe tener {h} meses y tiene {len(pru)}")
    assert ent.index.max() < pru.index.min()
    return ent, pru
