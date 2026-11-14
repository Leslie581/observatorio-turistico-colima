"""Jerarquías conceptuales de la capa oro (rúbrica de Ingeniería de Datos, PDF págs. 15 y 24).

Dos dimensiones que se construyen en cada corrida del pipeline, sin tocar el oro mensual (contrato 1.0.0):

  * ``dim_tiempo``: ``año -> trimestre -> mes`` para cada ``periodo`` del oro mensual (108 meses, clave ``periodo``).
  * ``dim_geografia``: ``entidad -> municipio -> centro turístico`` (con el tipo y subtipo de centro de DATATUR).
  * ``dim_ubicacion_denue``: ``entidad -> municipio -> localidad -> colonia`` de los establecimientos de DENUE (sin conteos, sin
    coordenadas y sin CLEE).

Qué justifica cada nivel (y qué NO se afirma):
  * Año, trimestre y mes salen de ``periodo`` (AAAA-MM); no hay supuesto alguno.
  * ``centro_turistico``, ``tipo_centro`` y ``subtipo_centro`` salen de las columnas ``centro``, ``tipo_centro`` y
    ``subtipo_centro`` de Base70 (plata de DATATUR).
  * ``municipio_clave`` sale de DENUE (``06007``, regla R-E03) y la entidad es su prefijo de 2 dígitos (``06``): la clave
    geoestadística del INEGI es ``entidad (2) + municipio (3)``. Los **nombres** (Colima, Manzanillo) son una tabla fija de un
    renglón del contrato §5, porque ninguna de las dos fuentes trae el nombre del estado ni del municipio de cada centro.
  * Base70 **no** dice en qué estado ni municipio está cada uno de los otros 63 centros: esos niveles solo se afirman para
    Manzanillo, el alcance del observatorio. No se inventan para los demás.
"""
from __future__ import annotations

import pandas as pd
import pandera.pandas as pa

from .calidad.cuarentena import ErrorPuertaCalidad
from .config import CENTRO_OBJETIVO, MUNICIPIO_CLAVE, N_PERIODOS

MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre")
# Tabla fija del contrato §5 (un renglón): claves geoestadísticas del INEGI y nombres de los niveles que las fuentes no traen.
ENTIDAD_CLAVE = MUNICIPIO_CLAVE[:2]
ENTIDAD_NOMBRE = "Colima"
MUNICIPIO_NOMBRE = "Manzanillo"

COLUMNAS_TIEMPO = ["periodo", "fecha_inicio", "anio", "trimestre", "anio_trimestre", "mes", "nombre_mes"]
COLUMNAS_GEOGRAFIA = ["entidad_clave", "entidad", "municipio_clave", "municipio", "centro_turistico", "tipo_centro", "subtipo_centro"]
COLUMNAS_UBICACION = ["entidad_clave", "municipio_clave", "localidad", "colonia"]

ESQUEMA_TIEMPO = pa.DataFrameSchema({
    "periodo": pa.Column(str, pa.Check.str_matches(r"^\d{4}-(0[1-9]|1[0-2])$"), unique=True),
    "fecha_inicio": pa.Column(str, pa.Check.str_matches(r"^\d{4}-\d{2}-01$")),
    "anio": pa.Column(int, pa.Check.in_range(2016, 2030)),
    "trimestre": pa.Column(int, pa.Check.isin([1, 2, 3, 4])),
    "anio_trimestre": pa.Column(str, pa.Check.str_matches(r"^\d{4}-T[1-4]$")),
    "mes": pa.Column(int, pa.Check.in_range(1, 12)),
    "nombre_mes": pa.Column(str, pa.Check.isin(list(MESES))),
}, strict=True, ordered=True)

ESQUEMA_GEOGRAFIA = pa.DataFrameSchema({
    "entidad_clave": pa.Column(str, pa.Check.str_matches(r"^\d{2}$")),
    "entidad": pa.Column(str, pa.Check.str_length(min_value=1)),
    "municipio_clave": pa.Column(str, pa.Check.str_matches(r"^\d{5}$")),
    "municipio": pa.Column(str, pa.Check.str_length(min_value=1)),
    "centro_turistico": pa.Column(str, pa.Check.str_length(min_value=1), unique=True),
    "tipo_centro": pa.Column(str, pa.Check.str_length(min_value=1)),
    "subtipo_centro": pa.Column(str, pa.Check.str_length(min_value=1)),
}, strict=True, ordered=True)

ESQUEMA_UBICACION = pa.DataFrameSchema({
    "entidad_clave": pa.Column(str, pa.Check.str_matches(r"^\d{2}$")),
    "municipio_clave": pa.Column(str, pa.Check.str_matches(r"^\d{5}$")),
    "localidad": pa.Column(str, pa.Check.str_length(min_value=1)),
    "colonia": pa.Column(str, pa.Check.str_length(min_value=1)),
}, strict=True, ordered=True)


