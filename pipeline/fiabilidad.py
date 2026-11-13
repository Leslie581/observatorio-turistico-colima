"""Fiabilidad y disponibilidad de la captura programada, medidas desde la bitácora (E1, Calidad).

    python -m pipeline.fiabilidad                      # imprime el informe JSON
    python -m pipeline.fiabilidad --escribir           # además lo guarda en calidad/fiabilidad_e1.json

Fuente única: ``calidad/bitacora_capturas.jsonl`` (una línea por ejecución; la escribe el extractor). Solo lectura de la bitácora,
sin red. El resultado es DETERMINISTA: la misma bitácora da el mismo informe (no lleva hora de cálculo).

Definiciones (documentadas en docs/E1/fiabilidad.md; no se ajustan después de ver los resultados):
  * Ejecución válida: ``resultado`` ``exito`` o ``fallo``. Las ``omitida_duplicada`` no cuentan (objetivo O1).
  * Tasa de éxito = éxitos / (éxitos + fallos).
  * Incidente = racha consecutiva de ejecuciones ``fallo``; termina en el siguiente ``exito``.
  * Tiempo de reparación de un incidente = ``fin_utc`` del primer éxito posterior − ``inicio_utc`` del primer fallo de la racha.
    Un incidente sin éxito posterior sigue ABIERTO y no entra en el MTTR.
  * MTTR = promedio de los tiempos de reparación de los incidentes cerrados.
  * MTBF = (tiempo observado − tiempo de reparación total) / número de incidentes. Solo se calcula con al menos
    ``MINIMO_INCIDENTES_MTBF`` (2) incidentes: con uno solo no hay un intervalo entre fallas y el valor sería una cota, no una estimación.
  * Disponibilidad A = MTBF / (MTBF + MTTR). Solo existe si existen MTBF y MTTR.
  * Cobertura diaria (descriptiva, no es A): días locales con al menos una captura exitosa / días locales con ejecuciones.
No se imputan valores: lo que no se puede calcular aparece como ``{"estimable": false, "motivo": ...}``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .config import RAIZ

BITACORA = RAIZ / "calidad" / "bitacora_capturas.jsonl"
SALIDA = RAIZ / "calidad" / "fiabilidad_e1.json"
OBJETIVO_O1 = 0.95            # calidad/objetivos.md (O1), fijado en E0
VENTANA_REQUERIDA_DIAS = 7    # rúbrica E1: «medidos con 7 días de bitácoras»
MINIMO_INCIDENTES_MTBF = 2
CRON_UTC = (13, 17)           # captura-diaria.yml: "17 13 * * *"


def _t(texto: str) -> datetime:
    d = datetime.fromisoformat(texto)
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _iso(d: datetime) -> str:
    return d.astimezone(timezone.utc).isoformat(timespec="seconds")


def cargar_bitacora(ruta: Path = BITACORA) -> list:
    ruta = Path(ruta)
    if not ruta.is_file():
        raise FileNotFoundError(f"no existe la bitácora: {ruta}")
    filas = [json.loads(x) for x in ruta.read_text(encoding="utf-8").splitlines() if x.strip()]
    return sorted(filas, key=lambda f: f["inicio_utc"])


def _incidentes(validas: list) -> list:
    """Rachas de fallos consecutivos; cada una cerrada por el siguiente éxito (o abierta si no lo hay)."""
    out, actual = [], None
    for f in validas:
        if f["resultado"] == "fallo":
            if actual is None:
                actual = {"inicio": _t(f["inicio_utc"]), "fallos": 0, "error": str(f.get("error") or "")[:80]}
            actual["fallos"] += 1
        elif actual is not None:  # éxito tras la racha: incidente cerrado
            fin = _t(f.get("fin_utc") or f["inicio_utc"])
            out.append({**actual, "recuperacion": fin, "reparacion_s": (fin - actual["inicio"]).total_seconds()})
            actual = None
    if actual is not None:
        out.append({**actual, "recuperacion": None, "reparacion_s": None})
    return out


def calcular(filas: list, objetivo: float = OBJETIVO_O1) -> dict:
    """Informe de fiabilidad de una lista de registros de bitácora. No modifica la entrada."""
    validas = [f for f in filas if f.get("resultado") in ("exito", "fallo")]
    omitidas = sum(f.get("resultado") == "omitida_duplicada" for f in filas)
    if not validas:
        return {"estado": "sin_datos", "motivo": "no hay ejecuciones exitosas ni fallidas", "registros": len(filas)}
    validas = sorted(validas, key=lambda f: f["inicio_utc"])
    exitos = sum(f["resultado"] == "exito" for f in validas)
    fallos = len(validas) - exitos
    tasa = exitos / len(validas)

    inicio = _t(validas[0]["inicio_utc"])
    fin = max(_t(f.get("fin_utc") or f["inicio_utc"]) for f in validas)
    dias = (fin - inicio).total_seconds() / 86400
    cumple_ventana = dias >= VENTANA_REQUERIDA_DIAS

    inc = _incidentes(validas)
    cerrados = [i for i in inc if i["reparacion_s"] is not None]
    abiertos = len(inc) - len(cerrados)
    mttr = sum(i["reparacion_s"] for i in cerrados) / len(cerrados) if cerrados else None

    observado_s = (fin - inicio).total_seconds()
    if len(inc) >= MINIMO_INCIDENTES_MTBF and cerrados:
        mtbf = (observado_s - sum(i["reparacion_s"] for i in cerrados)) / len(inc)
        mtbf_info = {"estimable": True, "segundos": round(mtbf, 1), "incidentes": len(inc)}
    else:
        ultimo_ok = [_t(f.get("fin_utc") or f["inicio_utc"]) for f in validas if f["resultado"] == "exito"]
        desde = cerrados[-1]["recuperacion"] if cerrados else None
        mtbf, mtbf_info = None, {
            "estimable": False,
            "motivo": f"hay {len(inc)} incidente(s); se necesitan al menos {MINIMO_INCIDENTES_MTBF} para tener un intervalo entre fallas",
            "tiempo_sin_fallas_desde_la_ultima_recuperacion_s": round((max(ultimo_ok) - desde).total_seconds(), 1) if desde and ultimo_ok else None,
            "nota_tiempo_sin_fallas": "dato CENSURADO por la derecha (no se observó una segunda falla): es una cota inferior, no el MTBF",
        }
    if mtbf is not None and mttr is not None:
        a = mtbf / (mtbf + mttr)
        disp = {"estimable": True, "valor": round(a, 6), "formula": "A = MTBF / (MTBF + MTTR)"}
    else:
        disp = {"estimable": False, "motivo": "requiere MTBF y MTTR; " + ("falta el MTBF" if mtbf is None else "falta el MTTR"),
                "formula": "A = MTBF / (MTBF + MTTR)"}

    por_dia = {}
    for f in validas:
        por_dia.setdefault(f["fecha_local"], []).append(f["resultado"])
    dias_con_captura = sum("exito" in v for v in por_dia.values())

    retrasos = []
    for f in validas:
        if f.get("disparador") == "schedule":
            t = _t(f["inicio_utc"])
            programada = t.replace(hour=CRON_UTC[0], minute=CRON_UTC[1], second=0, microsecond=0)
            retrasos.append({"ejecucion": f["ejecucion"], "retraso_min": round((t - programada).total_seconds() / 60, 1)})
    programadas = [f for f in validas if f.get("disparador") == "schedule"]

    avisos = []
    if not cumple_ventana:
        avisos.append(f"La bitácora cubre {dias:.2f} días; la rúbrica pide {VENTANA_REQUERIDA_DIAS}. El objetivo O1 («cualquier ventana de 7 días») no es evaluable todavía.")
    if len(cerrados) < 2:
        avisos.append(f"El MTTR se calcula con {len(cerrados)} incidente(s): es una observación, no una estimación estable.")
    if mtbf is None:
        avisos.append("MTBF y disponibilidad (A) no son estimables con los incidentes observados; no se sustituyen por valores supuestos.")
    return {
        "estado": "calculado",
        "fuente": "calidad/bitacora_capturas.jsonl",
        "registros_en_bitacora": len(filas),
        "ventana": {"inicio_utc": _iso(inicio), "fin_utc": _iso(fin), "dias": round(dias, 3),
                    "dias_requeridos": VENTANA_REQUERIDA_DIAS, "cumple_dias_requeridos": cumple_ventana},
        "ejecuciones": {"validas": len(validas), "exitosas": exitos, "fallidas": fallos, "omitidas_duplicadas_excluidas": omitidas,
                        "programadas_schedule": len(programadas), "programadas_exitosas": sum(f["resultado"] == "exito" for f in programadas)},
        "tasa_exito": {"valor": round(tasa, 4), "objetivo": objetivo, "cumple_objetivo_en_lo_observado": tasa >= objetivo,
                       "evaluable_como_se_definio_O1": cumple_ventana},
        "incidentes": {"total": len(inc), "cerrados": len(cerrados), "abiertos": abiertos,
                       "detalle": [{"inicio_utc": _iso(i["inicio"]), "fallos_consecutivos": i["fallos"], "causa_registrada": i["error"],
                                    "recuperacion_utc": _iso(i["recuperacion"]) if i["recuperacion"] else None,
                                    "reparacion_s": i["reparacion_s"]} for i in inc]},
        "mttr": {"estimable": mttr is not None, "segundos": round(mttr, 1) if mttr is not None else None, "incidentes_cerrados": len(cerrados)},
        "mtbf": mtbf_info,
        "disponibilidad_A": disp,
        "cobertura_diaria_descriptiva": {"dias_con_ejecucion": len(por_dia), "dias_con_captura_exitosa": dias_con_captura},
        "puntualidad_schedule": {"cron_utc": f"{CRON_UTC[0]:02d}:{CRON_UTC[1]:02d}", "retrasos": retrasos,
                                 "nota": "retraso = inicio real − hora programada del mismo día UTC"},
        "avisos": avisos,
    }


def informe(ruta: Path = BITACORA) -> dict:
    ruta = Path(ruta)
    res = calcular(cargar_bitacora(ruta))
    res["bitacora_sha256"] = hashlib.sha256(ruta.read_bytes()).hexdigest()
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Fiabilidad y disponibilidad de la captura (E1)")
    ap.add_argument("--bitacora", default=str(BITACORA))
    ap.add_argument("--escribir", action="store_true", help=f"guardar el informe en {SALIDA.relative_to(RAIZ)}")
    a = ap.parse_args(argv)
    try:
        res = informe(Path(a.bitacora))
    except Exception as e:  # noqa: BLE001 - error inesperado: se informa sin ocultarlo
        print(json.dumps({"estado": "error", "mensaje": f"{type(e).__name__}: {e}"}, ensure_ascii=False))
        return 1
    texto = json.dumps(res, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if a.escribir:
        SALIDA.write_bytes(texto.encode("utf-8"))
    sys.stdout.buffer.write(texto.encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
