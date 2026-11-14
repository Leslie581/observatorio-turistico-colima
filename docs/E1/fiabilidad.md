# Fiabilidad y disponibilidad de la captura programada (E1)

Rama `e1/leslie-calidad` · corte **2026-11-13** · Responsable: Leslie Valadez Macías (integrante A).
Requisito (PDF, pág. 16): «Fiabilidad y disponibilidad medidas, no supuestas: con la bitácora de su captura programada, calculen tasa de éxito por ejecución, MTBF, MTTR y disponibilidad. Compárenlas contra el objetivo que fijaron en E0». Rúbrica (pág. 25): «MTBF, MTTR y disponibilidad medidos con **7 días de bitácoras**» frente a «valores supuestos».

## Qué es cada magnitud (no son intercambiables)
| Magnitud | Qué mide | Valor al corte | Estado |
|---|---|---|---|
| **Tasa de éxito de ejecuciones** | Fracción de ejecuciones válidas que terminaron bien: éxitos ÷ (éxitos + fallos) | **6/7 = 85.7 %** (n = 7) | **Medida** |
| **MTTR observado** | Tiempo que tardó en recuperarse el único incidente cerrado | **268 s**, basado en **un único incidente** (n = 1) | **Medida, pero no es una estimación estable** |
| **MTBF** | Tiempo medio **entre fallas**. El mínimo de 2 incidentes es un **criterio metodológico interno** del proyecto, no un requisito de la rúbrica (que pide 7 días de bitácora) | — | **No estimable con ese criterio.** Estimación **exploratoria**: 91.7 h, IC 90 %: 19.3 h a 74.5 días (§3.1) |
| **Disponibilidad operativa** `A = MTBF/(MTBF+MTTR)` | Fracción del tiempo en que el servicio está operativo | — | **No estimable con ese criterio.** Estimación **exploratoria**: 0.9992 (0.9962 con la cota inferior), igual a la disponibilidad observada por tiempo (§3.1) |
La tasa de éxito **no es** la disponibilidad operativa: cuenta ejecuciones, no tiempo. Tampoco lo es la cobertura diaria (5 de 5 días con captura exitosa, §3), que es solo descriptiva. El objetivo O1 (95 %) **no se cumple en lo observado** (85.7 %) y **no es evaluable como se definió** (ventana de 7 días; hay 3.83). La única estimación adicional es la **exploratoria** de §3.1, con su intervalo y sus supuestos. No se agregaron incidentes ni se extendió la ventana para mejorar ninguna cifra, y **no se sustituyeron por valores supuestos** las magnitudes no estimables.

## 1. Fuente y herramienta
- **Fuente única:** [`calidad/bitacora_capturas.jsonl`](../../calidad/bitacora_capturas.jsonl), una línea por ejecución, escrita por el extractor (no se edita a mano).
- **Herramienta:** [`pipeline/fiabilidad.py`](../../pipeline/fiabilidad.py). Solo lee la bitácora (sin red) y es determinista. Pruebas: [`tests/test_fiabilidad.py`](../../tests/test_fiabilidad.py) (22: casos sintéticos declarados y un corte fijo de los 8 primeros registros reales).
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
| MTBF | (tiempo observado − tiempo de reparación total) ÷ número de incidentes. **Solo se calcula con ≥ 2 incidentes (criterio metodológico INTERNO del proyecto, no de la rúbrica)**: con uno no hay un intervalo entre fallas. Con un incidente, véase la estimación exploratoria de §3.1 |
| Disponibilidad A | MTBF ÷ (MTBF + MTTR) (fórmula del PDF). Solo existe si existen MTBF y MTTR |
| Cobertura diaria (descriptiva, **no es A**) | días locales con al menos una captura exitosa ÷ días locales con ejecuciones |
Husos: las fechas locales son de la Ciudad de México (UTC−6 fijo); los instantes se dan en UTC.

