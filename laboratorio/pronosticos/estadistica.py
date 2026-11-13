"""Análisis estadístico de la serie objetivo (insumos numéricos para la selección de modelos).

Todo lo que alimenta decisiones de modelado se calcula **solo con el entrenamiento** (2016-01 a
2023-12). Las gráficas exploratorias de la serie (contrato: integrante A, `laboratorio/exploracion/`)
no se duplican aquí: este módulo devuelve tablas.
"""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import acf, adfuller, kpss, pacf

from .datos import indicador_covid

PERIODO = 12


def caracterizar(serie: pd.Series) -> dict:
    """Estadísticos descriptivos, perfil estacional y contraste COVID / no COVID."""
    cov = indicador_covid(serie.index).astype(bool)
    anual = serie.groupby(serie.index.year).mean()
    mensual = serie.groupby(serie.index.month).mean()
    sin_cov = serie[~cov]
    perfil_sin_cov = sin_cov.groupby(sin_cov.index.month).mean()
    return {
        "n": len(serie), "inicio": str(serie.index[0]), "fin": str(serie.index[-1]),
        "media": float(serie.mean()), "mediana": float(serie.median()),
        "desv_est": float(serie.std()), "cv_pct": float(100 * serie.std() / serie.mean()),
        "min": float(serie.min()), "periodo_min": str(serie.idxmin()),
        "max": float(serie.max()), "periodo_max": str(serie.idxmax()),
        "media_covid": float(serie[cov].mean()), "media_sin_covid": float(sin_cov.mean()),
        "media_anual": {int(k): float(v) for k, v in anual.items()},
        "perfil_mensual": {int(k): float(v) for k, v in mensual.items()},
        "perfil_mensual_sin_covid": {int(k): float(v) for k, v in perfil_sin_cov.items()},
        "mes_pico_sin_covid": int(perfil_sin_cov.idxmax()),
        "mes_valle_sin_covid": int(perfil_sin_cov.idxmin()),
    }


def _fuerza(componente: np.ndarray, resto: np.ndarray) -> float:
    """Fuerza de un componente (Wang, Smith y Hyndman, 2006): max(0, 1 − Var(R)/Var(C+R))."""
    ok = ~np.isnan(componente) & ~np.isnan(resto)
    return float(max(0.0, 1 - np.var(resto[ok]) / np.var(componente[ok] + resto[ok])))


def descomponer(serie: pd.Series) -> dict:
    """Descomposición clásica aditiva y multiplicativa y criterio explícito para elegir.

    Criterios (ambos en las unidades de la serie, puntos porcentuales):
    1. Error de reconstrucción: RMS de y − (T+S) frente a RMS de y − T·S.
    2. Dependencia amplitud–nivel: correlación entre la media anual y el rango estacional anual
       (max − min de y − T). Si es claramente positiva, la estacionalidad crece con el nivel
       (multiplicativa); si no, aditiva.
    """
    y = serie.copy()
    y.index = y.index.to_timestamp()
    res = {}
    for modelo in ("additive", "multiplicative"):
        d = seasonal_decompose(y, model=modelo, period=PERIODO)
        t, s, r = d.trend.values, d.seasonal.values, d.resid.values
        if modelo == "additive":
            error = y.values - (t + s)
            f_t, f_s = _fuerza(t, r), _fuerza(s, r)
        else:  # fuerzas sobre el logaritmo equivalente
            error = y.values - t * s
            f_t, f_s = _fuerza(np.log(t), np.log(r)), _fuerza(np.log(s), np.log(r))
        res[modelo] = {"rms_error_pp": float(np.sqrt(np.nanmean(error ** 2))),
                       "fuerza_tendencia": f_t, "fuerza_estacionalidad": f_s,
                       "indice_estacional": _indice_por_mes(d.seasonal)}
    tend = seasonal_decompose(y, model="additive", period=PERIODO).trend
    desv = (y - tend).groupby(y.index.year)
    amplitud = desv.max() - desv.min()
    nivel = y.groupby(y.index.year).mean()
    completos = desv.count() >= 10  # años con casi todo el ciclo sin NaN de la media móvil
    r_amp = float(np.corrcoef(nivel[completos], amplitud[completos])[0, 1])
    res["amplitud_vs_nivel"] = {"correlacion": r_amp,
                                "anios": [int(a) for a in nivel[completos].index],
                                "amplitud_pp": [float(v) for v in amplitud[completos]],
                                "nivel_pp": [float(v) for v in nivel[completos]]}
    ea, em = res["additive"]["rms_error_pp"], res["multiplicative"]["rms_error_pp"]
    dif_rel = abs(ea - em) / max(ea, em)
    if dif_rel >= 0.05:  # el error de reconstrucción discrimina
        eleccion = "aditiva" if ea < em else "multiplicativa"
        razon = f"error de reconstrucción {min(ea, em):.2f} frente a {max(ea, em):.2f} pp"
    else:  # errores equivalentes: decide la relación amplitud–nivel
        eleccion = "multiplicativa" if r_amp >= 0.5 else "aditiva"
        razon = (f"errores equivalentes ({ea:.2f} y {em:.2f} pp, diferencia {100 * dif_rel:.1f} %);"
                 f" correlación amplitud–nivel {r_amp:.2f} {'≥' if r_amp >= 0.5 else '<'} 0.5")
    res["diferencia_relativa_error"] = float(dif_rel)
    res["eleccion"] = eleccion
    res["razon_eleccion"] = razon
    return res


