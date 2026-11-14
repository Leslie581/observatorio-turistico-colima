"""Ruido de la ocupación mensual: cuánto es ruido, cuánto estacionalidad y cuánto evento real (Ingeniería de Datos, E1, mejora posterior a la entrega).

    python -m laboratorio.exploracion.ruido

Reutiliza la descomposición STL robusta ya versionada (``laboratorio/pronosticos/resultados/descomposicion_componentes.csv``): serie = tendencia +
estacional + residuo. Cuantifica la parte de la varianza que explica cada componente, la razón señal/ruido y clasifica los meses de residuo
extremo (puntaje z robusto > 3.5) como evento real (COVID, regla de calendario del contrato) o «sin causa conocida: revisar».
Descriptivo: no modifica el oro ni elimina ningún mes. Escribe ``laboratorio/exploracion/resultados/ruido/``: ``componentes_varianza.csv``,
``residuos_extremos.csv`` y ``resumen.json``. Solo usa numpy y pandas.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from pipeline.interfaz import cargar_oro_mensual

RAIZ = Path(__file__).resolve().parents[2]
STL = RAIZ / "laboratorio" / "pronosticos" / "resultados" / "descomposicion_componentes.csv"
SALIDA = RAIZ / "laboratorio" / "exploracion" / "resultados" / "ruido"
UMBRAL_Z = 3.5
CONSTANTE_MAD = 0.6745


def _z(x: pd.Series) -> pd.Series:
    mad = (x - x.median()).abs().median()
    return CONSTANTE_MAD * (x - x.median()) / mad


def calcular(ruta_stl: Path = STL, oro: "Path | str | None" = None) -> tuple:
    stl = pd.read_csv(ruta_stl).set_index("periodo")
    df = cargar_oro_mensual(oro)
    covid = pd.Series(df["d_covid"].astype(bool).to_numpy(), index=df.index.astype(str))
    y, t, s, r = (stl[c] for c in ("observado", "tendencia_stl", "estacional_stl", "residuo_stl"))
    var_y = float(y.var(ddof=1))
    filas = [{"componente": n, "varianza": round(float(v.var(ddof=1)), 4), "porcentaje_de_la_varianza_observada": round(100 * float(v.var(ddof=1)) / var_y, 2)}
             for n, v in (("tendencia", t), ("estacional", s), ("residuo (ruido)", r))]
    tabla = pd.DataFrame(filas)
    sin_covid = ~covid.reindex(stl.index).fillna(False).to_numpy()
    z = _z(r)
    ext = pd.DataFrame({"periodo": r.index, "residuo_stl": r.round(3).to_numpy(), "z_robusto": z.round(3).to_numpy(),
                        "d_covid": covid.reindex(r.index).to_numpy()})
    ext = ext[ext.z_robusto.abs() > UMBRAL_Z].reset_index(drop=True)
    ext["tipo"] = np.where(ext.d_covid, "evento real (COVID, regla de calendario)", "sin causa conocida: revisar")
    señal = float((t + s).var(ddof=1))
    m = pd.Series(sin_covid, index=stl.index)
    var_sc = float(y[m].var(ddof=1))
    pct_sc = {n: round(100 * float(v[m].var(ddof=1)) / var_sc, 2) for n, v in (("tendencia", t), ("estacional", s), ("residuo", r))}
    resumen = {"n_meses": int(len(y)), "desviacion_residuo_pp": round(float(r.std(ddof=1)), 3),
               "desviacion_residuo_sin_covid_pp": round(float(r[m].std(ddof=1)), 3),
               "razon_senal_ruido": round(señal / float(r.var(ddof=1)), 2),
               "porcentaje_residuo_todos_los_meses": float(tabla.iloc[2].porcentaje_de_la_varianza_observada),
               "porcentaje_por_componente_sin_covid": pct_sc,
               "meses_residuo_extremo": int(len(ext)), "extremos_covid": int(ext.d_covid.sum()),
               "extremos_sin_causa_conocida": int((~ext.d_covid).sum()),
               "lectura": "Con todos los meses el residuo STL absorbe ~41 % de la varianza, pero la mayor parte es el evento real COVID (5 de los 7 meses "
                          "extremos): sin COVID la desviación del residuo baja de 8.06 a 2.87 pp. Los 2 extremos restantes (2017-04 y 2019-08, positivos) no tienen causa "
                          "conocida en el contrato: se marcan y se conservan; una hipótesis por verificar es el calendario (p. ej. Semana Santa), no un error de captura. "
                          "El residuo mezcla ruido de medición y variación real y no puede separarse sin una segunda fuente; no se elimina ni se suaviza ningún mes."}
    return tabla, ext, resumen


def ejecutar(salida: "Path | str | None" = None) -> dict:
    salida = Path(salida) if salida else SALIDA
    salida.mkdir(parents=True, exist_ok=True)
    tabla, ext, resumen = calcular()
    for nombre, d in (("componentes_varianza.csv", tabla), ("residuos_extremos.csv", ext)):
        (salida / nombre).write_bytes(d.to_csv(index=False, float_format="%.4f", lineterminator="\n").encode("utf-8"))
    (salida / "resumen.json").write_bytes((json.dumps(resumen, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    return resumen


def main(argv=None) -> int:
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(ejecutar(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
