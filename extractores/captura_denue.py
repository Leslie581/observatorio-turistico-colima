"""Captura diaria del DENUE (INEGI): fuente programada del Observatorio.

Uso local:
    python -m extractores.captura_denue            # una captura por día (idempotente)
    python -m extractores.captura_denue --forzar   # repite aunque ya exista la de hoy

Qué hace una ejecución (5 solicitudes HTTP como máximo, pausa >= 1.5 s):
1. Comprueba si ya existe la captura del día (hora de Ciudad de México) y, si es así,
   termina sin pedir nada a la API (``omitida_duplicada``), salvo ``--forzar``.
2. Lee el token de la variable de entorno ``INEGI_TOKEN`` (en GitHub: secreto del
   repositorio). Sin token falla de forma explícita; nunca imprime ni guarda el token.
3. Consulta ``Cuantificar`` y ``BuscarAreaAct`` (Colima 06 / Manzanillo 007 / SCIAN 721).
4. Guarda en bronce, particionado por fuente y fecha, las respuestas SIN datos
   personales (ver ``denue.sanitizar_crudo``) con su ``.meta.json`` (SHA-256, URL con el
   token enmascarado, HTTP, encabezados, ejecución).
5. Aplica los controles de ``denue.validar`` y los registra. La validación NO bloquea la
   escritura en bronce (el bronce conserva lo que llegó); un control fallido marca la
   ejecución como fallida para que se vea en la bitácora y en el workflow.
6. Añade UNA línea a ``calidad/bitacora_capturas.jsonl`` (bitácora de ejecuciones, base
   de la medición de fiabilidad de E1). Los eventos HTTP detallados van a
   ``logs/bitacora.jsonl`` (fuera de Git).

Código de salida: 0 = éxito u omitida por duplicada; 1 = fallo.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from . import denue
from .base import BRONCE, RAIZ, Bitacora, ExtractorEtico, ocultar_credenciales

ZONA = ZoneInfo("America/Mexico_City")
BITACORA_EJECUCIONES = RAIZ / "calidad" / "bitacora_capturas.jsonl"
BITACORA_HTTP = RAIZ / "logs" / "bitacora.jsonl"
FUENTE_ID = "denue"


def fecha_local(ahora: datetime | None = None) -> str:
    return (ahora or datetime.now(timezone.utc)).astimezone(ZONA).strftime("%Y-%m-%d")


def _relativa(ruta: Path, bronce: Path) -> str:
    """Ruta con barras normales relativa a la carpeta que contiene ``data/`` (si aplica)."""
    r, raiz = Path(ruta).resolve(), Path(bronce).resolve().parent.parent
    return (r.relative_to(raiz) if raiz in r.parents else r).as_posix()


def captura_existente(fecha: str, bronce: Path = BRONCE) -> bool:
    """True si el bronce ya tiene las dos respuestas del día (Cuantificar y BuscarAreaAct)."""
    carpeta = Path(bronce) / "denue" / fecha
    return (carpeta.is_dir() and any(carpeta.glob("*_Cuantificar.json"))
            and any(carpeta.glob("*_BuscarAreaAct.json")))


def registrar_ejecucion(fila: dict, ruta: Path = BITACORA_EJECUCIONES) -> dict:
    fila = ocultar_credenciales(fila)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(fila, ensure_ascii=False, sort_keys=True, default=str) + "\n")
    return fila


def ejecutar(forzar: bool = False, bronce: Path = BRONCE, bitacora_ejecuciones: Path = BITACORA_EJECUCIONES,
             bitacora_http: Path = BITACORA_HTTP, ex: ExtractorEtico | None = None,
             ahora: datetime | None = None) -> dict:
    t0 = time.time()
    inicio = ahora or datetime.now(timezone.utc)
    ejecucion = inicio.strftime("%Y%m%dT%H%M%SZ")
    fecha = fecha_local(inicio)
    fila = {
        "ejecucion": ejecucion, "fuente": FUENTE_ID, "fecha_local": fecha,
        "inicio_utc": inicio.isoformat(timespec="seconds"),
        "disparador": os.getenv("GITHUB_EVENT_NAME") or "local",
        "github_run_id": os.getenv("GITHUB_RUN_ID") or None,
        "github_run_attempt": os.getenv("GITHUB_RUN_ATTEMPT") or None,
        "resultado": "fallo", "error": None,
    }

    if not forzar and captura_existente(fecha, bronce):
        fila.update(resultado="omitida_duplicada", error=None,
                    nota="Ya existe la captura de esta fecha en bronce; no se consultó la API")
        fila["duracion_s"] = round(time.time() - t0, 2)
        return registrar_ejecucion(fila, bitacora_ejecuciones)

    bit = Bitacora(bitacora_http, ejecucion_id=ejecucion)
    cli = None
    try:
        ex = ex or ExtractorEtico(bitacora=bit)
        cli = denue.ClienteDenue(ex)  # lanza TokenNoConfigurado si falta INEGI_TOKEN
        resp_cuant = cli.cuantificar()
        esperado = denue.total_cuantificar(resp_cuant)
        registros = cli.buscar_area_act()
        rutas = denue.guardar_respuestas_crudas(cli, ejecucion, bronce=bronce, particion=fecha)
        validos, cuarentena = denue.normalizar(registros)
        validacion = denue.validar(registros, validos, cuarentena, esperado)
        bit.registrar("denue_validacion", **validacion)
        fila.update(
            resultado="exito" if (registros and validacion["ok"]) else "fallo",
            http=[{"metodo": r["metodo"], "estado": r["estado_http"], "sha256_respuesta": r["sha256"],
                   "bytes": r["bytes"]} for r in cli.respuestas],
            registros=len(registros), esperado_cuantificar=esperado,
            validos=int(len(validos)), cuarentena=int(len(cuarentena)),
            controles_fallidos=[c["control"] for c in validacion["controles"] if not c["ok"]],
            archivos_bronce=[_relativa(r, bronce) for r in rutas],
        )
        if fila["resultado"] == "fallo":
            fila["error"] = "controles de calidad fallidos: " + ", ".join(fila["controles_fallidos"] or ["sin registros"])
    except denue.TokenNoConfigurado as e:
        fila.update(resultado="fallo", error=f"sin_token: {e}")
    except Exception as e:  # noqa: BLE001 - se registra y se devuelve código 1
        fila.update(resultado="fallo", error=f"{type(e).__name__}: {e}")
        if cli is not None and cli.respuestas:  # conservar lo que sí respondió la API
            try:
                denue.guardar_respuestas_crudas(cli, ejecucion, bronce=bronce, particion=fecha)
            except Exception as e2:  # noqa: BLE001
                fila["error"] += f" | además falló guardar bronce: {type(e2).__name__}"
    fila["fin_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    fila["duracion_s"] = round(time.time() - t0, 2)
    return registrar_ejecucion(fila, bitacora_ejecuciones)


def cargar_env(ruta: Path = RAIZ / ".env") -> None:
    """Carga .env (si existe) sin sobrescribir variables ya definidas."""
    try:
        from dotenv import load_dotenv
        load_dotenv(ruta, override=False)
    except ImportError:
        pass


def main(argv=None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    p = argparse.ArgumentParser(description="Captura diaria del DENUE (hospedaje en Manzanillo)")
    p.add_argument("--forzar", action="store_true", help="Capturar aunque ya exista la captura de hoy")
    args = p.parse_args(argv)
    cargar_env()
    sys.path.insert(0, str(RAIZ))
    fila = ejecutar(forzar=args.forzar)
    print(json.dumps({k: fila.get(k) for k in ("ejecucion", "fecha_local", "resultado", "registros",
                                              "esperado_cuantificar", "controles_fallidos", "error")},
                     ensure_ascii=False, indent=2))
    return 0 if fila["resultado"] in ("exito", "omitida_duplicada") else 1


if __name__ == "__main__":
    raise SystemExit(main())