## 3. Resultados al corte (bitácora del 2026-11-10 00:39 UTC al 2026-11-13 20:28 UTC)
Corte: la captura programada del 2026-11-13 (20:28 UTC), commit `7a45356`. **Si llegan más capturas, estas cifras quedan desactualizadas** (véase §6).
| Medida | Resultado | Estado |
|---|---|---|
| Registros en la bitácora | 9 (6 éxitos, 1 fallo, 2 omitidas por duplicado) | |
| Ejecuciones válidas | 7 | |
| **Tasa de éxito** | **6/7 = 85.71 %**; objetivo O1: 95 % | **No cumple en lo observado.** No evaluable como se definió (ventana de 7 días) |
| Ejecuciones `schedule` | 4 de 4 exitosas (10, 11, 12 y 13 de noviembre) | Descriptivo (n = 4) |
| Ventana cubierta | **3.83 días** (rúbrica: 7) | **No cumple los 7 días** |
| Incidentes | 1, cerrado: 2026-11-10 00:39:33 UTC, causa registrada «falta de `INEGI_TOKEN`», 1 fallo | Corrido a mano (`workflow_dispatch`) en la puesta en marcha |
| **MTTR** | **268 s** (4 min 28 s), n = 1 | Calculado; una observación, **no una estimación estable** |
| **MTBF** | **No estimable con el criterio interno** (1 incidente; el mínimo de 2 es una regla del proyecto) | Tiempo sin fallas desde la recuperación: 330,295 s (3.82 días), **dato censurado**. Estimación exploratoria en §3.1 |
| **Disponibilidad A** | **No estimable con el criterio interno** (falta el MTBF) | Estimación exploratoria 0.9992 en §3.1; **no sustituye** a la tasa de éxito |
| Cobertura diaria (descriptiva) | 5 de 5 días locales con captura exitosa | No es la disponibilidad A |
| Puntualidad de `schedule` | Retraso de 7 h 11 min, 6 h 54 min, 7 h 31 min y 7 h 11 min respecto de las 13:17 UTC programadas | Observación (GitHub retrasa las ejecuciones programadas); no afecta el éxito de la captura |
**Cómo leer el 85.7 %.** Es la cifra honesta del periodo: incluye el único fallo, que ocurrió en el primer intento manual (el token aún no estaba configurado) y se corrigió 4 min 28 s después. No se excluye para mejorar el número. Con 7 ejecuciones, **un solo fallo mueve la tasa más de 14 puntos**: por eso no debe leerse como una propiedad estable del sistema. Las 4 ejecuciones programadas fueron 4 de 4, pero eso es n = 4.

