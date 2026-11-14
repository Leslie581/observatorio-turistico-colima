"""Jerarquías conceptuales de la capa oro (pipeline/jerarquias.py): tiempo, geografía y ubicación de DENUE.

Se prueban con el bronce REAL del repositorio (copiado a una carpeta temporal: no se escribe en data/) y con casos sintéticos
para las fallas. Las cifras de Base70 son estables (archivo congelado); DENUE crece con cada captura, así que de él solo se
comprueban invariantes.
"""
import shutil
from pathlib import Path

import pandas as pd
import pytest

from pipeline import jerarquias as j
from pipeline import oro as o
from pipeline.calidad.cuarentena import ErrorPuertaCalidad
from pipeline.ejecutar import ejecutar

RAIZ = Path(__file__).resolve().parent.parent
BRONCE = RAIZ / "data" / "bronce"
pytestmark = [pytest.mark.datos, pytest.mark.skipif(not (BRONCE / "datatur" / "Base70centros.csv").exists(), reason="sin bronce")]


@pytest.fixture(scope="module")
def corrida(tmp_path_factory):
    raiz = tmp_path_factory.mktemp("jerarquias")
    shutil.copytree(BRONCE, raiz / "data" / "bronce")
    res = ejecutar(raiz, ahora="2026-11-13T00:00:00+00:00")
    assert res["estado"] == "ok", res
    return raiz, res


def _leer(raiz, nombre):
    return pd.read_csv(raiz / "data" / "oro" / nombre, dtype=str, keep_default_na=False)


def test_el_pipeline_escribe_las_tres_dimensiones(corrida):
    raiz, res = corrida
    assert res["oro"]["dim_tiempo"] == 108 and res["oro"]["dim_geografia"] == 1 and res["oro"]["dim_ubicacion_denue"] >= 3
    for n in ("dim_tiempo.csv", "dim_geografia.csv", "dim_ubicacion_denue.csv"):
        assert (raiz / "data" / "oro" / n).is_file() and f"data/oro/{n}" in res["archivos"]


def test_la_jerarquia_temporal_cubre_los_108_meses_y_enlaza_con_el_oro(corrida):
    raiz, _ = corrida
    t, m = _leer(raiz, "dim_tiempo.csv"), _leer(raiz, "manzanillo_ocupacion_mensual.csv")
    assert list(t.columns) == j.COLUMNAS_TIEMPO and len(t) == 108
    assert t.periodo.tolist() == m.periodo.tolist()                       # clave foránea: mismos periodos y mismo orden
    assert t.periodo.is_unique and t.anio_trimestre.nunique() == 36 and t.anio.nunique() == 9
    primera, ultima = t.iloc[0], t.iloc[-1]
    assert (primera.anio, primera.trimestre, primera.mes, primera.nombre_mes) == ("2016", "1", "1", "enero")
    assert (ultima.anio, ultima.trimestre, ultima.mes, ultima.nombre_mes, ultima.anio_trimestre) == ("2024", "4", "12", "diciembre", "2024-T4")


def test_cada_trimestre_tiene_3_meses_y_cada_mes_un_solo_padre(corrida):
    raiz, _ = corrida
    t = _leer(raiz, "dim_tiempo.csv")
    assert (t.groupby("anio_trimestre").size() == 3).all()
    assert (t.groupby("periodo").anio_trimestre.nunique() == 1).all()
    esperado = {"1": "1", "2": "1", "3": "1", "4": "2", "5": "2", "6": "2", "7": "3", "8": "3", "9": "3", "10": "4", "11": "4", "12": "4"}
    assert {mes: g.trimestre.iloc[0] for mes, g in t.groupby("mes")} == esperado


