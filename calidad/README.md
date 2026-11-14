# Calidad: registros PSP, objetivos y bitácora de capturas

| Archivo | Qué es | Quién lo llena |
|---|---|---|
| `defectos-integrante-a.csv`, `defectos-integrante-b.csv` | Registro **individual** de defectos (formato del Kit TDL) | Cada integrante, solo el suyo |
| `tiempo-integrante-a.csv`, `tiempo-integrante-b.csv` | Registro **individual** de tiempo (formato del Kit TDL) | Cada integrante, solo el suyo |
| [`objetivos.md`](objetivos.md) | Tres objetivos de calidad medibles | Equipo |
| [`fiabilidad_e1.json`](fiabilidad_e1.json) | Informe de fiabilidad calculado desde la bitácora (`python -m pipeline.fiabilidad --escribir`); método y límites en [`docs/E1/fiabilidad.md`](../docs/E1/fiabilidad.md) | Automática (la regenera quien mide) |
| `bitacora_capturas.jsonl` | Una línea por ejecución de la captura (la escribe el extractor; no editar a mano). Aparece con la primera ejecución real. | Automática |
| `revision_calidad.md` | Responsable de revisión por entrega y lista de comprobación de E0 | Equipo |
| [`auditorias.md`](auditorias.md), [`lista_verificacion_auditoria.md`](lista_verificacion_auditoria.md) | Proceso y registro de la revisión cruzada; lista reutilizable | Quien audita |
| [`riesgos.md`](riesgos.md) | Riesgos pendientes (distintos de defectos) | Equipo |

**Estado de la entrega E1 (cerrada; etiqueta `e1`):** A: E0 750 min + E1 1,380 min = **2,130 min** (estimaciones retrospectivas; 480 min de E0 son del prototipo, etiquetados `[PROTOTIPO]`) y 22 defectos entregados (28 con los 6 documentales agregados el 2026-11-14); B: E0 633 min + E1 118 min en 23 intervalos con inicio y fin, y 14 defectos. Sin horarios inventados. **No se editan** las filas de la entrega.

**Trabajo posterior a la entrega (desde 2026-11-13/14):** se registra aparte en `tiempo-posentrega-integrante-a.csv` (mismo formato) para no alterar lo entregado; se llena **desde el inicio de cada bloque** con `inicio`, `fin` e `interrupcion_min` reales. Para la retrospectiva PSP de E3 (exactitud de las estimaciones, defectos inyectados y eliminados por fase, rendimiento de revisiones) cada defecto nuevo debe llevar `minutos_correccion` y las fases correctas.

**Compatibilidad con el formato del Kit.** Los CSV de defectos tienen exactamente las 8 columnas del Kit. Los de tiempo tienen las **6 columnas del Kit en el mismo orden** y una 7.ª, `minutos_estimados`, al final, que existe solo porque las filas retrospectivas no tienen `inicio` ni `fin` (la duración no se puede calcular); una lectura que use solo las columnas del Kit sigue funcionando. Las filas con horarios reales (desde la entrega, `tiempo-posentrega-integrante-a.csv`) dejan `minutos_estimados` vacío.
**Vacío significa «no registrado», no cero.** Ningún defecto tiene aún `minutos_correccion`: no se midieron y los commits solo dan fechas de introducción y corrección, no esfuerzo.
**Totales de A:** acumulado general 2,130 min = prototipo (`[PROTOTIPO]`) 480 + desarrollo formal 1,650 (E0 270 + E1 1,380). Detalle en [`psp-e0-integrante-a-respaldo.md`](psp-e0-integrante-a-respaldo.md) y [`psp-e1-integrante-a-respaldo.md`](psp-e1-integrante-a-respaldo.md).

## Cómo registrar
1. **No renombren** los archivos `...-integrante-a.csv` / `...-integrante-b.csv`: las pruebas y los documentos dependen de esos nombres.
2. **Tiempo:** una fila por bloque de trabajo. `fecha` AAAA-MM-DD, `inicio`/`fin` HH:MM (24 h), `interrupcion_min` entero, `fase` ∈ {planeacion, diseno, codigo, revision, pruebas, documentacion, entrevista}, `actividad` texto corto, `minutos_estimados` (columna añadida a la plantilla del Kit, **al final**, igual para los dos integrantes: solo para duraciones retrospectivas sin horario; si registras `inicio` y `fin` reales, déjala vacía). Las filas retrospectivas llevan `[ESTIMADO RETROSPECTIVO]` en `actividad` y `inicio`, `fin` e `interrupcion_min` vacíos. Registrar al terminar el bloque, no de memoria al final.
3. **Defectos:** una fila por defecto encontrado. `tipo` ∈ los diez de PSP: documentacion, sintaxis, construccion, asignacion, interfaz, verificacion, datos, funcion, sistema, entorno. `fase_introducido` y `fase_eliminado` ∈ las mismas fases que arriba. `minutos_correccion` entero. `defecto_origen`: número del defecto que causó este, si aplica. `numero` consecutivo por archivo.
4. Cada registro se compromete en Git por quien lo hizo (el historial es la evidencia).

Una fila de ejemplo del Kit (`2026-11-03,16:00,17:45,…`) **no** se copia aquí para no confundirla con datos reales.

