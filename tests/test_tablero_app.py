"""Gráficas y arranque del tablero (tablero/graficas.py y tablero/streamlit_app.py).

Requieren altair y streamlit (tablero/requirements.txt). Con ``TDL_EXIGIR_TABLERO=1`` (lo fija ci.yml) su ausencia es un ERROR, no una
omisión silenciosa. Sin esa variable (captura diaria, entornos locales sin las dependencias del tablero) estas pruebas se OMITEN y
``-rs`` lista el motivo; se ejecutan con ``pip install -r tablero/requirements.txt``.
"""
import os
import sys
from pathlib import Path

import pandas as pd
import pytest

try:
    import altair as alt  # noqa: F401
    import streamlit  # noqa: F401
except ImportError as error:
    if os.environ.get("TDL_EXIGIR_TABLERO") == "1":
        raise ImportError(f"falta una dependencia del tablero ({error.name}) y TDL_EXIGIR_TABLERO=1 exige ejecutar sus pruebas") from error
    pytest.skip("sin altair o streamlit (tablero/requirements.txt)", allow_module_level=True)

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "tablero"))
import cargador as cg  # noqa: E402
import graficas as gr  # noqa: E402

APP = RAIZ / "tablero" / "streamlit_app.py"


@pytest.fixture(scope="module")
def d():
    return cg.cargar_todo()


def _capas(grafica):
    """(especificación completa, lista APLANADA de capas con mark, encoding y datos resueltos; hereda los datos del nivel superior)."""
    spec = grafica.to_dict()
    capas = []

    def recorrer(nodo, datos_heredados):
        datos = nodo.get("data", datos_heredados)
        if "layer" in nodo:
            for sub in nodo["layer"]:
                recorrer(sub, datos)
            return
        tabla = pd.DataFrame(spec["datasets"][datos["name"]]) if datos and "name" in datos else pd.DataFrame()
        marca = nodo["mark"]["type"] if isinstance(nodo["mark"], dict) else nodo["mark"]
        capas.append({"mark": marca, "enc": nodo["encoding"], "datos": tabla})

    recorrer(spec, spec.get("data"))
    return spec, capas


def test_el_intervalo_del_95_se_dibuja_como_franja_con_limites_inferior_y_superior(d):
    retro = d.elegido[d.elegido["tipo"] == cg.TIPO_RETRO]
    spec, capas = _capas(gr.grafica_retrospectiva(retro))
    banda = [c for c in capas if c["mark"] == "area"]
    assert len(banda) == 1 and banda[0]["enc"]["y"]["field"] == "li" and banda[0]["enc"]["y2"]["field"] == "ls"
    assert len(banda[0]["datos"]) == 12 and (banda[0]["datos"]["li"] <= banda[0]["datos"]["ls"]).all()
    assert {"line", "point"} <= {c["mark"] for c in capas}
    dominio = capas[0]["enc"]["color"]["scale"]["domain"]
    assert dominio == ["Observado", "Pronóstico SARIMA", "Intervalo de predicción del 95 %"]  # leyenda en español
    obs = [c for c in capas if c["mark"] == "line" and c["enc"]["y"]["field"] == "observado"][0]["datos"]
    assert obs["observado"].round(4).tolist() == retro["observado"].round(4).tolist()  # lo que se dibuja es lo que está en el laboratorio


