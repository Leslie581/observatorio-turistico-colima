"""Tablero de E1 · Observatorio de Ocupación Hotelera de Colima (Manzanillo). NOMBRE PROVISIONAL.

    streamlit run tablero/streamlit_app.py

Solo LEE archivos versionados del repositorio (capa oro y resultados del laboratorio de pronósticos): no reentrena modelos, no ejecuta el
pipeline, no usa red ni secretos y no muestra datos de DENUE. Ver docs/E1/tablero.md.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # los módulos hermanos se importan sin depender del directorio de trabajo

import streamlit as st  # noqa: E402

import cargador as cg  # noqa: E402
import graficas as gr  # noqa: E402

TITULO = "Observatorio de Ocupación Hotelera de Colima · Manzanillo"

st.set_page_config(page_title=TITULO, layout="wide", initial_sidebar_state="collapsed")
st.markdown(
    """
<style>
  [data-testid="stMainBlockContainer"] { max-width: 1180px; }
  @media (max-width: 640px) {
    [data-testid="stMainBlockContainer"] { padding-left: .9rem; padding-right: .9rem; padding-top: 1.2rem; }
    h1 { font-size: 1.45rem !important; line-height: 1.25 !important; }
    h2, h3 { font-size: 1.15rem !important; }
  }
  div[data-testid="stMetricValue"] { font-size: 1.6rem; }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner="Cargando datos…")
def _cargar() -> cg.Datos:
    return cg.cargar_todo()


try:
    d = _cargar()
except cg.ErrorDatos as error:
    st.title(TITULO)
    st.error(f"No se pueden mostrar los resultados: {error}")
    st.stop()

oro, comp, por_modelo, elegido = d.oro, d.comparacion, d.por_modelo, d.elegido
retro = elegido[elegido["tipo"] == cg.TIPO_RETRO]
proy = elegido[elegido["tipo"] == cg.TIPO_PROYECCION]
textos = cg.textos_cliente(d)
generacion = cg.fecha_generacion(d.ejecucion)
fechas = cg.fechas_clave(d)
meses_dentro, meses_eval = cg.cobertura_ip95(retro)
sar = comp.set_index("familia").loc["SARIMA"]

st.title(TITULO)
st.caption("Nombre provisional · Ocupación mensual de hoteles de 2 a 5 estrellas · Datos de DataTur (Secretaría de Turismo) hasta diciembre de 2024")
st.info(
    f"Los datos observados llegan hasta **{fechas['ultimo_observado']}**. "
    "La proyección de 2025 es una **proyección histórica** calculada con la información disponible hasta diciembre de 2024; "
    "**no es un pronóstico vigente**."
)
with st.container(border=True):
    st.markdown("#### Resumen ejecutivo")
    st.markdown(textos["ejecutivo"])
    f1, f2, f3 = st.columns(3)
    f1.markdown(f"**Último mes con datos observados**  \n{fechas['ultimo_observado']}")
    f2.markdown(f"**Resultados estadísticos generados**  \n{fechas['resultados']}")
    if "capa_oro" in fechas:
        f3.markdown(f"**Capa oro generada**  \n{fechas['capa_oro']}")
    st.caption("Fechas tomadas de los archivos versionados. El tablero no muestra una fecha de actualización propia porque no puede verificarla "
               "desde sus archivos.")

tab_resumen, tab_2024, tab_modelos, tab_2025, tab_leer, tab_fuentes = st.tabs(
    ["Resumen", "Pronóstico 2024", "Comparación de modelos", "Proyección 2025", "Cómo leerlo", "Fuentes y datos"])

