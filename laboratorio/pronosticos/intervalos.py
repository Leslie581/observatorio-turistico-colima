"""Intervalos de predicción sin normalidad (bootstrap de residuos por bloques) y evaluación de origen móvil (posterior a E1).

    python -m laboratorio.pronosticos.intervalos

Por qué existe. La puerta 3 de supuestos estadísticos (PDF, págs. 9–10) pide que, si los residuos incumplen un supuesto, el hallazgo se
publique con un método que no dependa de él. Los residuos del SARIMA elegido pasan Ljung-Box y varianza estable, pero **no son normales**
(Jarque-Bera p < 0.001), y el intervalo original (``get_forecast``) es gaussiano. Aquí se agrega un intervalo por **bootstrap de bloques**
de los residuos de entrenamiento y se compara con el gaussiano. NO reemplaza los resultados de E1 ni los modifica: escribe archivos nuevos.

Cómo se hace y qué supone.
  * Se reajusta la **misma especificación** del elegido (leída de ``resumen.json``) y se simulan trayectorias con ``simulate`` usando como
    choques de estado los residuos del ajuste remuestreados en **bloques consecutivos** (conserva su estructura temporal) y centrados.
  * La trayectoria arranca del estado filtrado en el último mes observado (no se sortea el estado inicial) y el primer choque es la innovación que
    determina el mes siguiente (con choques en cero reproduce el pronóstico analítico; una prueba lo comprueba): **no entra ninguna normalidad**.
  * No incluye la incertidumbre de los parámetros (se reajusta una vez); los intervalos son, por eso, algo optimistas.
  * Supone que los residuos futuros se parecen a los de entrenamiento (incluidos los del COVID, que ensanchan el intervalo).
Evaluación sin fuga: el intervalo de 2024 usa solo 2016–2023; el origen móvil usa orígenes cuyos 12 meses a pronosticar caen **dentro** de
2016–2023 y nunca toca 2024. La especificación SARIMA se fijó con todo el entrenamiento (sesgo leve declarado).
Solo usa statsmodels, numpy y pandas (requirements-lab.txt).
"""
from __future__ import annotations

import json
import re
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from . import datos
from . import modelos as mod

RAIZ = Path(__file__).resolve().parents[2]
RESULTADOS = RAIZ / "laboratorio" / "pronosticos" / "resultados"
SALIDA = RESULTADOS / "intervalos"
SEMILLA = 20261114
B_BOOTSTRAP = 1000
B_ORIGEN_MOVIL = 400
LONGITUD_BLOQUE = 6
ALFA = 0.05
PRIMER_ORIGEN = pd.Period("2018-12", "M")       # al menos 36 meses de datos
PASO_ORIGENES = 3
H = 12


# ---------------------------------------------------------------- especificación elegida
def especificacion_elegida(ruta_resumen: Path = RESULTADOS / "resumen.json") -> tuple:
    """(orden, estacional, con_covid) del modelo elegido, leído del resumen versionado de E1 (sin volver a buscar)."""
    r = json.loads(Path(ruta_resumen).read_text(encoding="utf-8"))
    espec = r["elegido"]["especificacion"]
    m = re.match(r"SARIMA\((\d),(\d),(\d)\)\((\d),(\d),(\d)\)12", espec)
    if not m:
        raise ValueError(f"el elegido no es un SARIMA reconocible: {espec!r}")
    p, d, q, P, D, Q = (int(x) for x in m.groups())
    return (p, d, q), (P, D, Q), "d_covid" in espec


def ajustar(y: pd.Series, spec: tuple):
    orden, est, con_covid = spec
    return mod._sarimax(mod._a_timestamp(y), orden, est, mod.exog_covid(y.index) if con_covid else None)


# ---------------------------------------------------------------- bootstrap de bloques
def residuos_centrados(res) -> np.ndarray:
    e = np.asarray(res.resid, dtype=float)[mod.DESCARTE_INICIAL:]
    return e - e.mean()


def bloques(e: np.ndarray, h: int, longitud: int, rng: np.random.Generator) -> np.ndarray:
    """Secuencia de ``h`` residuos armada con bloques consecutivos (con reposición) del vector ``e``."""
    n = len(e)
    longitud = max(1, min(longitud, n))
    partes = []
    while sum(len(p) for p in partes) < h:
        i = int(rng.integers(0, n - longitud + 1))
        partes.append(e[i:i + longitud])
    return np.concatenate(partes)[:h]


def trayectorias(res, indice_futuro: pd.PeriodIndex, spec: tuple, B: int, semilla: int, longitud: int = LONGITUD_BLOQUE) -> np.ndarray:
    """B trayectorias simuladas (B x h) a partir del estado predicho al final de la muestra; ningún choque es gaussiano."""
    h = len(indice_futuro)
    exog = mod.exog_covid(indice_futuro) if spec[2] else None
    e = residuos_centrados(res)
    rng = np.random.default_rng(semilla)
    estado = res.filtered_state[:, -1]               # estado conocido en el último mes observado (no se sortea)
    out = np.empty((B, h))
    for b in range(B):
        # h + 1 pasos desde el último mes observado: el choque del paso 0 es la innovación que determina y_{T+1}; se descarta la observación 0
        choque = bloques(e, h + 1, longitud, rng).reshape(h + 1, 1)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            sim = np.asarray(res.simulate(nsimulations=h + 1, state_shocks=choque, measurement_shocks=np.zeros((h + 1, 1)),
                                          initial_state=estado, anchor=int(res.nobs) - 1, exog=exog)).ravel()
        out[b] = sim[1:]
    return out


