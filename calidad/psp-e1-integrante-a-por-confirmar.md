# PSP E1 de la integrante A: lo que falta confirmar

Corte: 2026-11-13. Este archivo **no es un registro**: reúne las actividades de E1 que se pueden respaldar con archivos o comandos para que la integrante A anote **su** tiempo real. No hay horas ni minutos escritos porque ninguno se cronometró ni se ha confirmado; no se inventaron.

## Defectos
Se agregaron 5 defectos reales de E1 a `calidad/defectos-integrante-a.csv` (números 12 a 16, fecha 2026-11-13, `minutos_correccion` vacío). Son errores que se introdujeron y se corrigieron durante L0 y L1, cada uno con su evidencia en el texto de la fila. Si alguno no debe figurar en tu registro, bórralo. Las observaciones de revisión sobre el trabajo de Eimy **no** son defectos tuyos y no se registran aquí.

## Actividades de E1 sin tiempo (para que las completes)
Fórmula para registrarlas, como en E0: una fila en `calidad/tiempo-integrante-a.csv` con `inicio`, `fin` e `interrupcion_min` vacíos si no los tienes, la etiqueta `[ESTIMADO RETROSPECTIVO]` en `actividad` y la duración en `minutos_estimados`.
| Fase | Actividad | Evidencia |
|---|---|---|
| planeacion | Lectura de los requisitos de E1 en el PDF y matriz de requisitos | `docs/E1/plan_trabajo.md` |
| codigo | Diagnóstico de Base70 y DENUE con los datos reales | `docs/E1/contrato_datos.md` §1 |
| documentacion | Contrato de datos 1.0.0 y su revisión r1 | `docs/E1/contrato_datos.md` |
| codigo | Plata de Base70 y DENUE, reglas R-D01 a R-D08 y R-E01 a R-E06 y cuarentena | `pipeline/plata_*.py`, `pipeline/calidad/` |
| codigo | Capa oro, diccionario, interfaz y orquestador | `pipeline/oro.py`, `interfaz.py`, `ejecutar.py` |
| pruebas | Pruebas del pipeline, de la interfaz, de la reproducibilidad y de `ci.yml` | `tests/test_pipeline_*.py`, `tests/test_ci_workflow.py` |
| codigo | Dependencias fijadas, `ruff.toml` y `ci.yml` (sin ejecutar en GitHub) | `requirements*.txt`, `.github/workflows/ci.yml` |
| revision | Revisión de las tres observaciones de Eimy (sin fusionar su rama) | `docs/E1/contrato_datos.md` §9 |

**Aviso:** parte de este trabajo se hizo con apoyo de Claude Code; el tiempo que registres es **tuyo**, no el de la herramienta.
