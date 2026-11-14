"""Reglas R-E01 a R-E06 de las capturas DENUE (contrato §2.3). Reutiliza las constantes de extractores.denue."""
from __future__ import annotations

import pandas as pd
import pandera.pandas as pa

from extractores.denue import CAMPOS_DOMICILIO, CAMPOS_NOMBRE, CAMPOS_PRIVADOS, CATALOGO_HOSPEDAJE, _normalizar_clave

from ..config import CAJA_COLIMA, COMPLETITUD_MAX, COMPLETITUD_MIN, MUNICIPIO_CLAVE, SUBSECTOR
from .cuarentena import ErrorPuertaCalidad

CAMPOS_PROHIBIDOS = CAMPOS_PRIVADOS | CAMPOS_NOMBRE | CAMPOS_DOMICILIO
CAMPOS_REQUERIDOS = ["CLEE", "Id", "Clase_actividad", "CLASE_ACTIVIDAD_ID", "Estrato", "Colonia", "CP", "Ubicacion",
                     "Longitud", "Latitud", "AGEB", "Manzana", "AreaGeo", "SUBSECTOR_ACTIVIDAD_ID",
                     "Tipo_Asentamiento", "Fecha_Alta"]


# Esquema pandera de la plata de DENUE (puerta 1, PDF págs. 9–10 y 15): esquema, tipos, rangos, unicidad y reglas de negocio. Reutiliza las
# constantes de las reglas R-E01 a R-E06 (municipio, subsector, catálogo SCIAN 721 y caja geográfica de Colima); es una SEGUNDA verificación sobre
# lo que ya pasó las máscaras: si algo se cuela, la corrida se detiene con ``ErrorPuertaCalidad`` (código 2) y no escribe salidas.
ESQUEMA_PLATA = pa.DataFrameSchema({
    "fecha_captura_local": pa.Column(str, pa.Check.str_matches(r"^\d{4}-\d{2}-\d{2}$")),
    "clee": pa.Column(str, pa.Check.str_length(min_value=1)),
    "id": pa.Column(str, pa.Check.str_length(min_value=1)),
    "clase_actividad": pa.Column(str),
    "scian_clase": pa.Column(str, pa.Check.isin(list(CATALOGO_HOSPEDAJE))),
    "estrato": pa.Column(str),
    "personal_min": pa.Column("Int64", pa.Check.ge(0), nullable=True),
    "personal_max": pa.Column("Int64", pa.Check.ge(0), nullable=True),
    "colonia": pa.Column(str, nullable=True),
    "cp": pa.Column(str, nullable=True),
    "localidad": pa.Column(str),
    "municipio_clave": pa.Column(str, pa.Check.eq(MUNICIPIO_CLAVE)),
    "ageb": pa.Column(str, nullable=True),
    "manzana": pa.Column(str, nullable=True),
    "tipo_asentamiento": pa.Column(str, nullable=True),
    "latitud": pa.Column(float, pa.Check.in_range(*CAJA_COLIMA["lat"])),
    "longitud": pa.Column(float, pa.Check.in_range(*CAJA_COLIMA["lon"])),
    "fecha_alta": pa.Column(str, pa.Check.str_matches(r"^\d{4}-(0[1-9]|1[0-2])-01$")),
    "capturas_del_dia": pa.Column(int, pa.Check.ge(1)),
    "ejecucion": pa.Column(str),
    "archivo_bronce": pa.Column(str, pa.Check.str_length(min_value=1)),
    "sha256_bronce": pa.Column(str, pa.Check.str_matches(r"^[0-9a-f]{64}$")),
}, checks=[
    pa.Check(lambda d: d["personal_max"].isna() | (d["personal_max"] >= d["personal_min"]), error="personal_max menor que personal_min"),
    pa.Check(lambda d: d["fecha_alta"].str[:7] <= d["fecha_captura_local"].str[:7], error="fecha_alta posterior a la captura"),
], unique=["fecha_captura_local", "clee"], strict=True, ordered=True)


