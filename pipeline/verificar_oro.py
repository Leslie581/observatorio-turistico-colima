"""Comprueba que el oro REGENERADO coincide con el oro VERSIONADO en git (puerta de CI).

Se ejecuta DESPUÉS de ``python -m pipeline.ejecutar``: éste reescribe ``data/oro/`` en el área de trabajo y aquí se compara
cada archivo con la copia que está en el commit (``git show <ref>:<ruta>``). Así un cambio de código o de datos que altere el
oro sin actualizar el archivo versionado hace fallar el CI, en vez de pasar desapercibido.

Qué se exige y qué no (y por qué):
  * ``manzanillo_ocupacion_mensual.csv`` y ``diccionario_datos.csv``: igualdad byte a byte. Dependen solo de Base70 (congelado)
    y del código; no cambian con las capturas diarias.
  * ``manzanillo_ocupacion_mensual.meta.json``: igualdad de todos los campos SALVO los variables, ``fecha_proceso_utc`` (hora
    de la corrida) y ``corrida`` (incluye el hash de las capturas DENUE, que crecen a diario).
  * ``manzanillo_oferta_hospedaje.csv`` y su ``.meta.json``: NO se exigen; cuentan establecimientos por día de captura DENUE y
    cambian legítimamente con cada captura del bot. Se informan como no comparados.

Códigos de salida: 0 = coincide; 2 = hay diferencias (o un archivo falta en el commit); 1 = error inesperado.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from .config import RAIZ

ESTRICTOS = ("data/oro/manzanillo_ocupacion_mensual.csv", "data/oro/diccionario_datos.csv")
META = "data/oro/manzanillo_ocupacion_mensual.meta.json"
CAMPOS_VARIABLES_META = ("fecha_proceso_utc", "corrida")
NO_COMPARADOS = ("data/oro/manzanillo_oferta_hospedaje.csv", "data/oro/manzanillo_oferta_hospedaje.meta.json")


def _versionado(raiz: Path, ruta: str, ref: str) -> "bytes | None":
    r = subprocess.run(["git", "-C", str(raiz), "show", f"{ref}:{ruta}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def _sin_variables(datos: bytes) -> dict:
    d = json.loads(datos.decode("utf-8"))
    return {k: v for k, v in d.items() if k not in CAMPOS_VARIABLES_META}


def comparar(raiz: Path = RAIZ, ref: str = "HEAD") -> dict:
    """Devuelve ``{"ok": bool, "diferencias": [...], "no_comparados": [...]}``."""
    raiz = Path(raiz)
    dif = []
    for ruta in (*ESTRICTOS, META):
        local = raiz / ruta
        versionado = _versionado(raiz, ruta, ref)
        if versionado is None:
            dif.append({"archivo": ruta, "motivo": f"no está versionado en {ref}"})
            continue
        if not local.is_file():
            dif.append({"archivo": ruta, "motivo": "el pipeline no lo regeneró"})
            continue
        actual = local.read_bytes()
        if ruta == META:
            a, v = _sin_variables(actual), _sin_variables(versionado)
            if a != v:
                campos = sorted(k for k in a.keys() | v.keys() if a.get(k) != v.get(k))
                dif.append({"archivo": ruta, "motivo": "metadatos distintos (sin contar campos de tiempo)", "campos": campos})
        elif actual != versionado:
            dif.append({"archivo": ruta, "motivo": "el contenido regenerado difiere del versionado",
                        "bytes_regenerado": len(actual), "bytes_versionado": len(versionado)})
    return {"ok": not dif, "referencia": ref, "diferencias": dif, "no_comparados": list(NO_COMPARADOS)}


def main(argv=None) -> int:
    try:
        res = comparar()
    except Exception as e:  # noqa: BLE001 - error inesperado: se informa sin ocultarlo
        print(json.dumps({"ok": False, "error_inesperado": f"{type(e).__name__}: {e}"}, ensure_ascii=False))
        return 1
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0 if res["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
