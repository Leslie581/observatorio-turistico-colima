"""Exploración estadística (laboratorio/exploracion): cifras, 4 PNG reproducibles y lectura exclusiva del oro.

matplotlib es una dependencia del laboratorio (requirements-lab.txt). El flujo de captura diaria NO la instala, así que sin ella
estas pruebas se OMITEN; con ``TDL_EXIGIR_PRONOSTICOS=1`` (CI) su ausencia es un ERROR, no una omisión silenciosa.
Las pruebas usan el oro versionado real (datos reales), salvo la de validación, que corrompe una COPIA sintética.
"""
import json
import os
import shutil
from pathlib import Path

import pandas as pd
import pytest

try:
    import matplotlib  # noqa: F401
except ImportError:  # pragma: no cover
    if os.environ.get("TDL_EXIGIR_PRONOSTICOS") == "1":
        raise ImportError("falta matplotlib y TDL_EXIGIR_PRONOSTICOS=1 exige ejecutar las pruebas de exploración")
    pytest.skip("sin matplotlib (requirements-lab.txt)", allow_module_level=True)

from laboratorio.exploracion import explorar
from pipeline.calidad.cuarentena import ErrorPuertaCalidad
from pipeline.interfaz import RUTA_ORO

RAIZ = Path(__file__).resolve().parent.parent
PNG = b"\x89PNG\r\n\x1a\n"


@pytest.fixture(scope="module")
def corrida(tmp_path_factory):
    salida = tmp_path_factory.mktemp("explor")
    return salida, explorar.ejecutar(salida=salida)


def test_genera_las_cuatro_figuras_png_validas(corrida):
    salida, res = corrida
    assert res["figuras"] == list(explorar.FIGURAS.values()) and len(res["figuras"]) == 4
    for nombre in res["figuras"]:
        datos = (salida / "figuras" / nombre).read_bytes()
        assert datos.startswith(PNG) and len(datos) > 20_000, nombre
        ancho, alto = int.from_bytes(datos[16:20], "big"), int.from_bytes(datos[20:24], "big")
        assert ancho >= 1200 and alto >= 700, (nombre, ancho, alto)
        assert b"Software" not in datos and b"Creation Time" not in datos  # sin marcas de tiempo ni versión


def test_las_cifras_coinciden_con_un_calculo_independiente_sobre_el_oro(corrida):
    salida, res = corrida
    crudo = pd.read_csv(RUTA_ORO)
    y = crudo["ocupacion_pct"]
    assert res["periodo"] == ["2016-01", "2024-12", 108]
    assert res["minimo"] == {"periodo": "2020-04", "valor": pytest.approx(y.min())}
    assert res["maximo"]["valor"] == pytest.approx(y.max()) and res["maximo"]["periodo"] == "2017-04"
    assert res["covid"]["n_meses"] == int(crudo.d_covid.sum()) == 16
    assert res["covid"]["media_covid"] == pytest.approx(y[crudo.d_covid == 1].mean())
    assert res["covid"]["media_resto"] == pytest.approx(y[crudo.d_covid == 0].mean())
    assert res["atipicos_iqr"] == ["2020-04", "2020-05", "2020-06"]
    assert res["oferta_diaria_implicita"]["cambio_2017_06_pct"] == pytest.approx(30.5, abs=0.1)  # contrato §1.1
    assert res["oferta_diaria_implicita"]["cambio_2017_11_pct"] == pytest.approx(17.0, abs=0.1)

    por_mes = pd.read_csv(salida / "estadisticas_por_mes.csv")
    assert len(por_mes) == 12 and (por_mes["n"] == 9).all() and por_mes["n_sin_covid"].sum() == 92
    esperado = y.groupby(pd.to_datetime(crudo.fecha_inicio).dt.month).mean().to_numpy()
    assert por_mes["media"].to_numpy() == pytest.approx(esperado, abs=1e-3)
    por_anio = pd.read_csv(salida / "estadisticas_por_anio.csv")
    assert por_anio["anio"].tolist() == list(range(2016, 2025)) and por_anio["n_meses_covid"].sum() == 16
    general = pd.read_csv(salida / "estadisticas_descriptivas.csv").set_index("grupo")
    assert general.loc["todo_2016_2024", "n"] == 108 and general.loc["entrenamiento_2016_2023", "n"] == 96
    assert general.loc["prueba_2024", "n"] == 12 and general.loc["sin_covid", "n"] == 92


