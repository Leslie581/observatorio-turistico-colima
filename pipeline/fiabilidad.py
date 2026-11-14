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
  * El mínimo de 2 incidentes para el MTBF es un criterio METODOLÓGICO INTERNO de este proyecto, no un requisito de la rúbrica (la rúbrica
    pide 7 días de bitácora).
  * Estimación EXPLORATORIA (clave ``estimacion_exploratoria``, solo si hay ≥ 1 incidente cerrado): MTBF = T / r con T = tiempo observado − reparación
    total y r = incidentes (máxima verosimilitud con tasa de fallos constante, observación truncada por tiempo); intervalo de confianza exacto
    (Epstein) con la ji cuadrada de 2r + 2 y 2r grados de libertad; A = MTBF / (MTBF + MTTR). No sustituye a las magnitudes de arriba y se presenta
    siempre con su intervalo y sus supuestos. Con un solo incidente, A puntual coincide con 1 − reparación / ventana (disponibilidad observada por tiempo).
No se imputan valores: lo que no se puede calcular aparece como ``{"estimable": false, "motivo": ...}``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from math import comb, exp, factorial
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


def _ji2_cdf_gl_par(x: float, gl: int) -> float:
    """Función de distribución de la ji cuadrada con grados de libertad PARES (forma cerrada con la suma de Poisson)."""
    k, m = gl // 2, x / 2
    return 1.0 - exp(-m) * sum(m ** j / factorial(j) for j in range(k))


def ji2_cuantil_gl_par(p: float, gl: int) -> float:
    """Cuantil de la ji cuadrada con ``gl`` PAR, por bisección (Python puro; el núcleo no depende de scipy)."""
    if gl % 2 or gl < 2 or not 0 < p < 1:
        raise ValueError("gl debe ser par y p estar entre 0 y 1")
    alto = 1.0
    while _ji2_cdf_gl_par(alto, gl) < p:
        alto *= 2
    bajo = 0.0
    for _ in range(200):
        medio = (bajo + alto) / 2
        bajo, alto = (medio, alto) if _ji2_cdf_gl_par(medio, gl) < p else (bajo, medio)
    return (bajo + alto) / 2


def intervalo_mtbf_epstein(tiempo_s: float, fallas: int, confianza: float = 0.90) -> tuple:
    """Intervalo de confianza exacto del MTBF (tasa de fallos constante, prueba truncada por tiempo, r ≥ 1), en segundos."""
    if fallas < 1 or tiempo_s <= 0:
        raise ValueError("se necesita al menos 1 falla y un tiempo positivo")
    a = 1 - confianza
    inferior = 2 * tiempo_s / ji2_cuantil_gl_par(1 - a / 2, 2 * fallas + 2)
    superior = 2 * tiempo_s / ji2_cuantil_gl_par(a / 2, 2 * fallas)
    return inferior, superior


def intervalo_clopper_pearson(exitos: int, n: int, confianza: float = 0.95) -> tuple:
    """Intervalo exacto de Clopper-Pearson para una proporción (bisección sobre la cola binomial)."""
    a = 1 - confianza

    def cola_sup(p):  # P(X >= exitos)
        return sum(comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(exitos, n + 1))

    def cola_inf(p):  # P(X <= exitos)
        return sum(comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(0, exitos + 1))

    def biseccion(f, objetivo, creciente):
        lo, hi = 0.0, 1.0
        for _ in range(200):
            m = (lo + hi) / 2
            if (f(m) < objetivo) == creciente:
                lo = m
            else:
                hi = m
        return (lo + hi) / 2

    inferior = 0.0 if exitos == 0 else biseccion(cola_sup, a / 2, True)
    superior = 1.0 if exitos == n else biseccion(cola_inf, a / 2, False)
    return inferior, superior


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

    reparacion_total = sum(i["reparacion_s"] for i in cerrados)
    explor = None
    if cerrados:
        t_oper = observado_s - reparacion_total
        r_inc = len(inc)
        m_h = t_oper / r_inc / 3600
        lo_s, hi_s = intervalo_mtbf_epstein(t_oper, r_inc, 0.90)
        mttr_prom = mttr
        a_ = lambda m_s: m_s / (m_s + mttr_prom)  # noqa: E731
        explor = {
            "estado": "EXPLORATORIA: no sustituye a las magnitudes medidas ni a la tasa de éxito",
            "metodo": "MTBF = T / r (máxima verosimilitud, tasa de fallos constante, observación truncada por tiempo); IC exacto de Epstein",
            "ventana_s": round(observado_s, 1), "reparacion_total_s": round(reparacion_total, 1), "tiempo_operativo_T_s": round(t_oper, 1),
            "fallas_r": r_inc, "mtbf_horas": round(m_h, 3),
            "intervalo_90_mtbf_horas": [round(lo_s / 3600, 3), round(hi_s / 3600, 1)],
            "disponibilidad_A": {"punto": round(a_(t_oper / r_inc), 5), "con_mtbf_cota_inferior_90": round(a_(lo_s), 5),
                                 "con_mtbf_cota_superior_90": round(a_(hi_s), 6), "formula": "A = MTBF / (MTBF + MTTR)"},
            "disponibilidad_observada_por_tiempo": round(1 - reparacion_total / observado_s, 5),
            "nota_equivalencia": "con un solo incidente A puntual es algebraicamente igual a la disponibilidad observada por tiempo (1 - reparación / ventana): el estimador solo aporta el intervalo",
            "supuestos_y_limites": [
                "tasa de fallos constante en el tiempo; el único fallo fue de configuración (falta de INEGI_TOKEN) en el primer intento, no un fallo aleatorio en régimen normal",
                "la captura es un trabajo diario, no un servicio continuo: solo puede fallar cuando se ejecuta, así que medir la exposición en horas no es natural",
                "la reparación (268 s) fue un reintento manual durante la puesta en marcha; un fallo de una ejecución programada tardaría hasta el siguiente ciclo (≈ 24 h)",
                "un solo fallo da un intervalo muy ancho; no es una estimación estable",
                "los dos extremos del incidente proceden de registros que la API pública de GitHub no corrobora (docs/E1/fiabilidad.md §4)",
            ],
        }
    cp_lo, cp_hi = intervalo_clopper_pearson(exitos, len(validas), 0.95)

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
                       "evaluable_como_se_definio_O1": cumple_ventana,
                       "intervalo_95_clopper_pearson": [round(cp_lo, 4), round(cp_hi, 4)],
                       "el_intervalo_incluye_el_objetivo": cp_lo <= objetivo <= cp_hi},
        "incidentes": {"total": len(inc), "cerrados": len(cerrados), "abiertos": abiertos,
                       "detalle": [{"inicio_utc": _iso(i["inicio"]), "fallos_consecutivos": i["fallos"], "causa_registrada": i["error"],
                                    "recuperacion_utc": _iso(i["recuperacion"]) if i["recuperacion"] else None,
                                    "reparacion_s": i["reparacion_s"]} for i in inc]},
        "mttr": {"estimable": mttr is not None, "segundos": round(mttr, 1) if mttr is not None else None, "incidentes_cerrados": len(cerrados)},
        "mtbf": mtbf_info,
        "disponibilidad_A": disp,
        "estimacion_exploratoria": explor,
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
