"""Atípicos y ruido: IQR frente a puntaje z robusto (MAD) sobre la ocupación mensual y la decisión por tipo (Ingeniería de Datos, E1).

    python -m laboratorio.exploracion.atipicos

El PDF (págs. 15 y 24) pide detección «por rango intercuartílico, puntaje z robusto o Isolation Forest» y «una decisión documentada
para cada tipo: corregir, marcar o eliminar». El pipeline ya marca con IQR 1.5 (``diag_atipico_iqr``); aquí se contrasta con el
puntaje z robusto y se clasifica cada mes señalado por su causa. Escribe ``laboratorio/exploracion/resultados/atipicos/``:
``comparacion_metodos.csv`` (un renglón por mes señalado por algún método) y ``resumen.json``.
Descriptivo: no modifica el oro ni elimina ningún mes. Solo usa numpy y pandas.
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
SALIDA = RAIZ / "laboratorio" / "exploracion" / "resultados" / "atipicos"
UMBRAL_Z = 3.5          # umbral habitual de Iglewicz y Hoaglin para el puntaje z modificado
CONSTANTE_MAD = 0.6745  # hace el MAD comparable con la desviación estándar de una normal


def z_robusto(y: pd.Series) -> pd.Series:
    """Puntaje z modificado: 0.6745 (x - mediana) / MAD."""
    mediana = y.median()
    mad = (y - mediana).abs().median()
    if mad == 0:
        raise ValueError("el MAD es cero: el puntaje z robusto no está definido")
    return CONSTANTE_MAD * (y - mediana) / mad


def limites_iqr(y: pd.Series, k: float = 1.5) -> tuple:
    q1, q3 = y.quantile([0.25, 0.75])
    return float(q1 - k * (q3 - q1)), float(q3 + k * (q3 - q1))


def calcular(oro: "Path | str | None" = None) -> tuple:
    df = cargar_oro_mensual(oro)
    y = df["ocupacion_pct"].astype(float)
    bajo, alto = limites_iqr(y)
    z = z_robusto(y)
    iqr = (y < bajo) | (y > alto)
    zr = z.abs() > UMBRAL_Z
    covid = df["d_covid"].astype(bool)
    tabla = pd.DataFrame({"periodo": df.index.astype(str), "ocupacion_pct": y.round(4).to_numpy(), "z_robusto": z.round(3).to_numpy(),
                          "iqr": iqr.to_numpy(), "z_robusto_mayor_3_5": zr.to_numpy(), "d_covid": covid.to_numpy()})
    tabla = tabla[tabla.iqr | tabla.z_robusto_mayor_3_5].reset_index(drop=True)

    def tipo(r):
        if r.d_covid:
            return "evento real (COVID, regla de calendario)"
        return "sin causa conocida: revisar"
    tabla["tipo"] = tabla.apply(tipo, axis=1)
    tabla["decision"] = np.where(tabla.d_covid, "MARCAR y conservar (no es un error: es el hallazgo)", "MARCAR y revisar contra la fuente")
    resumen = {"serie": "ocupacion_pct de Manzanillo, 108 meses", "iqr_k": 1.5, "limites_iqr": [round(bajo, 4), round(alto, 4)],
               "umbral_z_robusto": UMBRAL_Z, "senalados_iqr": int(iqr.sum()), "senalados_z_robusto": int(zr.sum()),
               "senalados_por_ambos": int((iqr & zr).sum()), "solo_iqr": [str(p) for p in df.index[iqr & ~zr]],
               "solo_z_robusto": [str(p) for p in df.index[zr & ~iqr]], "meses_covid_senalados": int((tabla.d_covid).sum()),
               "senalados_fuera_de_covid": int((~tabla.d_covid).sum()),
               "decision_por_tipo": {"error de captura (ocupados > disponibles)": "CUARENTENA con motivo (regla R-D06; en Manzanillo: 0 casos)",
                                     "evento real (COVID)": "MARCAR y conservar; se modela con la variable de calendario d_covid",
                                     "ruido (variación mes a mes sin causa)": "CONSERVAR sin suavizar: la serie es la medición; el pronóstico lo absorbe en la varianza",
                                     "valor sin causa conocida": "MARCAR y revisar contra la fuente; no se elimina sin evidencia"}}
    return tabla, resumen


def ejecutar(salida: "Path | str | None" = None, oro: "Path | str | None" = None) -> dict:
    salida = Path(salida) if salida else SALIDA
    tabla, resumen = calcular(oro)
    salida.mkdir(parents=True, exist_ok=True)
    (salida / "comparacion_metodos.csv").write_bytes(tabla.to_csv(index=False, lineterminator="\n").encode("utf-8"))
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
