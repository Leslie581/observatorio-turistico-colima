"""Pruebas de integración con red. Solo corren con TDL_RED=1 y token INEGI_TOKEN.

Solo se consulta la API documentada del DENUE (INEGI). No hay pruebas con red contra
DATATUR: sus condiciones de uso automatizado no están resueltas (ver docs/fuentes/).
"""
import os

import pytest

pytestmark = [pytest.mark.red,
              pytest.mark.skipif(os.getenv("TDL_RED") != "1", reason="sin red habilitada (TDL_RED=1)"),
              pytest.mark.skipif(not os.getenv("INEGI_TOKEN"), reason="sin token INEGI")]


def test_denue_cuantificar(tmp_path):
    from extractores import denue
    from extractores.base import Bitacora, ExtractorEtico
    cli = denue.ClienteDenue(ExtractorEtico(bitacora=Bitacora(tmp_path / "b.jsonl")))
    assert denue.total_cuantificar(cli.cuantificar())


def test_captura_denue_extremo_a_extremo(tmp_path):
    """Una captura real escribe bronce sin datos personales y registra la ejecución."""
    import json

    from extractores import captura_denue
    fila = captura_denue.ejecutar(bronce=tmp_path / "data" / "bronce",
                                  bitacora_ejecuciones=tmp_path / "ej.jsonl",
                                  bitacora_http=tmp_path / "http.jsonl")
    assert fila["resultado"] == "exito", fila
    crudos = list((tmp_path / "data" / "bronce" / "denue").rglob("*_BuscarAreaAct.json"))
    assert crudos
    claves = {k.lower() for r in json.loads(crudos[0].read_text(encoding="utf-8")) for k in r}
    assert not claves & {"telefono", "correo_e", "sitio_internet", "razon_social"}
    assert os.environ["INEGI_TOKEN"] not in (tmp_path / "http.jsonl").read_text(encoding="utf-8")
