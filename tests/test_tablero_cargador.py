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
    "comparacion_modelos_2024.csv", "pronosticos_2024_por_modelo.csv", "pronostico_modelo_elegido.csv", "resumen.json", "ejecucion.json")),
    *(cg.CARPETA_INTERVALOS / n for n in ("intervalos_2024_mensual.csv", "proyeccion_2025_2027.csv", "intervalos_origen_movil_resumen.csv", "origen_movil_modelos.csv"))]


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


CARPETAS_PUBLICADAS = ("tablero", ".streamlit")  # lo que Streamlit Community Cloud despliega del repositorio para el tablero
SUFIJOS_NO_PUBLICABLES = {".pyc", ".pyo", ".log", ".tmp", ".bak", ".env", ".swp"}
NOMBRES_NO_PUBLICABLES = {"secrets.toml", ".DS_Store", "Thumbs.db"}
PATRON_SECRETOS = re.compile(r"(?i)(INEGI_TOKEN\s*=|api[_-]?key|password|ghp_[A-Za-z0-9]{10,}|github_pat_)")
# Plantillas de variables de entorno: se permiten SOLO si ninguna variable trae un valor real (vacío o marcador evidente).
PLANTILLAS_ENV = {".env.example", ".env.sample", ".env.template"}
VALOR_MARCADOR = re.compile(r"(?i)^(|<[^>]*>|\.\.\.|\*+|x{3,}|changeme|cambiar|ejemplo|example|tu[_-][\w-]*|your[_-][\w-]*"
                            r"|token-de-prueba[\w-]*|[\w.+-]*@(ejemplo|example)\.\w+|0|1)$")
PREFIJOS_CREDENCIAL = re.compile(r"(ghp_|gho_|github_pat_|AKIA|sk-|xox[bp]-)[A-Za-z0-9_-]{8,}|[A-Za-z0-9_-]{32,}")


def plantilla_env_con_credenciales(texto: str) -> list:
    """Nombres (nunca valores) de las variables de una plantilla ``.env.*`` con algo que no sea vacío o un marcador evidente."""
    malas = []
    for linea in texto.splitlines():
        s = linea.strip()
        if not s or s.startswith("#"):
            continue
        nombre, separador, valor = s.partition("=")
        valor = valor.strip().strip("'\"")
        if not separador or not VALOR_MARCADOR.match(valor) or PREFIJOS_CREDENCIAL.search(valor):
            malas.append(nombre.strip() or "(línea sin nombre)")
    return malas


def archivos_no_publicables(rutas) -> list:
    """REGLA (no depende del disco): rutas que nunca deben versionarse ni desplegarse junto al tablero."""
    # Ojo: Path(".env").suffix es "" (Python lo trata como nombre sin extensión); por eso .env se revisa por nombre.
    return [p for p in map(Path, rutas)
            if p.suffix in SUFIJOS_NO_PUBLICABLES or p.name in NOMBRES_NO_PUBLICABLES or "__pycache__" in p.parts
            or p.name == ".env" or (p.name.startswith(".env.") and p.name not in PLANTILLAS_ENV)]


def inventario_publicable() -> list:
    """INVENTARIO: archivos que pueden llegar al despliegue, es decir, los versionados más los nuevos que Git NO ignora
    (se podrían confirmar por error). Lo que Git ignora (``__pycache__``, que Python crea al importar) no se publica.

    Antes la prueba recorría el disco y fallaba con ``tablero/__pycache__``, que el propio ``import cargador`` crea:
    así quedó en rojo el CI de ``main`` en ``06452fd``.
    """
    import subprocess
    r = subprocess.run(["git", "-C", str(RAIZ), "ls-files", "--cached", "--others", "--exclude-standard", "--", *CARPETAS_PUBLICADAS],
                       capture_output=True, text=True)
    if r.returncode != 0:
        pytest.skip("git no está disponible: no se puede saber qué archivos se publican")
    return [RAIZ / x for x in r.stdout.split()]


