"""Plata y puerta de calidad (reglas R-D01..R-D08 y R-E01..R-E06) con datos SINTÉTICOS; ver test_pipeline_real.py."""
import json

import pandas as pd
import pytest

from pipeline.calidad.cuarentena import Cuarentena, ErrorPuertaCalidad
from pipeline.plata_datatur import procesar_base70
from pipeline.plata_denue import estrato_a_rango, procesar_capturas
from tests.pipeline_helpers import escribir_base70, escribir_denue, filas_manzanillo, registro_denue

AHORA = "2026-11-13T00:00:00+00:00"


def _base70(tmp_path, filas, **kw):
    ruta = escribir_base70(tmp_path, filas, **kw)
    c = Cuarentena(AHORA)
    out, sha = procesar_base70(ruta, c)
    return out, c, sha


def _fila(**cambios):
    f = dict(zip(["anio", "mes", "tipo_centro", "subtipo_centro", "centro", "categoria", "cuartos_disponibles",
                  "cuartos_ocupados_no_residentes", "cuartos_ocupados_residentes", "llegada_turistas_no_residentes",
                  "llegada_turistas_residentes", "turistas_noche_no_residentes", "turistas_noche_residentes"],
                 [2020, "03", "Ciudades", "Fronterizas", "Mexicali", "5 estrellas", 1000, 100, 200, 10, 20, 30, 40]))
    f.update(cambios)
    return list(f.values())


def test_esquema_tipos_y_procedencia_de_la_plata(tmp_path):
    out, c, sha = _base70(tmp_path, filas_manzanillo())
    assert list(out.columns)[:5] == ["periodo", "centro", "tipo_centro", "subtipo_centro", "categoria"]
    assert out.cuartos_disponibles.dtype == "Int64" and (out.cuartos_disponibles > 0).all()
    assert out.periodo.str.fullmatch(r"\d{4}-\d{2}").all()
    assert (out.sha256_bronce == sha).all() and out.fila_origen.is_unique and out.fila_origen.min() == 2
    r = c.resumen()["fuentes"]["datatur_base70"]
    assert r["leidos"] == len(out) and r["rechazados"] == 0 and r["aceptados"] == len(out)


def test_r_d01_esquema_distinto_detiene_el_lote(tmp_path):
    with pytest.raises(ErrorPuertaCalidad) as e:
        _base70(tmp_path, filas_manzanillo(), modificar=lambda t: t.replace("cuartos_disponibles", "cuartos_libres", 1))
    assert e.value.regla == "R-D01"


def test_integridad_del_bronce_alterado_detiene_el_lote(tmp_path):
    ruta = escribir_base70(tmp_path, filas_manzanillo())
    ruta.write_bytes(ruta.read_bytes() + b"2016\t01\n")  # alterado después de su ficha
    with pytest.raises(ErrorPuertaCalidad) as e:
        procesar_base70(ruta, Cuarentena(AHORA))
    assert e.value.regla == "INTEGRIDAD"


def test_r_d02_fecha_invalida_a_cuarentena(tmp_path):
    out, c, _ = _base70(tmp_path, [_fila(mes="13"), _fila(anio=2031), _fila(anio="20x6"), _fila()])
    r = c.resumen()["fuentes"]["datatur_base70"]
    assert r["rechazos_por_regla"]["R-D02"] == 3 and len(out) == 1 and r["leidos"] == 4


def test_r_d03_duplicados_conservan_la_primera_aparicion(tmp_path):
    out, c, _ = _base70(tmp_path, [_fila(), _fila(cuartos_disponibles=999)])
    r = c.resumen()["fuentes"]["datatur_base70"]
    assert r["rechazos_por_regla"] == {"R-D03": 1} and len(out) == 1 and int(out.cuartos_disponibles.iloc[0]) == 1000


