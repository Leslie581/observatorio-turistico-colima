"""Extractor DATATUR (SECTUR) del Observatorio Turístico y Hotelero de Manzanillo.

Fuentes, en orden de preferencia (ver docs/fuentes.md):

1. **Base70centros.csv** - "Ocupación hotelera en los 70 destinos principales
   monitoreados en DataTur", publicado por SECTUR en datos.gob.mx. Serie
   MENSUAL por centro turístico y categoría (2016-01 en adelante). Es la base
   de la serie histórica.
2. **Reportes mensuales públicos** de datatur.sectur.gob.mx
   (``{AAAA}-MES_{MM}_Publico.pdf|zip``). Son ACUMULADOS enero-mes; los
   meses individuales se obtienen por diferencia (ver ``acumulado_a_mensual``).
   Sirven para extender la serie después del último mes de Base70centros.
3. **Espejo no oficial** (copia en GitHub) solo como respaldo cuando la fuente
   oficial no es alcanzable. Todo lo que provenga del espejo se marca con
   ``origen = 'espejo_no_oficial'`` y debe verificarse por SHA-256 contra el
   archivo oficial en cuanto éste se descargue.

El Sistema de Monitoreo Hotelero (monitoreohotelero.sectur.gob.mx) NO se
automatiza. Corrección 2026-11-09: su robots.txt NO existe (HTTP 404; ver
evidencias/datatur_oficial/robots_monitoreohotelero_20261109.json); la
"prohibición" anotada el 2026-11-08 venía de la herramienta de lectura web. No se
automatiza porque es un generador interactivo (formularios ASP.NET) y hacerlo
exigiría reproducir sus peticiones internas. Se usa solo por exportación manual.
El extractor verifica robots.txt y registra el resultado.
"""
from __future__ import annotations

import io
import os
import re
import zipfile
from calendar import monthrange
from pathlib import Path

import pandas as pd

from .base import BRONCE, Bitacora, ExtractorEtico, guardar_bronce, sha256_archivo

FUENTE = "datatur"

# --- Base70centros (datos.gob.mx) -------------------------------------------
DATASET_ID = "ocupacion_hotelera_70_destinos_principales_monitoreados_datatur"
PAGINA_DATASET = f"https://www.datos.gob.mx/dataset/{DATASET_ID}"
# URL del botón "Descargar" de la página del conjunto de datos (SECTUR, CC BY 4.0),
# leída el 2026-11-09. Verificada por SHA-256 desde la computadora del equipo:
# evidencias/datatur_oficial/verificacion_navegador_20261109T015542Z.json
# Ya NO se usa la API CKAN del portal: robots.txt de www.datos.gob.mx prohíbe /api/.
URL_OFICIAL_BASE70 = "https://repodatos.atdt.gob.mx/s_turismo/ocupacion_hotelera/Base70centros.csv"
SHA256_OFICIAL_VERIFICADO = "a8ca3f9bf34edf46321a45c1abcd3f774363d02db0395f1d6132b8a7c4d7d671"
ENV_URL_OFICIAL = "DATATUR_BASE70_URL"  # permite sustituir la URL si el portal la cambia

# Espejo no oficial (commit fijado para reproducibilidad).
ESPEJO_REPO = "https://github.com/carlosvaldes941105-debug/Hotel"
ESPEJO_COMMIT = "474c3c0264a6d21e3874753cb48986b380432168"
ESPEJO_URL = (
    "https://raw.githubusercontent.com/carlosvaldes941105-debug/Hotel/"
    f"{ESPEJO_COMMIT}/Base70centros%20(1).csv"
)
ESPEJO_SHA256 = "a8ca3f9bf34edf46321a45c1abcd3f774363d02db0395f1d6132b8a7c4d7d671"

COLUMNAS_BASE70 = [
    "anio", "mes", "tipo_centro", "subtipo_centro", "centro", "categoria",
    "cuartos_disponibles", "cuartos_ocupados_no_residentes", "cuartos_ocupados_residentes",
    "llegada_turistas_no_residentes", "llegada_turistas_residentes",
    "turistas_noche_no_residentes", "turistas_noche_residentes",
]
NUMERICAS_BASE70 = COLUMNAS_BASE70[6:]

