"""Comparación de min-max frente a z-score aplicada a métodos estadísticos (rúbrica E1).

Usa las funciones de ``pipeline/transformaciones.py`` (integrante A). Todos los parámetros de escala
se ajustan **solo con el entrenamiento** (filas con periodo <= 2023-12); 2024 se transforma con esos
parámetros sin recalcular nada.

Dos métodos, con propósitos distintos:

1. **k vecinos más cercanos (k-NN) para pronóstico a un paso** (método basado en distancias, donde
   la escala de las variables cambia qué meses son "vecinos"). Variables del mes t, todas conocidas
   antes de t: ocupación en t-1 y t-12, y las tres variables adicionales D7 en t-1
   (``pct_cuartos_no_residentes``, ``estadia_promedio``, ``densidad_ocupacion``). El objetivo no se
   transforma (se promedia la ocupación de los vecinos en puntos porcentuales). k se elige con una
   validación interna dentro del entrenamiento (ajuste 2017-2022, validación 2023), sin ver 2024.
2. **Control: SARIMA elegido** ajustado sobre la serie transformada. Un SARIMA con diferencias es
   equivariante ante transformaciones afines, así que tras invertir la escala debe dar el mismo
   pronóstico. Si sale igual, se reporta la equivalencia; no se fuerza una diferencia.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pipeline import transformaciones as tr

from .datos import FIN_ENTRENAMIENTO
from .modelos import (_a_timestamp, _sarimax, exog_covid, metricas)

VARIABLES = ["ocup_t-1", "ocup_t-12", "pct_no_res_t-1", "estadia_t-1", "densidad_t-1"]
ESCALAS = ("sin_escalar", "minmax", "zscore")
K_CANDIDATOS = (1, 3, 5, 7, 9)
FIN_SUBENTRENAMIENTO = pd.Period("2022-12", "M")  # validación interna para elegir k: 2023


def construir_variables(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Matriz de variables rezagadas (índice = mes que se pronostica) y objetivo, desde 2017-01."""
    y = df["ocupacion_pct"].astype(float)
    X = pd.DataFrame({
        "ocup_t-1": y.shift(1),
        "ocup_t-12": y.shift(12),
        "pct_no_res_t-1": df["pct_cuartos_no_residentes"].astype(float).shift(1),
        "estadia_t-1": df["estadia_promedio"].astype(float).shift(1),
        "densidad_t-1": df["densidad_ocupacion"].astype(float).shift(1),
    }, index=df.index)
    ok = X.notna().all(axis=1)
    return X[ok], y[ok]


def ajustar_escala(X_ent: pd.DataFrame, escala: str) -> dict:
    """Parámetros por variable con ``pipeline.transformaciones`` (exige índice <= 2023-12)."""
    if escala == "sin_escalar":
        return {}
    ajustar = tr.ajustar_minmax if escala == "minmax" else tr.ajustar_zscore
    return {c: ajustar(X_ent[c]) for c in X_ent.columns}


def aplicar_escala(X: pd.DataFrame, escala: str, params: dict) -> pd.DataFrame:
    if escala == "sin_escalar":
        return X.astype(float)
    aplicar = tr.aplicar_minmax if escala == "minmax" else tr.aplicar_zscore
    return pd.DataFrame({c: aplicar(X[c], params[c]).to_numpy() for c in X.columns}, index=X.index)


