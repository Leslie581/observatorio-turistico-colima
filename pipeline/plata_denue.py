"""Plata de DENUE: bronce sanitizado -> data/plata/denue_establecimientos.csv (contrato §2.2).

El bronce ya excluye nombre, razón social, contacto y domicilio; aquí se vuelve a verificar (R-E05) y se
descartan además las columnas constantes o vacías (reducción documentada). Coordenadas y CLEE solo viven en plata
(que no se versiona).
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

from .calidad import reglas_denue as re_
from .calidad.cuarentena import Cuarentena, ErrorPuertaCalidad
from .config import ZONA_LOCAL
from .plata_datatur import verificar_integridad

COLUMNAS_PLATA = [
    "fecha_captura_local", "clee", "id", "clase_actividad", "scian_clase", "estrato", "personal_min", "personal_max",
    "colonia", "cp", "localidad", "municipio_clave", "ageb", "manzana", "tipo_asentamiento", "latitud", "longitud",
    "fecha_alta", "capturas_del_dia", "ejecucion", "archivo_bronce", "sha256_bronce",
]
FUENTE = "denue_establecimientos"


def estrato_a_rango(texto: str) -> tuple[int | None, int | None]:
    """'6 a 10 personas' -> (6, 10); '251 y más personas' -> (251, None)."""
    t = (texto or "").strip().lower()
    m = re.match(r"(\d+)\s*a\s*(\d+)", t)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.match(r"(\d+)\s*y\s*m", t)
    if m:
        return int(m.group(1)), None
    return None, None


def listar_capturas(carpeta: Path) -> list[Path]:
    return sorted(Path(carpeta).glob("*/*_02_BuscarAreaAct.json"), key=lambda p: p.name)


def _cargar_captura(ruta: Path, raiz_bronce: Path, cuarentena: Cuarentena):
    """Devuelve (DataFrame de la captura, meta) o None si el lote se rechaza completo."""
    rel = ruta.relative_to(raiz_bronce.parent.parent).as_posix() if raiz_bronce.parent.parent in ruta.parents else ruta.name
    contenido = ruta.read_bytes()
    digest = verificar_integridad(ruta, contenido)  # ErrorPuertaCalidad si no coincide con su ficha
    meta = json.loads(Path(str(ruta) + ".meta.json").read_text(encoding="utf-8"))
    try:
        registros = json.loads(contenido.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ErrorPuertaCalidad("R-E01", f"{ruta.name} no es JSON válido") from None
    if not isinstance(registros, list):
        raise ErrorPuertaCalidad("R-E01", f"{ruta.name} no es una lista JSON")
    re_.r_e05_privacidad(registros, ruta.name)  # incidente: detiene toda la ejecución
    cuarentena.leidos(FUENTE, len(registros))
    df = pd.DataFrame(registros).astype("string") if registros else pd.DataFrame()
    faltan = re_.r_e01_esquema(df) if len(df) else re_.CAMPOS_REQUERIDOS
    if faltan:
        cuarentena.rechazar_lote(FUENTE, "R-E01", f"faltan campos requeridos {faltan}", rel, len(registros))
        return None
    cuant = Path(str(ruta).replace("_02_BuscarAreaAct.json", "_01_Cuantificar.json"))
    esperado = None
    if cuant.is_file():
        try:
            esperado = sum(int(str(x.get("Total", "")).replace(",", "")) for x in json.loads(cuant.read_text(encoding="utf-8")))
        except (ValueError, TypeError, AttributeError, json.JSONDecodeError):
            esperado = None
    ok, detalle = re_.r_e02_completitud(int(df.CLEE.nunique()), esperado)
    if not ok:
        cuarentena.rechazar_lote(FUENTE, "R-E02", detalle, rel, len(registros))
        return None
    df["fila_origen"] = range(1, len(df) + 1)  # posición del registro en la lista JSON
    return df, meta, rel, digest


def procesar_capturas(raiz_bronce: Path, cuarentena: Cuarentena) -> pd.DataFrame:
    raiz_bronce = Path(raiz_bronce)
    capturas = listar_capturas(raiz_bronce)
    if not capturas:
        raise ErrorPuertaCalidad("R-E01", f"no hay capturas DENUE en {raiz_bronce}")
    filas, aceptadas = [], []
    for ruta in capturas:
        cargada = _cargar_captura(ruta, raiz_bronce, cuarentena)
        if cargada is None:
            continue
        df, meta, rel, digest = cargada
        utc = datetime.fromisoformat(meta["capturado_utc"])
        local = utc.astimezone(ZoneInfo(ZONA_LOCAL))
        mes_captura = local.strftime("%Y-%m")
        rechazadas = pd.Series(False, index=df.index)
        for regla, motivo, mascara in re_.aplicar(df, mes_captura):
            if mascara.any():
                cuarentena.rechazar(FUENTE, regla, motivo, df[mascara], rel, digest)
            rechazadas |= mascara
        ok = df[~rechazadas]
        rangos = ok.Estrato.map(estrato_a_rango)
        out = pd.DataFrame({
            "fecha_captura_local": local.strftime("%Y-%m-%d"), "clee": ok.CLEE, "id": ok.Id,
            "clase_actividad": ok.Clase_actividad, "scian_clase": ok.CLASE_ACTIVIDAD_ID, "estrato": ok.Estrato,
            "personal_min": [r[0] for r in rangos], "personal_max": [r[1] for r in rangos],
            "colonia": ok.Colonia, "cp": ok.CP, "localidad": ok.Ubicacion.str.split(",").str[0].str.strip(),
            "municipio_clave": ok.AreaGeo.str[:5], "ageb": ok.AGEB, "manzana": ok.Manzana,
            "tipo_asentamiento": ok.Tipo_Asentamiento, "latitud": pd.to_numeric(ok.Latitud), "longitud": pd.to_numeric(ok.Longitud),
            "fecha_alta": ok.Fecha_Alta + "-01", "ejecucion": meta.get("ejecucion", ""), "archivo_bronce": rel, "sha256_bronce": digest,
        })
        out["_capturado_utc"] = utc.isoformat()
        filas.append(out)
        aceptadas.append((local.strftime("%Y-%m-%d"), utc.isoformat()))
    if not filas:
        raise ErrorPuertaCalidad("R-E02", "ninguna captura DENUE superó la puerta de calidad")
    todo = pd.concat(filas, ignore_index=True)
    # una captura por día local: se conserva la última y se cuenta cuántas hubo (contrato §2.2)
    por_dia = pd.Series([d for d, _ in aceptadas]).value_counts().to_dict()
    ultima = todo.groupby("fecha_captura_local")["_capturado_utc"].transform("max")
    antes = len(todo)
    todo = todo[todo["_capturado_utc"] == ultima].copy()
    cuarentena.marcar(FUENTE, "registros_aceptados_reemplazados_por_captura_posterior_del_dia", antes - len(todo))
    todo["capturas_del_dia"] = todo.fecha_captura_local.map(por_dia).astype(int)
    for c in ("personal_min", "personal_max"):
        todo[c] = todo[c].astype("Int64")
    cuarentena.informativo[FUENTE] = {"capturas_leidas": len(capturas), "dias_con_captura": len(por_dia),
                                      "capturas_por_dia": {k: int(v) for k, v in sorted(por_dia.items())},
                                      "nota": "los registros de capturas repetidas del mismo día se reemplazan por la última, "
                                              "no se rechazan (son fotos duplicadas, no datos erróneos)"}
    plata = todo.drop(columns="_capturado_utc")[COLUMNAS_PLATA].sort_values(["fecha_captura_local", "clee"]).reset_index(drop=True)
    re_.validar_plata(plata)                       # R-E07: segunda verificación con pandera (esquema, tipos, rangos, unicidad, reglas)
    return plata