# ------------------------------------------------------------------ Resumen
with tab_resumen:
    st.subheader("Ocupación hotelera mensual de Manzanillo, 2016–2024")
    y = oro["ocupacion_pct"]
    minimo = oro.loc[y.idxmin()]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ocupación media 2016–2024", f"{y.mean():.1f} %", help="Promedio de los 108 meses, incluidos los de COVID.")
    c2.metric("Ocupación media 2024", f"{oro[oro['periodo'] >= '2024-01']['ocupacion_pct'].mean():.1f} %")
    c3.metric(f"Mes más bajo ({minimo['mes_texto']})", f"{minimo['ocupacion_pct']:.1f} %", help="El valor mensual más bajo de toda la serie.")
    c4.metric("Meses de 2024 dentro del intervalo", f"{meses_dentro} de {meses_eval}",
              help="Meses en que el valor real cayó dentro del intervalo de predicción del 95 % del SARIMA.")
    clave = st.radio("Periodo que se muestra en la gráfica", options=list(cg.PERIODOS_HISTORICOS),
                     format_func=lambda k: cg.PERIODOS_HISTORICOS[k][0], horizontal=True, key="periodo_historico",
                     help="Solo cambia lo que se dibuja. No modifica el entrenamiento, los parámetros ni los resultados de los modelos.")
    vista = cg.filtrar_periodo(oro, clave)
    rp = cg.resumen_periodo(vista)
    p1, p2, p3 = st.columns(3)
    p1.metric("Media del periodo seleccionado", f"{rp['media']:.1f} %", help=f"{rp['n']} meses, de {rp['desde']} a {rp['hasta']}.")
    p2.metric(f"Mínimo del periodo ({rp['mes_min']})", f"{rp['min']:.1f} %")
    p3.metric(f"Máximo del periodo ({rp['mes_max']})", f"{rp['max']:.1f} %")
    st.altair_chart(gr.grafica_historica(vista), width="stretch")
    st.caption("Franja naranja: periodo de COVID (marzo de 2020 a junio de 2021). Franja gris: 2024, el año que se usó para probar los modelos. "
               "Enero y febrero de 2020 solo aparecen en «Toda la serie».")
    st.markdown(
        "**Qué se ve.** La ocupación sigue un patrón anual, con julio y diciembre como meses altos y septiembre como el más bajo, "
        "y una caída excepcional en 2020.")
    st.markdown(textos["historia"])
    with st.expander("Ver los datos del periodo en tabla"):
        st.dataframe(vista[["mes_texto", "ocupacion_pct", "conjunto"]].rename(columns={"mes_texto": "Mes", "ocupacion_pct": "Ocupación (%)", "conjunto": "Uso en el análisis"}),
                     hide_index=True, column_config={"Ocupación (%)": st.column_config.NumberColumn(format="%.1f")})

# ------------------------------------------------------------------ Pronóstico 2024
with tab_2024:
    st.subheader("Pronóstico SARIMA para 2024 frente a lo que ocurrió")
    st.markdown(textos["resultado_2024"])
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("MAE del SARIMA", f"{sar['MAE']:.2f} pp", help="Error absoluto medio en 2024, en puntos porcentuales de ocupación.")
    m2.metric("RMSE del SARIMA", f"{sar['RMSE']:.2f} pp", help="Raíz del error cuadrático medio: castiga más los errores grandes.")
    m3.metric("MAPE del SARIMA", f"{sar['MAPE']:.2f} %", help="Error medio como porcentaje del valor observado.")
    m4.metric("Meses dentro del intervalo del 95 %", f"{meses_dentro} de {meses_eval}")
    st.altair_chart(gr.grafica_retrospectiva(retro), width="stretch")
    st.caption("Línea negra: ocupación observada. Línea azul discontinua: pronóstico del SARIMA, entrenado solo con datos hasta diciembre de 2023. "
               "Franja azul: intervalo de predicción del 95 %.")
    st.markdown(
        "**Limitaciones de esta evaluación.** Es un solo año de prueba (12 meses), así que las métricas tienen mucha incertidumbre propia. "
        "Que los 12 meses cayeran dentro del intervalo indica que la franja es **conservadora** (amplia, por la variación que dejó el COVID en el "
        "entrenamiento), no que el modelo acierte con precisión. Los errores son de un pronóstico hecho de una vez para todo 2024, desde diciembre de 2023.")
    tabla = retro[["mes_texto", "observado", "media", "li", "ls"]].copy()
    tabla["dentro"] = ((tabla["observado"] >= tabla["li"]) & (tabla["observado"] <= tabla["ls"])).map({True: "Sí", False: "No"})
    with st.expander("Ver los valores mes por mes"):
        st.dataframe(tabla.rename(columns={"mes_texto": "Mes", "observado": "Observado (%)", "media": "Pronóstico (%)", "li": "Límite inferior 95 % (%)",
                                           "ls": "Límite superior 95 % (%)", "dentro": "¿Observado dentro del intervalo?"}),
                     hide_index=True, column_config={c: st.column_config.NumberColumn(format="%.1f") for c in
                                                     ["Observado (%)", "Pronóstico (%)", "Límite inferior 95 % (%)", "Límite superior 95 % (%)"]})

