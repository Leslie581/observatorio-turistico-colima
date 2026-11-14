# Riesgos pendientes (no son defectos)

Un **riesgo** es algo que puede salir mal; un **defecto** es un error realmente detectado y va al registro PSP. Esta lista no alimenta los CSV de defectos. Si un riesgo se materializa, se abre la fila de defecto con su evidencia.

| ID | Riesgo | Estado | Mitigación |
|---|---|---|---|
| R1 | Uso automatizado/publicación de DATATUR (Sistema de Monitoreo) sin autorización | Abierto | Canal suspendido y fuera de Git (`docs/fuentes/datatur.md`) |
| R2 | Hay 5 ejecuciones reales en GitHub Actions, 3 de ellas por `schedule`; `main` protegida haría fallar el push del bot | Abierto | Ejecución manual y revisión (`docs/E0/verificacion.md`) |
| R3 | El DENUE cambia poco; la captura diaria no produce serie diaria | Abierto | Documentado en la propuesta |
| R4 | Cuotas de la API DENUE no documentadas | Abierto | Máx. 2–3 solicitudes por ejecución |
| R5 | Cifras de SECTUR con revisiones retroactivas | Abierto | Hash y fecha en la ficha |
| R6 | MANOVA (E3) sin supuestos validados | Abierto | Rediseño en E3 |
| R7 | Entrevista con registro parcial (aplicada por un colaborador externo, sin respuestas publicables) y encuesta exploratoria: cliente e hipótesis sin validar | Abierto | Issue 5 |
| R8 | `Nombre` del DENUE podía contener el nombre de una persona física | **Mitigado** (2026-11-09): el campo se excluye del bronce; verificado con 4 archivos DENUE reales | `docs/fuentes/denue.md` |

## Incidencias pendientes (ya ocurrieron y siguen abiertas; no son riesgos ni defectos corregidos)
| ID | Incidencia | Evidencia | Estado |
|---|---|---|---|
| I1 | `repodatos.atdt.gob.mx` responde HTTP 403 a scripts (prototipo, Windows). Es una restricción del servidor; **no se evade**. Se mitiga con descarga manual por navegador y verificación por hash | `docs/fuentes/datatur.md` (R2) | Abierta; no se corrige, se evita |
| I2 | Fin de línea: la puerta de calidad del prototipo reescribió CSV validados con LF. En este repositorio esa puerta no se migró y `.gitattributes` conserva los datos byte a byte | `registro_cambios.md` e informe v5.1 del prototipo | Mitigada en el repositorio definitivo; sin corrección en el prototipo |
| I3 | Disponibilidad O1: **85.7 % (6 de 7) al 2026-11-13 20:28 UTC** (83.3 % al 2026-11-12; 66.7 % al crear la etiqueta e0), objetivo 95 % no cumplido; la bitácora cubre 3.83 días | `calidad/bitacora_capturas.jsonl` | Abierta; se mide en E1 con ejecuciones reales ([`docs/E1/fiabilidad.md`](../docs/E1/fiabilidad.md)) |
| I4 | “Fecha duplicada”: mencionada por la integrante A sin que se localizara evidencia en archivos | — | Falta descripción y evidencia; no está en el CSV de defectos |

MANOVA (E3) permanece en R6 como **riesgo metodológico**; no es un defecto corregido.