def test_la_jerarquia_geografica_solo_afirma_lo_que_las_fuentes_justifican(corrida):
    raiz, _ = corrida
    g = _leer(raiz, "dim_geografia.csv")
    assert list(g.columns) == j.COLUMNAS_GEOGRAFIA and len(g) == 1
    f = g.iloc[0]
    assert (f.entidad_clave, f.entidad, f.municipio_clave, f.municipio, f.centro_turistico) == ("06", "Colima", "06007", "Manzanillo", "Manzanillo")
    assert (f.tipo_centro, f.subtipo_centro) == ("Centros de Playa", "Tradicionales")      # salen de Base70, no se escriben a mano
    assert f.municipio_clave[:2] == f.entidad_clave                                        # la entidad es el prefijo de la clave municipal


def test_la_ubicacion_de_denue_no_trae_datos_de_establecimientos(corrida):
    raiz, _ = corrida
    u = _leer(raiz, "dim_ubicacion_denue.csv")
    assert list(u.columns) == j.COLUMNAS_UBICACION and len(u) >= 3
    assert not u.duplicated(["localidad", "colonia"]).any()
    assert set(u.municipio_clave) == {"06007"} and set(u.entidad_clave) == {"06"}
    assert not ({"clee", "latitud", "longitud", "id", "establecimientos"} & set(u.columns))


def test_las_dimensiones_son_deterministas_byte_a_byte(corrida, tmp_path):
    raiz, _ = corrida
    otra = tmp_path / "otra"
    shutil.copytree(BRONCE, otra / "data" / "bronce")
    assert ejecutar(otra, ahora="2027-01-01T00:00:00+00:00")["estado"] == "ok"           # otra hora de corrida: mismo resultado
    for n in ("dim_tiempo.csv", "dim_geografia.csv", "dim_ubicacion_denue.csv"):
        assert (raiz / "data" / "oro" / n).read_bytes() == (otra / "data" / "oro" / n).read_bytes(), n


def test_el_diccionario_documenta_cada_columna_de_las_dimensiones(corrida):
    raiz, _ = corrida
    d = pd.read_csv(raiz / "data" / "oro" / "diccionario_datos.csv", dtype=str)
    for dataset, columnas in (("dim_tiempo", j.COLUMNAS_TIEMPO), ("dim_geografia", j.COLUMNAS_GEOGRAFIA), ("dim_ubicacion_denue", j.COLUMNAS_UBICACION)):
        assert set(d[d.dataset == dataset].columna) == set(columnas), dataset
    assert not d.isna().any().any()                                                       # ninguna definición, fuente ni regla vacía
    assert len(o.diccionario_df()) == len(o.DICCIONARIO) + len(j.DICCIONARIO_JERARQUIAS)


def test_el_oro_mensual_no_cambia_con_las_jerarquias(corrida):
    """Las jerarquías son dimensiones aparte: el oro mensual conserva sus 20 columnas y el contrato 1.0.0."""
    raiz, _ = corrida
    m = _leer(raiz, "manzanillo_ocupacion_mensual.csv")
    assert list(m.columns) == o.COLUMNAS_ORO and len(m.columns) == 20
    assert (RAIZ / "data" / "oro" / "manzanillo_ocupacion_mensual.csv").read_bytes() == (raiz / "data" / "oro" / "manzanillo_ocupacion_mensual.csv").read_bytes()


# ------------------------------------------------------------------ fallas (datos sintéticos)
def _oro_sintetico():
    idx = pd.period_range("2016-01", periods=108, freq="M").astype(str)
    return pd.DataFrame({"periodo": idx, "fecha_inicio": [p + "-01" for p in idx]})


def test_una_clave_de_mes_invalida_se_rechaza():
    oro = _oro_sintetico()
    oro.loc[0, "periodo"] = "2016-13"
    with pytest.raises(Exception):
        j.construir_dim_tiempo(oro)


def test_un_oro_con_otro_numero_de_meses_se_rechaza():
    with pytest.raises(ErrorPuertaCalidad, match="108"):
        j.construir_dim_tiempo(_oro_sintetico().iloc[:100])


