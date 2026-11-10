"""Análisis reproducible de la encuesta de validación de usuarios (E0).

Reproduce las cifras automatizables de docs/E0/encuesta/informe_encuesta_e0.md a partir del
CSV original (privado, fuera de Git). Solo usa la biblioteca estándar.

    python laboratorio/encuesta_e0/analisis_encuesta.py
    python laboratorio/encuesta_e0/analisis_encuesta.py --csv RUTA
    TDL_ENCUESTA_CSV=RUTA python laboratorio/encuesta_e0/analisis_encuesta.py

Prioridad de la ruta: --csv > variable TDL_ENCUESTA_CSV > ruta por defecto relativa al repositorio
(evidencias_privadas/encuesta_e0/respuestas_original.csv).

Privacidad: la salida es SOLO agregada (conteos, denominadores y porcentajes). Las etiquetas impresas
son constantes de este script; nunca se imprime texto de una respuesta, una marca temporal ni una fila.
La ubicación se clasifica por regla, sin nombres de lugares concretos.

Códigos de salida: 0 = correcto; 2 = el archivo no supera la integridad o la validación (no se
publican cifras de un archivo distinto o de un formulario con columnas cambiadas).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import statistics
import sys
import unicodedata
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
CSV_POR_DEFECTO = RAIZ / "evidencias_privadas" / "encuesta_e0" / "respuestas_original.csv"
ENV_CSV = "TDL_ENCUESTA_CSV"
SHA256_ESPERADO = "84c36f9015b698c80702ada33921d19be93dd6e4f3858282aa355632d7ccadc8"  # LEEME §7
BASE70 = RAIZ / "data" / "bronce" / "datatur" / "Base70centros.csv"

V1, V2, V3 = "V1", "V2", "V3"
VERSIONES = (V1, V2, V3)
TODAS = frozenset(VERSIONES)
V23 = frozenset({V2, V3})
SOLO_V1 = frozenset({V1})
SOLO_V3 = frozenset({V3})


class ErrorValidacion(Exception):
    """El archivo no corresponde al instrumento documentado."""


def norm(texto: str) -> str:
    """NFC, espacios colapsados y sin espacios en los extremos."""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", texto or "")).strip()


def pct(f: int, n: int) -> float | None:
    if not n:
        return None
    return float((Decimal(f) * 100 / Decimal(n)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def sha256(ruta: Path) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 16), b""):
            h.update(bloque)
    return h.hexdigest()


# ---------------------------------------------------------------------------------------------------
# Instrumento: columnas, títulos esperados y disponibilidad por versión
# ---------------------------------------------------------------------------------------------------
# disponibilidad: versiones en que la pregunta EXISTÍA. INDET = versiones donde no puede saberse (nadie de
# esa versión la respondió y no hay otra evidencia); sus vacíos se cuentan como "indeterminados", no como
# omisiones ni como ausencias estructurales. Las versiones se infieren (LEEME §2).
TITULO_DECISIONES = "Si estuviera disponible, ¿en qué decisiones consultaría una plataforma como StayMetrics?"
COLUMNAS = {
    # clave: (índice, título normalizado esperado, disponibles, indeterminadas)
    "consentimiento": (1, "¿Acepta participar voluntariamente en esta entrevista?", TODAS, frozenset()),
    "puesto": (2, "¿Cuál es su puesto o función en el establecimiento?", TODAS, frozenset()),
    "tipo": (3, "¿Qué tipo de establecimiento representa?", TODAS, frozenset()),
    "ubicacion": (4, "¿En donde se encuentra el alojamiento?", TODAS, frozenset()),
    "antiguedad": (5, "¿Cuánto tiempo lleva trabajando en el sector de hospedaje?", TODAS, frozenset()),
    "meses_alta": (6, "¿En qué meses o temporadas reciben MÁS huéspedes?", TODAS, frozenset()),
    "anticipacion": (7, "¿Con cuánta anticipación suelen identificar que una temporada tendrá mayor o menor demanda?", TODAS, frozenset()),
    "usa_info": (12, "¿Actualmente utilizan estadísticas, reportes, registros de reservaciones o información del sector para planear sus actividades?", TODAS, frozenset()),
    "herramientas": (13, "¿Qué información o herramientas utilizan ACTUALMENTE para planear?", TODAS, frozenset()),
    "decisiones_texto": (14, TITULO_DECISIONES, SOLO_V1, frozenset()),
    "paga_herramienta": (16, "¿Actualmente utilizan alguna herramienta de pago para administrar reservaciones, analizar la ocupación o consultar información turística?", frozenset({V1, V3}), frozenset({V2})),
    "funcionalidades": (17, TITULO_DECISIONES, TODAS, frozenset()),  # LEEME I1: título duplicado; contiene funcionalidades
    "canales": (18, "¿A través de qué medios reciben reservaciones?", TODAS, frozenset()),
    "participa": (19, "¿Participa directamente en las decisiones relacionadas con precios, reservaciones, personal o administración del alojamiento?", TODAS, frozenset()),
    "factores": (20, "¿Qué factores considera que influyen más en la llegada de huéspedes?", TODAS, frozenset()),
    "col21": (21, "¿Qué podría hacer que NO la usara o la usara poco?", frozenset({V1, V3}), frozenset({V2})),  # LEEME I2
    "utilidad": (22, "¿Qué tan útil considera que sería una plataforma de análisis turístico para su establecimiento?", TODAS, frozenset()),
    "mejoras_texto": (23, "¿Qué mejoraría o agregaría a la propuesta de StayMetrics para que se adapte a las necesidades de su alojamiento?", TODAS, frozenset()),
    "info_falta_texto": (24, "¿Qué información les gustaría tener y no tienen fácilmente?", SOLO_V1, frozenset()),
    "pagaria": (25, "¿Consideraría pagar por una plataforma como StayMetrics si le ayudara a resolver problemas de su alojamiento?", TODAS, frozenset()),
    "deberia_ofrecer_texto": (26, "¿Qué información considera que debería ofrecer una plataforma como StayMetrics para que realmente le resultara útil en sus actividades?", frozenset({V1, V3}), frozenset({V2})),
    "organizacion_texto": (27, "¿Cómo se organizan cuando esperan recibir más o menos huéspedes? Por ejemplo, ¿realizan cambios en el personal, la limpieza, el mantenimiento, las reservaciones o los servicios que ofrecen?", SOLO_V1, frozenset()),
    "dificultades_texto": (28, "¿Cuáles son las principales dificultades que enfrentan al administrar su alojamiento, especialmente cuando reciben más o menos huéspedes de los que esperaban?", SOLO_V1, frozenset()),
    "meses_baja": (29, "¿En qué meses o temporadas reciben MENOS huéspedes?", V23, frozenset()),
    "dificultades": (30, "¿Cuáles son sus principales dificultades al planear las actividades del alojamiento?", V23, frozenset()),
    "mas_huespedes": (31, "Cuando esperan MÁS huéspedes de lo normal, ¿qué suelen hacer?", V23, frozenset()),
    "menos_huespedes": (32, "Cuando esperan MENOS huéspedes de lo normal, ¿qué suelen hacer?", V23, frozenset()),
    "info_dificil": (33, "¿Qué información le cuesta conseguir y le sería útil para planear?", SOLO_V3, frozenset()),
    "reaccion": (34, "Cuando la ocupación resulta distinta de lo esperado, ¿cómo suelen reaccionar?", SOLO_V3, frozenset()),
    "precios": (35, "¿Cómo deciden sus precios y promociones?", SOLO_V3, frozenset()),
    "desviacion": (37, "Durante el último año, ¿con qué frecuencia tuvieron una cantidad de huéspedes diferente a la que habían previsto?", SOLO_V3, frozenset()),
}
COLUMNA_FECHA = (0, "Marca temporal")
COLUMNAS_VACIAS = (8, 9, 10, 11, 15)  # vacías en todos los envíos (LEEME §1 y §6)
COLUMNA_CONDICIONAL = 36  # "En caso afirmativo…": depende de la col. 16; no se analiza en el informe
TOTAL_COLUMNAS = 38
# Columnas que distinguen las versiones (inferencia documentada en LEEME §2)
MARCAS_V3 = ("info_dificil", "reaccion", "precios", "desviacion")
MARCAS_V2 = ("meses_baja", "dificultades", "mas_huespedes", "menos_huespedes")

CONSENTIMIENTO_SI = "Sí, acepto participar"
CONSENTIMIENTO_NO = "No acepto participar"

# ---------------------------------------------------------------------------------------------------
# Catálogos (opción original -> etiqueta del informe). Equivalencias entre versiones: LEEME §4.
# ---------------------------------------------------------------------------------------------------
PUESTO = {"Propietario del alojamiento": "Propietario o anfitrión",
          "Anfitrión de alojamiento vacacional": "Propietario o anfitrión",
          "Gerente o director": "Dirección o administración",
          "Administrador del establecimiento": "Dirección o administración",
          "Encargado de cocina": "Operativo",
          "Encargado de recepción o atención a huéspedes": "Operativo",
          "Encargado de operaciones o mantenimiento": "Operativo"}
TIPO = {"Hotel": "Hotel o resort", "Resort o complejo turístico": "Hotel o resort",
        "Casa o departamento de renta vacacional": "Renta vacacional (casa o departamento)",
        "Bungalows": "Bungalows"}
PARTICIPA = {"Sí, participo directamente": "Sí, directamente",
             "Participo en algunas decisiones": "En algunas decisiones",
             "No tomo decisiones, pero conozco los procesos": "No decide, pero conoce los procesos",
             "No participo ni tengo información sobre esas decisiones": "No participa ni tiene información"}
ANTIGUEDAD = {"De 1 a 3 años": "1 a 3 años", "De 4 a 7 años": "4 a 7 años", "Más de 7 años": "Más de 7 años"}
ANTICIPACION = {k: k for k in ("Uno o varios meses antes", "Depende de la temporada",
                               "Una o dos semanas antes", "Unos días antes")}
DESVIACION = {"Frecuentemente": "Frecuentemente", "Rara vez": "Rara vez"}
UTILIDAD = {str(i): str(i) for i in range(1, 6)}
MESES = ("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre",
         "Octubre", "Noviembre", "Diciembre")


def catalogo_comun(pares):
    """Mismas opciones en todas las versiones: [(etiqueta, {versiones: [opciones originales]})]."""
    return [(etiqueta, {TODAS: [original]}) for original, etiqueta in pares]


def catalogo_v(pares, versiones):
    return [(etiqueta, {versiones: [original]}) for original, etiqueta in pares]


HERRAMIENTAS = [  # equivalencias V1 <-> V2/V3 (LEEME §4); el resto existe en una sola versión
    ("Reportes de plataformas de reservación", {SOLO_V1: ["Plataformas como Booking o Airbnb"],
                                                V23: ["Reportes de plataformas de reservación"]}),
    ("Hojas de cálculo (Excel)", {SOLO_V1: ["Excel u hojas de cálculo"], V23: ["Hojas de cálculo (Excel)"]}),
    ("Sistema o software de administración hotelera (PMS)", {SOLO_V1: ["Software de administración hotelera"],
                                                             V23: ["Sistema de administración hotelera"]}),
    ("Estadísticas oficiales (DataTur, SECTUR, asociaciones)",
     {V23: ["Estadísticas oficiales (DataTur, Secretaría de Turismo, asociaciones)"]}),
    ("Calendarios de eventos y vacaciones", {V23: ["Calendarios de eventos y vacaciones"]}),
    ("Solo experiencia, sin registros", {V23: ["Solo nuestra experiencia, sin registros"]}),
    ("Reportes de organismos turísticos", {SOLO_V1: ["Reportes de organismos turísticos"]}),
    ("Registros manuales", {SOLO_V1: ["Registros manuales"]}),
]
CANALES = [
    ("Reservación directa", {SOLO_V1: ["Reservaciones directamente en el establecimiento"],
                             V23: ["Reservaciones directas"]}),
] + catalogo_comun([(x, x) for x in ("WhatsApp o redes sociales", "Llamadas telefónicas", "Página web propia",
                                     "Airbnb", "Agencias de viajes")])
FUNCIONALIDADES = catalogo_comun([(x, x) for x in (
    "Pronósticos de ocupación", "Análisis de precios y competencia", "Apoyo para planificar personal y servicios",
    "Alertas de cambios en la demanda", "Reportes y gráficas fáciles de interpretar",
    "Identificación de temporadas altas y bajas", "Análisis de tendencias de reservaciones",
    "Comparaciones entre destinos turísticos")])
FACTORES = catalogo_comun([(x, x) for x in (
    "Días festivos y puentes", "Vacaciones escolares", "Calificaciones y reseñas en plataformas",
    "Precios del alojamiento", "Ubicación y accesibilidad", "Eventos turísticos, culturales o deportivos",
    "Promociones y descuentos", "Condiciones climáticas", "Competencia con otros alojamientos")])
DIFICULTADES = catalogo_v([
    ("Cancelaciones o huéspedes que no llegan", "Cancelaciones o huéspedes que no llegan"),
    ("Definir precios adecuados", "Definir precios adecuados"),
    ("Anticipar cuántos huéspedes llegarán", "Anticipar cuántos huéspedes llegarán"),
    ("Comisiones o dependencia de plataformas de reservación", "Comisiones o dependencia de plataformas"),
    ("Conseguir u organizar personal temporal", "Conseguir u organizar personal temporal"),
    ("Falta de tiempo para revisar registros", "Falta de tiempo para revisar registros"),
    ("No tenemos dificultades importantes", "No tienen dificultades importantes")], V23)
MAS_HUESPEDES = catalogo_v([
    ("Reforzar limpieza, mantenimiento o insumos", "Reforzar limpieza, mantenimiento o insumos"),
    ("Subir precios", "Subir precios"),
    ("Contratar personal temporal o ampliar turnos", "Contratar personal temporal o ampliar turnos"),
    ("Ajustar servicios (alimentos, actividades)", "Ajustar servicios"),
    ("Pedir anticipo o estancia mínima", "Pedir anticipo o estancia mínima"),
    ("Habilitar habitaciones o áreas cerradas", "Habilitar habitaciones o áreas cerradas")], V23)
MENOS_HUESPEDES = catalogo_v([
    ("Bajar precios o lanzar promociones", "Bajar precios o lanzar promociones"),
    ("Aprovechar para mantenimiento o remodelación", "Aprovechar para mantenimiento"),
    ("Más publicidad en redes sociales", "Más publicidad en redes sociales"),
    ("Paquetes o convenios con empresas o agencias", "Paquetes o convenios con empresas o agencias"),
    ("Cerrar habitaciones o áreas temporalmente", "Cerrar habitaciones o áreas"),
    ("Reducir personal o turnos", "Reducir personal o turnos")], V23)
INFO_DIFICIL = catalogo_v([
    ("Estimación de la demanda de las próximas semanas o meses", "Estimación de la demanda de las próximas semanas o meses"),
    ("Comparar mi ocupación con el promedio del destino", "Comparar la ocupación propia con el promedio del destino"),
    ("Precios promedio del destino", "Precios promedio del destino"),
    ("Origen o perfil de los turistas", "Origen o perfil de los turistas"),
    ("Calendario de eventos y vacaciones que afectan la demanda", "Calendario de eventos y vacaciones")], SOLO_V3)
REACCION = catalogo_v([(x, x) for x in (
    "Lanzamos promociones inmediatas", "Lo resolvemos sobre la marcha, sin un procedimiento",
    "Cambiamos precios de último momento", "Llamamos personal extra o reducimos turnos", "No hacemos cambios")], SOLO_V3)
PRECIOS = catalogo_v([(x, x) for x in (
    "Según la temporada o el calendario", "Revisando precios de otros alojamientos",
    "Con sugerencias de plataformas o de un sistema", "Según las reservaciones que ya tienen",
    "Con base en lo ocurrido en años anteriores", "Los decide el propietario o la empresa sin una regla fija")], SOLO_V3)
BARRERAS = catalogo_v([
    ("Dudas sobre qué tan confiables serían los datos", "Dudas sobre la confiabilidad de los datos"),
    ("Que tuviera costo", "Que tuviera costo"),
    ("Ya cuento con información o herramientas suficientes", "Ya cuentan con información o herramientas suficientes"),
    ("Prefiero guiarme por mi experiencia", "Prefieren guiarse por su experiencia"),
    ("Dificultad para usar herramientas digitales", "Dificultad para usar herramientas digitales"),
    ("Falta de tiempo", "Falta de tiempo")], SOLO_V3)
MESES_CAT = catalogo_v([(m, m) for m in MESES], V23)

# Texto libre que el informe resume con CODIFICACIÓN MANUAL (no reproducible aquí; solo se cuenta n).
CODIFICACION_MANUAL = [
    ("decisiones_texto", "§5.4 Decisiones que consultarían: temas y '3 informativas de 4'"),
    ("info_falta_texto", "§5.4 'Información que no tienen fácilmente': temas"),
    ("deberia_ofrecer_texto", "§5.4 'Qué debería ofrecer la plataforma': temas"),
    ("dificultades_texto", "§5.2 Evidencia cualitativa de V1 (dificultades): temas"),
    ("mejoras_texto", "§5.7 Sugerencias: temas y '7 proponen algo'"),
]


# ---------------------------------------------------------------------------------------------------
def parsear_multiple(valor: str, opciones: list[str]) -> tuple[list[str], bool]:
    """Separa una respuesta de opción múltiple usando el catálogo (hay opciones con comas).

    Devuelve (opciones encontradas, hay_texto_no_reconocido)."""
    resto, encontradas = norm(valor), []
    for op in sorted(opciones, key=len, reverse=True):
        m = re.search(r"(?:^|, )" + re.escape(op) + r"(?=, |$)", resto)
        if m:
            encontradas.append(op)
            resto = resto[:m.start()] + ", " + resto[m.end():]
    return encontradas, bool(re.sub(r"[,\s]+", "", resto))


def clasificar_ubicacion(valor: str) -> str | None:
    """Regla sin nombres de lugares concretos (salvo el municipio y el estado del proyecto)."""
    v = norm(valor).lower()
    if not v:
        return None
    partes = [p.strip() for p in v.split(",")]
    if "manzanillo" in partes[0]:
        return "Manzanillo"
    if len(partes) == 1 and partes[0] == "colima":
        return "Colima, municipio no especificado"
    if len(partes) >= 2 and partes[-1] == "colima":
        return "Otro municipio de Colima"
    if len(partes) >= 2:
        return "Fuera de Colima"
    return "No clasificable"


def primera_palabra_si_no(valor: str) -> str | None:
    p = re.split(r"[\s,.;:]+", norm(valor).lower(), maxsplit=1)[0] if norm(valor) else ""
    return {"si": "Sí", "sí": "Sí", "no": "No"}.get(p) if p else None


def clasificar_pagaria(valor: str) -> str | None:
    """Regla documentada en el README; reproduce la clasificación manual de la Tabla 9."""
    t = norm(valor).lower()
    if not t:
        return None
    if t.startswith(("tal vez", "talvez")):
        return "Tal vez"
    if t == "no":
        return "No"
    if t in ("si", "sí"):
        return "Sí, sin condiciones"
    if re.match(r"s[ií]\b", t):
        return "Sí, con condiciones"
    return "No pertinente (no responde a la pregunta)"


class Analisis:
    def __init__(self, encabezados: list[str], filas: list[list[str]]):
        self.h = [norm(x) for x in encabezados]
        self.filas = filas
        self.alertas: list[str] = []
        self._validar_estructura()
        self.validas = [r for r in filas if norm(r[COLUMNAS["consentimiento"][0]]) == CONSENTIMIENTO_SI]
        self.version = {id(r): self._version(r) for r in self.validas}
        self._validar_consentimiento_y_versiones()

    # --- validación ---------------------------------------------------------------------------------
    def _validar_estructura(self):
        if len(self.h) != TOTAL_COLUMNAS:
            raise ErrorValidacion(f"se esperaban {TOTAL_COLUMNAS} columnas y hay {len(self.h)}")
        if any(len(r) != TOTAL_COLUMNAS for r in self.filas):
            raise ErrorValidacion("hay filas con un número de campos distinto al encabezado")
        i, t = COLUMNA_FECHA
        if self.h[i] != t:
            raise ErrorValidacion(f"la columna {i} no tiene el título esperado")
        for clave, (i, titulo, *_r) in COLUMNAS.items():
            if self.h[i] != titulo:
                raise ErrorValidacion(f"la columna {i} ({clave}) no tiene el título esperado")
        for i in COLUMNAS_VACIAS:
            if any(norm(r[i]) for r in self.filas):
                raise ErrorValidacion(f"la columna {i} debía estar vacía en todos los envíos")

    def _version(self, r) -> str:
        con = lambda claves: any(norm(r[COLUMNAS[k][0]]) for k in claves)
        return V3 if con(MARCAS_V3) else V2 if con(MARCAS_V2) else V1

    def _validar_consentimiento_y_versiones(self):
        i_c = COLUMNAS["consentimiento"][0]
        valores = {norm(r[i_c]) for r in self.filas}
        if not valores <= {CONSENTIMIENTO_SI, CONSENTIMIENTO_NO}:
            raise ErrorValidacion("hay valores de consentimiento no previstos")
        for r in self.filas:
            if norm(r[i_c]) == CONSENTIMIENTO_NO and any(norm(x) for j, x in enumerate(r) if j not in (0, i_c)):
                raise ErrorValidacion("un envío sin consentimiento contiene respuestas")
        try:
            orden = sorted(self.validas, key=lambda r: datetime.strptime(norm(r[0]), "%d/%m/%Y %H:%M:%S"))
        except ValueError:
            raise ErrorValidacion("hay marcas temporales con formato no previsto") from None
        secuencia = [VERSIONES.index(self.version[id(r)]) for r in orden]
        if secuencia != sorted(secuencia):
            raise ErrorValidacion("las versiones inferidas no son sucesivas en el tiempo")
        for clave, (i, _t, disp, indet) in COLUMNAS.items():  # nadie responde una pregunta inexistente
            if clave == "consentimiento":
                continue
            for r in self.validas:
                v = self.version[id(r)]
                if norm(r[i]) and v not in disp and v not in indet:
                    raise ErrorValidacion(f"respuesta en {clave} desde una versión donde no existía")

    # --- utilidades ---------------------------------------------------------------------------------
    def valor(self, r, clave) -> str:
        return norm(r[COLUMNAS[clave][0]])

    def denominador(self, clave, filas=None) -> dict:
        _i, _t, disp, indet = COLUMNAS[clave]
        d = {"respondieron": 0, "omitidas": 0, "ausentes_estructurales": 0, "indeterminadas": 0}
        for r in (self.validas if filas is None else filas):
            v, val = self.version[id(r)], self.valor(r, clave)
            if val:
                d["respondieron"] += 1
            elif v in indet:
                d["indeterminadas"] += 1
            elif v in disp:
                d["omitidas"] += 1
            else:
                d["ausentes_estructurales"] += 1
        return d

    def simple(self, clave, catalogo, filas=None, etiqueta=None) -> dict:
        filas = self.validas if filas is None else filas
        den = self.denominador(clave, filas)
        conteo = {e: 0 for e in dict.fromkeys(catalogo.values())}
        for r in filas:
            val = self.valor(r, clave)
            if not val:
                continue
            e = etiqueta(val) if etiqueta else catalogo.get(val)
            if e is None:
                raise ErrorValidacion(f"valor no previsto en {clave}")
            conteo[e] = conteo.get(e, 0) + 1
        n = den["respondieron"]
        return {"denominador": den, "frecuencias": [{"etiqueta": e, "f": f, "n": n, "pct": pct(f, n)}
                                                   for e, f in conteo.items()]}

    def multiple(self, clave, catalogo, filas=None) -> dict:
        filas = self.validas if filas is None else filas
        den = self.denominador(clave, filas)
        respondieron = [r for r in filas if self.valor(r, clave)]
        no_reconocidas = 0
        marcadas: dict[str, int] = {e: 0 for e, _ in catalogo}
        n_por_etiqueta: dict[str, int] = {e: 0 for e, _ in catalogo}
        for r in respondieron:
            v = self.version[id(r)]
            opciones_version = {op: e for e, variantes in catalogo for vs, ops in variantes.items() if v in vs for op in ops}
            encontradas, resto = parsear_multiple(self.valor(r, clave), list(opciones_version))
            no_reconocidas += resto
            for e, variantes in catalogo:
                if any(v in vs for vs in variantes):
                    n_por_etiqueta[e] += 1
            for e in {opciones_version[op] for op in encontradas}:
                marcadas[e] += 1
        if no_reconocidas:
            raise ErrorValidacion(f"{no_reconocidas} respuesta(s) de {clave} con opciones fuera del catálogo de su versión")
        return {"denominador": den, "frecuencias": [
            {"etiqueta": e, "f": marcadas[e], "n": n_por_etiqueta[e], "pct": pct(marcadas[e], n_por_etiqueta[e])}
            for e, _ in catalogo]}

    def de_version(self, *versiones):
        return [r for r in self.validas if self.version[id(r)] in versiones]

    # --- resultados ---------------------------------------------------------------------------------
    def resultados(self) -> dict:
        val = self.validas
        manz = [r for r in val if clasificar_ubicacion(self.valor(r, "ubicacion")) == "Manzanillo"]
        hotel = lambda r: TIPO.get(self.valor(r, "tipo")) == "Hotel o resort"
        renta = lambda r: TIPO.get(self.valor(r, "tipo")) == "Renta vacacional (casa o departamento)"
        u = [int(self.valor(r, "utilidad")) for r in val if self.valor(r, "utilidad")]
        um = [int(self.valor(r, "utilidad")) for r in manz if self.valor(r, "utilidad")]
        v1 = self.de_version(V1)
        texto_v1 = [self.valor(r, "meses_alta").lower() for r in v1 if self.valor(r, "meses_alta")]
        cat_ubic = {k: k for k in ("Manzanillo", "Fuera de Colima", "Colima, municipio no especificado",
                                   "Otro municipio de Colima", "No clasificable")}
        r21 = self.denominador("col21")
        return {
            "envios": {"total": len(self.filas), "con_consentimiento": len(val),
                       "sin_consentimiento": len(self.filas) - len(val)},
            "versiones_inferidas": {v: sum(self.version[id(r)] == v for r in val) for v in VERSIONES},
            "columnas": {"total": TOTAL_COLUMNAS, "vacias_en_todos_los_envios": len(COLUMNAS_VACIAS)},
            "perfil_seccion_4": {
                "ubicacion": self.simple("ubicacion", cat_ubic, etiqueta=clasificar_ubicacion),
                "tipo": self.simple("tipo", TIPO), "puesto": self.simple("puesto", PUESTO),
                "participa_en_decisiones": self.simple("participa", PARTICIPA),
                "antiguedad": self.simple("antiguedad", ANTIGUEDAD),
                "manzanillo": {"n": len(manz), "hotel_o_resort": sum(map(hotel, manz)), "renta_vacacional": sum(map(renta, manz))},
            },
            "tabla_1_meses": {
                "alta_v2_v3": self.multiple("meses_alta", MESES_CAT, self.de_version(V2, V3)),
                "baja_v2_v3": self.multiple("meses_baja", MESES_CAT),
                "texto_v1_palabras_clave": {"n": len(texto_v1),
                                            "menciona_diciembre": sum("diciembre" in t for t in texto_v1),
                                            "menciona_semana_santa": sum("semana santa" in t for t in texto_v1),
                                            "menciona_septiembre": sum("septiembre" in t for t in texto_v1),
                                            "nota": "Conteo por palabra clave. Que septiembre se mencione como mes BAJO se verificó por lectura manual."},
                "base70_manzanillo": base70_mensual(),
            },
            "anticipacion": self.simple("anticipacion", ANTICIPACION),
            "tabla_2_dificultades": self.multiple("dificultades", DIFICULTADES),
            "frecuencia_desviacion_v3": self.simple("desviacion", DESVIACION),
            "reaccion_v3": self.multiple("reaccion", REACCION),
            "v1_cualitativo": {"dificultades_texto": self.denominador("dificultades_texto"),
                               "relatos_col21_v1": {"respondieron": sum(bool(self.valor(r, "col21")) for r in v1)},
                               "nota": "Los temas son codificación manual; aquí solo se cuenta n."},
            "tabla_3_mas_huespedes": self.multiple("mas_huespedes", MAS_HUESPEDES),
            "tabla_3_menos_huespedes": self.multiple("menos_huespedes", MENOS_HUESPEDES),
            "precios_v3": self.multiple("precios", PRECIOS),
            "usa_info": self.simple("usa_info", {"Sí": "Sí", "No": "No"}, etiqueta=primera_palabra_si_no),
            "tabla_4_herramientas": self.multiple("herramientas", HERRAMIENTAS),
            "paga_herramienta": self.simple("paga_herramienta", {"Sí": "Sí", "No": "No"}, etiqueta=primera_palabra_si_no),
            "canales": self.multiple("canales", CANALES),
            "tabla_5_info_dificil": self.multiple("info_dificil", INFO_DIFICIL),
            "tabla_6_factores": self.multiple("factores", FACTORES),
            "tabla_7_utilidad": {
                "todos": self.simple("utilidad", UTILIDAD) | {"media": round(statistics.mean(u), 2), "mediana": statistics.median(u)},
                "manzanillo": self.simple("utilidad", UTILIDAD, manz) | {"media": round(statistics.mean(um), 2), "mediana": statistics.median(um)},
            },
            "tabla_8_funcionalidades": self.multiple("funcionalidades", FUNCIONALIDADES),
            "tabla_8_funcionalidades_manzanillo": self.multiple("funcionalidades", FUNCIONALIDADES, manz),
            "tabla_9_pagaria": tabla_9(self.simple("pagaria", {k: k for k in (
                "Sí, con condiciones", "Sí, sin condiciones", "Tal vez", "No",
                "No pertinente (no responde a la pregunta)")}, etiqueta=clasificar_pagaria)),
            "tabla_10_barreras_v3": self.multiple("col21", BARRERAS, self.de_version(V3)),
            "col21_denominador_global": r21,
            "texto_libre_codificacion_manual": [
                {"seccion_informe": desc, "denominador": self.denominador(k)} for k, desc in CODIFICACION_MANUAL],
        }


def tabla_9(t: dict) -> dict:
    """Excluye 'No pertinente' del denominador (LEEME I3) y recalcula los porcentajes."""
    np_ = next(x["f"] for x in t["frecuencias"] if x["etiqueta"].startswith("No pertinente"))
    filas = [x for x in t["frecuencias"] if not x["etiqueta"].startswith("No pertinente")]
    n = sum(x["f"] for x in filas)
    return {"denominador": t["denominador"], "excluidas_no_pertinentes": np_,
            "frecuencias": [{"etiqueta": x["etiqueta"], "f": x["f"], "n": n, "pct": pct(x["f"], n)} for x in filas]}


def base70_mensual() -> dict:
    """Fila de Base70 de la Tabla 1: Manzanillo, 2 a 5 estrellas, 2016-2024 sin 2020 ni 2021."""
    if not BASE70.is_file():
        return {"estado": "sin_datos", "motivo": "no existe data/bronce/datatur/Base70centros.csv"}
    meta = json.loads(Path(str(BASE70) + ".meta.json").read_text(encoding="utf-8"))
    if sha256(BASE70) != meta.get("sha256"):
        return {"estado": "error", "motivo": "el SHA-256 de Base70 no coincide con su ficha"}
    sumas = {m: [0.0, 0.0] for m in range(1, 13)}
    with open(BASE70, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if r["centro"].strip() != "Manzanillo" or r["anio"] in ("2020", "2021") or r["categoria"].strip() == "1 estrella":
                continue
            m = int(r["mes"])
            sumas[m][0] += float(r["cuartos_disponibles"])
            sumas[m][1] += float(r["cuartos_ocupados_residentes"]) + float(r["cuartos_ocupados_no_residentes"])
    return {"estado": "ok", "pct_ocupacion": {MESES[m - 1]: float((Decimal(o) * 100 / Decimal(d)).quantize(
        Decimal("0.1"), rounding=ROUND_HALF_UP)) for m, (d, o) in sumas.items()}}


def resolver_csv(arg: str | None) -> tuple[Path, str]:
    if arg:
        return Path(arg), "--csv"
    if os.getenv(ENV_CSV):
        return Path(os.environ[ENV_CSV]), ENV_CSV
    return CSV_POR_DEFECTO, "ruta por defecto (relativa al repositorio)"


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Estadísticas agregadas de la encuesta E0 (solo biblioteca estándar)")
    p.add_argument("--csv", help=f"ruta del CSV original (si no: ${ENV_CSV} o la ruta por defecto)")
    p.add_argument("--permitir-otro-hash", action="store_true",
                   help="analiza un archivo con otro SHA-256; el resultado se marca como NO correspondiente al informe")
    args = p.parse_args(argv)
    ruta, origen = resolver_csv(args.csv)
    if not ruta.is_file():
        print(json.dumps({"error": "no se encontró el CSV", "origen_de_la_ruta": origen}, ensure_ascii=False))
        return 2
    digest = sha256(ruta)
    coincide = digest == SHA256_ESPERADO
    if not coincide and not args.permitir_otro_hash:
        print(json.dumps({"error": "el SHA-256 no coincide con el documentado (LEEME §7)",
                          "sha256_esperado": SHA256_ESPERADO, "sha256_obtenido": digest}, ensure_ascii=False))
        return 2
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        filas = list(csv.reader(f))
    try:
        analisis = Analisis(filas[0], filas[1:])
        res = analisis.resultados()
    except ErrorValidacion as e:
        print(json.dumps({"error": "validación fallida", "detalle": str(e)}, ensure_ascii=False))
        return 2
    salida = {"integridad": {"sha256": digest, "coincide_con_el_informe": coincide, "origen_de_la_ruta": origen},
              "validacion": "superada (títulos de columnas, versiones, catálogos y consentimiento)",
              "resultados": res}
    print(json.dumps(salida, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
