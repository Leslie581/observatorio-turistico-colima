import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
FIXTURES = Path(__file__).parent / "fixtures"
BRONCE_BASE70 = RAIZ / "data" / "bronce" / "datatur" / "Base70centros.csv"


def pytest_configure(config):
    config.addinivalue_line("markers", "red: requiere salida a internet (TDL_RED=1)")  # noqa: E501
    config.addinivalue_line("markers", "datos: requiere data/bronce poblado")


@pytest.fixture
def muestra_real():
    from extractores.datatur import leer_base70
    return leer_base70(FIXTURES / "base70_muestra_real.tsv")
