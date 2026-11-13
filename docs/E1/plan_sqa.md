# Plan de aseguramiento de la calidad del software (SQA) · Observatorio Turístico y Hotelero de Manzanillo

Versión 1.0 (borrador para revisión de la integrante B) · rama `e1/leslie-calidad` · corte **2026-11-13** · Autora: Leslie Valadez Macías (integrante A, Quality Lead de E1).
Estructura: IEEE 730 adaptada, según el PDF del Proyecto Integrador (pág. 16): «propósito y alcance, roles y responsabilidades, estándares y métricas, revisiones y auditorías, pruebas, reporte de problemas y acciones correctivas, herramientas, control de versiones y riesgos. El registro de defectos que abrieron en E0 es su sistema de reporte de problemas».
**Convención:** cada control dice si está **IMPLEMENTADO** (con evidencia), **PARCIAL** o **PENDIENTE**. Los controles pendientes **no** se presentan como cumplidos. Los requerimientos verificables están en [`requerimientos.md`](requerimientos.md).

## 1. Propósito y alcance
- **Propósito:** dar confianza, con evidencia repetible, en que el observatorio captura, limpia, integra y pronostica datos de ocupación hotelera de Manzanillo de forma disponible, íntegra, segura y reproducible, y que las entregas se aceptan o se rechazan con criterios explícitos.
- **Alcance (cubre):** el pipeline `bronce → plata → oro` (`pipeline/`), la captura programada de DENUE (`extractores/`, `captura-diaria.yml`), el laboratorio estadístico (`laboratorio/`), la integración continua (`ci.yml`), los datos versionados (`data/`), los registros de calidad (`calidad/`) y la documentación de `docs/`.
- **Fuera de alcance:** el tablero (aún no existe), la evaluación ISO/IEC 25010/25012 y el linaje (corresponden a E2) y la validación con clientes.
- **Aseguramiento vs. control de calidad (PDF, pág. 16):** *aseguramiento* = el **proceso** (revisiones, listas de comprobación, CI, registro de defectos); *control* = las **comprobaciones sobre el producto** (pruebas, la puerta de calidad de datos, `verificar_e0`). Este plan cubre ambos.

## 2. Roles y responsabilidades
| Rol | Persona | Responsabilidades | Independencia |
|---|---|---|---|
| **Quality Lead E1** | Leslie Valadez Macías (A) | Mantener este plan, los requerimientos, la medición de fiabilidad y seguridad; decidir con la lista de §7 si una entrega se acepta; custodiar `calidad/` | No audita lo que ella misma escribió: el pipeline lo audita B |
| Dueña del pipeline y de la calidad de datos | Leslie (A) | `pipeline/`, `pipeline/calidad/`, `tests/test_pipeline_*`, dependencias, `ci.yml`, `docs/E1/` (contrato, requerimientos, plan SQA) | — |
| Dueña del laboratorio estadístico | Eimy Melissa Urbina Meza (B) | `laboratorio/pronosticos/`, `tests/test_laboratorio_*`, `docs/E1/pronostico.md`, el tablero | Su trabajo lo revisa A (**revisión registrada: pendiente**, ver §5) |
| **Auditora recíproca del pipeline** | Eimy (B) | Revisar los cambios de A con la [lista de verificación](../../calidad/lista_verificacion_auditoria.md) y registrar hallazgos en `calidad/auditorias.md` | B no escribió el pipeline |
| **Auditora recíproca del laboratorio** | Leslie (A) | Revisar los cambios de B con la misma lista | A no escribió el laboratorio |
| Ambas | A y B | Registrar **su propio** tiempo y defectos (PSP); atender los hallazgos; no registrar el trabajo de la otra | — |
| Docentes (externos) | — | Revisión de la entrega con la rúbrica; issues que deben atenderse antes de la siguiente | Externos |
**Regla de independencia (PDF, pág. 16):** quien escribe un cambio no es quien lo revisa. En un equipo de dos, la revisión es recíproca. **Limitación reconocida:** el equipo es de dos personas y parte del trabajo se hace con apoyo de Claude Code; ese apoyo **no cuenta como revisión independiente**. Las verificaciones que las integrantes hacen con esa herramienta se declaran así en `auditorias.md`.

