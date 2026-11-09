"""Verificaciones reproducibles de E0 (solo lectura; no escribe ni usa la red).

    python -m pipeline.verificar_e0                  # informe JSON; exit 1 si algo FALLA
    python -m pipeline.verificar_e0 --solo historico
    python -m pipeline.verificar_e0 --exigir-datos   # "sin datos" también cuenta como fallo

Cada comprobación devuelve ``estado``:
- ``satisfactoria``: se ejecutó sobre datos reales y pasó (ok = True).
- ``fallida``: se ejecutó y encontró un problema (ok = False).
- ``sin_datos``: NO pudo ejecutarse porque aún no hay archivos que inspeccionar (ok = None).
  Esto NO demuestra nada: una verificación sobre cero archivos no prueba que los datos reales
  estén bien. Con ``--exigir-datos`` (usar en CI tras una captura) se trata como fallo.

Comprobaciones:
- historico: Base70centros.csv existe, no está vacío, fechas válidas, sin duplicados, sin huecos
  (periodos consecutivos), >= 36 periodos de Manzanillo y SHA-256/tamaño iguales a su ficha.
- integridad: SHA-256 y tamaño de cada archivo de bronce contra su .meta.json.
- privacidad: ningún JSON crudo del DENUE en bronce conserva campos personales ni el detalle
  de domicilio que se minimiza (ver extractores/denue.py).
- disponibilidad: tasa de ejecuciones exitosas de calidad/bitacora_capturas.jsonl (objetivo O1).
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BRONCE = RAIZ / "data" / "bronce"
BITACORA = RAIZ / "calidad" / "bitacora_capturas.jsonl"
CAMPOS_PERSONALES = {"telefono", "correo_e", "sitio_internet", "razon_social", "nombre"}
CAMPOS_DOMICILIO = {"calle", "num_exterior", "num_interior", "edificio", "edificio_piso", "numero_local"}
MINIMO_PERIODOS = 36


def _estado(ok: bool | None) -> str:
    return {True: "satisfactoria", False: "fallida", None: "sin_datos"}[ok]


def _sha256(ruta: Path) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()


def historico(bronce: Path = BRONCE, centro: str = "Manzanillo", minimo: int = MINIMO_PERIODOS) -> dict:
    import pandas as pd

    ruta = Path(bronce) / "datatur" / "Base70centros.csv"
    r: dict = {"archivo": ruta.name, "centro": centro, "minimo_requerido": minimo, "checks": {}}

    def terminar(ok: bool, motivo: str | None = None) -> dict:
        r.update(ok=ok, estado=_estado(ok), **({"motivo": motivo} if motivo else {}))
        return r

    c = r["checks"]
    c["archivo_existe"] = ruta.is_file()
    if not c["archivo_existe"]:
        return terminar(False, "no hay Base70centros.csv en data/bronce/datatur")
    c["archivo_no_vacio"] = ruta.stat().st_size > 0
    if not c["archivo_no_vacio"]:
        return terminar(False, "el archivo está vacío")
    try:
        df = pd.read_csv(io.StringIO(ruta.read_bytes().decode("utf-8-sig")), sep="\t", dtype=str)
        df.columns = [x.strip().lower() for x in df.columns]
        faltan = {"anio", "mes", "centro", "categoria"} - set(df.columns)
        if faltan:
            return terminar(False, f"columnas faltantes: {sorted(faltan)}")
    except Exception as e:  # noqa: BLE001
        return terminar(False, f"no se pudo leer el CSV: {type(e).__name__}")
    df = df[df["centro"].str.strip() == centro].copy()
    c["centro_con_filas"] = len(df) > 0
    if not c["centro_con_filas"]:
        return terminar(False, f"el centro {centro} no tiene filas")
    anio = pd.to_numeric(df["anio"], errors="coerce")
    mes = pd.to_numeric(df["mes"], errors="coerce")
    validas = anio.notna() & mes.notna() & mes.between(1, 12) & (anio % 1 == 0) & (mes % 1 == 0) & anio.between(1990, 2100)
    r["filas_con_fecha_invalida"] = int((~validas).sum())
    c["fechas_validas"] = bool(validas.all())
    d = df[validas].assign(_a=anio[validas].astype(int), _m=mes[validas].astype(int))
    dup = d.duplicated(subset=["_a", "_m", "categoria"], keep=False)
    r["filas_duplicadas"] = int(dup.sum())
    c["sin_duplicados"] = not bool(dup.any())
    periodos = sorted({f"{a}-{m:02d}" for a, m in zip(d["_a"], d["_m"])})
    r.update(periodos=len(periodos), primero=periodos[0] if periodos else None,
             ultimo=periodos[-1] if periodos else None)
    esperados = pd.period_range(periodos[0], periodos[-1], freq="M").strftime("%Y-%m").tolist() if periodos else []
    r["huecos_en_rango"] = sorted(set(esperados) - set(periodos))
    c["sin_huecos_periodos_consecutivos"] = bool(periodos) and not r["huecos_en_rango"]
    c["minimo_periodos"] = len(periodos) >= minimo
    meta_ruta = Path(str(ruta) + ".meta.json")
    if meta_ruta.is_file():
        m = json.loads(meta_ruta.read_text(encoding="utf-8"))
        c["hash_y_tamano_coinciden_con_ficha"] = m.get("sha256") == _sha256(ruta) and m.get("bytes") == ruta.stat().st_size
    else:
        c["hash_y_tamano_coinciden_con_ficha"] = False
    return terminar(all(c.values()))


def integridad(bronce: Path = BRONCE) -> dict:
    bronce = Path(bronce)
    revisados, fallos, sin_ficha = 0, [], []
    for meta in sorted(bronce.rglob("*.meta.json")):
        datos = Path(str(meta)[: -len(".meta.json")])
        if not datos.exists():
            fallos.append({"ficha": meta.name, "motivo": "falta el archivo de datos"})
            continue
        m = json.loads(meta.read_text(encoding="utf-8"))
        revisados += 1
        if m.get("sha256") != _sha256(datos) or m.get("bytes") != datos.stat().st_size:
            fallos.append({"archivo": datos.name, "motivo": "SHA-256 o tamaño distinto al de la ficha"})
    for datos in sorted(p for p in bronce.rglob("*") if p.is_file() and not p.name.endswith(".meta.json")
                        and p.suffix in (".csv", ".json", ".html", ".tsv")):
        if not Path(str(datos) + ".meta.json").exists():
            sin_ficha.append(datos.name)
    ok = None if (revisados == 0 and not fallos and not sin_ficha) else (not fallos and not sin_ficha)
    return {"ok": ok, "estado": _estado(ok), "fichas_revisadas": revisados, "fallos": fallos,
            "archivos_sin_ficha": sin_ficha}


def privacidad(bronce: Path = BRONCE) -> dict:
    carpeta = Path(bronce) / "denue"
    archivos = [f for f in sorted(carpeta.rglob("*.json")) if not f.name.endswith(".meta.json")] if carpeta.exists() else []
    infractores = []
    for f in archivos:
        datos = json.loads(f.read_text(encoding="utf-8-sig") or "[]")
        claves = {k.lower() for r in datos if isinstance(r, dict) for k in r}
        if claves & (CAMPOS_PERSONALES | CAMPOS_DOMICILIO):
            infractores.append({"archivo": f.name, "campos": sorted(claves & (CAMPOS_PERSONALES | CAMPOS_DOMICILIO))})
    if not archivos:
        return {"ok": None, "estado": "sin_datos", "archivos_denue_revisados": 0, "infractores": [],
                "aviso": "NO hay archivos reales del DENUE que inspeccionar: esto no demuestra que la "
                         "sanitización funcione sobre datos reales (solo las pruebas simuladas la cubren)."}
    return {"ok": not infractores, "estado": _estado(not infractores),
            "archivos_denue_revisados": len(archivos), "infractores": infractores,
            "nota": "El campo Nombre no se guarda en bronce; la lista de campos excluidos está en docs/fuentes/denue.md."}


def disponibilidad(bitacora: Path = BITACORA, objetivo: float = 0.95) -> dict:
    if not Path(bitacora).exists():
        return {"ok": None, "estado": "sin_datos", "motivo": "aún no hay bitácora de ejecuciones", "ejecuciones": 0}
    filas = [json.loads(x) for x in Path(bitacora).read_text(encoding="utf-8").splitlines() if x.strip()]
    validas = [f for f in filas if f.get("resultado") in ("exito", "fallo")]
    if not validas:
        return {"ok": None, "estado": "sin_datos", "motivo": "sin ejecuciones exitosas ni fallidas", "ejecuciones": len(filas)}
    exitos = sum(f["resultado"] == "exito" for f in validas)
    tasa = exitos / len(validas)
    return {"ok": tasa >= objetivo, "estado": _estado(tasa >= objetivo), "ejecuciones": len(validas),
            "exitosas": exitos, "tasa_exito": round(tasa, 4), "objetivo": objetivo,
            "dias_con_captura": len({f["fecha_local"] for f in validas if f["resultado"] == "exito"}),
            "nota": "La medición completa de fiabilidad (MTBF, MTTR) corresponde a E1"}


COMPROBACIONES = {"historico": historico, "integridad": integridad, "privacidad": privacidad,
                  "disponibilidad": disponibilidad}


def codigo_salida(informe: dict, exigir_datos: bool = False) -> int:
    malos = [v["ok"] is False or (exigir_datos and v["ok"] is None) for v in informe.values()]
    return 1 if any(malos) else 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--solo", choices=sorted(COMPROBACIONES), action="append")
    p.add_argument("--exigir-datos", action="store_true", help="'sin_datos' cuenta como fallo")
    args = p.parse_args(argv)
    informe = {n: COMPROBACIONES[n]() for n in (args.solo or COMPROBACIONES)}
    print(json.dumps(informe, ensure_ascii=False, indent=2))
    return codigo_salida(informe, args.exigir_datos)


if __name__ == "__main__":
    sys.exit(main())
