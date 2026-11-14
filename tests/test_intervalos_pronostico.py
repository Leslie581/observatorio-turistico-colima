"""Intervalos bootstrap de bloques (laboratorio/pronosticos/intervalos.py): correctitud del simulador, reproducibilidad y sin fuga."""
import json

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("statsmodels")
from laboratorio.pronosticos import datos, intervalos as iv  # noqa: E402
from laboratorio.pronosticos import modelos as mod  # noqa: E402


@pytest.fixture(scope="module")
def ajuste():
    serie = datos.cargar_serie("oro").serie
    spec = iv.especificacion_elegida()
    ent, _ = datos.partir(serie)
    return serie, spec, ent, iv.ajustar(ent, spec)


def test_choques_cero_reproducen_el_pronostico_analitico(ajuste, monkeypatch):
    _, spec, ent, res = ajuste
    h = 6
    futuro = pd.period_range(ent.index[-1] + 1, periods=h, freq="M")
    monkeypatch.setattr(iv, "bloques", lambda e, n, longitud, rng: np.zeros(n))
    tray = iv.trayectorias(res, futuro, spec, B=2, semilla=1)
    analitico = np.asarray(res.get_forecast(h, exog=mod.exog_covid(futuro) if spec[2] else None).predicted_mean)
    assert np.allclose(tray[0], analitico, atol=1e-6)


def test_bootstrap_es_reproducible_y_abre_desde_h1(ajuste):
    _, spec, ent, res = ajuste
    futuro = pd.period_range(ent.index[-1] + 1, periods=4, freq="M")
    a = iv.trayectorias(res, futuro, spec, B=30, semilla=7)
    b = iv.trayectorias(res, futuro, spec, B=30, semilla=7)
    assert np.array_equal(a, b)
    assert a[:, 0].std() > 0.5                            # el intervalo de h=1 no está colapsado (defecto corregido en el diseño)


def test_origen_movil_no_usa_2024(ajuste):
    serie, *_ = ajuste
    os_ = iv.origenes(serie)
    assert max(os_) + iv.H <= pd.Period("2023-12", "M")


def test_resultados_versionados_coherentes():
    carpeta = iv.SALIDA
    r = json.loads((carpeta / "resumen.json").read_text(encoding="utf-8"))
    assert r["semilla"] == iv.SEMILLA and "proyección histórica" in r["advertencia"]
    p = pd.read_csv(carpeta / "proyeccion_2025_2027.csv")
    assert len(p) == 36
    resumen = pd.read_csv(carpeta / "intervalos_origen_movil_resumen.csv")
    assert resumen.filter(regex="cobertura").le(1).all().all()