def construir_dim_tiempo(oro_mensual: pd.DataFrame) -> pd.DataFrame:
    """Año -> trimestre -> mes para cada periodo del oro mensual. La clave ``periodo`` enlaza con ``manzanillo_ocupacion_mensual``."""
    idx = pd.PeriodIndex(oro_mensual["periodo"], freq="M")
    out = pd.DataFrame({
        "periodo": oro_mensual["periodo"].astype(str).values,
        "fecha_inicio": oro_mensual["fecha_inicio"].astype(str).values,
        "anio": idx.year.astype(int),
        "trimestre": idx.quarter.astype(int),
        "anio_trimestre": [f"{a}-T{q}" for a, q in zip(idx.year, idx.quarter)],
        "mes": idx.month.astype(int),
        "nombre_mes": [MESES[m - 1] for m in idx.month],
    })[COLUMNAS_TIEMPO]
    try:
        ESQUEMA_TIEMPO.validate(out, lazy=True)
    except pa.errors.SchemaErrors as e:
        raise ErrorPuertaCalidad("JERARQUIA", f"dim_tiempo incumple su esquema: {e.failure_cases[['column', 'check']].head(3).to_dict('records')}") from None
    if len(out) != N_PERIODOS:
        raise ErrorPuertaCalidad("JERARQUIA", f"dim_tiempo debe tener {N_PERIODOS} meses; tiene {len(out)}")
    return out


def construir_dim_geografia(plata_datatur: pd.DataFrame) -> pd.DataFrame:
    """Entidad -> municipio -> centro turístico (+ tipo y subtipo) del alcance del observatorio (Manzanillo)."""
    c = plata_datatur[plata_datatur["centro"] == CENTRO_OBJETIVO][["centro", "tipo_centro", "subtipo_centro"]].drop_duplicates()
    if len(c) != 1:
        raise ErrorPuertaCalidad("JERARQUIA", f"{CENTRO_OBJETIVO} debe tener un único tipo y subtipo de centro; hay {len(c)}")
    fila = c.iloc[0]
    out = pd.DataFrame([{
        "entidad_clave": ENTIDAD_CLAVE, "entidad": ENTIDAD_NOMBRE, "municipio_clave": MUNICIPIO_CLAVE, "municipio": MUNICIPIO_NOMBRE,
        "centro_turistico": str(fila["centro"]), "tipo_centro": str(fila["tipo_centro"]), "subtipo_centro": str(fila["subtipo_centro"]),
    }])[COLUMNAS_GEOGRAFIA]
    try:
        ESQUEMA_GEOGRAFIA.validate(out, lazy=True)
    except pa.errors.SchemaErrors as e:
        raise ErrorPuertaCalidad("JERARQUIA", f"dim_geografia incumple su esquema: {e.failure_cases[['column', 'check']].head(3).to_dict('records')}") from None
    return out


def construir_dim_ubicacion_denue(plata_denue: pd.DataFrame) -> pd.DataFrame:
    """Entidad -> municipio -> localidad -> colonia de los establecimientos de DENUE, sin conteos ni coordenadas."""
    d = plata_denue[["municipio_clave", "localidad", "colonia"]].dropna().astype(str).drop_duplicates()
    if (d["municipio_clave"] != MUNICIPIO_CLAVE).any():
        raise ErrorPuertaCalidad("JERARQUIA", f"hay establecimientos fuera del municipio {MUNICIPIO_CLAVE}")
    d.insert(0, "entidad_clave", d["municipio_clave"].str[:2])
    out = d[COLUMNAS_UBICACION].sort_values(["localidad", "colonia"]).reset_index(drop=True)
    try:
        ESQUEMA_UBICACION.validate(out, lazy=True)
    except pa.errors.SchemaErrors as e:
        raise ErrorPuertaCalidad("JERARQUIA", f"dim_ubicacion_denue incumple su esquema: {e.failure_cases[['column', 'check']].head(3).to_dict('records')}") from None
    if out.duplicated(["localidad", "colonia"]).any() or {"clee", "latitud", "longitud"} & set(out.columns):
        raise ErrorPuertaCalidad("JERARQUIA", "dim_ubicacion_denue no puede traer duplicados, CLEE ni coordenadas")
    return out


