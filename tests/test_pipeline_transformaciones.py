"""Transformaciones (min-max, z-score, discretización) y, sobre todo, AUSENCIA DE FUGA TEMPORAL.

Las pruebas con series sintéticas lo declaran (no son evidencia operativa); la prueba final usa el oro versionado real.
Solo requieren numpy y pandas, así que corren también en el flujo de captura (requirements.txt).
"""
import numpy as np
import pandas as pd
import pytest

from pipeline import transformaciones as T
from pipeline.interfaz import cargar_oro_mensual, serie_objetivo
from pipeline.transformaciones import ErrorFuga


def serie_sintetica(prueba_desplazada=0.0):
    """SINTÉTICA: 108 meses (2016-01 a 2024-12); la prueba (2024) puede desplazarse para detectar fuga."""
    idx = pd.period_range("2016-01", "2024-12", freq="M")
    v = 40 + 15 * np.sin(np.arange(108) * 2 * np.pi / 12) + np.arange(108) * 0.05
    s = pd.Series(v, index=idx, name="ocupacion_pct")
    s[s.index > pd.Period("2023-12", "M")] += prueba_desplazada
    return s


def particion(s):
    return s[s.index <= pd.Period("2023-12", "M")], s[s.index > pd.Period("2023-12", "M")]


# ---------------------------------------------------------------- resultados correctos
def test_minmax_lleva_el_entrenamiento_a_0_1_y_se_invierte():
    ent, _ = particion(serie_sintetica())
    p = T.ajustar_minmax(ent)
    z = T.aplicar_minmax(ent, p)
    assert z.min() == pytest.approx(0.0) and z.max() == pytest.approx(1.0)
    assert (p.minimo, p.maximo) == (ent.min(), ent.max()) and p.n == 96 and p.ajustado_hasta == "2023-12"
    assert T.invertir_minmax(z, p).to_numpy() == pytest.approx(ent.to_numpy())


def test_minmax_formula_con_valores_conocidos():
    ent = pd.Series([10.0, 20.0, 30.0], index=pd.period_range("2023-10", "2023-12", freq="M"))
    p = T.ajustar_minmax(ent)
    x = pd.Series([10.0, 25.0, 40.0, 0.0], index=pd.period_range("2024-01", "2024-04", freq="M"))
    assert T.aplicar_minmax(x, p).tolist() == [0.0, 0.75, 1.5, -0.5]  # fuera del rango de entrenamiento: NO se recorta


def test_zscore_del_entrenamiento_tiene_media_0_y_desviacion_1_y_se_invierte():
    ent, _ = particion(serie_sintetica())
    p = T.ajustar_zscore(ent)
    z = T.aplicar_zscore(ent, p)
    assert z.mean() == pytest.approx(0.0, abs=1e-12) and z.std(ddof=0) == pytest.approx(1.0)
    assert p.desviacion == pytest.approx(ent.std(ddof=0))
    assert T.invertir_zscore(z, p).to_numpy() == pytest.approx(ent.to_numpy())


def test_zscore_formula_con_valores_conocidos():
    ent = pd.Series([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0], index=pd.period_range("2023-05", "2023-12", freq="M"))
    p = T.ajustar_zscore(ent)  # media 5, desviación poblacional 2
    assert (p.media, p.desviacion) == (5.0, 2.0)
    assert T.aplicar_zscore(pd.Series([9.0, 5.0, 1.0]), p).tolist() == [2.0, 0.0, -2.0]


def test_discretizacion_por_frecuencia_reparte_el_entrenamiento_en_partes_iguales():
    ent, _ = particion(serie_sintetica())
    p = T.ajustar_discretizacion(ent, "frecuencia_igual", 3)
    niveles = T.aplicar_discretizacion(ent, p)
    assert niveles.value_counts().to_dict() == {"bajo": 32, "medio": 32, "alto": 32}
    assert p.etiquetas == ("bajo", "medio", "alto") and len(p.bordes) == 2 and p.bordes[0] < p.bordes[1]
    assert niveles.cat.ordered and list(niveles.cat.categories) == ["bajo", "medio", "alto"]


