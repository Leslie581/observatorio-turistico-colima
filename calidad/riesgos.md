# Riesgos pendientes (no son defectos)

Un **riesgo** es algo que puede salir mal; un **defecto** es un error realmente detectado y va al registro PSP. Esta lista no alimenta los CSV de defectos. Si un riesgo se materializa, se abre la fila de defecto con su evidencia.

| ID | Riesgo | Estado | Mitigación |
|---|---|---|---|
| R1 | Uso automatizado/publicación de DATATUR (Sistema de Monitoreo) sin autorización | Abierto | Canal suspendido y fuera de Git (`docs/fuentes/datatur.md`) |
| R2 | La ejecución en GitHub Actions aún no se ha probado; `main` protegida haría fallar el push del bot | Abierto | Ejecución manual y revisión (`docs/E0/verificacion.md`) |
| R3 | El DENUE cambia poco; la captura diaria no produce serie diaria | Abierto | Documentado en la propuesta |
| R4 | Cuotas de la API DENUE no documentadas | Abierto | Máx. 2–3 solicitudes por ejecución |
| R5 | Cifras de SECTUR con revisiones retroactivas | Abierto | Hash y fecha en la ficha |
| R6 | MANOVA (E3) sin supuestos validados | Abierto | Rediseño en E3 |
| R7 | Entrevista pendiente: cliente e hipótesis sin validar | Abierto | Issue 5 |
| R8 | `Nombre` del DENUE podía contener el nombre de una persona física | **Mitigado** (2026-11-09): el campo se excluye del bronce; verificar con la primera captura real | `docs/fuentes/denue.md` |