def test_la_integridad_detecta_periodos_distintos_y_trimestres_equivocados():
    oro = _oro_sintetico()
    t = j.construir_dim_tiempo(oro)
    g = pd.DataFrame([{"entidad_clave": "06", "entidad": "Colima", "municipio_clave": "06007", "municipio": "Manzanillo",
                       "centro_turistico": "Manzanillo", "tipo_centro": "a", "subtipo_centro": "b"}])
    u = pd.DataFrame([{"entidad_clave": "06", "municipio_clave": "06007", "localidad": "X", "colonia": "Y"}])
    j.verificar_integridad(oro, t, g, u)                                                   # el caso sano pasa
    with pytest.raises(ErrorPuertaCalidad, match="periodos"):
        j.verificar_integridad(oro.iloc[:-1], t, g, u)
    malo = t.copy()
    malo.loc[0, "trimestre"] = 4
    with pytest.raises(ErrorPuertaCalidad):
        j.verificar_integridad(oro, malo, g, u)
    with pytest.raises(ErrorPuertaCalidad, match="no está en dim_geografia"):
        j.verificar_integridad(oro, t, g, u.assign(municipio_clave="06002"))


def test_un_establecimiento_fuera_del_municipio_se_rechaza():
    plata = pd.DataFrame([{"municipio_clave": "06002", "localidad": "X", "colonia": "Y"}])
    with pytest.raises(ErrorPuertaCalidad, match="fuera del municipio"):
        j.construir_dim_ubicacion_denue(plata)


def test_el_centro_objetivo_debe_tener_un_unico_tipo():
    ambiguo = pd.DataFrame([{"centro": "Manzanillo", "tipo_centro": "a", "subtipo_centro": "b"},
                            {"centro": "Manzanillo", "tipo_centro": "c", "subtipo_centro": "d"}])
    with pytest.raises(ErrorPuertaCalidad, match="único"):
        j.construir_dim_geografia(ambiguo)
    with pytest.raises(ErrorPuertaCalidad):
        j.construir_dim_geografia(pd.DataFrame(columns=["centro", "tipo_centro", "subtipo_centro"]))


def test_la_oferta_denue_se_enlaza_con_la_dimension_geografica_por_municipio():
    """El modelo integrado: la oferta de DENUE y la ocupación de DATATUR comparten la dimensión geográfica (municipio 06007)."""
    oro = _oro_sintetico()
    t = j.construir_dim_tiempo(oro)
    g = pd.DataFrame([{"entidad_clave": "06", "entidad": "Colima", "municipio_clave": "06007", "municipio": "Manzanillo",
                       "centro_turistico": "Manzanillo", "tipo_centro": "a", "subtipo_centro": "b"}])
    u = pd.DataFrame([{"entidad_clave": "06", "municipio_clave": "06007", "localidad": "X", "colonia": "Y"}])
    j.verificar_integridad(oro, t, g, u, pd.DataFrame({"municipio_clave": ["06007", "06007"]}))
    with pytest.raises(ErrorPuertaCalidad, match="oferta"):
        j.verificar_integridad(oro, t, g, u, pd.DataFrame({"municipio_clave": ["06007", "06002"]}))


def test_la_corrida_real_enlaza_la_oferta_con_la_geografia(corrida):
    raiz, _ = corrida
    oferta, g = _leer(raiz, "manzanillo_oferta_hospedaje.csv"), _leer(raiz, "dim_geografia.csv")
    assert set(oferta.municipio_clave) == set(g.municipio_clave) == {"06007"}


def test_el_pipeline_informa_la_reduccion_de_datos_con_porcentajes(corrida):
    """Rúbrica de E1: «reducción de datos, con el porcentaje de reducción logrado y lo que se pierde»."""
    _, res = corrida
    r = res["reduccion"]
    assert r["filas_plata_datatur"] == 31145 and r["filas_manzanillo_2_a_5_estrellas"] == 432 and r["filas_oro_mensual"] == 108
    assert r["reduccion_pct_agregacion_categoria_mes"] == 75.0 and r["reduccion_pct_plata_a_oro"] == 99.65
    assert "categoría" in r["se_pierde"]
