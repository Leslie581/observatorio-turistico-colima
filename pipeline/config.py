"""Constantes y rutas del pipeline E1 (contrato de datos 1.0.0, docs/E1/contrato_datos.md)."""
from __future__ import annotations

from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

VERSION_CONTRATO = "1.0.0"  # versión del ESQUEMA del oro; la valida el laboratorio de pronósticos

# --- DATATUR / variable objetivo (contrato §1.1b y §4.1)
CENTRO_OBJETIVO = "Manzanillo"
CATEGORIAS_OBJETIVO = ("2 estrellas", "3 estrellas", "4 estrellas", "5 estrellas")
PERIODO_INICIO = "2016-01"
PERIODO_FIN = "2024-12"
FIN_ENTRENAMIENTO = "2023-12"
H_PRUEBA = 12
N_PERIODOS = 108
COVID_INICIO = "2020-03"
COVID_FIN = "2021-06"
OFERTA_2017 = "2017-06"
ANIO_MIN, ANIO_MAX = 2016, 2030

# --- DENUE
MUNICIPIO_CLAVE = "06007"
SUBSECTOR = "721"
CAJA_COLIMA = {"lat": (18.6, 19.6), "lon": (-104.8, -103.4)}
COMPLETITUD_MIN, COMPLETITUD_MAX = 0.98, 1.02
ZONA_LOCAL = "America/Mexico_City"

# --- Atribución obligatoria de lo que se versiona (contrato §4.3)
ATRIBUCION = {
    "datatur": "Secretaría de Turismo (SECTUR), DataTur, 'Ocupación hotelera en los 70 destinos principales monitoreados', "
               "licencia Creative Commons Attribution 4.0 (CC BY 4.0), https://www.datos.gob.mx/dataset/"
               "ocupacion_hotelera_70_destinos_principales_monitoreados_datatur",
    "denue": "Fuente: INEGI, Directorio Estadístico Nacional de Unidades Económicas (DENUE), API de consulta; términos de "
             "libre uso del INEGI. Agregado propio; no es un producto del INEGI.",
}


def rutas(raiz: Path = RAIZ) -> dict[str, Path]:
    raiz = Path(raiz)
    return {
        "base70": raiz / "data" / "bronce" / "datatur" / "Base70centros.csv",
        "bronce_denue": raiz / "data" / "bronce" / "denue",
        "plata": raiz / "data" / "plata",
        "oro": raiz / "data" / "oro",
        "cuarentena": raiz / "data" / "cuarentena",
    }