def test_la_proyeccion_2025_dibuja_intervalo_corte_de_datos_y_solo_24_meses_observados(d):
    proy = d.elegido[d.elegido["tipo"] == cg.TIPO_PROYECCION]
    spec, capas = _capas(gr.grafica_proyeccion(d.oro, proy))
    banda = [c for c in capas if c["mark"] == "area"][0]
    assert banda["enc"]["y"]["field"] == "li" and banda["enc"]["y2"]["field"] == "ls" and len(banda["datos"]) == 12
    assert set(pd.to_datetime(banda["datos"]["fecha"]).dt.year) == {2025}
    reglas = [c for c in capas if c["mark"] == "rule"]
    assert len(reglas) == 1 and pd.to_datetime(reglas[0]["datos"]["fecha"]).dt.strftime("%Y-%m-%d").tolist() == ["2025-01-01"]
    obs = [c for c in capas if c["mark"] == "line" and c["enc"]["y"]["field"] == "ocupacion_pct"][0]["datos"]
    assert len(obs) == 24 and pd.to_datetime(obs["fecha"]).min() == pd.Timestamp("2023-01-01") and pd.to_datetime(obs["fecha"]).max() == pd.Timestamp("2024-12-01")
    assert "Proyección 2025" in capas[0]["enc"]["color"]["scale"]["domain"]


def test_la_serie_historica_tiene_108_puntos_y_sombrea_covid_y_el_ano_de_prueba(d):
    spec, capas = _capas(gr.grafica_historica(d.oro))
    lineas = [c for c in capas if c["mark"] == "line"][0]
    assert len(lineas["datos"]) == 108
    rect = [c for c in capas if c["mark"] == "rect"]
    inicios = sorted(pd.to_datetime(r["datos"]["inicio"]).dt.strftime("%Y-%m").iloc[0] for r in rect)
    assert inicios == ["2020-03", "2024-01"]


def test_las_barras_comparan_los_cinco_modelos_y_resaltan_el_elegido(d):
    for metrica in ("MAE", "RMSE", "MAPE"):
        spec, capas = _capas(gr.barras_metrica(d.comparacion, metrica, metrica))
        barras = [c for c in capas if c["mark"] == "bar"][0]["datos"]
        assert sorted(barras["etiqueta"]) == sorted(["SES", "Holt", "Holt-Winters", "SARIMA", "Ingenuo estacional"])
        assert barras.set_index("etiqueta").loc["SARIMA", "categoria"] == "Modelo elegido"
        assert barras.set_index("etiqueta").loc["Ingenuo estacional", "categoria"] == "Referencia"
        assert barras.set_index("etiqueta").loc["SARIMA", "valor"] == pytest.approx(d.comparacion.set_index("familia").loc["SARIMA", metrica])


def test_la_grafica_de_modelos_respeta_la_seleccion(d):
    retro = d.elegido[d.elegido["tipo"] == cg.TIPO_RETRO][["fecha", "mes_texto", "observado"]]
    spec, capas = _capas(gr.grafica_modelos_2024(d.por_modelo, retro, ["SARIMA", cg.FAMILIA_REFERENCIA]))
    assert capas[0]["enc"]["color"]["scale"]["domain"] == ["Observado", "SARIMA", "Ingenuo estacional"]
    assert set(capas[0]["datos"]["serie"]) == {"SARIMA", "Ingenuo estacional"}


# ---------------------------------------------------------------- arranque de la aplicación
def _app():
    import streamlit as st
    from streamlit.testing.v1 import AppTest

    st.cache_data.clear()
    return AppTest.from_file(str(APP), default_timeout=90)


