# Entrega E0 · Observatorio Turístico y Hotelero de Manzanillo (nombre comercial por definir)

Equipo: _integrantes por completar_ · Etiqueta: `e0` (**aún no creada**) · Tablero: no aplica en E0 · Corte: 2026-11-09
Repositorio: https://github.com/Leslie581/observatorio-turistico-colima

## Resumen en tres líneas
1. Observatorio de ocupación hotelera de Manzanillo, Colima; pregunta central y preguntas para E1, E2 y E3 en la [propuesta](propuesta.md).
2. Histórico de 108 meses (2016–2024) en bronce, con licencia CC BY 4.0 y hash verificado; segunda fuente (DENUE, INEGI) capturada **en GitHub Actions** (134 de 134 establecimientos, sin campos personales). La ejecución **programada** (`schedule`) aún no tiene evidencia.
3. **Pendientes:** entrevista, PSP y auditoría cruzada (las integra la compañera); ejecución programada real y bitácora de 7 días; colaboradores docentes; disponibilidad actual **66.7 % (2 de 3), por debajo del objetivo de 95 %**. Estado detallado en [`verificacion.md`](verificacion.md).

> Esta ficha enlaza evidencias que existen hoy. Donde la evidencia no existe, dice **PENDIENTE**; no se redondea a “cumplido”.
> **Plazo:** el expediente fija la entrega de E0 para el 6 de noviembre de 2026; este corte es del 9 de noviembre. Consulten con los docentes el tratamiento de la entrega tardía.

