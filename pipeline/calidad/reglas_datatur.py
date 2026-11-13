"""Reglas R-D01 a R-D08 de Base70 (contrato §2.3). Cada regla devuelve máscaras de filas; no borra nada."""
from __future__ import annotations

import pandas as pd
import pandera.pandas as pa

from ..config import ANIO_MAX, ANIO_MIN, N_PERIODOS
from .cuarentena import ErrorPuertaCalidad

COLUMNAS_BRUTAS = [
    "anio", "mes", "tipo_centro", "subtipo_centro", "centro", "categoria",
    "cuartos_disponibles", "cuartos_ocupados_no_residentes", "cuartos_ocupados_residentes",
    "llegada_turistas_no_residentes", "llegada_turistas_residentes",
    "turistas_noche_no_residentes", "turistas_noche_residentes",
]
CONTEOS = COLUMNAS_BRUTAS[6:]
CONTEOS_OBLIGATORIOS = [c for c in CONTEOS if not c.startswith("turistas_noche")]
CONTEOS_CON_FALTANTE_PERMITIDO = [c for c in CONTEOS if c.startswith("turistas_noche")]

# R-D01: columnas exactas y en orden (todas llegan como texto; el tipado es posterior)
ESQUEMA_BRUTO = pa.DataFrameSchema({c: pa.Column(str, nullable=True) for c in COLUMNAS_BRUTAS}, strict=True, ordered=True)


def r_d01_esquema(df: pd.DataFrame) -> None:
    """Esquema distinto = el formato de la fuente cambió: se detiene el lote completo."""
    try:
        ESQUEMA_BRUTO.validate(df, lazy=True)
    except pa.errors.SchemaErrors as e:
        casos = e.failure_cases[["schema_context", "column", "check"]].drop_duplicates().head(5).to_dict("records")
        raise ErrorPuertaCalidad("R-D01", f"esquema de Base70 distinto al del contrato: {casos}") from None


def _b(s: pd.Series) -> pd.Series:
    """Máscara booleana sin NA: un valor desconocido NUNCA debe filtrar filas en silencio."""
    return s.fillna(False).astype(bool)


def numerico(serie: pd.Series) -> pd.Series:
    return pd.to_numeric(serie.astype("string").str.strip().replace({"": pd.NA}), errors="coerce")


def aplicar(df: pd.DataFrame) -> dict:
    """Evalúa R-D02..R-D08 sobre el DataFrame de texto (con ``fila_origen``).

    Devuelve {"rechazos": [(regla, motivo, máscara)], "marcas": {...}, "num": DataFrame numérico, "informativo": {...}}.
    """
    t = df.copy()
    for c in ("anio", "mes", "tipo_centro", "subtipo_centro", "centro", "categoria"):
        t[c] = t[c].astype("string").str.strip()
    rech = []

    # R-D02: fecha válida
    ok_anio = t.anio.str.fullmatch(r"\d{4}").fillna(False)
    anio = pd.to_numeric(t.anio.where(ok_anio), errors="coerce")
    ok_mes = t.mes.str.fullmatch(r"(0[1-9]|1[0-2])").fillna(False)
    m02 = _b(~(_b(ok_anio) & _b(ok_mes) & _b(anio.between(ANIO_MIN, ANIO_MAX))))
    rech.append(("R-D02", "mes fuera de 01-12 o año fuera de 2016-2030 o con formato inválido", m02))

    # R-D04: conteos numéricos enteros >= 0 (los de turistas-noche pueden venir vacíos: R-D07 los marca)
    num = pd.DataFrame({c: numerico(t[c]) for c in CONTEOS})
    motivo04 = pd.Series("", index=t.index, dtype="object")
    m04 = pd.Series(False, index=t.index)
    for c in CONTEOS:
        vacio = t[c].astype("string").str.strip().replace({"": pd.NA}).isna()
        no_numero = _b(num[c].isna() & ~vacio)
        negativo = _b(num[c] < 0)
        no_entero = _b(num[c].notna() & ((num[c] % 1) != 0))
        sin_dato = vacio if c in CONTEOS_OBLIGATORIOS else pd.Series(False, index=t.index)
        malo = _b(no_numero | negativo | no_entero | sin_dato)
        motivo04[malo & ~m04] = f"{c}: no es un entero >= 0 (o está vacío)"
        m04 |= malo
    rech.append(("R-D04", motivo04, m04))

    # R-D03: clave (anio, mes, centro, categoria) única; se conserva la primera aparición
    m03 = t.duplicated(subset=["anio", "mes", "centro", "categoria"], keep="first")
    rech.append(("R-D03", "clave (anio, mes, centro, categoria) repetida; se conserva la primera aparición", m03))

    # R-D05 y R-D06 solo sobre filas con conteos obligatorios bien formados
    bien = ~m04
    disp, res, nores = num["cuartos_disponibles"], num["cuartos_ocupados_residentes"], num["cuartos_ocupados_no_residentes"]
    m05 = _b(bien & ~(disp > 0))
    rech.append(("R-D05", "cuartos_disponibles debe ser mayor que 0", m05))
    m06 = _b(bien & ((res + nores) > disp))
    rech.append(("R-D06", "cuartos ocupados (residentes + no residentes) mayores que los disponibles", m06))

    # R-D07: faltantes de turistas-noche se MARCAN (no se imputan en plata)
    faltante = _b(num[CONTEOS_CON_FALTANTE_PERMITIDO].isna().any(axis=1) & ~m04)
    # R-D08 (informativo): cobertura por centro
    periodos = (t.anio + "-" + t.mes)[~m02]
    cobertura = periodos.groupby(t.centro[~m02]).nunique()
    informativo = {"centros_con_menos_periodos_que_el_maximo": {
        k: int(v) for k, v in cobertura[cobertura < N_PERIODOS].items()}, "R-D08": "informativo (no rechaza filas)"}
    return {"rechazos": rech, "marcas": {"R-D07_faltante_turistas_noche": faltante}, "num": num, "informativo": informativo}
