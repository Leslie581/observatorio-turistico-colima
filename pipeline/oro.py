"""Capa oro (contrato §4): serie mensual de ocupación de Manzanillo y agregado municipal de DENUE.

Variable objetivo: ocupacion_pct = 100 x suma(ocupados residentes + no residentes) / suma(disponibles)
de las categorías 2 a 5 estrellas (cociente de sumas, NO promedio de porcentajes; contrato §1.1b).
"""
from __future__ import annotations

import hashlib

import numpy as np
import pandas as pd
import pandera.pandas as pa

from .calidad.cuarentena import ErrorPuertaCalidad
from .jerarquias import DICCIONARIO_JERARQUIAS
from .config import (CATEGORIAS_OBJETIVO, CENTRO_OBJETIVO, COVID_FIN, COVID_INICIO, N_PERIODOS, OFERTA_2017,
                     PERIODO_FIN, PERIODO_INICIO, VERSION_CONTRATO)

COLUMNAS_ORO = [
    "periodo", "fecha_inicio", "ocupacion_pct", "cuartos_disponibles", "cuartos_ocupados",
    "cuartos_ocupados_residentes", "cuartos_ocupados_no_residentes", "pct_cuartos_no_residentes",
    "llegadas_turistas", "turistas_noche", "estadia_promedio", "densidad_ocupacion", "d_covid",
    "d_oferta_2017", "diag_atipico_iqr", "categorias_incluidas", "n_categorias_fuente",
    "sha256_bronce", "ejecucion", "version_contrato",
]
COLUMNAS_OFERTA = ["fecha_captura_local", "municipio_clave", "clase_actividad", "scian_clase", "estrato",
                   "establecimientos", "personal_min_total"]
DECIMALES = 6

# Esquema del oro mensual (pandera): columnas exactas y en orden, tipos y rangos
ESQUEMA_ORO = pa.DataFrameSchema({
    "periodo": pa.Column(str, pa.Check.str_matches(r"^\d{4}-(0[1-9]|1[0-2])$"), unique=True),
    "fecha_inicio": pa.Column(str, pa.Check.str_matches(r"^\d{4}-\d{2}-01$")),
    "ocupacion_pct": pa.Column(float, pa.Check.in_range(0, 100)),
    "cuartos_disponibles": pa.Column(int, pa.Check.gt(0)),
    "cuartos_ocupados": pa.Column(int, pa.Check.ge(0)),
    "cuartos_ocupados_residentes": pa.Column(int, pa.Check.ge(0)),
    "cuartos_ocupados_no_residentes": pa.Column(int, pa.Check.ge(0)),
    "pct_cuartos_no_residentes": pa.Column(float, pa.Check.in_range(0, 100)),
    "llegadas_turistas": pa.Column(int, pa.Check.gt(0)),
    "turistas_noche": pa.Column(int, pa.Check.gt(0)),
    "estadia_promedio": pa.Column(float, pa.Check.gt(0)),
    "densidad_ocupacion": pa.Column(float, pa.Check.gt(0)),
    "d_covid": pa.Column(int, pa.Check.isin([0, 1])),
    "d_oferta_2017": pa.Column(int, pa.Check.isin([0, 1])),
    "diag_atipico_iqr": pa.Column(int, pa.Check.isin([0, 1])),
    "categorias_incluidas": pa.Column(str, pa.Check.isin(["2-5 estrellas"])),
    "n_categorias_fuente": pa.Column(int, pa.Check.isin([len(CATEGORIAS_OBJETIVO)])),
    "sha256_bronce": pa.Column(str, pa.Check.str_matches(r"^[0-9a-f]{64}$")),
    "ejecucion": pa.Column(str),
    "version_contrato": pa.Column(str, pa.Check.isin([VERSION_CONTRATO])),
}, strict=True, ordered=True)


def id_ejecucion(sha256_bronce: str) -> str:
    """Identifica la combinación entrada + contrato (no un instante): hace el oro reproducible byte a byte."""
    return f"oro-{sha256_bronce[:12]}-v{VERSION_CONTRATO}"


def _iqr_atipico(y: pd.Series) -> pd.Series:
    q1, q3 = y.quantile([0.25, 0.75])
    i = q3 - q1
    return ((y < q1 - 1.5 * i) | (y > q3 + 1.5 * i)).astype(int)


