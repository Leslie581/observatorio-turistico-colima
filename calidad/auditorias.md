# Registro de auditorías cruzadas

Proceso acordado:
1. Cuando A termina sus cambios, B los audita; cuando B termina los suyos, A los audita.
2. Quien audita documenta los hallazgos y es la responsable de revisión de calidad de ese conjunto de cambios.
3. La autora atiende las correcciones.
4. Cada quien registra **sus propios** tiempos y defectos (los de revisión los registra quien revisa; los de corrección, la autora). Un mismo defecto/tiempo no se registra dos veces.
5. Integración final con evidencia de revisión, preferentemente un pull request cuando se trabaje en ramas.
6. Los primeros commits directos en `main` se auditan **después** de integrarse; se anota como "auditoría posterior" y **no** se presenta como revisión previa.

Usar [`lista_verificacion_auditoria.md`](lista_verificacion_auditoria.md). No se llenan aprobaciones ni firmas hasta que ocurra la auditoría real.

| # | Conjunto de cambios | Autora | Auditora | Tipo (posterior / PR) | Fecha | Hallazgos | Correcciones (commit) | Estado |
|---|---|---|---|---|---|---|---|---|
| 1 | PR #1 `b/validacion-usuarios-e0` (commits `cb64a84`, `8d81922`; fusión `6038081`) | Integrante B (`eimymuz`) | Integrante A (`Leslie581`) | **Posterior a la fusión** (el PR #1 se fusionó el 2026-11-10 05:10 UTC, que en México (UTC-6) eran las 23:10 del 2026-11-09, sin revisiones ni comentarios) | 2026-11-09 | 2 solicitar corrección, 3 aprobar con observaciones, 1 revisión condicionada; detalle en [Auditoría 1](#auditoría-1-pr-1-posterior-a-la-fusión) | Pendientes (ningún commit de corrección todavía) | **Correcciones solicitadas.** Sin aprobación plena; entrevista y encuesta **no** quedan plenamente validadas |

## Auditoría 1: PR #1, posterior a la fusión
**Tipo:** auditoría **posterior**. El PR #1 (rama `b/validacion-usuarios-e0`, autora `eimymuz`) se fusionó el 2026-11-10 a las 05:10 **UTC** mediante `6038081`; esa fecha corresponde al horario UTC, y en México (UTC-6) todavía era el **2026-11-09 a las 23:10**. Las fechas del evento son las reales y no se modificaron. La auditoría es **posterior** a esa fusión y **sin revisión previa** (0 revisiones y 0 comentarios en GitHub). Esta revisión no se presenta como control previo a la integración.
**Auditora:** integrante A (`Leslie581`), responsable de revisión de calidad de este conjunto de cambios. **Lista usada:** [`lista_verificacion_auditoria.md`](lista_verificacion_auditoria.md). **Fecha del registro:** 2026-11-09 (reloj del equipo); no se consigna hora de la revisión. **Tiempo de revisión:** 30 minutos, **estimación retrospectiva** (no cronometrada), registrados por la auditora en [`tiempo-integrante-a.csv`](tiempo-integrante-a.csv) sin horario de inicio ni fin.
**Alcance:** los 7 archivos del PR. **Fuera de alcance:** la parte técnica de la integrante A (ver "Observaciones que no pertenecen al PR").
**Decisiones:** son de la auditora; el asistente solo reunió la evidencia. Ningún archivo queda marcado como aprobado sin reservas.

| Archivo | Decisión de la auditora |
|---|---|
| `docs/E0/Entrevistas/entrevista_01.md` | **SOLICITAR CORRECCIÓN** |
| `docs/E0/encuesta/LEEME.md` | **APROBAR CON OBSERVACIONES** |
| `docs/E0/encuesta/informe_encuesta_e0.md` | **APROBAR CON OBSERVACIONES** |
| `laboratorio/encuesta_e0/` (script y README) | **REVISIÓN CONDICIONADA** |
| `docs/E0/propuesta.md` | **APROBAR CON OBSERVACIONES** |
| `docs/E0/ENTREGA.md` | **SOLICITAR CORRECCIÓN** |