# --- Reportes mensuales (datatur.sectur.gob.mx) -----------------------------
BASE_MONITOREO = "https://datatur.sectur.gob.mx/Documentoscompartidos/monitoreo/"
SISTEMA_MONITOREO = "https://www.monitoreohotelero.sectur.gob.mx/Reportes/Menu.aspx"


def url_reporte_mensual(anio: int, mes: int, ext: str = "zip") -> str:
    return f"{BASE_MONITOREO}{anio}-MES_{mes:02d}_Publico.{ext}"


# ============================================================================
# Base70centros
# ============================================================================
def descubrir_url_base70(ex: ExtractorEtico) -> str:
    """URL oficial del CSV: la variable de entorno si existe; si no, la fija.

    No se consulta la API del portal (``/api/`` está prohibido en su robots.txt).
    """
    fija = (os.getenv(ENV_URL_OFICIAL) or "").strip()
    if fija:
        ex.bitacora.registrar("url_oficial_desde_entorno", url=fija)
        return fija
    return URL_OFICIAL_BASE70


def descargar_base70(ex: ExtractorEtico, permitir_espejo: bool = True) -> tuple[Path, str]:
    """Descarga Base70centros. Devuelve (ruta_bronce, origen)."""
    url = descubrir_url_base70(ex)
    try:
        r = ex.get(url)
        if not r.contenido.lstrip(b"\xef\xbb\xbf").startswith(b"anio"):
            raise ValueError(f"La respuesta no es el CSV esperado (tipo {r.tipo!r}, "
                             f"{len(r.contenido)} bytes)")
        ruta = guardar_bronce(r.contenido, FUENTE, "Base70centros.csv", {
            "fuente": "SECTUR/DataTur via datos.gob.mx", "url": url, "origen": "oficial",
            "metodo": "descarga_extractor", "estado_http": r.estado, "pagina": PAGINA_DATASET,
            "encabezados": r.encabezados, "sha256_respuesta": r.sha256,
        })
        ex.bitacora.registrar("base70_oficial", url=url, ruta=str(ruta), sha256=r.sha256,
                              bytes=len(r.contenido), encabezados=r.encabezados,
                              igual_al_espejo=r.sha256 == ESPEJO_SHA256,
                              igual_a_verificacion_previa=r.sha256 == SHA256_OFICIAL_VERIFICADO)
        return ruta, "oficial"
    except Exception as e:  # noqa: BLE001
        ex.bitacora.registrar("base70_oficial_fallo", url=url, error=repr(e))
    if not permitir_espejo:
        raise RuntimeError("Fuente oficial no disponible y el espejo está deshabilitado")
    r = ex.get(ESPEJO_URL)
    if r.sha256 != ESPEJO_SHA256:
        ex.bitacora.registrar("espejo_sha_distinto", esperado=ESPEJO_SHA256, obtenido=r.sha256)
    ruta = guardar_bronce(r.contenido, FUENTE, "Base70centros.csv", {
        "fuente": "Copia no oficial de Base70centros.csv (SECTUR/DataTur)",
        "url": ESPEJO_URL, "repositorio": ESPEJO_REPO, "commit": ESPEJO_COMMIT,
        "origen": "espejo_no_oficial",
        "advertencia": "Verificar SHA-256 contra el archivo oficial de datos.gob.mx",
    })
    ex.bitacora.registrar("base70_espejo", ruta=str(ruta), sha256=r.sha256)
    return ruta, "espejo_no_oficial"


def importar_base70_local(ruta_origen: Path, bitacora: Bitacora, origen: str,
                          url_declarada: str, bronce: Path = BRONCE, **extra) -> Path:
    """Importa a bronce un archivo obtenido por otro medio (p. ej. git clone).

    Se usa cuando el entorno de ejecución no tiene salida HTTP a la fuente.
    El archivo se copia sin modificar y su procedencia queda en .meta.json.
    """
    contenido = Path(ruta_origen).read_bytes()
    ruta = guardar_bronce(contenido, FUENTE, "Base70centros.csv", {
        "fuente": "Base70centros.csv (SECTUR/DataTur)", "url": url_declarada,
        "origen": origen, "metodo": "importacion_local", "ruta_origen": str(ruta_origen), **extra,
    }, bronce=bronce)
    bitacora.registrar("base70_importado_local", ruta=str(ruta), origen=origen,
                       sha256=sha256_archivo(ruta))
    return ruta


