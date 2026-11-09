# Entrega E0 · Observatorio Turístico y Hotelero de Manzanillo (nombre comercial por definir)

Equipo: _integrantes por completar_ · Etiqueta: `e0` (**aún no creada**) · Tablero: no aplica en E0 · Corte: 2026-11-09
Repositorio: https://github.com/Leslie581/observatorio-turistico-colima

## Resumen en tres líneas
1. Observatorio de ocupación hotelera de Manzanillo, Colima; pregunta central y preguntas para E1, E2 y E3 en la [propuesta](propuesta.md).
2. Histórico de 108 meses (2016–2024) en bronce, con licencia CC BY 4.0 y hash verificado; segunda fuente (DENUE, INEGI) con captura diaria **implementada**, aún **sin ejecución real**.
3. **Pendientes obligatorios:** entrevista, ejecución real en GitHub Actions (manual y programada), registros PSP con datos reales y colaboradores docentes. Estado detallado en [`verificacion.md`](verificacion.md).

> Esta ficha enlaza evidencias que existen hoy. Donde la evidencia no existe, dice **PENDIENTE**; no se redondea a “cumplido”.
> **Plazo:** el expediente fija la entrega de E0 para el 6 de noviembre de 2026; este corte es del 9 de noviembre. Consulten con los docentes el tratamiento de la entrega tardía.

## Ingeniería de Datos
| Criterio de la rúbrica E0 | Evidencia (enlace) | Estado | Nota del equipo |
|---|---|---|---|
| Plan de recopilación (estructura, formato, frecuencia, robots.txt, términos) | [`docs/fuentes/README.md`](../fuentes/README.md), [`datatur.md`](../fuentes/datatur.md), [`denue.md`](../fuentes/denue.md) | DOCUMENTADO. El `robots.txt` de INEGI queda por archivar en la primera corrida real | DATATUR: permisos separados en confirmados, restringidos y no aclarados |
| Dos fuentes funcionando | Base70: [`pipeline.verificar_e0 --solo historico`](../../pipeline/verificar_e0.py) · DENUE: [`captura_denue.py`](../../extractores/captura_denue.py), [pruebas](../../tests/test_captura_denue.py) | Base70 **VERIFICADO** (archivo íntegro; la descarga automática está bloqueada por el servidor). DENUE: **IMPLEMENTADO**, probado con respuestas simuladas; la corrida real con token es **PENDIENTE** | El prototipo sí obtuvo 134/134 establecimientos con token real (fuera de este repositorio) |
| Una fuente programada con GitHub Actions | [`captura-diaria.yml`](../../.github/workflows/captura-diaria.yml) | IMPLEMENTADO SIN PROBAR en GitHub. Ejecución manual y programada reales: **PENDIENTE** | Pasos en [`verificacion.md`](verificacion.md#pasos-para-obtener-la-evidencia-desde-su-cuenta) |
| Serie histórica ≥ 36 periodos en bronce | [`data/bronce/datatur/Base70centros.csv`](../../data/bronce/datatur/Base70centros.csv), [LEEME](../../data/bronce/datatur/LEEME.md), [ficha](../../data/bronce/datatur/Base70centros.csv.meta.json), [verificación del hash](../fuentes/evidencias/verificacion_base70_20261109_B.json) | **VERIFICADO**: 108 meses de Manzanillo, sin huecos | La ficha dice `espejo_no_oficial` porque describe el canal real; el hash coincide con el oficial |
| Metadatos y bitácora de captura | [`base.py`](../../extractores/base.py) (fichas `.meta.json`), [`calidad/bitacora_capturas.jsonl`](../../calidad/README.md) | Fichas **VERIFICADO**; bitácora de ejecuciones **PENDIENTE** (se crea en la primera corrida) | |
| Ética y datos personales | [`denue.md`](../fuentes/denue.md#datos-personales-y-minimización), pruebas de sanitización | Sanitización **VERIFICADA con datos simulados**; sobre datos reales **PENDIENTE** (aún no hay archivos DENUE reales) | `Nombre`, razón social, contacto y domicilio se excluyen del bronce |
| Estructura del Kit | [Árbol en el README](../../README.md#estructura) | **VERIFICADO** | Diferencias con el Kit explicadas en el README |

## Análisis Estadístico
| Criterio de la rúbrica E0 | Evidencia (enlace) | Estado | Nota del equipo |
|---|---|---|---|
| Tres preguntas analíticas (variable a pronosticar, factores del experimento, grupos a comparar) | [`propuesta.md` §4](propuesta.md) | DOCUMENTADO | E2 es el único experimento controlado; E1 y E3 son observacionales |
| Serie histórica identificada | [`propuesta.md` §3 y §5](propuesta.md), [`datatur.md` §5](../fuentes/datatur.md) | VERIFICADO (108 meses) | Quiebres 2017 y COVID señalados |
| Limitación de MANOVA | [`propuesta.md` §7](propuesta.md) | DOCUMENTADO | **MANOVA no validado**; sin análisis nuevos en E0 |

## Calidad en los Sistemas de Información
| Criterio de la rúbrica E0 | Evidencia (enlace) | Estado | Nota del equipo |
|---|---|---|---|
| Registros individuales de defectos y tiempo | [`calidad/`](../../calidad/README.md) (4 plantillas) | **PENDIENTE**: plantillas con encabezado del Kit, sin datos | Cada integrante registra lo suyo; no se inventan filas |
| Bitácora de captura activa | [`calidad/bitacora_capturas.jsonl`](../../calidad/README.md) | **PENDIENTE** (sin ejecuciones reales) | |
| Tres objetivos de calidad medibles | [`calidad/objetivos.md`](../../calidad/objetivos.md) | DOCUMENTADO (O1 disponibilidad ≥ 95 %, O2 completitud e integridad, O3 cero datos personales y defectos trazables) | Verificables con `pipeline.verificar_e0` |
| Revisión compartida / Quality Lead | [`calidad/revision_calidad.md`](../../calidad/revision_calidad.md) | PENDIENTE (Quality Lead de E0 sin asignar) | |
| Pruebas automáticas | [`verificacion.md`](verificacion.md) | **VERIFICADO**: 57 aprobadas, 2 omitidas (red), cobertura 80 % | |

## Pregunta y cliente (criterio común de la rúbrica)
| Criterio | Evidencia | Estado |
|---|---|---|
| Pregunta concreta con evidencia de la entrevista; cliente con motivo para pagar | [`propuesta.md` §1–2 y §8](propuesta.md) | Pregunta y cliente: hipótesis DOCUMENTADAS. **Entrevista PENDIENTE**: sin entrevistado, fecha ni respuestas |

## Repositorio y gestión
| Requisito | Estado |
|---|---|
| Ambos integrantes con commits | PENDIENTE: aún no hay commits; cada integrante debe hacer los suyos (el historial de Git es la evidencia) |
| Tres docentes como colaboradores | PENDIENTE (se hace desde GitHub) |
| Issues propuestos | [`issues_propuestos.md`](issues_propuestos.md) (sin crear) |
| Inventario de migración | [`migracion.md`](migracion.md) |

## Relatoría de etapa
El expediente pide relatoría de etapa desde E1 (`docs/relatoria-E1.md`); **no se crea `relatoria-E0.md`**: E0 no la exige y su contenido ya está en esta ficha, la propuesta y la verificación.

## Issues de la entrega anterior
No aplica (E0 es la primera entrega).

## Uso de IA generativa
Claude Code (Anthropic) se usó para inspeccionar el prototipo, migrar y adaptar código, redactar documentos, escribir pruebas y verificar hashes y licencias. El equipo debe revisar y poder explicar cada parte.
