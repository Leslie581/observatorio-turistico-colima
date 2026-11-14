"""Fiabilidad y disponibilidad (pipeline/fiabilidad.py).

Los casos con bitácoras armadas a mano son SINTÉTICOS y lo declaran: validan la lógica de cálculo, no son resultados de operación.
La prueba final usa los 8 primeros registros REALES de calidad/bitacora_capturas.jsonl (historia ya cerrada), de modo que no
cambia cuando el bot agrega ejecuciones nuevas.
"""
import json
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from pipeline import fiabilidad as f

RAIZ = Path(__file__).resolve().parent.parent
BASE = datetime(2026, 1, 1, 13, 30, tzinfo=timezone.utc)


def reg(horas, resultado="exito", disparador="schedule", dur_s=3.0, error=None):
    """SINTÉTICO: un registro de bitácora que empieza ``horas`` después de BASE."""
    ini = BASE + timedelta(hours=horas)
    return {"ejecucion": ini.strftime("%Y%m%dT%H%M%SZ"), "disparador": disparador, "resultado": resultado,
            "inicio_utc": ini.isoformat(), "fin_utc": (ini + timedelta(seconds=dur_s)).isoformat(),
            "fecha_local": ini.date().isoformat(), "error": error}


def test_sin_fallas_tasa_100_y_sin_incidentes_ni_mttr():
    r = f.calcular([reg(0), reg(24), reg(48)])
    assert r["tasa_exito"]["valor"] == 1.0 and r["incidentes"]["total"] == 0
    assert r["mttr"]["estimable"] is False and r["mtbf"]["estimable"] is False and r["disponibilidad_A"]["estimable"] is False


def test_un_incidente_da_mttr_pero_no_mtbf_ni_disponibilidad():
    filas = [reg(0, "fallo", error="sin_token"), reg(0.1), reg(24), reg(48)]  # el éxito empieza 6 min después del fallo
    r = f.calcular(filas)
    assert r["incidentes"]["total"] == 1 and r["incidentes"]["cerrados"] == 1
    # reparación = fin del éxito (inicio + 3 s) − inicio del fallo = 360 s + 3 s
    assert r["mttr"] == {"estimable": True, "segundos": 363.0, "incidentes_cerrados": 1}
    assert r["mtbf"]["estimable"] is False and "al menos 2" in r["mtbf"]["motivo"]
    assert r["mtbf"]["tiempo_sin_fallas_desde_la_ultima_recuperacion_s"] > 0 and "CENSURADO" in r["mtbf"]["nota_tiempo_sin_fallas"]
    assert r["disponibilidad_A"]["estimable"] is False


def test_dos_incidentes_permiten_mtbf_y_disponibilidad_con_la_formula():
    filas = [reg(0), reg(24, "fallo"), reg(24.5), reg(72), reg(96, "fallo"), reg(96.25), reg(120)]
    r = f.calcular(filas)
    assert r["incidentes"]["total"] == 2 and r["incidentes"]["cerrados"] == 2
    reparaciones = [(0.5 * 3600) + 3.0, (0.25 * 3600) + 3.0]  # inicio del fallo -> fin del éxito siguiente
    mttr = sum(reparaciones) / 2
    assert r["mttr"]["segundos"] == pytest.approx(mttr, abs=0.2)
    observado = (120 * 3600 + 3.0)
    mtbf = (observado - sum(reparaciones)) / 2
    assert r["mtbf"]["estimable"] is True and r["mtbf"]["segundos"] == pytest.approx(mtbf, abs=0.2)
    assert r["disponibilidad_A"]["valor"] == pytest.approx(mtbf / (mtbf + mttr), abs=1e-5)


