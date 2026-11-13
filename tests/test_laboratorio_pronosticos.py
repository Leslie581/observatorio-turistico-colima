"""Pruebas del laboratorio de pronósticos E1 (integrante B).

Dos grupos:
* Pruebas con **datos simulados** (series sintéticas generadas aquí con semilla fija): verifican la
  lógica de las funciones. No son evidencia operativa ni resultados del proyecto.
* Pruebas marcadas ``datos``: usan el bronce real de Base70 a través de la derivación de
  referencia del contrato §7 y comprueban las cifras fijadas en el contrato 1.0.0.

Requieren statsmodels y scipy, que **todavía no están en requirements.txt** (lo administra la
integrante A). Sin ellas:
* por defecto el módulo se omite con un motivo explícito ("PRUEBAS DE PRONÓSTICOS NO EJECUTADAS"),
  visible con ``pytest -rs`` (así se ejecuta en el workflow);
* con ``TDL_EXIGIR_PRONOSTICOS=1`` la falta de dependencias es un **error**, no una omisión. El CI
  de E1 debe instalar las dependencias y fijar esa variable para que estas pruebas se ejecuten
  realmente (docs/E1/pronostico.md §8).
No se hace fallar con la sola variable ``CI``: el workflow de captura diaria ejecuta pytest antes
de capturar y una falla por dependencias detendría la captura.
"""
from __future__ import annotations

import importlib.util
import os

import numpy as np
import pandas as pd
import pytest

_FALTAN = [m for m in ("statsmodels", "scipy") if importlib.util.find_spec(m) is None]
if _FALTAN:
    _MOTIVO = (f"PRUEBAS DE PRONÓSTICOS NO EJECUTADAS: faltan {', '.join(_FALTAN)} "
               "(instalar requirements-lab.txt)")
    if os.environ.get("TDL_EXIGIR_PRONOSTICOS") == "1":
        raise ImportError(_MOTIVO + " y TDL_EXIGIR_PRONOSTICOS=1 exige ejecutarlas")
    pytest.skip(_MOTIVO, allow_module_level=True)

# E402: las importaciones van después de la comprobación de dependencias a propósito.
from laboratorio.pronosticos import datos  # noqa: E402
from laboratorio.pronosticos import estadistica as est  # noqa: E402
from laboratorio.pronosticos import modelos as mod  # noqa: E402

from .conftest import BRONCE_BASE70  # noqa: E402

hay_bronce = pytest.mark.skipif(not BRONCE_BASE70.exists(), reason="sin data/bronce de Base70")


# ----------------------------------------------------------------------------- simulados
def _indice(n=108, inicio="2016-01"):
    return pd.period_range(inicio, periods=n, freq="M")


def _serie_estacional(n=108, semilla=0, ruido=1.0):
    """SIMULADA: nivel 50 + ciclo anual de amplitud 8 + ruido gaussiano."""
    rng = np.random.default_rng(semilla)
    t = np.arange(n)
    y = 50 + 8 * np.sin(2 * np.pi * t / 12) + rng.normal(0, ruido, n)
    return pd.Series(y, index=_indice(n), name="ocupacion_pct")


def test_metricas_valores_conocidos():
    m = mod.metricas([50, 40], [45, 44])
    assert m["MAE"] == pytest.approx(4.5)
    assert m["RMSE"] == pytest.approx(np.sqrt((25 + 16) / 2))
    assert m["MAPE"] == pytest.approx(100 * (5 / 50 + 4 / 40) / 2)
    assert m["sesgo_medio"] == pytest.approx(0.5)


def test_metricas_rechaza_cero_y_longitudes_distintas():
    with pytest.raises(ValueError):
        mod.metricas([0, 10], [1, 10])
    with pytest.raises(ValueError):
        mod.metricas([1, 2, 3], [1, 2])


