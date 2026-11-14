"""Gráficas Altair del tablero (sin Streamlit, para poder probarlas). Todas leen DataFrames ya validados por ``cargador``.

Convenciones: paleta apta para daltonismo (Okabe-Ito), etiquetas en español, el intervalo de predicción del 95 % siempre como
franja (``mark_area`` con ``y`` = límite inferior y ``y2`` = límite superior) y el periodo de COVID sombreado cuando aplica.
"""
from __future__ import annotations

import altair as alt
import pandas as pd

from cargador import COVID_FIN, COVID_INICIO, FAMILIA_REFERENCIA

TINTA, AZUL, MORADO, NARANJA, GRIS = "#111827", "#0072B2", "#7c3aed", "#d97706", "#6b7280"
AZUL_CLARO, MORADO_CLARO = "#8ec1e6", "#c4b5fd"  # color de la franja del intervalo (distinto de la línea del pronóstico)
COLORES_MODELOS = {"SES": "#E69F00", "Holt": "#56B4E9", "Holt-Winters": "#009E73", "SARIMA": AZUL, FAMILIA_REFERENCIA: GRIS}
ETIQUETAS_CORTAS = {"SES": "SES", "Holt": "Holt", "Holt-Winters": "Holt-Winters", "SARIMA": "SARIMA", FAMILIA_REFERENCIA: "Ingenuo estacional"}
_ABR = "['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']"
ALTURA = 430  # incluye el eje y la leyenda (en Streamlit el gráfico se ajusta a este alto total)


def _eje_mes() -> alt.Axis:
    """Eje de meses en español: «ene 2025» en enero y solo la abreviatura en los demás meses."""
    return alt.Axis(title=None, tickCount="month", labelAngle=0, labelOverlap=True,
                    labelExpr=f"month(datum.value) == 0 ? {_ABR}[0] + ' ' + year(datum.value) : {_ABR}[month(datum.value)]")


def _eje_anio() -> alt.Axis:
    return alt.Axis(title=None, format="%Y", tickCount="year", labelAngle=0)


def _eje_y(titulo="Ocupación (%)", dominio=(0, 75)) -> alt.Y:
    return alt.Y("valor:Q", title=titulo, scale=alt.Scale(domain=list(dominio), nice=False))


def _estilo(grafica: alt.TopLevelMixin, columnas: int = 1) -> alt.TopLevelMixin:
    """Estilo común: leyenda abajo y sin recortes, símbolos opacos (no heredan la transparencia de las franjas)."""
    return (grafica.configure_axis(labelFontSize=12, titleFontSize=12, gridColor="#e5e7eb")
            .configure_legend(orient="bottom", labelFontSize=12, symbolSize=140, title=None, columns=columnas, labelLimit=420, symbolOpacity=1)
            .configure_view(stroke=None))


def _escala(dominio, colores) -> alt.Scale:
    return alt.Scale(domain=list(dominio), range=list(colores))


def _bandas(fechas: list, etiqueta: str, color: str, y_texto: float) -> alt.LayerChart:
    d = pd.DataFrame({"inicio": [fechas[0]], "fin": [fechas[1]], "etiqueta": [etiqueta], "y": [y_texto]})
    rect = alt.Chart(d).mark_rect(color=color, opacity=0.14).encode(x="inicio:T", x2="fin:T")
    texto = alt.Chart(d).mark_text(color=TINTA, fontSize=11, dy=0, baseline="top", opacity=0.85).encode(
        x=alt.X("inicio:T"), y=alt.Y("y:Q"), text="etiqueta:N")
    return rect + texto