def test_los_parametros_de_transformacion_salen_solo_del_entrenamiento(corrida):
    salida, _ = corrida
    p = json.loads((salida / "parametros_transformaciones.json").read_text(encoding="utf-8"))
    crudo = pd.read_csv(RUTA_ORO)
    ent = crudo[crudo.periodo <= "2023-12"].ocupacion_pct
    assert p["minmax"]["n"] == p["zscore"]["n"] == 96 and p["minmax"]["ajustado_hasta"] == "2023-12"
    assert p["minmax"]["minimo"] == pytest.approx(ent.min()) and p["minmax"]["maximo"] == pytest.approx(ent.max())
    assert p["zscore"]["media"] == pytest.approx(ent.mean()) and p["zscore"]["desviacion"] == pytest.approx(ent.std(ddof=0))
    tab = pd.read_csv(salida / "transformaciones_ocupacion.csv")
    assert tab.conjunto.value_counts().to_dict() == {"entrenamiento": 96, "prueba": 12}
    prueba = tab[tab.conjunto == "prueba"]
    esperado = (prueba.valor - ent.min()) / (ent.max() - ent.min())  # parámetros del entrenamiento, no de 2024
    assert prueba.minmax.to_numpy() == pytest.approx(esperado.to_numpy(), abs=1e-5)


def test_es_reproducible_mismas_cifras_y_mismos_bytes_en_dos_corridas(corrida, tmp_path):
    salida, _ = corrida
    explorar.ejecutar(salida=tmp_path)
    archivos = sorted(p.relative_to(salida) for p in salida.rglob("*") if p.is_file())
    assert len(archivos) == 10  # 4 PNG + 3 CSV de estadísticas + resumen.json + parámetros + tabla de transformaciones
    for rel in archivos:
        assert (salida / rel).read_bytes() == (tmp_path / rel).read_bytes(), rel


def test_las_tablas_versionadas_estan_al_dia_con_el_oro_versionado(corrida):
    """Detecta resultados desactualizados. Compara cifras (CSV/JSON); los PNG dependen de la versión de matplotlib."""
    salida, _ = corrida
    versionadas = RAIZ / "laboratorio" / "exploracion" / "resultados"
    for nombre in ("estadisticas_descriptivas.csv", "estadisticas_por_anio.csv", "estadisticas_por_mes.csv", "resumen.json",
                   "parametros_transformaciones.json", "transformaciones_ocupacion.csv"):
        nuevo = (salida / nombre).read_bytes().replace(b"\r\n", b"\n")
        viejo = (versionadas / nombre).read_bytes().replace(b"\r\n", b"\n")
        assert nuevo == viejo, f"{nombre} está desactualizado: ejecute python -m laboratorio.exploracion.explorar"


def test_lee_la_capa_oro_por_la_interfaz_validada_y_no_acepta_un_oro_alterado(tmp_path):
    """SINTÉTICA: copia del oro con un valor imposible; la interfaz (puerta de calidad) debe rechazarla."""
    copia = tmp_path / "oro.csv"
    shutil.copy(RUTA_ORO, copia)
    df = pd.read_csv(copia, dtype=str)
    df.loc[10, "ocupacion_pct"] = "180.0"
    df.to_csv(copia, index=False, lineterminator="\n")
    with pytest.raises(ErrorPuertaCalidad):
        explorar.ejecutar(oro=copia, salida=tmp_path / "salida")
    assert not (tmp_path / "salida" / "figuras").exists()


def test_la_exploracion_no_ajusta_modelos_ni_repite_pronosticos():
    codigo = (RAIZ / "laboratorio" / "exploracion" / "explorar.py").read_text(encoding="utf-8")
    for prohibido in ("statsmodels", "scipy", "pronosticos", "bronce", "plata"):
        assert f"import {prohibido}" not in codigo and f"from {prohibido}" not in codigo
    assert "data/oro" in codigo and "cargar_oro_mensual" in codigo