def test_no_hay_secretos_ni_archivos_temporales_en_el_tablero():
    archivos = inventario_publicable()
    assert any(p.name == "streamlit_app.py" for p in archivos), "el inventario no incluye la aplicación"
    assert archivos_no_publicables(archivos) == []
    for p in archivos:
        if p.suffix in {".py", ".toml", ".txt", ".md"} and p.is_file():
            assert not PATRON_SECRETOS.search(p.read_text(encoding="utf-8")), p.name
        if p.name in PLANTILLAS_ENV and p.is_file():  # una plantilla se permite solo si no trae credenciales
            assert plantilla_env_con_credenciales(p.read_text(encoding="utf-8")) == [], p.name
    assert not (RAIZ / ".streamlit" / "secrets.toml").exists()


def test_la_regla_detecta_cada_tipo_de_archivo_no_publicable():
    """La regla no se debilitó: detecta cachés, temporales, registros, respaldos, .env y secretos de Streamlit."""
    malos = ["tablero/__pycache__/cargador.cpython-313.pyc", "tablero/__pycache__/x.cpython-314.opt-1.pyc", "tablero/x.pyo",
             "tablero/depuracion.log", "tablero/x.tmp", "tablero/app.py.bak", "tablero/.env", "tablero/.env.local",
             ".streamlit/secrets.toml", "tablero/.DS_Store"]
    assert [p.as_posix() for p in archivos_no_publicables(malos)] == malos
    assert archivos_no_publicables(["tablero/streamlit_app.py", "tablero/requirements.txt", ".streamlit/config.toml"]) == []
    assert PATRON_SECRETOS.search("INEGI_TOKEN = 'abc'") and PATRON_SECRETOS.search("ghp_" + "a" * 20)


def test_una_plantilla_env_example_se_permite_solo_sin_credenciales_reales():
    """``.env.example`` ya no es un falso positivo, pero un archivo con credenciales sigue rechazado (sin imprimir valores)."""
    assert archivos_no_publicables(["tablero/.env.example", ".streamlit/.env.sample", "tablero/.env.template"]) == []
    for real in (".env", ".env.local", ".env.production", ".env.development", "tablero/.env.example.bak"):
        assert archivos_no_publicables([real]), real
    buena = "# comentario\nINEGI_TOKEN=\nTDL_CONTACTO=correo@ejemplo.mx\nTDL_RED=0\nOTRA=<tu valor>\nCLAVE=tu_clave_aqui\n"
    assert plantilla_env_con_credenciales(buena) == []
    token_ghp = "ghp_" + "a" * 36  # construido en tiempo de ejecución: no es una credencial real ni queda literal en el repositorio
    larga = "Z" * 40
    for linea in (f"INEGI_TOKEN={token_ghp}", f"INEGI_TOKEN={larga}", "INEGI_TOKEN=abc123", "INEGI_TOKEN='valor-real'", "SOLO_NOMBRE"):
        malas = plantilla_env_con_credenciales(linea)
        assert malas and all(token_ghp not in m and larga not in m and "abc123" not in m for m in malas), linea  # solo nombres


def test_un_pycache_real_en_el_disco_no_rompe_la_prueba_pero_si_se_versionara_se_detectaria():
    """Reproduce la causa del CI en rojo: hay un ``__pycache__`` real en ``tablero/`` (lo crea Python al importar; si el entorno
    no escribe bytecode, se crea aquí). No entra al inventario porque Git lo ignora, y la regla lo marcaría si se versionara."""
    import py_compile
    cache = RAIZ / "tablero" / "__pycache__"
    creado = None
    if not any(cache.glob("*.pyc")):
        creado = Path(py_compile.compile(str(RAIZ / "tablero" / "cargador.py"), doraise=True))
    try:
        en_disco = sorted(cache.glob("*.pyc"))
        assert en_disco, "debe existir al menos un .pyc para reproducir el caso"
        inventario = {p.resolve() for p in inventario_publicable()}
        assert not any(p.resolve() in inventario for p in en_disco)  # ignorado por Git: no se publica
        assert archivos_no_publicables([p.relative_to(RAIZ) for p in en_disco])  # y la regla sí lo detecta
    finally:
        if creado is not None:
            creado.unlink(missing_ok=True)