### 3.1 Estimación exploratoria del MTBF con un solo incidente (propuesta de la integrante B, verificada)
La integrante B propuso (Auditoría 5, O1) estimar **MTBF = 68.1 h** y **A = 0.9989** con el único incidente y la bitácora al 12 de noviembre; la tabla siguiente usa el corte actual (13 de noviembre, 20:28 UTC), con el que las cifras son otras (el cálculo es el mismo). **El cálculo es matemáticamente correcto** y se reproduce con una implementación propia en Python puro y con `scipy` como referencia independiente. Se presenta **solo como estimación exploratoria, con su incertidumbre y sus supuestos**; no sustituye a la tasa de éxito ni cambia el criterio interno de §2.
| Elemento | Verificación |
|---|---|
| **Fórmula** | MTBF = T ÷ r (estimador de máxima verosimilitud con tasa de fallos constante, observación truncada por tiempo). `A = MTBF ÷ (MTBF + MTTR)`. Intervalo exacto de Epstein: `[2T / χ²(1−α/2; 2r+2) , 2T / χ²(α/2; 2r)]` |
| **Ventana real de observación** | **330,563 s (3.8259 días)**: del 2026-11-10 00:39:33 UTC (inicio del fallo) al 2026-11-13 20:28:56 UTC (fin de la última captura). Es la ventana de la bitácora; **no se extendió** |
| **Tiempo operativo** | T = 330,563 − 268 = **330,295 s = 91.749 h**; r = 1 incidente |
| **MTBF (estimación puntual)** | **91.749 h** (≈ 3.82 días) |
| **Intervalo de confianza del 90 %** | **19.34 h a 1,788.7 h (74.5 días)**: χ²(0.95; 4) = 9.4877 y χ²(0.05; 2) = 0.10259. Es **muy ancho**: con un solo fallo, el MTBF verdadero podría ser desde menos de un día hasta unos dos meses y medio |
| **Disponibilidad A** | **0.99919** (punto); **0.99617** con la cota inferior del MTBF y 0.99996 con la superior |
| **Disponibilidad observada por tiempo** | 1 − 268 ÷ 330,563 = **0.99919**. **Es idéntica a A puntual**: con r = 1, `T/(T + MTTR) = (W − R)/W` es una identidad algebraica. El estimador **no aporta información nueva**; solo agrega el intervalo |
| **Diferencia con la tasa de éxito (85.7 %)** | Son magnitudes distintas, **no se promedian ni se sustituyen**: la tasa cuenta **ejecuciones** (6 de 7; IC exacto de Clopper-Pearson del 95 %: **42.1 % a 99.6 %**, que **incluye** el 95 % del objetivo O1, es decir, con n = 7 no se puede ni confirmar ni descartar), y A mide **tiempo** (el servicio estuvo «caído» 268 s de 330,563 s) |
**Supuestos y por qué hay que leerlo con cautela:**
1. **Tasa de fallos constante.** El único fallo fue de **configuración** (falta de `INEGI_TOKEN`) en el **primer intento manual**, no un fallo aleatorio en régimen normal; su causa ya se corrigió. Un modelo de fallos aleatorios no describe bien ese evento.
2. **La captura es un trabajo diario, no un servicio continuo.** Solo puede fallar cuando se ejecuta; medir la exposición en horas (92 h) es una convención. En ejecuciones, el mismo dato es «1 fallo en 7 ejecuciones» (tasa de fallo 14.3 %; IC 95 %: 0.4 % a 57.9 %).
3. **El 268 s de reparación es optimista para el régimen normal.** Fue un reintento manual durante la puesta en marcha. Si falla una ejecución programada, la siguiente oportunidad es la del día siguiente (≈ 24 h); **solo como ilustración**, con ese MTTR y el mismo MTBF, A sería 91.7 ÷ (91.7 + 24) ≈ **0.79**: la cifra de 0.9992 depende por completo del reintento inmediato.
4. **Un solo fallo da un intervalo enorme**: no es una estimación estable.
5. **Los dos extremos del incidente no están corroborados por GitHub** (§4): el fallo y el éxito que lo cierra son dos de los tres registros que la API pública no reconoce.
**Reproducir:** `python -m pipeline.fiabilidad` (bloque `estimacion_exploratoria` y `tasa_exito.intervalo_95_clopper_pearson`). Pruebas en `tests/test_fiabilidad.py`: cuantiles de la ji cuadrada contra valores de tabla y contra `scipy`, casos límite y el corte real fijo.

