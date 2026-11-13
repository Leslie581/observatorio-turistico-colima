# Fiabilidad y disponibilidad de la captura programada (E1)

Rama `e1/leslie-calidad` · corte **2026-11-13** · Responsable: Leslie Valadez Macías (integrante A).
Requisito (PDF, pág. 16): «Fiabilidad y disponibilidad medidas, no supuestas: con la bitácora de su captura programada, calculen tasa de éxito por ejecución, MTBF, MTTR y disponibilidad. Compárenlas contra el objetivo que fijaron en E0». Rúbrica (pág. 25): «MTBF, MTTR y disponibilidad medidos con **7 días de bitácoras**» frente a «valores supuestos».

## Qué es cada magnitud (no son intercambiables)
| Magnitud | Qué mide | Valor al corte | Estado |
|---|---|---|---|
| **Tasa de éxito de ejecuciones** | Fracción de ejecuciones válidas que terminaron bien: éxitos ÷ (éxitos + fallos) | **5/6 = 83.3 %** (n = 6) | **Medida** |
| **MTTR observado** | Tiempo que tardó en recuperarse el único incidente cerrado | **268 s**, basado en **un único incidente** (n = 1) | **Medida, pero no es una estimación estable** |
| **MTBF** | Tiempo medio **entre fallas** (necesita al menos 2 incidentes) | — | **No estimable** |
| **Disponibilidad operativa** `A = MTBF/(MTBF+MTTR)` | Fracción del tiempo en que el servicio está operativo | — | **No estimable** (falta el MTBF) |
La tasa de éxito **no es** la disponibilidad operativa: cuenta ejecuciones, no tiempo. Tampoco lo es la cobertura diaria (4 de 4 días con captura exitosa, §3), que es solo descriptiva. El objetivo O1 (95 %) **no se cumple en lo observado** (83.3 %) y **no es evaluable como se definió** (ventana de 7 días; hay 2.84). No se agregaron incidentes ni se extendió la ventana para mejorar ninguna cifra, y **no se sustituyeron por valores supuestos** las magnitudes no estimables.

## 1. Fuente y herramienta
- **Fuente única:** [`calidad/bitacora_capturas.jsonl`](../../calidad/bitacora_capturas.jsonl), una línea por ejecución, escrita por el extractor (no se edita a mano).
- **Herramienta:** [`pipeline/fiabilidad.py`](../../pipeline/fiabilidad.py). Solo lee la bitácora (sin red) y es determinista. Pruebas: [`tests/test_fiabilidad.py`](../../tests/test_fiabilidad.py) (12: casos sintéticos declarados y un corte fijo de los 8 primeros registros reales).
- **Reproducir:** `python -m pipeline.fiabilidad` (imprime) o `python -m pipeline.fiabilidad --escribir` (guarda [`calidad/fiabilidad_e1.json`](../../calidad/fiabilidad_e1.json)). El informe incluye el SHA-256 de la bitácora usada, para ver si quedó desactualizado.
- **Una sola definición de tasa de éxito en el proyecto:** una prueba comprueba que coincide con la de `verificar_e0 --solo disponibilidad` (objetivo O1).

## 2. Definiciones (fijadas antes de calcular; no se ajustan después de ver los resultados)
| Magnitud | Definición |
|---|---|
| Ejecución válida | `resultado` = `exito` o `fallo`. Las `omitida_duplicada` (ya existía la captura del día) **no cuentan** (criterio de O1). |
| Tasa de éxito | éxitos ÷ (éxitos + fallos) |
| Incidente | racha de ejecuciones `fallo` consecutivas; termina en el siguiente `exito`. Sin éxito posterior queda **abierto** |
| Tiempo de reparación | `fin_utc` del primer éxito posterior − `inicio_utc` del primer fallo de la racha |
| MTTR | promedio de los tiempos de reparación de los incidentes **cerrados** |
| MTBF | (tiempo observado − tiempo de reparación total) ÷ número de incidentes. **Solo se calcula con ≥ 2 incidentes**: con uno no hay un intervalo entre fallas y el número sería una cota, no una estimación |
| Disponibilidad A | MTBF ÷ (MTBF + MTTR) (fórmula del PDF). Solo existe si existen MTBF y MTTR |
| Cobertura diaria (descriptiva, **no es A**) | días locales con al menos una captura exitosa ÷ días locales con ejecuciones |
Husos: las fechas locales son de la Ciudad de México (UTC−6 fijo); los instantes se dan en UTC.

