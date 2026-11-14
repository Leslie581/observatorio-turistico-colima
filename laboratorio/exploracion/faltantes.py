"""Valores faltantes: inventario real, diagnóstico del mecanismo y comparación de tratamientos (Ingeniería de Datos, E1).

    python -m laboratorio.exploracion.faltantes

El PDF (págs. 14 y 24) pide «diagnóstico del mecanismo (completamente al azar, al azar o no al azar) y tratamiento justificado:
eliminación, imputación por media o mediana, interpolación temporal o KNN». Esto produce, en
``laboratorio/exploracion/resultados/faltantes/``:
  * ``inventario_faltantes.csv``: lo que realmente falta en la plata de Base70 (celdas vacías y periodos ausentes por centro);
  * ``imputacion_comparacion.csv`` y ``resumen.json``: una SIMULACIÓN sobre la serie de Manzanillo (solo 2016-2023, nunca 2024):
    se ocultan meses con tres mecanismos (completamente al azar, por bloque de 3 meses y no al azar: los valores más altos) y se
    compara qué tan bien los reconstruyen cinco tratamientos. No imputa nada en los datos reales: Manzanillo **no** tiene faltantes.
Lee la plata (``data/plata/datatur_base70.csv``, que genera ``pipeline.ejecutar``) y el oro. Solo usa numpy y pandas.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from pipeline.config import FIN_ENTRENAMIENTO, N_PERIODOS, PERIODO_FIN, PERIODO_INICIO
from pipeline.interfaz import cargar_oro_mensual, partir_entrenamiento_prueba, serie_objetivo

RAIZ = Path(__file__).resolve().parents[2]
PLATA = RAIZ / "data" / "plata" / "datatur_base70.csv"
SALIDA = RAIZ / "laboratorio" / "exploracion" / "resultados" / "faltantes"
SEMILLA = 20261113
REPLICAS = 200
FRACCION = 0.10                      # 10 % de los meses del entrenamiento (≈ 10 de 96)
METODOS = ("media", "mediana", "interpolacion_lineal", "interpolacion_estacional", "knn")
MECANISMOS = ("completamente_al_azar", "bloque_de_3_meses", "no_al_azar_valores_altos")


# ---------------------------------------------------------------- inventario real
def inventario(plata: pd.DataFrame) -> pd.DataFrame:
    """Qué falta de verdad: celdas vacías por columna y periodos ausentes por centro (frente a los 108 meses esperados)."""
    esperados = set(pd.period_range(PERIODO_INICIO, PERIODO_FIN, freq="M").astype(str))
    filas = []
    for columna in plata.columns:
        vacias = plata[plata[columna].isna()]
        if len(vacias):
            filas.append({"tipo": "celda_vacia", "centro": "; ".join(sorted(vacias["centro"].unique())), "columna": columna,
                          "detalle": "; ".join(f"{r.periodo} {r.categoria}" for r in vacias.itertuples()), "n": int(len(vacias))})
    for centro, g in plata.groupby("centro"):
        ausentes = sorted(esperados - set(g["periodo"]))
        if ausentes:
            filas.append({"tipo": "periodos_ausentes", "centro": centro, "columna": "(todas)",
                          "detalle": f"{ausentes[0]} a {ausentes[-1]}" + ("" if len(ausentes) == (pd.Period(ausentes[-1], "M") - pd.Period(ausentes[0], "M")).n + 1 else " (no consecutivos)"),
                          "n": len(ausentes)})
    return pd.DataFrame(filas, columns=["tipo", "centro", "columna", "detalle", "n"])


def diagnostico(inv: pd.DataFrame, plata: pd.DataFrame) -> list:
    """Mecanismo de cada hallazgo, con la evidencia que lo sostiene y lo que NO se puede decir."""
    out = []
    manzanillo = plata[plata["centro"] == "Manzanillo"]
    n_man = int(manzanillo.isna().sum().sum())
    out.append({"caso": "Manzanillo (alcance del observatorio)", "faltantes": n_man,
                "mecanismo": "no aplica: no hay valores faltantes ni periodos ausentes",
                "tratamiento": "ninguno; no se imputa ni se elimina nada"})
    for r in inv[inv.tipo == "celda_vacia"].itertuples():
        otros = int((plata[(plata.periodo == r.detalle.split()[0])][r.columna].isna()).sum())
        out.append({"caso": f"{r.centro}, {r.columna} ({r.detalle})", "faltantes": int(r.n),
                    "mecanismo": f"INDETERMINADO: con {r.n} celda vacía no se puede contrastar completamente al azar frente a al azar; "
                                 f"coincide con el inicio de la pandemia (marzo de 2020), pero solo {otros} celda(s) falta(n) ese mes en todo el archivo",
                    "tratamiento": "se marca (`faltante_turistas_noche`) y no se imputa; la fila queda fuera de las derivadas que usan la columna"})
    for r in inv[inv.tipo == "periodos_ausentes"].itertuples():
        out.append({"caso": f"{r.centro}, periodos ausentes ({r.detalle})", "faltantes": int(r.n),
                    "mecanismo": "NO AL AZAR (ausencia estructural): faltan todas las columnas de meses consecutivos al final de la serie; el centro dejó de "
                                 "reportar, y esa ausencia depende del propio dato que no se observa",
                    "tratamiento": "no se imputa (la imputación inventaría un destino que no reportó); el centro queda fuera de las series que exigen 108 meses"})
    return out


# ---------------------------------------------------------------- tratamientos
def _vecinos(x: np.ndarray, falta: np.ndarray):
    return np.where(~falta)[0]


def imputar(x: np.ndarray, falta: np.ndarray, metodo: str, periodo_mes: np.ndarray) -> np.ndarray:
    """Devuelve ``x`` con los valores de ``falta`` reconstruidos. Solo usa los valores observados."""
    obs = ~falta
    y = x.astype(float).copy()
    idx = np.arange(len(x))
    if metodo == "media":
        y[falta] = x[obs].mean()
    elif metodo == "mediana":
        y[falta] = np.median(x[obs])
    elif metodo == "interpolacion_lineal":
        y[falta] = np.interp(idx[falta], idx[obs], x[obs])                     # fuera del rango observado repite el extremo
    elif metodo == "interpolacion_estacional":
        for i in idx[falta]:
            mismo_mes = obs & (periodo_mes == periodo_mes[i])
            y[i] = x[mismo_mes].mean() if mismo_mes.any() else np.interp(i, idx[obs], x[obs])
    elif metodo == "knn":                                                      # k = 3 meses cuyo vecino anterior y posterior se parecen más
        lin = np.interp(idx, idx[obs], x[obs])
        for i in idx[falta]:
            candidatos = [j for j in idx[obs] if 0 < j < len(x) - 1 and obs[j - 1] and obs[j + 1]]
            if not candidatos or i in (0, len(x) - 1):
                y[i] = lin[i]
                continue
            d = [abs(lin[i - 1] - x[j - 1]) + abs(lin[i + 1] - x[j + 1]) for j in candidatos]
            cercanos = [candidatos[k] for k in np.argsort(d, kind="stable")[:3]]
            y[i] = x[cercanos].mean()
    else:
        raise ValueError(f"método desconocido: {metodo!r}")
    return y


def _mascara(mecanismo: str, x: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    n, m = len(x), int(round(FRACCION * len(x)))
    falta = np.zeros(n, dtype=bool)
    if mecanismo == "completamente_al_azar":
        falta[rng.choice(np.arange(1, n - 1), m, replace=False)] = True
    elif mecanismo == "bloque_de_3_meses":
        for _ in range(3):                                                     # tres bloques de 3 meses, sin tocar los extremos
            ini = int(rng.integers(1, n - 4))
            falta[ini:ini + 3] = True
    elif mecanismo == "no_al_azar_valores_altos":
        interior = np.arange(1, n - 1)
        falta[interior[np.argsort(x[interior])[-m:]]] = True                   # lo que falta depende del propio valor: los más altos
    else:
        raise ValueError(mecanismo)
    return falta


def simular(serie_entrenamiento: pd.Series, replicas: int = REPLICAS, semilla: int = SEMILLA) -> pd.DataFrame:
    """RMSE, MAE y sesgo de cada tratamiento por mecanismo, sobre la serie de entrenamiento (nunca 2024)."""
    if serie_entrenamiento.index.max() > pd.Period(FIN_ENTRENAMIENTO, "M"):
        raise ValueError("la simulación solo usa 2016-2023")
    x = serie_entrenamiento.to_numpy(dtype=float)
    mes = np.asarray(serie_entrenamiento.index.month)
    filas = []
    for mecanismo in MECANISMOS:
        rng = np.random.default_rng([semilla, MECANISMOS.index(mecanismo)])
        errores = {m: [] for m in METODOS}
        for _ in range(replicas):
            falta = _mascara(mecanismo, x, rng)
            for m in METODOS:
                errores[m].append(imputar(x, falta, m, mes)[falta] - x[falta])
        for m in METODOS:
            e = np.concatenate(errores[m])
            filas.append({"mecanismo": mecanismo, "metodo": m, "rmse": float(np.sqrt((e ** 2).mean())), "mae": float(np.abs(e).mean()),
                          "sesgo": float(e.mean()), "meses_ocultos_por_replica": int(round(FRACCION * len(x))) if mecanismo != "bloque_de_3_meses" else 9})
    return pd.DataFrame(filas)


def calcular(oro: "Path | str | None" = None, plata: "Path | str | None" = None) -> tuple:
    df_plata = pd.read_csv(plata or PLATA, dtype={"periodo": str})
    inv = inventario(df_plata)
    entrenamiento, _ = partir_entrenamiento_prueba(serie_objetivo(cargar_oro_mensual(oro)))
    sim = simular(entrenamiento)
    mejor = {m: sim[sim.mecanismo == m].sort_values("rmse").iloc[0]["metodo"] for m in MECANISMOS}
    resumen = {"serie": "Manzanillo, ocupacion_pct, entrenamiento 2016-01 a 2023-12 (96 meses); 2024 no se usa",
               "replicas": REPLICAS, "semilla": SEMILLA, "fraccion_oculta": FRACCION, "periodos_esperados": N_PERIODOS,
               "mejor_metodo_por_mecanismo_rmse": mejor, "diagnostico": diagnostico(inv, df_plata),
               "faltantes_en_manzanillo": int(df_plata[df_plata.centro == "Manzanillo"].isna().sum().sum())}
    return inv, sim, resumen


def ejecutar(salida: "Path | str | None" = None, oro: "Path | str | None" = None, plata: "Path | str | None" = None) -> dict:
    salida = Path(salida) if salida else SALIDA
    inv, sim, resumen = calcular(oro, plata)
    salida.mkdir(parents=True, exist_ok=True)
    (salida / "inventario_faltantes.csv").write_bytes(inv.to_csv(index=False, lineterminator="\n").encode("utf-8"))
    (salida / "imputacion_comparacion.csv").write_bytes(sim.to_csv(index=False, float_format="%.4f", lineterminator="\n").encode("utf-8"))
    (salida / "resumen.json").write_bytes((json.dumps(resumen, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    return resumen


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--salida")
    a = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(ejecutar(a.salida), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