def test_partir_respeta_corte_2023_12():
    s = _serie_estacional()
    ent, pru = datos.partir(s)
    assert len(ent) == 96 and len(pru) == 12
    assert ent.index[-1] == pd.Period("2023-12", "M") and pru.index[0] == pd.Period("2024-01", "M")
    with pytest.raises(ValueError):
        datos.partir(s.iloc[:-1])  # prueba incompleta


def test_transformar_diferencias():
    s = pd.Series(np.arange(30, dtype=float) ** 2, index=_indice(30))
    assert len(est.transformar(s, d=1, D=1)) == 30 - 13
    assert est.transformar(s, d=1).iloc[0] == pytest.approx(1.0)
    assert est.transformar(s, D=1).iloc[0] == pytest.approx(144.0)


def test_elegir_diferenciacion_prefiere_la_menor_suficiente():
    filas = [  # tabla sintética con el mismo formato que pruebas_estacionariedad
        {"transformacion": "niveles", "d": 0, "D": 0, "adf_p": 0.5, "kpss_p": 0.01},
        {"transformacion": "D=1", "d": 0, "D": 1, "adf_p": 0.01, "kpss_p": 0.10},
        {"transformacion": "d=1", "d": 1, "D": 0, "adf_p": 0.01, "kpss_p": 0.10},
        {"transformacion": "d=1 y D=1", "d": 1, "D": 1, "adf_p": 0.001, "kpss_p": 0.10},
    ]
    t = pd.DataFrame(filas)
    t["adf_rechaza_raiz_unitaria"] = t.adf_p < 0.05
    t["kpss_rechaza_estacionariedad"] = t.kpss_p < 0.05
    assert est.elegir_diferenciacion(t)[:2] == (0, 1)
    t.loc[1, "adf_rechaza_raiz_unitaria"] = False
    assert est.elegir_diferenciacion(t)[:2] == (1, 0)


def test_pruebas_estacionariedad_detectan_paseo_aleatorio():
    """La diferencia de un paseo aleatorio es ruido blanco: ADF debe rechazar con claridad y su
    p-valor debe ser menor que el de los niveles (una sola realización en niveles puede rechazar
    por azar, así que no se exige un resultado binario sobre los niveles)."""
    rng = np.random.default_rng(1)
    s = pd.Series(np.cumsum(rng.normal(size=120)), index=_indice(120))  # SIMULADO
    t = est.pruebas_estacionariedad(s)
    niveles = t[t.transformacion == "niveles"].iloc[0]
    d1 = t[(t.d == 1) & (t.D == 0)].iloc[0]
    assert d1.adf_p < 0.01 and d1.adf_rechaza_raiz_unitaria
    assert niveles.adf_p > d1.adf_p
    assert set(t.transformacion) == {"niveles", "diferencia regular (d=1)",
                                     "diferencia estacional (D=1)", "d=1 y D=1"}


def test_autocorrelaciones_detecta_estacionalidad():
    ac = est.autocorrelaciones(_serie_estacional(ruido=0.5), rezagos=24)
    assert ac.loc[ac.rezago == 12, "acf"].iloc[0] > 0.5
    assert ac.loc[ac.rezago == 6, "acf"].iloc[0] < -0.5


def test_correlacion_cruzada_encuentra_rezago_y_bloquea_contemporanea():
    rng = np.random.default_rng(2)
    x = pd.Series(rng.normal(size=96), index=_indice(96))  # SIMULADO: y_t = x_{t-2} + ruido
    y = (x.shift(2) + rng.normal(0, 0.3, 96)).bfill()
    t = est.correlacion_cruzada(y, x, d=0, D=0, rezagos=6)
    assert int(t.loc[t.r.idxmax(), "rezago"]) == 2
    assert not t.loc[t.rezago == 0, "utilizable_para_pronostico"].iloc[0]
    assert t.loc[t.rezago >= 1, "utilizable_para_pronostico"].all()


def test_correlacion_cruzada_excluye_covid():
    s = _serie_estacional(96)
    t_todo = est.correlacion_cruzada(s, s * 0.5, d=1, D=1, rezagos=1)
    t_sin = est.correlacion_cruzada(s, s * 0.5, d=1, D=1, rezagos=1, excluir_covid=True)
    assert (t_sin.n < t_todo.n).all()