def verificar_integridad(oro_mensual: pd.DataFrame, dim_t: pd.DataFrame, dim_g: pd.DataFrame, dim_u: pd.DataFrame,
                         oferta: "pd.DataFrame | None" = None) -> None:
    """Claves foráneas e integridad jerárquica: cada nivel inferior tiene exactamente un padre.

    Con ``oferta`` (el agregado DENUE del oro) comprueba además que se enlace con la dimensión geográfica por ``municipio_clave``:
    es lo que une las dos fuentes en un solo modelo (DATATUR por ``periodo`` y centro; DENUE por municipio)."""
    if set(oro_mensual["periodo"]) != set(dim_t["periodo"]):
        raise ErrorPuertaCalidad("JERARQUIA", "los periodos del oro mensual y de dim_tiempo no coinciden")
    if (dim_t.groupby("anio_trimestre")["trimestre"].nunique() != 1).any() or (dim_t.groupby("periodo")["anio_trimestre"].nunique() != 1).any():
        raise ErrorPuertaCalidad("JERARQUIA", "un trimestre o un mes tiene más de un padre en dim_tiempo")
    if ((dim_t["mes"] - 1) // 3 + 1 != dim_t["trimestre"]).any():
        raise ErrorPuertaCalidad("JERARQUIA", "algún mes está asignado a un trimestre equivocado")
    if (dim_g["centro_turistico"] != CENTRO_OBJETIVO).any() or (dim_g["municipio_clave"].str[:2] != dim_g["entidad_clave"]).any():
        raise ErrorPuertaCalidad("JERARQUIA", "dim_geografia no corresponde al centro objetivo o su municipio no pertenece a la entidad")
    if not set(dim_u["municipio_clave"]) <= set(dim_g["municipio_clave"]):
        raise ErrorPuertaCalidad("JERARQUIA", "dim_ubicacion_denue trae un municipio que no está en dim_geografia")
    if oferta is not None and not set(oferta["municipio_clave"].astype(str)) <= set(dim_g["municipio_clave"]):
        raise ErrorPuertaCalidad("JERARQUIA", "el agregado de oferta DENUE trae un municipio que no está en dim_geografia")


def _d(dataset, col, tipo, unidad, definicion, fuente, regla):
    return {"dataset": dataset, "columna": col, "tipo": tipo, "unidad": unidad, "definicion": definicion, "fuente": fuente, "regla_de_calculo": regla}


_T, _G, _U = "dim_tiempo", "dim_geografia", "dim_ubicacion_denue"
DICCIONARIO_JERARQUIAS = [
    _d(_T, "periodo", "texto AAAA-MM", "mes", "Nivel mes. Clave: enlaza con manzanillo_ocupacion_mensual.periodo", "DATATUR Base70", "periodo del oro mensual"),
    _d(_T, "fecha_inicio", "fecha ISO", "día", "Primer día del mes", "derivada", "periodo + '-01'"),
    _d(_T, "anio", "entero", "año", "Nivel año (el más general de la jerarquía temporal)", "derivada", "año de periodo"),
    _d(_T, "trimestre", "entero 1-4", "trimestre", "Nivel trimestre dentro del año (calendario: T1 = enero a marzo)", "derivada", "(mes - 1) // 3 + 1"),
    _d(_T, "anio_trimestre", "texto AAAA-Tn", "trimestre", "Identificador único del trimestre (año + trimestre)", "derivada", "anio + '-T' + trimestre"),
    _d(_T, "mes", "entero 1-12", "mes", "Número del mes dentro del año", "derivada", "mes de periodo"),
    _d(_T, "nombre_mes", "texto", "-", "Nombre del mes en español, en minúsculas", "derivada", "tabla fija de 12 nombres"),
    _d(_G, "entidad_clave", "texto 2 dígitos", "-", "Nivel estado. Clave geoestadística del INEGI", "INEGI DENUE", "primeros 2 dígitos de municipio_clave"),
    _d(_G, "entidad", "texto", "-", "Nombre del estado (nivel más general). Base70 y DENUE no traen el nombre: tabla fija del contrato §5", "contrato §5", "clave 06 = Colima"),
    _d(_G, "municipio_clave", "texto 5 dígitos", "-", "Nivel municipio. Clave geoestadística (entidad + municipio)", "INEGI DENUE", "AreaGeo (regla R-E03)"),
    _d(_G, "municipio", "texto", "-", "Nombre del municipio. Tabla fija del contrato §5", "contrato §5", "clave 06007 = Manzanillo"),
    _d(_G, "centro_turistico", "texto", "-", "Nivel centro turístico (el más específico). Solo se afirma su pertenencia al municipio para Manzanillo", "DATATUR Base70", "columna centro"),
    _d(_G, "tipo_centro", "texto", "-", "Clasificación del centro turístico en DATATUR", "DATATUR Base70", "columna tipo_centro"),
    _d(_G, "subtipo_centro", "texto", "-", "Subclasificación del centro turístico en DATATUR", "DATATUR Base70", "columna subtipo_centro"),
    _d(_U, "entidad_clave", "texto 2 dígitos", "-", "Nivel estado de los establecimientos de DENUE", "INEGI DENUE", "primeros 2 dígitos de municipio_clave"),
    _d(_U, "municipio_clave", "texto 5 dígitos", "-", "Nivel municipio de los establecimientos de DENUE", "INEGI DENUE", "AreaGeo (regla R-E03)"),
    _d(_U, "localidad", "texto", "-", "Nivel localidad dentro del municipio", "INEGI DENUE", "columna localidad"),
    _d(_U, "colonia", "texto", "-", "Nivel colonia dentro de la localidad (el más específico). Sin conteos, coordenadas ni CLEE: no identifica establecimientos", "INEGI DENUE", "columna colonia"),
]
