"""Exploración estadística de la ocupación hotelera de Manzanillo (E1, integrante A).

Lee SOLO la capa oro (`data/oro/manzanillo_ocupacion_mensual.csv`) mediante `pipeline.interfaz` y genera:
  * 4 gráficas PNG en `laboratorio/exploracion/resultados/figuras/`
  * `estadisticas_descriptivas.csv`, `estadisticas_por_anio.csv`, `estadisticas_por_mes.csv` y `resumen.json`
  * `transformaciones_ocupacion.csv` y `parametros_transformaciones.json` (min-max, z-score y niveles; parámetros SOLO con 2016-2023)

    python -m laboratorio.exploracion.explorar            # usa el oro versionado y escribe en resultados/

Es descriptiva: no ajusta modelos ni explica causas. Las pruebas de estacionariedad, ACF/PACF y los pronósticos
son del laboratorio de la integrante B (`laboratorio/pronosticos/`) y NO se repiten aquí. Interpretación: docs/E1/exploracion.md.
Requiere matplotlib (requirements-lab.txt). Las cifras salen de pandas y son idénticas entre corridas; los PNG se generan
sin marcas de tiempo, de modo que la misma versión de matplotlib produce los mismos bytes.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

from pipeline.config import COVID_FIN, COVID_INICIO, FIN_ENTRENAMIENTO, OFERTA_2017, RAIZ
from pipeline.interfaz import cargar_oro_mensual, serie_objetivo
from pipeline.transformaciones import transformar_serie_oro

SALIDA = RAIZ / "laboratorio" / "exploracion" / "resultados"
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
SEGUNDO_SALTO_OFERTA = "2017-11"  # contrato §1.1: segundo salto de la oferta, sin indicador propio en 1.0.0
FIGURAS = {
    "serie": "01_serie_mensual_ocupacion.png",
    "boxplot": "02_boxplot_ocupacion_por_mes.png",
    "calor": "03_mapa_calor_anio_mes.png",
    "curvas": "04_curvas_mensuales_por_anio.png",
}
# Paleta mínima: un acento azul para los datos, naranja SOLO para el periodo COVID, grises para el resto.
TINTA, GRIS, AZUL, NARANJA, AZUL_OSC = "#222222", "#8a8f98", "#2a6fbb", "#d9822b", "#123a6b"


# ---------------------------------------------------------------- estadísticas
def _resumen(x: pd.Series) -> dict:
    return {"n": int(x.count()), "media": float(x.mean()), "desv_est": float(x.std(ddof=1)), "min": float(x.min()),
            "p25": float(x.quantile(0.25)), "mediana": float(x.median()), "p75": float(x.quantile(0.75)),
            "max": float(x.max()), "coef_var_pct": float(100 * x.std(ddof=1) / x.mean()), "asimetria": float(x.skew())}


def estadisticas(df: pd.DataFrame) -> dict:
    """Tablas descriptivas. Todas son DESCRIPTIVAS de la serie observada; ninguna se usa para ajustar nada."""
    y = df["ocupacion_pct"].astype(float)
    corte = pd.Period(FIN_ENTRENAMIENTO, "M")
    covid = df["d_covid"] == 1
    grupos = {
        "todo_2016_2024": y,
        "entrenamiento_2016_2023": y[y.index <= corte],
        "prueba_2024": y[y.index > corte],
        "sin_covid": y[~covid],
        "covid_2020_03_a_2021_06": y[covid],
        "entrenamiento_sin_covid": y[(y.index <= corte) & ~covid],
    }
    general = pd.DataFrame({k: _resumen(v) for k, v in grupos.items()}).T.rename_axis("grupo").reset_index()

    d = pd.DataFrame({"y": y, "anio": y.index.year, "mes": y.index.month, "covid": covid})
    por_anio = d.groupby("anio").agg(n=("y", "size"), media=("y", "mean"), desv_est=("y", "std"), min=("y", "min"),
                                     max=("y", "max"), n_meses_covid=("covid", "sum")).reset_index()
    por_anio["mes_min"] = [MESES[int(d[d.anio == a].y.idxmin().month) - 1] for a in por_anio.anio]
    por_anio["mes_max"] = [MESES[int(d[d.anio == a].y.idxmax().month) - 1] for a in por_anio.anio]
    sc = d[~d.covid]
    por_mes = d.groupby("mes").agg(n=("y", "size"), media=("y", "mean"), mediana=("y", "median"), desv_est=("y", "std"),
                                   min=("y", "min"), max=("y", "max")).reset_index()
    por_mes["n_sin_covid"] = sc.groupby("mes")["y"].size().to_numpy()
    por_mes["media_sin_covid"] = sc.groupby("mes")["y"].mean().to_numpy()
    por_mes["mediana_sin_covid"] = sc.groupby("mes")["y"].median().to_numpy()
    por_mes["nombre"] = MESES
    return {"general": general, "por_anio": por_anio, "por_mes": por_mes}


def resumen_json(df: pd.DataFrame, tablas: dict) -> dict:
    y = df["ocupacion_pct"].astype(float)
    pm, pa = tablas["por_mes"], tablas["por_anio"]
    dias = pd.Series(df.index.days_in_month, index=df.index)
    oferta_dia = df["cuartos_disponibles"] / dias
    p_oferta = pd.Period(OFERTA_2017, "M")
    p_oferta2 = pd.Period(SEGUNDO_SALTO_OFERTA, "M")
    cambio = lambda p: float(100 * (oferta_dia[p] / oferta_dia[p - 1] - 1))  # noqa: E731
    alto, bajo = pm.loc[pm.media_sin_covid.idxmax()], pm.loc[pm.media_sin_covid.idxmin()]
    atipicos = [str(p) for p in df.index[df["diag_atipico_iqr"] == 1]]
    return {
        "fuente": "data/oro/manzanillo_ocupacion_mensual.csv", "version_contrato": str(df["version_contrato"].iloc[0]),
        "sha256_bronce": str(df["sha256_bronce"].iloc[0]), "periodo": [str(y.index.min()), str(y.index.max()), int(len(y))],
        "minimo": {"periodo": str(y.idxmin()), "valor": float(y.min())}, "maximo": {"periodo": str(y.idxmax()), "valor": float(y.max())},
        "covid": {"inicio": COVID_INICIO, "fin": COVID_FIN, "n_meses": int((df.d_covid == 1).sum()),
                  "media_covid": float(y[df.d_covid == 1].mean()), "media_resto": float(y[df.d_covid == 0].mean())},
        "atipicos_iqr": atipicos,
        "oferta_diaria_implicita": {"cambio_2017_06_pct": cambio(p_oferta), "cambio_2017_11_pct": cambio(p_oferta2),
                                    "nota": "cuartos_disponibles / dias del mes, 2 a 5 estrellas; es oferta medida por el reporte, no causa"},
        "estacionalidad_sin_covid": {"mes_mas_alto": {"mes": alto["nombre"], "media": float(alto.media_sin_covid)},
                                     "mes_mas_bajo": {"mes": bajo["nombre"], "media": float(bajo.media_sin_covid)},
                                     "amplitud_pp": float(alto.media_sin_covid - bajo.media_sin_covid)},
        "anio_mas_bajo": {"anio": int(pa.loc[pa.media.idxmin(), "anio"]), "media": float(pa.media.min())},
        "anio_mas_alto": {"anio": int(pa.loc[pa.media.idxmax(), "anio"]), "media": float(pa.media.max())},
        "figuras": list(FIGURAS.values()),
        "avisos": ["Descriptivo: no se explican causas.", "Las pruebas de estacionariedad, ACF/PACF y los pronósticos son de laboratorio/pronosticos."],
    }


# ---------------------------------------------------------------- figuras
def _plt():
    import matplotlib
    matplotlib.use("Agg")  # sin ventana: reproducible y apto para CI
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRIS, "axes.labelcolor": TINTA,
                         "xtick.color": TINTA, "ytick.color": TINTA, "text.color": TINTA, "axes.spines.top": False,
                         "axes.spines.right": False, "axes.grid": True, "grid.color": "#e3e5e8", "grid.linewidth": 0.7,
                         "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white"})
    return plt


def _guardar(fig, ruta: Path):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta, dpi=150, bbox_inches="tight", metadata={"Software": None})  # sin marcas de tiempo ni versión
    import matplotlib.pyplot as plt
    plt.close(fig)


def _fechas(df):
    return df.index.to_timestamp()


def figura_serie(df: pd.DataFrame, ruta: Path):
    plt = _plt()
    f = _fechas(df)
    y = df["ocupacion_pct"].astype(float).to_numpy()
    dias = df.index.days_in_month
    oferta = (df["cuartos_disponibles"] / dias).to_numpy()
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(11, 6.6), sharex=True, gridspec_kw={"height_ratios": [3, 1.6], "hspace": 0.12})
    ini, fin = pd.Period(COVID_INICIO, "M").to_timestamp(), pd.Period(COVID_FIN, "M").to_timestamp(how="end")
    corte = pd.Period(FIN_ENTRENAMIENTO, "M").to_timestamp(how="end")
    for ax in (a1, a2):
        ax.axvspan(ini, fin, color=NARANJA, alpha=0.16, lw=0)
        ax.axvspan(corte, f.max() + pd.Timedelta(days=31), color=GRIS, alpha=0.12, lw=0)
        for p, est in ((OFERTA_2017, "-"), (SEGUNDO_SALTO_OFERTA, "--")):
            ax.axvline(pd.Period(p, "M").to_timestamp(), color=GRIS, lw=1.2, ls=est)
    a1.plot(f, y, color=AZUL, lw=2, marker="o", ms=3.2, mec="white", mew=0.5)
    at = df["diag_atipico_iqr"].to_numpy() == 1
    a1.scatter(f[at], y[at], s=46, color=NARANJA, zorder=5, edgecolor="white", linewidth=0.8, label="Atípico por IQR (2020-04 a 2020-06)")
    a1.set_ylabel("Ocupación (%)")
    a1.set_ylim(0, 72)
    a1.set_title("Ocupación hotelera mensual de Manzanillo, 2–5 estrellas (2016-01 a 2024-12)", loc="left", fontweight="bold", fontsize=12)
    a1.text(ini + (fin - ini) / 2, 69, "COVID\n2020-03 a 2021-06", ha="center", va="top", fontsize=8.5, color=TINTA)
    a1.text(corte + pd.Timedelta(days=20), 69, "Prueba\n2024", ha="left", va="top", fontsize=8.5, color=TINTA)
    a1.legend(loc="lower left", frameon=False, fontsize=8.5)
    a2.plot(f, oferta, color=AZUL_OSC, lw=1.8)
    a2.set_ylabel("Cuartos disponibles\npor día (implícito)")
    a2.set_ylim(0, oferta.max() * 1.18)
    x1, x2 = pd.Period(OFERTA_2017, "M").to_timestamp(), pd.Period(SEGUNDO_SALTO_OFERTA, "M").to_timestamp()
    a2.text(x1 - pd.Timedelta(days=25), oferta.max() * 1.12, "2017-06 (línea continua):\nprimer salto de la oferta", ha="right", va="top", fontsize=8.5)
    a2.text(x2 + pd.Timedelta(days=25), oferta.max() * 0.45, "2017-11 (línea discontinua):\nsegundo salto", ha="left", va="top", fontsize=8.5)
    a2.set_xlabel("Periodo (mes)")
    _guardar(fig, ruta)


def figura_boxplot(df: pd.DataFrame, ruta: Path):
    plt = _plt()
    y = df["ocupacion_pct"].astype(float)
    mes, anio, cov = y.index.month, y.index.year, (df["d_covid"] == 1).to_numpy()
    fig, ax = plt.subplots(figsize=(11, 5.6))
    datos = [y[mes == m].to_numpy() for m in range(1, 13)]
    ax.boxplot(datos, positions=range(1, 13), widths=0.55, showfliers=False, patch_artist=True,
               boxprops={"facecolor": "#dbe7f5", "edgecolor": AZUL, "linewidth": 1.2}, medianprops={"color": AZUL_OSC, "linewidth": 2},
               whiskerprops={"color": AZUL}, capprops={"color": AZUL})
    # Cada punto es un año; el desplazamiento horizontal es determinista (según el año), no aleatorio.
    desplazamiento = (anio.to_numpy() - 2020) * 0.045
    ax.scatter(mes.to_numpy()[~cov] + desplazamiento[~cov], y.to_numpy()[~cov], s=16, color=AZUL, alpha=0.75, zorder=3, label="Mes observado")
    ax.scatter(mes.to_numpy()[cov] + desplazamiento[cov], y.to_numpy()[cov], s=40, marker="D", color=NARANJA, zorder=4,
               edgecolor="white", linewidth=0.6, label="Mes de COVID (2020-03 a 2021-06)")
    ax.set_xticks(range(1, 13), MESES)
    ax.set_ylabel("Ocupación (%)")
    ax.set_ylim(0, 72)
    ax.set_title("Ocupación por mes del año, 2016–2024 (las cajas incluyen los meses de COVID)", loc="left", fontweight="bold", fontsize=12)
    ax.legend(loc="lower left", frameon=False, fontsize=9, ncol=2)
    ax.grid(axis="x", visible=False)
    _guardar(fig, ruta)


def figura_calor(df: pd.DataFrame, ruta: Path):
    plt = _plt()
    from matplotlib.patches import Rectangle
    y = df["ocupacion_pct"].astype(float)
    tabla = pd.DataFrame({"anio": y.index.year, "mes": y.index.month, "v": y.to_numpy()}).pivot(index="anio", columns="mes", values="v")
    cov = pd.DataFrame({"anio": y.index.year, "mes": y.index.month, "c": (df["d_covid"] == 1).to_numpy()}).pivot(index="anio", columns="mes", values="c")
    fig, ax = plt.subplots(figsize=(11.5, 5.8))
    im = ax.imshow(tabla.to_numpy(), cmap="Blues", vmin=0, vmax=70, aspect="auto")
    ax.grid(False)
    for i, a in enumerate(tabla.index):
        for j, m in enumerate(tabla.columns):
            v = tabla.iloc[i, j]
            ax.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=8.5, color="white" if v > 40 else TINTA)
            if bool(cov.iloc[i, j]):
                ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, edgecolor=NARANJA, linewidth=2.2))
    ax.set_xticks(range(12), MESES)
    ax.set_yticks(range(len(tabla.index)), [str(a) for a in tabla.index])
    ax.set_xlabel("Mes")
    ax.set_ylabel("Año")
    ax.set_title("Ocupación (%) por año y mes · recuadro naranja = meses de COVID (2020-03 a 2021-06)", loc="left", fontweight="bold", fontsize=12)
    cb = fig.colorbar(im, ax=ax, pad=0.015, fraction=0.035)
    cb.set_label("Ocupación (%)")
    for s in ax.spines.values():
        s.set_visible(False)
    _guardar(fig, ruta)


def _separar_etiquetas(valores: dict, hueco: float = 2.3) -> dict:
    """Ubica etiquetas al final de cada curva sin que se encimen: orden por valor y separación mínima (determinista)."""
    orden = sorted(valores, key=valores.get)
    pos = {}
    previo = None
    for k in orden:
        v = valores[k] if previo is None else max(valores[k], previo + hueco)
        pos[k], previo = v, v
    return pos


def figura_curvas(df: pd.DataFrame, ruta: Path):
    plt = _plt()
    y = df["ocupacion_pct"].astype(float)
    cov = df["d_covid"].to_numpy() == 1
    fig, ax = plt.subplots(figsize=(11, 5.8))
    anios = sorted(set(y.index.year))
    finales = {}
    for a in anios:
        m = y.index.year == a
        s, c = y[m], cov[m]
        x = s.index.month.to_numpy()
        destacado = a in (2020, 2024)
        color = NARANJA if a == 2020 else AZUL_OSC if a == 2024 else "#9db8d8"
        ax.plot(x, s.to_numpy(), color=color, lw=2.6 if destacado else 1.5, zorder=4 if destacado else 2)
        if c.any():  # rombos naranjas = meses de COVID, en cualquier año (también ene-jun de 2021)
            ax.scatter(x[c], s.to_numpy()[c], s=26, marker="D", color=NARANJA, edgecolor="white", linewidth=0.5, zorder=5)
        finales[a] = float(s.to_numpy()[-1])
    pos = _separar_etiquetas(finales)
    for a in anios:
        destacado = a in (2020, 2024)
        ax.text(12.15, pos[a], str(a), va="center", ha="left", fontsize=8.5, fontweight="bold" if destacado else "normal",
                color=(NARANJA if a == 2020 else AZUL_OSC) if destacado else GRIS)
    ax.set_xticks(range(1, 13), MESES)
    ax.set_xlim(0.8, 12.9)
    ax.set_ylim(0, 72)
    ax.set_ylabel("Ocupación (%)")
    ax.set_title("Curvas mensuales por año · rombos naranjas = meses de COVID · 2024 (prueba) en azul oscuro", loc="left", fontweight="bold", fontsize=12)
    ax.grid(axis="x", visible=False)
    _guardar(fig, ruta)


# ---------------------------------------------------------------- transformaciones (pipeline/transformaciones.py)
def tabla_transformaciones(df: pd.DataFrame):
    """(parámetros por método, tabla de 108 filas). Los parámetros se ajustan SOLO con el entrenamiento (2016-2023)."""
    s = serie_objetivo(df)
    t_frec, tab = transformar_serie_oro(s, "frecuencia_igual", 3)
    t_anc, tab_anc = transformar_serie_oro(s, "ancho_igual", 3)
    tab = tab.rename(columns={"nivel": "nivel_frecuencia_igual"})
    tab["nivel_ancho_igual"] = tab_anc["nivel"].astype(str)
    tab["nivel_frecuencia_igual"] = tab["nivel_frecuencia_igual"].astype(str)
    tab.index = tab.index.astype(str)
    params = {"ajuste": "solo entrenamiento 2016-01 a 2023-12; 2024 se transforma con estos parámetros, sin recalcular",
              "minmax": t_frec.a_dict()["minmax"], "zscore": t_frec.a_dict()["zscore"],
              "discretizacion_frecuencia_igual": t_frec.a_dict()["discretizacion"],
              "discretizacion_ancho_igual": t_anc.a_dict()["discretizacion"],
              "n_prueba_fuera_del_rango_de_entrenamiento": int(tab[tab.conjunto == "prueba"]["fuera_rango_entrenamiento"].sum())}
    return params, tab.rename_axis("periodo").reset_index()


# ---------------------------------------------------------------- orquestación
def ejecutar(oro: "Path | str | None" = None, salida: "Path | str | None" = None) -> dict:
    """Genera tablas, resumen y las 4 figuras. Lee solo el oro (validado por `cargar_oro_mensual`)."""
    salida = Path(salida) if salida else SALIDA
    df = cargar_oro_mensual(oro)
    tablas = estadisticas(df)
    res = resumen_json(df, tablas)
    salida.mkdir(parents=True, exist_ok=True)
    for nombre, tabla in (("estadisticas_descriptivas", tablas["general"]), ("estadisticas_por_anio", tablas["por_anio"]),
                          ("estadisticas_por_mes", tablas["por_mes"])):
        (salida / f"{nombre}.csv").write_bytes(tabla.to_csv(index=False, float_format="%.4f", lineterminator="\n").encode("utf-8"))
    (salida / "resumen.json").write_bytes((json.dumps(res, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    params, tab = tabla_transformaciones(df)
    (salida / "parametros_transformaciones.json").write_bytes((json.dumps(params, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    (salida / "transformaciones_ocupacion.csv").write_bytes(tab.to_csv(index=False, float_format="%.6f", lineterminator="\n").encode("utf-8"))
    fig = salida / "figuras"
    figura_serie(df, fig / FIGURAS["serie"])
    figura_boxplot(df, fig / FIGURAS["boxplot"])
    figura_calor(df, fig / FIGURAS["calor"])
    figura_curvas(df, fig / FIGURAS["curvas"])
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--oro", help="ruta del oro mensual (por defecto, el versionado)")
    ap.add_argument("--salida", help="carpeta de salida (por defecto, laboratorio/exploracion/resultados)")
    a = ap.parse_args(argv)
    res = ejecutar(a.oro, a.salida)
    print(f"exploración lista: {len(res['figuras'])} figuras, periodo {res['periodo'][0]} a {res['periodo'][1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
