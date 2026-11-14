"""Análisis de ruido: los resultados versionados se regeneran idénticos y los extremos de COVID se distinguen de los demás."""
import json

from laboratorio.exploracion import ruido


def test_resumen_regenerado_igual_al_versionado(tmp_path):
    nuevo = ruido.ejecutar(tmp_path)
    viejo = json.loads((ruido.SALIDA / "resumen.json").read_text(encoding="utf-8"))
    assert nuevo == viejo


def test_extremos_se_clasifican_sin_eliminar_meses(tmp_path):
    tabla, ext, r = ruido.calcular()
    assert r["n_meses"] == 108 and r["extremos_covid"] + r["extremos_sin_causa_conocida"] == r["meses_residuo_extremo"]
    assert set(ext.loc[ext.d_covid, "periodo"]) <= {f"2020-{m:02d}" for m in range(3, 13)}
    assert r["desviacion_residuo_sin_covid_pp"] < r["desviacion_residuo_pp"]