def intervalo(tray: np.ndarray, alfa: float = ALFA) -> pd.DataFrame:
    return pd.DataFrame({"media": tray.mean(axis=0), "li": np.quantile(tray, alfa / 2, axis=0), "ls": np.quantile(tray, 1 - alfa / 2, axis=0)})


def intervalo_gaussiano(res, indice_futuro: pd.PeriodIndex, spec: tuple, alfa: float = ALFA) -> pd.DataFrame:
    exog = mod.exog_covid(indice_futuro) if spec[2] else None
    fc = res.get_forecast(len(indice_futuro), exog=exog)
    ci = fc.conf_int(alpha=alfa)
    return pd.DataFrame({"media": np.asarray(fc.predicted_mean), "li": np.asarray(ci.iloc[:, 0]), "ls": np.asarray(ci.iloc[:, 1])})


# ---------------------------------------------------------------- evaluación
def cobertura_y_ancho(obs: np.ndarray, iv: pd.DataFrame) -> dict:
    dentro = (obs >= iv["li"].to_numpy()) & (obs <= iv["ls"].to_numpy())
    return {"cobertura": float(dentro.mean()), "ancho_medio_pp": float((iv["ls"] - iv["li"]).mean()), "n": int(len(obs))}


def evaluar_2024(serie: pd.Series, spec: tuple) -> pd.DataFrame:
    """Intervalos del año de prueba con modelo ajustado SOLO con 2016-2023: gaussiano frente a bootstrap de bloques."""
    ent, pru = datos.partir(serie)
    res = ajustar(ent, spec)
    g = intervalo_gaussiano(res, pru.index, spec)
    bt = intervalo(trayectorias(res, pru.index, spec, B_BOOTSTRAP, SEMILLA))
    filas = []
    for nombre, iv in (("gaussiano (E1)", g), ("bootstrap de bloques", bt)):
        filas.append({"evaluacion": "2024 (prueba)", "metodo": nombre, **cobertura_y_ancho(pru.to_numpy(), iv)})
    return pd.DataFrame(filas)


def origenes(serie: pd.Series) -> list:
    """Orígenes (último mes observado) cuyos H meses siguientes caen dentro del entrenamiento 2016-2023."""
    ent, _ = datos.partir(serie)
    ultimo = ent.index[-1] - H
    out, o = [], PRIMER_ORIGEN
    while o <= ultimo:
        out.append(o)
        o += PASO_ORIGENES
    return out


def origen_movil_intervalos(serie: pd.Series, spec: tuple) -> pd.DataFrame:
    """Cobertura y ancho de los dos intervalos en cada origen móvil (modelo reajustado en cada origen, sin ver el futuro)."""
    ent, _ = datos.partir(serie)
    filas = []
    for k, o in enumerate(origenes(serie)):
        y = ent[ent.index <= o]
        futuro = pd.period_range(o + 1, periods=H, freq="M")
        obs = ent.reindex(futuro).to_numpy()
        try:
            res = ajustar(y, spec)
        except (np.linalg.LinAlgError, ValueError):
            continue
        g = intervalo_gaussiano(res, futuro, spec)
        bt = intervalo(trayectorias(res, futuro, spec, B_ORIGEN_MOVIL, SEMILLA + k))
        covid = datos.indicador_covid(futuro).astype(bool)
        for nombre, iv in (("gaussiano (E1)", g), ("bootstrap de bloques", bt)):
            for etiqueta, mascara in (("todos los meses", np.ones(H, bool)), ("sin meses COVID", ~covid)):
                if mascara.sum() == 0:
                    continue
                c = cobertura_y_ancho(obs[mascara], iv[mascara])
                filas.append({"origen": str(o), "metodo": nombre, "meses": etiqueta, **c})
    return pd.DataFrame(filas)


def resumen_origen_movil(d: pd.DataFrame) -> pd.DataFrame:
    g = d.groupby(["metodo", "meses"]).apply(lambda x: pd.Series({
        "origenes": int(x["origen"].nunique()), "meses_evaluados": int(x["n"].sum()),
        "cobertura": float((x["cobertura"] * x["n"]).sum() / x["n"].sum()), "ancho_medio_pp": float((x["ancho_medio_pp"] * x["n"]).sum() / x["n"].sum())}),
        include_groups=False)
    return g.reset_index()


