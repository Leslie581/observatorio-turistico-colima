# PSP E1 de la integrante A: respaldo de los tiempos y defectos de E1

Corte: 2026-11-13. Este archivo **no es el registro** (el registro son los CSV de `calidad/`): reúne las actividades de E1 que respaldan, con archivos o comandos, el tiempo de **su** autora. Ningún tiempo se cronometró: los minutos de E1 son estimaciones aceptadas por la integrante A (ver abajo), y los horarios de inicio y fin no se inventaron.

## Defectos
Se agregaron 7 defectos reales de E1 (más los 19 a 21, véase «Registro») a `calidad/defectos-integrante-a.csv` (números 12 a 18, fecha 2026-11-13, `minutos_correccion` vacío). Los números 12 a 16 son de L0 y L1; los **17 y 18 son de L3** (una expectativa incorrecta en `tests/test_fiabilidad.py` y un recuento mal sumado en `docs/E1/requerimientos.md`). Son errores que se introdujeron y se corrigieron, cada uno con su evidencia en el texto de la fila. Si alguno no debe figurar en tu registro, bórralo. Las observaciones de revisión sobre el trabajo de Eimy **no** son defectos tuyos y no se registran aquí.

## Tiempo de E1: estimación revisada y aceptada
La integrante A revisó y aceptó (2026-11-13) una distribución de **240 minutos** entre ocho actividades, y se registró en `calidad/tiempo-integrante-a.csv` con la marca `[ESTIMADO RETROSPECTIVO]`. Son **estimaciones, no tiempos medidos**: nada se cronometró. `inicio`, `fin` e `interrupcion_min` quedan vacíos porque no se pueden reconstruir; todas las filas llevan fecha 2026-11-13 y la duración en `minutos_estimados`.
| Fase | Actividad | Minutos | Evidencia |
|---|---|---|---|
| planeacion | Lectura de los requisitos de E1 en el PDF y matriz de requisitos | 25 | `docs/E1/plan_trabajo.md` |
| codigo | Diagnóstico de Base70 y DENUE con datos reales | 30 | `docs/E1/contrato_datos.md` §1 |
| documentacion | Contrato de datos 1.0.0 y su revisión r1 | 40 | `docs/E1/contrato_datos.md` |
| revision | Revisión de las tres observaciones de Eimy (sin fusionar su rama) | 15 | `docs/E1/contrato_datos.md` §9 |
| codigo | Plata de Base70 y DENUE, reglas R-D01 a R-E06 y cuarentena | 45 | `pipeline/plata_*.py`, `pipeline/calidad/` |
| codigo | Capa oro, diccionario, interfaz, orquestador y validación contra derivación independiente | 30 | `pipeline/oro.py`, `interfaz.py`, `ejecutar.py` |
| pruebas | Pruebas del pipeline, de la interfaz, de la reproducibilidad y de `ci.yml` | 35 | `tests/test_pipeline_*.py`, `tests/test_ci_workflow.py` |
| codigo | Dependencias fijadas, `ruff.toml`, `ci.yml` y revisión de `wrapt` | 20 | `requirements*.txt`, `.github/workflows/ci.yml` |

**Alcance de este bloque.** Estos 240 minutos cubren las actividades de L0 y L1 listadas arriba. L2 y L3 están en las secciones siguientes. **El único tiempo pendiente de registrar es el del cierre documental**, porque ese trabajo no ha terminado. Ningún tiempo es medido: todos son `[ESTIMADO RETROSPECTIVO]` y no se agregan horas futuras. Los `minutos_correccion` de los defectos 12 a 22 están vacíos por falta de evidencia.

**Aviso:** parte de este trabajo se hizo con apoyo de Claude Code; el tiempo que registres es **tuyo**, no el de la herramienta.

## Tiempo de L3: estimación aceptada y registrada (270 min)
Estimación retrospectiva aceptada por la integrante A (2026-11-13) y registrada en `calidad/tiempo-integrante-a.csv` (8 filas) con la etiqueta `[ESTIMADO RETROSPECTIVO]`; `inicio`, `fin` e `interrupcion_min` vacíos. **No son tiempos medidos.**
| Fase | Actividad | Minutos | Evidencia |
|---|---|---|---|
| planeacion | Lectura de los requisitos de Calidad en el PDF y comparación con lo existente | 25 | `docs/E1/requerimientos.md` §1 |
| codigo | `pipeline/fiabilidad.py` y sus 12 pruebas | 35 | `pipeline/fiabilidad.py`, `tests/test_fiabilidad.py` |
| pruebas | Evidencia operativa: API de Actions, cotejo con la bitácora, restauración del bronce, búsqueda de secretos, `pip-audit` y permisos | 40 | `docs/E1/seguridad.md`, `docs/E1/fiabilidad.md` §4 |
| documentacion | `requerimientos.md` (36 requerimientos) y su prueba de consistencia | 45 | `docs/E1/requerimientos.md`, `tests/test_requerimientos.py` |
| documentacion | `fiabilidad.md` y `seguridad.md` | 40 | `docs/E1/fiabilidad.md`, `docs/E1/seguridad.md` |
| documentacion | `plan_sqa.md` y actualización de `plan_trabajo.md` y `README` | 35 | `docs/E1/plan_sqa.md` |
| pruebas | Validación (suite, `ruff`, verificador E0, pipeline) | 10 | salidas de los comandos |
| codigo | Cierre de observaciones: `gitleaks`, evaluación del UUID, horarios y defectos 17 y 18 | 40 | `docs/E1/seguridad.md` §3, `calidad/defectos-integrante-a.csv` |
| | **Total L3** | **270** | |