def componentes_descomposicion(serie: pd.Series) -> tuple[pd.DataFrame, dict]:
    """Componentes de la serie (108 meses del oro) con dos métodos, periodo 12, aditivos:

    * **Clásica** (``seasonal_decompose``): tendencia = media móvil centrada 2x12, de modo que los
      6 primeros y los 6 últimos meses no tienen tendencia ni residuo; estacionalidad = promedio por
      mes de la serie sin tendencia, **idéntica cada año**; residuo = lo que queda.
    * **STL robusta** (Cleveland et al., 1990; ``robust=True``): estimación local con pesos que
      reducen la influencia de los atípicos; la estacionalidad puede cambiar lentamente entre años
      y no pierde los extremos de la serie.

    Es descriptiva: usa los 108 meses (incluido 2024). Las decisiones de modelado se tomaron con la
    descomposición del entrenamiento (``descomponer``).
    """
    from statsmodels.tsa.seasonal import STL

    y = serie.astype(float).copy()
    y.index = y.index.to_timestamp()
    clasica = seasonal_decompose(y, model="additive", period=PERIODO)
    stl = STL(y, period=PERIODO, robust=True).fit()
    comp = pd.DataFrame({
        "observado": y.to_numpy(),
        "tendencia_clasica": clasica.trend.to_numpy(), "estacional_clasica": clasica.seasonal.to_numpy(),
        "residuo_clasico": clasica.resid.to_numpy(),
        "tendencia_stl": stl.trend.to_numpy(), "estacional_stl": stl.seasonal.to_numpy(),
        "residuo_stl": stl.resid.to_numpy(), "peso_robusto_stl": stl.weights.to_numpy(),
    }, index=serie.index)
    cov = pd.Series(indicador_covid(serie.index).astype(bool), index=serie.index)
    res = {}
    for m, sufijo in (("clasica", "clasico"), ("stl", "stl")):
        r, s = comp[f"residuo_{sufijo}"], comp[f"estacional_{m}"]
        res[m] = {
            "fuerza_tendencia": _fuerza(comp[f"tendencia_{m}"].to_numpy(), r.to_numpy()),
            "fuerza_estacionalidad": _fuerza(s.to_numpy(), r.to_numpy()),
            "desv_residuo_covid": float(r[cov].std()), "desv_residuo_resto": float(r[~cov].std()),
            "residuo_min": float(r.min()), "periodo_residuo_min": str(r.idxmin()),
            "meses_sin_componente": int(r.isna().sum()),
            "estacional_por_mes_promedio": {int(k): float(v) for k, v in
                                            s.groupby(s.index.month).mean().items()},
        }
    res["stl"]["meses_peso_robusto_menor_0_5"] = [str(p) for p in comp.index[comp.peso_robusto_stl < 0.5]]
    return comp, res


def _indice_por_mes(seasonal: pd.Series) -> dict:
    s = seasonal.groupby(seasonal.index.month).mean()
    return {int(k): float(v) for k, v in s.items()}


def transformar(serie: pd.Series, d: int = 0, D: int = 0, s: int = PERIODO) -> pd.Series:
    """Aplica D diferencias estacionales y d diferencias regulares (en ese orden)."""
    x = serie.copy()
    for _ in range(D):
        x = x.diff(s)
    for _ in range(d):
        x = x.diff()
    return x.dropna()


