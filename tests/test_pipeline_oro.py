"""Capa oro: fórmula, 108 periodos, columnas del contrato, errores controlados y agregado DENUE (datos SINTÉTICOS)."""
import pandas as pd
import pytest

from pipeline import oro as o
from pipeline.calidad.cuarentena import Cuarentena, ErrorPuertaCalidad
from pipeline.plata_datatur import procesar_base70
from pipeline.plata_denue import procesar_capturas
from tests.pipeline_helpers import escribir_base70, escribir_denue, filas_manzanillo, registro_denue

AHORA = "2026-11-13T00:00:00+00:00"


def _oro(tmp_path, filas):
    ruta = escribir_base70(tmp_path, filas)
    plata, sha = procesar_base70(ruta, Cuarentena(AHORA))
    return o.construir_oro_mensual(plata, sha)


def test_ocupacion_es_cociente_de_sumas_y_no_promedio_de_porcentajes(tmp_path):
    oro = _oro(tmp_path, filas_manzanillo())
    # 2016-01, 2 a 5 estrellas: disponibles 100+200+300+400 = 1000; ocupados (res + no res) 70+140+180+180 = 570
    assert oro.ocupacion_pct.iloc[0] == pytest.approx(57.0)
    promedio_simple = (70 / 100 + 140 / 200 + 180 / 300 + 180 / 400) / 4 * 100  # 61.25: NO es la definición
    assert promedio_simple == pytest.approx(61.25) and oro.ocupacion_pct.iloc[0] != pytest.approx(promedio_simple)
    assert oro.cuartos_disponibles.iloc[0] == 1000 and oro.cuartos_ocupados.iloc[0] == 570


def test_una_estrella_se_excluye_y_no_cambia_el_resultado(tmp_path):
    con = _oro(tmp_path / "a", filas_manzanillo(con_una_estrella=True))
    sin = _oro(tmp_path / "b", filas_manzanillo(con_una_estrella=False))
    pd.testing.assert_frame_equal(con.drop(columns=["sha256_bronce", "ejecucion"]), sin.drop(columns=["sha256_bronce", "ejecucion"]))
    assert (con.categorias_incluidas == "2-5 estrellas").all() and (con.n_categorias_fuente == 4).all()


def test_108_periodos_columnas_y_orden_del_contrato(tmp_path):
    oro = _oro(tmp_path, filas_manzanillo())
    assert list(oro.columns) == o.COLUMNAS_ORO and len(o.COLUMNAS_ORO) == 20
    assert len(oro) == 108 and oro.periodo.is_unique and oro.periodo.is_monotonic_increasing
    assert oro.periodo.iloc[0] == "2016-01" and oro.periodo.iloc[-1] == "2024-12"
    assert oro.periodo.tolist() == pd.period_range("2016-01", "2024-12", freq="M").astype(str).tolist()
    assert oro.d_covid.sum() == 16 and oro.d_oferta_2017.sum() == 91 and (oro.version_contrato == "1.0.0").all()
    assert oro.loc[oro.periodo == "2020-02", "d_covid"].item() == 0 and oro.loc[oro.periodo == "2020-03", "d_covid"].item() == 1
    assert oro.loc[oro.periodo == "2017-05", "d_oferta_2017"].item() == 0 and oro.loc[oro.periodo == "2017-06", "d_oferta_2017"].item() == 1


def test_variables_adicionales_segun_sus_formulas(tmp_path):
    oro = _oro(tmp_path, filas_manzanillo()).iloc[0]
    assert oro.pct_cuartos_no_residentes == pytest.approx(100 * (10 + 40 + 60 + 80) / 570, abs=1e-6)
    assert oro.estadia_promedio == pytest.approx(oro.turistas_noche / oro.llegadas_turistas, abs=1e-6)
    assert oro.densidad_ocupacion == pytest.approx(oro.turistas_noche / oro.cuartos_ocupados, abs=1e-6)


def test_la_marca_de_atipicos_es_solo_diagnostico_y_no_elimina_filas(tmp_path):
    filas = filas_manzanillo()
    for f in filas:  # un mes extremo (como COVID): casi sin ocupación
        if (f[0], f[1]) == (2020, "04"):
            f[7], f[8] = 0, 1
    oro = _oro(tmp_path, filas)
    assert len(oro) == 108 and oro.loc[oro.periodo == "2020-04", "diag_atipico_iqr"].item() == 1  # se marca, no se borra


def test_mes_sin_las_4_categorias_es_un_error_controlado(tmp_path):
    filas = [f for f in filas_manzanillo() if not (f[0] == 2020 and f[1] == "05" and f[5] == "4 estrellas")]
    with pytest.raises(ErrorPuertaCalidad) as e:
        _oro(tmp_path, filas)
    assert e.value.regla == "ORO" and "4 categorías" in e.value.mensaje


def test_serie_incompleta_no_produce_oro(tmp_path):
    filas = [f for f in filas_manzanillo() if f[0] != 2024]
    with pytest.raises(ErrorPuertaCalidad) as e:
        _oro(tmp_path, filas)
    assert "108" in e.value.mensaje


def test_duplicados_en_bronce_no_duplican_totales(tmp_path):
    base = _oro(tmp_path / "a", filas_manzanillo())
    filas = filas_manzanillo()
    filas.append(list(filas[10]))  # misma clave repetida
    dup = _oro(tmp_path / "b", filas)
    pd.testing.assert_series_equal(base.cuartos_disponibles, dup.cuartos_disponibles)


def test_validacion_detecta_una_ocupacion_que_no_coincide_con_la_formula(tmp_path):
    oro = _oro(tmp_path, filas_manzanillo())
    oro.loc[5, "ocupacion_pct"] = oro.loc[5, "ocupacion_pct"] + 3
    with pytest.raises(ErrorPuertaCalidad):
        o.validar_oro_mensual(oro)


def test_oferta_denue_es_agregada_sin_coordenadas_ni_clee(tmp_path):
    escribir_denue(tmp_path, "2026-11-10", "2026-11-10T15:00:00+00:00",
                   [registro_denue(i, Estrato="0 a 5 personas") for i in range(3)] + [registro_denue(5), registro_denue(6)])
    plata = procesar_capturas(tmp_path / "data" / "bronce" / "denue", Cuarentena(AHORA))
    oferta = o.construir_oferta_hospedaje(plata)
    assert list(oferta.columns) == o.COLUMNAS_OFERTA
    assert not ({"clee", "id", "latitud", "longitud", "ageb", "manzana"} & set(oferta.columns))
    assert oferta.establecimientos.sum() == 5 and set(oferta.estrato) == {"0 a 5 personas", "6 a 10 personas"}
    assert oferta.loc[oferta.estrato == "6 a 10 personas", "personal_min_total"].item() == 12


def test_el_diccionario_documenta_todas_las_columnas_de_oro():
    d = o.diccionario_df()
    for dataset, columnas in (("manzanillo_ocupacion_mensual", o.COLUMNAS_ORO), ("manzanillo_oferta_hospedaje", o.COLUMNAS_OFERTA)):
        assert set(columnas) == set(d[d.dataset == dataset].columna), dataset
    assert (d.definicion.str.len() > 10).all() and not d.isna().any().any()
