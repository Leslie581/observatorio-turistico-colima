# PSP E1 de la integrante A: lo que falta confirmar

Corte: 2026-11-13. Este archivo **no es un registro**: reúne las actividades de E1 que se pueden respaldar con archivos o comandos para respaldar el registro de **su** tiempo. Ningún tiempo se cronometró: los minutos de E1 son estimaciones aceptadas por la integrante A (ver abajo), y los horarios de inicio y fin no se inventaron.

## Defectos
Se agregaron 7 defectos reales de E1 a `calidad/defectos-integrante-a.csv` (números 12 a 18, fecha 2026-11-13, `minutos_correccion` vacío). Los números 12 a 16 son de L0 y L1; los **17 y 18 son de L3** (una expectativa incorrecta en `tests/test_fiabilidad.py` y un recuento mal sumado en `docs/E1/requerimientos.md`). Son errores que se introdujeron y se corrigieron, cada uno con su evidencia en el texto de la fila. Si alguno no debe figurar en tu registro, bórralo. Las observaciones de revisión sobre el trabajo de Eimy **no** son defectos tuyos y no se registran aquí.

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

**Lo que sigue sin registrarse.** Estos 240 minutos cubren solo las actividades de L0 y L1 listadas arriba. **No tienen tiempo registrado** el trabajo de L2 (exploración, transformaciones, `verificar_oro`, textos de CI), ni el de L3 (requerimientos, fiabilidad, seguridad, plan SQA, `gitleaks`), ni el de verificación final, commit y publicación de las ramas. Cuando apruebes una estimación para cada fase se agregará como `[ESTIMADO RETROSPECTIVO]`; **no se agregan horas futuras**. El objetivo aproximado de E1 es de 8 horas. Los `minutos_correccion` de los defectos 12 a 18 siguen vacíos por falta de evidencia.

**Aviso:** parte de este trabajo se hizo con apoyo de Claude Code; el tiempo que registres es **tuyo**, no el de la herramienta.

## Propuesta de tiempo de L3: PENDIENTE de tu confirmación (NO registrada en `tiempo-integrante-a.csv`)
Estimación retrospectiva **propuesta** (2026-11-13) por el volumen de trabajo de L3; **no son tiempos medidos** y **no se han agregado al CSV**. La integrante A debe confirmar o ajustar cuánto tiempo **personal** dedicó; hasta entonces estas filas no existen en su registro. Si se aprueban, cada una se agregaría con fecha 2026-11-13, `inicio`, `fin` e `interrupcion_min` vacíos, la etiqueta `[ESTIMADO RETROSPECTIVO]` y la duración en `minutos_estimados`.
| Fase | Actividad | Minutos propuestos | Evidencia |
|---|---|---|---|
| planeacion | Lectura de los requisitos de Calidad en el PDF y comparación con lo existente | 25 | `docs/E1/requerimientos.md` §1 |
| codigo | `pipeline/fiabilidad.py` y sus 12 pruebas | 35 | `pipeline/fiabilidad.py`, `tests/test_fiabilidad.py` |
| pruebas | Evidencia operativa: API de Actions, cotejo con la bitácora, restauración del bronce, búsqueda de secretos, `pip-audit` y permisos | 40 | `docs/E1/seguridad.md`, `docs/E1/fiabilidad.md` §4 |
| documentacion | `requerimientos.md` (36 requerimientos) y su prueba de consistencia | 45 | `docs/E1/requerimientos.md`, `tests/test_requerimientos.py` |
| documentacion | `fiabilidad.md` y `seguridad.md` | 40 | `docs/E1/fiabilidad.md`, `docs/E1/seguridad.md` |
| documentacion | `plan_sqa.md` y actualización de `plan_trabajo.md` y `README` | 35 | `docs/E1/plan_sqa.md` |
| pruebas | Validación (suite, `ruff`, verificador E0, pipeline) | 10 | salidas de los comandos |
| codigo | Cierre de observaciones: `gitleaks`, evaluación del UUID, horarios y defectos 17 y 18 | 40 | `docs/E1/seguridad.md` §3, `calidad/defectos-integrante-a.csv` |
| | **Total propuesto** | **270** | |
**Pendientes de estimar (tampoco registrados):** el trabajo de **L2** (exploración, transformaciones, `verificar_oro`, textos de CI) y el de verificación final, commit y publicación de las ramas. Con los 240 minutos ya registrados y estos 270, el total superaría el objetivo aproximado de 8 horas; no se recorta para que cuadre sin una estimación honesta de la integrante A.