# ------------------------------------------------------------------ Comparación de modelos
with tab_modelos:
    st.subheader("Comparación de modelos en 2024")
    st.markdown(
        "Se compararon cuatro modelos estadísticos (SES, Holt, Holt-Winters y SARIMA) y una **referencia ingenua estacional**, "
        "que simplemente repite el valor del mismo mes del año anterior. Todos se entrenaron con datos de 2016 a 2023 y se evaluaron en 2024. "
        "**Menor error es mejor.**")
    st.info(textos["destacado"])
    col_a, col_b, col_c = st.columns(3)
    col_a.altair_chart(gr.barras_metrica(comp, "MAE", "MAE (puntos porcentuales)"), width="stretch")
    col_b.altair_chart(gr.barras_metrica(comp, "RMSE", "RMSE (puntos porcentuales)"), width="stretch")
    col_c.altair_chart(gr.barras_metrica(comp, "MAPE", "MAPE (%)"), width="stretch")
    st.caption("Azul: modelo elegido (SARIMA). Gris oscuro: referencia ingenua estacional. Gris claro: los otros modelos.")
    st.markdown(textos["comparacion"])
    tabla = comp[["modelo", "MAE", "RMSE", "MAPE", "sesgo_medio"]].rename(columns={
        "modelo": "Modelo", "MAE": "MAE (pp)", "RMSE": "RMSE (pp)", "MAPE": "MAPE (%)", "sesgo_medio": "Sesgo medio (pp)"})
    st.dataframe(tabla, hide_index=True, column_config={c: st.column_config.NumberColumn(format="%.2f") for c in tabla.columns if c != "Modelo"})
    st.markdown("**Proyección de 2024 por modelo.** Elija qué modelos comparar con lo observado.")
    nombres = {f: cg.NOMBRES[f] for f in (*cg.FAMILIAS, cg.FAMILIA_REFERENCIA)}
    elegidos = st.multiselect("Modelos", options=list(nombres), default=["SARIMA", cg.FAMILIA_REFERENCIA], format_func=lambda f: nombres[f])
    if elegidos:
        observado = retro[["fecha", "mes_texto", "observado"]]
        st.altair_chart(gr.grafica_modelos_2024(por_modelo, observado, elegidos), width="stretch")
    else:
        st.info("Seleccione al menos un modelo para ver su proyección.")
    with st.expander("Qué significan MAE, RMSE y MAPE"):
        st.markdown(
            "- **MAE**: el error promedio, en puntos porcentuales de ocupación.\n"
            "- **RMSE**: parecido al MAE, pero castiga más los errores grandes.\n"
            "- **MAPE**: el error promedio como porcentaje del valor real.")