def pruebas_estacionariedad(serie: pd.Series) -> pd.DataFrame:
    """ADF (H0: raíz unitaria) y KPSS (H0: estacionaria) sobre niveles y diferencias."""
    filas = []
    for nombre, d, D in [("niveles", 0, 0), ("diferencia regular (d=1)", 1, 0),
                         ("diferencia estacional (D=1)", 0, 1), ("d=1 y D=1", 1, 1)]:
        x = transformar(serie, d, D)
        reg = "ct" if (d, D) == (0, 0) else "c"
        with warnings.catch_warnings():
            # statsmodels 0.15 avisa del cambio futuro del tipo de retorno; KPSS avisa cuando p
            # cae fuera de su tabla (se reporta acotado: 0.01 significa ≤ 0.01; 0.10, ≥ 0.10).
            warnings.simplefilter("ignore")
            est, p, rez, nobs, crit, _ = adfuller(x.values, regression=reg, autolag="AIC")
            k_est, k_p, _, _ = kpss(x.values, regression=reg, nlags="auto")
        filas.append({"transformacion": nombre, "d": d, "D": D, "n": int(nobs),
                      "adf_regresion": reg, "adf_estadistico": est, "adf_p": p,
                      "adf_rezagos": int(rez), "adf_critico_5pct": crit["5%"],
                      "kpss_estadistico": k_est, "kpss_p": k_p,
                      "adf_rechaza_raiz_unitaria": bool(p < 0.05),
                      "kpss_rechaza_estacionariedad": bool(k_p < 0.05)})
    return pd.DataFrame(filas)


def elegir_diferenciacion(tabla: pd.DataFrame) -> tuple[int, int, str]:
    """Menor diferenciación con ADF que rechaza H0 y KPSS que no la rechaza (al 5 %).

    Se prefiere D=1 frente a d=1 cuando ambas bastan, porque la serie es estacional y
    los modelos SARIMA con D=1 eliminan la estacionalidad determinista del entrenamiento.
    """
    orden = [(0, 0), (0, 1), (1, 0), (1, 1)]
    for d, D in orden:
        f = tabla[(tabla.d == d) & (tabla.D == D)].iloc[0]
        if f.adf_rechaza_raiz_unitaria and not f.kpss_rechaza_estacionariedad:
            return d, D, f"{f.transformacion}: ADF p={f.adf_p:.4f}, KPSS p={f.kpss_p:.3f}"
    return 1, 1, "ninguna transformación cumple ambos criterios; se usa d=1, D=1"


def autocorrelaciones(serie: pd.Series, rezagos: int = 36) -> pd.DataFrame:
    """ACF y PACF con banda aproximada ±1.96/√n y marca de significancia."""
    x = serie.dropna().values
    n = len(x)
    rez = min(rezagos, n // 2 - 1)
    a = acf(x, nlags=rez, fft=False)
    p = pacf(x, nlags=rez, method="ywm")
    banda = 1.96 / np.sqrt(n)
    return pd.DataFrame({"rezago": range(rez + 1), "acf": a, "pacf": p, "banda_95": banda,
                         "acf_significativa": np.abs(a) > banda,
                         "pacf_significativa": np.abs(p) > banda})


def correlacion_cruzada(y: pd.Series, x: pd.Series, d: int, D: int,
                        rezagos: int = 12, excluir_covid: bool = False) -> pd.DataFrame:
    """corr(y_t, x_{t−k}) para k = 0..rezagos, sobre series estacionarizadas (mismas d y D).

    Solo debe recibir el entrenamiento (sin fuga temporal hacia 2024). k = 0 es contemporánea y
    **no es utilizable para pronosticar** (x_t se publica a la vez que y_t, contrato §4.1); solo
    k ≥ 1 cumple la restricción de disponibilidad. Con ``excluir_covid`` se descartan los pares en
    los que alguna observación usada por la diferenciación cae en 2020-03..2021-06.
    """
    yt, xt = transformar(y, d, D), transformar(x, d, D)
    alcance = d + D * PERIODO  # observaciones pasadas que entran en cada valor diferenciado
    cov = pd.Series(indicador_covid(y.index), index=y.index)
    contaminado = cov.rolling(alcance + 1, min_periods=1).max().astype(bool)
    filas = []
    for k in range(rezagos + 1):
        par = pd.concat([yt, xt.shift(k)], axis=1, keys=["y", "x"]).dropna()
        if excluir_covid:
            malo = contaminado.reindex(par.index) | contaminado.shift(k).reindex(par.index).fillna(True)
            par = par[~malo.astype(bool)]
        n = len(par)
        r = float(par.y.corr(par.x))
        filas.append({"rezago": k, "r": r, "n": n, "banda_95": 1.96 / np.sqrt(n),
                      "significativa": abs(r) > 1.96 / np.sqrt(n),
                      "utilizable_para_pronostico": k >= 1})
    return pd.DataFrame(filas)