### Observaciones VERIFICADAS (con evidencia consultable)
| # | Archivo y línea | Observación | Evidencia |
|---|---|---|---|
| V1 | [`entrevista_01.md:70`](../docs/E0/Entrevistas/entrevista_01.md) (§6) | No hay respuestas publicadas: las cinco filas dicen "registrada en los apuntes privados" | Lectura del archivo |
| V2 | [`entrevista_01.md:83`](../docs/E0/Entrevistas/entrevista_01.md) (§7) | Los aprendizajes son sobre el proceso de registro, no sobre el sector | Lectura del archivo |
| V3 | [`entrevista_01.md:10`](../docs/E0/Entrevistas/entrevista_01.md), [`:14`](../docs/E0/Entrevistas/entrevista_01.md), [`:100`](../docs/E0/Entrevistas/entrevista_01.md) | Duración "aproximadamente 15 minutos" **reportada y sin comprobante**; la llamada de recuperación sin fecha ni duración; el SHA-256 de los apuntes se menciona pero **no está publicado** | El propio documento |
| V4 | [`entrevista_01.md:17`](../docs/E0/Entrevistas/entrevista_01.md), [`:18`](../docs/E0/Entrevistas/entrevista_01.md) | Consentimiento para publicar y validez para E0 siguen sin confirmar | El propio documento |
| V5 | [`LEEME.md:45`](../docs/E0/encuesta/LEEME.md) (I10) | Menciona "3 en Jalisco": dato geográfico potencialmente identificable, en tensión con la regla de no publicar cuasi-identificadores ([`:76`](../docs/E0/encuesta/LEEME.md)) | Lectura del archivo |
| V6 | [`LEEME.md:81`](../docs/E0/encuesta/LEEME.md) | El CSV privado está en una carpeta sincronizada con OneDrive: queda fuera de GitHub, no fuera de OneDrive; el resguardo no está resuelto | El propio documento; `.gitignore` línea 39 ignora `evidencias_privadas/` |
| V7 | [`informe_encuesta_e0.md:255`](../docs/E0/encuesta/informe_encuesta_e0.md), [`:261`](../docs/E0/encuesta/informe_encuesta_e0.md) | El informe cita la guía interna `PENDIENTES_COMPANERA_E0.md` como fuente | Lectura del archivo |
| V8 | `informe_encuesta_e0.md` §4 a §5 | Los totales y porcentajes de las tablas son aritméticamente consistentes (perfiles suman 10; medias y medianas de utilidad correctas; porcentajes de las Tablas 2 a 10 correctos) | Recálculo de la auditoría |
| V9 | `informe_encuesta_e0.md` Tabla 1 | La fila de ocupación de Base70 es correcta: recalculada con la función del script y con un cálculo independiente en pandas | Resultados idénticos: 47.7, 46.7, 50.2, 56.2, 51.4, 53.1, 59.9, 50.4, 36.9, 42.7, 48.7, 56.2 |
| V10 | [`analisis_encuesta.py:458`](../laboratorio/encuesta_e0/analisis_encuesta.py), [`:459`](../laboratorio/encuesta_e0/analisis_encuesta.py) | Error no controlado con entradas vacías: `StatisticsError: mean requires at least one data point` en lugar del código 2 que documenta la cabecera (líneas 17 y 18) | Reproducido con un CSV sintético en una carpeta temporal (solo consentimientos, sin respuestas); no es un caso del CSV real |
| V11 | `analisis_encuesta.py` | El script solo lee (no escribe); sin el CSV termina con código 2 y un mensaje claro; con otro SHA-256 se niega a dar cifras | Ejecución y revisión del código |
| V12 | [`propuesta.md:124`](../docs/E0/propuesta.md) (§8.3) | Guion preliminar "no utilizado": contenido innecesario que alarga el documento; está presentado como de la integrante A | Lectura del archivo |
| V13 | [`propuesta.md:3`](../docs/E0/propuesta.md), [`ENTREGA.md:3`](../docs/E0/ENTREGA.md) | Nombres del equipo siguen sin completar | Lectura de los archivos |
| V14 | `propuesta.md` | 2,824 palabras (antes unas 2,150) | Conteo de palabras |
| V15 | `propuesta.md` §8.2 y aprendizajes | Las cifras citadas coinciden con el informe (8 de 10, 4 de 5, 3 de 10, 6 de 10) | Cotejo con el informe |
| V16 | [`ENTREGA.md:19`](../docs/E0/ENTREGA.md) | Tres de los cinco enlaces a ejecuciones de Actions devuelven 404: `42729922838`, `42730477358`, `42732765759` (solo `42733220215` y `42733335021` existen) | Consulta a la API pública de GitHub, 2026-11-10 |
| V17 | [`ENTREGA.md:39`](../docs/E0/ENTREGA.md), [`:49`](../docs/E0/ENTREGA.md) | Datos desactualizados: "69 aprobadas" (la suite actual da 87 aprobadas y 2 omitidas) y "aún no hay commits" (ya hay commits de ambas integrantes) | `pytest` sobre un clon limpio de `6038081`; `git log` |
| V18 | `ENTREGA.md` | Estructura de tres apartados correcta y 86 enlaces relativos de los `.md` del repositorio válidos | Verificación de enlaces |

