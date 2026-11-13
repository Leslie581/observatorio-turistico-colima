"""Transformaciones de la variable objetivo para E1: min-max, z-score y discretización.

Regla central (contrato D2, sin fuga temporal): los parámetros se AJUSTAN solo con el entrenamiento
(2016-01 a 2023-12) y después se APLICAN, sin recalcularse, a cualquier otro periodo (por ejemplo 2024).
Por eso hay dos pasos separados y un candado: ``ajustar_*`` lanza ``ErrorFuga`` si recibe un solo mes
posterior a ``FIN_ENTRENAMIENTO``; ``aplicar_*`` no recalcula nada y solo usa los parámetros recibidos.

Solo depende de numpy y pandas (núcleo de requirements.txt). Guía de uso y limitaciones: docs/E1/transformaciones.md.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

from .config import FIN_ENTRENAMIENTO

METODOS_DISCRETIZACION = ("frecuencia_igual", "ancho_igual")
ETIQUETAS_TERCILES = ("bajo", "medio", "alto")


class ErrorFuga(ValueError):
    """Se intentó ajustar una transformación con datos que no son de entrenamiento."""


@dataclass(frozen=True)
class ParametrosMinMax:
    minimo: float
    maximo: float
    n: int
    ajustado_hasta: str


@dataclass(frozen=True)
class ParametrosZScore:
    media: float
    desviacion: float  # poblacional (ddof=0), como StandardScaler de scikit-learn
    n: int
    ajustado_hasta: str


@dataclass(frozen=True)
class ParametrosDiscretizacion:
    metodo: str
    bordes: tuple  # bordes INTERNOS ascendentes; los extremos son abiertos (-inf, +inf)
    etiquetas: tuple
    n: int
    ajustado_hasta: str

    @property
    def k(self) -> int:
        return len(self.etiquetas)


# ---------------------------------------------------------------- candado de entrenamiento
def _exigir_entrenamiento(serie: pd.Series) -> pd.Series:
    """Valida que la serie sea de entrenamiento: índice mensual, sin NaN y sin meses posteriores a 2023-12."""
    if not isinstance(serie, pd.Series) or not isinstance(serie.index, pd.PeriodIndex) or serie.index.freqstr != "M":
        raise ErrorFuga("el ajuste exige una Series con PeriodIndex mensual, para poder comprobar que no hay fuga temporal")
    if len(serie) < 2:
        raise ValueError("se necesitan al menos 2 observaciones de entrenamiento")
    ultimo = serie.index.max()
    if ultimo > pd.Period(FIN_ENTRENAMIENTO, "M"):
        raise ErrorFuga(f"fuga temporal: el ajuste incluye {ultimo}, posterior al fin del entrenamiento ({FIN_ENTRENAMIENTO})")
    valores = serie.astype(float)
    if valores.isna().any():
        raise ValueError("el entrenamiento no puede tener valores faltantes: no se imputan en silencio")
    if not np.isfinite(valores.to_numpy()).all():
        raise ValueError("el entrenamiento contiene valores no finitos")
    return valores


# ---------------------------------------------------------------- min-max
def ajustar_minmax(entrenamiento: pd.Series) -> ParametrosMinMax:
    s = _exigir_entrenamiento(entrenamiento)
    mn, mx = float(s.min()), float(s.max())
    if mx == mn:
        raise ValueError("serie constante: min-max no está definido (máximo = mínimo)")
    return ParametrosMinMax(mn, mx, int(len(s)), str(s.index.max()))


def aplicar_minmax(x: pd.Series, p: ParametrosMinMax) -> pd.Series:
    """(x - min) / (max - min) con min y max del entrenamiento. Fuera de ese rango el resultado sale de [0, 1]: no se recorta."""
    return ((x.astype(float) - p.minimo) / (p.maximo - p.minimo)).rename("minmax")


def invertir_minmax(z: pd.Series, p: ParametrosMinMax) -> pd.Series:
    return (z.astype(float) * (p.maximo - p.minimo) + p.minimo).rename("valor")


# ---------------------------------------------------------------- z-score
def ajustar_zscore(entrenamiento: pd.Series) -> ParametrosZScore:
    s = _exigir_entrenamiento(entrenamiento)
    sd = float(s.std(ddof=0))
    if sd == 0.0:
        raise ValueError("serie constante: z-score no está definido (desviación 0)")
    return ParametrosZScore(float(s.mean()), sd, int(len(s)), str(s.index.max()))


def aplicar_zscore(x: pd.Series, p: ParametrosZScore) -> pd.Series:
    return ((x.astype(float) - p.media) / p.desviacion).rename("zscore")


def invertir_zscore(z: pd.Series, p: ParametrosZScore) -> pd.Series:
    return (z.astype(float) * p.desviacion + p.media).rename("valor")


# ---------------------------------------------------------------- discretización
def ajustar_discretizacion(entrenamiento: pd.Series, metodo: str = "frecuencia_igual", k: int = 3,
                           etiquetas: "tuple | None" = None) -> ParametrosDiscretizacion:
    """Calcula los bordes SOLO con el entrenamiento.

    * ``frecuencia_igual`` (por defecto): bordes en los cuantiles i/k del entrenamiento; cada nivel recibe ~1/k de los meses.
    * ``ancho_igual``: k intervalos del mismo ancho entre el mínimo y el máximo del entrenamiento.
    """
    if metodo not in METODOS_DISCRETIZACION:
        raise ValueError(f"método desconocido: {metodo!r}; use uno de {METODOS_DISCRETIZACION}")
    if k < 2:
        raise ValueError("k debe ser al menos 2")
    s = _exigir_entrenamiento(entrenamiento)
    if metodo == "frecuencia_igual":
        bordes = np.quantile(s.to_numpy(), [i / k for i in range(1, k)])
    else:
        bordes = np.linspace(s.min(), s.max(), k + 1)[1:-1]
    bordes = tuple(float(b) for b in bordes)
    if any(b2 <= b1 for b1, b2 in zip(bordes, bordes[1:])):
        raise ValueError(f"los bordes no son estrictamente ascendentes ({bordes}); reduzca k o cambie de método")
    if etiquetas is None:
        etiquetas = ETIQUETAS_TERCILES if k == 3 else tuple(f"N{i}" for i in range(1, k + 1))
    etiquetas = tuple(etiquetas)
    if len(etiquetas) != k or len(set(etiquetas)) != k:
        raise ValueError(f"se necesitan {k} etiquetas distintas")
    return ParametrosDiscretizacion(metodo, bordes, etiquetas, int(len(s)), str(s.index.max()))


def aplicar_discretizacion(x: pd.Series, p: ParametrosDiscretizacion) -> pd.Series:
    """Nivel ordinal de cada valor. Intervalos [borde_i, borde_i+1); los extremos son abiertos, así que un valor de
    prueba fuera del rango de entrenamiento cae en el nivel extremo (no genera un nivel nuevo)."""
    v = x.astype(float)
    codigos = np.searchsorted(np.asarray(p.bordes), v.to_numpy(), side="right")
    cat = pd.Categorical.from_codes(np.where(v.isna().to_numpy(), -1, codigos), categories=list(p.etiquetas), ordered=True)
    return pd.Series(cat, index=x.index, name="nivel")


# ---------------------------------------------------------------- conjunto de transformaciones
@dataclass(frozen=True)
class Transformaciones:
    minmax: ParametrosMinMax
    zscore: ParametrosZScore
    discretizacion: ParametrosDiscretizacion

    def a_dict(self) -> dict:
        d = asdict(self)
        d["discretizacion"]["bordes"] = list(self.discretizacion.bordes)
        d["discretizacion"]["etiquetas"] = list(self.discretizacion.etiquetas)
        return d


def ajustar_todo(entrenamiento: pd.Series, metodo: str = "frecuencia_igual", k: int = 3) -> Transformaciones:
    return Transformaciones(ajustar_minmax(entrenamiento), ajustar_zscore(entrenamiento),
                            ajustar_discretizacion(entrenamiento, metodo, k))


def transformar(serie: pd.Series, t: Transformaciones) -> pd.DataFrame:
    """Aplica las tres transformaciones con los parámetros YA ajustados (no recalcula nada)."""
    s = serie.astype(float)
    out = pd.DataFrame({"valor": s})
    out["minmax"] = aplicar_minmax(s, t.minmax)
    out["zscore"] = aplicar_zscore(s, t.zscore)
    out["nivel"] = aplicar_discretizacion(s, t.discretizacion)
    out["fuera_rango_entrenamiento"] = (s < t.minmax.minimo) | (s > t.minmax.maximo)
    return out


def transformar_serie_oro(serie: pd.Series, metodo: str = "frecuencia_igual", k: int = 3):
    """Partición del contrato (96 + 12), ajuste con el entrenamiento y aplicación a ambos conjuntos.

    Devuelve ``(parametros, tabla)``; ``tabla`` lleva la columna ``conjunto`` (``entrenamiento`` o ``prueba``)."""
    from .interfaz import partir_entrenamiento_prueba  # import diferido: evita ciclos y carga del oro al importar

    entrenamiento, prueba = partir_entrenamiento_prueba(serie)
    t = ajustar_todo(entrenamiento, metodo, k)
    tabla = pd.concat([transformar(entrenamiento, t).assign(conjunto="entrenamiento"),
                       transformar(prueba, t).assign(conjunto="prueba")])
    return t, tabla
