# Entrega E0 · Observatorio Turístico y Hotelero de Manzanillo (nombre comercial por definir)

Equipo: Leslie Valadez Macias (integrante A, `Leslie581`) y Eimy Melissa Urbina Meza (integrante B, `eimymuz`) · Etiqueta: `e0` (creada sobre `94da76d`, la fusión del PR #5 en `main`) · Tablero: no aplica en E0 · Corte: 2026-11-10; **actualizada el 2026-11-12** con la evidencia de ejecuciones programadas (posterior a la etiqueta)
Repositorio: https://github.com/Leslie581/observatorio-turistico-colima

## Resumen en tres líneas
1. Observatorio de ocupación hotelera de Manzanillo para propietarios, administradores y gerentes (pregunta y cliente: [propuesta](propuesta.md) §1–2); histórico de **108 meses** (2016–2024) y segunda fuente (DENUE) capturada en GitHub Actions: 134 de 134 establecimientos, sin campos personales.
2. Calidad: PSP individuales de las dos integrantes, tres objetivos medibles, bitácora de 8 ejecuciones y dos auditorías internas posteriores. **Disponibilidad medida: 83.3 % (5 de 6) al 2026-11-12 (66.7 % al crear la etiqueta), por debajo del objetivo de 95 %.**
3. **Limitaciones declaradas:** la entrevista tiene registro parcial; la ejecución programada (`schedule`) está **confirmada en 3 días consecutivos** (10, 11 y 12 de noviembre); los docentes aún no son colaboradores (pendiente administrativo). Detalle en [`verificacion.md`](verificacion.md).

> Esta ficha enlaza solo evidencias que existen. Lo que no está probado figura como **PENDIENTE** o **PARCIAL**.
> **Plazo:** el expediente fija E0 para el 6 de noviembre de 2026; la entrega es posterior. Consulten con los docentes su tratamiento.

## Ingeniería de Datos
| Criterio de la rúbrica E0 | Evidencia (enlace) | Estado | Nota |
|---|---|---|---|
| Ficha del observatorio: sector, región, pregunta central y cliente potencial | [`propuesta.md` §1–2](propuesta.md) | CUMPLE (cliente y disposición a pagar son **hipótesis**) | La encuesta indica que la disposición a pagar es mayormente condicional |
| Entrevista ≥ 15 min, cinco preguntas, respuestas y aprendizajes | [`propuesta.md` §8](propuesta.md), [`Entrevistas/entrevista_01.md`](Entrevistas/entrevista_01.md) | **PARCIAL**: la aplicó un colaborador externo, duración reportada (~15 min) sin comprobante, **respuestas sin publicar** (falta consentimiento) y validez sin confirmar con los docentes | Evidencia complementaria: [encuesta](encuesta/LEEME.md) e [informe](encuesta/informe_encuesta_e0.md) (11 envíos, 10 con consentimiento; exploratoria, no representativa) |
| Plan de recopilación: estructura, formato, frecuencia, acceso, robots.txt y términos | [`docs/fuentes/README.md`](../fuentes/README.md), [`datatur.md`](../fuentes/datatur.md), [`denue.md`](../fuentes/denue.md) | CUMPLE (el contenido del `robots.txt` de INEGI no está archivado en el repositorio) | Permisos de DATATUR separados en confirmados, restringidos y no aclarados |
| Dos fuentes funcionando | Base70: `python -m pipeline.verificar_e0 --solo historico`; DENUE: [`captura_denue.py`](../../extractores/captura_denue.py), [bronce](../../data/bronce/denue/2026-11-09/), [bitácora](../../calidad/bitacora_capturas.jsonl) | CUMPLE | Base70 se descarga con navegador (el servidor bloquea scripts) |
| Una fuente programada con GitHub Actions | [`captura-diaria.yml`](../../.github/workflows/captura-diaria.yml) (cron diario 13:17 UTC). Ejecuciones programadas (`schedule`) en verde: [42895566130](https://github.com/Leslie581/observatorio-turistico-colima/actions/runs/42895566130), [43094099548](https://github.com/Leslie581/observatorio-turistico-colima/actions/runs/43094099548), [43303888985](https://github.com/Leslie581/observatorio-turistico-colima/actions/runs/43303888985). Manuales en verde: [42733220215](https://github.com/Leslie581/observatorio-turistico-colima/actions/runs/42733220215), [42733335021](https://github.com/Leslie581/observatorio-turistico-colima/actions/runs/42733335021) | CUMPLE: workflow implementado, con **3 ejecuciones `schedule` exitosas** (134 de 134 cada una) y 2 manuales; al crear la etiqueta solo había manuales | GitHub retrasó los eventos `schedule` unas 7 horas respecto al cron de las 13:17 UTC (corrieron entre las 20:00 y las 20:50 UTC). La bitácora registra además 3 ejecuciones manuales anteriores cuyas páginas ya no existen en GitHub (fallo por falta de `INEGI_TOKEN`, un éxito y una omisión por duplicado) |
| Bronce con metadatos y serie histórica ≥ 36 periodos | [`Base70centros.csv`](../../data/bronce/datatur/Base70centros.csv), [LEEME](../../data/bronce/datatur/LEEME.md), [ficha](../../data/bronce/datatur/Base70centros.csv.meta.json), [verificación del hash](../fuentes/evidencias/verificacion_base70_20261109_B.json) | CUMPLE: 108 meses de Manzanillo, sin huecos; 11 fichas con hash coincidente | La ficha dice `espejo_no_oficial` porque describe el canal real; el hash coincide con el oficial |
| Bitácora de capturas y trazabilidad | [`calidad/bitacora_capturas.jsonl`](../../calidad/bitacora_capturas.jsonl) | CUMPLE: 8 ejecuciones (5 éxitos, 1 fallo, 2 omitidas por duplicado); 5 manuales y 3 programadas | |
| Ética: robots.txt, User-Agent y cero datos personales | [`denue.md`](../fuentes/denue.md#datos-personales-y-minimización) | CUMPLE: privacidad satisfactoria sobre 10 archivos reales | Se excluyen nombre, razón social, contacto y domicilio |
| Repositorio con ambas integrantes y estructura del Kit | [README](../../README.md#estructura); historial: 8 commits propios de A y 3 de B, más 4 pull requests | CUMPLE | Colaboradores docentes: **pendiente administrativo** externo al equipo |

## Análisis Estadístico para Ciencia de Datos
| Criterio de la rúbrica E0 | Evidencia (enlace) | Estado | Nota |
|---|---|---|---|
| Tres preguntas analíticas medibles: variable a pronosticar (E1), factores (E2) y grupos (E3) | [`propuesta.md` §4](propuesta.md) | CUMPLE | E2 es el único experimento controlado; E1 y E3 son observacionales |
| Serie histórica identificada (≥ 36 periodos) | [`propuesta.md` §3 y §5](propuesta.md), [`datatur.md` §5](../fuentes/datatur.md) | CUMPLE: 108 meses | Quiebres de 2017 y COVID señalados |
| Limitaciones metodológicas | [`propuesta.md` §7](propuesta.md) | CUMPLE | **MANOVA no está validado**; no se hicieron análisis nuevos en E0 |
| Pregunta central y cliente | Ver el primer criterio de Ingeniería de Datos | — | — |

## Calidad en los Sistemas de Información
| Criterio de la rúbrica E0 | Evidencia (enlace) | Estado | Nota |
|---|---|---|---|
| Registro de tiempo y de defectos individual, integrante A | [`tiempo-integrante-a.csv`](../../calidad/tiempo-integrante-a.csv), [`defectos-integrante-a.csv`](../../calidad/defectos-integrante-a.csv) | CUMPLE: 12 actividades, **750 min estimados retrospectivamente** (sin horarios), y 11 defectos corregidos sin minutos | Son estimaciones declaradas, no mediciones |
| Registro de tiempo y de defectos individual, integrante B | [`tiempo-integrante-b.csv`](../../calidad/tiempo-integrante-b.csv), [`defectos-integrante-b.csv`](../../calidad/defectos-integrante-b.csv) | CUMPLE: 9 actividades, **633 min estimados retrospectivamente** (sin horarios); 0 defectos registrados | Cero defectos es válido; las observaciones de las auditorías no son defectos propios |
| Bitácora de la captura activa | [`bitacora_capturas.jsonl`](../../calidad/bitacora_capturas.jsonl) | CUMPLE | Medición de fiabilidad (MTBF, MTTR): E1 |
| Tres objetivos de calidad medibles | [`calidad/objetivos.md`](../../calidad/objetivos.md) | CUMPLE: O1 disponibilidad ≥ 95 %, O2 completitud e integridad, O3 cero datos personales y defectos trazables | **O1 no cumplido todavía: 83.3 % (5 de 6) al 2026-11-12; 66.7 % al crear la etiqueta.** El único fallo es el de la primera ejecución (falta de `INEGI_TOKEN`). Las pruebas simuladas del cálculo ([`test_disponibilidad_escenarios.py`](../../tests/test_disponibilidad_escenarios.py)) solo validan la fórmula, no son evidencia operativa |
| Revisión de calidad (el otro integrante revisa el trabajo) | [`auditorias.md`](../../calidad/auditorias.md), [`revision_calidad.md`](../../calidad/revision_calidad.md) | CUMPLE con correcciones abiertas: **Auditoría 1** (A revisa el PR #1 de B; 30 min) y **Auditoría 2** (B revisa la parte técnica de A; 40 min), ambas **posteriores** a la integración | No hay un Quality Lead único: cada integrante es responsable de la revisión del conjunto que auditó |
| Pruebas automáticas y reproducibilidad | [`verificacion.md`](verificacion.md) | CUMPLE: **91 aprobadas y 2 omitidas** (requieren red y token) | Verificador E0 (histórico, integridad, privacidad) satisfactorio |

## Relatoría de etapa
No aplica a E0: el expediente la pide desde E1 (`docs/relatoria-E1.md`). La auditoría cruzada entre equipos (ISO 25010/25012) es de E2.

## Issues de la entrega anterior
No aplica (E0 es la primera entrega).

## Uso de IA generativa
Ambas integrantes usaron Claude Code (Anthropic) para inspeccionar el prototipo, migrar y adaptar código, redactar documentos, escribir pruebas y revisar evidencias. Cada una debe poder explicar lo que entrega.

## Pendientes declarados
| Pendiente | Estado |
|---|---|
| Ejecución programada (`schedule`) y bitácora de 7 días | EN CURSO: la ejecución programada ya está confirmada; hay 4 días con captura al 2026-11-12 |
| Consentimiento para publicar la entrevista y confirmación docente de su validez | PENDIENTE (registro parcial) |
| Correcciones abiertas de las dos auditorías | Ver [`auditorias.md`](../../calidad/auditorias.md) |
| Docentes como colaboradores del repositorio | Pendiente administrativo externo al equipo (faltan sus usuarios) |
