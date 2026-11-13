"""Carga y validación de los datos del tablero (Observatorio de Ocupación Hotelera · Manzanillo, E1).

Este módulo SOLO lee archivos versionados del repositorio (capa oro y resultados del laboratorio de pronósticos), los valida y
prepara textos para el cliente. No reentrena modelos, no ejecuta el pipeline, no usa red ni secretos y no lee datos de DENUE.
Depende únicamente de pandas y numpy (no de Streamlit), de modo que se prueba en cualquier entorno.

Las rutas se calculan a partir de la ubicación de ESTE archivo, así que funcionan desde cualquier directorio de trabajo.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
RUTA_ORO = Path("data") / "oro" / "manzanillo_ocupacion_mensual.csv"
RUTA_META_ORO = Path("data") / "oro" / "manzanillo_ocupacion_mensual.meta.json"
CARPETA_RESULTADOS = Path("laboratorio") / "pronosticos" / "resultados"

# Constantes del contrato de datos 1.0.0 (docs/E1/contrato_datos.md); una prueba las compara con pipeline.config.
N_MESES = 108
PRIMER_PERIODO, ULTIMO_PERIODO = "2016-01", "2024-12"
FIN_ENTRENAMIENTO = "2023-12"
COVID_INICIO, COVID_FIN = "2020-03", "2021-06"
FAMILIAS = ("SES", "Holt", "Holt-Winters", "SARIMA")
FAMILIA_REFERENCIA = "ingenuo"
NOMBRES = {
    "SES": "Suavizamiento exponencial simple (SES)", "Holt": "Holt", "Holt-Winters": "Holt-Winters", "SARIMA": "SARIMA",
    FAMILIA_REFERENCIA: "Referencia ingenua estacional",
}
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
TIPO_RETRO, TIPO_PROYECCION = "proyeccion_retrospectiva", "proyeccion_futura"  # así vienen rotulados en el CSV del laboratorio
TOLERANCIA_COHERENCIA = 1e-4  # los CSV redondean a 6 decimales


class ErrorDatos(Exception):
    """Un archivo falta, está incompleto o no es coherente con el laboratorio: el tablero no debe mostrar cifras dudosas."""


def mes_texto(ts: pd.Timestamp) -> str:
    """«marzo de 2024» (en español, sin depender de la configuración regional del sistema)."""
    return f"{MESES[ts.month - 1]} de {ts.year}"


def _ruta(raiz: Path, relativa: Path) -> Path:
    ruta = Path(raiz) / relativa
    if not ruta.is_file():
        raise ErrorDatos(f"Falta el archivo {relativa.as_posix()}: el tablero lee solo archivos versionados del repositorio.")
    return ruta


def _csv(raiz: Path, relativa: Path, columnas: set) -> pd.DataFrame:
    df = pd.read_csv(_ruta(raiz, relativa), dtype={"periodo": str})
    faltan = columnas - set(df.columns)
    if faltan:
        raise ErrorDatos(f"{relativa.name}: faltan las columnas {sorted(faltan)}.")
    return df


def _json(raiz: Path, relativa: Path) -> dict:
    try:
        return json.loads(_ruta(raiz, relativa).read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ErrorDatos(f"{relativa.name} no es un JSON válido: {e}") from e


def _con_fecha(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["fecha"] = pd.to_datetime(df["periodo"] + "-01", format="%Y-%m-%d", errors="coerce")
    if df["fecha"].isna().any():
        raise ErrorDatos("Hay periodos con formato distinto de AAAA-MM.")
    df["mes_texto"] = df["fecha"].map(mes_texto)
    return df


# ---------------------------------------------------------------- capa oro
def cargar_oro(raiz: Path = RAIZ) -> pd.DataFrame:
    """Ocupación mensual de Manzanillo (2 a 5 estrellas) desde la capa oro: 108 meses, 2016-01 a 2024-12."""
    df = _csv(raiz, RUTA_ORO, {"periodo", "ocupacion_pct", "d_covid"})
    if len(df) != N_MESES:
        raise ErrorDatos(f"La capa oro debe tener {N_MESES} meses y tiene {len(df)}.")
    if df["periodo"].duplicated().any():
        raise ErrorDatos("La capa oro tiene periodos repetidos.")
    df = _con_fecha(df).sort_values("fecha").reset_index(drop=True)
    esperado = pd.period_range(PRIMER_PERIODO, ULTIMO_PERIODO, freq="M").astype(str)
    if list(df["periodo"]) != list(esperado):
        raise ErrorDatos(f"La capa oro debe cubrir {PRIMER_PERIODO} a {ULTIMO_PERIODO} sin huecos.")
    y = pd.to_numeric(df["ocupacion_pct"], errors="coerce")
    if y.isna().any() or not np.isfinite(y).all() or ((y < 0) | (y > 100)).any():
        raise ErrorDatos("La ocupación debe ser numérica y estar entre 0 y 100 en todos los meses.")
    if not set(df["d_covid"].unique()) <= {0, 1}:
        raise ErrorDatos("d_covid debe valer 0 o 1.")
    df["ocupacion_pct"] = y.astype(float)
    df["conjunto"] = np.where(df["periodo"] <= FIN_ENTRENAMIENTO, "Entrenamiento (2016–2023)", "Prueba (2024)")
    return df[["periodo", "fecha", "mes_texto", "ocupacion_pct", "d_covid", "conjunto"]]


def cargar_meta_oro(raiz: Path = RAIZ) -> dict:
    meta = _json(raiz, RUTA_META_ORO)
    for clave in ("atribucion", "version_contrato", "filas", "periodo_min", "periodo_max", "sha256_csv"):
        if clave not in meta:
            raise ErrorDatos(f"La ficha de la capa oro no tiene el campo {clave}.")
    return meta


# ---------------------------------------------------------------- resultados del laboratorio
def cargar_resumen(raiz: Path = RAIZ) -> dict:
    r = _json(raiz, CARPETA_RESULTADOS / "resumen.json")
    for clave in ("elegido", "referencia_ingenuo_estacional", "elegido_frente_a_referencia", "criterio_seleccion", "particion"):
        if clave not in r:
            raise ErrorDatos(f"resumen.json no tiene la clave {clave}.")
    return r


def cargar_ejecucion(raiz: Path = RAIZ) -> dict:
    e = _json(raiz, CARPETA_RESULTADOS / "ejecucion.json")
    for clave in ("fin_utc", "versiones", "fuente", "version_contrato"):
        if clave not in e:
            raise ErrorDatos(f"ejecucion.json no tiene la clave {clave}.")
    return e


def cargar_comparacion(raiz: Path = RAIZ) -> pd.DataFrame:
    """Errores de los cuatro modelos en 2024 (tabla del laboratorio) más la referencia ingenua estacional (de resumen.json)."""
    t = _csv(raiz, CARPETA_RESULTADOS / "comparacion_modelos_2024.csv", {"familia", "especificacion", "MAE", "RMSE", "MAPE", "sesgo_medio", "cobertura_IP95_2024"})
    if sorted(t["familia"]) != sorted(FAMILIAS):
        raise ErrorDatos(f"La comparación debe tener los modelos {list(FAMILIAS)}; trae {list(t['familia'])}.")
    r = cargar_resumen(raiz)
    ref = r["referencia_ingenuo_estacional"]
    fila = {"familia": FAMILIA_REFERENCIA, "especificacion": "Valor del mismo mes del año anterior", "MAE": ref["MAE"], "RMSE": ref["RMSE"],
            "MAPE": ref["MAPE"], "sesgo_medio": ref["sesgo_medio"], "cobertura_IP95_2024": np.nan}
    t = pd.concat([t[["familia", "especificacion", "MAE", "RMSE", "MAPE", "sesgo_medio", "cobertura_IP95_2024"]], pd.DataFrame([fila])], ignore_index=True)
    if (t[["MAE", "RMSE", "MAPE"]] <= 0).any().any() or t[["MAE", "RMSE", "MAPE"]].isna().any().any():
        raise ErrorDatos("Las métricas de error deben ser números positivos.")
    t["modelo"] = t["familia"].map(NOMBRES)
    t["es_elegido"] = t["familia"] == r["elegido"]["familia"]
    t["es_referencia"] = t["familia"] == FAMILIA_REFERENCIA
    return t


def cargar_pronosticos_2024(raiz: Path = RAIZ) -> pd.DataFrame:
    """Proyección retrospectiva de 2024 de cada modelo (entrenados con 2016–2023), con el valor observado."""
    d = _csv(raiz, CARPETA_RESULTADOS / "pronosticos_2024_por_modelo.csv", {"periodo", "tipo", "familia", "observado", "media", "li", "ls"})
    d = _con_fecha(d)
    esperadas = set(FAMILIAS) | {FAMILIA_REFERENCIA}
    if set(d["familia"]) != esperadas:
        raise ErrorDatos(f"pronosticos_2024_por_modelo.csv debe traer {sorted(esperadas)}.")
    for fam, g in d.groupby("familia"):
        if list(g["periodo"]) != [f"2024-{m:02d}" for m in range(1, 13)]:
            raise ErrorDatos(f"{fam}: debe haber un valor por cada mes de 2024.")
    con_ip = d[d["familia"].isin(FAMILIAS)]
    if con_ip[["li", "ls"]].isna().any().any() or not ((con_ip["li"] <= con_ip["media"]) & (con_ip["media"] <= con_ip["ls"])).all():
        raise ErrorDatos("Cada intervalo de predicción debe cumplir límite inferior ≤ media ≤ límite superior.")
    d["modelo"] = d["familia"].map(NOMBRES)
    return d.sort_values(["familia", "fecha"]).reset_index(drop=True)


def cargar_pronostico_elegido(raiz: Path = RAIZ) -> pd.DataFrame:
    """SARIMA elegido: comparación retrospectiva de 2024 (entrenado hasta 2023-12) y proyección de 2025 (entrenado hasta 2024-12)."""
    e = _csv(raiz, CARPETA_RESULTADOS / "pronostico_modelo_elegido.csv", {"periodo", "tipo", "modelo", "entrenado_con", "observado", "media", "li", "ls"})
    e = _con_fecha(e)
    if set(e["tipo"]) != {TIPO_RETRO, TIPO_PROYECCION}:
        raise ErrorDatos("pronostico_modelo_elegido.csv debe traer la proyección retrospectiva de 2024 y la proyección de 2025.")
    if list(e["periodo"]) != [f"{a}-{m:02d}" for a in (2024, 2025) for m in range(1, 13)]:
        raise ErrorDatos("El pronóstico elegido debe cubrir 2024-01 a 2025-12 mes por mes.")
    if e[["media", "li", "ls"]].isna().any().any() or not ((e["li"] <= e["media"]) & (e["media"] <= e["ls"])).all():
        raise ErrorDatos("Cada intervalo de predicción debe cumplir límite inferior ≤ media ≤ límite superior.")
    proy = e[e["tipo"] == TIPO_PROYECCION]
    if proy["observado"].notna().any():
        raise ErrorDatos("La proyección de 2025 no debe traer valores observados (la fuente termina en 2024-12).")
    e["serie"] = np.where(e["tipo"] == TIPO_RETRO, "Comparación retrospectiva 2024", "Proyección 2025 (calculada con datos hasta diciembre de 2024)")
    e["semiancho"] = (e["ls"] - e["li"]) / 2
    return e


# ---------------------------------------------------------------- coherencia y cálculos derivados
def metricas(observado, pronostico) -> dict:
    o, p = np.asarray(observado, dtype=float), np.asarray(pronostico, dtype=float)
    err = p - o
    return {"MAE": float(np.mean(np.abs(err))), "RMSE": float(np.sqrt(np.mean(err ** 2))), "MAPE": float(100 * np.mean(np.abs(err) / o)),
            "sesgo_medio": float(np.mean(err))}


def cobertura_ip95(df: pd.DataFrame) -> tuple[int, int]:
    """(meses cuyo valor observado cae dentro del intervalo del 95 %, meses evaluables)."""
    g = df.dropna(subset=["observado", "li", "ls"])
    return int(((g["observado"] >= g["li"]) & (g["observado"] <= g["ls"])).sum()), int(len(g))


def resumen_proyeccion(e: pd.DataFrame) -> dict:
    p = e[e["tipo"] == TIPO_PROYECCION]
    alto, bajo = p.loc[p["media"].idxmax()], p.loc[p["media"].idxmin()]
    return {"media_anual": float(p["media"].mean()), "mes_max": MESES[alto["fecha"].month - 1], "valor_max": float(alto["media"]),
            "mes_min": MESES[bajo["fecha"].month - 1], "valor_min": float(bajo["media"]),
            "semiancho_min": float(p["semiancho"].min()), "semiancho_max": float(p["semiancho"].max())}


def validar_coherencia(oro: pd.DataFrame, comparacion: pd.DataFrame, por_modelo: pd.DataFrame, elegido: pd.DataFrame, resumen: dict) -> list:
    """Cotejo entre archivos: devuelve la lista de problemas (vacía si todo es coherente con el laboratorio y con la capa oro)."""
    problemas = []
    obs_oro = oro.set_index("periodo")["ocupacion_pct"]
    for nombre, df in (("pronosticos_2024_por_modelo.csv", por_modelo), ("pronostico_modelo_elegido.csv", elegido[elegido["tipo"] == TIPO_RETRO])):
        mal = [p for p, o in zip(df["periodo"], df["observado"]) if abs(o - obs_oro[p]) > TOLERANCIA_COHERENCIA]
        if mal:
            problemas.append(f"{nombre}: el valor observado no coincide con la capa oro en {sorted(set(mal))[:3]}.")
    for fam, g in por_modelo.groupby("familia"):
        calc = metricas(g["observado"], g["media"])
        fila = comparacion.set_index("familia").loc[fam]
        for m in ("MAE", "RMSE", "MAPE"):
            if abs(calc[m] - fila[m]) > TOLERANCIA_COHERENCIA:
                problemas.append(f"{fam}: {m} recalculado desde los pronósticos ({calc[m]:.6f}) difiere de la tabla del laboratorio ({fila[m]:.6f}).")
    retro = elegido[elegido["tipo"] == TIPO_RETRO]
    calc = metricas(retro["observado"], retro["media"])
    fam_elegida = resumen["elegido"]["familia"]
    fila = comparacion.set_index("familia").loc[fam_elegida]
    for m in ("MAE", "RMSE", "MAPE"):
        if abs(calc[m] - fila[m]) > TOLERANCIA_COHERENCIA:
            problemas.append(f"El pronóstico elegido ({fam_elegida}): {m} recalculado difiere de la tabla del laboratorio.")
    sar = por_modelo[por_modelo["familia"] == fam_elegida].set_index("periodo")
    if not np.allclose(sar.loc[retro["periodo"], "media"], retro.set_index("periodo")["media"], atol=TOLERANCIA_COHERENCIA):
        problemas.append("La media 2024 del modelo elegido no coincide entre los dos archivos del laboratorio.")
    cob = cobertura_ip95(retro)
    if abs(cob[0] / cob[1] - float(fila["cobertura_IP95_2024"])) > TOLERANCIA_COHERENCIA:
        problemas.append("La cobertura del intervalo del 95 % recalculada difiere de la tabla del laboratorio.")
    if resumen["particion"]["entrenamiento"][:2] != [PRIMER_PERIODO, FIN_ENTRENAMIENTO]:
        problemas.append("La partición de entrenamiento del laboratorio no es 2016-01 a 2023-12.")
    return problemas


@dataclass(frozen=True)
class Datos:
    oro: pd.DataFrame
    meta_oro: dict
    comparacion: pd.DataFrame
    por_modelo: pd.DataFrame
    elegido: pd.DataFrame
    resumen: dict
    ejecucion: dict


def cargar_todo(raiz: Path = RAIZ, validar: bool = True) -> Datos:
    """Lee y valida todo lo que muestra el tablero. Si algo no es coherente, lanza ``ErrorDatos`` con el motivo."""
    d = Datos(cargar_oro(raiz), cargar_meta_oro(raiz), cargar_comparacion(raiz), cargar_pronosticos_2024(raiz),
              cargar_pronostico_elegido(raiz), cargar_resumen(raiz), cargar_ejecucion(raiz))
    if validar:
        problemas = validar_coherencia(d.oro, d.comparacion, d.por_modelo, d.elegido, d.resumen)
        if problemas:
            raise ErrorDatos("Los resultados no son coherentes con el laboratorio: " + " | ".join(problemas))
    return d


# ---------------------------------------------------------------- textos para el cliente (todo sale de los datos)
def fecha_generacion(ejecucion: dict) -> str:
    """«13 de noviembre de 2026, 02:20 (hora de la Ciudad de México; 08:20 UTC)» a partir de ejecucion.json."""
    utc = pd.Timestamp(ejecucion["fin_utc"])
    local = utc.tz_convert("America/Mexico_City")
    return f"{local.day} de {MESES[local.month - 1]} de {local.year}, {local:%H:%M} (hora de la Ciudad de México; {utc:%H:%M} UTC)"


def textos_cliente(d: Datos) -> dict:
    """Explicaciones para el cliente, con cifras tomadas de los archivos (no escritas a mano)."""
    retro = d.elegido[d.elegido["tipo"] == TIPO_RETRO]
    cob, n = cobertura_ip95(retro)
    fila = d.comparacion.set_index("familia")
    s, ref = fila.loc["SARIMA"], fila.loc[FAMILIA_REFERENCIA]
    p = resumen_proyeccion(d.elegido)
    gen = pd.Timestamp(d.ejecucion["fin_utc"]).tz_convert("America/Mexico_City")
    mes_generacion = f"{MESES[gen.month - 1]} de {gen.year}"
    media_obs, media_pron = float(retro["observado"].mean()), float(retro["media"].mean())
    mejora = [m for m in ("MAE", "RMSE", "MAPE") if s[m] < ref[m]]
    peor = [m for m in ("MAE", "RMSE", "MAPE") if s[m] >= ref[m]]
    return {
        "intervalo": (
            "**Qué es el intervalo del 95 %.** Cada pronóstico mensual es un valor central (la línea) y una franja alrededor de él. "
            "La franja es el rango en el que, si los patrones del pasado se mantienen, esperamos que caiga el valor real con una confianza del 95 %. "
            f"Es amplia: en la proyección de 2025 va de ±{p['semiancho_min']:.0f} a ±{p['semiancho_max']:.0f} puntos porcentuales alrededor del valor central, "
            "porque la serie incluye el periodo de COVID, que aumentó mucho la variación. Una franja amplia es honesta, pero limita su uso para decisiones finas."),
        "resultado_2024": (
            f"**Qué pasó en 2024 (comparación retrospectiva).** El modelo se entrenó solo con datos hasta diciembre de 2023 y se comparó con lo que realmente ocurrió en 2024. "
            f"La ocupación observada promedió {media_obs:.1f} % y el modelo proyectó {media_pron:.1f} %. "
            f"Los valores reales cayeron dentro del intervalo en {cob} de {n} meses, y el error medio fue de {s['MAE']:.1f} puntos porcentuales por mes."),
        "comparacion": (
            f"**SARIMA frente a la referencia ingenua.** La referencia ingenua repite el valor del mismo mes del año anterior. "
            f"El SARIMA tuvo menor error en {', '.join(mejora) if mejora else 'ninguna métrica'} y no fue mejor en {', '.join(peor) if peor else 'ninguna métrica'} "
            f"(MAE {s['MAE']:.2f} frente a {ref['MAE']:.2f}; RMSE {s['RMSE']:.2f} frente a {ref['RMSE']:.2f}; MAPE {s['MAPE']:.2f} % frente a {ref['MAPE']:.2f} %). "
            "Con solo 12 meses de prueba, las diferencias son pequeñas y no permiten declarar un ganador claro. "
            "El SARIMA se eligió entre los cuatro modelos obligatorios por su menor RMSE entre los que tenían residuos sin autocorrelación; la referencia ingenua no participa en esa elección."),
        "proyeccion_2025": (
            "**Proyección 2025: una proyección histórica, no un pronóstico vigente.** Se calculó con la información disponible hasta diciembre de 2024, "
            f"que es donde termina la fuente de datos. Cuando se generaron estos resultados ({mes_generacion}) 2025 ya había transcurrido, pero la fuente usada no trae datos observados de 2025, "
            f"así que esta proyección no se pudo comparar con la realidad. Su valor central anual es {p['media_anual']:.1f} %, con {p['mes_max']} ({p['valor_max']:.1f} %) como el mes más alto "
            f"y {p['mes_min']} ({p['valor_min']:.1f} %) como el más bajo. No debe usarse como una predicción para decisiones de 2026."),
    }


LIMITACIONES = (
    "Los datos son mensuales y llegan hasta diciembre de 2024; no incluyen 2025 ni 2026.",
    "Describen la ocupación de los hoteles de 2 a 5 estrellas de Manzanillo en conjunto; no representan a un hotel en particular ni a otras categorías.",
    "La prueba del modelo usa un solo año (12 meses): con tan pocos meses no se puede afirmar que un modelo sea mejor que otro de forma estable.",
    "El periodo de COVID (marzo de 2020 a junio de 2021) aumenta la variación y hace los intervalos muy amplios.",
    "Los modelos suponen que los patrones del pasado (estacionalidad y nivel) se mantienen; no anticipan eventos nuevos ni cambios de oferta.",
    "Los resultados se calcularon una vez y se leen de archivos versionados; el tablero no vuelve a entrenar modelos ni a consultar fuentes.",
)
