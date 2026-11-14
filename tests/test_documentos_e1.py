"""Consistencia documental de la entrega E1: estructura de la ficha, enlaces, relatoría y auditorías."""

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ENTREGA = RAIZ / "docs" / "E1" / "ENTREGA.md"
RELATORIA = RAIZ / "docs" / "relatoria-E1.md"
AUDITORIA_INTEGRAL = RAIZ / "docs" / "E1" / "auditoria_integral_pdf.md"
AUDITORIAS = RAIZ / "calidad" / "auditorias.md"


def _leer(ruta: Path) -> str:
    return ruta.read_text(encoding="utf-8")


def _enlaces_relativos(ruta: Path):
    texto = _leer(ruta)
    for destino in re.findall(r"\]\(([^)\s]+)\)", texto):
        if destino.startswith(("http://", "https://", "#", "mailto:")):
            continue
        yield destino.split("#")[0]


def test_ficha_tiene_la_estructura_exacta_del_pdf():
    texto = _leer(ENTREGA)
    orden = [
        "## Resumen en tres líneas",
        "## Ingeniería de Datos",
        "## Análisis Estadístico para Ciencia de Datos",
        "## Calidad en los Sistemas de Información",
        "## Relatoría de etapa",
        "## Issues de la entrega anterior",
    ]
    posiciones = [texto.index(t) for t in orden]
    assert posiciones == sorted(posiciones)
    assert re.search(r"^Equipo: .*Etiqueta: .*Tablero: ", texto, re.M)


def test_ficha_cubre_cada_criterio_de_la_rubrica():
    texto = _leer(ENTREGA)
    criterios = [
        "Valores faltantes", "Atípicos y ruido", "Normalización, discretización y reducción",
        "Integración de fuentes", "Puerta de calidad",
        "Caracterización y descomposición", "Estacionariedad y autocorrelación",
        "Cuatro modelos", "Selección por error", "Residuos y comunicación",
        "Fiabilidad y disponibilidad", "Seguridad", "Requerimientos", "Plan SQA", "Integración continua",
    ]
    faltan = [c for c in criterios if f"**{c}**" not in texto]
    assert not faltan, faltan


def test_los_enlaces_relativos_de_los_documentos_de_cierre_existen():
    rotos = []
    for ruta in (ENTREGA, RELATORIA, AUDITORIA_INTEGRAL):
        for destino in _enlaces_relativos(ruta):
            if not (ruta.parent / destino).resolve().exists():
                rotos.append(f"{ruta.name}: {destino}")
    assert not rotos, rotos


def test_la_ficha_no_afirma_lo_que_no_esta_verificado():
    texto = _leer(ENTREGA)
    assert "no creada todavía" in texto
    assert "@@" not in texto and "@@" not in _leer(RELATORIA)
    for prohibida in ("tablero está actualizado con `main`", "CI en verde", "disponibilidad cumplida"):
        assert prohibida not in texto


def test_la_relatoria_cabe_en_dos_paginas_y_sigue_la_plantilla():
    texto = _leer(RELATORIA)
    assert len(texto.split()) <= 950
    orden = [
        "## 1. Qué nos propusimos", "## 2. Qué hicimos", "## 3. Qué decidimos y por qué",
        "## 4. Qué salió mal y cómo lo corregimos", "## 5. Qué aprendimos",
        "### ", "## 6. Evidencias", "## Uso de IA generativa",
    ]
    posiciones = [texto.index(t) for t in orden if t != "### "]
    assert posiciones == sorted(posiciones)
    for materia in ("**Ingeniería de Datos.**", "**Análisis Estadístico.**", "**Calidad.**"):
        assert materia in texto


def test_las_auditorias_estan_numeradas_de_forma_consecutiva_y_sin_duplicados():
    texto = _leer(AUDITORIAS)
    numeros = [int(n) for n in re.findall(r"^## Auditoría (\d+)\b", texto, re.M)]
    assert numeros == list(range(1, len(numeros) + 1))
    assert len(numeros) >= 7
    filas = re.findall(r"^\| (\d+) \| PR #", texto, re.M)
    assert len(filas) == len(set(filas))


def test_los_recuentos_de_requerimientos_coinciden_entre_documentos():
    plan = _leer(RAIZ / "docs" / "E1" / "plan_trabajo.md")
    entrega = _leer(ENTREGA)
    assert "35 cumplidos, 3 parciales, 4 no cumplidos" in plan
    assert "35 cumplidos, 3 parciales, 4 no cumplidos" in entrega


def test_los_documentos_e1_no_usan_el_nombre_antiguo_del_prototipo():
    for ruta in (ENTREGA, RELATORIA, AUDITORIA_INTEGRAL):
        assert "StayMetrics" not in _leer(ruta)
