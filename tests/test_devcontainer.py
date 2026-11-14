"""Contenedor de desarrollo (.devcontainer/devcontainer.json): versión de Python, dependencias fijadas y protecciones de Streamlit.

El archivo original (commit f8811ac) usaba Python 3.11, instalaba ``streamlit`` sin versión, hacía ``apt upgrade`` y desactivaba CORS y
XSRF. Se cambió porque el proyecto usa Python 3.13 y dependencias fijadas, y porque esas dos protecciones no tenían una justificación técnica.
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DC = RAIZ / ".devcontainer" / "devcontainer.json"


def _config():
    texto = re.sub(r"^\s*//.*$", "", DC.read_text(encoding="utf-8"), flags=re.M)      # el formato admite comentarios de línea
    return json.loads(texto)


def test_usa_python_313_como_el_resto_del_proyecto():
    assert re.search(r"python:1-3\.13", _config()["image"])


def test_instala_las_dependencias_del_tablero_desde_el_bloqueo_con_hashes():
    cmd = _config()["updateContentCommand"]
    assert "--require-hashes" in cmd and "tablero/requirements.lock.txt" in cmd
    assert (RAIZ / "tablero" / "requirements.lock.txt").is_file()
    assert not re.search(r"pip3? install[^&;]*\bstreamlit\b(?!.*lock)", cmd.replace("tablero/requirements.lock.txt", ""))   # nada sin versión
    assert "apt upgrade" not in cmd and "apt-get upgrade" not in cmd                  # sin cambios de sistema no fijados


def test_no_desactiva_cors_ni_xsrf():
    texto = DC.read_text(encoding="utf-8").lower()
    assert "enablecors false" not in texto and "enablexsrfprotection false" not in texto
    assert "streamlit run tablero/streamlit_app.py" in "".join(_config()["postAttachCommand"].values())


def test_el_puerto_expuesto_es_el_de_streamlit_y_no_se_publica_un_secreto():
    c = _config()
    assert c["forwardPorts"] == [8501] and "8501" in c["portsAttributes"]
    assert not re.search(r"(?i)token|password|secret|api[_-]?key", DC.read_text(encoding="utf-8"))