## 3. Resultados al corte (bitácora del 2026-11-10 00:39 UTC al 2026-11-12 20:48 UTC)
| Medida | Resultado | Estado |
|---|---|---|
| Registros en la bitácora | 8 (5 éxitos, 1 fallo, 2 omitidas por duplicado) | |
| Ejecuciones válidas | 6 | |
| **Tasa de éxito** | **5/6 = 83.33 %**; objetivo O1: 95 % | **No cumple en lo observado.** No evaluable como se definió (ventana de 7 días) |
| Ejecuciones `schedule` | 3 de 3 exitosas (10, 11 y 12 de noviembre) | Descriptivo (n = 3) |
| Ventana cubierta | **2.84 días** (rúbrica: 7) | **No cumple los 7 días** |
| Incidentes | 1, cerrado: 2026-11-10 00:39:33 UTC, causa registrada «falta de `INEGI_TOKEN`», 1 fallo | Corrido a mano (`workflow_dispatch`) en la puesta en marcha |
| **MTTR** | **268 s** (4 min 28 s), n = 1 | Calculado; una observación, **no una estimación estable** |
| **MTBF** | **No estimable**: 1 incidente (se necesitan ≥ 2) | Tiempo sin fallas desde la recuperación: 245,075 s (2.84 días), **dato censurado**: es una cota inferior, no el MTBF |
| **Disponibilidad A** | **No estimable** (falta el MTBF) | No se sustituye por un valor supuesto |
| Cobertura diaria (descriptiva) | 4 de 4 días locales con captura exitosa | No es la disponibilidad A |
| Puntualidad de `schedule` | Retraso de 7 h 11 min, 6 h 54 min y 7 h 31 min respecto de las 13:17 UTC programadas | Observación (GitHub retrasa las ejecuciones programadas); no afecta el éxito de la captura |
**Cómo leer el 83.3 %.** Es la cifra honesta del periodo: incluye el único fallo, que ocurrió en el primer intento manual (el token aún no estaba configurado) y se corrigió 4 min 28 s después. No se excluye para mejorar el número. Con 6 ejecuciones, **un solo fallo mueve la tasa más de 16 puntos**: por eso no debe leerse como una propiedad estable del sistema. Las 3 ejecuciones programadas fueron 3 de 3, pero eso es n = 3.

## 4. Cotejo con GitHub Actions (consulta a la API pública, 2026-11-13)
| Concepto | Resultado |
|---|---|
| Ejecuciones de `captura-diaria.yml` listadas por la API | 5 (todas con conclusión `success`) |
| Esas 5 ¿están en la bitácora? | **Sí, 5 de 5** (`run_id` 42733220215, 42733335021, 42895566130, 43094099548, 43303888985) |
| Registros de la bitácora que la API **no** reconoce | **3 de 8** (`run_id` 42729922838, 42730477358 y 42732765759: respuesta 404). Entre ellos **está el único fallo** |
| Ejecuciones de `ci.yml` (otro flujo, no es la captura) | 9, todas `success` (6 push y 3 pull request, 2026-11-13) |
**Limitación:** el fallo inicial y los otros dos registros no se pudieron cotejar con GitHub. Pudieron borrarse las ejecuciones o haberse corrido en otro contexto; **no se sabe**. La bitácora los registra y se usan tal como están, pero su verificación independiente queda **pendiente**.