@pytest.mark.parametrize("campo,valor", [("cuartos_ocupados_residentes", -5), ("cuartos_disponibles", "abc"),
                                         ("llegada_turistas_residentes", 1.5), ("cuartos_ocupados_no_residentes", None)])
def test_r_d04_conteos_invalidos_o_vacios_obligatorios(tmp_path, campo, valor):
    out, c, _ = _base70(tmp_path, [_fila(**{campo: valor})])
    assert c.resumen()["fuentes"]["datatur_base70"]["rechazos_por_regla"].get("R-D04") == 1 and out.empty


def test_r_d05_y_r_d06_rangos_y_coherencia(tmp_path):
    out, c, _ = _base70(tmp_path, [_fila(cuartos_disponibles=0, cuartos_ocupados_residentes=0, cuartos_ocupados_no_residentes=0),
                           _fila(mes="04", cuartos_ocupados_residentes=950), _fila(mes="05")])
    r = c.resumen()["fuentes"]["datatur_base70"]["rechazos_por_regla"]
    assert r == {"R-D05": 1, "R-D06": 1} and len(out) == 1


def test_r_d07_faltante_de_turistas_noche_se_marca_y_no_se_imputa(tmp_path):
    out, c, _ = _base70(tmp_path, [_fila(turistas_noche_residentes=None), _fila(mes="04")])
    assert len(out) == 2 and out.faltante_turistas_noche.tolist() == [True, False]
    assert pd.isna(out.turistas_noche_residentes.iloc[0])  # no se imputó
    assert c.resumen()["fuentes"]["datatur_base70"]["marcados"]["R-D07_faltante_turistas_noche"] == 1


def test_r_d08_cobertura_incompleta_es_informativa(tmp_path):
    out, c, _ = _base70(tmp_path, filas_manzanillo() + [_fila()])
    info = c.resumen()["informativo"]["datatur_base70"]["centros_con_menos_periodos_que_el_maximo"]
    assert info == {"Mexicali": 1} and len(out) == len(filas_manzanillo()) + 1  # no rechaza filas


def test_nada_se_pierde_en_silencio_leidos_igual_aceptados_mas_rechazados(tmp_path):
    filas = filas_manzanillo() + [_fila(mes="13"), _fila(cuartos_disponibles=0), _fila(mes="04", turistas_noche_residentes=None)]
    out, c, _ = _base70(tmp_path, filas)
    r = c.resumen()["fuentes"]["datatur_base70"]
    assert r["leidos"] == len(filas) == r["aceptados"] + r["rechazados"] and r["aceptados"] == len(out)


# ------------------------------------------------------------------ DENUE
def _denue(tmp_path, capturas):
    c = Cuarentena(AHORA)
    for carpeta, utc, regs, *extra in capturas:
        escribir_denue(tmp_path, carpeta, utc, regs, *extra)
    out = procesar_capturas(tmp_path / "data" / "bronce" / "denue", c)
    return out, c


def test_denue_plata_esquema_y_agregado_privado(tmp_path):
    out, c = _denue(tmp_path, [("2026-11-10", "2026-11-10T15:00:00+00:00", [registro_denue(i) for i in range(3)])])
    assert len(out) == 3 and out.clee.is_unique
    assert out.fecha_captura_local.eq("2026-11-10").all() and out.municipio_clave.eq("06007").all()
    assert {"nombre", "razon_social", "telefono", "calle"}.isdisjoint(out.columns)
    assert out.personal_min.tolist() == [6, 6, 6] and out.personal_max.tolist() == [10, 10, 10]


def test_denue_fecha_local_no_es_utc(tmp_path):
    out, _ = _denue(tmp_path, [("2026-11-09", "2026-11-10T03:00:00+00:00", [registro_denue(1)])])  # 21:00 del día 9 en México
    assert out.fecha_captura_local.iloc[0] == "2026-11-09"


