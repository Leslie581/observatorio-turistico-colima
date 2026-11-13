"""Carga de la serie objetivo según el contrato de datos E1 1.0.0.

Orden de preferencia (``fuente="auto"``):
1. ``data/oro/manzanillo_ocupacion_mensual.csv`` (capa oro de la integrante A), validada contra el
   esquema del contrato §0/§4.1 **y** contra la derivación de referencia (§7) antes de usarse.
2. La derivación de referencia del contrato §7, mientras el oro no exista.

El laboratorio no lee plata. La derivación de referencia lee bronce únicamente porque el contrato §7
la prescribe como sustituto temporal del oro; se elimina en cuanto el oro esté integrado.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
RUTA_ORO = RAIZ / "data" / "oro" / "manzanillo_ocupacion_mensual.csv"
RUTA_BRONCE_BASE70 = RAIZ / "data" / "bronce" / "datatur" / "Base70centros.csv"

VERSION_CONTRATO = "1.0.0"
CATEGORIAS = ["2 estrellas", "3 estrellas", "4 estrellas", "5 estrellas"]
H_PRUEBA = 12
INICIO = pd.Period("2016-01", "M")
FIN_ENTRENAMIENTO = pd.Period("2023-12", "M")
FIN_PRUEBA = pd.Period("2024-12", "M")
N_ESPERADO = 108
COVID = (pd.Period("2020-03", "M"), pd.Period("2021-06", "M"))
OFERTA_2017 = pd.Period("2017-06", "M")
TOLERANCIA_ORO = 1e-5  # el oro redondea a 6 decimales

COLUMNAS_ORO = [
    "periodo", "fecha_inicio", "ocupacion_pct", "cuartos_disponibles", "cuartos_ocupados",
    "cuartos_ocupados_residentes", "cuartos_ocupados_no_residentes", "pct_cuartos_no_residentes",
    "llegadas_turistas", "turistas_noche", "estadia_promedio", "densidad_ocupacion", "d_covid",
    "d_oferta_2017", "diag_atipico_iqr", "categorias_incluidas", "n_categorias_fuente",
    "sha256_bronce", "ejecucion", "version_contrato",
]


@dataclass
class SerieCargada:
    serie: pd.Series            # ocupacion_pct con PeriodIndex mensual
    exogenas: pd.DataFrame      # variables adicionales exploratorias (D7), mismo índice
    fuente: str                 # "oro" o "referencia_contrato_s7"
    detalle: dict               # procedencia y verificaciones realizadas


def derivar_referencia(ruta_bronce: Path | str = RUTA_BRONCE_BASE70) -> pd.DataFrame:
    """Derivación de referencia del contrato §7 (cociente de sumas, 2 a 5 estrellas).

    Devuelve un DataFrame mensual con el objetivo y las variables adicionales de §4.1 calculadas con
    las mismas fórmulas del contrato, para poder comparar columna por columna con el oro.
    """
    from extractores.datatur import leer_base70  # importación diferida: solo si no hay oro

    df = leer_base70(Path(ruta_bronce))
    m = df[(df.centro == "Manzanillo") & df.categoria.isin(CATEGORIAS)]
    if m.duplicated(["periodo", "categoria"]).any():
        raise ValueError("Duplicados (periodo, categoria) en Manzanillo: contrato §1.1b incumplido")
    if not (m.groupby("periodo").size() == len(CATEGORIAS)).all():
        raise ValueError("Algún mes no tiene exactamente las 4 categorías de 2 a 5 estrellas")
    g = m.groupby("periodo").sum(numeric_only=True).astype(float)
    g.index = g.index.to_period("M")
    ocupados = g.cuartos_ocupados_residentes + g.cuartos_ocupados_no_residentes
    llegadas = g.llegada_turistas_residentes + g.llegada_turistas_no_residentes
    noches = g.turistas_noche_residentes + g.turistas_noche_no_residentes
    out = pd.DataFrame({
        "ocupacion_pct": 100 * ocupados / g.cuartos_disponibles,
        "cuartos_disponibles": g.cuartos_disponibles,
        "cuartos_ocupados": ocupados,
        "cuartos_ocupados_residentes": g.cuartos_ocupados_residentes,
        "cuartos_ocupados_no_residentes": g.cuartos_ocupados_no_residentes,
        "pct_cuartos_no_residentes": 100 * g.cuartos_ocupados_no_residentes / ocupados,
        "llegadas_turistas": llegadas,
        "turistas_noche": noches,
        "estadia_promedio": noches / llegadas,
        "densidad_ocupacion": noches / ocupados,
    })
    out.index.name = "periodo"
    out["d_covid"] = indicador_covid(out.index)
    out["d_oferta_2017"] = (out.index >= OFERTA_2017).astype(int)
    return out


def indicador_covid(indice: pd.PeriodIndex) -> np.ndarray:
    """1 de 2020-03 a 2021-06 (regla de calendario del contrato §4.1)."""
    return ((indice >= COVID[0]) & (indice <= COVID[1])).astype(int)


def cargar_oro(ruta: Path | str = RUTA_ORO) -> pd.DataFrame:
    """Lee el oro y valida el esquema exacto del contrato (columnas, orden, filas, huecos, rango)."""
    try:  # interfaz oficial de la integrante A, si ya existe
        from pipeline.interfaz import cargar_oro_mensual  # type: ignore
        df = cargar_oro_mensual(ruta)
    except ImportError:
        df = pd.read_csv(ruta, dtype={"periodo": str})
        if list(df.columns) != COLUMNAS_ORO:
            raise ValueError(f"Columnas del oro distintas al contrato §0: {list(df.columns)}")
        df.index = pd.PeriodIndex(df.pop("periodo"), freq="M")
        df.index.name = "periodo"
    validar_forma(df)
    return df


def validar_forma(df: pd.DataFrame) -> None:
    idx = df.index
    if len(df) != N_ESPERADO:
        raise ValueError(f"Se esperaban {N_ESPERADO} meses y hay {len(df)}")
    if idx[0] != INICIO or idx[-1] != FIN_PRUEBA:
        raise ValueError(f"Cobertura {idx[0]}..{idx[-1]} distinta de {INICIO}..{FIN_PRUEBA}")
    esperado = pd.period_range(INICIO, FIN_PRUEBA, freq="M")
    if not idx.equals(esperado):
        raise ValueError("El índice no es mensual, ascendente y sin huecos")
    y = df["ocupacion_pct"]
    if y.isna().any() or (y < 0).any() or (y > 100).any():
        raise ValueError("ocupacion_pct con nulos o fuera de 0–100")
    if "version_contrato" in df and set(df["version_contrato"].astype(str)) != {VERSION_CONTRATO}:
        raise ValueError(f"version_contrato distinta de {VERSION_CONTRATO}")


def comparar_con_referencia(oro: pd.DataFrame, ref: pd.DataFrame,
                            tolerancia: float = TOLERANCIA_ORO) -> dict:
    """Compara oro y referencia columna por columna; devuelve las diferencias máximas."""
    cols = ["ocupacion_pct", "cuartos_disponibles", "cuartos_ocupados",
            "cuartos_ocupados_residentes", "cuartos_ocupados_no_residentes",
            "pct_cuartos_no_residentes", "llegadas_turistas", "turistas_noche",
            "estadia_promedio", "densidad_ocupacion", "d_covid", "d_oferta_2017"]
    difs = {c: float(np.max(np.abs(oro[c].astype(float).values - ref[c].astype(float).values)))
            for c in cols}
    return {"diferencia_max": difs, "tolerancia": tolerancia,
            "coincide": all(v <= tolerancia for v in difs.values())}


def cargar_serie(fuente: str = "auto", ruta_oro: Path | str = RUTA_ORO,
                 ruta_bronce: Path | str = RUTA_BRONCE_BASE70) -> SerieCargada:
    """Devuelve la serie objetivo y las variables exploratorias.

    ``fuente``: "auto" (oro si existe, si no la referencia), "oro" (exige oro) o "referencia".
    Con oro, la evaluación se detiene si no coincide con la referencia (requisito de integración).
    """
    if fuente not in {"auto", "oro", "referencia"}:
        raise ValueError(f"fuente desconocida: {fuente}")
    ref = None
    if Path(ruta_bronce).exists():
        ref = derivar_referencia(ruta_bronce)
        validar_forma(ref)
    usar_oro = fuente == "oro" or (fuente == "auto" and Path(ruta_oro).exists())
    if usar_oro:
        oro = cargar_oro(ruta_oro)
        detalle = {"ruta": str(Path(ruta_oro).relative_to(RAIZ)) if Path(ruta_oro).is_relative_to(RAIZ)
                   else str(ruta_oro)}
        if ref is None:
            raise FileNotFoundError("No hay bronce para verificar el oro contra la referencia §7")
        comp = comparar_con_referencia(oro, ref)
        detalle["verificacion_vs_referencia"] = comp
        if not comp["coincide"]:
            raise ValueError(f"El oro no coincide con la derivación de referencia: {comp}")
        base, nombre = oro, "oro"
    else:
        if ref is None:
            raise FileNotFoundError("No existe el oro ni el bronce de Base70")
        base, nombre = ref, "referencia_contrato_s7"
        detalle = {"ruta": "data/bronce/datatur/Base70centros.csv (derivación §7)",
                   "nota": "Oro no disponible; serie equivalente según el contrato §7"}
    serie = base["ocupacion_pct"].astype(float).rename("ocupacion_pct")
    exog = base[["pct_cuartos_no_residentes", "estadia_promedio", "densidad_ocupacion",
                 "d_covid", "d_oferta_2017"]].astype(float)
    detalle.update({"n": len(serie), "inicio": str(serie.index[0]), "fin": str(serie.index[-1]),
                    "min": round(float(serie.min()), 2), "max": round(float(serie.max()), 2),
                    "media": round(float(serie.mean()), 2), "version_contrato": VERSION_CONTRATO})
    return SerieCargada(serie, exog, nombre, detalle)


def partir(serie: pd.Series | pd.DataFrame, h: int = H_PRUEBA):
    """Partición D2: todo hasta 2023-12 es entrenamiento; los últimos ``h`` meses, prueba."""
    ent = serie[serie.index <= FIN_ENTRENAMIENTO]
    pru = serie[serie.index > FIN_ENTRENAMIENTO]
    if len(pru) != h:
        raise ValueError(f"La prueba debe tener {h} meses y tiene {len(pru)}")
    return ent, pru
