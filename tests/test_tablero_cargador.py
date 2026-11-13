"""Carga y validación de los datos del tablero (tablero/cargador.py).

Solo requieren pandas y numpy, así que corren también en la captura diaria. Las pruebas con datos alterados usan una COPIA en una
carpeta temporal (declaradas SINTÉTICAS); las demás usan los archivos reales versionados del repositorio.
"""
import json
import re
import shutil
import sys
from pathlib import Path

import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "tablero"))
import cargador as cg  # noqa: E402

ARCHIVOS = [cg.RUTA_ORO, cg.RUTA_META_ORO, *(cg.CARPETA_RESULTADOS / n for n in (
    "comparacion_modelos_2024.csv", "pronosticos_2024_por_modelo.csv", "pronostico_modelo_elegido.csv", "resumen.json", "ejecucion.json"))]


@pytest.fixture
def copia(tmp_path):
    """SINTÉTICA: copia de los 7 archivos que lee el tablero, para poder alterarlos sin tocar el repositorio."""
    for rel in ARCHIVOS:
        destino = tmp_path / rel
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(RAIZ / rel, destino)
    return tmp_path


# ---------------------------------------------------------------- lectura con los datos reales
def test_la_raiz_se_calcula_desde_el_archivo_y_los_datos_se_leen_desde_cualquier_directorio(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # un directorio de trabajo ajeno al repositorio
    assert cg.RAIZ.is_absolute() and (cg.RAIZ / "tablero" / "cargador.py").is_file()
    d = cg.cargar_todo()
    assert len(d.oro) == 108 and len(d.comparacion) == 5 and len(d.por_modelo) == 60 and len(d.elegido) == 24


def test_el_oro_cubre_108_meses_sin_huecos_y_con_ocupacion_valida():
    oro = cg.cargar_oro()
    assert oro["periodo"].iloc[0] == "2016-01" and oro["periodo"].iloc[-1] == "2024-12" and oro["periodo"].is_unique
    assert oro["ocupacion_pct"].between(0, 100).all() and oro["ocupacion_pct"].notna().all()
    assert oro["fecha"].is_monotonic_increasing and (oro["conjunto"] == "Prueba (2024)").sum() == 12
    assert oro.loc[oro["ocupacion_pct"].idxmin(), "periodo"] == "2020-04"


def test_las_constantes_del_tablero_coinciden_con_las_del_pipeline():
    from pipeline import config

    assert (cg.N_MESES, cg.PRIMER_PERIODO, cg.ULTIMO_PERIODO) == (config.N_PERIODOS, config.PERIODO_INICIO, config.PERIODO_FIN)
    assert (cg.FIN_ENTRENAMIENTO, cg.COVID_INICIO, cg.COVID_FIN) == (config.FIN_ENTRENAMIENTO, config.COVID_INICIO, config.COVID_FIN)


def test_las_cifras_del_tablero_coinciden_con_el_laboratorio():
    d = cg.cargar_todo()
    assert cg.validar_coherencia(d.oro, d.comparacion, d.por_modelo, d.elegido, d.resumen) == []
    fila = d.comparacion.set_index("familia")
    assert fila.loc["SARIMA", "MAE"] == pytest.approx(2.376157, abs=1e-6) and fila.loc["SARIMA", "RMSE"] == pytest.approx(2.638843, abs=1e-6)
    ref = d.resumen["referencia_ingenuo_estacional"]
    assert fila.loc[cg.FAMILIA_REFERENCIA, "MAE"] == ref["MAE"] and fila.loc[cg.FAMILIA_REFERENCIA, "RMSE"] == ref["RMSE"]
    assert d.comparacion.set_index("familia")["es_elegido"].to_dict() == {"SES": False, "Holt": False, "Holt-Winters": False, "SARIMA": True, "ingenuo": False}
    assert d.resumen["elegido"]["familia"] == "SARIMA" and d.ejecucion["fuente"] == "oro"


def test_las_metricas_recalculadas_desde_los_pronosticos_igualan_la_tabla_del_laboratorio():
    d = cg.cargar_todo()
    for fam, g in d.por_modelo.groupby("familia"):
        m = cg.metricas(g["observado"], g["media"])
        f = d.comparacion.set_index("familia").loc[fam]
        assert (m["MAE"], m["RMSE"], m["MAPE"]) == pytest.approx((f["MAE"], f["RMSE"], f["MAPE"]), abs=1e-5), fam


def test_los_intervalos_se_representan_con_limites_ordenados_y_el_2024_cae_dentro_12_de_12():
    d = cg.cargar_todo()
    e = d.elegido
    assert ((e["li"] <= e["media"]) & (e["media"] <= e["ls"])).all()
    retro = e[e["tipo"] == cg.TIPO_RETRO]
    assert cg.cobertura_ip95(retro) == (12, 12)
    assert (retro["semiancho"] > 10).all() and (retro["observado"] >= retro["li"]).all()
    con_ip = d.por_modelo[d.por_modelo["familia"].isin(cg.FAMILIAS)]
    assert ((con_ip["li"] <= con_ip["media"]) & (con_ip["media"] <= con_ip["ls"])).all()
    assert d.por_modelo[d.por_modelo["familia"] == cg.FAMILIA_REFERENCIA][["li", "ls"]].isna().all().all()  # la ingenua no tiene intervalo


def test_la_proyeccion_2025_no_trae_valores_observados_y_se_rotula_como_historica():
    e = cg.cargar_pronostico_elegido()
    p = e[e["tipo"] == cg.TIPO_PROYECCION]
    assert list(p["periodo"]) == [f"2025-{m:02d}" for m in range(1, 13)] and p["observado"].isna().all()
    assert (p["entrenado_con"] == "2016-01..2024-12").all()
    assert set(p["serie"]) == {"Proyección 2025 (calculada con datos hasta diciembre de 2024)"}
    r = cg.resumen_proyeccion(e)
    assert r["media_anual"] == pytest.approx(54.62, abs=0.01) and r["mes_max"] == "diciembre" and r["mes_min"] == "septiembre"


def test_el_texto_para_el_cliente_sale_de_los_datos_y_no_presenta_2025_como_pronostico_vigente():
    d = cg.cargar_todo()
    t = cg.textos_cliente(d)
    p = t["proyeccion_2025"]
    assert "no un pronóstico vigente" in p and "proyección histórica" in p and "diciembre de 2024" in p and "noviembre de 2026" in p
    assert "54.6 %" in p and "diciembre (62.5 %)" in p and "septiembre (43.7 %)" in p
    assert "12 de 12 meses" in t["resultado_2024"] and "54.7 %" in t["resultado_2024"]
    assert "no fue mejor en MAE, MAPE" in t["comparacion"] and "no permiten declarar un ganador claro" in t["comparacion"]
    assert "±12 a ±21" in t["intervalo"] and len(cg.LIMITACIONES) >= 5
    assert cg.fecha_generacion(d.ejecucion).startswith("13 de noviembre de 2026, 02:20")


# ---------------------------------------------------------------- validaciones que deben fallar (copias sintéticas alteradas)
def test_falta_un_archivo_lanza_un_error_claro(copia):
    (copia / cg.CARPETA_RESULTADOS / "resumen.json").unlink()
    with pytest.raises(cg.ErrorDatos, match="Falta el archivo laboratorio/pronosticos/resultados/resumen.json"):
        cg.cargar_todo(copia)


def test_una_raiz_sin_datos_no_inventa_nada(tmp_path):
    with pytest.raises(cg.ErrorDatos):
        cg.cargar_todo(tmp_path)


def test_oro_incompleto_o_fuera_de_rango_se_rechaza(copia):
    ruta = copia / cg.RUTA_ORO
    df = pd.read_csv(ruta)
    df.iloc[:-1].to_csv(ruta, index=False)
    with pytest.raises(cg.ErrorDatos, match="108 meses"):
        cg.cargar_oro(copia)
    df.loc[10, "ocupacion_pct"] = 140.0
    df.to_csv(ruta, index=False)
    with pytest.raises(cg.ErrorDatos, match="entre 0 y 100"):
        cg.cargar_oro(copia)
    df = pd.read_csv(RAIZ / cg.RUTA_ORO)
    df.loc[5, "periodo"] = "2016-07"  # periodo repetido
    df.to_csv(ruta, index=False)
    with pytest.raises(cg.ErrorDatos, match="repetidos"):
        cg.cargar_oro(copia)


def test_un_intervalo_invertido_se_rechaza(copia):
    ruta = copia / cg.CARPETA_RESULTADOS / "pronostico_modelo_elegido.csv"
    df = pd.read_csv(ruta)
    df.loc[3, ["li", "ls"]] = df.loc[3, ["ls", "li"]].to_numpy()  # límite inferior > superior
    df.to_csv(ruta, index=False)
    with pytest.raises(cg.ErrorDatos, match="límite inferior ≤ media ≤ límite superior"):
        cg.cargar_pronostico_elegido(copia)


def test_la_proyeccion_2025_con_observados_se_rechaza(copia):
    ruta = copia / cg.CARPETA_RESULTADOS / "pronostico_modelo_elegido.csv"
    df = pd.read_csv(ruta)
    df.loc[df["periodo"] == "2025-03", "observado"] = 50.0
    df.to_csv(ruta, index=False)
    with pytest.raises(cg.ErrorDatos, match="no debe traer valores observados"):
        cg.cargar_pronostico_elegido(copia)


def test_falta_un_modelo_o_un_mes_se_rechaza(copia):
    ruta = copia / cg.CARPETA_RESULTADOS / "comparacion_modelos_2024.csv"
    df = pd.read_csv(ruta)
    df[df["familia"] != "Holt"].to_csv(ruta, index=False)
    with pytest.raises(cg.ErrorDatos, match="debe tener los modelos"):
        cg.cargar_comparacion(copia)
    ruta = copia / cg.CARPETA_RESULTADOS / "pronosticos_2024_por_modelo.csv"
    df = pd.read_csv(ruta)
    df.drop(df.index[5]).to_csv(ruta, index=False)
    with pytest.raises(cg.ErrorDatos, match="un valor por cada mes de 2024"):
        cg.cargar_pronosticos_2024(copia)


def test_cifras_que_no_cuadran_con_la_capa_oro_o_con_la_tabla_se_detectan(copia):
    ruta = copia / cg.CARPETA_RESULTADOS / "pronosticos_2024_por_modelo.csv"
    df = pd.read_csv(ruta)
    df.loc[(df["familia"] == "SARIMA") & (df["periodo"] == "2024-05"), "observado"] += 5  # observado distinto del oro
    df.to_csv(ruta, index=False)
    with pytest.raises(cg.ErrorDatos, match="no son coherentes con el laboratorio"):
        cg.cargar_todo(copia)
    assert cg.cargar_todo(copia, validar=False) is not None  # sin validar, lee pero no garantiza coherencia
    ruta = copia / cg.CARPETA_RESULTADOS / "comparacion_modelos_2024.csv"
    c = pd.read_csv(RAIZ / cg.CARPETA_RESULTADOS / "pronosticos_2024_por_modelo.csv")
    c.to_csv(copia / cg.CARPETA_RESULTADOS / "pronosticos_2024_por_modelo.csv", index=False)
    t = pd.read_csv(ruta)
    t.loc[t["familia"] == "SARIMA", "RMSE"] = 1.0  # tabla que no corresponde a los pronósticos
    t.to_csv(ruta, index=False)
    with pytest.raises(cg.ErrorDatos, match="RMSE recalculado"):
        cg.cargar_todo(copia)


def test_json_invalido_o_incompleto_se_rechaza(copia):
    (copia / cg.CARPETA_RESULTADOS / "ejecucion.json").write_text("{no es json", encoding="utf-8")
    with pytest.raises(cg.ErrorDatos, match="JSON válido"):
        cg.cargar_ejecucion(copia)
    (copia / cg.CARPETA_RESULTADOS / "ejecucion.json").write_text(json.dumps({"fuente": "oro"}), encoding="utf-8")
    with pytest.raises(cg.ErrorDatos, match="no tiene la clave"):
        cg.cargar_ejecucion(copia)


# ---------------------------------------------------------------- arquitectura, privacidad y despliegue
def test_el_tablero_no_lee_denue_bronce_plata_ni_usa_secretos_ni_rutas_absolutas():
    fuentes = {p.name: p.read_text(encoding="utf-8") for p in (RAIZ / "tablero").glob("*.py")}
    assert set(fuentes) >= {"cargador.py", "graficas.py", "streamlit_app.py"}
    for nombre, codigo in fuentes.items():
        assert not re.search(r"(?i)\b(bronce|plata|oferta_hospedaje|clee)\b", re.sub(r'""".*?"""', "", codigo, flags=re.S)), nombre
        assert not re.search(r"st\.secrets|os\.environ|getenv|requests|urllib|subprocess|import statsmodels|from statsmodels|pipeline\.ejecutar", codigo), nombre
        assert not re.search(r"[A-Za-z]:\\\\|[A-Za-z]:/Users|/Users/|/home/", codigo), nombre
    assert all("denue" not in str(r).lower() and "bronce" not in str(r) for r in ARCHIVOS)  # solo capa oro y resultados versionados


def test_la_marca_provisional_se_usa_y_no_aparece_el_nombre_anterior():
    for p in (RAIZ / "tablero").glob("*.py"):
        assert "staymetrics" not in p.read_text(encoding="utf-8").lower(), p.name
    assert "nombre provisional" in (RAIZ / "tablero" / "streamlit_app.py").read_text(encoding="utf-8").lower()


def test_requirements_del_tablero_son_minimos_y_estan_fijados():
    lineas = [x.strip() for x in (RAIZ / "tablero" / "requirements.txt").read_text(encoding="utf-8").splitlines() if x.strip() and not x.startswith("#")]
    nombres = [re.split(r"[=<>]", x)[0].lower() for x in lineas]
    assert nombres == ["streamlit", "altair", "pandas", "numpy"] and all(re.fullmatch(r"[a-z]+==\d+(\.\d+)*", x) for x in lineas)
    assert not set(nombres) & {"statsmodels", "scipy", "matplotlib", "pandera", "requests"}  # nada de laboratorio ni de red
    assert {x.split("==")[0]: x.split("==")[1] for x in lineas}["pandas"] == "3.0.5"  # misma versión que el resto del proyecto


def test_no_hay_secretos_ni_archivos_temporales_en_el_tablero():
    for p in (RAIZ / "tablero").rglob("*"):
        if p.is_file():
            assert p.suffix not in {".pyc", ".log", ".tmp", ".bak", ".env"} and "__pycache__" not in p.parts, p
    for p in (RAIZ / "tablero").glob("*.py"):
        assert not re.search(r"(?i)(INEGI_TOKEN|api[_-]?key|password|ghp_|github_pat_)", p.read_text(encoding="utf-8")), p.name
    assert not (RAIZ / ".streamlit" / "secrets.toml").exists()