def construir_oro_mensual(plata: pd.DataFrame, sha256_bronce: str) -> pd.DataFrame:
    """Plata de Base70 -> serie mensual de Manzanillo (2 a 5 estrellas). Lanza ErrorPuertaCalidad si no es confiable."""
    m = plata[(plata.centro == CENTRO_OBJETIVO) & plata.categoria.isin(CATEGORIAS_OBJETIVO)].copy()
    if m.empty:
        raise ErrorPuertaCalidad("ORO", f"no hay filas de {CENTRO_OBJETIVO} de 2 a 5 estrellas en la plata")
    if m.duplicated(["periodo", "categoria"]).any():
        raise ErrorPuertaCalidad("ORO", "categorías duplicadas por periodo: el total se contaría dos veces")
    por_mes = m.groupby("periodo").categoria.nunique()
    if not (por_mes == len(CATEGORIAS_OBJETIVO)).all():
        malos = por_mes[por_mes != len(CATEGORIAS_OBJETIVO)].index.tolist()[:5]
        raise ErrorPuertaCalidad("ORO", f"meses sin las 4 categorías de 2 a 5 estrellas (p. ej. {malos}): "
                                        "faltan filas por cuarentena o por la fuente")
    if m.faltante_turistas_noche.any():
        raise ErrorPuertaCalidad("ORO", "hay faltantes de turistas-noche en Manzanillo: no se imputan en E1")
    cols = ["cuartos_disponibles", "cuartos_ocupados_residentes", "cuartos_ocupados_no_residentes",
            "llegada_turistas_residentes", "llegada_turistas_no_residentes",
            "turistas_noche_residentes", "turistas_noche_no_residentes"]
    g = m.groupby("periodo")[cols].sum().astype("int64").sort_index()
    ocupados = g.cuartos_ocupados_residentes + g.cuartos_ocupados_no_residentes
    llegadas = g.llegada_turistas_residentes + g.llegada_turistas_no_residentes
    noches = g.turistas_noche_residentes + g.turistas_noche_no_residentes
    idx = pd.PeriodIndex(g.index, freq="M")
    out = pd.DataFrame({
        "periodo": g.index.astype(str),
        "fecha_inicio": [p.start_time.strftime("%Y-%m-%d") for p in idx],
        "ocupacion_pct": (100 * ocupados / g.cuartos_disponibles).astype(float),
        "cuartos_disponibles": g.cuartos_disponibles.values,
        "cuartos_ocupados": ocupados.values,
        "cuartos_ocupados_residentes": g.cuartos_ocupados_residentes.values,
        "cuartos_ocupados_no_residentes": g.cuartos_ocupados_no_residentes.values,
        "pct_cuartos_no_residentes": (100 * g.cuartos_ocupados_no_residentes / ocupados).astype(float),
        "llegadas_turistas": llegadas.values,
        "turistas_noche": noches.values,
        "estadia_promedio": (noches / llegadas).astype(float),
        "densidad_ocupacion": (noches / ocupados).astype(float),
        "d_covid": ((idx >= pd.Period(COVID_INICIO, "M")) & (idx <= pd.Period(COVID_FIN, "M"))).astype(int),
        "d_oferta_2017": (idx >= pd.Period(OFERTA_2017, "M")).astype(int),
    }).reset_index(drop=True)
    out["diag_atipico_iqr"] = _iqr_atipico(out.ocupacion_pct).values
    out["categorias_incluidas"] = "2-5 estrellas"
    out["n_categorias_fuente"] = len(CATEGORIAS_OBJETIVO)
    out["sha256_bronce"] = sha256_bronce
    out["ejecucion"] = id_ejecucion(sha256_bronce)
    out["version_contrato"] = VERSION_CONTRATO
    out = out[COLUMNAS_ORO]
    for c in ("ocupacion_pct", "pct_cuartos_no_residentes", "estadia_promedio", "densidad_ocupacion"):
        out[c] = out[c].round(DECIMALES)
    validar_oro_mensual(out)
    return out


