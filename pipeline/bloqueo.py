"""Archivo de bloqueo con hashes (SHA-256) para las dependencias del tablero.

    # 1) entorno nuevo con SOLO tablero/requirements.txt; 2) su cierre exacto; 3) bloqueo con los hashes de PyPI
    python -m venv entorno_nuevo && entorno_nuevo/bin/pip install -r tablero/requirements.txt
    entorno_nuevo/bin/pip freeze > cierre.txt
    python -m pipeline.bloqueo generar --cierre cierre.txt --escribir      # consulta la API JSON de PyPI
    python -m pipeline.bloqueo verificar                                    # sin red: estructura y coherencia del bloqueo

``tablero/requirements.txt`` fija solo 4 dependencias directas; las otras 30 las resuelve ``pip`` cuando alguien instala. El
bloqueo fija el cierre completo y exige el hash de cada archivo (``pip install --require-hashes``), de modo que un paquete
reemplazado en el índice con el mismo número de versión no se instala. Límites: los hashes son los publicados por PyPI
(prueban que el archivo no cambió desde que se generó el bloqueo, no que el paquete sea benigno) y Streamlit Community Cloud
sigue leyendo ``tablero/requirements.txt``, no este archivo.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Callable

from .config import RAIZ

DIRECTAS = RAIZ / "tablero" / "requirements.txt"
BLOQUEO = RAIZ / "tablero" / "requirements.lock.txt"
CABECERA = (
    "# Archivo de bloqueo del tablero: cierre transitivo EXACTO de tablero/requirements.txt con el SHA-256 de cada distribucion publicada en PyPI.\n"
    "# Generado el {fecha} (Python 3.13; la resolucion para Linux y para Windows dio los mismos {n} paquetes). Instalar: pip install --require-hashes -r tablero/requirements.lock.txt\n"
    "# Lo usan CI (instalacion con hashes y pip-audit) y quien quiera reproducir el entorno. Streamlit Community Cloud sigue leyendo tablero/requirements.txt.\n"
    "# Para regenerarlo: python -m pipeline.bloqueo generar --cierre <pip freeze de un entorno nuevo> --escribir (consulta la API JSON de PyPI)\n"
)
LINEA_PAQUETE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)==([^\s\\]+)\s*\\?\s*$")
LINEA_HASH = re.compile(r"^\s+--hash=sha256:([0-9a-f]{64})\s*\\?\s*$")


def normalizar(nombre: str) -> str:
    return re.sub(r"[-_.]+", "-", nombre).lower()


def leer_pines(ruta: Path) -> dict:
    """``{nombre: version}`` de un archivo con líneas ``nombre==version`` (ignora comentarios y vacías)."""
    pines = {}
    for linea in Path(ruta).read_text(encoding="utf-8").splitlines():
        s = linea.strip()
        if s and not s.startswith("#") and "==" in s:
            n, v = s.split("==", 1)
            pines[normalizar(n)] = v.strip()
    return pines


def hashes_de_pypi(nombre: str, version: str) -> list:
    with urllib.request.urlopen(f"https://pypi.org/pypi/{nombre}/{version}/json", timeout=60) as r:
        datos = json.load(r)
    return sorted({u["digests"]["sha256"] for u in datos["urls"]})


def generar(cierre: dict, directas: dict, fecha: str, obtener_hashes: Callable[[str, str], list] = hashes_de_pypi) -> str:
    """Texto del bloqueo. Falla si una dependencia directa no está en el cierre con la misma versión o si un paquete no tiene hashes."""
    for n, v in directas.items():
        if cierre.get(n) != v:
            raise ValueError(f"la dependencia directa {n}=={v} no está en el cierre con esa versión ({cierre.get(n)})")
    bloques = []
    for nombre in sorted(cierre):
        hs = obtener_hashes(nombre, cierre[nombre])
        if not hs:
            raise ValueError(f"{nombre}=={cierre[nombre]} no tiene archivos con hash publicados")
        bloques.append(f"{nombre}=={cierre[nombre]} \\\n" + " \\\n".join(f"    --hash=sha256:{h}" for h in hs))
    return CABECERA.format(fecha=fecha, n=len(cierre)) + "\n".join(bloques) + "\n"


def analizar(texto: str) -> dict:
    """``{nombre: (version, [hashes])}`` y los problemas de estructura que encuentre (sin red)."""
    paquetes, problemas, actual = {}, [], None
    for linea in texto.splitlines():
        if not linea.strip() or linea.lstrip().startswith("#"):
            continue
        m = LINEA_PAQUETE.match(linea)
        if m and not linea.startswith(" "):
            actual = normalizar(m.group(1))
            if actual in paquetes:
                problemas.append(f"{actual}: aparece dos veces")
            paquetes[actual] = (m.group(2), [])
            continue
        h = LINEA_HASH.match(linea)
        if h and actual:
            paquetes[actual][1].append(h.group(1))
        else:
            problemas.append(f"línea no reconocida: {linea[:60]!r}")
    return {"paquetes": paquetes, "problemas": problemas}


def verificar(ruta_bloqueo: Path = BLOQUEO, ruta_directas: Path = DIRECTAS) -> dict:
    """Sin red: cada paquete tiene hashes SHA-256 sin repetir y las dependencias directas están con su versión exacta."""
    a = analizar(Path(ruta_bloqueo).read_text(encoding="utf-8"))
    problemas = list(a["problemas"])
    for n, (v, hs) in a["paquetes"].items():
        if not hs:
            problemas.append(f"{n}=={v}: sin hashes")
        if len(hs) != len(set(hs)):
            problemas.append(f"{n}=={v}: hashes repetidos")
    for n, v in leer_pines(ruta_directas).items():
        if n not in a["paquetes"] or a["paquetes"][n][0] != v:
            problemas.append(f"la dependencia directa {n}=={v} no está en el bloqueo con esa versión")
    return {"ok": not problemas, "paquetes": len(a["paquetes"]), "hashes": sum(len(h) for _, h in a["paquetes"].values()), "problemas": problemas}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="orden", required=True)
    g = sub.add_parser("generar")
    g.add_argument("--cierre", required=True, help="salida de `pip freeze` de un entorno nuevo con solo tablero/requirements.txt")
    g.add_argument("--fecha", required=True, help="fecha de generación (AAAA-MM-DD)")
    g.add_argument("--escribir", action="store_true", help="escribe tablero/requirements.lock.txt (si no, solo imprime)")
    sub.add_parser("verificar")
    a = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if a.orden == "verificar":
        res = verificar()
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0 if res["ok"] else 2
    texto = generar(leer_pines(Path(a.cierre)), leer_pines(DIRECTAS), a.fecha)
    if a.escribir:
        BLOQUEO.write_bytes(texto.encode("utf-8"))
        print(f"escrito {BLOQUEO.relative_to(RAIZ)}")
    else:
        print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