### Cuestiones que SIGUEN SIN PODER COMPROBARSE
| # | Cuestión | Por qué |
|---|---|---|
| N1 | Que la entrevista se realizó, su duración real, el rol de la persona entrevistada y la identidad y procedencia del colaborador externo | No hay grabación ni registro de llamadas; el registro es indirecto (apuntes privados) |
| N2 | Contenido y existencia de los apuntes privados y de su SHA-256 | No están en el repositorio ni en la copia de la auditora |
| N3 | Consentimiento para publicar las respuestas | Sin confirmar |
| N4 | Cifras derivadas del CSV de la encuesta (11 envíos, 10 con consentimiento, 38 columnas, frecuencias de las Tablas 2 a 10 y SHA-256 `84c36f90…`) | El CSV original no está en la copia de la auditora; solo las verificó la autora |
| N5 | Ejecución completa de `analisis_encuesta.py` sobre el CSV original | Mismo motivo; solo se verificó la parte de Base70 |
| N6 | Extensión en páginas de la propuesta (3 a 5) | No hay forma de renderizarla en este entorno; 2,824 palabras con tablas probablemente la excede |
| N7 | Que la persona entrevistada corresponda o no a un envío de la encuesta | La propia documentación indica que no se ha verificado |

### Correcciones solicitadas a la autora del PR (pendientes)
1. **Entrevista:** si hay consentimiento, publicar un resumen anónimo de las cinco respuestas y aprendizajes sobre el sector; documentar fecha y duración de la llamada de recuperación; publicar el SHA-256 de los apuntes o retirar la mención; aclarar la duración y la procedencia. Sin consentimiento, mantener la limitación declarada y no darla por cumplida.
2. **LEEME:** revisar el dato geográfico de I10 y aclarar dónde queda resguardado el CSV privado.
3. **Informe:** retirar las referencias a `PENDIENTES_COMPANERA_E0.md` (líneas 255 y 261); validar las cifras derivadas del CSV (N4) entregando el CSV a la auditora para comprobar el hash y ejecutar el script.
4. **Script:** manejar entradas sin respuestas con el código de salida documentado, y quedar condicionado a la ejecución sobre el CSV original.
5. **Propuesta:** revisar la extensión, retirar la §8.3 si no aporta, y completar nombres.
6. **Ficha:** corregir enlaces 404, cifras desactualizadas y campos pendientes (ver abajo sobre su procedencia).

### Observaciones que no pertenecen al PR (parte técnica de la integrante A)
Estas **no** se atribuyen a la autora del PR.
- Los enlaces 404 (V16) y las cifras desactualizadas (V17) de `ENTREGA.md` proceden de texto anterior al PR #1, escrito por la parte técnica; la corrección de la ficha corresponde a quien mantiene esas filas.
- [`tests/test_calidad_plantillas.py:45`](../tests/test_calidad_plantillas.py) (`test_b_no_tiene_datos_precargados`) exige que el PSP de B esté vacío; fallaría cuando B registre su PSP. Como el paso "Pruebas sin red" del workflow ([`captura-diaria.yml:49`](../.github/workflows/captura-diaria.yml)) es obligatorio, bloquearía la captura. Pertenece a la parte técnica y debe ajustarse antes de que B suba su PSP.
- El PR #1 se fusionó sin revisión previa (proceso del equipo).

### Fuera de esta auditoría
No se evaluó el PSP de la integrante B (sigue vacío). El tiempo de esta revisión (30 min, estimado) está en el PSP de la auditora. **No se registraron defectos** en `defectos-integrante-a.csv`: las observaciones sobre el trabajo de la integrante B permanecen en este documento y no se convierten en defectos de la auditora; solo se registrarían allí defectos que la propia auditora hubiera introducido y corregido. La auditoría recíproca (la integrante B revisando los cambios de la integrante A) sigue **pendiente**. Esta revisión interna de E0 es distinta de la auditoría cruzada entre equipos de E2.
