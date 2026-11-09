"""Cliente de la API del DENUE (INEGI) para establecimientos de hospedaje.

Documentación consultada: https://www.inegi.org.mx/servicios/api-denue/
(2026-11-08 y 2026-11-09). Métodos usados:

- ``BuscarAreaAct/{entidad}/{municipio}/{localidad}/{ageb}/{manzana}/{sector}/
  {subsector}/{rama}/{clase}/{nombre}/{registro_inicial}/{registro_final}/{id}/{token}``
  para descargar los establecimientos del subsector 721 (servicios de
  alojamiento temporal) en Manzanillo (entidad 06, municipio 007), paginando.
- ``Cuantificar/{actividad}/{area}/{estrato}/{token}`` para obtener el total
  esperado y medir la completitud de la descarga.

El token se lee de la variable de entorno ``INEGI_TOKEN``; nunca se escribe en
el código, la bitácora ni los archivos de bronce (las URLs se registran con el
token enmascarado).

Privacidad: antes de escribir en bronce se eliminan teléfono, correo, sitio web, razón social
(puede ser el nombre de una persona física) y el detalle de domicilio (ver ``sanitizar_crudo``).
El resto del JSON se guarda tal como llega, y sin el token.
"""
from __future__ import annotations

import json
import os
import unicodedata
from pathlib import Path

import pandas as pd

from .base import ExtractorEtico, guardar_bronce

FUENTE = "denue"
BASE_API = "https://www.inegi.org.mx/app/api/denue/v1/consulta/"
ENV_TOKEN = "INEGI_TOKEN"

ENTIDAD_COLIMA = "06"
MUNICIPIO_MANZANILLO = "007"

# Catálogo SCIAN (México) del subsector 721 "Servicios de alojamiento temporal".
# Verificar contra el catálogo vigente que use el DENUE (SCIAN 2018/2023).
CATALOGO_HOSPEDAJE = {
    "721111": "Hoteles con otros servicios integrados",
    "721112": "Hoteles sin otros servicios integrados",
    "721113": "Moteles",
    "721190": "Cabañas, villas y similares",
    "721210": "Campamentos y albergues recreativos",
    "721311": "Pensiones y casas de huéspedes",
    "721312": "Departamentos y casas amueblados con servicios de hotelería",
}
CLASES_HOTELERAS_DATATUR = {"721111", "721112", "721113"}  # comparables con DataTur

ESTRATOS = {
    "0 a 5 personas": (0, 5), "6 a 10 personas": (6, 10), "11 a 30 personas": (11, 30),
    "31 a 50 personas": (31, 50), "51 a 100 personas": (51, 100),
    "101 a 250 personas": (101, 250), "251 y más personas": (251, None),
}

CAMPOS_PRIVADOS = {"telefono", "correo_e", "sitio_internet", "razon_social"}
# El nombre comercial puede ser el nombre de una persona física en micronegocios y no se puede
# detectar automáticamente: no se guarda en el bronce público. CLEE e Id bastan para la trazabilidad.
CAMPOS_NOMBRE = {"nombre"}
# Minimización: el detalle de domicilio no se necesita (la ubicación la dan latitud/longitud, AGEB,
# manzana, colonia y CP) y en micronegocios (63 de 134 tienen 0 a 5 personas) puede ser una casa.
CAMPOS_DOMICILIO = {"calle", "num_exterior", "num_interior", "edificio", "edificio_piso", "numero_local"}

SINONIMOS = {
    "clee": "clee", "id": "id", "nombre": "nombre", "razon_social": "razon_social",
    "clase_actividad": "clase_actividad", "estrato": "estrato",
    "tipo_vialidad": "tipo_vialidad", "calle": "calle", "num_exterior": "num_exterior",
    "num_interior": "num_interior", "colonia": "colonia", "cp": "cp",
    "ubicacion": "ubicacion", "telefono": "telefono", "correo_e": "correo_e",
    "sitio_internet": "sitio_internet", "tipo": "tipo", "longitud": "longitud",
    "latitud": "latitud", "ageb": "ageb", "manzana": "manzana",
    "id_actividad": "id_actividad", "clase_actividad_id": "id_actividad",
    "fecha_alta": "fecha_alta",
}


class TokenNoConfigurado(RuntimeError):
    pass


class RespuestaDenueInvalida(RuntimeError):
    """La API respondió algo que no es la lista JSON documentada."""


def _token() -> str:
    t = os.getenv(ENV_TOKEN, "").strip()
    if not t:
        raise TokenNoConfigurado(
            f"Defina la variable de entorno {ENV_TOKEN} (token gratuito de INEGI)")
    return t