def leer_base70(ruta: Path) -> pd.DataFrame:
    """Lee el CSV (separado por tabuladores, UTF-8, CRLF) con tipos explícitos."""
    crudo = Path(ruta).read_bytes()
    texto = crudo.decode("utf-8-sig")
    sep = "\t" if texto.split("\n", 1)[0].count("\t") >= 5 else ","
    df = pd.read_csv(io.StringIO(texto), sep=sep, dtype={"mes": str, "anio": "Int64"})
    df.columns = [c.strip().lower() for c in df.columns]
    faltan = set(COLUMNAS_BASE70) - set(df.columns)
    if faltan:
        raise ValueError(f"Columnas faltantes en Base70centros: {sorted(faltan)}")
    df = df[COLUMNAS_BASE70].copy()
    for c in ["tipo_centro", "subtipo_centro", "centro", "categoria"]:
        df[c] = df[c].astype(str).str.strip()
    df["mes"] = df["mes"].astype(str).str.zfill(2)
    for c in NUMERICAS_BASE70:
        df[c] = pd.to_numeric(df[c], errors="coerce").astype("Float64")
    df["periodo"] = pd.to_datetime(df["anio"].astype(str) + "-" + df["mes"] + "-01", errors="coerce")
    df["fila_origen"] = range(2, len(df) + 2)  # línea en el CSV original (1 = encabezado)
    return df


# ============================================================================
# Reportes mensuales públicos (acumulados)
# ============================================================================
def verificar_sistema_monitoreo(ex: ExtractorEtico) -> bool | None:
    """Comprueba (y registra) si robots.txt permite el Sistema de Monitoreo.

    Devuelve None si el dominio no es alcanzable (no se puede afirmar nada).
    """
    try:
        ok = ex.permitido(SISTEMA_MONITOREO)
    except Exception as e:  # noqa: BLE001
        ex.bitacora.registrar("monitoreo_no_alcanzable", url=SISTEMA_MONITOREO, error=repr(e))
        return None
    ex.bitacora.registrar("monitoreo_robots", url=SISTEMA_MONITOREO, permitido=ok)
    return ok


def descargar_reportes_mensuales(ex: ExtractorEtico, periodos: list[tuple[int, int]],
                                 extensiones=("zip", "pdf")) -> list[dict]:
    resultados = []
    for anio, mes in periodos:
        for ext in extensiones:
            url = url_reporte_mensual(anio, mes, ext)
            fila = {"anio": anio, "mes": mes, "ext": ext, "url": url}
            try:
                r = ex.get(url)
                ruta = guardar_bronce(r.contenido, FUENTE + "/reportes_mensuales",
                                      Path(url).name, {"fuente": "DataTur reporte mensual público",
                                                       "url": url, "origen": "oficial",
                                                       "naturaleza": "acumulado enero-mes"})
                fila.update(ok=True, ruta=str(ruta), sha256=r.sha256)
            except Exception as e:  # noqa: BLE001
                fila.update(ok=False, error=repr(e))
            resultados.append(fila)
    return resultados


def contenido_zip(ruta: Path) -> list[str]:
    with zipfile.ZipFile(ruta) as z:
        return z.namelist()


_NUM = r"-?[\d,]+(?:\.\d+)?%?"
CAMPOS_FILA_PDF = [
    "disp_a2", "disp_a1", "disp_a0", "disp_dif_a2a1", "disp_dif_a1a0", "disp_var_a2a1", "disp_var_a1a0",
    "ocup_a2", "ocup_a1", "ocup_a0", "ocup_dif_a2a1", "ocup_dif_a1a0", "ocup_var_a2a1", "ocup_var_a1a0",
    "pct_a2", "pct_a1", "pct_a0", "pct_dif_a2a1", "pct_dif_a1a0",
]
_PATRON_CENTRO = re.compile(
    rf"^(?P<centro>[A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜ .\-]+?,\s*[A-Z]{{2,6}}\.?)\s+"
    rf"(?P<nums>(?:{_NUM}\s+){{{len(CAMPOS_FILA_PDF) - 1}}}{_NUM})\s*$"
)


