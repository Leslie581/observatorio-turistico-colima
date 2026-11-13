"""Orquestador reproducible del laboratorio de pronósticos E1.

    python -m laboratorio.pronosticos.ejecutar                # oro si existe; si no, referencia §7
    python -m laboratorio.pronosticos.ejecutar --fuente oro   # exige el oro (evaluación definitiva)

Escribe en ``laboratorio/pronosticos/resultados/``: tablas CSV, ``resumen.json``, ``ejecucion.json``
(versiones, fuente y huellas) y figuras PNG en ``figuras/``. Cada figura tiene su tabla CSV.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import warnings
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path

import numpy as np
import pandas as pd

from . import datos
from . import estadistica as est
from . import modelos as mod

SALIDA = Path(__file__).resolve().parent / "resultados"
VARIABLES_D7 = ["pct_cuartos_no_residentes", "estadia_promedio", "densidad_ocupacion"]

# Paleta de referencia (skill dataviz, modo claro): orden categórico fijo por familia.
COLOR = {"SES": "#2a78d6", "Holt": "#eb6834", "Holt-Winters": "#1baf7a", "SARIMA": "#eda100"}
TINTA, TINTA_2, REJILLA, SUPERFICIE, NEUTRO = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb", "#8a8985"


def _sha256(ruta: Path) -> str | None:
    return hashlib.sha256(ruta.read_bytes()).hexdigest() if ruta.exists() else None


def _versiones() -> dict:
    v = {"python": platform.python_version()}
    for p in ("pandas", "numpy", "statsmodels", "scipy", "matplotlib"):
        try:
            v[p] = metadata.version(p)
        except metadata.PackageNotFoundError:
            v[p] = None
    return v


def _json(obj, ruta: Path) -> None:
    def conv(o):
        if isinstance(o, (np.floating, np.integer)):
            return o.item()
        if isinstance(o, np.bool_):
            return bool(o)
        raise TypeError(type(o))
    ruta.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=conv) + "\n",
                    encoding="utf-8", newline="\n")


def _csv(df: pd.DataFrame, ruta: Path, index=False) -> None:
    df.to_csv(ruta, index=index, lineterminator="\n", float_format="%.6f", encoding="utf-8")


# ----------------------------------------------------------------------------- figuras
def _estilo(ax):
    ax.set_facecolor(SUPERFICIE)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(REJILLA)
    ax.tick_params(colors=TINTA_2, labelsize=9)
    ax.grid(axis="y", color=REJILLA, linewidth=0.8)
    ax.set_axisbelow(True)


def _fig(nfilas=1, ncols=1, alto=4.2, ancho=9.5):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(nfilas, ncols, figsize=(ancho, alto), facecolor=SUPERFICIE,
                            squeeze=False)
    for ax in axs.flat:
        _estilo(ax)
    return fig, axs


def figura_identificacion(acf_tabla: pd.DataFrame, ruta: Path, titulo: str) -> None:
    fig, axs = _fig(1, 2, alto=3.6)
    for ax, col, nombre in zip(axs[0], ("acf", "pacf"), ("ACF", "PACF")):
        t = acf_tabla[acf_tabla.rezago >= 1]
        ax.vlines(t.rezago, 0, t[col], color=COLOR["SES"], linewidth=2)
        ax.scatter(t.rezago, t[col], s=14, color=COLOR["SES"], zorder=3)
        ax.axhline(0, color=TINTA_2, linewidth=0.8)
        for s in (1, -1):
            ax.axhline(s * t.banda_95.iloc[0], color=NEUTRO, linestyle="--", linewidth=1)
        ax.set_xticks(range(0, int(t.rezago.max()) + 1, 6))
        ax.set_title(nombre, loc="left", fontsize=10, color=TINTA)
        ax.set_xlabel("rezago (meses)", fontsize=9, color=TINTA_2)
    fig.suptitle(titulo, x=0.01, ha="left", fontsize=11, color=TINTA)
    fig.text(0.01, 0.01, "Líneas discontinuas: banda ±1.96/√n. Entrenamiento 2016-01 a 2023-12.",
             fontsize=8, color=TINTA_2)
    fig.tight_layout(rect=(0, 0.04, 1, 0.95))
    fig.savefig(ruta, dpi=150)


def figura_comparacion(pru: pd.Series, pron: dict, ingenuo: np.ndarray, ruta: Path) -> None:
    fig, axs = _fig(alto=4.6)
    ax = axs[0, 0]
    x = pru.index.to_timestamp()
    ax.plot(x, pru.values, color=TINTA, linewidth=2.4, marker="o", markersize=5,
            label="Observado 2024 (dato real)")
    ax.plot(x, ingenuo, color=NEUTRO, linewidth=1.5, linestyle="--",
            label="Ingenuo estacional (referencia)")
    for fam, df in pron.items():
        # Sin etiquetas directas: SES, Holt y Holt-Winters terminan casi en el mismo punto y
        # se encimarían; la leyenda (siempre presente) identifica cada serie.
        ax.plot(x, df.media.values, color=COLOR[fam], linewidth=2, label=f"{fam} (pronóstico)")
    ax.set_ylabel("ocupación (%)", fontsize=9, color=TINTA_2)
    ax.legend(frameon=False, fontsize=8, loc="lower left", ncol=2)
    ax.set_title("Proyección retrospectiva 2024: modelos entrenados con 2016–2023 frente al "
                 "dato observado", loc="left", fontsize=10.5, color=TINTA)
    fig.tight_layout()
    fig.savefig(ruta, dpi=150)


def figura_residuos(res: pd.Series, indice: pd.PeriodIndex, ac: pd.DataFrame, nombre: str,
                    ruta: Path) -> None:
    fig, axs = _fig(1, 3, alto=3.4, ancho=11)
    a, b, c = axs[0]
    x = indice.to_timestamp()
    a.plot(x, res.values, color=COLOR["SARIMA"] if "SARIMA" in nombre else COLOR["SES"],
           linewidth=1.5)
    a.axhline(0, color=TINTA_2, linewidth=0.8)
    a.set_title("Residuos en el tiempo (pp)", loc="left", fontsize=10, color=TINTA)
    t = ac[ac.rezago >= 1]
    b.vlines(t.rezago, 0, t.acf, color=COLOR["SES"], linewidth=2)
    for s in (1, -1):
        b.axhline(s * t.banda_95.iloc[0], color=NEUTRO, linestyle="--", linewidth=1)
    b.axhline(0, color=TINTA_2, linewidth=0.8)
    lim = 1.25 * max(t.banda_95.iloc[0], t.acf.abs().max())
    b.set_ylim(-lim, lim)
    b.set_title("ACF de residuos", loc="left", fontsize=10, color=TINTA)
    b.set_xlabel("rezago (meses)", fontsize=9, color=TINTA_2)
    c.hist(res.values, bins=20, color=COLOR["SES"], edgecolor=SUPERFICIE, linewidth=2)
    c.set_title("Distribución de residuos", loc="left", fontsize=10, color=TINTA)
    fig.suptitle(f"Diagnóstico de residuos de entrenamiento · {nombre}", x=0.01, ha="left",
                 fontsize=11, color=TINTA)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(ruta, dpi=150)


def figura_pronostico(serie: pd.Series, retro: pd.DataFrame, futuro: pd.DataFrame,
                      nombre: str, ruta: Path) -> None:
    fig, axs = _fig(alto=4.8, ancho=10.5)
    ax = axs[0, 0]
    hist = serie[serie.index >= pd.Period("2021-07", "M")]
    xh = hist.index.to_timestamp()
    ax.plot(xh, hist.values, color=TINTA, linewidth=2.2, label="Observado (DataTur)")
    xr, xf = retro.index.to_timestamp(), futuro.index.to_timestamp()
    c = COLOR["SARIMA"] if "SARIMA" in nombre else COLOR["Holt-Winters"]
    ax.fill_between(xr, retro.li, retro.ls, color=c, alpha=0.18, linewidth=0)
    ax.plot(xr, retro.media, color=c, linewidth=2, linestyle="--",
            label="Proyección retrospectiva 2024 (entrenado con 2016–2023), IP 95 %")
    ax.fill_between(xf, futuro.li, futuro.ls, color=c, alpha=0.32, linewidth=0)
    ax.plot(xf, futuro.media, color=c, linewidth=2.4,
            label="Proyección futura 2025 (no observada), IP 95 %")
    ax.axvspan(xf[0] - pd.Timedelta(days=15), xf[-1] + pd.Timedelta(days=15), color=REJILLA,
               alpha=0.35, linewidth=0)
    ax.text(xf[0], 98, "PROYECCIÓN · no son datos observados", fontsize=8, color=TINTA_2,
            va="top")
    ax.set_ylim(0, 100)
    ax.set_ylabel("ocupación (%)", fontsize=9, color=TINTA_2)
    ax.legend(frameon=False, fontsize=8, loc="lower left")
    ax.set_title(f"Ocupación hotelera mensual de Manzanillo (2 a 5 estrellas) · {nombre}",
                 loc="left", fontsize=10.5, color=TINTA)
    fig.tight_layout()
    fig.savefig(ruta, dpi=150)


def figura_descomposicion(comp: pd.DataFrame, ruta: Path) -> None:
    """Observado, tendencia, estacionalidad y residuo (clásica y STL robusta), con COVID sombreado."""
    import matplotlib.dates as mdates

    fig, axs = _fig(4, 1, alto=9.2, ancho=10.5)
    x = comp.index.to_timestamp()
    ini, fin = pd.Timestamp("2020-03-01"), pd.Timestamp("2021-06-30")
    paneles = [("Observado (oro) y tendencia", "tendencia_clasica", "tendencia_stl"),
               ("Estacionalidad", "estacional_clasica", "estacional_stl"),
               ("Residuo", "residuo_clasico", "residuo_stl")]
    ax0 = axs[0, 0]
    ax0.plot(x, comp.observado, color=TINTA, linewidth=1.6, label="Observado")
    for i, (fila, (titulo, c_cla, c_stl)) in enumerate(zip((0, 2, 3), paneles)):
        ax = axs[fila, 0]
        ax.plot(x, comp[c_cla], color=COLOR["SES"], linewidth=2,
                label="Clásica aditiva (media móvil 2×12)")
        ax.plot(x, comp[c_stl], color=COLOR["Holt"], linewidth=2, label="STL robusta")
        if i > 0:
            ax.axhline(0, color=TINTA_2, linewidth=0.8)
        ax.set_title(titulo, loc="left", fontsize=10, color=TINTA)
        ax.set_ylabel("pp", fontsize=9, color=TINTA_2)
    # panel 2: peso robusto de STL (qué meses trató como atípicos)
    axp = axs[1, 0]
    axp.bar(x, comp.peso_robusto_stl, width=20, color=COLOR["Holt"], alpha=0.85)
    axp.set_ylim(0, 1.05)
    axp.set_title("Peso robusto de STL por mes (1 = normal; cerca de 0 = tratado como atípico)",
                  loc="left", fontsize=10, color=TINTA)
    axp.set_ylabel("peso", fontsize=9, color=TINTA_2)
    for ax in axs[:, 0]:
        ax.axvspan(ini, fin, color=REJILLA, alpha=0.6, linewidth=0, zorder=0)
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax0.text(ini + (fin - ini) / 2, 70, "COVID\n2020-03 a 2021-06", ha="center", va="top",
             fontsize=8, color=TINTA_2)
    ax0.set_ylim(0, 72)
    ax0.legend(frameon=False, fontsize=8, loc="lower left", ncol=3)
    fig.suptitle("Descomposición aditiva de la ocupación mensual de Manzanillo (oro, 2016-01 a "
                 "2024-12, periodo 12)", x=0.01, ha="left", fontsize=11, color=TINTA)
    fig.text(0.01, 0.005, "La clásica no tiene tendencia ni residuo en los 6 primeros y 6 últimos "
             "meses. Banda gris: COVID.", fontsize=8, color=TINTA_2)
    fig.tight_layout(rect=(0, 0.02, 1, 0.97))
    fig.savefig(ruta, dpi=150, metadata={"Software": None})


# ----------------------------------------------------------------------------- flujo
def ejecutar(fuente: str = "auto", salida: Path = SALIDA, figuras: bool = True) -> dict:
    # statsmodels 0.15 avisa del cambio futuro de tipo de retorno (tupla → objeto); no afecta.
    warnings.filterwarnings("ignore", category=FutureWarning, message=".*result_object.*")
    salida.mkdir(parents=True, exist_ok=True)
    dir_fig = salida / "figuras"
    dir_fig.mkdir(exist_ok=True)
    inicio = datetime.now(UTC)

    carga = datos.cargar_serie(fuente)
    serie, exog = carga.serie, carga.exogenas
    ent, pru = datos.partir(serie)
    exog_ent, _ = datos.partir(exog)

    # 1. Caracterización y descomposición (solo entrenamiento para lo que decide el modelo)
    carac = {"serie_completa": est.caracterizar(serie), "entrenamiento": est.caracterizar(ent)}
    desc = est.descomponer(ent)

    # 2. Estacionariedad y diferenciación
    t_est = est.pruebas_estacionariedad(ent)
    _csv(t_est, salida / "estacionariedad_adf_kpss.csv")
    d, D, razon_dif = est.elegir_diferenciacion(t_est)

    # 3. ACF/PACF de la serie diferenciada (identificación) y en niveles (tabla)
    ac_dif = est.autocorrelaciones(est.transformar(ent, d, D))
    ac_niv = est.autocorrelaciones(ent)
    _csv(ac_dif, salida / f"acf_pacf_d{d}_D{D}.csv")
    _csv(ac_niv, salida / "acf_pacf_niveles.csv")
    sig = ac_dif[(ac_dif.rezago >= 1) & (ac_dif.acf_significativa | ac_dif.pacf_significativa)]

    # 4. Correlación cruzada exploratoria (entrenamiento, series estacionarizadas, sin fuga)
    ccf = []
    for var in VARIABLES_D7:
        for excl in (False, True):
            t = est.correlacion_cruzada(ent, exog_ent[var], d, D, excluir_covid=excl)
            t.insert(0, "excluye_covid", excl)
            t.insert(0, "variable", var)
            ccf.append(t)
    ccf = pd.concat(ccf, ignore_index=True)
    _csv(ccf, salida / "correlacion_cruzada.csv")

    # 5. Modelos (ajuste solo con entrenamiento)
    ajustes = {"SES": mod.ajustar_ses(ent), "Holt": mod.ajustar_holt(ent),
               "Holt-Winters": mod.ajustar_holt_winters(ent),
               "SARIMA": mod.ajustar_sarima(ent, d, D)}
    pron = {f: mod.pronostico_ajuste(a, pru.index) for f, a in ajustes.items()}
    ingenuo = mod.ingenuo_estacional(ent, len(pru))

    filas, diag = [], {}
    for fam, aj in ajustes.items():
        m = mod.metricas(pru.values, pron[fam].media.values)
        dg = mod.diagnosticar_residuos(aj.residuos(), mod.grados_libertad(aj))
        diag[fam] = dg
        cobertura = float(np.mean((pru.values >= pron[fam].li.values) &
                                  (pru.values <= pron[fam].ls.values)))
        n_par = sum(1 for k in aj.parametros if k not in {"usa_d_covid"})
        filas.append({"familia": fam, "especificacion": aj.especificacion, **m,
                      "AICc_entrenamiento": aj.aicc, "n_parametros": n_par,
                      "cobertura_IP95_2024": cobertura,
                      "ljung_box_p12": dg["ljung_box"][12]["p"],
                      "ljung_box_p24": dg["ljung_box"][24]["p"],
                      "independencia_ok": dg["independencia_ok"],
                      "varianza_estable_ok": dg["varianza_estable_ok"],
                      "normalidad_ok": dg["normalidad_ok"]})
    ref = mod.metricas(pru.values, ingenuo)
    tabla = pd.DataFrame(filas)
    _csv(tabla, salida / "comparacion_modelos_2024.csv")
    candidatos = pd.DataFrame([{"familia": f, "especificacion": e, "AICc": a}
                               for f, aj in ajustes.items() for e, a in aj.candidatos])
    _csv(candidatos, salida / "candidatos_aicc.csv")

    ganador, motivo = mod.seleccionar(tabla)
    aj_g = ajustes[ganador]

    # 6. Pronósticos: retrospectivo (2024) y futuro (2025, reajustado con 2016–2024)
    detalle_pron = []
    for fam, df in pron.items():
        x = df.copy()
        x.insert(0, "observado", pru.values)
        x.insert(0, "familia", fam)
        x.insert(0, "tipo", "proyeccion_retrospectiva")
        detalle_pron.append(x)
    x = pd.DataFrame({"tipo": "referencia_ingenuo_estacional", "familia": "ingenuo",
                      "observado": pru.values, "media": ingenuo}, index=pru.index)
    detalle_pron.append(x)
    detalle_pron = pd.concat(detalle_pron)
    detalle_pron.index.name = "periodo"
    _csv(detalle_pron.reset_index().assign(periodo=lambda t: t.periodo.astype(str)),
         salida / "pronosticos_2024_por_modelo.csv")

    aj_total = mod.reajustar(aj_g, serie)
    idx_fut = pd.period_range(serie.index[-1] + 1, periods=datos.H_PRUEBA, freq="M")
    futuro = mod.pronostico_ajuste(aj_total, idx_fut)
    retro = pron[ganador]
    salida_g = pd.concat([
        retro.assign(tipo="proyeccion_retrospectiva", observado=pru.values,
                     entrenado_con="2016-01..2023-12"),
        futuro.assign(tipo="proyeccion_futura", observado=np.nan,
                      entrenado_con="2016-01..2024-12")])
    salida_g.index.name = "periodo"
    salida_g = salida_g.reset_index().assign(periodo=lambda t: t.periodo.astype(str),
                                             modelo=aj_g.especificacion)
    _csv(salida_g[["periodo", "tipo", "modelo", "entrenado_con", "observado", "media", "li", "ls"]],
         salida / "pronostico_modelo_elegido.csv")

    res_g = aj_g.residuos()
    ac_res = est.autocorrelaciones(res_g, rezagos=24)
    if figuras:
        figura_identificacion(ac_dif, dir_fig / f"identificacion_sarima_d{d}_D{D}.png",
                              f"Identificación SARIMA: ACF y PACF de la serie con d={d}, D={D}")
        figura_comparacion(pru, pron, ingenuo, dir_fig / "comparacion_modelos_2024.png")
        figura_residuos(res_g, ent.index[mod.DESCARTE_INICIAL:], ac_res, aj_g.especificacion,
                        dir_fig / "residuos_modelo_elegido.png")
        figura_pronostico(serie, retro, futuro, aj_g.especificacion,
                          dir_fig / "pronostico_modelo_elegido.png")
    _csv(pd.DataFrame({"periodo": ent.index[mod.DESCARTE_INICIAL:].astype(str),
                       "residuo": res_g.values}), salida / "residuos_modelo_elegido.csv")

    # 7. Descomposición completa del oro (descriptiva, 108 meses): figura y componentes
    comp, desc_completa = est.componentes_descomposicion(serie)
    _csv(comp.reset_index().assign(periodo=lambda t: t.periodo.astype(str)),
         salida / "descomposicion_componentes.csv")
    if figuras:
        figura_descomposicion(comp, dir_fig / "descomposicion_oro.png")

    # 8. Min-max frente a z-score (parámetros solo con entrenamiento; pipeline.transformaciones)
    from . import escalamiento as esc
    knn = esc.comparar_knn(exog.assign(ocupacion_pct=serie))
    control = esc.control_sarima(serie)
    _csv(knn["tabla"], salida / "escalamiento_knn_2024.csv")
    _csv(knn["validacion"], salida / "escalamiento_knn_validacion_2023.csv")
    _csv(knn["pronosticos"].reset_index().assign(periodo=lambda t: t.periodo.astype(str)),
         salida / "escalamiento_knn_pronosticos_2024.csv")
    _csv(control, salida / "escalamiento_control_sarima.csv")
    parametros_escala = {
        escala: {c: {k: v for k, v in vars(p).items()} for c, p in ps.items()}
        for escala, ps in knn["parametros"].items() if ps}
    _json({"ajuste": "solo filas de entrenamiento (2017-01 a 2023-12; 2016 aporta los rezagos)",
           "n_entrenamiento": knn["n_entrenamiento"], "n_prueba": knn["n_prueba"],
           "parametros": parametros_escala,
           "coincidencia_vecinos_2024": knn["coincidencia_vecinos"],
           "meses_2024_fuera_del_rango_minmax": knn["meses_2024_fuera_del_rango_minmax"]},
          salida / "escalamiento_parametros.json")

    resumen = {
        "advertencia": "2024 es una proyección retrospectiva contra datos observados; 2025 es "
                       "una proyección futura sin dato observado. Ninguna predicción es dato.",
        "fuente": carga.fuente, "detalle_fuente": carga.detalle,
        "particion": {"entrenamiento": [str(ent.index[0]), str(ent.index[-1]), len(ent)],
                      "prueba": [str(pru.index[0]), str(pru.index[-1]), len(pru)]},
        "caracterizacion": carac, "descomposicion": desc,
        "descomposicion_completa_oro": desc_completa,
        "comparacion_escalas": {
            "knn_2024": knn["tabla"].to_dict("records"),
            "control_sarima_2024": control.to_dict("records"),
            "coincidencia_vecinos_2024": knn["coincidencia_vecinos"]},
        "diferenciacion": {"d": d, "D": D, "razon": razon_dif},
        "acf_pacf_rezagos_significativos": sig[["rezago", "acf", "pacf"]].to_dict("records"),
        "modelos": {f: {"especificacion": a.especificacion, "AICc": a.aicc, "AIC": a.aic,
                        "BIC": a.bic, "parametros": a.parametros, "residuos": diag[f]}
                    for f, a in ajustes.items()},
        "referencia_ingenuo_estacional": ref,
        "elegido_frente_a_referencia": {
            m: {"elegido": tabla.set_index("familia").loc[ganador, m], "ingenuo": ref[m],
                "elegido_es_mejor": bool(tabla.set_index("familia").loc[ganador, m] < ref[m])}
            for m in ("MAE", "RMSE", "MAPE")},
        "nota_seleccion": "La selección compara solo los cuatro modelos obligatorios. El ingenuo "
                          "estacional es una referencia externa a la selección: ser el mejor de "
                          "los cuatro no implica superar a la referencia en todas las métricas.",
        "criterio_seleccion": mod.CRITERIO_SELECCION,
        "elegido": {"familia": ganador, "especificacion": aj_g.especificacion, "motivo": motivo,
                    "parametros_reajuste_2016_2024": aj_total.parametros},
    }
    _json(resumen, salida / "resumen.json")
    fin = datetime.now(UTC)
    _json({"comando": "python -m laboratorio.pronosticos.ejecutar" +
                      (f" --fuente {fuente}" if fuente != "auto" else ""),
           "inicio_utc": inicio.isoformat(timespec="seconds"),
           "fin_utc": fin.isoformat(timespec="seconds"),
           "duracion_s": round((fin - inicio).total_seconds(), 1),
           "plataforma": platform.platform(), "versiones": _versiones(),
           "fuente": carga.fuente,
           "sha256_bronce_base70": _sha256(datos.RUTA_BRONCE_BASE70),
           "sha256_oro": _sha256(datos.RUTA_ORO),
           "version_contrato": datos.VERSION_CONTRATO},
          salida / "ejecucion.json")
    return resumen


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fuente", choices=["auto", "oro", "referencia"], default="auto")
    ap.add_argument("--sin-figuras", action="store_true")
    a = ap.parse_args(argv)
    r = ejecutar(a.fuente, figuras=not a.sin_figuras)
    e = r["elegido"]
    print(f"Fuente: {r['fuente']} · elegido: {e['especificacion']} · {e['motivo']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