def validar_plata(df: pd.DataFrame) -> None:
    """Valida la plata de DENUE con ``ESQUEMA_PLATA``; lanza ``ErrorPuertaCalidad('R-E07', ...)`` con los primeros casos si falla."""
    try:
        ESQUEMA_PLATA.validate(df, lazy=True)
    except pa.errors.SchemaErrors as e:
        casos = e.failure_cases[["column", "check", "failure_case"]].head(5).to_dict("records")
        raise ErrorPuertaCalidad("R-E07", f"la plata de DENUE incumple su esquema: {casos}") from None


def r_e05_privacidad(registros: list[dict], archivo: str) -> None:
    """R-E05: un campo excluido por privacidad en el bronce es un incidente: se detiene todo."""
    presentes = sorted({k for r in registros if isinstance(r, dict) for k in r if _normalizar_clave(k) in CAMPOS_PROHIBIDOS})
    if presentes:
        raise ErrorPuertaCalidad("R-E05", f"{archivo} contiene campos excluidos por privacidad {presentes}: "
                                          "incidente de seguridad; no se genera ninguna salida")


def r_e01_esquema(df: pd.DataFrame) -> list[str]:
    return [c for c in CAMPOS_REQUERIDOS if c not in df.columns]


def r_e02_completitud(n_unicos: int, esperado: int | None) -> tuple[bool, str]:
    if not esperado:
        return False, "Cuantificar no devolvió un total utilizable"
    razon = n_unicos / esperado
    return COMPLETITUD_MIN <= razon <= COMPLETITUD_MAX, f"únicos/Total de Cuantificar = {razon:.4f} (debe estar entre 0.98 y 1.02)"


def aplicar(df: pd.DataFrame, mes_captura: str) -> list[tuple[str, "str | pd.Series", pd.Series]]:
    """R-E01, R-E03, R-E04 y R-E06 por fila. ``df`` trae ``fila_origen`` y todos los campos como texto."""
    t = df.copy()
    for c in CAMPOS_REQUERIDOS:
        t[c] = t[c].astype("string").str.strip()
    rech = []
    # R-E01: CLEE e Id no vacíos; CLEE único dentro de la captura
    vacio = (t.CLEE.isna() | (t.CLEE == "") | t.Id.isna() | (t.Id == "")).fillna(True).astype(bool)
    dup = t.duplicated(subset=["CLEE"], keep="first") & ~vacio
    rech.append(("R-E01", "CLEE o Id vacío", vacio))
    rech.append(("R-E01", "CLEE repetido en la captura; se conserva la primera aparición", dup))
    # R-E03: municipio, subsector y clase dentro del catálogo
    fuera_mun = ~t.AreaGeo.str.startswith(MUNICIPIO_CLAVE).fillna(False).astype(bool)
    fuera_sub = (t.SUBSECTOR_ACTIVIDAD_ID != SUBSECTOR).fillna(True).astype(bool)
    fuera_cat = ~t.CLASE_ACTIVIDAD_ID.isin(list(CATALOGO_HOSPEDAJE)).astype(bool)
    rech.append(("R-E03", "AreaGeo no pertenece al municipio 06007, o subsector distinto de 721, o clase fuera del catálogo SCIAN 721",
                 fuera_mun | fuera_sub | fuera_cat))
    # R-E04: coordenadas numéricas dentro de Colima
    lat = pd.to_numeric(t.Latitud, errors="coerce")
    lon = pd.to_numeric(t.Longitud, errors="coerce")
    fuera = ~(lat.between(*CAJA_COLIMA["lat"]) & lon.between(*CAJA_COLIMA["lon"]))
    rech.append(("R-E04", "latitud o longitud no numérica o fuera de Colima", fuera))
    # R-E06: Fecha_Alta AAAA-MM y no posterior a la captura
    formato = t.Fecha_Alta.str.fullmatch(r"\d{4}-(0[1-9]|1[0-2])").fillna(False)
    formato = formato.astype(bool)
    futura = formato & (t.Fecha_Alta > mes_captura).fillna(False).astype(bool)
    rech.append(("R-E06", "Fecha_Alta sin formato AAAA-MM o posterior a la fecha de captura", ~formato | futura))
    return rech