def validar_oro_mensual(df: pd.DataFrame) -> None:
    """Puerta de calidad del oro: 108 meses 2016-01..2024-12, sin huecos, orden, rangos y coherencia de la fórmula."""
    try:
        ESQUEMA_ORO.validate(df, lazy=True)
    except pa.errors.SchemaErrors as e:
        casos = e.failure_cases[["column", "check", "failure_case"]].head(5).to_dict("records")
        raise ErrorPuertaCalidad("ORO", f"esquema del oro incumplido: {casos}") from None
    esperado = pd.period_range(PERIODO_INICIO, PERIODO_FIN, freq="M").astype(str).tolist()
    if len(df) != N_PERIODOS or df.periodo.tolist() != esperado:
        raise ErrorPuertaCalidad("ORO", f"el oro debe tener exactamente {N_PERIODOS} meses, {PERIODO_INICIO} a {PERIODO_FIN}, "
                                        f"ascendentes y sin huecos; hay {len(df)}")
    recomputo = 100 * (df.cuartos_ocupados_residentes + df.cuartos_ocupados_no_residentes) / df.cuartos_disponibles
    if not np.allclose(recomputo, df.ocupacion_pct, atol=10 ** -(DECIMALES - 1)):
        raise ErrorPuertaCalidad("ORO", "ocupacion_pct no coincide con el cociente de sumas")
    if (df.cuartos_ocupados != df.cuartos_ocupados_residentes + df.cuartos_ocupados_no_residentes).any():
        raise ErrorPuertaCalidad("ORO", "cuartos_ocupados no es la suma de residentes y no residentes")
    if (df.cuartos_ocupados > df.cuartos_disponibles).any():
        raise ErrorPuertaCalidad("ORO", "hay meses con más cuartos ocupados que disponibles")


def construir_oferta_hospedaje(plata_denue: pd.DataFrame) -> pd.DataFrame:
    """Contexto agregado por clase y tamaño, SIN coordenadas ni CLEE y sin relación alguna con la ocupación."""
    g = (plata_denue.groupby(["fecha_captura_local", "municipio_clave", "clase_actividad", "scian_clase", "estrato"], dropna=False)
         .agg(establecimientos=("clee", "nunique"), personal_min_total=("personal_min", "sum")).reset_index())
    g["personal_min_total"] = g.personal_min_total.astype("Int64")
    g["establecimientos"] = g.establecimientos.astype(int)
    out = g[COLUMNAS_OFERTA].sort_values(["fecha_captura_local", "scian_clase", "estrato"]).reset_index(drop=True)
    if "clee" in out.columns or {"latitud", "longitud"} & set(out.columns):
        raise ErrorPuertaCalidad("ORO", "el agregado público no puede traer CLEE ni coordenadas")
    return out


# ---------------------------------------------------------------- diccionario de datos (rúbrica E1)
def _d(dataset, col, tipo, unidad, definicion, fuente, regla):
    return {"dataset": dataset, "columna": col, "tipo": tipo, "unidad": unidad, "definicion": definicion,
            "fuente": fuente, "regla_de_calculo": regla}


