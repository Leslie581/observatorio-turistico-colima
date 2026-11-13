"""Modelos de pronóstico, métricas, diagnóstico de residuos y criterio de selección.

Familias exigidas por E1: suavizamiento exponencial simple (SES), Holt, Holt-Winters y SARIMA.
SES, Holt y Holt-Winters se ajustan como modelos ETS de error aditivo (statsmodels ``ETSModel``),
lo que da AIC/AICc por máxima verosimilitud e intervalos de predicción analíticos.
Dentro de cada familia, la variante (amortiguada o no; estacionalidad aditiva o multiplicativa;
órdenes de SARIMA y uso de la intervención COVID) se elige **por AICc con el entrenamiento**.
La comparación entre familias usa el error fuera de muestra en 2024.
"""
from __future__ import annotations

import itertools
import warnings
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch
from statsmodels.tsa.exponential_smoothing.ets import ETSModel
from statsmodels.tsa.statespace.sarimax import SARIMAX

from .datos import indicador_covid

PERIODO = 12
ALFA = 0.05
DESCARTE_INICIAL = 13  # residuos iniciales afectados por la inicialización / diferenciación
# ETS con estacionalidad multiplicativa no tiene intervalo analítico: statsmodels lo simula.
# Semilla y repeticiones fijas para que los intervalos sean reproducibles entre ejecuciones.
SEMILLA_SIMULACION = 20261113
REPETICIONES_SIMULACION = 5000


# ----------------------------------------------------------------------------- métricas
def metricas(observado, pronostico) -> dict:
    """MAE y RMSE en puntos porcentuales de ocupación; MAPE en % del valor observado."""
    y = np.asarray(observado, dtype=float)
    f = np.asarray(pronostico, dtype=float)
    if y.shape != f.shape or y.size == 0:
        raise ValueError("observado y pronostico deben tener la misma longitud no nula")
    if np.any(y == 0):
        raise ValueError("MAPE indefinido: hay observaciones iguales a cero")
    e = y - f
    return {"MAE": float(np.mean(np.abs(e))), "RMSE": float(np.sqrt(np.mean(e ** 2))),
            "MAPE": float(100 * np.mean(np.abs(e / y))), "sesgo_medio": float(np.mean(e))}


# ----------------------------------------------------------------------------- ajustes
@dataclass
class Ajuste:
    familia: str
    especificacion: str
    resultado: object
    aicc: float
    aic: float
    bic: float
    parametros: dict
    candidatos: list = field(default_factory=list)  # (especificación, AICc) evaluados

    def pronostico(self, h: int, alfa: float = ALFA, exog_futuro=None) -> pd.DataFrame:
        """Media e intervalo de predicción (1 − alfa) para los ``h`` meses siguientes."""
        if self.familia == "SARIMA":
            fc = self.resultado.get_forecast(h, exog=exog_futuro)
            ci = fc.conf_int(alpha=alfa)
            df = pd.DataFrame({"media": fc.predicted_mean, "li": ci.iloc[:, 0],
                               "ls": ci.iloc[:, 1]})
        else:
            n = self.resultado.nobs
            pred = self.resultado.get_prediction(
                start=n, end=n + h - 1, simulate_repetitions=REPETICIONES_SIMULACION,
                rng=np.random.RandomState(SEMILLA_SIMULACION))  # explícito: estable entre versiones
            sf = pred.summary_frame(alpha=alfa)
            df = pd.DataFrame({"media": sf["mean"], "li": sf["pi_lower"], "ls": sf["pi_upper"]})
        return df

    def residuos(self) -> pd.Series:
        r = pd.Series(np.asarray(self.resultado.resid, dtype=float))
        return r.iloc[DESCARTE_INICIAL:].reset_index(drop=True)


def _a_timestamp(serie: pd.Series) -> pd.Series:
    s = serie.astype(float).copy()
    s.index = s.index.to_timestamp() if isinstance(s.index, pd.PeriodIndex) else s.index
    s.index.freq = "MS"
    return s


def _ets(y: pd.Series, trend=None, damped=False, seasonal=None):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m = ETSModel(y, error="add", trend=trend, damped_trend=damped, seasonal=seasonal,
                     seasonal_periods=PERIODO if seasonal else None,
                     initialization_method="estimated")
        return m.fit(disp=False, maxiter=2000)


def _params(res) -> dict:
    nombres = getattr(res, "param_names", None) or list(getattr(res.params, "index", []))
    return {str(k): float(v) for k, v in zip(nombres, np.asarray(res.params))}