# ------------------------------------------------------------------ Proyección 2025
with tab_2025:
    st.subheader("Proyección histórica para 2025")
    st.warning(
        "**Esto es una proyección histórica, no un pronóstico vigente.** Se calculó con la información disponible hasta diciembre de 2024. "
        "La fuente de datos no incluye valores observados de 2025, por lo que esta proyección no se pudo comparar con la realidad.", icon=None)
    st.altair_chart(gr.grafica_proyeccion(oro, proy), width="stretch")
    st.caption("Línea negra: ocupación observada en 2023 y 2024. Línea morada discontinua: proyección del SARIMA para 2025. Franja morada: intervalo de predicción del 95 %.")
    st.markdown(textos["proyeccion_2025"])
    st.dataframe(
        proy[["mes_texto", "media", "li", "ls"]].rename(columns={"mes_texto": "Mes", "media": "Proyección (%)", "li": "Límite inferior 95 % (%)", "ls": "Límite superior 95 % (%)"}),
        hide_index=True, column_config={c: st.column_config.NumberColumn(format="%.1f") for c in ["Proyección (%)", "Límite inferior 95 % (%)", "Límite superior 95 % (%)"]})

# ------------------------------------------------------------------ Cómo leerlo
with tab_leer:
    st.subheader("Cómo leer este tablero")
    st.markdown(textos["historia"])
    st.markdown(textos["intervalo"])
    st.markdown(textos["resultado_2024"])
    st.markdown(textos["comparacion"])
    st.markdown(textos["proyeccion_2025"])
    st.markdown("**Limitaciones**")
    st.markdown("\n".join(f"- {t}" for t in cg.LIMITACIONES))

# ------------------------------------------------------------------ Fuentes y datos
with tab_fuentes:
    st.subheader("Fuentes de datos y cobertura")
    meta, ej = d.meta_oro, d.ejecucion
    st.markdown(
        "| Elemento | Detalle |\n|---|---|\n"
        "| **Fuente de los datos** | DataTur, Secretaría de Turismo (SECTUR): *Ocupación hotelera en los 70 destinos principales monitoreados* |\n"
        "| **Licencia** | Creative Commons Atribución 4.0 (CC BY 4.0) |\n"
        f"| **Cobertura temporal** | {meta['periodo_min']} a {meta['periodo_max']} ({meta['filas']} meses) |\n"
        "| **Cobertura geográfica y de categorías** | Manzanillo; hoteles de 2 a 5 estrellas en conjunto |\n"
        "| **Variable** | Ocupación (%): cuartos ocupados entre cuartos disponibles, calculada con sumas del conjunto (no un promedio de porcentajes) |\n"
        f"| **Resultados generados** | {generacion} |\n"
        f"| **Modelo elegido** | {d.resumen['elegido']['especificacion']}, seleccionado por menor RMSE en 2024 entre los modelos cuyos residuos no muestran autocorrelación |\n"
        f"| **Entrenamiento y prueba** | Entrenamiento 2016-01 a 2023-12 (96 meses); prueba 2024-01 a 2024-12 (12 meses); la proyección de 2025 usa 2016-01 a 2024-12 |\n"
        f"| **Versión del contrato de datos** | {meta['version_contrato']} |\n"
        f"| **Software de los resultados** | Python {ej['versiones']['python']}, statsmodels {ej['versiones']['statsmodels']} |")
    st.markdown("**Atribución.** " + meta["atribucion"].split(", licencia")[0] + ". Los datos se redistribuyen con la misma licencia (CC BY 4.0), "
                "agregados por mes y sin información de establecimientos individuales.")
    with st.expander("Qué archivos lee este tablero"):
        st.markdown(
            "- `data/oro/manzanillo_ocupacion_mensual.csv` y su ficha `.meta.json` (capa oro)\n"
            "- `laboratorio/pronosticos/resultados/`: `comparacion_modelos_2024.csv`, `pronosticos_2024_por_modelo.csv`, "
            "`pronostico_modelo_elegido.csv`, `resumen.json` y `ejecucion.json`\n\n"
            "El tablero **no** reentrena modelos, no ejecuta el procesamiento de datos, no consulta servicios externos y no muestra datos de establecimientos.")

st.divider()
st.caption("Observatorio de Ocupación Hotelera de Colima (nombre provisional) · Proyecto Integrador Trusted Data Lab · Entrega E1 · Los modelos son estadísticos y las proyecciones no son datos observados.")