# ---------------------------------------------------------------- filtro histórico, fechas y textos de cierre de E1
def test_el_filtro_historico_cubre_cada_periodo_y_no_modifica_el_oro():
    d = cg.cargar_todo()
    antes = d.oro.copy()
    esperado = {"todo": (108, "2016-01", "2024-12"), "pre_covid": (48, "2016-01", "2019-12"),
                "covid": (16, "2020-03", "2021-06"), "recuperacion": (42, "2021-07", "2024-12")}
    for clave, (n, ini, fin) in esperado.items():
        v = cg.filtrar_periodo(d.oro, clave)
        assert (len(v), v["periodo"].iloc[0], v["periodo"].iloc[-1]) == (n, ini, fin), clave
        assert v["periodo"].is_monotonic_increasing and not v["periodo"].duplicated().any()
    covid = cg.filtrar_periodo(d.oro, "covid")
    assert (covid["d_covid"] == 1).all() and len(covid) == int(d.oro["d_covid"].sum())  # mismo periodo que la regla del contrato
    pd.testing.assert_frame_equal(d.oro, antes)  # el filtro no altera los datos
    with pytest.raises(ValueError):
        cg.filtrar_periodo(d.oro, "2025")


def test_el_filtro_no_cambia_resultados_ni_textos_de_los_modelos():
    d = cg.cargar_todo()
    t1 = cg.textos_cliente(d)
    for clave in cg.PERIODOS_HISTORICOS:
        cg.filtrar_periodo(d.oro, clave)
    assert cg.textos_cliente(d) == t1
    d2 = cg.cargar_todo()
    pd.testing.assert_frame_equal(d.comparacion, d2.comparacion)
    pd.testing.assert_frame_equal(d.elegido, d2.elegido)


def test_resumen_del_periodo_coincide_con_el_oro():
    d = cg.cargar_todo()
    r = cg.resumen_periodo(cg.filtrar_periodo(d.oro, "covid"))
    assert r["n"] == 16 and r["media"] == pytest.approx(d.oro.loc[d.oro["d_covid"] == 1, "ocupacion_pct"].mean())
    assert r["mes_min"] == "abril de 2020" and r["min"] == pytest.approx(d.oro["ocupacion_pct"].min())


def test_las_fechas_salen_de_los_archivos_y_no_se_inventa_una_actualizacion_del_tablero():
    d = cg.cargar_todo()
    f = cg.fechas_clave(d)
    assert f["ultimo_observado"] == "diciembre de 2024" and d.meta_oro["periodo_max"] == "2024-12"
    assert f["resultados"] == cg.fecha_generacion(d.ejecucion)
    utc = pd.Timestamp(d.meta_oro["fecha_proceso_utc"]).tz_convert("America/Mexico_City")
    assert f["capa_oro"].startswith(f"{utc.day} de {cg.MESES[utc.month - 1]} de {utc.year}, {utc:%H:%M}")
    assert set(f) == {"ultimo_observado", "resultados", "capa_oro"}  # ninguna «fecha de actualización del tablero»