def _mejor_ets(y, familia, variantes) -> Ajuste:
    evaluados = []
    for espec, kw in variantes:
        r = _ets(y, **kw)
        evaluados.append((espec, float(r.aicc), r))
    espec, aicc, r = min(evaluados, key=lambda t: t[1])
    return Ajuste(familia, espec, r, aicc, float(r.aic), float(r.bic), _params(r),
                  [(e, a) for e, a, _ in evaluados])


def ajustar_ses(y: pd.Series) -> Ajuste:
    return _mejor_ets(_a_timestamp(y), "SES", [("ETS(A,N,N)", {})])


def ajustar_holt(y: pd.Series) -> Ajuste:
    return _mejor_ets(_a_timestamp(y), "Holt", [
        ("ETS(A,A,N)", {"trend": "add"}),
        ("ETS(A,Ad,N) amortiguado", {"trend": "add", "damped": True})])


def ajustar_holt_winters(y: pd.Series) -> Ajuste:
    return _mejor_ets(_a_timestamp(y), "Holt-Winters", [
        ("ETS(A,A,A)", {"trend": "add", "seasonal": "add"}),
        ("ETS(A,Ad,A) amortiguado", {"trend": "add", "damped": True, "seasonal": "add"}),
        ("ETS(A,A,M)", {"trend": "add", "seasonal": "mul"}),
        ("ETS(A,Ad,M) amortiguado", {"trend": "add", "damped": True, "seasonal": "mul"})])


def exog_covid(indice) -> pd.DataFrame:
    """Intervención de calendario d_covid (contrato §4.1). Es 0 en 2024 y en adelante."""
    idx = indice if isinstance(indice, pd.PeriodIndex) else pd.PeriodIndex(indice, freq="M")
    ts = idx.to_timestamp()
    return pd.DataFrame({"d_covid": indicador_covid(idx).astype(float)}, index=ts)


def _sarimax(y, orden, estacional, exog):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m = SARIMAX(y, exog=exog, order=orden, seasonal_order=estacional + (PERIODO,),
                    trend="n", enforce_stationarity=True, enforce_invertibility=True)
        return m.fit(disp=False, maxiter=500)


def ajustar_sarima(y: pd.Series, d: int, D: int, p_max: int = 2, q_max: int = 2,
                   P_max: int = 1, Q_max: int = 1, probar_covid: bool = True) -> Ajuste:
    """Búsqueda acotada por AICc con d y D fijos (elegidos con ADF/KPSS).

    Los límites p, q ≤ 2 y P, Q ≤ 1 se fijan con la lectura de ACF/PACF de la serie diferenciada
    (cortes en rezagos bajos y en el 12). Con d y D fijos los AICc son comparables entre sí.
    """
    yt = _a_timestamp(y)
    exog = exog_covid(y.index) if probar_covid else None
    evaluados = []
    for p, q, P, Q in itertools.product(range(p_max + 1), range(q_max + 1),
                                        range(P_max + 1), range(Q_max + 1)):
        for con_covid in ([False, True] if probar_covid else [False]):
            try:
                r = _sarimax(yt, (p, d, q), (P, D, Q), exog if con_covid else None)
            except (np.linalg.LinAlgError, ValueError):
                continue
            if not np.isfinite(r.aicc) or not r.mle_retvals.get("converged", True):
                continue
            espec = f"SARIMA({p},{d},{q})({P},{D},{Q})12" + (" + d_covid" if con_covid else "")
            evaluados.append((espec, float(r.aicc), r, con_covid))
    if not evaluados:
        raise RuntimeError("Ningún SARIMA convergió")
    espec, aicc, r, con_covid = min(evaluados, key=lambda t: t[1])
    aj = Ajuste("SARIMA", espec, r, aicc, float(r.aic), float(r.bic), _params(r),
                sorted([(e, a) for e, a, _, _ in evaluados], key=lambda t: t[1]))
    aj.parametros["usa_d_covid"] = float(con_covid)
    aj.con_covid = con_covid  # type: ignore[attr-defined]
    aj.orden = (r.model.order, r.model.seasonal_order)  # type: ignore[attr-defined]
    return aj


def reajustar(aj: Ajuste, y: pd.Series) -> Ajuste:
    """Reajusta la misma especificación con otra muestra (p. ej., 2016–2024 para el futuro)."""
    yt = _a_timestamp(y)
    if aj.familia == "SARIMA":
        orden, est = aj.orden  # type: ignore[attr-defined]
        exog = exog_covid(y.index) if aj.con_covid else None  # type: ignore[attr-defined]
        r = _sarimax(yt, orden, est[:3], exog)
        nuevo = Ajuste(aj.familia, aj.especificacion, r, float(r.aicc), float(r.aic),
                       float(r.bic), _params(r))
        nuevo.con_covid, nuevo.orden = aj.con_covid, aj.orden  # type: ignore[attr-defined]
        return nuevo
    kw = {"trend": aj.resultado.model.trend, "damped": aj.resultado.model.damped_trend,
          "seasonal": aj.resultado.model.seasonal}
    r = _ets(yt, **kw)
    return Ajuste(aj.familia, aj.especificacion, r, float(r.aicc), float(r.aic), float(r.bic),
                  _params(r))


