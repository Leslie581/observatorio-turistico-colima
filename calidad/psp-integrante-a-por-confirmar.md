# PSP integrante A (parte técnica): qué hay y qué debes confirmar

Corte 2026-11-10. Si no eres la persona de la parte técnica, no uses estos archivos. Parte del trabajo se hizo con asistencia de Claude Code (declararlo en la relatoría): lo que registras es **tu** tiempo.

## Cómo se registraron las horas
Confirmado por la integrante A el 2026-11-10: **prototipo el 2026-11-08 (480 min)** y **repositorio definitivo el 2026-11-09 (240 min)**; total 720 min. Son **estimaciones retrospectivas, no cronometradas**. No se inventaron horarios: `inicio`, `fin` e `interrupcion_min` están **vacíos**. Se añadió al final de la plantilla la columna **`minutos_estimados`** (en `tiempo-integrante-a.csv` y `tiempo-integrante-b.csv`, con las mismas columnas; los datos de B siguen vacíos) y cada fila lleva `[PROTOTIPO]` o `[DEFINITIVO]` y `[ESTIMADO RETROSPECTIVO]` en `actividad`.

| Bloque | Min | Fase | Fecha |
|---|---:|---|---|
| [PROTOTIPO] Investigación de fuentes y viabilidad | 60 | planeacion | 2026-11-08 |
| [PROTOTIPO] Obtención y verificación del histórico DATATUR | 75 | codigo | 2026-11-08 |
| [PROTOTIPO] Diagnóstico de extracción DATATUR y corrección del parser | 135 | codigo | 2026-11-08 |
| [PROTOTIPO] Conexión y validación DENUE | 65 | codigo | 2026-11-08 |
| [PROTOTIPO] Pruebas de integridad y transformaciones | 65 | pruebas | 2026-11-08 |
| [PROTOTIPO] Exploración estadística E1, PCA y MANOVA | 80 | codigo | 2026-11-08 |
| **Subtotal prototipo** | **480** | | |
| [DEFINITIVO] Organización del repositorio y documentación E0 | 75 | documentacion | 2026-11-09 |
| [DEFINITIVO] Integración Git, commits y seguridad | 45 | codigo | 2026-11-09 |
| [DEFINITIVO] Captura local DENUE y verificación E0 | 35 | pruebas | 2026-11-09 |
| [DEFINITIVO] Configuración y depuración de GitHub Actions | 65 | codigo | 2026-11-09 |
| [DEFINITIVO] Revisión de pruebas y ejecución exitosa | 20 | pruebas | 2026-11-09 |
| **Subtotal definitivo** | **240** | | |
| **Total (reconstrucción inicial)** | **720** | | |
| [DEFINITIVO] Auditoría interna posterior a la fusión del PR #1 sobre los 7 archivos de la integrante B (estimación retrospectiva, sin horario) | 30 | revision | 2026-11-09 |
| **Total con la auditoría** | **750** | | |

Las **fases** (columna `fase`) las asignó el asistente a partir del nombre de cada bloque; la integrante A puede corregirlas.

## Columnas
**Tiempo:** `fecha` · `inicio`/`fin` (HH:MM) · `interrupcion_min` · `fase` (planeacion, diseno, codigo, revision, pruebas, documentacion, entrevista) · `actividad`. **Defectos:** `numero` · `fecha` · `tipo` (los 10 de PSP) · `fase_introducido` · `fase_eliminado` · `minutos_correccion` · `defecto_origen` · `descripcion`.

## Defectos (solo corregidos; `minutos_correccion` vacío en todos: no se inventó)
| # | Dónde | Qué | Evidencia |
|---|---|---|---|
| 1 | Prototipo | Parser leyó la definición (20 argumentos) y no la llamada (16) | `evidencias/diagnostico_monitoreo_20261109T044253Z` del prototipo |
| 2 | Prototipo | Interpretación de la tabla (Subtotal, NA/ND, meses ausentes) | informe v5.1 §3.3 e INFORME_PARA_CLAUDE del prototipo. Fecha 2026-11-08 (día del prototipo); la evidencia es documental |
| 3 | Prototipo | Token de INEGI en la bitácora | `redaccion_token_20261109.json` (no estaba en tu lista; hay evidencia) |
| 4–7 | Definitivo | pandas bloqueado; sanitización sin domicilio/`Nombre`; histórico sin comprobar huecos; paso final sin la verificación | `requirements.txt`, `ef6d23b` |
| 8 | Definitivo | Falta de `INEGI_TOKEN` en Actions (run 42729922838) | bitácora |
| 9 | Definitivo | Tratamiento incorrecto del incumplimiento de disponibilidad (run 42730477358) | `156a024` |
| 10–11 | Definitivo | Salida cp1252; fallo de la prueba del paso final | `156a024` |

No consta **quién** corrigió cada uno: el CSV es tu registro individual; si alguno lo corrigió tu compañera, quítalo.

## Fuera del CSV de defectos (ver `calidad/riesgos.md`)
- **Incidencias pendientes:** HTTP 403 de `repodatos` (no se corrige: no se evade), fin de línea del prototipo (mitigado aquí), disponibilidad 66.7 % sin cumplir, y **“fecha duplicada”**: **sin evidencia verificable** en los archivos, por lo que **no se agregó**; solo entra si se aporta commit, archivo o ejecución.
- **Riesgos:** MANOVA (R6) y el resto; no son defectos.