def test_fallos_consecutivos_forman_un_solo_incidente():
    r = f.calcular([reg(0), reg(24, "fallo"), reg(26, "fallo"), reg(28, "fallo"), reg(30)])
    assert r["incidentes"]["total"] == 1 and r["incidentes"]["detalle"][0]["fallos_consecutivos"] == 3
    assert r["incidentes"]["detalle"][0]["reparacion_s"] == pytest.approx(6 * 3600 + 3.0)


def test_incidente_sin_recuperacion_queda_abierto_y_no_entra_al_mttr():
    r = f.calcular([reg(0), reg(24), reg(48, "fallo")])
    assert r["incidentes"] == {"total": 1, "cerrados": 0, "abiertos": 1, "detalle": r["incidentes"]["detalle"]}
    assert r["mttr"]["estimable"] is False and r["incidentes"]["detalle"][0]["recuperacion_utc"] is None


def test_las_omitidas_por_duplicado_no_cuentan_para_la_tasa():
    r = f.calcular([reg(0), reg(1, "omitida_duplicada"), reg(2, "omitida_duplicada"), reg(24, "fallo")])
    assert r["ejecuciones"]["validas"] == 2 and r["ejecuciones"]["omitidas_duplicadas_excluidas"] == 2
    assert r["tasa_exito"]["valor"] == 0.5 and r["tasa_exito"]["cumple_objetivo_en_lo_observado"] is False


def test_la_ventana_de_7_dias_se_declara_cumplida_o_no():
    corta = f.calcular([reg(0), reg(24), reg(48)])
    assert corta["ventana"]["cumple_dias_requeridos"] is False and corta["tasa_exito"]["evaluable_como_se_definio_O1"] is False
    assert any("rúbrica pide 7" in a for a in corta["avisos"])
    larga = f.calcular([reg(24 * d) for d in range(0, 9)])  # 8 días + 3 s
    assert larga["ventana"]["cumple_dias_requeridos"] is True and larga["tasa_exito"]["evaluable_como_se_definio_O1"] is True


def test_puntualidad_mide_el_retraso_frente_a_la_hora_programada():
    # BASE es 13:30 UTC; el cron es 13:17 -> 13 minutos de retraso
    r = f.calcular([reg(0, disparador="schedule"), reg(24, disparador="workflow_dispatch")])
    assert [x["retraso_min"] for x in r["puntualidad_schedule"]["retrasos"]] == [13.0]


def test_sin_ejecuciones_validas_se_informa_sin_datos_y_no_se_inventa_nada():
    assert f.calcular([])["estado"] == "sin_datos"
    assert f.calcular([reg(0, "omitida_duplicada")])["estado"] == "sin_datos"