def test_la_app_arranca_sin_errores_desde_otro_directorio_y_muestra_lo_pedido(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # lectura de datos desde cualquier directorio
    at = _app().run()
    assert not at.exception and not at.error
    assert at.title[0].value == "Observatorio de Ocupación Hotelera de Colima · Manzanillo"
    assert [t.label for t in at.tabs] == ["Resumen", "Pronóstico 2024", "Comparación de modelos", "Proyección 2025–2027", "Cómo leerlo", "Fuentes y datos"]
    assert dict((m.label.split(" (")[0], m.value) for m in at.metric) == {
        "Ocupación media 2016–2024": "45.9 %", "Ocupación media 2024": "54.7 %", "Mes más bajo": "1.5 %", "Meses de 2024 dentro del intervalo": "12 de 12",
        "Media del periodo seleccionado": "45.9 %", "Mínimo del periodo": "1.5 %", "Máximo del periodo": "66.3 %",
        "MAE del SARIMA": "2.38 pp", "RMSE del SARIMA": "2.64 pp", "MAPE del SARIMA": "4.36 %", "Meses dentro del intervalo del 95 %": "12 de 12"}
    texto = " ".join(x.value for x in [*at.markdown, *at.info, *at.warning, *at.caption])
    assert "proyección histórica" in texto and "no es un pronóstico vigente" in texto and "Nombre provisional" in texto
    assert "Referencia ingenua estacional" in texto or "referencia ingenua estacional" in texto
    assert "no son normales" in texto and "No es más preciso" in texto and "no supone normalidad" in texto and "la elección no es firme" in texto   # intervalos bootstrap publicados con su limitación
    assert "StayMetrics" not in texto and "DENUE" not in texto and "pronóstico para 2025" not in texto.lower()


def test_la_app_muestra_un_error_claro_y_no_cifras_si_los_datos_no_son_coherentes(monkeypatch):
    def falla(*a, **k):
        raise cg.ErrorDatos("prueba: falta un archivo")

    monkeypatch.setattr(cg, "cargar_todo", falla)
    at = _app().run()
    assert not at.exception and len(at.error) == 1 and "prueba: falta un archivo" in at.error[0].value
    assert not list(at.metric) and not list(at.tabs)  # no se muestra ninguna cifra


def test_el_selector_de_modelos_no_rompe_la_app_ni_con_seleccion_vacia():
    at = _app().run()
    sel = at.multiselect[0]
    sel.set_value(["SES", "Holt", "Holt-Winters", "SARIMA", cg.FAMILIA_REFERENCIA]).run()
    assert not at.exception
    sel.set_value([]).run()
    assert not at.exception and any("Seleccione al menos un modelo" in i.value for i in at.info)


# ---------------------------------------------------------------- cierre de E1: secciones, filtro, intervalos, rutas y textos
from .test_tablero_cargador import afirmaciones_incorrectas  # noqa: E402


def _textos(at) -> str:
    return " ".join(x.value for x in [*at.markdown, *at.info, *at.warning, *at.caption])


def test_las_tres_secciones_estadisticas_muestran_los_datos_reales(d):
    at = _app().run()
    assert not at.exception
    sar = d.comparacion.set_index("familia").loc["SARIMA"]
    metricas = {m.label: m.value for m in at.metric}
    assert metricas["MAE del SARIMA"] == f"{sar['MAE']:.2f} pp" and metricas["RMSE del SARIMA"] == f"{sar['RMSE']:.2f} pp"
    assert metricas["MAPE del SARIMA"] == f"{sar['MAPE']:.2f} %"
    # Comparación: la tabla trae los cinco modelos con las métricas del laboratorio
    tablas = [t.value for t in at.dataframe]
    comp = [t for t in tablas if "MAE (pp)" in t.columns][0].set_index("Modelo")
    assert len(comp) == 5
    for fam in (*cg.FAMILIAS, cg.FAMILIA_REFERENCIA):
        fila = d.comparacion.set_index("familia").loc[fam]
        assert comp.loc[cg.NOMBRES[fam], "RMSE (pp)"] == pytest.approx(fila["RMSE"]) and comp.loc[cg.NOMBRES[fam], "MAE (pp)"] == pytest.approx(fila["MAE"])
    assert any("menor RMSE de los cuatro modelos obligatorios" in i.value and "mejor MAE y MAPE" in i.value for i in at.info)
    # Proyección 2025: la tabla es la del CSV, con límites ordenados
    proy_csv = d.elegido[d.elegido["tipo"] == cg.TIPO_PROYECCION]
    proy = [t for t in tablas if "Proyección (%)" in t.columns][0]
    assert len(proy) == 12
    assert proy["Proyección (%)"].round(6).tolist() == proy_csv["media"].round(6).tolist()
    assert (proy["Límite inferior 95 % (%)"] <= proy["Proyección (%)"]).all() and (proy["Proyección (%)"] <= proy["Límite superior 95 % (%)"]).all()


def test_las_franjas_del_95_reproducen_los_limites_del_csv(d):
    for tipo, grafica in ((cg.TIPO_RETRO, gr.grafica_retrospectiva), (cg.TIPO_PROYECCION, lambda p: gr.grafica_proyeccion(d.oro, p))):
        datos = d.elegido[d.elegido["tipo"] == tipo]
        banda = [c for c in _capas(grafica(datos))[1] if c["mark"] == "area"][0]["datos"]
        assert banda["li"].round(6).tolist() == datos["li"].round(6).tolist()
        assert banda["ls"].round(6).tolist() == datos["ls"].round(6).tolist()
        assert (banda["li"] <= banda["media"]).all() and (banda["media"] <= banda["ls"]).all()


@pytest.mark.parametrize("clave,n,bandas", [("todo", 108, ["COVID", "Año de prueba"]), ("pre_covid", 48, []),
                                            ("covid", 16, ["COVID"]), ("recuperacion", 42, ["Año de prueba"])])
def test_la_grafica_historica_filtrada_dibuja_solo_el_periodo_elegido(d, clave, n, bandas):
    vista = cg.filtrar_periodo(d.oro, clave)
    spec, capas = _capas(gr.grafica_historica(vista))
    linea = [c for c in capas if c["mark"] == "line"][0]["datos"]
    assert len(linea) == n
    rect = [c for c in capas if c["mark"] == "rect"]
    assert sorted(r["datos"]["etiqueta"].iloc[0] for r in rect) == sorted(bandas)
    desde, hasta = vista["fecha"].min(), vista["fecha"].max() + pd.offsets.MonthEnd(0)
    for r in rect:  # ninguna franja extiende el eje fuera del periodo
        assert pd.to_datetime(r["datos"]["inicio"]).iloc[0] >= desde and pd.to_datetime(r["datos"]["fin"]).iloc[0] <= hasta


def test_el_filtro_de_la_app_cambia_solo_la_vista_historica(d):
    at = _app().run()
    fijas = {m.label: m.value for m in at.metric if "periodo" not in m.label}
    for clave in cg.PERIODOS_HISTORICOS:
        at.radio[0].set_value(clave).run()
        assert not at.exception
        r = cg.resumen_periodo(cg.filtrar_periodo(d.oro, clave))
        metricas = {m.label: m.value for m in at.metric}
        assert metricas["Media del periodo seleccionado"] == f"{r['media']:.1f} %"
        assert {k: v for k, v in metricas.items() if "periodo" not in k} == fijas  # modelos y cifras globales sin cambio
        tabla = [t.value for t in at.dataframe if "Uso en el análisis" in t.value.columns][0]
        assert len(tabla) == r["n"]


@pytest.mark.parametrize("donde", ["raiz", "tablero", "otro"])
def test_la_app_arranca_desde_distintas_rutas(donde, tmp_path, monkeypatch):
    monkeypatch.chdir({"raiz": RAIZ, "tablero": RAIZ / "tablero", "otro": tmp_path}[donde])
    at = _app().run()
    assert not at.exception and not at.error
    assert any(m.label == "RMSE del SARIMA" for m in at.metric)


def test_la_app_no_presenta_2025_ni_2026_como_pronostico_vigente_y_explica_las_fechas():
    at = _app().run()
    texto = _textos(at)
    assert afirmaciones_incorrectas(texto) == []
    assert "Los modelos de este tablero usan esa historia para proyectar los meses siguientes" not in texto
    assert "evaluación retrospectiva de 2024" in texto and "proyección histórica de 2025" in texto
    assert "Último mes con datos observados" in texto and "Resultados estadísticos generados" in texto
    assert "no muestra una fecha de actualización propia" in texto
    assert "Resumen ejecutivo" in texto and "95 de cada 100" in texto and "StayMetrics" not in texto