### 4.1 Horarios: UTC, hora local y marcas de GitHub (verificado el 2026-11-13)
- **Convenciones.** El cron está en UTC (`17 13 * * *` = 13:17 UTC = **07:17 en la Ciudad de México**, UTC−6 fijo). La bitácora guarda `inicio_utc`/`fin_utc` en UTC y `fecha_local` en hora de la Ciudad de México. La API de GitHub entrega `created_at` en UTC (la interfaz web lo muestra en la zona del navegador).
- **Qué marca cada fuente.** `created_at` de GitHub es el momento en que la ejecución se **creó/encoló**; `inicio_utc` de la bitácora es el momento en que empezó el **paso de captura**, que va **después** de instalar las dependencias y correr las pruebas dentro del mismo trabajo. Por eso la bitácora marca 18 a 30 s **después** que GitHub, siempre.
| `run_id` | Evento | GitHub `created_at` (UTC) | Bitácora `inicio_utc` | Diferencia | Hora local (CDMX) | `fecha_local` | Retraso frente a 13:17 UTC (desde `created_at`) |
|---|---|---|---|---|---|---|---|
| 42733220215 | manual (omitida por duplicado) | 11-10 01:05:32 | 01:06:02 | 30 s | 11-09 19:06:02 | 2026-11-09 | — |
| 42733335021 | manual | 11-10 01:06:26 | 01:06:46 | 20 s | 11-09 19:06:46 | 2026-11-09 | — |
| 42895566130 | `schedule` | 11-10 20:28:08 | 20:28:26 | 18 s | 11-10 14:28:26 | 2026-11-10 | **7 h 11 min 08 s** |
| 43094099548 | `schedule` | 11-11 20:11:06 | 20:11:25 | 19 s | 11-11 14:11:25 | 2026-11-11 | **6 h 54 min 06 s** |
| 43303888985 | `schedule` | 11-12 20:48:09 | 20:48:32 | 23 s | 11-12 14:48:32 | 2026-11-12 | **7 h 31 min 09 s** |
- **El retraso del `schedule` es el mismo con cualquiera de las dos fuentes** (la bitácora da 431.4, 414.4 y 451.5 min; GitHub, 7 h 11 min, 6 h 54 min y 7 h 31 min). GitHub puede retrasar las ejecuciones programadas; aquí las tres corrieron unas 7 horas después de las 07:17 locales (a las 14:11 a 14:48 locales) y **ninguna se omitió**.
- **Fallo inicial:** `inicio_utc` 2026-11-10 00:39:33 = **2026-11-09 18:39:33** en la Ciudad de México, por eso su `fecha_local` es 2026-11-09. Ese registro y las ejecuciones 42730477358 y 42732765759 son los 3 que la API de Actions no reconoce (§4), así que **no tienen marca de GitHub con la que compararlos**.
- **Ventana en hora local:** del 2026-11-09 18:39:33 al 2026-11-12 14:48:36 (2.84 días); en UTC, del 2026-11-10 00:39:33 al 2026-11-12 20:48:36. Los «4 días locales con captura» (9 al 12 de noviembre) incluyen la tarde del 9, que corresponde a las ejecuciones manuales de la noche UTC del 10.
- **Consecuencia para las mediciones:** los retrasos no cuentan como fallos ni como tiempo de reparación. El MTTR (268 s) usa `inicio_utc` del fallo y `fin_utc` del éxito, ambos de la bitácora (misma fuente y mismo reloj).

## 5. Limitaciones y lo que falta
1. **Ventana insuficiente.** La rúbrica pide 7 días de bitácora y hay 2.84. La captura programada empezó a funcionar el 2026-11-10 (UTC), no el 6 de noviembre. Con la ejecución del 13 de noviembre habrá ~3.9 días; los 7 días se alcanzarían hacia el **2026-11-17**, después del plazo de E1.
2. **Un solo incidente.** Sin al menos dos fallas no existe un intervalo entre fallas: el MTBF y la disponibilidad `A` quedan sin estimar. Si no ocurren más fallas, **eso no demuestra un MTBF alto**; solo que no hay datos para estimarlo.
3. **El MTTR es una observación** (n = 1), de una falla de configuración durante la puesta en marcha, no de una caída en régimen normal.
4. **Granularidad diaria.** La captura es un trabajo por lotes (una vez al día); «disponibilidad» aquí es la de ese trabajo, no la de un servicio que se consulta continuamente (el tablero aún no está publicado).
5. **La tasa de éxito no mide la calidad de lo capturado**: eso lo cubren O2 y O3 (integridad, completitud y privacidad), que se verifican por separado.

## 6. Procedimiento para actualizar la medición
1. Después de nuevas ejecuciones (el bot agrega líneas a la bitácora): `python -m pipeline.fiabilidad --escribir`.
2. Con ≥ 7 días de bitácora, el informe marca `cumple_dias_requeridos: true` y O1 pasa a ser evaluable en su ventana.
3. Con ≥ 2 incidentes, el informe calcula el MTBF y `A` con las fórmulas de la sección 2; hasta entonces dice «no estimable».
4. Repetir el cotejo con la API de Actions (sección 4) y registrar los `run_id` que no se reconozcan.
5. Si una cifra cambia respecto de este documento, actualizar este documento y [`objetivos.md`](../../calidad/objetivos.md) (O1) con la fecha del corte; **no cambiar la fórmula ni el umbral** (regla de `objetivos.md`).

## 7. Prueba de que el resultado se obtiene del dato y no de una suposición
- `tests/test_fiabilidad.py` comprueba con bitácoras armadas a mano (declaradas sintéticas) que: sin incidentes no hay MTTR ni MTBF; un incidente da MTTR pero no MTBF; dos incidentes sí dan MTBF y `A` con la fórmula; las fallas consecutivas son un solo incidente; un incidente sin recuperación queda abierto; las omitidas no cuentan; la ventana de 7 días se declara cumplida o no; y la entrada no se modifica.
- La prueba final recalcula sobre los **8 primeros registros reales** y fija el resultado de este documento (6 válidas, 83.33 %, MTTR 268 s, 2.84 días).
