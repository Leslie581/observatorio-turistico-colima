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

**Estado de la entrega E1 (cerrada; etiqueta `e1`):** A: E0 750 min + E1 1,380 min = **2,130 min** (estimaciones retrospectivas; 480 min de E0 son del prototipo, etiquetados `[PROTOTIPO]`) y 22 defectos; B: E0 633 min + E1 118 min en 23 intervalos con inicio y fin, y 14 defectos. Sin horarios inventados. **No se editan** las filas de la entrega.

**Trabajo posterior a la entrega (desde 2026-11-13/14):** se registra aparte en `tiempo-posentrega-integrante-a.csv` (mismo formato) para no alterar lo entregado; se llena **desde el inicio de cada bloque** con `inicio`, `fin` e `interrupcion_min` reales. Para la retrospectiva PSP de E3 (exactitud de las estimaciones, defectos inyectados y eliminados por fase, rendimiento de revisiones) cada defecto nuevo debe llevar `minutos_correccion` y las fases correctas.

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
