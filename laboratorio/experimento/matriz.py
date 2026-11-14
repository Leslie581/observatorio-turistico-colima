"""Matriz del diseño factorial 2^3 del experimento de E2 (ruta ingeniería: nuestro propio extractor).

    python -m laboratorio.experimento.matriz

PREPARACIÓN, no el experimento: fija la estructura que pide el PDF (pág. 17) para que E2 solo tenga que correrla.
  * 3 factores a 2 niveles: procesos (1 / 4), analizador (json / orjson) y formato de salida (csv / parquet). Los niveles
    DEFINITIVOS se confirman en E2 (docs/E0/propuesta.md §4); aquí solo se codifican como -1 / +1.
  * Dos réplicas completas = dos bloques (día 1 y día 2, la fuente de variación que no controlamos): cada tratamiento aparece
    exactamente una vez por bloque, y el ORDEN de las 8 corridas se aleatoriza dentro de cada bloque con una semilla fija.
  * Respuestas: segundos de procesamiento y tasa de error. Se correrá contra una copia local de las respuestas ya capturadas
    (``data/bronce/denue``), nunca contra un sitio ajeno.
No ejecuta ninguna corrida ni mide tiempos. Solo usa numpy, pandas y la biblioteca estándar.
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd

FACTORES = {"procesos": (1, 4), "analizador": ("json", "orjson"), "formato": ("csv", "parquet")}
BLOQUES = ("dia_1", "dia_2")
SEMILLA = 20261113
SALIDA = Path(__file__).resolve().parent / "resultados" / "matriz_2x3.csv"


def matriz(semilla: int = SEMILLA, bloques: tuple = BLOQUES) -> pd.DataFrame:
    """Diseño 2^3 con un bloque por réplica y orden aleatorio dentro de cada bloque."""
    rng = np.random.default_rng(semilla)
    nombres = list(FACTORES)
    base = list(itertools.product((-1, 1), repeat=len(nombres)))                    # orden estándar
    filas = []
    for bloque in bloques:
        orden = rng.permutation(len(base))
        for corrida, i in enumerate(orden, start=1):
            codigos = base[i]
            fila = {"bloque": bloque, "corrida": corrida, "tratamiento": i + 1}
            fila.update({f"{n}_cod": c for n, c in zip(nombres, codigos)})
            fila.update({n: FACTORES[n][0 if c < 0 else 1] for n, c in zip(nombres, codigos)})
            filas.append(fila)
    return pd.DataFrame(filas)


def escribir(ruta: "Path | str" = SALIDA, semilla: int = SEMILLA) -> pd.DataFrame:
    m = matriz(semilla)
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_bytes(m.to_csv(index=False, lineterminator="\n").encode("utf-8"))
    return m


def main(argv=None) -> int:
    m = escribir()
    print(f"{len(m)} corridas ({len(BLOQUES)} bloques x 8 tratamientos) en {SALIDA.name}, semilla {SEMILLA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
