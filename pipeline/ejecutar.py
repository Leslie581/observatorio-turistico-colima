"""Orquestador bronce -> plata -> oro con puerta de calidad y cuarentena (contrato 1.0.0).

    python -m pipeline.ejecutar

Códigos de salida: 0 = correcto; 2 = la puerta de calidad impide una salida confiable (no se escribe plata ni oro,
solo un resumen de la falla en data/cuarentena/); 1 = error inesperado. Nunca modifica data/bronce/.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


from . import oro as o
from .calidad.cuarentena import Cuarentena, ErrorPuertaCalidad, csv_bytes, escribir_atomico
from .config import ATRIBUCION, RAIZ, VERSION_CONTRATO, rutas
from .plata_datatur import procesar_base70
from .plata_denue import listar_capturas, procesar_capturas


def _json(d: dict) -> bytes:
    return (json.dumps(d, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def id_corrida(sha_base70: str, bronce_denue: Path) -> str:
    """Determinista: la misma entrada produce la misma identificación (y los mismos archivos)."""
    shas = sorted(json.loads(Path(str(p) + ".meta.json").read_text(encoding="utf-8")).get("sha256", "")
                  for p in listar_capturas(bronce_denue) if Path(str(p) + ".meta.json").is_file())
    return "e1-" + hashlib.sha256("|".join([sha_base70, *shas]).encode()).hexdigest()[:12]


def ejecutar(raiz: Path = RAIZ, ahora: "str | None" = None) -> dict:
    ahora = ahora or datetime.now(timezone.utc).isoformat(timespec="seconds")
    r = rutas(raiz)
    cuar = Cuarentena(ahora)
    try:
        plata_d, sha = procesar_base70(r["base70"], cuar)
        plata_e = procesar_capturas(r["bronce_denue"], cuar)
        oro_m = o.construir_oro_mensual(plata_d, sha)
        oro_o = o.construir_oferta_hospedaje(plata_e)
        corrida = id_corrida(sha, r["bronce_denue"])
    except ErrorPuertaCalidad as e:
        cuar.informativo["error_controlado"] = {"regla": e.regla, "mensaje": e.mensaje}
        ruta = r["cuarentena"] / f"resumen_fallida-{ahora.replace(':', '').replace('-', '')[:15]}.json"
        escribir_atomico(ruta, _json(cuar.resumen()))
        return {"estado": "error_controlado", "regla": e.regla, "mensaje": e.mensaje,
                "resumen": str(ruta.relative_to(raiz)) if raiz in ruta.parents else str(ruta)}

    # todo se calculó y validó: recién ahora se escribe (salidas atómicas, bronce intacto)
    csv_m, csv_o = csv_bytes(oro_m), csv_bytes(oro_o)
    meta_m = {"archivo": "manzanillo_ocupacion_mensual.csv", "filas": len(oro_m), "periodo_min": oro_m.periodo.iloc[0],
              "periodo_max": oro_m.periodo.iloc[-1], "sha256_csv": o.hash_bytes(csv_m), "sha256_bronce": sha,
              "version_contrato": VERSION_CONTRATO, "ejecucion": oro_m.ejecucion.iloc[0], "corrida": corrida,
              "fecha_proceso_utc": ahora, "definicion_objetivo": "100 x suma(ocupados residentes + no residentes) / suma(disponibles), "
              "categorias 2 a 5 estrellas de Manzanillo (cociente de sumas)", "atribucion": ATRIBUCION["datatur"]}
    meta_o = {"archivo": "manzanillo_oferta_hospedaje.csv", "filas": len(oro_o), "sha256_csv": o.hash_bytes(csv_o),
              "version_contrato": VERSION_CONTRATO, "corrida": corrida, "fecha_proceso_utc": ahora,
              "nota": "contexto agregado por municipio, sin coordenadas ni CLEE; no se asigna ocupación a establecimientos",
              "atribucion": ATRIBUCION["denue"]}
    escritos = {
        r["plata"] / "datatur_base70.csv": csv_bytes(plata_d),
        r["plata"] / "denue_establecimientos.csv": csv_bytes(plata_e),
        r["oro"] / "manzanillo_ocupacion_mensual.csv": csv_m,
        r["oro"] / "manzanillo_ocupacion_mensual.meta.json": _json(meta_m),
        r["oro"] / "manzanillo_oferta_hospedaje.csv": csv_o,
        r["oro"] / "manzanillo_oferta_hospedaje.meta.json": _json(meta_o),
        r["oro"] / "diccionario_datos.csv": csv_bytes(o.diccionario_df()),
    }
    for ruta, contenido in escritos.items():
        escribir_atomico(ruta, contenido)
    cuar_paths = cuar.escribir(r["cuarentena"], corrida)
    res = cuar.resumen()
    return {"estado": "ok", "corrida": corrida,
            "plata": {"datatur_base70": len(plata_d), "denue_establecimientos": len(plata_e)},
            "oro": {"manzanillo_ocupacion_mensual": len(oro_m), "manzanillo_oferta_hospedaje": len(oro_o)},
            "calidad": res["fuentes"], "lotes_rechazados": res["lotes_rechazados"],
            "archivos": sorted(str(p.relative_to(raiz)).replace("\\", "/") for p in [*escritos, *cuar_paths])}


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        res = ejecutar()
    except Exception as e:  # noqa: BLE001 - error inesperado: se informa sin ocultarlo
        print(json.dumps({"estado": "error_inesperado", "tipo": type(e).__name__, "mensaje": str(e)}, ensure_ascii=False))
        return 1
    print(json.dumps(res, ensure_ascii=False, indent=2, default=str))
    return 0 if res["estado"] == "ok" else 2


if __name__ == "__main__":
    sys.exit(main())