def knn_predecir(X_mem: np.ndarray, y_mem: np.ndarray, X_q: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    """Promedio simple de la ocupación de los k vecinos euclidianos. Devuelve (predicción, índices)."""
    d = np.sqrt(((X_q[:, None, :] - X_mem[None, :, :]) ** 2).sum(axis=2))
    idx = np.argsort(d, axis=1, kind="stable")[:, :k]
    return y_mem[idx].mean(axis=1), idx


def elegir_k(X: pd.DataFrame, y: pd.Series, escala: str) -> tuple[int, pd.DataFrame]:
    """Validación interna: escala y memoria con 2017-2022, error en 2023. Criterio: menor RMSE."""
    sub, val = X.index <= FIN_SUBENTRENAMIENTO, (X.index > FIN_SUBENTRENAMIENTO) & (X.index <= FIN_ENTRENAMIENTO)
    p = ajustar_escala(X[sub], escala)
    Xs_sub, Xs_val = aplicar_escala(X[sub], escala, p), aplicar_escala(X[val], escala, p)
    filas = []
    for k in K_CANDIDATOS:
        pred, _ = knn_predecir(Xs_sub.to_numpy(), y[sub].to_numpy(), Xs_val.to_numpy(), k)
        filas.append({"escala": escala, "k": k, **metricas(y[val].to_numpy(), pred)})
    t = pd.DataFrame(filas)
    k = int(t.sort_values(["RMSE", "k"]).iloc[0]["k"])
    return k, t


def comparar_knn(df: pd.DataFrame) -> dict:
    """Ajuste con 2017-01..2023-12 y pronóstico a un paso de 2024 para cada escala."""
    X, y = construir_variables(df)
    ent, pru = X.index <= FIN_ENTRENAMIENTO, X.index > FIN_ENTRENAMIENTO
    resultados, validacion, parametros, pronosticos, vecinos = [], [], {}, {}, {}
    for escala in ESCALAS:
        k, tval = elegir_k(X, y, escala)
        validacion.append(tval)
        p = ajustar_escala(X[ent], escala)
        parametros[escala] = p
        Xs_ent, Xs_pru = aplicar_escala(X[ent], escala, p), aplicar_escala(X[pru], escala, p)
        pred, idx = knn_predecir(Xs_ent.to_numpy(), y[ent].to_numpy(), Xs_pru.to_numpy(), k)
        pronosticos[escala] = pd.Series(pred, index=X.index[pru])
        vecinos[escala] = idx
        # Peso efectivo de cada variable en la distancia: su varianza en el entrenamiento escalado,
        # como proporción de la suma (la distancia euclidiana suma diferencias al cuadrado).
        var = Xs_ent.var(ddof=0)
        resultados.append({"escala": escala, "k_elegido": k, **metricas(y[pru].to_numpy(), pred),
                           **{f"peso_{c}": float(var[c] / var.sum()) for c in X.columns}})
    meses_ent = X.index[ent]
    coincidencia = {}
    for a, b in (("sin_escalar", "minmax"), ("sin_escalar", "zscore"), ("minmax", "zscore")):
        comunes = [len(set(meses_ent[vecinos[a][i]]) & set(meses_ent[vecinos[b][i]]))
                   / max(len(vecinos[a][i]), len(vecinos[b][i])) for i in range(int(pru.sum()))]
        coincidencia[f"{a}_vs_{b}"] = float(np.mean(comunes))
    fuera = {c: int(((X[pru][c] < parametros["minmax"][c].minimo) | (X[pru][c] > parametros["minmax"][c].maximo)).sum())
             for c in X.columns}
    return {"tabla": pd.DataFrame(resultados), "validacion": pd.concat(validacion, ignore_index=True),
            "parametros": parametros, "pronosticos": pd.DataFrame(pronosticos).assign(observado=y[pru]),
            "coincidencia_vecinos": coincidencia, "n_entrenamiento": int(ent.sum()),
            "n_prueba": int(pru.sum()), "meses_2024_fuera_del_rango_minmax": fuera}


def control_sarima(serie: pd.Series, orden=(1, 1, 1), estacional=(0, 1, 1)) -> pd.DataFrame:
    """SARIMA(1,1,1)(0,1,1)12 + d_covid ajustado sobre la serie original, min-max y z-score del
    entrenamiento; el pronóstico de 2024 se invierte a puntos porcentuales y se compara.

    Para distinguir una diferencia real de una numérica, la log-verosimilitud se lleva a la escala
    original con el jacobiano de la transformación afín sobre las observaciones efectivas
    (n - d - D*12; las primeras se pierden por la diferenciación). Además, cada variante escalada se
    reajusta **partiendo del óptimo de la serie original reescalado**: si así alcanza la misma
    verosimilitud, la diferencia venía del optimizador (valores iniciales), no del método.
    """
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    ent = serie[serie.index <= FIN_ENTRENAMIENTO]
    pru = serie[serie.index > FIN_ENTRENAMIENTO]
    exog_ent, exog_pru = exog_covid(ent.index), exog_covid(pru.index)
    pmm, pz = tr.ajustar_minmax(ent), tr.ajustar_zscore(ent)
    variantes = {"sin_escalar": (ent, 1.0, lambda s: s),
                 "minmax": (tr.aplicar_minmax(ent, pmm), pmm.maximo - pmm.minimo,
                            lambda s: tr.invertir_minmax(s, pmm)),
                 "zscore": (tr.aplicar_zscore(ent, pz), pz.desviacion,
                            lambda s: tr.invertir_zscore(s, pz))}
    n_efectivo = len(ent) - orden[1] - estacional[1] * 12
    original = _sarimax(_a_timestamp(ent), orden, estacional, exog_ent)
    nombres = list(original.param_names)
    filas, base = [], None
    for escala, (s, factor, invertir) in variantes.items():
        r = _sarimax(_a_timestamp(s), orden, estacional, exog_ent)

        def pronostico(res):
            f = res.get_forecast(len(pru), exog=exog_pru).predicted_mean
            return invertir(pd.Series(f.to_numpy(), index=pru.index)).to_numpy()

        f = pronostico(r)
        base = f if base is None else base
        # reajuste desde el óptimo original reescalado (d_covid / factor, sigma2 / factor²)
        ini = original.params.to_numpy().copy()
        ini[nombres.index("d_covid")] /= factor
        ini[nombres.index("sigma2")] /= factor ** 2
        m = SARIMAX(_a_timestamp(s), exog=exog_ent, order=orden, seasonal_order=estacional + (12,),
                    trend="n", enforce_stationarity=True, enforce_invertibility=True)
        r2 = m.fit(start_params=ini, disp=False, maxiter=500)
        p = dict(zip(r.param_names, r.params))
        filas.append({"escala": escala, **metricas(pru.to_numpy(), f),
                      "dif_max_vs_sin_escalar_pp": float(np.max(np.abs(f - base))),
                      "llf_escala_original": float(r.llf - n_efectivo * np.log(factor)),
                      "theta_estacional": float(p["ma.S.L12"]),
                      "llf_reajuste_desde_optimo": float(r2.llf - n_efectivo * np.log(factor)),
                      "dif_max_reajuste_vs_sin_escalar_pp": float(np.max(np.abs(pronostico(r2) - base))),
                      "convergio": bool(r.mle_retvals.get("converged", True))})
    return pd.DataFrame(filas)