# ---------------------------------------------------------------- 1. serie histórica
def bandas_visibles(oro: pd.DataFrame) -> list:
    """Bandas (COVID y año de prueba) recortadas al rango de fechas de ``oro``; se omiten las que no se cruzan con él.

    Sin el recorte, Altair extendería el eje hasta 2024 aunque la serie filtrada termine en 2019.
    """
    desde, hasta = oro["fecha"].min(), oro["fecha"].max() + pd.offsets.MonthEnd(0)
    candidatas = [("COVID", pd.Timestamp(COVID_INICIO + "-01"), pd.Timestamp(COVID_FIN + "-01") + pd.offsets.MonthEnd(0), NARANJA),
                  ("Año de prueba", pd.Timestamp("2024-01-01"), pd.Timestamp("2024-12-31"), GRIS)]
    return [(etq, max(ini, desde), min(fin, hasta), color) for etq, ini, fin, color in candidatas if ini <= hasta and fin >= desde]


def grafica_historica(oro: pd.DataFrame) -> alt.LayerChart:
    """Ocupación mensual (toda la serie o el periodo filtrado), con el periodo de COVID y el año de prueba sombreados si son visibles."""
    d = oro.rename(columns={"ocupacion_pct": "valor"})
    corta = len(d) <= 24  # en periodos cortos el eje muestra meses; en largos, años
    base = alt.Chart(d).encode(x=alt.X("fecha:T", axis=_eje_mes() if corta else _eje_anio()), y=_eje_y(),
                               tooltip=[alt.Tooltip("mes_texto:N", title="Mes"), alt.Tooltip("valor:Q", title="Ocupación (%)", format=".1f")])
    capas = [_bandas([ini, fin], etq, color, 73) for etq, ini, fin, color in bandas_visibles(oro)]
    capas.append(base.mark_line(color=AZUL, strokeWidth=2) + base.mark_point(color=AZUL, filled=True, size=26))
    return _estilo(alt.layer(*capas).properties(height=ALTURA))


# ---------------------------------------------------------------- 2. SARIMA 2024 frente a lo observado
def grafica_retrospectiva(retro: pd.DataFrame) -> alt.LayerChart:
    """Pronóstico del SARIMA para 2024 (entrenado hasta 2023-12), su intervalo del 95 % y el valor observado."""
    nombres = ["Observado", "Pronóstico SARIMA", "Intervalo de predicción del 95 %"]
    escala = _escala(nombres, [TINTA, AZUL, AZUL_CLARO])
    color = alt.Color("serie:N", scale=escala, legend=alt.Legend(title=None))
    x = alt.X("fecha:T", axis=_eje_mes())
    tip = [alt.Tooltip("mes_texto:N", title="Mes"), alt.Tooltip("observado:Q", title="Observado (%)", format=".1f"),
           alt.Tooltip("media:Q", title="Pronóstico (%)", format=".1f"), alt.Tooltip("li:Q", title="Límite inferior 95 % (%)", format=".1f"),
           alt.Tooltip("ls:Q", title="Límite superior 95 % (%)", format=".1f")]
    d = retro.assign(valor_obs=retro["observado"])
    banda = alt.Chart(d.assign(serie=nombres[2])).mark_area(opacity=0.55).encode(
        x=x, y=alt.Y("li:Q", title="Ocupación (%)", scale=alt.Scale(domain=[0, 100], nice=False)), y2="ls:Q", color=color, tooltip=tip)
    pron = alt.Chart(d.assign(serie=nombres[1])).mark_line(strokeWidth=2.5, strokeDash=[6, 3]).encode(x=x, y=alt.Y("media:Q"), color=color, tooltip=tip)
    obs_l = alt.Chart(d.assign(serie=nombres[0])).mark_line(strokeWidth=2.5).encode(x=x, y=alt.Y("observado:Q"), color=color, tooltip=tip)
    obs_p = alt.Chart(d.assign(serie=nombres[0])).mark_point(filled=True, size=50).encode(x=x, y=alt.Y("observado:Q"), color=color, tooltip=tip)
    return _estilo((banda + pron + obs_l + obs_p).properties(height=ALTURA))