## Alcance de los registros (reglas)
- Solo actividades, tiempos y defectos **reales**, con evidencia (commit, issue, captura). Las duraciones que no se cronometraron se registran como **estimación retrospectiva** (`minutos_estimados` y la etiqueta `[ESTIMADO RETROSPECTIVO]`), sin inventar horarios de inicio ni fin.
- El trabajo del **prototipo exploratorio** (`staymetrics-prototipo`) figura en el registro de la integrante A con la etiqueta `[PROTOTIPO]`, separado del proyecto definitivo (`[DEFINITIVO]`) y nunca atribuido a otra persona.
- Cada integrante registra únicamente lo suyo; el trabajo hecho por una no se asigna a la otra.
- **Cero defectos es válido:** una actividad con tiempo y sin filas en el CSV de defectos significa que no se detectó ninguno; no se inventan defectos para llenar el registro. Si se quiere dejar constancia, usar la columna `actividad` del tiempo (p. ej. "revisión de X: 0 defectos").
- Los tiempos de revisión cruzada los registra quien revisa; las correcciones, la autora. No se duplican.

## PSP de A: métricas de E3 y confirmaciones pendientes (2026-11-14)
**Qué se puede calcular hoy (con la salvedad de que el tiempo es estimado):** tiempo por fase; defectos por fase de introducción y de eliminación; proporción de defectos eliminados en `revision` y en `pruebas` (rendimiento por fase); defectos por tipo; densidad de defectos por KLOC (las líneas se obtienen de Git). **Qué no se puede calcular:** exactitud de las estimaciones (nunca se registró una estimación **previa** frente a un tiempo real); tiempo medio de corrección y esfuerzo perdido por defecto (sin `minutos_correccion`); productividad (líneas/hora) fiable (el tiempo no es medido); rendimiento de las revisiones en defectos/hora (el tiempo de revisión está mezclado con otras tareas en una sola fila). **Desde ahora** deben registrarse: la estimación **antes** de cada bloque, `inicio`/`fin`/`interrupcion_min` reales y `minutos_correccion` por defecto.
**Fases:** cada fila lleva una sola fase aunque varias actividades mezclan código, pruebas y documentación (p. ej. «Jerarquías, discretización, faltantes y atípicos», 150 min, `codigo`); eso sesga el tiempo por fase. **Tiempo personal frente a ejecución autónoma:** los minutos son dedicación personal de A; no incluyen suites, CI ni escaneos ejecutados por herramientas. **Duplicados:** no se encontraron actividades ni defectos repetidos ni tiempo contado dos veces (la Auditoría 6 está dentro de L3; la 7, en el cierre).
**Confirmaciones que solo A puede dar** (no se modifica ninguna fila hasta recibirlas):
| # | Pregunta | Dato de Git que sirve de referencia (no es tiempo trabajado) |
|---|---|---|
| 1 | ¿Las 8 filas de L0 y L1 (240 min) deben llevar fecha 2026-11-12, 2026-11-13 o repartirse? ¿A qué hora empezó L0? | Commit del contrato `f18e93a`, 11-12 23:17; pipeline `70a26b9`, 11-13 00:43 |
| 2 | ¿Fecha y hora de inicio de L2 (150 min)? | Commit `de42284`, 11-13 01:45 |
| 3 | ¿Fecha y hora de inicio de L3 (270 min), y cuándo se hizo el «cierre de observaciones» (40 min)? | `809cfa3`, 11-13 02:35; Auditoría 5 de B, 12:55; PR #13, 14:49 |
| 4 | ¿Cuándo empezó y terminó el cierre documental (720 min)? | Commits de A del 11-13 entre 14:49 y 23:16 (≈ 507 min de reloj) |
| 5 | La suma de L0 a L3 (660 min) cabe mal en las 3 h 18 min entre el commit de L0 y el de L3: ¿hubo trabajo antes del commit o en paralelo con la herramienta, o las estimaciones están infladas? ¿Se conservan o se corrigen? | Ventana total 11-12 23:17 a 11-13 23:29 ≈ 24 h 12 min frente a 1,380 min (23 h) |
| 6 | ¿Los 480 min del prototipo (11-08) y los 270 de E0 formal (11-09) se confirman? ¿Las fases asignadas a E0 son correctas? | Commits de E0 del 11-09 desde las 09:16 |
| 7 | ¿Cuántos minutos de corrección recuerda para cada defecto (#1 a #28)? Si no los recuerda, quedan «no registrados» | Fechas de introducción y corrección en la descripción de los defectos 23 a 28 |
| 8 | ¿Confirma las clasificaciones dudosas: #15 (importaciones sin usar: `construccion` o `sintaxis`), #16 (script que cambió fines de línea: `sistema` o `entorno`) y #28 (devcontainer: ¿lo agregó usted?)? | Descripciones en `defectos-integrante-a.csv` |
| 9 | ¿Cuántos minutos dedicó a esta rama posterior a la entrega (2026-11-13/14) y en qué horarios? Se registrarán en `tiempo-posentrega-integrante-a.csv` | Commits `cb11c30` (11-13 23:58), `dcc4bb2` y `07838e6` |