def test_no_modifica_la_entrada_y_es_determinista():
    filas = [reg(0), reg(24, "fallo"), reg(25)]
    copia = deepcopy(filas)
    a, b = f.calcular(filas), f.calcular(filas)
    assert filas == copia and a == b and json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_con_la_bitacora_real_primeros_8_registros(tmp_path):
    """REAL: historia cerrada del 2026-11-10 al 2026-11-12. Los registros posteriores los agrega el bot y no afectan este corte."""
    lineas = (RAIZ / "calidad" / "bitacora_capturas.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lineas) >= 8
    corte = tmp_path / "bitacora.jsonl"
    corte.write_text("\n".join(lineas[:8]) + "\n", encoding="utf-8")
    r = f.informe(corte)
    assert r["ejecuciones"] == {"validas": 6, "exitosas": 5, "fallidas": 1, "omitidas_duplicadas_excluidas": 2,
                                "programadas_schedule": 3, "programadas_exitosas": 3}
    assert r["tasa_exito"]["valor"] == pytest.approx(0.8333, abs=1e-4) and r["tasa_exito"]["cumple_objetivo_en_lo_observado"] is False
    assert r["incidentes"]["total"] == 1 and r["mttr"]["segundos"] == 268.0
    assert r["ventana"]["dias"] == pytest.approx(2.84, abs=0.005) and r["ventana"]["cumple_dias_requeridos"] is False
    assert r["mtbf"]["estimable"] is False and r["disponibilidad_A"]["estimable"] is False
    assert r["cobertura_diaria_descriptiva"] == {"dias_con_ejecucion": 4, "dias_con_captura_exitosa": 4}


def test_la_tasa_coincide_con_la_del_verificador_de_e0():
    """Una sola definición de tasa de éxito en el proyecto (O1): la de verificar_e0.disponibilidad."""
    from pipeline.verificar_e0 import disponibilidad

    bit = RAIZ / "calidad" / "bitacora_capturas.jsonl"
    nuevo, viejo = f.informe(bit), disponibilidad(bit)
    assert nuevo["tasa_exito"]["valor"] == viejo["tasa_exito"] and nuevo["ejecuciones"]["validas"] == viejo["ejecuciones"]


# ---------------------------------------------------------------- estimación EXPLORATORIA del MTBF (con un solo incidente)
def test_cuantiles_ji_cuadrada_en_python_puro_coinciden_con_valores_de_tabla():
    assert f.ji2_cuantil_gl_par(0.05, 2) == pytest.approx(0.102587, abs=1e-6)
    assert f.ji2_cuantil_gl_par(0.95, 4) == pytest.approx(9.487729, abs=1e-6)
    assert f.ji2_cuantil_gl_par(0.5, 2) == pytest.approx(1.386294, abs=1e-6)  # mediana de una exponencial de media 2: 2 ln 2


def test_cuantiles_y_cp_coinciden_con_scipy_si_esta_instalado():
    stats = pytest.importorskip("scipy.stats")
    for gl in (2, 4, 6, 10):
        for p in (0.025, 0.05, 0.5, 0.95, 0.975):
            assert f.ji2_cuantil_gl_par(p, gl) == pytest.approx(stats.chi2.ppf(p, gl), rel=1e-9)
    for x, n in ((5, 6), (0, 6), (6, 6), (3, 10)):
        lo, hi = f.intervalo_clopper_pearson(x, n, 0.95)
        assert lo == pytest.approx(0.0 if x == 0 else stats.beta.ppf(0.025, x, n - x + 1), abs=1e-9)
        assert hi == pytest.approx(1.0 if x == n else stats.beta.ppf(0.975, x + 1, n - x), abs=1e-9)


def test_intervalo_de_epstein_con_un_fallo_reproduce_los_valores_calculados_aparte():
    lo, hi = f.intervalo_mtbf_epstein(245075.0, 1, 0.90)  # T real de la bitácora (ventana 245,343 s menos 268 s)
    assert lo / 3600 == pytest.approx(14.350, abs=0.001) and hi / 3600 == pytest.approx(1327.2, abs=0.1)
    with pytest.raises(ValueError):
        f.intervalo_mtbf_epstein(100.0, 0)


def test_clopper_pearson_casos_limite_y_el_valor_de_5_de_6():
    assert f.intervalo_clopper_pearson(5, 6) == pytest.approx((0.3588, 0.9958), abs=1e-4)
    assert f.intervalo_clopper_pearson(0, 6)[0] == 0.0 and f.intervalo_clopper_pearson(6, 6)[1] == 1.0


def test_estimacion_exploratoria_se_declara_exploratoria_y_con_intervalo():
    filas = [reg(0, "fallo", error="sin_token"), reg(0.1), reg(24), reg(48), reg(72)]  # 1 incidente
    e = f.calcular(filas)["estimacion_exploratoria"]
    assert e["estado"].startswith("EXPLORATORIA") and e["fallas_r"] == 1
    assert e["intervalo_90_mtbf_horas"][0] < e["mtbf_horas"] < e["intervalo_90_mtbf_horas"][1]
    assert e["disponibilidad_A"]["con_mtbf_cota_inferior_90"] < e["disponibilidad_A"]["punto"] < e["disponibilidad_A"]["con_mtbf_cota_superior_90"]
    assert e["supuestos_y_limites"] and "no sustituye" in e["estado"]


def test_con_un_incidente_A_puntual_es_igual_a_la_disponibilidad_observada_por_tiempo():
    """Equivalencia algebraica: T/(T+R) = (W−R)/W; el estimador solo aporta el intervalo."""
    e = f.calcular([reg(0, "fallo"), reg(0.1), reg(24), reg(48)])["estimacion_exploratoria"]
    assert e["disponibilidad_A"]["punto"] == pytest.approx(e["disponibilidad_observada_por_tiempo"], abs=1e-5)


def test_sin_incidentes_cerrados_no_hay_estimacion_y_no_se_cambia_el_criterio_interno():
    assert f.calcular([reg(0), reg(24), reg(48)])["estimacion_exploratoria"] is None
    assert f.calcular([reg(0), reg(24), reg(48, "fallo")])["estimacion_exploratoria"] is None  # incidente abierto: sin recuperación
    r = f.calcular([reg(0, "fallo"), reg(0.1), reg(24)])
    assert r["mtbf"]["estimable"] is False and r["disponibilidad_A"]["estimable"] is False  # el criterio interno de 2 incidentes no cambia


def test_dos_incidentes_usan_r_igual_a_2_en_la_estimacion():
    e = f.calcular([reg(0), reg(24, "fallo"), reg(24.5), reg(72), reg(96, "fallo"), reg(96.25), reg(120)])["estimacion_exploratoria"]
    assert e["fallas_r"] == 2 and e["intervalo_90_mtbf_horas"][0] < e["mtbf_horas"] < e["intervalo_90_mtbf_horas"][1]


def test_estimacion_con_los_8_primeros_registros_reales(tmp_path):
    """REAL (corte fijo): MTBF 68.076 h, IC 90 % 14.35 h a 1327.2 h, A 0.99891 (0.99484 con la cota inferior); tasa 5/6 con su IC."""
    lineas = (RAIZ / "calidad" / "bitacora_capturas.jsonl").read_text(encoding="utf-8").splitlines()
    corte = tmp_path / "bitacora.jsonl"
    corte.write_text("\n".join(lineas[:8]) + "\n", encoding="utf-8")
    r = f.informe(corte)
    e = r["estimacion_exploratoria"]
    assert e["ventana_s"] == 245343.0 and e["reparacion_total_s"] == 268.0 and e["tiempo_operativo_T_s"] == 245075.0 and e["fallas_r"] == 1
    assert e["mtbf_horas"] == pytest.approx(68.076, abs=0.001) and e["intervalo_90_mtbf_horas"] == pytest.approx([14.35, 1327.2], abs=0.1)
    assert e["disponibilidad_A"]["punto"] == pytest.approx(0.99891, abs=1e-5) and e["disponibilidad_A"]["con_mtbf_cota_inferior_90"] == pytest.approx(0.99484, abs=1e-5)
    assert e["disponibilidad_observada_por_tiempo"] == pytest.approx(0.99891, abs=1e-5)
    assert r["tasa_exito"]["intervalo_95_clopper_pearson"] == pytest.approx([0.3588, 0.9958], abs=1e-4)
    assert r["tasa_exito"]["el_intervalo_incluye_el_objetivo"] is True and r["tasa_exito"]["valor"] == pytest.approx(0.8333, abs=1e-4)
    assert r["mtbf"]["estimable"] is False and r["disponibilidad_A"]["estimable"] is False  # la medición con el criterio interno no cambia


def test_el_nucleo_de_fiabilidad_no_depende_de_scipy():
    """La captura diaria solo instala requirements.txt; el módulo debe funcionar sin scipy."""
    codigo = (RAIZ / "pipeline" / "fiabilidad.py").read_text(encoding="utf-8")
    assert "import scipy" not in codigo and "from scipy" not in codigo
