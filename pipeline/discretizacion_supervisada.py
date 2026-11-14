"""Discretización supervisada por entropía (Fayyad e Irani) de la ocupación hotelera, sin fuga de información.

Complementa a ``pipeline/transformaciones.py`` (ancho igual y frecuencia igual), que NO se modifica.

Qué se discretiza y con qué objetivo (y por qué no es circular):
  * Variable a discretizar: ``ocupacion_pct`` (porcentaje mensual).
  * Variable objetivo (la «supervisión»): ``temporada_alta`` = 1 si el mes es julio, agosto o diciembre. La definición es de
    **calendario** (vacaciones escolares de verano y de fin de año), se fijó **antes** de calcular ningún corte y no usa ningún
    valor de ocupación; la Semana Santa se excluye de la regla porque cae en marzo o abril según el año. Por eso el objetivo
    no se deriva de la variable discretizada (no hay circularidad) y no depende de 2024.
  * Pregunta de negocio: ¿a partir de qué nivel de ocupación un mes «se parece» a uno de temporada alta? Los cortes lo
    contestan con los datos de entrenamiento.
Sin fuga: ``ajustar_supervisada`` reutiliza el candado de ``transformaciones`` (``ErrorFuga`` si hay un solo mes posterior a
2023-12, o si el índice no es mensual); 2024 solo se usa para EVALUAR los cortes ya fijados. Los meses de COVID
(2020-03 a 2021-06, regla de calendario del contrato) pueden excluirse del ajuste: ese periodo rompió la estacionalidad.

Solo depende de numpy y pandas. Guía de uso y limitaciones: docs/E1/transformaciones.md §8.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .transformaciones import ETIQUETAS_TERCILES, ParametrosDiscretizacion, _exigir_entrenamiento, aplicar_discretizacion

MESES_TEMPORADA_ALTA = (7, 8, 12)
METODO = "supervisada_entropia"
SEMILLA_PERMUTACIONES = 20261113


@dataclass(frozen=True)
class ParametrosSupervisada:
    discretizacion: ParametrosDiscretizacion
    ganancias_bits: tuple          # ganancia de información de cada corte, en el orden en que se eligió
    mdlp_acepta: tuple             # si el criterio MDL de Fayyad-Irani acepta ese corte (con el segmento que lo originó)
    excluidos: int                 # meses del entrenamiento que no entraron al ajuste (COVID)


def temporada_alta(indice: pd.PeriodIndex) -> pd.Series:
    """1 si el mes es de temporada alta por calendario (julio, agosto, diciembre); 0 en los demás. No usa datos de ocupación."""
    return pd.Series(np.isin(indice.month, MESES_TEMPORADA_ALTA).astype(int), index=indice, name="temporada_alta")


def entropia(y) -> float:
    """Entropía de Shannon (bits) de una variable de clase."""
    y = np.asarray(y)
    if len(y) == 0:
        return 0.0
    p = np.unique(y, return_counts=True)[1] / len(y)
    return float(-(p * np.log2(p)).sum())


def _ganancia(y, izq) -> float:
    n = len(y)
    return entropia(y) - (izq.sum() / n) * entropia(y[izq]) - ((~izq).sum() / n) * entropia(y[~izq])


def mdlp_acepta_corte(y, izq) -> bool:
    """Criterio de longitud mínima de descripción (Fayyad e Irani, 1993): ¿la ganancia justifica el corte?"""
    n = len(y)
    if n < 3 or izq.sum() == 0 or (~izq).sum() == 0:
        return False
    y1, y2 = y[izq], y[~izq]
    k, k1, k2 = len(np.unique(y)), len(np.unique(y1)), len(np.unique(y2))
    delta = np.log2(3 ** k - 2) - (k * entropia(y) - k1 * entropia(y1) - k2 * entropia(y2))
    return bool(_ganancia(y, izq) > (np.log2(n - 1) + delta) / n)


def mejor_corte(x, y, min_hoja: int = 8):
    """Corte de mayor ganancia de información entre los puntos medios de valores consecutivos distintos.

    Cada lado del corte debe tener al menos ``min_hoja`` observaciones. Devuelve ``(corte, ganancia, mdlp)`` o ``None``.
    """
    x, y = np.asarray(x, dtype=float), np.asarray(y)
    v = np.unique(x)
    mejor = None
    for corte in (v[:-1] + v[1:]) / 2:
        izq = x < corte
        if izq.sum() < min_hoja or (~izq).sum() < min_hoja:
            continue
        g = _ganancia(y, izq)
        if mejor is None or g > mejor[1] + 1e-12:
            mejor = (float(corte), float(g), mdlp_acepta_corte(y, izq))
    return mejor


def _cortes_voraces(x, y, k: int, min_hoja: int):
    """Divide recursivamente el segmento con mayor ganancia ponderada hasta tener ``k`` niveles."""
    segmentos = [np.ones(len(x), dtype=bool)]
    cortes, ganancias, mdlp = [], [], []
    for _ in range(k - 1):
        opciones = []
        for s in segmentos:
            m = mejor_corte(x[s], y[s], min_hoja)
            if m is not None:
                opciones.append((m[1] * s.sum() / len(x), s, m))
        if not opciones:
            raise ValueError(f"no hay un corte factible con al menos {min_hoja} meses por nivel; reduzca k o min_hoja")
        _, s, (corte, g, ok) = max(opciones, key=lambda o: o[0])
        segmentos = [seg for seg in segmentos if seg is not s] + [s & (x < corte), s & (x >= corte)]
        cortes.append(corte), ganancias.append(g), mdlp.append(ok)
    orden = np.argsort(cortes)
    return [cortes[i] for i in orden], [ganancias[i] for i in orden], [mdlp[i] for i in orden]


def ajustar_supervisada(entrenamiento: pd.Series, objetivo: pd.Series, k: int = 3, min_hoja: int = 8,
                        excluir: "pd.Series | None" = None, etiquetas: tuple = ETIQUETAS_TERCILES) -> ParametrosSupervisada:
    """Calcula los cortes SOLO con el entrenamiento (2016-01 a 2023-12).

    ``entrenamiento``: variable continua (``ocupacion_pct``); ``objetivo``: clase (0/1) alineada por índice;
    ``excluir``: máscara booleana opcional de meses que no entran al ajuste (p. ej. ``d_covid == 1``).
    """
    x = _exigir_entrenamiento(entrenamiento)                       # candado: ErrorFuga si hay meses posteriores a 2023-12
    if not isinstance(objetivo, pd.Series) or not x.index.equals(objetivo.index):
        raise ValueError("el objetivo debe ser una Series con el mismo índice mensual que la variable")
    if objetivo.isna().any():
        raise ValueError("el objetivo no puede tener valores faltantes")
    if k < 2 or len(etiquetas) != k:
        raise ValueError("k debe ser al menos 2 y haber una etiqueta por nivel")
    usar = np.ones(len(x), dtype=bool) if excluir is None else ~np.asarray(excluir.reindex(x.index), dtype=bool)
    if usar.sum() < k * min_hoja:
        raise ValueError(f"solo {usar.sum()} meses para ajustar: se necesitan al menos {k * min_hoja}")
    xs, ys = x.to_numpy()[usar], objetivo.to_numpy()[usar]
    if len(np.unique(ys)) < 2:
        raise ValueError("el objetivo tiene una sola clase en el entrenamiento: no hay nada que separar")
    cortes, ganancias, mdlp = _cortes_voraces(xs, ys, k, min_hoja)
    p = ParametrosDiscretizacion(METODO, tuple(float(c) for c in cortes), tuple(etiquetas), int(usar.sum()), str(x.index.max()))
    return ParametrosSupervisada(p, tuple(float(g) for g in ganancias), tuple(mdlp), int((~usar).sum()))


def aplicar_supervisada(x: pd.Series, p: ParametrosSupervisada) -> pd.Series:
    """Nivel de cada valor con los cortes ya fijados (no recalcula nada; extremos abiertos)."""
    return aplicar_discretizacion(x, p.discretizacion)


# ---------------------------------------------------------------- evaluación de una partición
def informacion_mutua(niveles, y) -> float:
    """Entropía de la clase menos la entropía condicionada al nivel (bits): cuánto informa el nivel sobre la clase."""
    niveles, y = np.asarray(niveles), np.asarray(y)
    cond = sum((niveles == n).sum() / len(y) * entropia(y[niveles == n]) for n in np.unique(niveles))
    return float(entropia(y) - cond)


def regla_mayoritaria(niveles_entrenamiento, y_entrenamiento) -> dict:
    """Clase mayoritaria de cada nivel en el entrenamiento (se aplica a la prueba sin reajustar)."""
    n, y = np.asarray(niveles_entrenamiento), np.asarray(y_entrenamiento)
    return {nivel: int(np.round(y[n == nivel].mean())) if (n == nivel).any() else 0 for nivel in np.unique(n)}


def exactitud(niveles, y, regla: dict) -> float:
    pred = np.array([regla.get(n, 0) for n in np.asarray(niveles)])
    return float((pred == np.asarray(y)).mean())


def p_valor_permutacion(x, y, ganancia_observada: float, k: int, min_hoja: int, n_perm: int = 500, semilla: int = SEMILLA_PERMUTACIONES) -> float:
    """Probabilidad de obtener una ganancia total igual o mayor si la clase no tuviera relación con la variable.

    Reajusta los cortes con la clase permutada (semilla fija: reproducible). Corrige la ventaja de la supervisada, que siempre
    mejora su ganancia de entrenamiento por construcción.
    """
    rng = np.random.default_rng(semilla)
    x, y = np.asarray(x, dtype=float), np.asarray(y)
    mayores = 0
    for _ in range(n_perm):
        yp = rng.permutation(y)
        cortes, _, _ = _cortes_voraces(x, yp, k, min_hoja)
        niveles = np.searchsorted(np.asarray(cortes), x, side="right")
        mayores += informacion_mutua(niveles, yp) >= ganancia_observada - 1e-12
    return float((mayores + 1) / (n_perm + 1))