## 4. Cotejo con GitHub Actions (consulta a la API pública, 2026-11-13)
| Concepto | Resultado |
|---|---|
| Ejecuciones de `captura-diaria.yml` listadas por la API | 6 (todas con conclusión `success`) |
| Esas 6 ¿están en la bitácora? | **Sí, 6 de 6** (`run_id` 42733220215, 42733335021, 42895566130, 43094099548, 43303888985 y la del 13 de noviembre, 43501875036) |
| Registros de la bitácora que la API **no** reconoce | **3 de 9** (`run_id` 42729922838, 42730477358 y 42732765759: respuesta 404, repetida el 2026-11-13). Son el fallo, el éxito que lo cierra y una omitida por duplicado |
| **Los dos extremos del único incidente** | **El fallo y el éxito que lo cierra están entre esos 3**: el incidente, y por tanto el MTTR de 268 s, **proceden solo de registros locales que la API pública de GitHub no corrobora** |
| Resultado usando **solo** los registros corroborados por la API | 5 ejecuciones válidas, **5 éxitos y 0 fallos** (tasa 5/5): no habría incidente y el MTTR no se podría calcular. No se propone cambiar la cifra (la bitácora es la fuente definida), solo hacer explícita esta dependencia |
| Ejecuciones de `ci.yml` (otro flujo, no es la captura) | **25** al corte del 2026-11-14 03:14 UTC: **21 en éxito, 1 cancelada** por la política de concurrencia y **3 fallidas**. Las 3 fallidas son del commit `9489dc5` del tablero (push de su rama, pull request y push de `main` en `06452fd`): una prueba del tablero dependía de `__pycache__`. La corrigió `eb8f606` (PR #15) y `main` (`ac9c88d`, ejecución 43548657495) terminó en **éxito**. Los registros de Actions no se leyeron (§4 de `pipeline.md`); la causa se reprodujo en un clon limpio |
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
| 43501875036 | `schedule` | 11-13 20:28:29 | 20:28:53 | 24 s | 11-13 14:28:53 | 2026-11-13 | **7 h 11 min 29 s** |
- **El retraso del `schedule` es el mismo con cualquiera de las dos fuentes** (la bitácora da 431.4, 414.4, 451.5 y 431.9 min; GitHub, 7 h 11 min, 6 h 54 min, 7 h 31 min y 7 h 11 min). GitHub puede retrasar las ejecuciones programadas; aquí las cuatro corrieron unas 7 horas después de las 07:17 locales (a las 14:11 a 14:48 locales) y **ninguna se omitió**.
- **Fallo inicial:** `inicio_utc` 2026-11-10 00:39:33 = **2026-11-09 18:39:33** en la Ciudad de México, por eso su `fecha_local` es 2026-11-09. Ese registro y las ejecuciones 42730477358 y 42732765759 son los 3 que la API de Actions no reconoce (§4), así que **no tienen marca de GitHub con la que compararlos**.
- **Ventana en hora local:** del 2026-11-09 18:39:33 al 2026-11-13 14:28:56 (3.83 días); en UTC, del 2026-11-10 00:39:33 al 2026-11-13 20:28:56. Los «5 días locales con captura» (9 al 13 de noviembre) incluyen la tarde del 9, que corresponde a las ejecuciones manuales de la noche UTC del 10.
- **Consecuencia para las mediciones:** los retrasos no cuentan como fallos ni como tiempo de reparación. El MTTR (268 s) usa `inicio_utc` del fallo y `fin_utc` del éxito, ambos de la bitácora (misma fuente y mismo reloj).

### 4.2 ¿Se puede recuperar más historia real de Actions para completar los 7 días? (consulta del 2026-11-14)
Se intentó, sin inventar nada, por todas las vías públicas:
| Vía | Resultado |
|---|---|
| API de ejecuciones (`/actions/workflows/.../runs` y `/actions/runs`) | **6 ejecuciones** de `captura-diaria.yml` (la más antigua, 2026-11-10 01:05 UTC) y 25 de `ci.yml`; `total_count` del repositorio: 32. Las 6 están en la bitácora |
| Ejecuciones de la bitácora que la API ya no muestra | `42729922838`, `42730477358` y `42732765759` (2026-11-10 00:39, 00:43 y 01:02 UTC): la API devuelve **404**. La bitácora las conserva porque cada ejecución la escribe al terminar; no hay una segunda fuente que las corrobore |
| Fecha de creación | El repositorio se creó el 2026-11-09 15:16 UTC y el flujo `captura-diaria-denue`, el 2026-11-09 19:10 UTC: **antes de esas fechas no existe ninguna captura programada**, así que los días 6, 7 y 8 de noviembre de la ventana del PDF no se pueden recuperar |
| Registros (logs) de las ejecuciones | **403** sin sesión: no se pueden leer sin una cuenta con permisos |
| Artefactos | 6 artefactos sin expirar (de las 6 ejecuciones visibles), pero su descarga exige sesión; no se descargaron |
| Historial de Git | Cada captura del bot tiene su commit (`captura DENUE <id> [skip ci]`): confirma que las ejecuciones ocurrieron y coincide con la bitácora, **pero no aporta nada que la bitácora no tenga** |
**Conclusión:** no hay datos reales adicionales y **no se agregó, alteró ni infirió ninguna ejecución, incidente ni tiempo de reparación**. La limitación se conserva: la bitácora cubre 3.83 días (2026-11-10 00:39 UTC a 2026-11-13 20:28 UTC), MTBF y disponibilidad siguen siendo estimaciones exploratorias con un solo incidente, y la ventana del PDF (6 al 13 de noviembre) **ya no se puede completar** hacia atrás. Solo ejecuciones futuras la alargarían (la captura diaria sigue activa; con una captura cada ~24 h se llegaría a 7 días de cobertura hacia el 2026-11-17, sin que eso cambie lo anterior).

## 5. Limitaciones y lo que falta
1. **Ventana insuficiente.** La rúbrica pide 7 días de bitácora y hay 3.83 (corte del 13 de noviembre, 20:28 UTC). La captura programada empezó a funcionar el 2026-11-10 (UTC), no el 6 de noviembre. Los 7 días se alcanzarían hacia el **2026-11-17**, después del plazo de E1.
2. **Un solo incidente.** Con el criterio interno (≥ 2 incidentes) el MTBF y la disponibilidad `A` quedan sin estimar; la estimación exploratoria de §3.1 tiene un intervalo de 19.3 h a 74.5 días. Si no ocurren más fallas, **eso no demuestra un MTBF alto**; solo que no hay datos para estimarlo.
3. **El MTTR es una observación** (n = 1), de una falla de configuración durante la puesta en marcha, no de una caída en régimen normal, y **sus dos extremos no están corroborados por la API de GitHub** (§4).
4. **Granularidad diaria.** La captura es un trabajo por lotes (una vez al día); «disponibilidad» aquí es la de ese trabajo, no la de un servicio que se consulta continuamente (el tablero aún no está publicado).
5. **La tasa de éxito no mide la calidad de lo capturado**: eso lo cubren O2 y O3 (integridad, completitud y privacidad), que se verifican por separado.

## 6. Procedimiento para actualizar la medición
1. Después de nuevas ejecuciones (el bot agrega líneas a la bitácora): `python -m pipeline.fiabilidad --escribir`.
2. Con ≥ 7 días de bitácora, el informe marca `cumple_dias_requeridos: true` y O1 pasa a ser evaluable en su ventana.
3. Con ≥ 2 incidentes, el informe calcula el MTBF y `A` con las fórmulas de la sección 2; hasta entonces dice «no estimable» y solo ofrece la estimación exploratoria de §3.1.
4. Repetir el cotejo con la API de Actions (sección 4) y registrar los `run_id` que no se reconozcan.
5. **Antes de la etiqueta `e1` hay que volver a regenerar `calidad/fiabilidad_e1.json`**: se regeneró el 2026-11-13 con la captura de las 20:28 UTC (corte de §3); si llega otra, el informe versionado queda desactualizado; lleva el SHA-256 de la bitácora para detectarlo, pero CI no lo comprueba. Después de regenerarlo, actualizar las cifras de este documento.
6. Si una cifra cambia respecto de este documento, actualizar este documento y [`objetivos.md`](../../calidad/objetivos.md) (O1) con la fecha del corte; **no cambiar la fórmula ni el umbral** (regla de `objetivos.md`).

## 7. Prueba de que el resultado se obtiene del dato y no de una suposición
- `tests/test_fiabilidad.py` comprueba con bitácoras armadas a mano (declaradas sintéticas) que: sin incidentes no hay MTTR ni MTBF; un incidente da MTTR pero no MTBF; dos incidentes sí dan MTBF y `A` con la fórmula; las fallas consecutivas son un solo incidente; un incidente sin recuperación queda abierto; las omitidas no cuentan; la ventana de 7 días se declara cumplida o no; y la entrada no se modifica.
- La prueba final recalcula sobre los **8 primeros registros reales** y fija el resultado del corte **del 12 de noviembre** (6 válidas, 83.33 % con su intervalo de Clopper-Pearson, MTTR 268 s, 2.84 días y la estimación exploratoria de entonces: 68.076 h, IC 90 % 14.35 h a 1,327.2 h, A 0.99891). Las cifras de §3 son las del informe regenerado con la bitácora completa (`calidad/fiabilidad_e1.json`).