def pronostico_ajuste(aj: Ajuste, indice_futuro: pd.PeriodIndex, alfa: float = ALFA) -> pd.DataFrame:
    exog = None
    if aj.familia == "SARIMA" and getattr(aj, "con_covid", False):
        exog = exog_covid(indice_futuro)
    df = aj.pronostico(len(indice_futuro), alfa, exog)
    df.index = indice_futuro
    return df


def ingenuo_estacional(entrenamiento: pd.Series, h: int) -> np.ndarray:
    """Referencia: y_{t+h} = y_{t+h−12} (el mismo mes del último año de entrenamiento)."""
    if h > PERIODO:
        raise ValueError("El ingenuo estacional simple solo cubre h ≤ 12")
    return entrenamiento.values[-PERIODO:][:h].astype(float)


# ----------------------------------------------------------------------------- residuos
def diagnosticar_residuos(residuos: pd.Series, gl_modelo: int = 0,
                          rezagos=(12, 24)) -> dict:
    """Ljung-Box (independencia), ARCH-LM y Levene por mitades (varianza), Jarque-Bera (normalidad)."""
    r = pd.Series(residuos, dtype=float).dropna().reset_index(drop=True)
    lb = acorr_ljungbox(r, lags=list(rezagos), model_df=gl_modelo)
    mitad = len(r) // 2
    lev = stats.levene(r.iloc[:mitad], r.iloc[mitad:])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)  # aviso de cambio de tipo de retorno
        arch = het_arch(r, nlags=12)
    jb = stats.jarque_bera(r)
    return {
        "n": len(r), "media": float(r.mean()), "desv_est": float(r.std()),
        "ljung_box": {int(k): {"estadistico": float(lb.loc[k, "lb_stat"]),
                               "p": float(lb.loc[k, "lb_pvalue"])} for k in rezagos},
        "independencia_ok": bool(all(lb.loc[k, "lb_pvalue"] >= ALFA for k in rezagos)),
        "arch_lm_p": float(arch[1]), "levene_mitades_p": float(lev.pvalue),
        "varianza_estable_ok": bool(arch[1] >= ALFA and lev.pvalue >= ALFA),
        "jarque_bera_p": float(jb.pvalue), "normalidad_ok": bool(jb.pvalue >= ALFA),
    }


def grados_libertad(aj: Ajuste) -> int:
    """Parámetros ARMA para ajustar los gl de Ljung-Box (solo SARIMA; 0 en ETS)."""
    if aj.familia != "SARIMA":
        return 0
    (p, _, q), (P, _, Q, _) = aj.orden  # type: ignore[attr-defined]
    return p + q + P + Q


# ----------------------------------------------------------------------------- selección
CRITERIO_SELECCION = (
    "1) Menor RMSE en la prueba 2024 (penaliza errores grandes, en puntos porcentuales). "
    "2) El modelo elegido no debe rechazar Ljung-Box al 5 % en los rezagos 12 y 24 sobre sus "
    "residuos de entrenamiento; si el de menor RMSE la rechaza, se pasa al siguiente que la cumpla. "
    "3) Empates (diferencia de RMSE < 0.1 pp): menor MAE y luego el modelo más simple. "
    "Si ningún modelo cumple 2), se elige por 1) y se declara la limitación.")


def seleccionar(tabla: pd.DataFrame) -> tuple[str, str]:
    """``tabla`` con columnas familia, RMSE, MAE, independencia_ok, n_parametros."""
    t = tabla.sort_values(["RMSE", "MAE", "n_parametros"]).reset_index(drop=True)
    validos = t[t.independencia_ok]
    if validos.empty:
        return t.iloc[0].familia, "ningún modelo supera Ljung-Box; elegido solo por RMSE"
    mejor = validos.iloc[0]
    empatados = validos[validos.RMSE - mejor.RMSE < 0.1].sort_values(["MAE", "n_parametros"])
    elegido = empatados.iloc[0]
    motivo = (f"mejor de los {len(t)} modelos obligatorios: menor RMSE ({elegido.RMSE:.2f} pp) "
              f"entre los que tienen residuos sin autocorrelación significativa (Ljung-Box)")
    if elegido.familia != t.iloc[0].familia:
        motivo += f"; {t.iloc[0].familia} tenía menor RMSE pero no supera Ljung-Box"
    return elegido.familia, motivo
