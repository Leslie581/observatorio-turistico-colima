"""Plata de DATATUR Base70: bronce -> data/plata/datatur_base70.csv (contrato §2.1). No modifica bronce."""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path

import pandas as pd

from .calidad import reglas_datatur as rd
from .calidad.cuarentena import Cuarentena, ErrorPuertaCalidad

COLUMNAS_PLATA = [
    "periodo", "centro", "tipo_centro", "subtipo_centro", "categoria",
    "cuartos_disponibles", "cuartos_ocupados_residentes", "cuartos_ocupados_no_residentes",
    "llegada_turistas_residentes", "llegada_turistas_no_residentes",
    "turistas_noche_residentes", "turistas_noche_no_residentes",
    "faltante_turistas_noche", "fila_origen", "sha256_bronce",
]


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def verificar_integridad(ruta: Path, contenido: bytes) -> str:
    """El SHA-256 y el tamaño del archivo deben coincidir con su ficha; si no, no hay salida confiable."""
    digest = sha256_bytes(contenido)
    ficha = Path(str(ruta) + ".meta.json")
    if not ficha.is_file():
        raise ErrorPuertaCalidad("INTEGRIDAD", f"falta la ficha {ficha.name} de {ruta.name}")
    meta = json.loads(ficha.read_text(encoding="utf-8"))
    if meta.get("sha256") != digest or meta.get("bytes") != len(contenido):
        raise ErrorPuertaCalidad("INTEGRIDAD", f"{ruta.name} no coincide con su ficha (SHA-256 o tamaño distinto)")
    return digest


def procesar_base70(ruta: Path, cuarentena: Cuarentena) -> tuple[pd.DataFrame, str]:
    """Devuelve (plata, sha256 del bronce). Lanza ErrorPuertaCalidad si el lote no es confiable."""
    ruta = Path(ruta)
    if not ruta.is_file():
        raise ErrorPuertaCalidad("INTEGRIDAD", f"no existe {ruta}")
    contenido = ruta.read_bytes()
    if not contenido:
        raise ErrorPuertaCalidad("R-D01", "Base70centros.csv está vacío")
    digest = verificar_integridad(ruta, contenido)
    try:
        df = pd.read_csv(io.StringIO(contenido.decode("utf-8-sig")), sep="\t", dtype=str, keep_default_na=False)
    except Exception as e:  # noqa: BLE001
        raise ErrorPuertaCalidad("R-D01", f"no se pudo leer como TSV UTF-8: {type(e).__name__}") from None
    df.columns = [c.strip().lower() for c in df.columns]
    rd.r_d01_esquema(df)
    df["fila_origen"] = range(2, len(df) + 2)  # línea del CSV original (1 = encabezado)
    nombre = ruta.name
    cuarentena.leidos("datatur_base70", len(df))

    res = rd.aplicar(df)
    rechazadas = pd.Series(False, index=df.index)
    for regla, motivo, mascara in res["rechazos"]:
        if mascara.any():
            cuarentena.rechazar("datatur_base70", regla, motivo, df[mascara], nombre, digest)
        rechazadas |= mascara
    for nombre_marca, mascara in res["marcas"].items():
        cuarentena.marcar("datatur_base70", nombre_marca, int(mascara.sum()))
    cuarentena.informativo["datatur_base70"] = res["informativo"]

    ok = df[~rechazadas].copy()
    num = res["num"].loc[ok.index]
    out = pd.DataFrame({
        "periodo": ok.anio.str.strip() + "-" + ok.mes.str.strip(),
        "centro": ok.centro.str.strip(), "tipo_centro": ok.tipo_centro.str.strip(),
        "subtipo_centro": ok.subtipo_centro.str.strip(), "categoria": ok.categoria.str.strip(),
    })
    for c in rd.CONTEOS:
        out[c] = num[c].astype("Int64")
    out["faltante_turistas_noche"] = res["marcas"]["R-D07_faltante_turistas_noche"].loc[ok.index]
    out["fila_origen"] = ok.fila_origen.astype(int)
    out["sha256_bronce"] = digest
    out = out[COLUMNAS_PLATA].reset_index(drop=True)
    resumen = cuarentena.resumen()["fuentes"]["datatur_base70"]
    if len(out) != resumen["aceptados"]:
        raise ErrorPuertaCalidad("CUENTA", "las filas de plata no coinciden con las aceptadas del resumen")
    return out, digest