def test_el_destacado_de_la_comparacion_sale_de_la_tabla_del_laboratorio():
    d = cg.cargar_todo()
    dest = cg.destacado_comparacion(d)
    t = d.comparacion.set_index("familia")
    assert dest["menor_rmse_entre_obligatorios"] and t.loc[list(cg.FAMILIAS), "RMSE"].idxmin() == "SARIMA"
    assert dest["referencia_mejor_en"] == ["MAE", "MAPE"] and dest["elegido_mejor_que_referencia_en"] == ["RMSE"]
    texto = cg.textos_cliente(d)["destacado"]
    for m, fam in (("RMSE", "SARIMA"), ("MAE", "SARIMA"), ("MAE", cg.FAMILIA_REFERENCIA), ("MAPE", cg.FAMILIA_REFERENCIA)):
        assert f"{t.loc[fam, m]:.2f}" in texto, (m, fam)
    assert "menor RMSE de los cuatro modelos obligatorios" in texto and "referencia ingenua estacional obtuvo mejor MAE y MAPE" in texto
    assert "ninguna diferencia permite afirmar que un modelo sea mejor de forma general" in texto


def test_el_resumen_ejecutivo_y_la_lectura_de_la_historia_distinguen_2024_y_2025():
    d = cg.cargar_todo()
    t = cg.textos_cliente(d)
    e, h = t["ejecutivo"], t["historia"]
    p = cg.resumen_proyeccion(d.elegido)
    assert "12 de 12 meses" in e and f"±{p['semiancho_min']:.0f} a ±{p['semiancho_max']:.0f}" in e and "95 de cada 100" in e
    assert "no es una garantía" in e and "No hay un ganador claro" in e
    assert "evaluación retrospectiva de 2024" in h and "proyección histórica de 2025" in h and "diciembre de 2023" in h
    assert "diciembre de 2024" in h and "no es un pronóstico vigente" in h


PROHIBIDAS = [r"meses siguientes", r"próximos meses", r"pronóstic\w* (?:para|de) 202[56]", r"proyecci\w+ (?:para|de) 2026",
              r"(?:en|para) 202[56] se (?:espera|prevé|proyecta)", r"pronóstico actual", r"datos? (?:observados? )?de 2025 (?:muestran|indican)"]


def afirmaciones_incorrectas(texto: str) -> list:
    """Frases que presentarían 2025 o 2026 como pronóstico vigente u observado. Toda mención de «vigente» debe ir negada."""
    import re as _re
    malas = [m.group(0) for p in PROHIBIDAS for m in _re.finditer(p, texto, flags=_re.IGNORECASE)]
    for m in _re.finditer(r"vigente", texto, flags=_re.IGNORECASE):
        if not _re.search(r"\bno\b[^.]{0,40}$", texto[max(0, m.start() - 45):m.start()], flags=_re.IGNORECASE):
            malas.append(texto[max(0, m.start() - 45):m.end()])
    return malas


def test_los_textos_no_presentan_2025_ni_2026_como_pronostico_vigente():
    d = cg.cargar_todo()
    todo = " ".join([*cg.textos_cliente(d).values(), *cg.LIMITACIONES])
    assert afirmaciones_incorrectas(todo) == []
    assert afirmaciones_incorrectas("La ocupación de los meses siguientes será alta.") != []  # el detector sí detecta
    assert afirmaciones_incorrectas("Este es un pronóstico vigente para 2026.") != []


# ---------------------------------------------------------------- intervalos sin supuesto de normalidad (ampliación posterior a la entrega)
def test_los_intervalos_bootstrap_se_cargan_y_su_gaussiano_coincide_con_el_publicado():
    d = cg.cargar_todo()
    assert cg.validar_intervalos(d.intervalos, d.elegido) == []
    assert len(d.intervalos["mensual_2024"]) == 12 and len(d.intervalos["proyeccion"]) == 36


def test_un_intervalo_gaussiano_distinto_del_publicado_se_detecta(copia):
    ruta = copia / cg.CARPETA_INTERVALOS / "proyeccion_2025_2027.csv"
    df = pd.read_csv(ruta)
    df.loc[0, "ls_gauss"] += 5
    df.to_csv(ruta, index=False)
    with pytest.raises(cg.ErrorDatos, match="no coincide"):
        cg.cargar_todo(copia)