def test_discretizacion_por_ancho_usa_intervalos_iguales_entre_min_y_max_del_entrenamiento():
    ent = pd.Series([0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 100.0],
                    index=pd.period_range("2023-01", "2023-12", freq="M"))
    p = T.ajustar_discretizacion(ent, "ancho_igual", 4)
    assert p.bordes == (25.0, 50.0, 75.0) and p.etiquetas == ("N1", "N2", "N3", "N4")
    x = pd.Series([0, 24.9, 25, 49.9, 50, 74.9, 75, 100])
    assert T.aplicar_discretizacion(x, p).astype(str).tolist() == ["N1", "N1", "N2", "N2", "N3", "N3", "N4", "N4"]  # [borde, borde)


def test_discretizacion_valores_fuera_del_rango_caen_en_el_nivel_extremo_y_los_faltantes_se_conservan():
    ent, _ = particion(serie_sintetica())
    p = T.ajustar_discretizacion(ent)
    r = T.aplicar_discretizacion(pd.Series([-500.0, np.nan, 500.0]), p)
    assert r.iloc[0] == "bajo" and pd.isna(r.iloc[1]) and r.iloc[2] == "alto"


def test_aplicar_conserva_nan_e_indice_y_no_modifica_la_entrada():
    ent, pru = particion(serie_sintetica())
    t = T.ajustar_todo(ent)
    x = pru.copy()
    x.iloc[3] = np.nan
    copia = x.copy()
    out = T.transformar(x, t)
    pd.testing.assert_series_equal(x, copia)
    assert out.index.equals(x.index) and np.isnan(out["minmax"].iloc[3]) and pd.isna(out["nivel"].iloc[3])


# ---------------------------------------------------------------- AUSENCIA DE FUGA TEMPORAL
@pytest.mark.parametrize("ajuste", [T.ajustar_minmax, T.ajustar_zscore, T.ajustar_discretizacion, T.ajustar_todo])
def test_ajustar_con_la_serie_completa_incluida_la_prueba_lanza_error_de_fuga(ajuste):
    with pytest.raises(ErrorFuga, match="2024"):
        ajuste(serie_sintetica())


def test_un_solo_mes_de_prueba_basta_para_detectar_la_fuga():
    ent, pru = particion(serie_sintetica())
    with pytest.raises(ErrorFuga):
        T.ajustar_minmax(pd.concat([ent, pru.iloc[:1]]))


def test_el_ajuste_exige_indice_mensual_para_poder_comprobar_la_fecha():
    with pytest.raises(ErrorFuga):
        T.ajustar_zscore(pd.Series([1.0, 2.0, 3.0]))  # sin fechas no se puede garantizar que no haya fuga


def test_los_parametros_no_dependen_de_los_valores_de_2024():
    """Se cambia la prueba radicalmente: los parámetros y la transformación del entrenamiento NO deben moverse."""
    base_t, base_tab = T.transformar_serie_oro(serie_sintetica())
    mod_t, mod_tab = T.transformar_serie_oro(serie_sintetica(prueba_desplazada=500.0))
    assert base_t == mod_t
    cols = ["valor", "minmax", "zscore"]
    pd.testing.assert_frame_equal(base_tab[base_tab.conjunto == "entrenamiento"][cols],
                                  mod_tab[mod_tab.conjunto == "entrenamiento"][cols])


def test_la_prueba_se_transforma_con_los_parametros_del_entrenamiento_sin_recalcular():
    s = serie_sintetica()
    t, tabla = T.transformar_serie_oro(s)
    ent, pru = particion(s)
    prueba = tabla[tabla.conjunto == "prueba"]
    assert prueba["minmax"].to_numpy() == pytest.approx(((pru - ent.min()) / (ent.max() - ent.min())).to_numpy())
    assert prueba["zscore"].to_numpy() == pytest.approx(((pru - ent.mean()) / ent.std(ddof=0)).to_numpy())
    # Si se hubiera recalculado con la prueba, su z-score tendría media 0; con los parámetros del entrenamiento no.
    assert abs(prueba["zscore"].mean()) > 1e-3 and not np.isclose(prueba["minmax"].min(), 0.0)