def _serie_con_tendencia(multiplicativa: bool, n=96):
    """SIMULADA: nivel creciente de 20 a 80; amplitud estacional fija (8) o proporcional al nivel."""
    rng = np.random.default_rng(4)
    t = np.arange(n)
    nivel = 20 + 60 * t / (n - 1)
    estacional = np.sin(2 * np.pi * t / 12)
    y = nivel * (1 + 0.25 * estacional) if multiplicativa else nivel + 8 * estacional
    return pd.Series(y + rng.normal(0, 0.3, n), index=_indice(n))


def test_descomponer_elige_aditiva_con_amplitud_constante():
    r = est.descomponer(_serie_con_tendencia(multiplicativa=False))
    assert r["eleccion"] == "aditiva", r["razon_eleccion"]
    assert r["additive"]["fuerza_estacionalidad"] > 0.9


def test_descomponer_elige_multiplicativa_si_la_amplitud_crece_con_el_nivel():
    r = est.descomponer(_serie_con_tendencia(multiplicativa=True))
    assert r["eleccion"] == "multiplicativa", r["razon_eleccion"]


def test_holt_winters_supera_a_ses_en_serie_estacional():
    s = _serie_estacional()
    ent, pru = datos.partir(s)
    hw, ses = mod.ajustar_holt_winters(ent), mod.ajustar_ses(ent)
    e_hw = mod.metricas(pru, mod.pronostico_ajuste(hw, pru.index).media)["RMSE"]
    e_ses = mod.metricas(pru, mod.pronostico_ajuste(ses, pru.index).media)["RMSE"]
    assert e_hw < e_ses
    assert hw.aicc < ses.aicc


def test_intervalos_de_prediccion_ordenados():
    ent, pru = datos.partir(_serie_estacional())
    for aj in (mod.ajustar_ses(ent), mod.ajustar_holt(ent)):
        p = mod.pronostico_ajuste(aj, pru.index)
        assert list(p.index) == list(pru.index)
        assert (p.li < p.media).all() and (p.media < p.ls).all()


def test_intervalos_simulados_son_reproducibles():
    """ETS(A,A,M) calcula su intervalo por simulación: con semilla fija debe repetirse igual."""
    ent, pru = datos.partir(_serie_estacional())
    aj = mod._mejor_ets(mod._a_timestamp(ent), "Holt-Winters",
                        [("ETS(A,A,M)", {"trend": "add", "seasonal": "mul"})])
    p1 = mod.pronostico_ajuste(aj, pru.index)
    p2 = mod.pronostico_ajuste(aj, pru.index)
    assert np.array_equal(p1.values, p2.values)


def test_sarima_busqueda_acotada_y_reajuste():
    ent, pru = datos.partir(_serie_estacional())
    aj = mod.ajustar_sarima(ent, d=0, D=1, p_max=1, q_max=0, P_max=0, Q_max=1, probar_covid=False)
    assert aj.familia == "SARIMA" and aj.candidatos[0][1] == pytest.approx(aj.aicc)
    p = mod.pronostico_ajuste(aj, pru.index)
    assert mod.metricas(pru, p.media)["RMSE"] < 3
    total = mod.reajustar(aj, pd.concat([ent, pru]))
    assert total.especificacion == aj.especificacion and total.resultado.nobs == 108


def test_ingenuo_estacional():
    ent, _ = datos.partir(_serie_estacional())
    assert np.allclose(mod.ingenuo_estacional(ent, 12), ent.values[-12:])
    with pytest.raises(ValueError):
        mod.ingenuo_estacional(ent, 13)


def test_diagnostico_residuos_ruido_blanco_y_autocorrelacionado():
    rng = np.random.default_rng(3)
    blanco = pd.Series(rng.normal(size=200))  # SIMULADO
    assert mod.diagnosticar_residuos(blanco)["independencia_ok"]
    ar = pd.Series(np.zeros(200))
    for i in range(1, 200):
        ar[i] = 0.8 * ar[i - 1] + rng.normal()
    assert not mod.diagnosticar_residuos(ar)["independencia_ok"]