def _enmascarar(url: str, token: str) -> str:
    return url.replace(token, "***TOKEN***")


def _normalizar_clave(k: str) -> str:
    k = unicodedata.normalize("NFKD", k).encode("ascii", "ignore").decode().lower().strip()
    return SINONIMOS.get(k, k)


def _normalizar_texto(t: str) -> str:
    return unicodedata.normalize("NFKD", str(t)).encode("ascii", "ignore").decode().lower().strip()


def interpretar_respuesta(contenido: bytes):
    """Convierte el cuerpo de una respuesta DENUE en lista JSON o lanza error.

    La documentación sólo describe respuestas exitosas (lista de objetos). Un
    cuerpo vacío se interpreta como "sin resultados"; cualquier otra cosa
    (HTML, texto, objeto de error) se rechaza para no confundirla con datos.
    """
    texto = contenido.decode("utf-8-sig", errors="replace").strip()
    if not texto:
        return []
    try:
        datos = json.loads(texto)
    except json.JSONDecodeError:
        raise RespuestaDenueInvalida(f"Respuesta no JSON: {texto[:200]!r}") from None
    if not isinstance(datos, list):
        raise RespuestaDenueInvalida(f"Se esperaba una lista JSON y llegó {type(datos).__name__}: "
                                     f"{str(datos)[:200]}")
    return datos


class ClienteDenue:
    def __init__(self, ex: ExtractorEtico, token: str | None = None):
        self.ex = ex
        self.token = token or _token()
        self.respuestas: list[dict] = []  # cuerpos crudos con metadatos (token enmascarado)

    def _get_json(self, ruta: str):
        url = BASE_API + ruta + "/" + self.token
        # La API es un servicio documentado para consumo automatizado; robots.txt
        # del dominio se verifica igualmente en ExtractorEtico.get.
        try:
            r = self.ex.get(url)
        except Exception as e:
            raise RuntimeError(_enmascarar(str(e), self.token)) from None
        self.respuestas.append({"metodo": ruta.split("/", 1)[0], "url": _enmascarar(url, self.token),
                                "estado_http": r.estado, "sha256": r.sha256, "bytes": len(r.contenido),
                                "encabezados": r.encabezados, "contenido": r.contenido})
        return interpretar_respuesta(r.contenido)

    def cuantificar(self, actividad: str = "721",
                    area: str = ENTIDAD_COLIMA + MUNICIPIO_MANZANILLO, estrato: str = "0"):
        return self._get_json(f"Cuantificar/{actividad}/{area}/{estrato}")

    def buscar_area_act(self, entidad=ENTIDAD_COLIMA, municipio=MUNICIPIO_MANZANILLO,
                        sector="72", subsector="721", tam_pagina=1000, max_paginas=50):
        registros: list[dict] = []
        for p in range(max_paginas):
            ini, fin = p * tam_pagina + 1, (p + 1) * tam_pagina
            ruta = (f"BuscarAreaAct/{entidad}/{municipio}/0/0/0/{sector}/{subsector}/0/0/0/"
                    f"{ini}/{fin}/0")
            lote = self._get_json(ruta)
            if not isinstance(lote, list) or not lote:
                break
            registros.extend(lote)
            if len(lote) < tam_pagina:
                break
        return registros


def guardar_crudo(registros, nombre: str, metadatos: dict) -> Path:
    contenido = json.dumps(registros, ensure_ascii=False, indent=1).encode("utf-8")
    return guardar_bronce(contenido, FUENTE, nombre, metadatos)