_M = "manzanillo_ocupacion_mensual"
_O = "manzanillo_oferta_hospedaje"
DICCIONARIO = [
    _d(_M, "periodo", "texto AAAA-MM", "mes", "Mes de referencia (clave única, ascendente)", "DATATUR Base70", "anio y mes del bronce"),
    _d(_M, "fecha_inicio", "fecha ISO", "día", "Primer día del mes", "derivada", "periodo + '-01'"),
    _d(_M, "ocupacion_pct", "decimal 0-100 (6 decimales)", "%", "Variable objetivo: ocupación hotelera de Manzanillo, categorías 2 a 5 estrellas",
       "DATATUR Base70", "100 x suma(ocupados residentes + no residentes) / suma(disponibles) de las 4 categorías; cociente de sumas, no promedio de porcentajes"),
    _d(_M, "cuartos_disponibles", "entero", "cuartos-noche al mes", "Oferta mensual de cuartos", "DATATUR Base70", "suma de las 4 categorías"),
    _d(_M, "cuartos_ocupados", "entero", "cuartos-noche al mes", "Cuartos ocupados", "DATATUR Base70", "residentes + no residentes"),
    _d(_M, "cuartos_ocupados_residentes", "entero", "cuartos-noche al mes", "Cuartos ocupados por residentes", "DATATUR Base70", "suma de las 4 categorías"),
    _d(_M, "cuartos_ocupados_no_residentes", "entero", "cuartos-noche al mes", "Cuartos ocupados por no residentes", "DATATUR Base70", "suma de las 4 categorías"),
    _d(_M, "pct_cuartos_no_residentes", "decimal 0-100", "%", "Variable adicional exploratoria (D7): peso de los no residentes. Riesgo de correlación mecánica con el objetivo; no es regresor por defecto",
       "DATATUR Base70", "100 x cuartos_ocupados_no_residentes / cuartos_ocupados"),
    _d(_M, "llegadas_turistas", "entero", "personas al mes", "Llegadas de turistas", "DATATUR Base70", "residentes + no residentes, suma de las 4 categorías"),
    _d(_M, "turistas_noche", "entero", "personas-noche al mes", "Turistas-noche", "DATATUR Base70", "residentes + no residentes, suma de las 4 categorías"),
    _d(_M, "estadia_promedio", "decimal", "noches", "Variable adicional exploratoria (D7): se publica junto con el objetivo, no se conoce antes de él", "DATATUR Base70", "turistas_noche / llegadas_turistas"),
    _d(_M, "densidad_ocupacion", "decimal", "personas por cuarto", "Variable adicional exploratoria (D7): dependencia mecánica con el objetivo (mismo numerador en el denominador)", "DATATUR Base70", "turistas_noche / cuartos_ocupados"),
    _d(_M, "d_covid", "0/1", "indicador", "1 de 2020-03 a 2021-06 (regla de calendario, conocida de antemano)", "derivada", "periodo entre 2020-03 y 2021-06"),
    _d(_M, "d_oferta_2017", "0/1", "indicador", "1 desde 2017-06 (primer salto de la oferta; calendario). El segundo salto (2017-11) no tiene indicador en 1.0.0", "derivada", "periodo >= 2017-06"),
    _d(_M, "diag_atipico_iqr", "0/1", "indicador", "SOLO DIAGNÓSTICO (se calcula con toda la serie): prohibido como regresor", "derivada", "ocupacion_pct fuera de [Q1 - 1.5 IQR, Q3 + 1.5 IQR]"),
    _d(_M, "categorias_incluidas", "texto", "-", "Categorías que componen el total ('1 estrella' se excluye: solo existe 2016-01 a 2017-09)", "constante", "2-5 estrellas"),
    _d(_M, "n_categorias_fuente", "entero", "categorías", "Categorías sumadas en cada mes", "constante", "4"),
    _d(_M, "sha256_bronce", "texto", "-", "SHA-256 del archivo de bronce del que proviene", "procedencia", "hash de Base70centros.csv"),
    _d(_M, "ejecucion", "texto", "-", "Identifica la combinación entrada + contrato (no un instante)", "procedencia", "oro-<12 primeros hex del hash>-v<versión>"),
    _d(_M, "version_contrato", "texto", "-", "Versión del esquema del contrato de datos", "procedencia", "1.0.0"),
    _d(_O, "fecha_captura_local", "fecha ISO", "día (America/Mexico_City)", "Día de la captura DENUE", "INEGI DENUE", "capturado_utc de la ficha de bronce, en hora local"),
    _d(_O, "municipio_clave", "texto", "-", "Clave INEGI del municipio (Manzanillo = 06007)", "INEGI DENUE", "primeros 5 dígitos de AreaGeo"),
    _d(_O, "clase_actividad", "texto", "-", "Clase SCIAN 721 (alojamiento temporal)", "INEGI DENUE", "Clase_actividad"),
    _d(_O, "scian_clase", "texto 6 dígitos", "-", "Código SCIAN de la clase", "INEGI DENUE", "CLASE_ACTIVIDAD_ID"),
    _d(_O, "estrato", "texto", "personas ocupadas (rango)", "Tamaño del establecimiento por personal ocupado (NO mide cuartos)", "INEGI DENUE", "Estrato"),
    _d(_O, "establecimientos", "entero", "establecimientos", "Conteo en esa fecha, clase y estrato. Contexto: no se relaciona con la ocupación mensual ni con hoteles individuales", "INEGI DENUE", "CLEE distintos"),
    _d(_O, "personal_min_total", "entero", "personas", "Suma de los mínimos de personal ocupado del estrato (cota inferior)", "INEGI DENUE", "suma de personal_min"),
]


def diccionario_df() -> pd.DataFrame:
    """Diccionario de las capas oro: el oro mensual, la oferta DENUE y las dimensiones de las jerarquías conceptuales."""
    return pd.DataFrame(DICCIONARIO + DICCIONARIO_JERARQUIAS)


def hash_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()