## Ingeniería de Datos
| Criterio de la rúbrica E0 | Evidencia (enlace) | Estado | Nota del equipo |
|---|---|---|---|
| Plan de recopilación (estructura, formato, frecuencia, robots.txt, términos) | [`docs/fuentes/README.md`](../fuentes/README.md), [`datatur.md`](../fuentes/datatur.md), [`denue.md`](../fuentes/denue.md) | DOCUMENTADO. El `robots.txt` de INEGI queda por archivar en la primera corrida real | DATATUR: permisos separados en confirmados, restringidos y no aclarados |
| Dos fuentes funcionando | Base70: [`pipeline.verificar_e0 --solo historico`](../../pipeline/verificar_e0.py) · DENUE: [`captura_denue.py`](../../extractores/captura_denue.py), [bronce publicado](../../data/bronce/denue/2026-11-09/), [bitácora](../../calidad/bitacora_capturas.jsonl) | Base70 **VERIFICADO** (archivo íntegro; la descarga automática está bloqueada por el servidor). DENUE **VERIFICADO**: capturas reales del 2026-11-09 con 134 de 134 registros y 0 controles fallidos (ejecuciones `42730477358` y `42733335021` de la bitácora, más una captura local con el mismo resultado) | |
| Una fuente programada con GitHub Actions | [`captura-diaria.yml`](../../.github/workflows/captura-diaria.yml); ejecuciones manuales: [42729922838](https://github.com/Leslie581/observatorio-turistico-colima/actions/runs/42729922838), [42730477358](https://github.com/Leslie581/observatorio-turistico-colima/actions/runs/42730477358), [42732765759](https://github.com/Leslie581/observatorio-turistico-colima/actions/runs/42732765759), [42733220215](https://github.com/Leslie581/observatorio-turistico-colima/actions/runs/42733220215), [42733335021](https://github.com/Leslie581/observatorio-turistico-colima/actions/runs/42733335021) | Workflow implementado y **ejecutado manualmente en GitHub** (resultado de captura según la bitácora: 42729922838 fallo por falta de `INEGI_TOKEN`; 42730477358 y 42733335021 éxito; 42732765759 y 42733220215 omitidas por duplicado). Ejecución **programada** (`schedule`): **PENDIENTE** | El estado verde/rojo de cada job se confirma en la página de cada ejecución; la 42730477358 terminó en rojo por la disponibilidad informativa (corregido en `156a024`); **confirmar en GitHub** que 42732765759, 42733220215 y 42733335021 (posteriores a la corrección) terminaron en verde |
| Serie histórica ≥ 36 periodos en bronce | [`data/bronce/datatur/Base70centros.csv`](../../data/bronce/datatur/Base70centros.csv), [LEEME](../../data/bronce/datatur/LEEME.md), [ficha](../../data/bronce/datatur/Base70centros.csv.meta.json), [verificación del hash](../fuentes/evidencias/verificacion_base70_20261109_B.json) | **VERIFICADO**: 108 meses de Manzanillo, sin huecos | La ficha dice `espejo_no_oficial` porque describe el canal real; el hash coincide con el oficial |
| Metadatos y bitácora de captura | [`base.py`](../../extractores/base.py) (fichas `.meta.json`), [`calidad/bitacora_capturas.jsonl`](../../calidad/bitacora_capturas.jsonl) | **VERIFICADO**: 5 fichas con SHA-256 coincidente (`verificar_e0 --solo integridad`); bitácora con 5 ejecuciones reales | |
| Ética y datos personales | [`denue.md`](../fuentes/denue.md#datos-personales-y-minimización), pruebas de sanitización | **VERIFICADO** también sobre datos reales: `verificar_e0 --solo privacidad` revisó 4 archivos DENUE publicados por el bot sin campos excluidos | Se excluyen nombre, razón social, contacto y domicilio |
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
| Registros individuales de defectos y tiempo | [`calidad/`](../../calidad/README.md) | **Integrante A (parte técnica):** 720 min **estimados retrospectivamente** (480 prototipo el 2026-11-08 + 240 definitivo el 2026-11-09), sin horarios de reloj, en la columna `minutos_estimados`; 11 defectos corregidos con evidencia, sin minutos de corrección (ver `calidad/psp-integrante-a-por-confirmar.md`). **Integrante B:** plantillas vacías con las mismas columnas; las completa la compañera | Estimaciones declaradas por la integrante A, no mediciones; pendientes, incidencias y riesgos en `calidad/riesgos.md` |
| Bitácora de captura activa | [`calidad/bitacora_capturas.jsonl`](../../calidad/bitacora_capturas.jsonl) | **VERIFICADO**: 5 ejecuciones reales (2 éxitos, 1 fallo, 2 omitidas por duplicado). Disponibilidad medida: **2 de 3 = 66.7 %**, objetivo 95 % **no cumplido todavía** | Se excluyen las omitidas del cálculo; la medición completa (MTBF, MTTR) es de E1 |
| Tres objetivos de calidad medibles | [`calidad/objetivos.md`](../../calidad/objetivos.md) | DOCUMENTADO (O1 disponibilidad ≥ 95 %, O2 completitud e integridad, O3 cero datos personales y defectos trazables) | Verificables con `pipeline.verificar_e0` |
| Revisión compartida / Quality Lead | [`calidad/revision_calidad.md`](../../calidad/revision_calidad.md) | PENDIENTE (Quality Lead de E0 sin asignar) | |
| Pruebas automáticas | [`verificacion.md`](verificacion.md) | **VERIFICADO**: 69 aprobadas, 2 omitidas (red) | |

## Pregunta y cliente (criterio común de la rúbrica)
| Criterio | Evidencia | Estado |
|---|---|---|
| Pregunta concreta con evidencia de la entrevista; cliente con motivo para pagar | [`propuesta.md` §1–2 y §8](propuesta.md) | Pregunta y cliente: hipótesis DOCUMENTADAS. **Entrevista: la integra la compañera** (sin respuestas en el repositorio todavía) |

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


## Pendientes que completa la compañera (no completar desde otra copia)
| Pendiente | Dónde se integra | Estado |
|---|---|---|
| Registro de la entrevista (≥ 15 min, cinco preguntas, respuestas, aprendizajes) | [`propuesta.md` §8](propuesta.md) | PENDIENTE de integrar; no hay respuestas en el repositorio |
| Registros PSP propios (tiempo y defectos) | `calidad/tiempo-integrante-b.csv`, `calidad/defectos-integrante-b.csv` | PENDIENTE |
| Auditoría de la parte técnica (A) con la [lista de verificación](../../calidad/lista_verificacion_auditoria.md), registrada en [`auditorias.md`](../../calidad/auditorias.md) | `calidad/auditorias.md` | PENDIENTE; no existe ninguna auditoría todavía |
| Nombres de integrantes en esta ficha y en la propuesta | `ENTREGA.md`, `propuesta.md` | PENDIENTE |
| Responsable de revisión de calidad de E0 | [`revision_calidad.md`](../../calidad/revision_calidad.md) | PENDIENTE |