def test_denue_una_captura_por_dia_se_conserva_la_ultima_y_se_cuenta(tmp_path):
    out, c = _denue(tmp_path, [("2026-11-10", "2026-11-10T15:00:00+00:00", [registro_denue(i) for i in range(3)]),
                              ("2026-11-10", "2026-11-10T20:00:00+00:00", [registro_denue(i) for i in range(3)])])
    assert len(out) == 3 and out.capturas_del_dia.eq(2).all()
    assert c.resumen()["fuentes"]["denue_establecimientos"]["marcados"]["registros_aceptados_reemplazados_por_captura_posterior_del_dia"] == 3


def test_denue_reglas_por_fila_a_cuarentena(tmp_path):
    regs = [registro_denue(0), registro_denue(1, CLEE=""), registro_denue(2, AreaGeo="060010001"),
            registro_denue(3, Latitud="45.0"), registro_denue(4, Fecha_Alta="2031-01"), registro_denue(5, Fecha_Alta="marzo"),
            registro_denue(6, CLASE_ACTIVIDAD_ID="722511"), registro_denue(7), registro_denue(7, Id="9999")]
    out, c = _denue(tmp_path, [("2026-11-10", "2026-11-10T15:00:00+00:00", regs, len(regs) - 1)])
    r = c.resumen()["fuentes"]["denue_establecimientos"]
    assert r["rechazos_por_regla"] == {"R-E01": 2, "R-E03": 2, "R-E04": 1, "R-E06": 2}
    assert len(out) == 2 and r["leidos"] == len(regs) == r["aceptados"] + r["rechazados"]


def test_r_e02_completitud_fuera_de_rango_rechaza_el_lote(tmp_path):
    with pytest.raises(ErrorPuertaCalidad) as e:  # solo hay un lote y se rechaza: no hay salida confiable
        _denue(tmp_path, [("2026-11-10", "2026-11-10T15:00:00+00:00", [registro_denue(i) for i in range(5)], 100)])
    assert e.value.regla == "R-E02"


def test_r_e02_un_lote_malo_no_arrastra_a_los_buenos(tmp_path):
    out, c = _denue(tmp_path, [("2026-11-10", "2026-11-10T15:00:00+00:00", [registro_denue(i) for i in range(5)], 100),
                              ("2026-11-11", "2026-11-11T15:00:00+00:00", [registro_denue(i) for i in range(5)])])
    assert len(out) == 5 and out.fecha_captura_local.eq("2026-11-11").all()
    res = c.resumen()
    assert res["lotes_rechazados"][0]["regla_id"] == "R-E02"
    f = res["fuentes"]["denue_establecimientos"]
    assert f["leidos"] == 10 == f["aceptados"] + f["rechazados"]


def test_r_e05_campo_excluido_por_privacidad_es_incidente_y_detiene_todo(tmp_path):
    with pytest.raises(ErrorPuertaCalidad) as e:
        _denue(tmp_path, [("2026-11-10", "2026-11-10T15:00:00+00:00", [registro_denue(0, Telefono="3140000000")])])
    assert e.value.regla == "R-E05" and "Telefono" in e.value.mensaje


def test_denue_integridad_alterada_detiene(tmp_path):
    ruta = escribir_denue(tmp_path, "2026-11-10", "2026-11-10T15:00:00+00:00", [registro_denue(0)])
    ruta.write_text(json.dumps([registro_denue(0, Id="manipulado")]), encoding="utf-8")
    with pytest.raises(ErrorPuertaCalidad) as e:
        procesar_capturas(tmp_path / "data" / "bronce" / "denue", Cuarentena(AHORA))
    assert e.value.regla == "INTEGRIDAD"


@pytest.mark.parametrize("texto,esperado", [("0 a 5 personas", (0, 5)), ("101 a 250 personas", (101, 250)),
                                            ("251 y más personas", (251, None)), ("", (None, None))])
def test_estrato_a_rango(texto, esperado):
    assert estrato_a_rango(texto) == esperado
