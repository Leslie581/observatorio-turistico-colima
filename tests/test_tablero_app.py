"""Gráficas y arranque del tablero (tablero/graficas.py y tablero/streamlit_app.py).

Requieren altair y streamlit (tablero/requirements.txt). El CI actual y la captura diaria NO los instalan, así que aquí se OMITEN
(`-rs` lista el motivo); se ejecutan con ``pip install -r tablero/requirements.txt`` y están pensadas para correr localmente antes del despliegue.
"""
import sys
from pathlib import Path

import pandas as pd
import pytest

alt = pytest.importorskip("altair", reason="sin altair (tablero/requirements.txt)")
pytest.importorskip("streamlit", reason="sin streamlit (tablero/requirements.txt)")

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
    assert [t.label for t in at.tabs] == ["Resumen", "Pronóstico 2024", "Comparación de modelos", "Proyección 2025", "Cómo leerlo", "Fuentes y datos"]
    assert dict((m.label.split(" (")[0], m.value) for m in at.metric) == {
        "Ocupación media 2016–2024": "45.9 %", "Ocupación media 2024": "54.7 %", "Mes más bajo": "1.5 %", "Meses de 2024 dentro del intervalo": "12 de 12"}
    texto = " ".join(x.value for x in [*at.markdown, *at.info, *at.warning, *at.caption])
    assert "proyección histórica" in texto and "no es un pronóstico vigente" in texto and "Nombre provisional" in texto
    assert "Referencia ingenua estacional" in texto or "referencia ingenua estacional" in texto
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