# ---------------------------------------------------------------- 3. comparación de modelos
def barras_metrica(comparacion: pd.DataFrame, metrica: str, titulo: str) -> alt.LayerChart:
    d = comparacion.copy()
    d["etiqueta"] = d["familia"].map(ETIQUETAS_CORTAS)
    d["categoria"] = d.apply(lambda f: "Modelo elegido" if f["es_elegido"] else ("Referencia" if f["es_referencia"] else "Otros modelos"), axis=1)
    d["valor"] = d[metrica]
    escala = _escala(["Modelo elegido", "Referencia", "Otros modelos"], [AZUL, GRIS, "#9ca3af"])
    base = alt.Chart(d).encode(y=alt.Y("etiqueta:N", sort="x", title=None, axis=alt.Axis(labelLimit=200)),
                               x=alt.X("valor:Q", title=titulo, scale=alt.Scale(domain=[0, float(d["valor"].max()) * 1.25])),
                               tooltip=[alt.Tooltip("modelo:N", title="Modelo"), alt.Tooltip("valor:Q", title=titulo, format=".2f")])
    barras = base.mark_bar().encode(color=alt.Color("categoria:N", scale=escala, legend=None))  # sin leyenda: se explica con una nota
    etiquetas = base.mark_text(align="left", dx=4, color=TINTA, fontSize=12).encode(text=alt.Text("valor:Q", format=".2f"))
    return _estilo((barras + etiquetas).properties(height=240))


def grafica_modelos_2024(por_modelo: pd.DataFrame, observado: pd.DataFrame, familias: list) -> alt.LayerChart:
    """Proyección retrospectiva de 2024 de los modelos elegidos por el usuario frente a lo observado (sin intervalos, para legibilidad)."""
    sel = por_modelo[por_modelo["familia"].isin(familias)].assign(serie=lambda t: t["familia"].map(ETIQUETAS_CORTAS))
    obs = observado.assign(serie="Observado")
    dominio = ["Observado"] + [ETIQUETAS_CORTAS[f] for f in COLORES_MODELOS if f in familias]
    colores = [TINTA] + [COLORES_MODELOS[f] for f in COLORES_MODELOS if f in familias]
    color = alt.Color("serie:N", scale=_escala(dominio, colores), legend=alt.Legend(title=None))
    x = alt.X("fecha:T", axis=_eje_mes())
    tip = [alt.Tooltip("mes_texto:N", title="Mes"), alt.Tooltip("serie:N", title="Serie"), alt.Tooltip("valor:Q", title="Ocupación (%)", format=".1f")]
    modelos = alt.Chart(sel.assign(valor=sel["media"])).mark_line(strokeWidth=2, point=alt.OverlayMarkDef(size=30)).encode(
        x=x, y=alt.Y("valor:Q", title="Ocupación (%)", scale=alt.Scale(domain=[20, 80], nice=False)), color=color, tooltip=tip)
    reales = alt.Chart(obs.assign(valor=obs["observado"])).mark_line(strokeWidth=3.5, point=alt.OverlayMarkDef(size=45, filled=True)).encode(
        x=x, y=alt.Y("valor:Q"), color=color, tooltip=tip)
    return _estilo((modelos + reales).properties(height=ALTURA), columnas=2)