def test_seleccion_salta_modelo_que_no_supera_ljung_box():
    t = pd.DataFrame([
        {"familia": "A", "RMSE": 2.0, "MAE": 1.5, "independencia_ok": False, "n_parametros": 3},
        {"familia": "B", "RMSE": 2.5, "MAE": 2.0, "independencia_ok": True, "n_parametros": 5},
        {"familia": "C", "RMSE": 2.55, "MAE": 1.9, "independencia_ok": True, "n_parametros": 2},
    ])
    fam, motivo = mod.seleccionar(t)
    assert fam == "C"  # empate (< 0.1 pp) con B y menor MAE
    assert "A tenía menor RMSE" in motivo
    t["independencia_ok"] = False
    assert mod.seleccionar(t)[0] == "A"


def test_exog_covid_es_calendario():
    e = mod.exog_covid(pd.period_range("2020-01", "2024-12", freq="M"))
    assert e.d_covid.sum() == 16 and e.loc["2024"].d_covid.sum() == 0
    assert e.loc["2020-03"].d_covid.iloc[0] == 1 and e.loc["2021-06"].d_covid.iloc[0] == 1
    assert e.loc["2020-02"].d_covid.iloc[0] == 0 and e.loc["2021-07"].d_covid.iloc[0] == 0
    futuro = mod.exog_covid(pd.period_range("2025-01", "2025-12", freq="M"))
    assert futuro.d_covid.sum() == 0


def test_d_covid_no_usa_la_variable_objetivo():
    """El regresor del SARIMA depende solo de las fechas: dos series distintas con el mismo
    índice producen exactamente la misma matriz exógena, en el ajuste y en el pronóstico."""
    cov = datos.indicador_covid(_indice(96)).astype(bool)
    s1 = _serie_estacional(96, semilla=5)  # SIMULADAS, con una caída en la ventana COVID
    s1[cov] -= 20
    s2 = _serie_estacional(96, semilla=6) * 0.5
    s2[cov] -= 10
    kw = {"d": 0, "D": 1, "p_max": 0, "q_max": 0, "P_max": 0, "Q_max": 1}
    a1, a2 = mod.ajustar_sarima(s1, **kw), mod.ajustar_sarima(s2, **kw)
    esperado = datos.indicador_covid(s1.index).astype(float)
    for aj in (a1, a2):
        assert aj.con_covid  # la intervención se elige por AICc
        assert np.array_equal(np.asarray(aj.resultado.model.exog).ravel(), esperado)
    idx_fut = pd.period_range("2024-01", periods=12, freq="M")
    p = mod.pronostico_ajuste(a1, idx_fut)  # usa d_covid = 0 en el horizonte
    assert len(p) == 12 and mod.exog_covid(idx_fut).d_covid.sum() == 0


def test_validar_forma_rechaza_huecos_y_rango():
    df = pd.DataFrame({"ocupacion_pct": np.full(108, 50.0)}, index=_indice())
    datos.validar_forma(df)
    with pytest.raises(ValueError):
        datos.validar_forma(df.drop(df.index[5]))
    malo = df.copy()
    malo.iloc[3, 0] = 120
    with pytest.raises(ValueError):
        datos.validar_forma(malo)


# ----------------------------------------------------------------------------- datos reales
@pytest.fixture(scope="module")
def referencia():
    return datos.derivar_referencia(BRONCE_BASE70)


@pytest.mark.datos
@hay_bronce
def test_referencia_coincide_con_cifras_del_contrato(referencia):
    s = referencia.ocupacion_pct
    assert len(s) == 108 and str(s.index[0]) == "2016-01" and str(s.index[-1]) == "2024-12"
    assert round(s.min(), 2) == 1.46 and str(s.idxmin()) == "2020-04"
    assert round(s.max(), 2) == 66.34 and round(s.mean(), 2) == 45.86
    assert referencia.d_covid.sum() == 16
    assert referencia.d_oferta_2017.idxmax() == pd.Period("2017-06", "M")


