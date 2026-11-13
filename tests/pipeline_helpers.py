"""Construye árboles de bronce SINTÉTICOS (en carpetas temporales) para probar el pipeline.

Los datos son inventados y solo prueban la lógica del código; no son evidencia operativa ni datos reales.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from extractores.base import guardar_bronce

COLUMNAS = ["anio", "mes", "tipo_centro", "subtipo_centro", "centro", "categoria", "cuartos_disponibles",
            "cuartos_ocupados_no_residentes", "cuartos_ocupados_residentes", "llegada_turistas_no_residentes",
            "llegada_turistas_residentes", "turistas_noche_no_residentes", "turistas_noche_residentes"]
DISPONIBLES = {"1 estrella": 50, "2 estrellas": 100, "3 estrellas": 200, "4 estrellas": 300, "5 estrellas": 400}
RES = {"1 estrella": 10, "2 estrellas": 60, "3 estrellas": 100, "4 estrellas": 120, "5 estrellas": 100}
NORES = {"1 estrella": 5, "2 estrellas": 10, "3 estrellas": 40, "4 estrellas": 60, "5 estrellas": 80}


def filas_manzanillo(con_una_estrella: bool = True) -> list[list]:
    filas = []
    for p in pd.period_range("2016-01", "2024-12", freq="M"):
        cats = ["2 estrellas", "3 estrellas", "4 estrellas", "5 estrellas"]
        if con_una_estrella and p <= pd.Period("2017-09", "M"):
            cats = ["1 estrella"] + cats
        for c in cats:
            filas.append([p.year, f"{p.month:02d}", "Centros de Playa", "Tradicionales", "Manzanillo", c,
                          DISPONIBLES[c], NORES[c], RES[c], 20, 40, 60, 120])
    return filas


def escribir_base70(raiz: Path, filas: list[list], modificar=None) -> Path:
    """Escribe Base70 sintético (TSV, CRLF) con su ficha `.meta.json`. `modificar(texto)` permite estropear el contenido."""
    texto = "\t".join(COLUMNAS) + "\r\n" + "".join("\t".join("" if v is None else str(v) for v in f) + "\r\n" for f in filas)
    if modificar:
        texto = modificar(texto)
    return guardar_bronce(texto.encode("utf-8"), "datatur", "Base70centros.csv", {"url": "sintetico"}, bronce=Path(raiz) / "data" / "bronce")


def registro_denue(i: int, **cambios) -> dict:
    r = {"CLEE": f"0600772111100052300{i:04d}", "Id": str(1000 + i), "Clase_actividad": "Hoteles sin otros servicios integrados",
         "Estrato": "6 a 10 personas", "Tipo_vialidad": "CALLE", "Colonia": "CENTRO", "CP": "28200",
         "Ubicacion": "MANZANILLO,Manzanillo,COLIMA", "Tipo": "Fijo", "Longitud": "-104.32", "Latitud": "19.09",
         "tipo_corredor_industrial": "", "nom_corredor_industrial": "", "AGEB": "0329", "Manzana": "006",
         "CLASE_ACTIVIDAD_ID": "721112", "SECTOR_ACTIVIDAD_ID": "72", "SUBSECTOR_ACTIVIDAD_ID": "721",
         "RAMA_ACTIVIDAD_ID": "7211", "SUBRAMA_ACTIVIDAD_ID": "72111", "Tipo_Asentamiento": "COLONIA",
         "Fecha_Alta": "2015-03", "AreaGeo": "060070001"}
    r.update(cambios)
    return r


def escribir_denue(raiz: Path, carpeta: str, capturado_utc: str, registros: list[dict], total: int | None = None,
                   ejecucion: str | None = None) -> Path:
    """Escribe una captura sintética (Cuantificar + BuscarAreaAct) con sus fichas, bajo data/bronce/denue/<carpeta>/."""
    bronce = Path(raiz) / "data" / "bronce"
    ts = capturado_utc.replace("-", "").replace(":", "")[:15] + "Z"
    ej = ejecucion or ts
    total = len(registros) if total is None else total
    guardar_bronce(json.dumps([{"AE": "721", "AG": "06007", "Total": str(total)}]).encode(), f"denue/{carpeta}",
                   f"{ts}_01_Cuantificar.json", {"capturado_utc": capturado_utc, "ejecucion": ej}, bronce=bronce)
    return guardar_bronce(json.dumps(registros, ensure_ascii=False, indent=1).encode("utf-8"), f"denue/{carpeta}",
                          f"{ts}_02_BuscarAreaAct.json", {"capturado_utc": capturado_utc, "ejecucion": ej}, bronce=bronce)


def arbol_completo(raiz: Path) -> Path:
    """Base70 sintético válido (con 1 estrella al inicio) y dos capturas DENUE en días distintos."""
    escribir_base70(raiz, filas_manzanillo())
    escribir_denue(raiz, "2026-11-10", "2026-11-10T15:00:00+00:00", [registro_denue(i) for i in range(5)])
    escribir_denue(raiz, "2026-11-11", "2026-11-11T15:00:00+00:00", [registro_denue(i) for i in range(5)])
    return Path(raiz)