def origen_movil_modelos(serie: pd.Series) -> pd.DataFrame:
    """Error de los cuatro modelos obligatorios en los mismos orígenes (pronóstico a 1..12 meses), sin 2024."""
    ent, _ = datos.partir(serie)
    spec = especificacion_elegida()
    cubo = {m: [] for m in ("SES", "Holt", "Holt-Winters", "SARIMA")}
    for o in origenes(serie):
        y = ent[ent.index <= o]
        futuro = pd.period_range(o + 1, periods=H, freq="M")
        obs = ent.reindex(futuro).to_numpy()
        covid = datos.indicador_covid(futuro).astype(bool)
        ajustes = {"SES": mod.ajustar_ses, "Holt": mod.ajustar_holt, "Holt-Winters": mod.ajustar_holt_winters}
        pred = {}
        for nombre, f in ajustes.items():
            try:
                pred[nombre] = np.asarray(f(y).pronostico(H)["media"], dtype=float)
            except Exception:  # noqa: BLE001 - un origen que no converge se omite y se cuenta abajo
                pred[nombre] = None
        try:
            pred["SARIMA"] = intervalo_gaussiano(ajustar(y, spec), futuro, spec)["media"].to_numpy()
        except (np.linalg.LinAlgError, ValueError):
            pred["SARIMA"] = None
        for nombre, p in pred.items():
            if p is not None:
                cubo[nombre].append((obs, p, covid))
    filas = []
    for nombre, lista in cubo.items():
        for etiqueta, usar_covid in (("todos los meses", True), ("sin meses COVID", False)):
            e = np.concatenate([(o - p)[(np.ones(H, bool) if usar_covid else ~c)] for o, p, c in lista])
            ob = np.concatenate([o[(np.ones(H, bool) if usar_covid else ~c)] for o, p, c in lista])
            filas.append({"modelo": nombre, "meses": etiqueta, "origenes": len(lista), "n_errores": int(len(e)), "MAE": float(np.abs(e).mean()),
                          "RMSE": float(np.sqrt((e ** 2).mean())), "MAPE_pct": float(np.mean(np.abs(e) / ob) * 100)})
    return pd.DataFrame(filas)


def proyeccion(serie: pd.Series, spec: tuple, hasta: str = "2027-12") -> pd.DataFrame:
    """Proyección histórica con datos hasta 2024-12 (reajustando con 2016-2024), con los dos intervalos. NO es un pronóstico actualizado."""
    res = ajustar(serie, spec)
    futuro = pd.period_range(serie.index[-1] + 1, pd.Period(hasta, "M"), freq="M")
    g = intervalo_gaussiano(res, futuro, spec)
    bt = intervalo(trayectorias(res, futuro, spec, B_BOOTSTRAP, SEMILLA + 999))
    out = pd.DataFrame({"periodo": futuro.astype(str), "horizonte_meses": np.arange(1, len(futuro) + 1), "media_gauss": g["media"].round(3),
                        "li_gauss": g["li"].round(3), "ls_gauss": g["ls"].round(3), "media_bootstrap": bt["media"].round(3),
                        "li_bootstrap": bt["li"].round(3), "ls_bootstrap": bt["ls"].round(3)})
    out["tipo"] = "proyeccion_historica_con_datos_hasta_" + str(serie.index[-1])
    return out


def ejecutar(salida: Path = SALIDA, fuente: str = "oro") -> dict:
    salida.mkdir(parents=True, exist_ok=True)
    warnings.filterwarnings("ignore")
    serie = datos.cargar_serie(fuente).serie
    spec = especificacion_elegida()
    a = evaluar_2024(serie, spec)
    om = origen_movil_intervalos(serie, spec)
    res_om = resumen_origen_movil(om)
    modelos = origen_movil_modelos(serie)
    proy = proyeccion(serie, spec)
    ent, _ = datos.partir(serie)
    e = residuos_centrados(ajustar(ent, spec))
    ac1 = float(np.corrcoef(e[:-1], e[1:])[0, 1])
    info = {"especificacion": f"SARIMA{spec[0]}{spec[1]}12" + (" + d_covid" if spec[2] else ""), "semilla": SEMILLA, "bloque": LONGITUD_BLOQUE,
            "B_2024_y_proyeccion": B_BOOTSTRAP, "B_origen_movil": B_ORIGEN_MOVIL, "origenes": [str(o) for o in origenes(serie)],
            "autocorrelacion_residuos_rezago_1": round(ac1, 4), "n_residuos": int(len(e)),
            "supuestos_del_bootstrap": ["residuos intercambiables por bloques", "sin incertidumbre de parámetros", "residuos futuros parecidos a los de entrenamiento (incluye COVID)"],
            "advertencia": "La proyección usa datos hasta 2024-12: es una proyección histórica, no un pronóstico actualizado."}
    for nombre, df in (("intervalos_2024.csv", a), ("intervalos_origen_movil_detalle.csv", om), ("intervalos_origen_movil_resumen.csv", res_om),
                       ("origen_movil_modelos.csv", modelos), ("proyeccion_2025_2027.csv", proy)):
        (salida / nombre).write_bytes(df.to_csv(index=False, float_format="%.4f", lineterminator="\n").encode("utf-8"))
    (salida / "resumen.json").write_bytes((json.dumps(info, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    return info


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(ejecutar(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
