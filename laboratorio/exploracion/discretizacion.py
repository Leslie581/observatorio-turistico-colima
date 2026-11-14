"""Comparación de la discretización por ancho, por frecuencia y supervisada de la ocupación hotelera (E1).

    python -m laboratorio.exploracion.discretizacion

Lee solo el oro mensual (validado por ``pipeline.interfaz``) y escribe en
``laboratorio/exploracion/resultados/discretizacion_supervisada/``:
  * ``comparacion_metodos.csv``: por escenario y método, cortes, meses por nivel y calidad de la partición (ganancia de
    información y exactitud) en el ajuste y en 2024;
  * ``resumen.json``: definición del objetivo, parámetros, criterio MDL y valor p de permutación.

Reglas: los cortes de los tres métodos se ajustan SOLO con 2016-01 a 2023-12 (con ``ErrorFuga`` si no); 2024 solo evalúa. Escenarios:
  * ``sin_covid``: ajuste con los meses que no son de COVID (80 de 96); escenario principal, porque el COVID rompió la estacionalidad;
  * ``todo_entrenamiento``: ajuste con los 96 meses (sensibilidad; es el ajuste de ``pipeline/transformaciones.py``).
No se hace ningún modelado: es descriptivo. Solo usa numpy y pandas.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

from pipeline import discretizacion_supervisada as ds
from pipeline.interfaz import cargar_oro_mensual, partir_entrenamiento_prueba, serie_objetivo
from pipeline.transformaciones import aplicar_discretizacion, ajustar_discretizacion

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "laboratorio" / "exploracion" / "resultados" / "discretizacion_supervisada"
K = 3
MIN_HOJA = 8
N_PERMUTACIONES = 500
METODOS = ("ancho_igual", "frecuencia_igual", ds.METODO)


def _ajuste(metodo: str, x: pd.Series, y: pd.Series, usar: pd.Series):
    if metodo == ds.METODO:
        ps = ds.ajustar_supervisada(x, y, k=K, min_hoja=MIN_HOJA, excluir=~usar)   # la exclusión (COVID) queda registrada en los parámetros
        return ps.discretizacion, ps
    return ajustar_discretizacion(x[usar], metodo, K), None


def _fila(escenario, metodo, p, ps, x_tr, y_tr, x_te, y_te, usar):
    niv_tr = aplicar_discretizacion(x_tr, p).astype(str)
    niv_te = aplicar_discretizacion(x_te, p).astype(str)
    regla = ds.regla_mayoritaria(niv_tr[usar], y_tr[usar])
    etiquetas = list(p.etiquetas)
    return {
        "escenario": escenario, "metodo": metodo, "cortes": " | ".join(f"{b:.4f}" for b in p.bordes),
        "meses_por_nivel_ajuste": " / ".join(str(int((niv_tr[usar] == e).sum())) for e in etiquetas),
        "meses_por_nivel_2024": " / ".join(str(int((niv_te == e).sum())) for e in etiquetas),
        "ganancia_bits_ajuste": ds.informacion_mutua(niv_tr[usar], y_tr[usar]),
        "exactitud_ajuste": ds.exactitud(niv_tr[usar], y_tr[usar], regla),
        "exactitud_referencia_ajuste": float(max(y_tr[usar].mean(), 1 - y_tr[usar].mean())),  # predecir siempre la clase más frecuente
        "ganancia_bits_2024": ds.informacion_mutua(niv_te, y_te),
        "exactitud_2024": ds.exactitud(niv_te, y_te, regla),
        "exactitud_referencia_2024": float((y_te == int(round(y_tr[usar].mean()))).mean()),  # la misma clase mayoritaria del ajuste, sin niveles
        "mdlp_acepta_cortes": " / ".join("sí" if a else "no" for a in ps.mdlp_acepta) if ps else "no aplica",
    }


def _valor_p(p: float) -> dict:
    """Valor p con la corrección (b + 1) / (B + 1) y lo que significa: ``b`` permutaciones con ganancia igual o mayor de ``B``.

    Con b = 0 el valor es 1 / (B + 1): **el mínimo que el procedimiento puede dar**, es decir, su límite de resolución. No es un
    valor exacto ni se convierte en una desigualdad: solo dice que ninguna de las B permutaciones igualó la ganancia observada.
    """
    b = int(round(p * (N_PERMUTACIONES + 1))) - 1
    return {"p_valor_permutacion": round(p, 6), "permutaciones_con_ganancia_igual_o_mayor": b,
            "p_valor_minimo_alcanzable": round(1 / (N_PERMUTACIONES + 1), 6),
            "p_valor_en_el_limite_de_resolucion": b == 0}


def calcular(oro: "Path | str | None" = None) -> tuple[pd.DataFrame, dict]:
    df = cargar_oro_mensual(oro)
    x = serie_objetivo(df)
    x_tr, x_te = partir_entrenamiento_prueba(x)
    y_tr, y_te = ds.temporada_alta(x_tr.index), ds.temporada_alta(x_te.index)
    covid = df["d_covid"].astype(bool).reindex(x_tr.index)
    filas, resumen = [], {}
    for escenario, usar in (("sin_covid", ~covid), ("todo_entrenamiento", pd.Series(True, index=x_tr.index))):
        for metodo in METODOS:
            p, ps = _ajuste(metodo, x_tr, y_tr, usar)
            filas.append(_fila(escenario, metodo, p, ps, x_tr, y_tr, x_te, y_te, usar))
            if ps is not None:
                ganancia = ds.informacion_mutua(aplicar_discretizacion(x_tr[usar], p).astype(str), y_tr[usar])
                resumen[f"supervisada_{escenario}"] = {
                    "cortes": list(p.bordes), "ganancias_por_corte_bits": [round(g, 6) for g in ps.ganancias_bits],
                    "mdlp_acepta": list(ps.mdlp_acepta), "meses_ajuste": p.n, "meses_excluidos": ps.excluidos,
                    "ganancia_total_bits": round(ganancia, 6),
                    **_valor_p(ds.p_valor_permutacion(x_tr[usar], y_tr[usar], ganancia, K, MIN_HOJA, N_PERMUTACIONES))}
    tabla = pd.DataFrame(filas)
    resumen.update({
        "objetivo": "temporada_alta = 1 si el mes es julio, agosto o diciembre (calendario; no usa ocupación)",
        "variable_discretizada": "ocupacion_pct", "k": K, "min_hoja": MIN_HOJA, "permutaciones": N_PERMUTACIONES,
        "semilla_permutaciones": ds.SEMILLA_PERMUTACIONES,
        "ajuste": "solo 2016-01 a 2023-12; 2024 (12 meses) solo evalúa los cortes ya fijados",
        "entropia_objetivo_ajuste_sin_covid_bits": round(ds.entropia(y_tr[~covid]), 6),
        "meses_temporada_alta_2024": int(y_te.sum()), "meses_2024": int(len(y_te))})
    return tabla, resumen


def ejecutar(oro: "Path | str | None" = None, salida: "Path | str | None" = None) -> dict:
    salida = Path(salida) if salida else SALIDA
    tabla, resumen = calcular(oro)
    salida.mkdir(parents=True, exist_ok=True)
    (salida / "comparacion_metodos.csv").write_bytes(tabla.to_csv(index=False, float_format="%.6f", lineterminator="\n").encode("utf-8"))
    (salida / "resumen.json").write_bytes((json.dumps(resumen, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    return resumen


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--oro", help="ruta del oro mensual (por defecto, el versionado)")
    ap.add_argument("--salida", help="carpeta de salida")
    a = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(ejecutar(a.oro, a.salida), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
