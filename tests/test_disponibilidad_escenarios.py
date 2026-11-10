"""Escenarios SIMULADOS del indicador de disponibilidad (objetivo O1 = 95 %).

Usan archivos temporales (tmp_path). No leen ni escriben calidad/bitacora_capturas.jsonl y sus resultados
NO son evidencia operativa: solo demuestran que la fórmula se comporta como se definió.
"""
import json
from pathlib import Path

import pytest

from pipeline import verificar_e0 as v

REAL = Path(__file__).resolve().parent.parent / "calidad" / "bitacora_capturas.jsonl"


def _bitacora(tmp_path, exitos, fallos, omitidas=0):
    filas = []
    for i in range(exitos + fallos + omitidas):
        filas.append({"ejecucion": f"sim{i:03d}", "fecha_local": f"2026-12-{(i % 28) + 1:02d}"})
    for f in filas[:exitos]:
        f["resultado"] = "exito"
    for f in filas[exitos:exitos + fallos]:
        f["resultado"] = "fallo"
    for f in filas[exitos + fallos:]:
        f["resultado"] = "omitida_duplicada"
    ruta = tmp_path / "bitacora_simulada.jsonl"
    ruta.write_text("\n".join(json.dumps(f) for f in filas) + "\n", encoding="utf-8")
    return ruta


@pytest.mark.parametrize("exitos,fallos,tasa,cumplido", [
    (2, 1, 0.6667, False),    # 1) 66.7 %: objetivo no cumplido
    (19, 1, 0.95, True),      # 2) exactamente 95 %: cumplido (>=)
    (20, 0, 1.0, True),       # 3) 100 %: cumplido
    (18, 1, 0.9474, False),   # control: 18/19 = 94.7 % queda justo debajo
])
@pytest.mark.parametrize("omitidas", [0, 5])  # las omitidas por duplicado no deben cambiar nada
def test_escenarios_de_disponibilidad(tmp_path, exitos, fallos, tasa, cumplido, omitidas):
    r = v.disponibilidad(_bitacora(tmp_path, exitos, fallos, omitidas))
    assert r["ejecuciones"] == exitos + fallos          # denominador sin las omitidas
    assert r["exitosas"] == exitos
    assert r["tasa_exito"] == tasa
    assert r["objetivo"] == 0.95
    assert r["objetivo_cumplido"] is cumplido and r["ok"] is cumplido
    assert r["estado"] == ("satisfactoria" if cumplido else "fallida")


def test_solo_omitidas_no_es_evaluable_ni_cumple(tmp_path):
    r = v.disponibilidad(_bitacora(tmp_path, 0, 0, omitidas=4))
    assert r["ok"] is None and r["estado"] == "sin_datos"


@pytest.mark.parametrize("exitos,fallos,salida_informativa,salida_normal", [(2, 1, 0, 1), (19, 1, 0, 0), (20, 0, 0, 0)])
def test_codigos_de_salida_por_escenario(tmp_path, monkeypatch, capsys, exitos, fallos, salida_informativa, salida_normal):
    ruta = _bitacora(tmp_path, exitos, fallos, omitidas=2)
    monkeypatch.setitem(v.COMPROBACIONES, "disponibilidad", lambda: v.disponibilidad(ruta))
    assert v.main(["--solo", "disponibilidad", "--informativo"]) == salida_informativa
    assert v.main(["--solo", "disponibilidad"]) == salida_normal
    capsys.readouterr()


def test_la_prueba_no_toca_la_bitacora_real(tmp_path):
    antes = REAL.read_bytes() if REAL.exists() else None
    v.disponibilidad(_bitacora(tmp_path, 19, 1, 3))
    assert (REAL.read_bytes() if REAL.exists() else None) == antes