## Tiempo de L2: estimación aceptada y registrada (150 min)
**Qué es medido y qué no.** *Medido:* nada; no hubo cronómetro. *Evidencia de actividad (no es tiempo trabajado):* las horas locales de los commits propios del 13 de noviembre (L2 `de42284` a las 01:45, L3 `809cfa3` a las 02:35); los intervalos entre commits son una cota superior de calendario, no minutos de trabajo. *Estimado y aceptado:* L0 y L1 (240 min), L2 (150 min) y L3 (270 min), registrados en el CSV (5 filas de L2). *Pendiente:* el cierre documental.

| Fase | Actividad de L2 (PR #10) | Minutos | Evidencia |
|---|---|---|---|
| codigo | Exploración: estadísticas y cuatro gráficas del oro | 40 | `laboratorio/exploracion/`, `docs/E1/exploracion.md` |
| codigo | Transformaciones sin fuga (min-max, z-score, discretización) | 40 | `pipeline/transformaciones.py` |
| pruebas | Pruebas de exploración y de transformaciones | 25 | `tests/test_exploracion.py`, `tests/test_pipeline_transformaciones.py` |
| codigo | `verificar_oro` y su paso en `ci.yml` | 25 | `pipeline/verificar_oro.py`, `tests/test_verificar_oro.py` |
| documentacion | `transformaciones.md` y textos de CI | 20 | `docs/E1/transformaciones.md`, `docs/E1/pipeline.md` |
| | **Total L2** | **150** | |

**Cierre documental (sin minutos todavía):** integración de `main` sin sobrescribir; Auditoría 6; respuesta a la Auditoría 5; actualización de fiabilidad con la captura del 13 de noviembre; evidencia de `gitleaks`; `ENTREGA.md`, relatoría y auditoría integral; validación. Se estimará cuando terminen las correcciones, pruebas y revisión de la entrega.

## Registro (2026-11-13)
- **Tiempos de A aceptados y registrados:** L0 y L1 240 min, L2 150 min y L3 270 min = **660 min de E1 registrados hasta ahora**, más 750 min de E0. Todos `[ESTIMADO RETROSPECTIVO]`, con `inicio`, `fin` e `interrupcion_min` vacíos. El total de E1 crecerá cuando se registre el cierre documental.
- **Defectos 19, 20 y 21** (Auditoría 5, D2, D3 y D4): registrados con `minutos_correccion` vacío. El 21 no duplica al 18 (recuento de requerimientos). El defecto de la prueba del tablero con `__pycache__` se registró como defecto 22 (véase abajo).
- **Pendiente:** el tiempo del cierre documental.
- El PSP de B no se tocó.

## Defecto de la prueba del tablero (Auditoría 7, D4): autoría y registro
Historial de Git (consultado el 2026-11-13): la prueba `test_no_hay_secretos_ni_archivos_temporales_en_el_tablero` entró en el commit `9489dc5` (2026-11-13 17:08 -0600), cuyo **autor y comitente es Leslie Valadez**; la corrigieron los commits `80d8b5b` y `eb8f606` de **eimymuz** (20:27 y 20:42 -0600), fusionados en el PR #15. El defecto tuvo 3 ejecuciones de CI fallidas. Se registró como **defecto 22 en `defectos-integrante-a.csv`** (con `minutos_correccion` vacío), porque el commit que lo introdujo figura a nombre de la integrante A; la documentación del tablero lo atribuye a un trabajo de B, pero Git no distingue quién redactó el código dentro de ese commit. El defecto 14 de B es otro (un `import`).

## Trabajo del cierre documental ampliado (2026-11-14), sin tiempo registrado todavía
Actividades hechas después de aceptar L2 y L3, que se estimarán junto con el resto del cierre documental cuando este termine (**no se propone ningún minuto ahora y no se agregó nada a los CSV**): integración de `main` y revisión del PR #15 (Auditoría 7); `gitleaks` y pruebas del tablero en CI; jerarquías conceptuales en el oro; discretización supervisada y su comparación; faltantes y atípicos; respaldo del bronce con manifiesto; bloqueo con hashes y acciones por SHA; cobertura; preparación de E2; auditoría integral y evaluación contra las rúbricas; actualización de la documentación. El PSP de B no se tocó.
