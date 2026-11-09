# Calidad: registros PSP, objetivos y bitácora de capturas

| Archivo | Qué es | Quién lo llena |
|---|---|---|
| `defectos-integrante-a.csv`, `defectos-integrante-b.csv` | Registro **individual** de defectos (formato del Kit TDL) | Cada integrante, solo el suyo |
| `tiempo-integrante-a.csv`, `tiempo-integrante-b.csv` | Registro **individual** de tiempo (formato del Kit TDL) | Cada integrante, solo el suyo |
| [`objetivos.md`](objetivos.md) | Tres objetivos de calidad medibles | Equipo |
| `bitacora_capturas.jsonl` | Una línea por ejecución de la captura (la escribe el extractor; no editar a mano). Aparece con la primera ejecución real. | Automática |
| `revision_calidad.md` | Responsable de revisión por entrega y lista de comprobación de E0 | Equipo |
| [`auditorias.md`](auditorias.md), [`lista_verificacion_auditoria.md`](lista_verificacion_auditoria.md) | Proceso y registro de la revisión cruzada; lista reutilizable | Quien audita |
| [`riesgos.md`](riesgos.md) | Riesgos pendientes (distintos de defectos) | Equipo |

**Estado: plantillas vacías.** No hay filas porque nadie ha registrado tiempo ni defectos reales todavía; **no se inventan datos**. Los archivos están listos con el encabezado del Kit.

## Cómo registrar
1. Cuando decidan quién es A y quién B, renombren los archivos al formato del Kit: `defectos-<nombre>.csv` y `tiempo-<nombre>.csv` (por ejemplo con `git mv`; el contenido no cambia).
2. **Tiempo:** una fila por bloque de trabajo. `fecha` AAAA-MM-DD, `inicio`/`fin` HH:MM (24 h), `interrupcion_min` entero, `fase` ∈ {planeacion, diseno, codigo, revision, pruebas, documentacion, entrevista}, `actividad` texto corto. Registrar al terminar el bloque, no de memoria al final.
3. **Defectos:** una fila por defecto encontrado. `tipo` ∈ los diez de PSP: documentacion, sintaxis, construccion, asignacion, interfaz, verificacion, datos, funcion, sistema, entorno. `fase_introducido` y `fase_eliminado` ∈ las mismas fases que arriba. `minutos_correccion` entero. `defecto_origen`: número del defecto que causó este, si aplica. `numero` consecutivo por archivo.
4. Cada registro se compromete en Git por quien lo hizo (el historial es la evidencia).

Una fila de ejemplo del Kit (`2026-11-03,16:00,17:45,…`) **no** se copia aquí para no confundirla con datos reales.

## Alcance de los registros (reglas)
- Solo actividades, tiempos y defectos **reales** del proyecto definitivo, con evidencia (commit, issue, captura). No se reconstruyen horas de memoria ni se rellenan con tiempos supuestos.
- El trabajo del **prototipo exploratorio** (`staymetrics-prototipo`) es anterior y no se carga a estos registros. Si el equipo quiere conservar su tiempo, irá en un archivo aparte marcado `prototipo`, solo con evidencia y por quien lo hizo; nunca atribuido a otra persona.
- Cada integrante registra únicamente lo suyo; el trabajo hecho por una no se asigna a la otra.
- **Cero defectos es válido:** una actividad con tiempo y sin filas en el CSV de defectos significa que no se detectó ninguno; no se inventan defectos para llenar el registro. Si se quiere dejar constancia, usar la columna `actividad` del tiempo (p. ej. "revisión de X: 0 defectos").
- Los tiempos de revisión cruzada los registra quien revisa; las correcciones, la autora. No se duplican.
