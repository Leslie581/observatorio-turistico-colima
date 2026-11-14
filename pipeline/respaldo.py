"""Respaldo de la capa bronce con manifiesto SHA-256 y prueba de restauración (seguridad, rúbrica de Calidad).

    python -m pipeline.respaldo crear --destino <carpeta>          # zip + manifiesto, sin tocar el bronce
    python -m pipeline.respaldo verificar --zip <archivo.zip> --manifiesto <archivo.json>
    python -m pipeline.respaldo restaurar --zip <archivo.zip> --manifiesto <archivo.json> --destino <carpeta vacía>
    python -m pipeline.respaldo probar [--destino <carpeta>]       # crea el respaldo y lo restaura en un directorio temporal

Garantías: nunca escribe dentro de ``data/bronce/``, nunca sobrescribe un respaldo existente ni restaura sobre una carpeta que
tenga archivos, y solo usa la biblioteca estándar. El zip es determinista (fechas fijas y orden alfabético): el mismo bronce
produce el mismo zip. El manifiesto lista cada archivo con su tamaño y su SHA-256 y el SHA-256 del propio zip.
Límite: un respaldo en el mismo disco o la misma cuenta no es independiente; hay que copiarlo a otro lugar.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
import zipfile
from pathlib import Path

from .config import RAIZ

BRONCE = RAIZ / "data" / "bronce"
FECHA_FIJA_ZIP = (1980, 1, 1, 0, 0, 0)  # el zip no depende de la hora a la que se crea


class ErrorRespaldo(Exception):
    """El respaldo o la restauración no se puede hacer de forma segura."""


def sha256_archivo(ruta: Path) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def _archivos(bronce: Path) -> list[Path]:
    return sorted((p for p in Path(bronce).rglob("*") if p.is_file()), key=lambda p: p.relative_to(bronce).as_posix())


def generar_manifiesto(bronce: Path = BRONCE) -> dict:
    """Lista cada archivo del bronce con tamaño y SHA-256, ordenados por ruta."""
    bronce = Path(bronce)
    if not bronce.is_dir():
        raise ErrorRespaldo(f"no existe la carpeta del bronce: {bronce}")
    entradas = [{"ruta": p.relative_to(bronce).as_posix(), "bytes": p.stat().st_size, "sha256": sha256_archivo(p)} for p in _archivos(bronce)]
    if not entradas:
        raise ErrorRespaldo("el bronce no tiene archivos: no hay nada que respaldar")
    return {"algoritmo": "sha256", "archivos": entradas, "total_archivos": len(entradas), "total_bytes": sum(e["bytes"] for e in entradas)}


def _fuera_del_bronce(destino: Path, bronce: Path) -> None:
    d, b = Path(destino).resolve(), Path(bronce).resolve()
    if d == b or b in d.parents or d in b.parents:
        raise ErrorRespaldo(f"el destino no puede estar dentro ni contener al bronce ({d})")


def crear_respaldo(bronce: Path = BRONCE, destino: "Path | str" = ".", nombre: str = "bronce", creado_utc: "str | None" = None) -> dict:
    """Escribe ``<nombre>.zip`` y ``<nombre>.manifiesto.json`` en ``destino``. No sobrescribe nada."""
    bronce, destino = Path(bronce), Path(destino)
    _fuera_del_bronce(destino, bronce)
    ruta_zip, ruta_man = destino / f"{nombre}.zip", destino / f"{nombre}.manifiesto.json"
    if ruta_zip.exists() or ruta_man.exists():
        raise ErrorRespaldo(f"ya existe un respaldo con el nombre {nombre!r} en {destino}: no se sobrescribe")
    manifiesto = generar_manifiesto(bronce)
    destino.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ruta_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for e in manifiesto["archivos"]:
            info = zipfile.ZipInfo(e["ruta"], FECHA_FIJA_ZIP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, (bronce / e["ruta"]).read_bytes())
    manifiesto["zip"] = {"archivo": ruta_zip.name, "bytes": ruta_zip.stat().st_size, "sha256": sha256_archivo(ruta_zip)}
    if creado_utc:
        manifiesto["creado_utc"] = creado_utc
    ruta_man.write_bytes((json.dumps(manifiesto, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    return {"zip": ruta_zip, "manifiesto": ruta_man, **{k: manifiesto[k] for k in ("total_archivos", "total_bytes")}}


def _leer_manifiesto(ruta: Path) -> dict:
    m = json.loads(Path(ruta).read_text(encoding="utf-8"))
    if m.get("algoritmo") != "sha256" or not m.get("archivos"):
        raise ErrorRespaldo("el manifiesto no es válido (falta el algoritmo o la lista de archivos)")
    return m


def verificar_respaldo(ruta_zip: Path, ruta_manifiesto: Path) -> dict:
    """Comprueba el zip contra el manifiesto: hash del zip, mismos archivos y hash de cada uno. No extrae nada a disco."""
    m, fallos = _leer_manifiesto(ruta_manifiesto), []
    if "zip" in m and m["zip"]["sha256"] != sha256_archivo(Path(ruta_zip)):
        fallos.append({"archivo": Path(ruta_zip).name, "motivo": "el SHA-256 del zip no coincide con el del manifiesto"})
    esperado = {e["ruta"]: e for e in m["archivos"]}
    with zipfile.ZipFile(ruta_zip) as z:
        if z.testzip() is not None:
            fallos.append({"archivo": z.testzip(), "motivo": "entrada del zip dañada"})
        presentes = {i.filename for i in z.infolist() if not i.is_dir()}
        for falta in sorted(set(esperado) - presentes):
            fallos.append({"archivo": falta, "motivo": "falta en el zip"})
        for sobra in sorted(presentes - set(esperado)):
            fallos.append({"archivo": sobra, "motivo": "el zip trae un archivo que el manifiesto no declara"})
        for ruta in sorted(presentes & set(esperado)):
            datos = z.read(ruta)
            if hashlib.sha256(datos).hexdigest() != esperado[ruta]["sha256"] or len(datos) != esperado[ruta]["bytes"]:
                fallos.append({"archivo": ruta, "motivo": "SHA-256 o tamaño distinto al del manifiesto"})
    return {"ok": not fallos, "archivos": len(esperado), "fallos": fallos}


def restaurar(ruta_zip: Path, ruta_manifiesto: Path, destino: Path, bronce: Path = BRONCE) -> dict:
    """Extrae el respaldo en una carpeta vacía y comprueba cada archivo restaurado contra el manifiesto."""
    destino = Path(destino)
    _fuera_del_bronce(destino, bronce)
    if destino.exists() and any(destino.iterdir()):
        raise ErrorRespaldo(f"el destino {destino} no está vacío: no se restaura sobre archivos existentes")
    previo = verificar_respaldo(ruta_zip, ruta_manifiesto)
    if not previo["ok"]:
        raise ErrorRespaldo(f"el respaldo no pasa la verificación: {previo['fallos'][:3]}")
    m = _leer_manifiesto(ruta_manifiesto)
    destino.mkdir(parents=True, exist_ok=True)
    raiz = destino.resolve()
    with zipfile.ZipFile(ruta_zip) as z:
        for e in m["archivos"]:
            objetivo = (raiz / e["ruta"]).resolve()
            if raiz not in objetivo.parents:                                          # sin rutas que salgan de la carpeta (zip-slip)
                raise ErrorRespaldo(f"ruta peligrosa en el respaldo: {e['ruta']}")
            objetivo.parent.mkdir(parents=True, exist_ok=True)
            objetivo.write_bytes(z.read(e["ruta"]))
    fallos = [{"archivo": e["ruta"], "motivo": "el archivo restaurado no coincide con el manifiesto"}
              for e in m["archivos"] if sha256_archivo(raiz / e["ruta"]) != e["sha256"]]
    return {"ok": not fallos, "restaurados": len(m["archivos"]), "destino": str(raiz), "fallos": fallos}


def comparar_con_origen(ruta_manifiesto: Path, bronce: Path = BRONCE) -> dict:
    """¿El bronce actual conserva, sin cambios, todo lo que declara el manifiesto? Los archivos nuevos (capturas) no son un fallo."""
    m, bronce = _leer_manifiesto(ruta_manifiesto), Path(bronce)
    modificados, ausentes = [], []
    for e in m["archivos"]:
        f = bronce / e["ruta"]
        if not f.is_file():
            ausentes.append(e["ruta"])
        elif sha256_archivo(f) != e["sha256"]:
            modificados.append(e["ruta"])
    declarados = {e["ruta"] for e in m["archivos"]}
    nuevos = sorted(p.relative_to(bronce).as_posix() for p in _archivos(bronce) if p.relative_to(bronce).as_posix() not in declarados)
    return {"ok": not modificados and not ausentes, "modificados": modificados, "ausentes": ausentes, "nuevos_desde_el_manifiesto": nuevos}


def probar(bronce: Path = BRONCE, destino: "Path | None" = None) -> dict:
    """Crea el respaldo, lo verifica y lo restaura en un directorio temporal; compara lo restaurado con el origen."""
    bronce = Path(bronce)
    with tempfile.TemporaryDirectory(prefix="respaldo_bronce_") as tmp:
        base = Path(destino) if destino else Path(tmp) / "respaldo"
        creado = crear_respaldo(bronce, base, "bronce")
        verificacion = verificar_respaldo(creado["zip"], creado["manifiesto"])
        restauracion = restaurar(creado["zip"], creado["manifiesto"], Path(tmp) / "restaurado", bronce)
        origen = comparar_con_origen(creado["manifiesto"], Path(tmp) / "restaurado")   # lo restaurado contra el manifiesto
        contra_bronce = comparar_con_origen(creado["manifiesto"], bronce)
        return {"ok": verificacion["ok"] and restauracion["ok"] and origen["ok"] and contra_bronce["ok"],
                "archivos": creado["total_archivos"], "bytes": creado["total_bytes"], "verificacion_del_zip": verificacion["ok"],
                "restauracion": restauracion["ok"], "restaurado_igual_al_manifiesto": origen["ok"], "bronce_igual_al_manifiesto": contra_bronce["ok"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="orden", required=True)
    c = sub.add_parser("crear")
    c.add_argument("--destino", required=True)
    c.add_argument("--nombre", default="bronce")
    v = sub.add_parser("verificar")
    v.add_argument("--zip", required=True)
    v.add_argument("--manifiesto", required=True)
    r = sub.add_parser("restaurar")
    r.add_argument("--zip", required=True)
    r.add_argument("--manifiesto", required=True)
    r.add_argument("--destino", required=True)
    p = sub.add_parser("probar")
    p.add_argument("--destino")
    a = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        if a.orden == "crear":
            res = crear_respaldo(BRONCE, a.destino, a.nombre)
        elif a.orden == "verificar":
            res = verificar_respaldo(Path(a.zip), Path(a.manifiesto))
        elif a.orden == "restaurar":
            res = restaurar(Path(a.zip), Path(a.manifiesto), Path(a.destino))
        else:
            res = probar(BRONCE, Path(a.destino) if a.destino else None)
    except ErrorRespaldo as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps(res, ensure_ascii=False, indent=2, default=str))
    return 0 if res.get("ok", True) else 2


if __name__ == "__main__":
    sys.exit(main())
