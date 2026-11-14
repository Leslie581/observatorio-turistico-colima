# Plan de aseguramiento de la calidad del software (SQA) · Observatorio Turístico y Hotelero de Manzanillo

Versión 1.1 · revisada por la integrante B (Auditoría 5) y actualizada por la autora con las Auditorías 6 y 7 · rama `e1/cierre-documental` · corte **2026-11-14** (la verificación local de este corte se hizo entre las 03:10 y las 05:00 UTC) · Autora: Leslie Valadez Macías (integrante A, Quality Lead de E1).
Estructura: IEEE 730 adaptada, según el PDF del Proyecto Integrador (pág. 16): «propósito y alcance, roles y responsabilidades, estándares y métricas, revisiones y auditorías, pruebas, reporte de problemas y acciones correctivas, herramientas, control de versiones y riesgos. El registro de defectos que abrieron en E0 es su sistema de reporte de problemas».
**Convención:** cada control dice si está **IMPLEMENTADO** (con evidencia), **PARCIAL** o **PENDIENTE**. Los controles pendientes **no** se presentan como cumplidos. Los requerimientos verificables están en [`requerimientos.md`](requerimientos.md).

## 1. Propósito y alcance
- **Propósito:** dar confianza, con evidencia repetible, en que el observatorio captura, limpia, integra y pronostica datos de ocupación hotelera de Manzanillo de forma disponible, íntegra, segura y reproducible, y que las entregas se aceptan o se rechazan con criterios explícitos.
- **Alcance (cubre):** el pipeline `bronce → plata → oro` (`pipeline/`), la captura programada de DENUE (`extractores/`, `captura-diaria.yml`), el laboratorio estadístico (`laboratorio/`), la integración continua (`ci.yml`), los datos versionados (`data/`), los registros de calidad (`calidad/`) y la documentación de `docs/`.
- **Fuera de alcance:** la evaluación ISO/IEC 25010/25012 y el linaje (corresponden a E2) y la validación con clientes.
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
| **O1** (E0) | Disponibilidad de la captura | Éxitos ÷ (éxitos + fallos) ≥ 95 % en cualquier ventana de 7 días | **No cumplido en lo observado** (6/7 = 85.7 %; IC 95 % exacto 42.1 % a 99.6 %, que incluye el 95 %) y **no evaluable** (3.83 de 7 días; corte 2026-11-13 20:28 UTC). [`fiabilidad.md`](fiabilidad.md) |
| **O2** (E0) | Completitud e integridad | (a) completitud DENUE entre 0.98 y 1.02 en el 100 % de las capturas exitosas; (b) 100 % del bronce con hash y tamaño iguales a su ficha | **Cumplido** (a: 5 de 5 capturas con 134 de 134; b: 24 archivos sin fallos) |
| **O3** (E0) | Cero datos personales y defectos trazables | (a) 0 campos personales en el bronce; (b) 100 % de los defectos con formato PSP | (a) **Cumplido**; (b) **parcial** (formato verificado por prueba; revisión del contenido pendiente) |
| **O4** (nuevo) | El pipeline no pierde filas en silencio | `leídos = aceptados + rechazados` en el 100 % de las corridas | **Cumplido** en la corrida real y en CI (la cuenta falla la ejecución si no cuadra) |
| **O5** (nuevo) | CI en verde | 100 % de las ejecuciones de `ci.yml` en `main` con éxito | **No cumplido en el historial; cumplido en el último commit.** `ci.yml` suma 25 ejecuciones (corte 2026-11-14 03:14 UTC): 21 en éxito, 1 cancelada por concurrencia y **3 fallidas**; en `main` (push): 6 en éxito, 1 cancelada y **1 fallida (`06452fd`, fusión del tablero)**. Las 3 fallidas son del commit `9489dc5`; las corrigió `eb8f606` y `ac9c88d` (ejecución 43548657495) terminó en **éxito**. Detalle en §6 |
| **O6** (nuevo) | Revisión recíproca antes de fusionar | 100 % de los PR con ≥ 1 revisión registrada antes de la fusión | **No cumplido**: 0 de 9 PR de E1 (#7 a #15); ver §5.1 |
| **O7** (nuevo) | Seguridad | `gitleaks` y `pip-audit` con 0 hallazgos abiertos | `pip-audit`: 0 (incluidas las dependencias transitivas del tablero); `gitleaks` 8.30.1: **0** (ejecución local del 2026-11-13, resumen versionado en `calidad/evidencia/`); ambos corren ahora **automáticamente en CI** (trabajos `auditoria-dependencias` y `secretos`; su primera ejecución en GitHub llegará con el push) |
Los umbrales de O4 a O7 se fijan hoy, antes de tener más datos, y requieren la aprobación de B. **No se ajustan después de ver los resultados** sin dejar constancia (misma regla que `objetivos.md`).

### 3.2 Métricas de proceso
Tiempo y defectos por fase (PSP), tasa de éxito de la captura, MTTR/MTBF (cuando existan datos), defectos por severidad en auditoría, número de reglas de calidad con prueba, pruebas aprobadas/omitidas y PR revisados antes de fusionar.

## 4. Pruebas
**Estrategia:** pruebas automatizadas en capas, ejecutadas en cada push por `ci.yml`, más verificaciones independientes por la otra integrante.
| Capa | Qué comprueba | Pruebas (corte) |
|---|---|---|
| Unitarias sintéticas (declaradas) | Cada regla de la puerta de calidad (R-D01 a R-E06), fórmulas del oro, transformaciones y fiabilidad | `test_pipeline_plata` 25, `test_pipeline_oro` 11, `test_pipeline_interfaz` 8, `test_pipeline_transformaciones` 20, `test_fiabilidad` 22 |
| Con datos reales (copiados a una carpeta temporal) | El pipeline sobre el bronce real y el oro frente a una derivación independiente | `test_pipeline_real` 6, `test_verificar_oro` 8 (una con datos reales) |
| Reproducibilidad y regresión | Misma entrada, mismos bytes; bronce intacto; fallo controlado | `test_pipeline_reproducibilidad` 7, `test_exploracion` 7 |
| Estructura de los flujos | Permisos, pasos, orden, secretos acotados, que la captura no dependa de librerías opcionales | `test_workflow` 15, `test_ci_workflow` 12 |
| Extractores y verificación de E0 | Pausa, robots.txt, enmascarado del token, integridad, privacidad | `test_base` 8, `test_datatur` 10, `test_denue` 8, `test_captura_denue` 7, `test_verificar_e0` 21, `test_disponibilidad_escenarios` 13 (simuladas) |
| Registros de calidad, requerimientos y evidencia | Formato PSP sin datos inventados; tabla de requerimientos bien formada y con recuento al día; evidencia de `gitleaks` coherente y sin rutas privadas | `test_calidad_plantillas` 9, `test_requerimientos` 4, `test_evidencia_gitleaks` 4 |
| Laboratorio estadístico (B) | Modelos, métricas, residuos, contrato del oro | `test_laboratorio_pronosticos` 32 |
| Red (opcionales) | Integración con la API real | `test_integracion_red` 2 (**omitidas**: exigen `TDL_RED=1` y token) |
**Resultado al corte (rama `e1/cierre-documental`, con `TDL_EXIGIR_PRONOSTICOS=1` y `TDL_EXIGIR_TABLERO=1`, instaladas las dependencias del tablero):** **320 aprobadas y 2 omitidas** (las 2 de red, sin `TDL_RED=1`; ninguna del tablero; `ruff check` sin errores; `pipeline.verificar_oro` con `ok: true`). El CI de `main` está en **éxito** en `ac9c88d`; el rojo anterior (`06452fd`) se debía a una prueba del tablero que dependía de `__pycache__` y se corrigió en `eb8f606` (§6). `ci.yml` de esta rama instala las dependencias del tablero y **exige** que sus pruebas se ejecuten (§6); esa ejecución en GitHub llegará con el push.
**Reglas de las pruebas:** las pruebas con datos simulados lo dicen y no se presentan como evidencia operativa; una omisión no cuenta como prueba ejecutada (`-rs` lista los motivos); con `TDL_EXIGIR_PRONOSTICOS=1` en CI, la falta de `statsmodels`, `scipy` o `matplotlib` es un **error**; la captura diaria no instala esas librerías y omite esas pruebas.
**Verificaciones independientes realizadas:** la auditoría 3 (B sobre el PR #8) recalculó el oro sin usar el código de A, inyectó fallas en las 14 reglas con datos reales alterados y reprodujo el oro byte a byte.
**Pendiente:** pruebas de mutación sistemáticas (solo se hizo una a mano sobre las transformaciones); pruebas de carga/estrés (no aplican a un trabajo diario); cobertura de código medida (no se mide).

## 5. Revisiones y auditorías
| Actividad | Estado | Evidencia |
|---|---|---|
| Revisión recíproca **previa** a la fusión de cada PR (regla de `plan_trabajo.md` §3) | **NO CUMPLIDA** en los PR #7 a #15 (los nueve de E1) | API de GitHub (2026-11-14): 0 revisiones; fusionados 15, 68, 12, 37, 9, 13, 25, 19 y 11 s después de abrirse, desde la cuenta `Leslie581`. Detalle y excepción en §5.1 |
| Auditorías posteriores de B sobre pull requests de A | **REALIZADAS** (con asistencia de Claude Code, declarada): Auditoría 3 (PR #8), Auditoría 4 (PR #10) y Auditoría 5 (PR #11), las tres **integradas en `main`** (la 5, por el PR #13) | [`auditorias.md`](../../calidad/auditorias.md) |
| Auditorías de E0 (PR #1 y parte técnica de A) | **REALIZADAS** | `auditorias.md`, auditorías 1 y 2 |
| Revisión de A sobre el cierre estadístico de B (PR #12) | **REALIZADA y registrada como Auditoría 6** en `auditorias.md` **en la rama `e1/cierre-documental`** (sin commit ni fusión todavía) | [`auditorias.md`](../../calidad/auditorias.md), «Auditoría 6» |
| Revisión de A sobre el PR #15 (cierre del tablero de B) | **REALIZADA y registrada como Auditoría 7** en `auditorias.md` **en la rama `e1/cierre-documental`** (sin commit ni fusión todavía); **posterior** a la fusión | [`auditorias.md`](../../calidad/auditorias.md), «Auditoría 7» |
| Revisión de A sobre los PR #7, #9, #13 y #14 (contrato, laboratorio base, auditoría 5 de B y tablero MVP) | **No registrada** | — |
| Lista de verificación común | **IMPLEMENTADA** | [`lista_verificacion_auditoria.md`](../../calidad/lista_verificacion_auditoria.md) |
**Procedimiento (cada conjunto de cambios):** (1) la autora abre un PR y no lo fusiona; (2) la otra integrante aplica la lista de verificación, ejecuta las pruebas y registra hallazgos con archivo, línea, severidad (crítico, mayor o menor) y evidencia en `auditorias.md`; (3) la autora corrige y registra sus defectos propios; (4) se fusiona solo con CI en verde y la revisión registrada; (5) quien revisa registra su tiempo; quien corrige, el suyo. **No implementado:** la protección de `main` (revisión obligatoria y CI en verde, con una excepción para el bot de captura) **no se puede verificar ni activar sin permisos de administración**.

### 5.1 Fusiones sin revisión previa, acción correctiva de proceso y excepción de E1
**Hecho verificado (API pública de GitHub, 2026-11-14):** los nueve pull requests de E1 (#7 a #15) se fusionaron **antes** de cualquier revisión recíproca, con 0 revisiones registradas y desde la cuenta `Leslie581`. Las Auditorías 3, 4 y 5 señalaron el problema para los #8 a #11; las Auditorías 6 y 7 lo señalan para los #12 y #15; y los #13 y #14 (fusionados después) y el #7 (anterior) repiten la misma práctica:
| PR | Contenido | Autora | Abierto → fusionado | Revisión recíproca posterior registrada |
|---|---|---|---|---|
| #7 | Contrato de datos (L0) | A | 15 s | **No registrada** |
| #8 | Pipeline (L1) | A | 68 s | Auditoría 3 (B) |
| #9 | Laboratorio de pronósticos | B | 12 s | **No registrada** por A para este PR |
| #10 | L2: exploración, transformaciones y CI | A | 37 s | Auditoría 4 (B) |
| #11 | L3: calidad, fiabilidad, seguridad y plan SQA | A | 9 s | Auditoría 5 (B), integrada en `main` por el PR #13 |
| #12 | Cierre estadístico | B | 13 s | Auditoría 6 (A), registrada en la rama `e1/cierre-documental`, **sin fusionar todavía** |
| #13 | Auditoría 5 de B | B | 25 s | **No registrada** |
| #14 | Tablero (MVP) | B (trabajo de B; el commit figura a nombre de A por haberse publicado desde la máquina de A) | 19 s | **No registrada**; además dejó el CI de `main` en rojo (§6) |
| #15 | Cierre del tablero y corrección de la prueba | B | 11 s | Auditoría 7 (A), registrada en la rama `e1/cierre-documental`, **sin fusionar todavía** |
Es el defecto de proceso **D1 de las Auditorías 3 a 7**, recurrente. El plan de trabajo (§3) pedía que desde E1 todo cambio se integrara por pull request **revisado por la otra integrante**; no se cumplió.

**Protección de ramas: NO configurada.** El 2026-11-13 a las 19:14 UTC la API pública de GitHub devolvía para `main` `protected: false`, sin comprobaciones obligatorias y sin reglas ni *rulesets* activos. **No hay ninguna protección configurada.** Activarla (revisión obligatoria de 1 aprobación y CI en verde antes de fusionar, con una excepción para el bot de captura, riesgo R2 de `riesgos.md`) **requiere permisos de administración y no se ha hecho**; mientras no exista, el cumplimiento depende solo de la disciplina del equipo.

**Acción correctiva de proceso (NO implementada; requiere la aceptación de ambas integrantes):**
1. La autora abre el pull request y **no lo fusiona**.
2. La otra integrante deja una **revisión visible en el pull request** (aprobación o comentarios) y, cuando haya hallazgos, la registra en `calidad/auditorias.md`.
3. Se fusiona solo con CI en verde y esa revisión; **no se fusiona el mismo día en segundos**.
4. Antes de cada etiqueta se comprueba la lista de pull requests fusionados y sus revisiones: `curl -s https://api.github.com/repos/Leslie581/tdl-turistico-colima/pulls/<n>/reviews` (0 = no hay revisión previa).
5. Si se activa la protección de `main`, se anota la fecha y se verifica con `GET /branches/main` (campo `protected`).

**Excepción explícita para la entrega E1 (NO declarada todavía; requiere la conformidad de ambas integrantes y declararse en `docs/E1/ENTREGA.md`):**
- **Alcance:** el criterio 5 de §7 («cada PR integrado tiene su revisión recíproca registrada») **se incumple** para los PR #7 a #15 y se acepta **solo para la etiqueta `e1`**; no es un precedente para E2.
- **Razones que se invocarían:** cada fusión tiene una revisión recíproca **posterior** (#11, #12 y #15 en las Auditorías 5, 6 y 7) con ejecución real de pruebas, salvo los PR #7, #9, #13 y #14; las auditorías no hallaron defectos técnicos bloqueantes. **Contra la excepción:** el PR #14 se fusionó 14 s después de abrirse **con el CI fallando** y dejó `main` en rojo, y el PR #15 se fusionó 11 s después de abrirse, antes de que terminara su CI; el CI en verde **no** estuvo garantizado en cada commit fusionado.
- **Condiciones de cierre:** (a) la Auditoría 5 de B ya está en `main`; las Auditorías 6 y 7 de A están registradas en la rama `e1/cierre-documental` (falta fusionarlas); (b) registrar o declarar pendiente la revisión de A sobre los PR #7, #9, #13 y #14; (c) citar el defecto D1 y esta excepción en la ficha; (d) **no afirmar** que existe protección de ramas.
- **Lo que la excepción NO cubre:** no reemplaza el control previo; si una revisión posterior hubiera hallado un defecto bloqueante, la etiqueta no se crearía.

## 6. Reporte de problemas y acciones correctivas
**Sistema de reporte:** los CSV de defectos (`calidad/defectos-integrante-a.csv` y `-b.csv`, formato del Kit TDL con los diez tipos de PSP) son el registro de defectos **corregidos**; los hallazgos de una revisión ajena van a `auditorias.md`; lo que **puede** salir mal va a [`riesgos.md`](../../calidad/riesgos.md) y no a los CSV.
**Flujo:** detectar → registrar (defecto propio en el CSV, hallazgo ajeno en `auditorias.md`) → clasificar (severidad) → corregir con un commit que lo referencie → verificar (prueba o revisión) → cerrar. Un defecto solo se anota cuando se introdujo **y** se corrigió; los minutos de corrección no se inventan.
**Acciones correctivas pendientes (estado al corte):**
| Origen | Acción | Estado |
|---|---|---|
| Auditorías 3 a 7, D1 | No fusionar sin revisión de la otra integrante | **Abierta** (se repitió en los nueve PR #7 a #15). Acción correctiva y excepción de E1 **no implementadas** (§5.1); protección de `main` **no configurada** (`protected: false`) |
| Auditoría 3, D2 y Auditoría 4, D2 | Actualizar los textos sobre el estado de CI y de la comprobación del oro | **Corregidas en la rama `e1/cierre-documental`** (textos actualizados con las ejecuciones reales; **sin commit ni fusión todavía**) |
| Auditoría 3, R3 | Comprobar en CI que el oro regenerado es igual al versionado | **Cerrada**: `pipeline/verificar_oro.py` (CI en éxito en `main`) |
| Auditoría 3, R4 | Acordar cuándo se versiona un `resumen_<corrida>.json` nuevo | **Abierta** |
| Auditoría 3, R5 | Celdas del agregado de oferta con un solo establecimiento | **Abierta** (RNF-PRI-03) |
| Auditoría 3, O1 | Considerar «conservar la primera copia válida» en una versión futura del contrato | **Abierta**; cambio de contrato, no urgente |
| Auditoría 3, O4 | Una sola fuente de requisitos del laboratorio (`requirements-pronosticos.txt` de B frente a `requirements-lab.txt`) | **Cerrada**: ese archivo se retiró en el commit `18d75eb` de B (verificado en `git`) |
| E0, `riesgos.md` I3 | O1 (95 %) no cumplido | **Abierta**: se mide en [`fiabilidad.md`](fiabilidad.md) |
| Auditoría 5, D2, D3 y D4 | Separador de la fila O7; el mínimo de 2 incidentes no es de la rúbrica; cifras y listas desactualizadas | **Corregidas en la rama `e1/cierre-documental`** (sin commit ni fusión todavía); los recuentos se volvieron a actualizar con las cifras del 2026-11-13 |
| Auditoría 5, O1 y O2 | Estimación exploratoria del MTBF con su intervalo; hacer explícito que los dos extremos del incidente no están corroborados | **Atendidas en la rama** ([`fiabilidad.md`](fiabilidad.md) §3.1 y §4), actualizadas con el corte del 13 de noviembre |
| Auditoría 5, O3 | Resumen versionado y verificable del escaneo de `gitleaks`; que no sea solo local | **Atendida en la rama**: `calidad/evidencia/gitleaks-8.30.1-resumen.json`, [`seguridad.md`](seguridad.md) §3.2 y el trabajo `secretos` de `ci.yml` (§3.4 de `seguridad.md`); su primera ejecución en GitHub llegará con el push |
| Auditoría 5, O4 | Regenerar `fiabilidad_e1.json` antes de la etiqueta `e1` | **Parcial**: se regeneró el 2026-11-13 con la captura de las 20:28 UTC; **abierta** hasta etiquetar, por si llega otra captura ([`fiabilidad.md`](fiabilidad.md) §6) |
| **CI de `main` en rojo** (hallazgo de la autora; Auditorías 5 y 6) | Una prueba del tablero, `test_no_hay_secretos_ni_archivos_temporales_en_el_tablero`, fallaba cuando existía `__pycache__` en `tablero/`; en CI se crea al importar el módulo. Las 3 ejecuciones fallidas son del commit `9489dc5` (ejecución de `main`: 43525789614) | **Cerrada en `main`**: B corrigió la prueba en `eb8f606` (fusionado en `ac9c88d`, PR #15); la ejecución 43548657495 de `main` terminó en **éxito**. La Auditoría 7 verificó la corrección (V1, V2) |
| Auditoría 7, D2 | La URL pública del tablero no sirve la versión integrada | **Cerrada**: la titular reconfiguró el despliegue desde `main`; lectura del 2026-11-14 04:25 UTC con la versión integrada |
| Auditoría 7, D3 | Las pruebas de la aplicación del tablero se omitían en CI | **Corregida en la rama**: `ci.yml` instala `tablero/requirements.txt`, fija `TDL_EXIGIR_TABLERO=1` y la caché lo cubre; `tests/test_ci_workflow.py` lo comprueba. Primera ejecución en GitHub: con el push |
| Auditoría 7, O1 | `.env.example` marcado como archivo no publicable | **Corregida en la rama** (la plantilla se permite solo sin valores reales; `.env` y similares siguen rechazados) |
| Este plan, seguridad | `gitleaks` en CI y auditoría de dependencias transitivas del tablero | **Implementadas en la rama** (`ci.yml`); verificadas localmente (control positivo, hash de la release, `pip-audit` del cierre de 34 paquetes); **primera ejecución en GitHub: con el push** |
| Este plan, seguridad | Acciones fijadas por SHA, archivo de bloqueo con hashes del tablero, `persist-credentials: false`, cobertura con piso de 75 %, copia adicional del bronce con manifiesto y restauración probada | **Implementados y comprobados en local** (2026-11-14); su ejecución en GitHub llegará con el push ([`seguridad.md`](seguridad.md) §4 a §6) |
| Este plan, seguridad | Protección de `main`, hashes para las otras tres listas de dependencias, copia del bronce fuera del equipo | **Abiertas** ([`seguridad.md`](seguridad.md) §7) |
| Fiabilidad (rúbrica de Calidad, 25 pts) | Completar la bitácora con historia real de Actions | **No hay datos recuperables:** las 3 ejecuciones más antiguas de la bitácora ya no existen en la API (404), los registros dan 403 y el flujo se creó el 2026-11-09; se conserva la limitación ([`fiabilidad.md`](fiabilidad.md) §4.2) |

## 7. Criterios para aceptar o rechazar una entrega
**Se acepta** (pasa a la etiqueta `e<n>`) solo si **todo** lo siguiente es cierto y está enlazado a evidencia:
1. `main` en el commit a etiquetar tiene `ci.yml` en **éxito**: `ruff`, `pytest` (sin fallos; las omitidas listadas con motivo; las del tablero **no** se omiten), `pipeline.ejecutar`, `pipeline.verificar_oro`, `pipeline.verificar_e0`, la auditoría de dependencias y `gitleaks`.
2. `python -m pipeline.verificar_e0 --solo historico --solo integridad --solo privacidad --exigir-datos` termina con código 0.
3. Ninguna afirmación de la ficha `ENTREGA.md` carece de evidencia; lo no probado figura como PENDIENTE o PARCIAL.
4. Sin secretos ni datos personales (`gitleaks` con 0 hallazgos abiertos, ejecutado sobre el commit a etiquetar; privacidad satisfactoria).
5. Cada PR integrado tiene su revisión recíproca **registrada**, o la excepción queda declarada en la ficha (**excepción de E1 aún no declarada, §5.1**).
6. Los PSP de ambas integrantes están al día, sin tiempos ni defectos inventados.
7. Los hallazgos **críticos** y **mayores** de las auditorías están corregidos o declarados abiertos con su justificación.
**Se rechaza (no se etiqueta)** si ocurre cualquiera de: CI en rojo en el commit a etiquetar; un secreto en el repositorio; datos personales en el bronce; una cifra de la ficha que contradiga la evidencia; o una verificación presentada como ejecutada que no se ejecutó.
**Estado hoy (no es un dictamen de entrega):** el criterio 1 se cumple en `ac9c88d` (ejecución 43548657495) con el CI anterior; **el CI nuevo (tablero obligatorio, `gitleaks`, auditoría ampliada) no se ha ejecutado en GitHub** y hay que verificarlo al fusionar; el 2 se comprueba con el verificador; el 4 se cumple con las ejecuciones locales de `gitleaks` y `pip-audit` y queda automatizado en el CI nuevo, pero hay que repetir el escaneo sobre el commit a etiquetar; el 5 **no se cumple** para los PR #7 a #15 y se acepta solo con la excepción de §5.1, que **aún requiere la conformidad de ambas integrantes**; el 3 depende de la ficha `docs/E1/ENTREGA.md`, que está en esta rama; y los criterios 6 y 7 **no se evaluaron aquí**: hay que revisarlos al momento de etiquetar (el tiempo del cierre documental sigue sin estimar en el PSP de A y los hallazgos abiertos de §6 cuentan).

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
- **Protección de `main`: NO configurada.** La API pública (2026-11-13 19:14 UTC) devuelve `protected: false` y ninguna regla activa; **no está implementada** y requiere permisos de administración (§5.1).

## 10. Riesgos de calidad
Los riesgos generales viven en [`riesgos.md`](../../calidad/riesgos.md) (R1 a R8 e I1 a I4). Los **nuevos** de E1, con su mitigación:
| ID | Riesgo | Mitigación | Estado |
|---|---|---|---|
| Q1 | Fusionar sin revisión repite la situación de E0 y deja pasar defectos | Acción correctiva y excepción de §5.1 (**no implementadas**); protección de `main` (**no configurada**) | **Materializado** (PR #7 a #15; el #14 dejó `main` en rojo) |
| Q2 | La medición de fiabilidad no alcanza los 7 días que pide la rúbrica, y con un solo incidente no cumple el criterio interno de 2 incidentes para el MTBF (regla metodológica de este plan, **no** de la rúbrica) | Declararlo; ofrecer solo la estimación exploratoria con su intervalo; actualizar con `pipeline.fiabilidad`; no suponer valores | Abierto |
| Q3 | Un secreto futuro que nadie detecte porque `gitleaks` no corre en cada cambio, o uno fuera de su alcance (registros y secretos de GitHub) | `gitleaks` en CI (trabajo `secretos`, [`seguridad.md`](seguridad.md) §3.4); rotar el token si hay duda | Mitigado en la rama; **primera ejecución en GitHub: con el push**. Lo que está fuera de su alcance sigue sin cubrirse |
| Q4 | El único respaldo del bronce es GitHub | Copia adicional con manifiesto SHA-256 y restauración probada ([`seguridad.md`](seguridad.md) §6); falta copiarla fuera del equipo | Mitigado; **la copia no es independiente todavía** |
| Q5 | Plazo: E1 vence el 2026-11-13 y la etiqueta `e1` aún no existe | Declarar lo pendiente en la ficha | Abierto |
| Q6 | Equipo de dos personas y apoyo de una herramienta de IA: la independencia de la revisión es limitada | Declararlo en cada auditoría; ejecutar y reproducir, no solo leer | Aceptado |
| Q7 | El agregado de oferta DENUE no protege las celdas de un solo establecimiento | No publicarlo en el tablero sin agrupar celdas < 3 | Abierto |
| Q8 | Un cambio sin revisión rompe el CI de `main` y la rúbrica pide que «un cambio que rompe algo no entra» | Revisión previa y protección de `main` (**no implementadas**); `main` ya está en verde (`eb8f606`) | **Materializado** (`06452fd`); corregido en `eb8f606` |
| Q9 | La URL pública del tablero muestra una versión distinta de la integrada | Comprobar la rama configurada y repetir la lectura (Auditoría 7, D2) | **Materializado y resuelto** (2026-11-14 04:25 UTC); repetir la lectura tras la integración definitiva |

## 11. Qué está implementado y qué falta (resumen)
| Implementado (con evidencia) | Parcial | Pendiente |
|---|---|---|
| Puerta de calidad y cuarentena, pipeline determinista, oro validado con jerarquías conceptuales, discretización supervisada comparada, copia del bronce con manifiesto, bloqueo con hashes del tablero, acciones por SHA, CI en `main` (en éxito en `ac9c88d`), `verificar_oro`, `pip-audit` (con las transitivas del tablero), permisos mínimos, restauración del bronce, registro de defectos y de tiempo, lista de auditoría, medición de fiabilidad (lo calculable), `gitleaks` local, pruebas del tablero obligatorias en CI (en la rama), tablero publicado (URL pública verificada) | Revisión recíproca previa a fusionar (incumplida en #7 a #15; excepción no declarada); revisión del PSP, medición de O1/MTBF/A (faltan datos), el CI nuevo (`secretos`, tablero obligatorio) **sin ejecutar aún en GitHub** | Protección de `main`, etiqueta `e1`, copia del bronce fuera del equipo, hashes para las otras tres listas de dependencias |