def test_ajustar_con_toda_la_serie_daria_otros_parametros_lo_que_el_candado_evita():
    """Demuestra que la fuga cambiaría el resultado (con una prueba desplazada) y que el flujo correcto no la comete."""
    s = serie_sintetica(prueba_desplazada=60.0)
    ent, _ = particion(s)
    con_fuga = (s.min(), s.max(), s.mean())
    sin_fuga = T.ajustar_minmax(ent), T.ajustar_zscore(ent)
    assert con_fuga[1] != sin_fuga[0].maximo and con_fuga[2] != sin_fuga[1].media
    t, _ = T.transformar_serie_oro(s)
    assert t.minmax.maximo == ent.max() and t.zscore.media == pytest.approx(ent.mean())


def test_un_valor_de_prueba_extremo_no_mueve_los_bordes_de_discretizacion():
    t0, _ = T.transformar_serie_oro(serie_sintetica())
    t1, tab = T.transformar_serie_oro(serie_sintetica(prueba_desplazada=1000.0))
    assert t0.discretizacion.bordes == t1.discretizacion.bordes
    assert set(tab[tab.conjunto == "prueba"]["nivel"].astype(str)) == {"alto"}
    assert tab[tab.conjunto == "prueba"]["fuera_rango_entrenamiento"].all()


# ---------------------------------------------------------------- entradas inválidas
def test_entradas_invalidas_fallan_con_mensaje():
    idx = pd.period_range("2023-01", "2023-12", freq="M")
    constante = pd.Series(5.0, index=idx)
    con_nan = pd.Series([1.0] * 11 + [np.nan], index=idx)
    with pytest.raises(ValueError, match="constante"):
        T.ajustar_minmax(constante)
    with pytest.raises(ValueError, match="constante"):
        T.ajustar_zscore(constante)
    with pytest.raises(ValueError, match="faltantes"):
        T.ajustar_minmax(con_nan)
    with pytest.raises(ValueError, match="al menos 2"):
        T.ajustar_zscore(pd.Series([1.0], index=idx[:1]))
    with pytest.raises(ValueError, match="método"):
        T.ajustar_discretizacion(pd.Series(range(12), index=idx, dtype=float), "magia")
    with pytest.raises(ValueError, match="k debe"):
        T.ajustar_discretizacion(pd.Series(range(12), index=idx, dtype=float), k=1)
    with pytest.raises(ValueError, match="ascendentes"):
        T.ajustar_discretizacion(pd.Series([1.0] * 11 + [2.0], index=idx), "frecuencia_igual", 3)  # bordes repetidos
    with pytest.raises(ValueError, match="etiquetas"):
        T.ajustar_discretizacion(pd.Series(range(12), index=idx, dtype=float), k=3, etiquetas=("a", "b"))


# ---------------------------------------------------------------- oro real (versionado)
def test_con_el_oro_real_los_parametros_salen_solo_de_2016_2023():
    df = cargar_oro_mensual()
    s = serie_objetivo(df)
    t, tabla = T.transformar_serie_oro(s)
    ent = s[s.index <= pd.Period("2023-12", "M")]
    assert t.minmax.n == t.zscore.n == t.discretizacion.n == 96 and t.minmax.ajustado_hasta == "2023-12"
    assert (t.minmax.minimo, t.minmax.maximo) == (float(ent.min()), float(ent.max()))
    assert t.zscore.media == pytest.approx(float(ent.mean())) and t.zscore.desviacion == pytest.approx(float(ent.std(ddof=0)))
    assert tabla.conjunto.value_counts().to_dict() == {"entrenamiento": 96, "prueba": 12}
    with pytest.raises(ErrorFuga):
        T.ajustar_minmax(s)  # la serie completa de 108 meses se rechaza
    json_ok = t.a_dict()
    assert json_ok["discretizacion"]["bordes"] == list(t.discretizacion.bordes)
