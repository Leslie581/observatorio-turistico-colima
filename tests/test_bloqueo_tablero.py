"""Archivo de bloqueo con hashes del tablero (tablero/requirements.lock.txt y pipeline/bloqueo.py).

Sin red: se comprueba la estructura y la coherencia con tablero/requirements.txt; la instalación real con
``--require-hashes`` la hace el trabajo ``bloqueo-tablero`` de ci.yml. Los casos de falla son SINTÉTICOS y lo declaran.
"""
import re
from pathlib import Path

import pytest

from pipeline import bloqueo as b

RAIZ = Path(__file__).resolve().parent.parent
LOCK = RAIZ / "tablero" / "requirements.lock.txt"


def test_el_bloqueo_versionado_es_valido_y_cubre_las_dependencias_directas():
    v = b.verificar()
    assert v["ok"] is True, v["problemas"]
    assert v["paquetes"] == 34 and v["hashes"] >= 34
    directas = b.leer_pines(RAIZ / "tablero" / "requirements.txt")
    bloqueado = b.analizar(LOCK.read_text(encoding="utf-8"))["paquetes"]
    assert {n: bloqueado[n][0] for n in directas} == directas                                # mismas versiones exactas


def test_cada_paquete_tiene_hashes_sha256_validos_sin_repetir():
    for nombre, (version, hashes) in b.analizar(LOCK.read_text(encoding="utf-8"))["paquetes"].items():
        assert hashes and len(hashes) == len(set(hashes)), nombre
        assert all(re.fullmatch(r"[0-9a-f]{64}", h) for h in hashes), nombre
        assert re.fullmatch(r"[0-9][0-9A-Za-z.!+_-]*", version), nombre


def test_el_bloqueo_no_trae_urls_ni_rutas_ni_indices_alternativos():
    texto = LOCK.read_text(encoding="utf-8")
    for prohibido in ("--index-url", "--extra-index-url", "--find-links", "git+", "http://", "file:", "@ "):
        assert prohibido not in texto, prohibido


def test_el_bloqueo_coincide_con_el_cierre_documentado_en_la_evidencia():
    """El cierre (pip freeze) versionado en calidad/evidencia/ es el que originó el bloqueo."""
    cierre = b.leer_pines(RAIZ / "calidad" / "evidencia" / "tablero-cierre-transitivo-2026-11-13.txt")
    bloqueado = {n: v for n, (v, _) in b.analizar(LOCK.read_text(encoding="utf-8"))["paquetes"].items()}
    assert cierre == bloqueado


# ------------------------------------------------------------------ generación y fallas (SINTÉTICAS)
def _falso(nombre, version):
    return ["a" * 64, "b" * 64] if nombre != "sin-hashes" else []


def test_generar_produce_un_bloqueo_que_vuelve_a_analizarse(tmp_path):
    texto = b.generar({"pandas": "3.0.5", "numpy": "2.5.3", "six": "1.0"}, {"pandas": "3.0.5"}, "2026-11-14", _falso)
    p = b.analizar(texto)
    assert p["problemas"] == [] and set(p["paquetes"]) == {"numpy", "pandas", "six"}
    assert p["paquetes"]["pandas"] == ("3.0.5", ["a" * 64, "b" * 64])
    archivo, directas = tmp_path / "x.lock", tmp_path / "x.txt"
    archivo.write_text(texto, encoding="utf-8")
    directas.write_text("pandas==3.0.5\n", encoding="utf-8")
    assert b.verificar(archivo, directas)["ok"] is True


def test_generar_rechaza_una_directa_ausente_o_con_otra_version_y_paquetes_sin_hashes():
    with pytest.raises(ValueError, match="no está en el cierre"):
        b.generar({"numpy": "2.5.3"}, {"pandas": "3.0.5"}, "2026-11-14", _falso)
    with pytest.raises(ValueError, match="no está en el cierre"):
        b.generar({"pandas": "3.0.4"}, {"pandas": "3.0.5"}, "2026-11-14", _falso)
    with pytest.raises(ValueError, match="sin hashes|no tiene archivos"):
        b.generar({"sin-hashes": "1.0"}, {}, "2026-11-14", _falso)


def test_verificar_detecta_un_paquete_sin_hash_una_version_distinta_y_lineas_ajenas(tmp_path):
    base = b.generar({"pandas": "3.0.5"}, {"pandas": "3.0.5"}, "2026-11-14", _falso)
    directas = tmp_path / "d.txt"
    directas.write_text("pandas==3.0.5\n", encoding="utf-8")
    casos = {
        "sin_hash": base.split("pandas==")[0] + "pandas==3.0.5" + chr(10),
        "version": base.replace("pandas==3.0.5", "pandas==3.0.4"),
        "repetido": base.replace("b" * 64, "a" * 64),
        "ajena": base + "pip install algo\n",
    }
    for nombre, texto in casos.items():
        f = tmp_path / f"{nombre}.lock"
        f.write_text(texto, encoding="utf-8")
        assert b.verificar(f, directas)["ok"] is False, nombre


def test_la_linea_de_comandos_verifica_el_bloqueo(capsys):
    assert b.main(["verificar"]) == 0
    assert '"ok": true' in capsys.readouterr().out