## 3. Estándares, normas y objetivos medibles
**Referencias:** IEEE 730 (estructura de este plan), PSP (registro de tiempo y defectos), `docs/E1/contrato_datos.md` (contrato de datos 1.0.0), LFPDPPP y términos de INEGI y SECTUR (ética de datos, `docs/fuentes/`). Las normas ISO/IEC 25010 y 25012 se aplican en E2, no antes.

### 3.1 Objetivos de calidad
| ID | Objetivo | Métrica y umbral | Estado al corte |
|---|---|---|---|
| **O1** (E0) | Disponibilidad de la captura | Éxitos ÷ (éxitos + fallos) ≥ 95 % en cualquier ventana de 7 días | **No cumplido en lo observado** (5/6 = 83.3 %) y **no evaluable** (2.84 de 7 días). [`fiabilidad.md`](fiabilidad.md) |
| **O2** (E0) | Completitud e integridad | (a) completitud DENUE entre 0.98 y 1.02 en el 100 % de las capturas exitosas; (b) 100 % del bronce con hash y tamaño iguales a su ficha | **Cumplido** (a: 5 de 5 capturas con 134 de 134; b: 24 archivos sin fallos) |
| **O3** (E0) | Cero datos personales y defectos trazables | (a) 0 campos personales en el bronce; (b) 100 % de los defectos con formato PSP | (a) **Cumplido**; (b) **parcial** (formato verificado por prueba; revisión del contenido pendiente) |
| **O4** (nuevo, **propuesto**) | El pipeline no pierde filas en silencio | `leídos = aceptados + rechazados` en el 100 % de las corridas | **Cumplido** en la corrida real y en CI (la cuenta falla la ejecución si no cuadra) |
| **O5** (nuevo, **propuesto**) | CI en verde | 100 % de las ejecuciones de `ci.yml` en `main` con éxito | 9 de 9 ejecuciones del 2026-11-13 (n pequeño) |
| **O6** (nuevo, **propuesto**) | Revisión recíproca antes de fusionar | 100 % de los PR con ≥ 1 revisión registrada antes de la fusión | **No cumplido**: 0 de 3 PR de E1 (#8, #9, #10) |
| **O7** (nuevo, **propuesto**) | Seguridad | `gitleaks` y `pip-audit` con 0 hallazgos abiertos `pip-audit`: 0; `gitleaks` 8.30.1: **0** (ejecución local del 2026-11-13; **no está en CI**) |
Los umbrales de O4 a O7 se fijan hoy, antes de tener más datos, y requieren la aprobación de B. **No se ajustan después de ver los resultados** sin dejar constancia (misma regla que `objetivos.md`).

### 3.2 Métricas de proceso
Tiempo y defectos por fase (PSP), tasa de éxito de la captura, MTTR/MTBF (cuando existan datos), defectos por severidad en auditoría, número de reglas de calidad con prueba, pruebas aprobadas/omitidas y PR revisados antes de fusionar.

## 4. Pruebas
**Estrategia:** pruebas automatizadas en capas, ejecutadas en cada push por `ci.yml`, más verificaciones independientes por la otra integrante.
| Capa | Qué comprueba | Pruebas (corte) |
|---|---|---|
| Unitarias sintéticas (declaradas) | Cada regla de la puerta de calidad (R-D01 a R-E06), fórmulas del oro, transformaciones y fiabilidad | `test_pipeline_plata` 25, `test_pipeline_oro` 11, `test_pipeline_interfaz` 8, `test_pipeline_transformaciones` 20, `test_fiabilidad` 12 |
| Con datos reales (copiados a una carpeta temporal) | El pipeline sobre el bronce real y el oro frente a una derivación independiente | `test_pipeline_real` 6, `test_verificar_oro` 8 (una con datos reales) |
| Reproducibilidad y regresión | Misma entrada, mismos bytes; bronce intacto; fallo controlado | `test_pipeline_reproducibilidad` 7, `test_exploracion` 7 |
| Estructura de los flujos | Permisos, pasos, orden, secretos acotados, que la captura no dependa de librerías opcionales | `test_workflow` 15, `test_ci_workflow` 12 |
| Extractores y verificación de E0 | Pausa, robots.txt, enmascarado del token, integridad, privacidad | `test_base` 8, `test_datatur` 10, `test_denue` 8, `test_captura_denue` 7, `test_verificar_e0` 21, `test_disponibilidad_escenarios` 13 (simuladas) |
| Registros de calidad y requerimientos | Formato PSP sin datos inventados; tabla de requerimientos bien formada y con recuento al día | `test_calidad_plantillas` 9, `test_requerimientos` 4 |
| Laboratorio estadístico (B) | Modelos, métricas, residuos, contrato del oro | `test_laboratorio_pronosticos` 25 |
| Red (opcionales) | Integración con la API real | `test_integracion_red` 2 (**omitidas**: exigen `TDL_RED=1` y token) |
**Resultado al corte (rama `e1/leslie-calidad`, con `TDL_EXIGIR_PRONOSTICOS=1`):** 236 aprobadas y 2 omitidas (red).
**Reglas de las pruebas:** las pruebas con datos simulados lo dicen y no se presentan como evidencia operativa; una omisión no cuenta como prueba ejecutada (`-rs` lista los motivos); con `TDL_EXIGIR_PRONOSTICOS=1` en CI, la falta de `statsmodels`, `scipy` o `matplotlib` es un **error**; la captura diaria no instala esas librerías y omite esas pruebas.
**Verificaciones independientes realizadas:** la auditoría 3 (B sobre el PR #8) recalculó el oro sin usar el código de A, inyectó fallas en las 14 reglas con datos reales alterados y reprodujo el oro byte a byte.
**Pendiente:** pruebas de mutación sistemáticas (solo se hizo una a mano sobre las transformaciones); pruebas de carga/estrés (no aplican a un trabajo diario); cobertura de código medida (no se mide).

## 5. Revisiones y auditorías
| Actividad | Estado | Evidencia |
|---|---|---|
| Revisión recíproca **previa** a la fusión de cada PR (regla de `plan_trabajo.md` §3) | **NO CUMPLIDA** en los PR #8, #9 y #10 | API de GitHub: 0 revisiones; fusionados 68 s, 12 s y 37 s después de abrirse, desde la cuenta `Leslie581` |
| Auditoría posterior del PR #8 por B | **REALIZADA** (con asistencia de Claude Code, declarada) | [`auditorias.md`](../../calidad/auditorias.md), «Auditoría 3» |
| Auditorías de E0 (PR #1 y parte técnica de A) | **REALIZADAS** | `auditorias.md`, auditorías 1 y 2 |
| Revisión de L2 (PR #10) por B | **No registrada** (la integrante A informa que está en curso; el PR ya está fusionado) | — |
| Revisión del laboratorio y del PR #9 por A | **No registrada** | — |
| Lista de verificación común | **IMPLEMENTADA** | [`lista_verificacion_auditoria.md`](../../calidad/lista_verificacion_auditoria.md) |
**Procedimiento (cada conjunto de cambios):** (1) la autora abre un PR y no lo fusiona; (2) la otra integrante aplica la lista de verificación, ejecuta las pruebas y registra hallazgos con archivo, línea, severidad (crítico, mayor o menor) y evidencia en `auditorias.md`; (3) la autora corrige y registra sus defectos propios; (4) se fusiona solo con CI en verde y la revisión registrada; (5) quien revisa registra su tiempo; quien corrige, el suyo. **Acción propuesta:** activar la protección de `main` (revisión obligatoria y CI en verde) con una excepción para el bot de captura; **no verificable ni activable sin permisos de administración**.

## 6. Reporte de problemas y acciones correctivas
**Sistema de reporte:** los CSV de defectos (`calidad/defectos-integrante-a.csv` y `-b.csv`, formato del Kit TDL con los diez tipos de PSP) son el registro de defectos **corregidos**; los hallazgos de una revisión ajena van a `auditorias.md`; lo que **puede** salir mal va a [`riesgos.md`](../../calidad/riesgos.md) y no a los CSV.
**Flujo:** detectar → registrar (defecto propio en el CSV, hallazgo ajeno en `auditorias.md`) → clasificar (severidad) → corregir con un commit que lo referencie → verificar (prueba o revisión) → cerrar. Un defecto solo se anota cuando se introdujo **y** se corrigió; los minutos de corrección no se inventan.
**Acciones correctivas pendientes (estado al corte):**
| Origen | Acción | Estado |
|---|---|---|
| Auditoría 3, D1 | No fusionar sin revisión de la otra integrante | **Abierta** (se repitió en los PR #9 y #10) |
| Auditoría 3, D2 | Actualizar los textos sobre el estado de CI | **Cerrada** en la rama L2 (PR #10) |
| Auditoría 3, R3 | Comprobar en CI que el oro regenerado es igual al versionado | **Cerrada**: `pipeline/verificar_oro.py` (CI en éxito en `main`) |
| Auditoría 3, R4 | Acordar cuándo se versiona un `resumen_<corrida>.json` nuevo | **Abierta** |
| Auditoría 3, R5 | Celdas del agregado de oferta con un solo establecimiento | **Abierta** (RNF-PRI-03) |
| Auditoría 3, O1 | Considerar «conservar la primera copia válida» en una versión futura del contrato | **Abierta**; cambio de contrato, no urgente |
| Auditoría 3, O4 | Una sola fuente de requisitos del laboratorio (`requirements-pronosticos.txt` de B frente a `requirements-lab.txt`) | **Abierta**, de B; no verificado en esta rama |
| E0, `riesgos.md` I3 | O1 (95 %) no cumplido | **Abierta**: se mide en [`fiabilidad.md`](fiabilidad.md) |
| Este plan, seguridad | Integrar `gitleaks` en CI, protección de `main`, acciones por *hash*, copia independiente del bronce | **Abiertas** ([`seguridad.md`](seguridad.md) §7) |

## 7. Criterios para aceptar o rechazar una entrega
**Se acepta** (pasa a la etiqueta `e<n>`) solo si **todo** lo siguiente es cierto y está enlazado a evidencia:
1. `main` en el commit a etiquetar tiene `ci.yml` en **éxito**: `ruff`, `pytest` (sin fallos; las omitidas listadas con motivo), `pipeline.ejecutar`, `pipeline.verificar_oro` y `pipeline.verificar_e0`.
2. `python -m pipeline.verificar_e0 --solo historico --solo integridad --solo privacidad --exigir-datos` termina con código 0.
3. Ninguna afirmación de la ficha `ENTREGA.md` carece de evidencia; lo no probado figura como PENDIENTE o PARCIAL.
4. Sin secretos ni datos personales (`gitleaks` con 0 hallazgos abiertos, ejecutado sobre el commit a etiquetar; privacidad satisfactoria).
5. Cada PR integrado tiene su revisión recíproca **registrada**, o la excepción queda declarada en la ficha.
6. Los PSP de ambas integrantes están al día, sin tiempos ni defectos inventados.
7. Los hallazgos **críticos** y **mayores** de las auditorías están corregidos o declarados abiertos con su justificación.
**Se rechaza (no se etiqueta)** si ocurre cualquiera de: CI en rojo en el commit a etiquetar; un secreto en el repositorio; datos personales en el bronce; una cifra de la ficha que contradiga la evidencia; o una verificación presentada como ejecutada que no se ejecutó.
**Estado hoy (no es un dictamen de entrega):** los criterios 1 y 2 se comprueban con CI y con el verificador, y estaban en verde en las ejecuciones del 2026-11-13; el 4 se cumplió con la ejecución local de `gitleaks` del 2026-11-13 (0 hallazgos), pero **no está automatizado**: hay que repetirla sobre el commit a etiquetar; el 5 **no se cumple** para los PR #8, #9 y #10; el 3 depende de que la ficha `docs/E1/ENTREGA.md` (que **aún no existe**) cite esta evidencia; y los criterios 6 y 7 **no se evaluaron aquí**: hay que revisarlos al momento de etiquetar (los 240 minutos de PSP aún sin registrar y los hallazgos abiertos de §6 cuentan).

## 8. Herramientas
| Herramienta | Versión fijada | Uso | Estado |
|---|---|---|---|
| Python | 3.13 (CI y local: 3.13.15) | Lenguaje | Implementada |
| `pytest` | 9.2.0 | Pruebas | Implementada |
| `ruff` | 0.17.5 | Linter (`ruff.toml`) | Implementada |
| `pandera` | 0.36.0 | Puerta de calidad de datos (R-D01 y el esquema del oro) | Implementada |
| `pip-audit` | 2.10.1 | Vulnerabilidades de dependencias | Implementada (trabajo aparte en CI) |
| `gitleaks` | 8.30.1 (binario oficial, verificado por *hash*) | Búsqueda de secretos en el historial | **Ejecutada localmente** (0 hallazgos); **no integrada en CI** |
| GitHub Actions | `ci.yml`, `captura-diaria.yml` | Integración continua y captura programada | Implementada |
| `pipeline.verificar_e0`, `pipeline.verificar_oro`, `pipeline.fiabilidad` | del repositorio | Verificaciones de datos, del oro y de fiabilidad | Implementadas |
| Registros PSP (CSV) | Kit TDL | Tiempo y defectos | Implementada |

## 9. Control de versiones y de configuración
- **Ramas:** `e1/leslie-*` y `e1/eimy-*`; integración a `main` por pull request; no se modifica `main` directamente ni se reescribe el historial.
- **Etiquetas:** `e0` y `e1` sobre un commit de `main` **antes de las 23:59** del día de entrega; no se mueven una vez creadas. (`e0` está en `6585afe`; `e1` **no existe**.)
- **Datos:** `.gitattributes` conserva los datos byte a byte (`data/** -text`); se versiona solo el oro público, agregado y reproducible; el bronce se publica sin datos personales ni de permiso incierto.
- **Dependencias:** versiones exactas (`==`) en tres archivos separados (captura, laboratorio y desarrollo), para que una falla de una librería opcional no detenga la captura diaria.
- **Atribución:** los commits asistidos por Claude Code lo declaran con `Co-Authored-By`.
- **Pendiente:** protección de `main`.

## 10. Riesgos de calidad
Los riesgos generales viven en [`riesgos.md`](../../calidad/riesgos.md) (R1 a R8 e I1 a I4). Los **nuevos** de E1, con su mitigación:
| ID | Riesgo | Mitigación | Estado |
|---|---|---|---|
| Q1 | Fusionar sin revisión repite la situación de E0 y deja pasar defectos | Protección de `main`; seguir §5 | **Materializado** (PR #8, #9 y #10) |
| Q2 | La medición de fiabilidad no alcanza los 7 días ni los 2 incidentes que pide la rúbrica | Declararlo; actualizar con `pipeline.fiabilidad`; no suponer valores | Abierto |
| Q3 | Un secreto futuro que nadie detecte porque `gitleaks` no corre en cada cambio, o uno fuera de su alcance (registros y secretos de GitHub) | Integrar `gitleaks` en CI ([`seguridad.md`](seguridad.md) §3.4); rotar el token si hay duda | Abierto |
| Q4 | El único respaldo del bronce es GitHub | Copia independiente y prueba periódica de restauración | Abierto |
| Q5 | Plazo: E1 vence el 2026-11-13 y faltan la ficha `ENTREGA.md`, la relatoría y el tablero | Priorizar; declarar lo pendiente en la ficha | Abierto |
| Q6 | Equipo de dos personas y apoyo de una herramienta de IA: la independencia de la revisión es limitada | Declararlo en cada auditoría; ejecutar y reproducir, no solo leer | Aceptado |
| Q7 | El agregado de oferta DENUE no protege las celdas de un solo establecimiento | No publicarlo en el tablero sin agrupar celdas < 3 | Abierto |

## 11. Qué está implementado y qué falta (resumen)
| Implementado (con evidencia) | Parcial | Pendiente |
|---|---|---|
| Puerta de calidad y cuarentena, pipeline determinista, oro validado, CI en `main`, `verificar_oro`, `pip-audit`, permisos mínimos, restauración del bronce, registro de defectos y de tiempo, lista de auditoría, medición de fiabilidad (lo calculable), `gitleaks` ejecutado localmente | Revisión recíproca previa a fusionar, revisión del PSP, medición de O1/MTBF/A (faltan datos), reproducción independiente del laboratorio | `gitleaks` en CI, protección de `main`, ficha `ENTREGA.md`, relatoría, tablero, copia independiente del bronce, acciones por *hash* |