@pytest.mark.datos
@hay_bronce
def test_comparacion_oro_detecta_diferencias(referencia):
    assert datos.comparar_con_referencia(referencia, referencia)["coincide"]
    alterado = referencia.copy()
    alterado.iloc[50, alterado.columns.get_loc("ocupacion_pct")] += 0.01
    assert not datos.comparar_con_referencia(alterado, referencia)["coincide"]


@pytest.mark.datos
@hay_bronce
def test_carga_oro_simulado_valida_contra_referencia(referencia, tmp_path):
    """Oro SIMULADO a partir de la referencia, válido contra el esquema completo del contrato
    (lo valida también ``pipeline.interfaz`` si existe). Después se altera de forma coherente
    (conteos y cociente) para que supere el esquema y lo detecte el cotejo contra la fuente."""
    ref = referencia
    y = ref.ocupacion_pct
    q1, q3 = y.quantile([0.25, 0.75])
    enteros = ["cuartos_disponibles", "cuartos_ocupados", "cuartos_ocupados_residentes",
               "cuartos_ocupados_no_residentes", "llegadas_turistas", "turistas_noche"]
    oro = pd.DataFrame({
        "periodo": ref.index.astype(str),
        "fecha_inicio": [f"{p}-01" for p in ref.index.astype(str)],
        **{c: ref[c].values for c in ["ocupacion_pct", *enteros, "pct_cuartos_no_residentes",
                                       "estadia_promedio", "densidad_ocupacion"]},
        "d_covid": ref.d_covid.values, "d_oferta_2017": ref.d_oferta_2017.values,
        "diag_atipico_iqr": ((y < q1 - 1.5 * (q3 - q1)) | (y > q3 + 1.5 * (q3 - q1))).astype(int).values,
        "categorias_incluidas": "2-5 estrellas", "n_categorias_fuente": 4,
        "sha256_bronce": "0" * 64, "ejecucion": "simulada", "version_contrato": datos.VERSION_CONTRATO,
    })[datos.COLUMNAS_ORO]
    oro[enteros] = oro[enteros].astype("int64")

    def guardar(df):
        ruta = tmp_path / "oro.csv"
        df.round(6).to_csv(ruta, index=False, lineterminator="\n")
        return ruta

    c = datos.cargar_serie("oro", ruta_oro=guardar(oro))
    assert c.fuente == "oro" and c.detalle["verificacion_vs_referencia"]["coincide"]
    alterado = oro.copy()
    alterado.loc[10, "cuartos_ocupados_residentes"] += 100
    alterado["cuartos_ocupados"] = (alterado.cuartos_ocupados_residentes
                                    + alterado.cuartos_ocupados_no_residentes)
    alterado["ocupacion_pct"] = 100 * alterado.cuartos_ocupados / alterado.cuartos_disponibles
    alterado["pct_cuartos_no_residentes"] = (100 * alterado.cuartos_ocupados_no_residentes
                                             / alterado.cuartos_ocupados)
    alterado["densidad_ocupacion"] = alterado.turistas_noche / alterado.cuartos_ocupados
    with pytest.raises(ValueError, match="no coincide"):
        datos.cargar_serie("oro", ruta_oro=guardar(alterado))


@pytest.mark.datos
@hay_bronce
def test_sin_fuga_el_pronostico_no_depende_de_2024(referencia):
    s = referencia.ocupacion_pct
    ent, pru = datos.partir(s)
    p1 = mod.pronostico_ajuste(mod.ajustar_holt_winters(ent), pru.index).media
    s2 = s.copy()
    s2.loc[pru.index] = 0.5  # 2024 alterado: el ajuste no debe verlo
    ent2, _ = datos.partir(s2)
    p2 = mod.pronostico_ajuste(mod.ajustar_holt_winters(ent2), pru.index).media
    assert np.allclose(p1.values, p2.values)