def sanitizar_crudo(contenido: bytes) -> tuple[bytes, dict]:
    """Elimina campos personales y de domicilio ANTES de escribir en bronce.

    - Personales (``CAMPOS_PRIVADOS`` y ``CAMPOS_NOMBRE``): teléfono, correo, sitio web, razón social y
      nombre comercial (pueden ser el nombre de una persona física). Regla: cero datos personales (LFPDPPP).
    - Domicilio (``CAMPOS_DOMICILIO``): calle, números, edificio/piso y local. Minimización de datos.
    - Se CONSERVAN los campos públicos necesarios: CLEE, Id, Clase_actividad y claves SCIAN,
      Estrato, Colonia, CP, Ubicacion, Tipo, Longitud, Latitud, AGEB, Manzana, Tipo_Asentamiento,
      Fecha_Alta, AreaGeo y corredor industrial (justificación en docs/fuentes/denue.md).
    Si la respuesta no contiene campos a eliminar, los bytes se conservan intactos. La huella de la
    respuesta original queda en la ficha (``sha256_respuesta_original``).
    """
    info = {"campos_personales_eliminados": [], "campos_domicilio_eliminados": [],
            "registros_con_campos_eliminados": 0}
    try:
        datos = json.loads(contenido.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return contenido, info
    if not isinstance(datos, list):
        return contenido, info
    pers: set[str] = set()
    dom: set[str] = set()
    limpios = []
    for reg in datos:
        if not isinstance(reg, dict):
            limpios.append(reg)
            continue
        p_ = [k for k in reg if _normalizar_clave(k) in CAMPOS_PRIVADOS | CAMPOS_NOMBRE]
        d_ = [k for k in reg if _normalizar_clave(k) in CAMPOS_DOMICILIO]
        if p_ or d_:
            info["registros_con_campos_eliminados"] += 1
            pers.update(p_)
            dom.update(d_)
        limpios.append({k: v for k, v in reg.items() if k not in p_ and k not in d_})
    if not pers and not dom:
        return contenido, info
    info["campos_personales_eliminados"] = sorted(pers)
    info["campos_domicilio_eliminados"] = sorted(dom)
    return json.dumps(limpios, ensure_ascii=False, indent=1).encode("utf-8"), info


def guardar_respuestas_crudas(cli: "ClienteDenue", ejecucion: str, bronce=None,
                              particion: str = "crudo") -> list[Path]:
    """Guarda cada respuesta HTTP en bronce con su ficha de captura.

    Los campos personales se eliminan antes de escribir (``sanitizar_crudo``); el resto
    del cuerpo queda intacto. El token nunca está en el cuerpo y en la ficha la URL va
    enmascarada. La ficha conserva el SHA-256 y el tamaño de la respuesta original.
    """
    rutas = []
    for i, resp in enumerate(cli.respuestas, start=1):
        cuerpo, info = sanitizar_crudo(resp["contenido"])
        meta = {k: v for k, v in resp.items() if k not in ("contenido", "sha256", "bytes")}
        meta.update(fuente="INEGI DENUE API", origen="oficial", ejecucion=ejecucion,
                    parametros="Colima 06 / Manzanillo 007 / subsector SCIAN 721",
                    sha256_respuesta_original=resp["sha256"], bytes_respuesta_original=resp["bytes"],
                    **info)
        nombre = f"{ejecucion}_{i:02d}_{resp['metodo']}.json"
        kw = {"bronce": bronce} if bronce else {}
        rutas.append(guardar_bronce(cuerpo, f"{FUENTE}/{particion}", nombre, meta, **kw))
    return rutas


def total_cuantificar(respuesta) -> int | None:
    """Suma ``Total`` de la respuesta de Cuantificar (lista de {AE, AG, Total})."""
    try:
        return int(sum(int(str(x.get("Total", x.get("total"))).replace(",", "")) for x in respuesta))
    except (TypeError, ValueError, AttributeError):
        return None


def normalizar(registros: list[dict]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Normaliza registros DENUE. Devuelve (validos, cuarentena).

    - claves en minúsculas sin acentos;
    - elimina campos privados;
    - coordenadas numéricas y dentro de una caja de Colima;
    - verifica que la clase pertenezca al catálogo de hospedaje (por código
      si la API lo trae, o por nombre de clase);
    - elimina duplicados por ``id``/``clee``.
    """
    filas = [{_normalizar_clave(k): v for k, v in r.items()} for r in registros]
    df = pd.DataFrame(filas)
    if df.empty:
        return df, df
    df = df.drop(columns=[c for c in CAMPOS_PRIVADOS if c in df.columns])
    for c in ("latitud", "longitud"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    nombres_catalogo = {_normalizar_texto(v): k for k, v in CATALOGO_HOSPEDAJE.items()}
    if "id_actividad" in df.columns:
        df["scian"] = df["id_actividad"].astype(str).str.strip()
    else:
        df["scian"] = df.get("clase_actividad", pd.Series(index=df.index, dtype=str)).map(
            lambda t: nombres_catalogo.get(_normalizar_texto(t)))
    motivos = pd.Series("", index=df.index)
    motivos[~df["scian"].isin(CATALOGO_HOSPEDAJE.keys())] += "clase_fuera_de_catalogo;"
    if {"latitud", "longitud"} <= set(df.columns):
        fuera = ~(df["latitud"].between(18.6, 19.6) & df["longitud"].between(-104.8, -103.4))
        motivos[fuera] += "coordenadas_fuera_de_colima;"
    clave = "clee" if "clee" in df.columns else "id"
    dup = df.duplicated(subset=[clave], keep="first")
    motivos[dup] += "duplicado;"
    df["motivo_rechazo"] = motivos
    cuarentena = df[motivos != ""].copy()
    validos = df[motivos == ""].drop(columns="motivo_rechazo").copy()
    validos["comparable_datatur"] = validos["scian"].isin(CLASES_HOTELERAS_DATATUR)
    return validos, cuarentena


CAMPOS_MINIMOS = ["clee", "id", "nombre", "clase_actividad", "estrato", "latitud", "longitud"]


def validar(registros: list[dict], validos: pd.DataFrame, cuarentena: pd.DataFrame,
            esperado: int | None) -> dict:
    """Controles básicos equivalentes a los aplicados a la serie DATATUR.

    Integridad (hay datos), completitud contra ``Cuantificar``, esquema mínimo,
    faltantes por campo, duplicados, tipos/rangos de coordenadas y catálogo.
    """
    crudos = pd.DataFrame([{_normalizar_clave(k): v for k, v in r.items()} for r in registros])
    clave = "clee" if "clee" in crudos.columns else ("id" if "id" in crudos.columns else None)
    unicos = int(crudos[clave].nunique()) if clave else 0
    chequeos = []

    def chk(nombre, ok, valor, regla):
        chequeos.append({"control": nombre, "ok": bool(ok), "valor": valor, "regla": regla})

    chk("hay_registros", len(crudos) > 0, len(crudos), "> 0 registros")
    faltan = [c for c in CAMPOS_MINIMOS if c not in crudos.columns]
    chk("esquema_minimo", not faltan, faltan, f"columnas {CAMPOS_MINIMOS}")
    if esperado:
        comp = unicos / esperado
        chk("completitud_vs_cuantificar", 0.98 <= comp <= 1.02, round(comp, 4),
            "únicos / Total de Cuantificar entre 0.98 y 1.02")
    else:
        chk("completitud_vs_cuantificar", False, None, "Cuantificar no devolvió un total")
    dup = int(len(crudos) - unicos) if clave else None
    chk("duplicados", dup == 0, dup, "0 claves repetidas en la respuesta")
    nulos = {}
    for c in CAMPOS_MINIMOS:
        if c in crudos.columns:
            v = crudos[c].replace({"": None}).isna().mean()
            nulos[c] = round(float(v), 4)
    chk("faltantes_campos_minimos", all(v <= 0.05 for v in nulos.values()), nulos,
        "<= 5 % vacío por campo mínimo")
    if {"latitud", "longitud"} <= set(crudos.columns):
        lat = pd.to_numeric(crudos["latitud"], errors="coerce")
        chk("coordenadas_numericas", lat.notna().mean() >= 0.95, round(float(lat.notna().mean()), 4),
            ">= 95 % convertibles a número")
    en_cat = 1 - (cuarentena["motivo_rechazo"].str.contains("clase_fuera_de_catalogo").sum()
                  / max(len(crudos), 1)) if not cuarentena.empty else 1.0
    chk("clase_en_catalogo_721", en_cat >= 0.95, round(float(en_cat), 4), ">= 95 % en el catálogo SCIAN 721")
    return {"registros_crudos": int(len(crudos)), "unicos": unicos, "esperado_cuantificar": esperado,
            "validos": int(len(validos)), "cuarentena": int(len(cuarentena)),
            "ok": all(c["ok"] for c in chequeos), "controles": chequeos}


def resumen_agregado(validos: pd.DataFrame) -> dict:
    """Integración descriptiva/agregada (no se asigna ocupación a cada hotel)."""
    if validos.empty:
        return {"establecimientos": 0}
    out = {
        "establecimientos": int(len(validos)),
        "por_clase": validos["scian"].map(CATALOGO_HOSPEDAJE).value_counts().to_dict(),
        "comparables_datatur": int(validos["comparable_datatur"].sum()),
    }
    if "estrato" in validos.columns:
        out["por_estrato"] = validos["estrato"].value_counts().to_dict()
        lim = validos["estrato"].map(lambda e: ESTRATOS.get(str(e).strip(), (None, None)))
        out["personal_ocupado_min"] = int(sum(a for a, _ in lim if a is not None))
    if "ubicacion" in validos.columns:
        out["por_ubicacion"] = validos["ubicacion"].value_counts().head(15).to_dict()
    if {"latitud", "longitud"} <= set(validos.columns):
        out["con_coordenadas"] = int(validos[["latitud", "longitud"]].notna().all(axis=1).sum())
    return out
