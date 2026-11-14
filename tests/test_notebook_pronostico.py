"""El notebook de pronóstico es ejecutable: todas sus celdas de código corren en orden contra los resultados versionados."""
import json
from pathlib import Path

import pytest

pytest.importorskip("statsmodels")
NB = Path(__file__).resolve().parents[1] / "notebooks" / "pronostico_e1.ipynb"


def test_celdas_de_codigo_se_ejecutan():
    nb = json.loads(NB.read_text(encoding="utf-8"))
    espacio: dict = {}
    n = 0
    for c in nb["cells"]:
        if c["cell_type"] == "code":
            exec(compile("".join(c["source"]), str(NB), "exec"), espacio)  # noqa: S102 - código propio versionado
            n += 1
    assert n >= 5 and "serie" in espacio