def _a_numero(t: str) -> float:
    return float(t.replace(",", "").replace("%", ""))


def parsear_linea_centro(linea: str) -> dict | None:
    """Interpreta una fila de centro de un reporte mensual público (PDF).

    Orden de columnas observado en 2025-MES_09_Publico.pdf (19 valores):
    cuartos disponibles promedio diario (3 años, 2 diferencias, 2 variaciones %),
    cuartos ocupados promedio diario (igual) y % de ocupación (3 años y
    2 diferencias en puntos). ``a0`` es el año del reporte; ``a1`` y ``a2`` los
    dos anteriores. Las cifras son ACUMULADAS de enero al mes del reporte.
    Devuelve None si la línea no tiene el formato esperado.
    """
    m = _PATRON_CENTRO.match(linea.strip())
    if not m:
        return None
    valores = [_a_numero(n) for n in m.group("nums").split()]
    fila = dict(zip(CAMPOS_FILA_PDF, valores))
    fila["centro_pdf"] = m.group("centro").strip()
    return fila


def parsear_pdf_mensual(ruta: Path, centros=("MANZANILLO",)) -> pd.DataFrame:
    """Extrae las filas de los centros pedidos de un reporte mensual en PDF."""
    import pdfplumber

    filas = []
    with pdfplumber.open(ruta) as pdf:
        for n, pagina in enumerate(pdf.pages, start=1):
            for linea in (pagina.extract_text() or "").splitlines():
                if any(linea.upper().startswith(c) for c in centros):
                    fila = parsear_linea_centro(linea)
                    if fila:
                        fila["pagina"] = n
                        fila["archivo"] = Path(ruta).name
                        filas.append(fila)
    return pd.DataFrame(filas)


def acumulado_a_mensual(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte cifras acumuladas enero-mes a cifras del mes.

    Entrada: columnas ``anio, mes, disp_prom_acum, ocup_prom_acum`` (promedios
    diarios del periodo acumulado). Se reconstruyen cuartos-noche acumulados
    (promedio x días transcurridos) y se diferencian. El error por redondeo de
    los promedios publicados es de a lo sumo 0.5 x días por cada acumulado.
    Requiere meses consecutivos dentro de cada año; si falta un mes, el mes
    siguiente queda como NaN (no se imputa).
    """
    d = df.sort_values(["anio", "mes"]).copy()
    d["dias_acum"] = [sum(monthrange(int(a), k)[1] for k in range(1, int(m) + 1))
                      for a, m in zip(d["anio"], d["mes"])]
    d["disp_noches_acum"] = d["disp_prom_acum"] * d["dias_acum"]
    d["ocup_noches_acum"] = d["ocup_prom_acum"] * d["dias_acum"]
    salida = []
    for anio, g in d.groupby("anio"):
        g = g.set_index("mes").reindex(range(1, 13))
        prev_disp = g["disp_noches_acum"].shift(1)
        prev_ocup = g["ocup_noches_acum"].shift(1)
        prev_disp.iloc[0] = 0.0
        prev_ocup.iloc[0] = 0.0
        g["cuartos_disponibles"] = g["disp_noches_acum"] - prev_disp
        g["cuartos_ocupados"] = g["ocup_noches_acum"] - prev_ocup
        g["anio"] = anio
        salida.append(g.dropna(subset=["disp_noches_acum"]).reset_index())
    out = pd.concat(salida, ignore_index=True) if salida else d.iloc[0:0]
    out["ocupacion_pct"] = 100 * out["cuartos_ocupados"] / out["cuartos_disponibles"]
    out["derivado_de_acumulado"] = True
    return out[["anio", "mes", "cuartos_disponibles", "cuartos_ocupados", "ocupacion_pct",
                "derivado_de_acumulado"]]
