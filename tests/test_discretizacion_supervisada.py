"""Discretización supervisada por entropía (pipeline/discretizacion_supervisada.py) y su comparación con ancho y frecuencia.

Las pruebas con series fabricadas son SINTÉTICAS y lo declaran; las demás usan el oro versionado real. Garantías centrales:
sin fuga (nada de 2024 entra al ajuste), objetivo no circular, reproducibilidad y que los métodos existentes no cambian.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from laboratorio.exploracion import discretizacion as comparar
from pipeline import discretizacion_supervisada as ds
from pipeline.interfaz import cargar_oro_mensual, partir_entrenamiento_prueba, serie_objetivo
from pipeline.transformaciones import ErrorFuga, ajustar_discretizacion

RAIZ = Path(__file__).resolve().parent.parent
RUTA_ORO = RAIZ / "data" / "oro" / "manzanillo_ocupacion_mensual.csv"
VERSIONADO = comparar.SALIDA
pytestmark = pytest.mark.skipif(not RUTA_ORO.exists(), reason="sin oro")


def _mensual(valores, inicio="2016-01"):
    return pd.Series(valores, index=pd.period_range(inicio, periods=len(valores), freq="M"), dtype=float)


# ------------------------------------------------------------------ entropía y criterio MDL (SINTÉTICAS)
def test_entropia_y_ganancia_con_valores_conocidos():
    assert ds.entropia([0, 0, 0, 0]) == 0.0
    assert ds.entropia([0, 1, 0, 1]) == pytest.approx(1.0)
    assert ds.entropia([0, 0, 0, 1]) == pytest.approx(0.8112781, abs=1e-6)
    y, izq = np.array([0, 0, 0, 1, 1, 1]), np.array([True, True, True, False, False, False])
    assert ds._ganancia(y, izq) == pytest.approx(1.0)                                   # separación perfecta: toda la entropía


def test_mdlp_acepta_una_separacion_clara_y_rechaza_el_ruido():
    y = np.array([0] * 30 + [1] * 30)
    assert ds.mdlp_acepta_corte(y, np.arange(60) < 30) is True
    rng = np.random.default_rng(1)
    ruido = rng.integers(0, 2, 60)
    assert ds.mdlp_acepta_corte(ruido, np.arange(60) < 30) is False


def test_mejor_corte_recupera_la_frontera_de_una_serie_fabricada():
    x = np.concatenate([np.linspace(10, 40, 30), np.linspace(60, 90, 30)])
    y = np.array([0] * 30 + [1] * 30)
    corte, ganancia, ok = ds.mejor_corte(x, y, min_hoja=8)
    assert 40 < corte < 60 and ganancia == pytest.approx(1.0) and ok is True


def test_min_hoja_impide_niveles_diminutos():
    x, y = np.arange(20.0), np.array([0] * 19 + [1])
    assert ds.mejor_corte(x, y, min_hoja=8)[0] < 19                                       # no corta para aislar un solo mes


# ------------------------------------------------------------------ ajuste, candado y objetivo
def test_el_objetivo_es_de_calendario_y_no_depende_de_la_ocupacion():
    idx = pd.period_range("2016-01", "2023-12", freq="M")
    t = ds.temporada_alta(idx)
    assert t.sum() == 3 * 8 and set(idx[t.to_numpy() == 1].month) == {7, 8, 12}
    assert ds.temporada_alta(idx).equals(t)                                               # solo depende del índice
    assert "ocupacion" not in ds.temporada_alta.__code__.co_varnames


def test_el_ajuste_rechaza_cualquier_mes_de_2024():
    x = _mensual(np.linspace(30, 70, 97))                                                 # llega a 2024-01
    with pytest.raises(ErrorFuga, match="2024-01"):
        ds.ajustar_supervisada(x, ds.temporada_alta(x.index))


def test_el_ajuste_exige_indice_mensual_para_poder_comprobar_la_fuga():
    with pytest.raises(ErrorFuga):
        ds.ajustar_supervisada(pd.Series(np.linspace(1, 90, 60)), pd.Series([0, 1] * 30))


def test_el_ajuste_rechaza_un_objetivo_de_una_sola_clase_y_poca_muestra():
    x = _mensual(np.linspace(30, 70, 60))
    with pytest.raises(ValueError, match="una sola clase"):
        ds.ajustar_supervisada(x, pd.Series(0, index=x.index))
    with pytest.raises(ValueError, match="al menos"):
        ds.ajustar_supervisada(x.iloc[:12], ds.temporada_alta(x.index[:12]))


def test_cortes_ascendentes_k_niveles_y_extremos_abiertos():
    oro = cargar_oro_mensual()
    x_tr, _ = partir_entrenamiento_prueba(serie_objetivo(oro))
    p = ds.ajustar_supervisada(x_tr, ds.temporada_alta(x_tr.index), k=3, min_hoja=8, excluir=oro["d_covid"].astype(bool))
    b = p.discretizacion.bordes
    assert len(b) == 2 and b[0] < b[1] and p.discretizacion.k == 3 and p.discretizacion.metodo == ds.METODO
    assert p.discretizacion.ajustado_hasta == "2023-12" and p.excluidos == 16 and p.discretizacion.n == 80
    niveles = ds.aplicar_supervisada(pd.Series([0.0, b[0] - 1e-9, b[0], b[1], 100.0]), p)
    assert list(niveles.astype(str)) == ["bajo", "bajo", "medio", "alto", "alto"]         # [borde_i, borde_i+1) y extremos abiertos


# ------------------------------------------------------------------ sin fuga: 2024 no puede cambiar los cortes
def test_alterar_2024_no_cambia_los_cortes_ni_las_metricas_de_ajuste(tmp_path):
    base_tabla, base_resumen = comparar.calcular()
    copia = tmp_path / "oro.csv"
    df = pd.read_csv(RUTA_ORO, dtype=str)
    prueba = df.periodo >= "2024-01"
    assert prueba.sum() == 12
    # SINTÉTICA: se escribe un 2024 distinto, pero coherente con la puerta de calidad (menos ocupados, misma oferta)
    for c in ("cuartos_ocupados_residentes", "cuartos_ocupados_no_residentes"):
        df.loc[prueba, c] = (df.loc[prueba, c].astype(int) // 2).astype(str)
    df.loc[prueba, "cuartos_ocupados"] = (df.loc[prueba, "cuartos_ocupados_residentes"].astype(int)
                                          + df.loc[prueba, "cuartos_ocupados_no_residentes"].astype(int)).astype(str)
    df.loc[prueba, "ocupacion_pct"] = (100 * df.loc[prueba, "cuartos_ocupados"].astype(int)
                                       / df.loc[prueba, "cuartos_disponibles"].astype(int)).round(6).astype(str)
    df.to_csv(copia, index=False, lineterminator="\n")
    tabla, resumen = comparar.calcular(copia)
    for clave in ("supervisada_sin_covid", "supervisada_todo_entrenamiento"):
        assert resumen[clave] == base_resumen[clave]                                      # cortes, ganancias, MDL y p-valor idénticos
    columnas_ajuste = ["escenario", "metodo", "cortes", "meses_por_nivel_ajuste", "ganancia_bits_ajuste", "exactitud_ajuste"]
    assert tabla[columnas_ajuste].equals(base_tabla[columnas_ajuste])
    assert not tabla[["ganancia_bits_2024", "meses_por_nivel_2024"]].equals(base_tabla[["ganancia_bits_2024", "meses_por_nivel_2024"]])


# ------------------------------------------------------------------ comparación, reproducibilidad y no regresión
def test_la_comparacion_incluye_los_tres_metodos_en_los_dos_escenarios():
    tabla, resumen = comparar.calcular()
    assert set(zip(tabla.escenario, tabla.metodo)) == {(e, m) for e in ("sin_covid", "todo_entrenamiento") for m in comparar.METODOS}
    s = tabla[(tabla.escenario == "sin_covid") & (tabla.metodo == ds.METODO)].iloc[0]
    assert s.meses_por_nivel_ajuste.count("/") == 2 and sum(int(v) for v in s.meses_por_nivel_ajuste.split(" / ")) == 80
    assert resumen["meses_temporada_alta_2024"] == 3 and resumen["meses_2024"] == 12
    assert resumen["supervisada_sin_covid"]["p_valor_permutacion"] < 0.05                # la asociación en el ajuste no es ruido


def test_dos_ejecuciones_producen_los_mismos_bytes(tmp_path):
    comparar.ejecutar(salida=tmp_path / "a")
    comparar.ejecutar(salida=tmp_path / "b")
    for n in ("comparacion_metodos.csv", "resumen.json"):
        assert (tmp_path / "a" / n).read_bytes() == (tmp_path / "b" / n).read_bytes()


def test_los_resultados_versionados_estan_al_dia(tmp_path):
    comparar.ejecutar(salida=tmp_path)
    for n in ("comparacion_metodos.csv", "resumen.json"):
        nuevo = (tmp_path / n).read_bytes().replace(b"\r\n", b"\n")
        viejo = (VERSIONADO / n).read_bytes().replace(b"\r\n", b"\n")
        assert nuevo == viejo, f"{n} está desactualizado: ejecute python -m laboratorio.exploracion.discretizacion"


def test_los_metodos_existentes_no_cambian():
    """Ancho y frecuencia siguen dando los bordes que ya documentan transformaciones.md y parametros_transformaciones.json."""
    params = json.loads((RAIZ / "laboratorio" / "exploracion" / "resultados" / "parametros_transformaciones.json").read_text(encoding="utf-8"))
    x_tr, _ = partir_entrenamiento_prueba(serie_objetivo(cargar_oro_mensual()))
    assert list(ajustar_discretizacion(x_tr, "frecuencia_igual", 3).bordes) == pytest.approx(params["discretizacion_frecuencia_igual"]["bordes"])
    assert list(ajustar_discretizacion(x_tr, "ancho_igual", 3).bordes) == pytest.approx(params["discretizacion_ancho_igual"]["bordes"])


def test_el_p_valor_de_permutacion_es_reproducible_y_distingue_senal_de_ruido():
    rng = np.random.default_rng(3)
    x = rng.normal(50, 10, 80)
    y_senal = (x > 55).astype(int)
    y_ruido = rng.integers(0, 2, 80)
    def p(y):
        niveles = np.searchsorted(np.asarray(ds._cortes_voraces(x, y, 3, 8)[0]), x, side="right")
        return ds.p_valor_permutacion(x, y, ds.informacion_mutua(niveles, y), 3, 8, n_perm=100)
    assert p(y_senal) == p(y_senal) and p(y_senal) < 0.05 and p(y_ruido) > 0.05


def test_la_comparacion_no_importa_bibliotecas_pesadas_ni_lee_otras_capas():
    codigo = (RAIZ / "laboratorio" / "exploracion" / "discretizacion.py").read_text(encoding="utf-8")
    for prohibido in ("statsmodels", "scipy", "sklearn", "matplotlib", "bronce", "plata"):
        assert f"import {prohibido}" not in codigo and f"from {prohibido}" not in codigo


def test_la_linea_de_comandos_escribe_los_dos_archivos(tmp_path, capsys):
    assert comparar.main(["--salida", str(tmp_path)]) == 0
    assert sorted(p.name for p in tmp_path.iterdir()) == ["comparacion_metodos.csv", "resumen.json"]
    assert '"p_valor_permutacion"' in capsys.readouterr().out