# ---------------------------------------------------------------- 4. proyección 2025 (histórica)
def grafica_intervalos_comparados(df: pd.DataFrame, con_observado: bool) -> alt.LayerChart:
    """Franja gaussiana (supone residuos normales) frente a las líneas del bootstrap de bloques (no lo supone); mismo pronóstico central."""
    x = alt.X("fecha:T", axis=_eje_mes())
    y = alt.Y("li_gauss:Q", title="Ocupación (%)", scale=alt.Scale(domain=[0, 100], nice=False))
    gauss = alt.Chart(df.assign(serie="Intervalo gaussiano (supone residuos normales)")).mark_area(opacity=0.3, color=AZUL).encode(
        x=x, y=y, y2="ls_gauss:Q", tooltip=[alt.Tooltip("mes_texto:N", title="Mes"), alt.Tooltip("li_gauss:Q", title="Gauss inf.", format=".1f"),
                                            alt.Tooltip("ls_gauss:Q", title="Gauss sup.", format=".1f")])
    largo = pd.concat([df[["fecha", "mes_texto", c]].rename(columns={c: "valor"}).assign(serie="Intervalo bootstrap de bloques (sin normalidad)", lado=c)
                       for c in ("li_bootstrap", "ls_bootstrap")])
    boot = alt.Chart(largo).mark_line(strokeWidth=2.2, strokeDash=[5, 3], color=MORADO).encode(
        x=x, y=alt.Y("valor:Q"), detail="lado:N", tooltip=[alt.Tooltip("mes_texto:N", title="Mes"), alt.Tooltip("valor:Q", title="Límite bootstrap", format=".1f")])
    centro = alt.Chart(df).mark_line(strokeWidth=2, color=AZUL).encode(x=x, y=alt.Y("media_gauss:Q"))
    capas = [gauss, boot, centro]
    if con_observado:
        capas.append(alt.Chart(df).mark_line(strokeWidth=2.5, color=TINTA, point=alt.OverlayMarkDef(size=30, filled=True)).encode(x=x, y=alt.Y("observado:Q")))
    return _estilo(alt.layer(*capas).properties(height=ALTURA))


def grafica_proyeccion(oro: pd.DataFrame, proyeccion: pd.DataFrame) -> alt.LayerChart:
    """Últimos 24 meses observados y la proyección de 2025 con su intervalo del 95 % (calculada con datos hasta 2024-12)."""
    nombres = ["Observado (hasta dic 2024)", "Proyección 2025", "Intervalo de predicción del 95 %"]
    color = alt.Color("serie:N", scale=_escala(nombres, [TINTA, MORADO, MORADO_CLARO]), legend=alt.Legend(title=None))
    x = alt.X("fecha:T", axis=_eje_mes())
    ult = oro[oro["fecha"] >= pd.Timestamp("2023-01-01")].assign(serie=nombres[0])
    tip_obs = [alt.Tooltip("mes_texto:N", title="Mes"), alt.Tooltip("ocupacion_pct:Q", title="Observado (%)", format=".1f")]
    tip = [alt.Tooltip("mes_texto:N", title="Mes"), alt.Tooltip("media:Q", title="Proyección (%)", format=".1f"),
           alt.Tooltip("li:Q", title="Límite inferior 95 % (%)", format=".1f"), alt.Tooltip("ls:Q", title="Límite superior 95 % (%)", format=".1f")]
    eje = alt.Y("li:Q", title="Ocupación (%)", scale=alt.Scale(domain=[0, 100], nice=False))
    banda = alt.Chart(proyeccion.assign(serie=nombres[2])).mark_area(opacity=0.55).encode(x=x, y=eje, y2="ls:Q", color=color, tooltip=tip)
    linea = alt.Chart(proyeccion.assign(serie=nombres[1])).mark_line(strokeWidth=2.5, strokeDash=[6, 3]).encode(x=x, y=alt.Y("media:Q"), color=color, tooltip=tip)
    obs = alt.Chart(ult).mark_line(strokeWidth=2.5, point=alt.OverlayMarkDef(size=30, filled=True)).encode(
        x=x, y=alt.Y("ocupacion_pct:Q"), color=color, tooltip=tip_obs)
    corte = pd.DataFrame({"fecha": [pd.Timestamp("2025-01-01")], "etiqueta": ["Fin de los datos observados (dic 2024)"], "y": [97]})
    regla = alt.Chart(corte).mark_rule(color=GRIS, strokeDash=[2, 3]).encode(x="fecha:T")
    texto = alt.Chart(corte).mark_text(align="right", dx=-6, color=GRIS, fontSize=11, baseline="top").encode(x="fecha:T", y=alt.Y("y:Q"), text="etiqueta:N")
    return _estilo((banda + linea + obs + regla + texto).properties(height=ALTURA))
