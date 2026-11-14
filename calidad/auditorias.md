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
| 2 | Parte técnica de la integrante A: commits directos en `main` (`ef6d23b`, `156a024`, `2e76361`, `12b1df8`, `55bc6b4`), revisados en el estado de `6c151b0` | Integrante A (`Leslie581`) | Integrante B (`eimymuz`) | **Auditoría interna posterior** (commits directos en `main`, sin revisión previa) | 2026-11-09 | 5 mayores (3 nuevos, 2 existentes) y 13 menores (12 nuevos, 1 existente), sin críticos; detalle en [Auditoría 2](#auditoría-2-parte-técnica-de-a-auditoría-interna-posterior) | Pendientes (ningún commit de corrección todavía) | **Correcciones requeridas, sin aprobación definitiva** |
| 3 | PR #8 `e1/leslie-pipeline` (commit `70a26b9`; fusión `7e64ffa`) | Integrante A (`Leslie581`) | Integrante B (`eimymuz`) | **Revisión recíproca posterior a la fusión** (el PR #8 se abrió el 2026-11-13 06:47:15 UTC y se fusionó 68 s después, sin revisiones) | 2026-11-13 | 1 mayor de proceso, 1 menor de documentación, 6 riesgos y 8 observaciones; **ningún defecto técnico bloqueante**; detalle en [Auditoría 3](#auditoría-3-pr-8-pipeline-e1-revisión-recíproca-posterior) | Pendientes | **Aprobado técnicamente con correcciones menores**; la fusión ya ocurrió sin revisión previa |
| 4 | PR #10 `e1/leslie-l2` (commits `de42284`, `67b3b10`, `68d8aaa`; fusión `0c4a682`) | Integrante A (`Leslie581`) | Integrante B (`eimymuz`) | **Revisión recíproca posterior a la fusión** (se pidió como previa; el PR #10 se fusionó 37 s después de abrirse, sin revisiones) | 2026-11-13 | 1 mayor de proceso (recurrente; incluye el PR #9), 1 menor de documentación, 3 riesgos (2 de rúbrica, a cargo de la integrante B) y 6 observaciones; **ningún defecto técnico bloqueante**; detalle en [Auditoría 4](#auditoría-4-pr-10-l2-transformaciones-exploración-y-ci-revisión-recíproca-posterior) | Pendientes | **Aprobado técnicamente con correcciones menores**; la fusión ya ocurrió sin revisión previa |
| 5 | PR #11 `e1/leslie-calidad` (commit `809cfa3`; fusión `1712d17`) | Integrante A (`Leslie581`) | Integrante B (`eimymuz`) | **Revisión recíproca posterior a la fusión** (se pidió como previa; el PR #11 se fusionó 9 s después de abrirse, sin revisiones; el PR #12 de la integrante B, 13 s después) | 2026-11-13 | 1 mayor de proceso (recurrente: PR #8 a #12), 3 menores de documentación y 7 observaciones; **ningún defecto técnico bloqueante**; detalle en [Auditoría 5](#auditoría-5-pr-11-l3-requerimientos-fiabilidad-seguridad-y-plan-sqa-revisión-recíproca-posterior) | Pendientes | **Aprobado con correcciones menores**; la fusión ya ocurrió sin revisión previa |
| 6 | PR #12 `e1/eimy-cierre-estadistico` (commit `c47d4e4`; fusión `c7302f8`) | Integrante B (`eimymuz`) | Integrante A (`Leslie581`) | **Revisión recíproca posterior a la fusión** (se pidió como previa; el PR #12 se fusionó 13 s después de abrirse, sin revisiones) | 2026-11-13 | 1 mayor de proceso (recurrente) y 8 observaciones; **ningún defecto técnico bloqueante**; detalle en [Auditoría 6](#auditoría-6-pr-12-cierre-estadístico-de-b-revisión-recíproca-posterior) | Pendientes | **Aprobado técnicamente con observaciones menores**; la fusión ya ocurrió sin revisión previa |
| 7 | PR #15 `e1/eimy-tablero` (commits `80d8b5b` y `eb8f606`; fusión `ac9c88d`) | Integrante B (`eimymuz`) | Integrante A (`Leslie581`) | **Revisión recíproca posterior a la fusión** (se pidió como previa; el PR #15 se fusionó 11 s después de abrirse, sin revisiones) | 2026-11-14 (02:59 a 03:10 UTC) | 1 mayor de proceso (recurrente), 3 importantes y 5 observaciones; **ningún defecto técnico bloqueante**; detalle en [Auditoría 7](#auditoría-7-pr-15-cierre-del-tablero-de-b-revisión-recíproca-posterior) | Ver «Seguimiento de la Auditoría 7» | **Aprobado técnicamente con observaciones**; la fusión ya ocurrió sin revisión previa |
| 8 | PR #16 `e1/cierre-documental` (commits `4242ea5` y `7f8f315`; fusión `628136b`) y el commit posterior `372a6ab` de la misma rama | Integrante A (`Leslie581`) | Integrante B (`eimymuz`) | **Mixta:** `4242ea5` revisado **antes** de la fusión, pero el dictamen no llegó al PR; `7f8f315` revisado **después** (el PR #16 se fusionó 13 s después de abrirse, con 0 revisiones); `372a6ab` revisado **antes** de integrarse | 2026-11-13 (22:33 a 22:58, hora de la Ciudad de México) | 1 mayor de proceso (D1, recurrente), 3 menores de documentación | Pendientes (de A) | Aprobado técnicamente con observaciones menores |

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

## Auditoría 2: parte técnica de A, auditoría interna posterior
**Tipo:** auditoría **interna de E0, posterior** a los commits directos de la integrante A en `main` (`ef6d23b`, `156a024`, `2e76361`, `12b1df8`, `55bc6b4`). Se revisó el estado del repositorio en `6c151b0`. No se presenta como revisión previa a la integración y **no es** la auditoría cruzada entre equipos prevista para E2.
**Auditada:** integrante A (`Leslie581`). **Auditora:** integrante B (`eimymuz`), responsable de revisión de calidad de este conjunto de cambios. **Lista usada:** [`lista_verificacion_auditoria.md`](lista_verificacion_auditoria.md). **Fecha:** 2026-11-09. **Tiempo de revisión:** 40 minutos de revisión personal, **estimación retrospectiva**, registrados por la auditora en [`tiempo-integrante-b.csv`](tiempo-integrante-b.csv). No incluye las ejecuciones automáticas del asistente.
**Alcance:** DATATUR y DENUE, extracción y almacenamiento en bronce, histórico de 108 periodos, pruebas y reproducibilidad, bitácora de capturas, objetivos de calidad y documentación técnica de E0.
**Decisión:** **Correcciones requeridas, sin aprobación definitiva.** Es de la auditora; el asistente (Claude Code) reunió la evidencia.

**Origen de la evidencia:** **E** = ejecutado en esta revisión · **I** = inferido del código o de los documentos (no ejecutado) · **R** = reportado por la integrante A y no reproducido por la auditora.

### Resultados verificados
| Comprobación | Resultado | Origen |
|---|---|---|
| Integridad del bronce | 5 fichas `.meta.json`; SHA-256 y tamaño sin discrepancias | E |
| Privacidad del DENUE | 4 archivos JSON en `data/bronce/denue/`, ninguno con los campos personales o de domicilio excluidos | E |
| Histórico | Manzanillo: 108 periodos (2016-01 a 2024-12), sin huecos ni duplicados (año, mes, categoría) | E |
| Bitácora de capturas | 5 ejecuciones (2 éxitos, 1 fallo, 2 omitidas por duplicado), todas `workflow_dispatch` | E |
| Disponibilidad O1 | 2 de 3 = 66.7 %, por debajo del objetivo del 95 %. Es un **incumplimiento real** del objetivo, no un error de cálculo | E |
| Secretos y archivos privados | Historial completo: solo aparece el token ficticio de una prueba; sin `.env` ni credenciales versionados; sin datos del canal B de DATATUR ni crudos del DENUE en Git | E |
| Reglas éticas del extractor | `extractores/base.py`: pausa mínima de 1 s (línea 106), reintentos ≤ 5 (109), bloqueo ante 401/403 de robots.txt (136), `PermissionError` si robots.txt prohíbe la ruta (177) | I (lectura del código) |
| `tests/test_calidad_plantillas.py` | 4 aprobadas, 1 fallida (`test_b_no_tiene_datos_precargados`). Se ejecutaron las funciones directamente con Python porque `pytest` no está instalado en el equipo de la auditora | E |
| Suite completa (87 aprobadas, 2 omitidas) | No reproducida por la auditora | R (Auditoría 1, V17) |

### Limitaciones (no comprobado)
| Comprobación | Motivo |
|---|---|
| Suite completa de `pytest` | `pytest` no está instalado; no se instalaron dependencias |
| Ejecución de `python -m pipeline.verificar_e0` | Falta `pandas` en el equipo de la auditora; H2 se deduce del código y de la bitácora |
| Enlaces a GitHub Actions (V16) y color de cada ejecución | No se consultó GitHub en esta revisión |
| Ejecución programada (`schedule`) | El último commit revisado (`6c151b0`) es anterior a la primera ejecución programada posible |
| Variable `TDL_CONTACTO` en GitHub | Solo puede verse en la configuración del repositorio |
| Contenido real del `robots.txt` del INEGI | No está archivado en el repositorio (H11) |
| Pruebas con red (`TDL_RED=1`) | Requieren red y token |

### Hallazgos
Se revisaron con los archivos de `6c151b0`. "Existente" = ya registrado en la Auditoría 1 o documentado por la integrante A.

| # | Gravedad | Archivo y líneas | Descripción | Evidencia | Corrección recomendada | Responsable | Estado |
|---|---|---|---|---|---|---|---|
| H1 | Mayor | [`tests/test_calidad_plantillas.py:45-46`](../tests/test_calidad_plantillas.py) | `test_b_no_tiene_datos_precargados` exige que el PSP de B esté vacío. Con los registros de B, falla, y como el paso "Pruebas sin red" del workflow es obligatorio ([`captura-diaria.yml:49-52`](../.github/workflows/captura-diaria.yml)), detendría la captura diaria | E: la prueba falla con el PSP de B en la rama `e0/psp-auditoria-integrante-b` | Sustituirla por una validación de formato (fecha, fase válida, actividad no vacía; en filas retrospectivas, inicio, fin e interrupción vacíos y minutos > 0). Integrar el arreglo **antes** que el PSP de B | A | **Existente** (Auditoría 1), ahora reproducido |
| H2 | Mayor | [`pipeline/verificar_e0.py:177`](../pipeline/verificar_e0.py); `PENDIENTES_COMPANERA_E0.md:112` (archivo retirado de `main`; consta en la etiqueta `e0`); [`revision_calidad.md:14`](revision_calidad.md); [`lista_verificacion_auditoria.md`](lista_verificacion_auditoria.md) ("`verificar_e0` sin fallos") | Hay que distinguir dos cosas. (a) **Incumplimiento real:** la disponibilidad es de 66.7 % y O1 no se cumple; esto no es un error y debe seguir visible. (b) **Problema en el criterio de aceptación:** sin `--solo`, el verificador incluye la disponibilidad y termina con código 1, así que las instrucciones que piden "sin fallos" no pueden cumplirse mientras O1 no se alcance | I (código y bitácora); no ejecutado | Que la guía y las listas exijan, como control obligatorio, `--solo historico --solo integridad --solo privacidad`, y reporten la disponibilidad aparte como indicador. **No** marcar O1 como cumplido ni ocultarlo | A (código y guía) y equipo (listas) | Nuevo |
| H3 | Mayor | [`objetivos.md:7`](objetivos.md); [`verificar_e0.py:144-157`](../pipeline/verificar_e0.py); [`captura_denue.py:78-85`](../extractores/captura_denue.py) | O1 se define "en cualquier ventana de 7 días", pero el cálculo usa todas las ejecuciones. Mezcla ejecuciones manuales, programadas y forzadas, y la bitácora no registra si se usó `--forzar` (la ejecución `42733335021` fue un éxito después de dos omitidas el mismo día) | E (bitácora sin campo `forzar`) e I (código) | Registrar `forzar` en la bitácora; calcular O1 por ventana de 7 días y separar `schedule` de `workflow_dispatch`. Si cambia el método, dejar constancia sin cambiar el umbral | A | Nuevo |
| H4 | Menor | [`docs/fuentes/denue.md:9`](../docs/fuentes/denue.md) | Afirma que el contenido repetido se detecta por SHA-256, pero dos capturas con el mismo contenido tienen distinto hash, porque la API devuelve los registros en otro orden | E: los SHA-256 originales de `BuscarAreaAct` difieren (`4fa8…` frente a `22d9…`) y los registros son iguales como conjunto | Corregir la afirmación, u ordenar por `CLEE` antes de calcular el hash | A | Nuevo |
| H5 | Mayor | [`docs/E0/verificacion.md:10, 18, 22, 24`](../docs/E0/verificacion.md); [`migracion.md:4, 23, 25`](../docs/E0/migracion.md); [`fuentes/denue.md:35, 42`](../docs/fuentes/denue.md); [`fuentes/README.md:8`](../docs/fuentes/README.md); [`propuesta.md:62`](../docs/E0/propuesta.md); [`captura-diaria.yml:5`](../.github/workflows/captura-diaria.yml) | Cifras y estados desactualizados: "57 aprobadas" o "69 pruebas", privacidad `sin_datos`, captura real "PENDIENTE", "no hay ejecución real en GitHub" | E: hay 4 archivos DENUE reales y 5 ejecuciones en la bitácora; R: 87 aprobadas y 2 omitidas según A | Actualizar cifras y estados con la evidencia actual, distinguiendo lo verificado de lo reportado | A | Nuevo (la Auditoría 1 solo cubría `ENTREGA.md`) |
| H6 | Menor | [`calidad/README.md:13, 16`](README.md) | "Estado: plantillas vacías" (A ya tiene registros) y "renombren los archivos", que contradice "No renombres" de la guía; las pruebas dependen de esos nombres | E (lectura) | Actualizar el estado y quitar la instrucción de renombrar | A | Nuevo |
| H7 | Menor | [`calidad/README.md:24-25`](README.md) | "No se reconstruyen horas de memoria" y "el prototipo no se carga a estos registros", pero los dos PSP usan `[ESTIMADO RETROSPECTIVO]` y el de A incluye filas `[PROTOTIPO]` | E (lectura de los CSV) | Alinear las reglas con la práctica que permite la guía (estimaciones etiquetadas) o declarar la excepción | Equipo | Nuevo |
| H8 | Menor | [`objetivos.md:9`](objetivos.md) (O3b) y [`test_calidad_plantillas.py:40`](../tests/test_calidad_plantillas.py) | O3(b) exige minutos de corrección en el 100 % de los defectos, y la prueba exige que estén vacíos en el PSP de A: con la definición actual, O3(b) no puede cumplirse | E (lectura) | El equipo decide si redefine O3(b) o lo declara no cumplido, y deja constancia | Equipo | Nuevo |
| H9 | Menor | [`calidad/riesgos.md:8, 13, 14`](riesgos.md) | R2 dice "aún no se ha probado" (hay 5 ejecuciones). R7 dice "Entrevista pendiente" (se realizó mediante un colaborador externo; registro parcial). R8 pide "verificar con la primera captura real" (ya verificado) | E (bitácora, privacidad); documentos de la entrevista | Actualizar R2, R7 y R8 | A | Nuevo |
| H10 | Menor | [`README.md:12, 28`](../README.md) | "entrevista pendiente"; `laboratorio/` aparece solo como "notebooks (E1–E3)" y no menciona `laboratorio/encuesta_e0/` | E (lectura) | Actualizar ambas líneas | A | Nuevo |
| H11 | Menor | [`fuentes/denue.md:15`](../docs/fuentes/denue.md); [`ENTREGA.md:17`](../docs/E0/ENTREGA.md); [`captura-diaria.yml:140`](../.github/workflows/captura-diaria.yml) | La evidencia `robots_leido` del INEGI queda en `logs/bitacora.jsonl` (no versionado) y en un artefacto que se borra a los 30 días | I (configuración) | Archivar en el repositorio el resultado de la lectura de robots.txt (dominio, estado y fecha, sin token) | A | Nuevo |
| H12 | Menor | [`extractores/datatur.py:3, 20, 46, 93, 245`](../extractores/datatur.py) | Referencias a `docs/fuentes.md` y `evidencias/…`, que no existen en el repositorio; `permitir_espejo=True` por defecto recurre a un espejo no oficial; `pdfplumber` no está en `requirements.txt`. Ningún flujo ejecuta este código | E (lectura) | Corregir las referencias, usar `permitir_espejo=False` por defecto y declarar o retirar el código de PDF | A | Nuevo |
| H13 | Menor | [`extractores/denue.py:282`](../extractores/denue.py); [`captura_denue.py:101-103`](../extractores/captura_denue.py) | `CAMPOS_MINIMOS` incluye `nombre`; solo funciona porque la validación usa los registros sin sanitizar. Si se reordena el flujo, el control de esquema fallaría | I (código) | Documentar el acoplamiento o quitar `nombre` de los campos mínimos | A | Nuevo |
| H14 | Menor | [`captura_denue.py:7`](../extractores/captura_denue.py) frente a [`fuentes/denue.md:16`](../docs/fuentes/denue.md) | "5 solicitudes como máximo" frente a "2–3". Sin reintentos son 3 (robots, Cuantificar y una página); con reintentos, más | I (código) | Igualar las cifras | A | Nuevo |
| H15 | Menor | [`extractores/base.py:111`](../extractores/base.py) | Sin `TDL_CONTACTO`, el User-Agent dice "definir TDL_CONTACTO", y no se registra en fichas ni bitácora qué User-Agent se usó | I (código); configuración en GitHub no comprobada | Registrar el User-Agent usado en la bitácora de ejecuciones | A | Nuevo |
| H16 | Menor | [`captura_denue.py:101-115`](../extractores/captura_denue.py); [`captura-diaria.yml:122`](../.github/workflows/captura-diaria.yml) | Una captura que falla la validación pero pasa la verificación publica su bronce, y las ejecuciones siguientes de ese día se omiten como duplicadas aunque el día "falló" | I (código; caso no observado) | Que `captura_existente` exija una captura con resultado `exito`, o documentarlo | A | Nuevo |
| H17 | Mayor | [`ENTREGA.md:19, 39, 49`](../docs/E0/ENTREGA.md) | (a) Enlaces a Actions que devuelven 404. (b) "69 aprobadas". (c) "aún no hay commits" | (a) R: Auditoría 1, V16; no comprobado por la auditora. (b) R: la suite da 87 aprobadas y 2 omitidas según A; no reproducido. (c) E: `git log` muestra commits de las dos integrantes (`cb64a84`, `8d81922` de B) | Ya solicitado en la Auditoría 1 | A | **Existente** (V16 y V17) |
| H18 | Menor | [`captura-diaria.yml:37, 39, 129`](../.github/workflows/captura-diaria.yml); [`verificacion.md:40`](../docs/E0/verificacion.md) | Las acciones se referencian por etiqueta (`@v4`, `@v5`), no por SHA | E (lectura); la integrante A ya lo documentó como límite conocido | Opcional: fijarlas por SHA en E1 | A | **Existente** (límite documentado) |

**Recuento** (sin duplicidades): **5 mayores** (H1, H2, H3, H5, H17; de ellos, H1 y H17 son existentes) y **13 menores** (H4, H6 a H16, H18; H18 es existente). **Ningún hallazgo crítico**: no se encontraron datos personales, secretos ni datos sin permiso en Git.

### Correcciones solicitadas a la auditada (pendientes)
1. **H1** antes que cualquier otra corrección, para que el PSP de B pueda integrarse sin detener la captura diaria.
2. **H2 y H3:** criterio de aceptación del verificador y medición de O1, sin ocultar el incumplimiento actual.
3. **H5 y H17:** documentación de verificación y ficha de entrega.
4. Los hallazgos menores, en el orden que acuerde el equipo. H7 y H8 los decide el equipo.

### Fuera de esta auditoría
Esta auditoría no evalúa el trabajo de la integrante B (ver la Auditoría 1). **No se registraron defectos** en `defectos-integrante-b.csv`: los hallazgos sobre el trabajo de la integrante A quedan en este documento y no son defectos de la auditora.

## Seguimiento al cierre de E0 (2026-11-10, rama `e0/cierre-final`)
Estado de atención de las observaciones. **RESUELTA** = corregida y con archivo que lo respalda; **PARCIAL** = atendida en parte; **PENDIENTE** = sin cambios. Esta tabla no aprueba nada: solo informa. Las cuestiones "N" (no comprobables) y las cifras que dependen del CSV privado de la encuesta **siguen sin poder verificarse**.

### Auditoría 1 (integrante A revisa el PR #1 de la integrante B)
| Observaciones | Estado | Respaldo |
|---|---|---|
| V1 a V4: entrevista sin respuestas publicadas, aprendizajes del proceso, duración sin comprobante, consentimiento y validez sin confirmar | **PENDIENTE** | [`entrevista_01.md`](../docs/E0/Entrevistas/entrevista_01.md) no ha cambiado desde la auditoría |
| V5 y V6: dato geográfico de I10 y resguardo del CSV privado | **PENDIENTE** | [`LEEME.md`](../docs/E0/encuesta/LEEME.md) sin cambios |
| V7: referencia a la guía interna en el informe | **PARCIAL** | La guía lleva ahora un aviso de "superada" (`PENDIENTES_COMPANERA_E0.md` (archivo retirado de `main`; consta en la etiqueta `e0`)), pero el [informe](../docs/E0/encuesta/informe_encuesta_e0.md) la sigue citando |
| V8, V9, V11, V15, V18: cifras y estructura consistentes | Sin acción requerida | — |
| V10: error no controlado con entradas vacías | **PENDIENTE** | [`analisis_encuesta.py`](../laboratorio/encuesta_e0/analisis_encuesta.py) sin cambios |
| V12: guion preliminar innecesario (§8.3) | **RESUELTA** | Retirado de [`propuesta.md`](../docs/E0/propuesta.md) |
| V13: nombres del equipo | **RESUELTA** | [`propuesta.md`](../docs/E0/propuesta.md), [`ENTREGA.md`](../docs/E0/ENTREGA.md), [`revision_calidad.md`](revision_calidad.md) |
| V14: extensión de la propuesta | **PARCIAL** | De 2,824 a unas 1,730 palabras; la paginación exacta **no se pudo verificar** |
| V16 y V17: enlaces 404 y cifras desactualizadas de la ficha | **RESUELTA** | [`ENTREGA.md`](../docs/E0/ENTREGA.md) reescrita |

### Auditoría 2 (integrante B revisa la parte técnica de A)
| Hallazgos | Estado | Respaldo |
|---|---|---|
| H1: prueba que exige el PSP de B vacío | **RESUELTA** | [`test_calidad_plantillas.py`](../tests/test_calidad_plantillas.py) valida formato y coherencia (91 aprobadas, 2 omitidas) |
| H2: criterio de aceptación del verificador | **PARCIAL** | [`revision_calidad.md`](revision_calidad.md) y la [lista de verificación](lista_verificacion_auditoria.md) exigen ahora histórico, integridad y privacidad; falta alinear el texto de `verificar_e0.py` |
| H3: O1 por ventana de 7 días y registro de `--forzar` | **PENDIENTE** | Cambio de código y de método; se deja para E1 |
| H4: afirmación sobre detección de repetidos por SHA-256 | **PENDIENTE** | [`denue.md`](../docs/fuentes/denue.md) |
| H5: cifras y estados desactualizados | **PARCIAL** | Actualizados [`verificacion.md`](../docs/E0/verificacion.md), [`migracion.md`](../docs/E0/migracion.md), [`denue.md`](../docs/fuentes/denue.md), [`fuentes/README.md`](../docs/fuentes/README.md) y la [propuesta](../docs/E0/propuesta.md); el comentario de [`captura-diaria.yml`](../.github/workflows/captura-diaria.yml) línea 5 no se tocó |
| H6 y H7: reglas y estado en `calidad/README.md` | **RESUELTA** | [`calidad/README.md`](README.md) |
| H8: definición de O3(b) | **PENDIENTE** | Decisión del equipo |
| H9 y H10: riesgos y README desactualizados | **RESUELTA** | [`riesgos.md`](riesgos.md), [`README.md`](../README.md) |
| H11 a H16, H18: archivar robots.txt, referencias de `datatur.py`, acoplamiento de `nombre`, solicitudes por ejecución, User-Agent, captura fallida que se omite, acciones por SHA | **PENDIENTE** | Cambios de código o de configuración; ninguno bloquea E0 |
| H17: enlaces 404, "69 aprobadas", "aún no hay commits" | **RESUELTA** | [`ENTREGA.md`](../docs/E0/ENTREGA.md) |

## Auditoría 3: PR #8 (pipeline E1), revisión recíproca posterior
**Tipo:** revisión recíproca **posterior a la fusión**. El PR #8 (`e1/leslie-pipeline` → `main`, 1 commit `70a26b9`) se abrió el 2026-11-13 a las 06:47:15 UTC y `Leslie581` lo fusionó a las 06:48:23 UTC (`7e64ffa`), con **0 revisiones** (API pública de GitHub). La revisión empezó después (2026-11-13 00:46, hora de México), así que **no se presenta como control previo**. El contenido de `main` en `7e64ffa` es idéntico al del commit revisado (`git diff 70a26b9 7e64ffa` vacío), por lo que los resultados aplican a `main`.
**Auditora:** integrante B (`eimymuz`), con asistencia de Claude Code para ejecutar las verificaciones. **Lista usada:** [`lista_verificacion_auditoria.md`](lista_verificacion_auditoria.md), adaptada a E1. **Tiempo:** registrado por la auditora en [`tiempo-integrante-b.csv`](tiempo-integrante-b.csv).
**Alcance:** los 34 archivos del commit `70a26b9` frente a `28e1cad`. **Método:** lectura del código; ejecución en un *worktree* separado con las dependencias fijadas por la autora (`requirements.txt`, `requirements-lab.txt` y `requirements-dev.txt`; Python **3.14.3** local, porque 3.13 no está instalado en el equipo); recálculo **independiente** del oro desde el TSV de bronce, sin usar el código de la autora; inyección de fallas en **copias temporales** del bronce real (nunca en `data/bronce/`), recalculando el SHA-256 de la ficha para que actúen las reglas y no la verificación de integridad; e integración simulada de `e1/eimy-pronosticos` sobre `70a26b9` sin crear commits.

### Resultados verificados
| # | Punto revisado | Resultado | Evidencia |
|---|---|---|---|
| V1 | Pruebas de la autora | **156 aprobadas, 2 omitidas** (red) en Python 3.14.3; `ruff check .` sin hallazgos | `pytest -q -rs` sobre `70a26b9` |
| V2 | CI en GitHub | Las ejecuciones [43380739918](https://github.com/Leslie581/observatorio-turistico-colima/actions/runs/43380739918) (push) y [43381130865](https://github.com/Leslie581/observatorio-turistico-colima/actions/runs/43381130865) (pull_request) sobre `70a26b9` terminaron con **éxito en todos los pasos**: instalación de las tres listas de dependencias, ruff, pruebas, pipeline, verificador de E0 y `pip-audit` (Ubuntu, Python 3.13) | API pública de GitHub (`/actions/runs/{id}/jobs`) |
| V3 | Reproducibilidad | Regenerar con `python -m pipeline.ejecutar` (código 0) produce los tres CSV del oro **idénticos byte a byte** a los versionados; solo cambia `fecha_proceso_utc` en los dos `.meta.json` y en el resumen, como documenta `pipeline.md` §1 | `git diff` del *worktree* tras la ejecución |
| V4 | 108 meses y contrato §4.1 | 108 filas, de 2016-01 a 2024-12, ascendentes y sin huecos; las 20 columnas en el orden del contrato; UTF-8 sin BOM, LF y 6 decimales; `categorias_incluidas` = `2-5 estrellas`, `n_categorias_fuente` = 4, `version_contrato` = `1.0.0` | Script de cotejo independiente |
| V5 | Cociente de sumas, 2 a 5 estrellas | Recalculado desde el TSV sin el código de la autora: los conteos (`cuartos_*`, `llegadas_turistas`, `turistas_noche`) y los indicadores (`d_covid`, `d_oferta_2017`, `diag_atipico_iqr`) coinciden **exactamente**; los cocientes difieren ≤ 5.0e-7 (redondeo a 6 decimales). Frente al promedio simple de porcentajes la diferencia llega a 12.82 pp, así que el oro **no** es un promedio. `oro.py` además recalcula la fórmula al validar (líneas 127 a 129) | Script de cotejo independiente; [`pipeline/oro.py`](../pipeline/oro.py) |
| V6 | Sin pérdida silenciosa (Base70) | 31,147 leídas = 31,145 en plata + 2 en cuarentena (R-D06, Ciudad Juárez, filas 19587 y 22733); las 453 filas de Manzanillo llegan a plata; 1 faltante marcado (R-D07, Mexicali). Si la cuenta no cuadra, se detiene (`CUENTA`, `plata_datatur.py:186`) | `rechazados.csv` y `resumen_e1-e6c9a995c9ed.json` regenerados |
| V7 | Sin pérdida silenciosa (DENUE) | 670 leídos = 670 aceptados; 134 reemplazados por una captura posterior del mismo día, **contados como marcados** (no rechazados ni perdidos) | Resumen de cuarentena |
| V8 | Las 14 reglas con datos reales alterados | Cada falla inyectada produjo el efecto del contrato §2.3. **R-D01** (columna renombrada): se detiene el lote, sin plata ni oro. **R-D02** (mes 13), **R-D04** (negativo) y **R-D06** (ocupados > disponibles) en una fila de Manzanillo: la fila va a cuarentena y el oro **se detiene** con código 2 ("meses sin las 4 categorías", 2019-05) en vez de publicar un mes incompleto. **R-D03** (duplicado): se conserva la primera. **R-D05** (disponibles = 0, Cancún): la fila va a cuarentena. **R-D07** (faltante en Manzanillo): se marca y el oro se detiene (no se imputa). **R-E01** (CLEE vacío), **R-E03** (municipio 06001), **R-E04** (latitud 40) y **R-E06** (alta 2030-01): la fila va a cuarentena. **R-E02** (lote de 100 de 134): se rechaza el lote y se cuentan los 100 registros. **R-E05** (campo `Telefono`): incidente, se detiene todo sin salida. **R-D08**: informativo (El Fuerte, 96 periodos, en el resumen real) | Scripts de inyección en copias temporales |
| V9 | Fuga temporal | El oro no contiene transformaciones ajustadas con la serie. `d_covid` y `d_oferta_2017` son reglas de calendario. `diag_atipico_iqr` usa los 108 meses, incluido 2024, pero el contrato §4.1 y el diccionario lo declaran **solo diagnóstico, prohibido como regresor**, y el laboratorio no lo usa. `partir_entrenamiento_prueba` fija h = 12 y comprueba que todo el entrenamiento es anterior a la prueba | [`pipeline/interfaz.py`](../pipeline/interfaz.py), diccionario |
| V10 | Datos privados en el oro | `manzanillo_ocupacion_mensual.csv` es un agregado mensual público. `manzanillo_oferta_hospedaje.csv` no tiene CLEE, coordenadas, nombres, teléfonos, correos ni domicilios; "CLEE" solo aparece en el texto del diccionario y del `.meta.json`. Sin rutas locales ni nombres de usuario en `data/oro/` ni en el resumen | Búsqueda por patrones en `data/oro/*` y `data/cuarentena/resumen_*.json` |
| V11 | Cifras corregidas del contrato (revisión r1, §9) | Coinciden con un recálculo propio. Oferta: +30.5 % y +17.0 % diarios, +26.3 % y +13.2 % mensuales; 3,373 cuartos al día. COVID: 25.55 % frente a 49.39 %. Medias alrededor de 2017-11: 48.5 frente a 47.6 y 51.9 frente a 52.1. Correlaciones solo con entrenamiento: 0.191 / −0.022, 0.223 / 0.111, 0.650 / 0.516, 0.994; con rezago 1: 0.181, 0.102, 0.403. Las tres observaciones de la integrante B quedaron atendidas sin cambiar el esquema; mantener `1.0.0` está justificado | Script de cotejo |
| V12 | Interfaz y laboratorio | `cargar_oro_mensual` entrega `PeriodIndex` mensual, las columnas del contrato y `version_contrato` como texto. En la integración simulada, `python -m laboratorio.pronosticos.ejecutar --fuente oro` usa el oro y coincide con la derivación de referencia en las 12 columnas cotejadas (≤ 5.0e-7); mismo modelo elegido; métricas del SARIMA idénticas a 3 decimales; Holt-Winters cambia en el tercer decimal (RMSE 5.268 → 5.271) | *Worktree* de integración |
| V13 | Dependencias y CI para el laboratorio | `requirements-lab.txt` fija las mismas versiones que el laboratorio (statsmodels 0.15.0, scipy 1.18.1, matplotlib 3.11.2); `pip check` sin conflictos. `ci.yml` las instala y fija `TDL_EXIGIR_PRONOSTICOS=1`. En la integración simulada, con esa variable: **181 aprobadas, 2 omitidas** (solo red); las 25 pruebas de pronósticos **se ejecutan**. Con solo `requirements.txt` (como `captura-diaria.yml`): 156 aprobadas, 3 omitidas, una de ellas el módulo de pronósticos con su motivo explícito, **sin fallas que detengan la captura** | *Worktree* de integración; entorno con solo `requirements.txt` |

### Hallazgos
**Defectos**
| # | Severidad | Archivo y línea | Descripción | Evidencia |
|---|---|---|---|---|
| D1 | **Mayor (proceso)** | PR #8 | Fusionado 68 s después de abrirse, **sin revisión** de la otra integrante, aunque `plan_trabajo.md` §3 establece que "desde E1, todo cambio se integra por pull request revisado por la otra integrante". Repite la situación de E0 que esa regla buscaba evitar. No afecta al resultado técnico | API de GitHub: `created_at` 06:47:15Z, `merged_at` 06:48:23Z, 0 revisiones |
| D2 | Menor (documentación) | [`.github/workflows/ci.yml:4`](../.github/workflows/ci.yml), [`docs/E1/pipeline.md:71`](../docs/E1/pipeline.md) (y "No se probó la instalación desde cero en Linux ni en GitHub", §6), [`docs/E1/plan_trabajo.md:87`](../docs/E1/plan_trabajo.md) | Afirman "preparado, **sin ejecutar** en GitHub", pero hay dos ejecuciones exitosas sobre el mismo commit (V2). Era cierto al redactarse; quedó desactualizado al hacer push. [`tests/test_ci_workflow.py:46`](../tests/test_ci_workflow.py) exige el texto "SIN EJECUTAR", así que corregirlo requiere cambiar también la prueba | V2 |

**Riesgos**
| # | Riesgo | Propuesta |
|---|---|---|
| R1 | La revisión se hizo con Python 3.14.3; CI usa 3.13. Ya está cubierto para la rama de la autora (V2), pero el laboratorio de pronósticos **todavía no se ha ejecutado en CI** | Integrar `e1/eimy-pronosticos` por PR y confirmar en Actions que las 25 pruebas se ejecutan (sin el motivo "NO EJECUTADAS") |
| R2 | Control de aplicaciones de Windows: la autora documenta bloqueos intermitentes de DLL de statsmodels (`pipeline.md` §6). En el equipo de la auditora no ocurrió en esta sesión | Tomar CI (Linux) como referencia de validación |
| R3 | `ci.yml` regenera el oro, pero **no comprueba** que el regenerado sea igual al versionado; un oro editado a mano o desactualizado pasaría el CI | Añadir `git diff --exit-code -- data/oro/*.csv` después de `python -m pipeline.ejecutar` |
| R4 | Las capturas diarias de DENUE cambian el identificador de corrida (`id_corrida` incluye sus hashes): cada ejecución local con una captura nueva crea otro `resumen_<corrida>.json` versionable | Acordar cuándo se versiona un resumen nuevo |
| R5 | En `manzanillo_oferta_hospedaje.csv`, 3 de las 22 celdas por fecha tienen **un solo establecimiento** (p. ej., "Hoteles con otros servicios integrados", 101 a 250 personas). El DENUE es público y nominativo, así que el riesgo de reidentificación es bajo, pero el agregado no protege esas celdas | Documentarlo, o agrupar celdas con menos de 3 establecimientos si el tablero lo publica |
| R6 | La gestión de duplicados conserva la primera aparición aunque sea inválida (V8; contrato §2.3 "se conserva la primera"). Si la primera copia falla R-D04 y la segunda es válida, ambas van a cuarentena: no es silencioso (se cuentan) y en Manzanillo detiene el oro, pero en otros centros se pierde un registro válido | Ver O1 |

**Observaciones**
| # | Observación |
|---|---|
| O1 | R-D03 y R-E01: considerar "conservar la primera copia **válida**" en una versión futura del contrato (comprobado con una inyección: duplicado cuya primera copia tiene un negativo) |
| O2 | R-E02 usa CLEE **únicos** / `Cuantificar` ([`reglas_denue.py`](../pipeline/calidad/reglas_denue.py), `r_e02_completitud`); el contrato §2.3 dice "Total de registros / `Cuantificar`". Hoy coinciden (134 = 134); difieren solo si hay CLEE repetidos, que R-E01 ya manda a cuarentena |
| O3 | El resumen de una corrida fallida por R-D01 no tiene la cuenta `leidos` de Base70 (el lote se rechaza antes de leerlo), conforme al contrato §3 ("solo el resumen y el motivo") |
| O4 | `requirements-lab.txt` (de la autora) y `laboratorio/pronosticos/requirements-pronosticos.txt` (de la auditora) fijan las mismas tres versiones: tras integrar debe quedar una sola fuente. Corresponde a la auditora retirar o redirigir el suyo |
| O5 | El esquema `pandera` del oro y la validación de la interfaz rechazan correctamente un oro incompleto: detectaron que un oro **simulado** de las pruebas de la auditora no cumplía el contrato (ver "Integración") |
| O6 | El contrato §0 afirma diferencias "menores de 1e-6" entre oro y derivación §7: medido, 4.92e-7 |
| O7 | `pipeline.md` §3 declara honestamente qué reglas tienen 0 rechazos reales y solo pruebas sintéticas; esta auditoría las ejerció con datos reales alterados (V8) |
| O8 | Las fechas (`fecha_captura_local`) y la regla de un día local por captura se comportan como el contrato §2.2: 5 capturas → 4 días, 536 filas de plata |

### Integración con `e1/eimy-pronosticos` (defectos de la rama B, no de la autora)
La integración simulada (`git merge --no-commit` en un *worktree* temporal; sin conflictos) mostró **dos defectos en la rama de la auditora**. Los registra la auditora como propios en [`defectos-integrante-b.csv`](defectos-integrante-b.csv) (9 y 10):
1. `tests/test_laboratorio_pronosticos.py`: 4 errores **E402** con el `ruff.toml` de la autora. Las importaciones van después de la comprobación de dependencias a propósito; el `# noqa: E402` lo había quitado una corrección automática de ruff ejecutada con otra configuración.
2. `test_carga_oro_simulado_valida_contra_referencia` falló: el oro simulado de la prueba llenaba columnas con 0, y la interfaz real lo rechaza por el esquema. Se reconstruyó un oro simulado válido contra el contrato y se altera de forma coherente (conteos y cociente) para comprobar que el cotejo contra la fuente lo detecta. `derivar_referencia` y `comparar_con_referencia` cotejan ahora 12 columnas (antes 6).
Corregidos en el árbol de trabajo de `e1/eimy-pronosticos` (**sin commit** al cierre de esta auditoría). Con la corrección, la integración da ruff limpio y 181 aprobadas; la rama sola, 116 aprobadas y 2 omitidas.

### Correcciones solicitadas a la autora
1. **D2:** actualizar `ci.yml:4`, `pipeline.md` §6 y `plan_trabajo.md` §4 con el estado real de CI (enlazar las ejecuciones 43380739918 y 43381130865) y ajustar `tests/test_ci_workflow.py:46`.
2. **D1:** para lo que falta de E1, esperar la revisión de la otra integrante antes de fusionar.
3. **R3** (recomendada): comprobar en CI que el oro regenerado es igual al versionado.

### Dictamen
**No hay defectos técnicos bloqueantes.** La puerta de calidad aplica las 14 reglas del contrato; el pipeline no pierde filas en silencio; el oro tiene los 108 meses del contrato, calcula la ocupación como cociente de sumas de 2 a 5 estrellas, no contiene datos privados ni transformaciones con fuga; y la interfaz es compatible con el laboratorio. Habría recomendado **autorizar la fusión** con las correcciones menores D2 y R3 como seguimiento. El PR **ya estaba fusionado** sin revisión (D1), así que este dictamen es una **validación posterior** de `main` en `7e64ffa`, no una aprobación previa.

## Auditoría 4: PR #10 (L2: transformaciones, exploración y CI), revisión recíproca posterior
**Tipo:** revisión recíproca **posterior a la fusión**. Se pidió como revisión previa, pero el PR #10 (`e1/leslie-l2`, commits `de42284`, `67b3b10` y `68d8aaa`) se abrió el 2026-11-13 a las 07:56:18 UTC y `Leslie581` lo fusionó a las 07:56:55 UTC (`0c4a682`), 37 s después, con **0 revisiones** (API pública de GitHub). La revisión empezó después (02:01, hora de México) y **no se presenta como control previo**. Los resultados aplican a `main` en `0c4a682`.
**Auditora:** integrante B (`eimymuz`), con asistencia de Claude Code para ejecutar las verificaciones. **Tiempo:** en [`tiempo-integrante-b.csv`](tiempo-integrante-b.csv).
**Alcance:** los 26 archivos que cambian entre `49934ca` (`main` tras el PR #9) y `0c4a682`. **Método:** lectura del código; ejecución en un *worktree* separado de `0c4a682` con `requirements.txt`, `requirements-lab.txt` y `requirements-dev.txt` (Python 3.14.3 local); recálculo **propio** de los parámetros desde el oro; pruebas negativas de `verificar_oro` (con un commit temporal desprendido, local y no publicado); y consulta de Actions en la API pública.

### Resultados verificados
| # | Punto | Resultado | Evidencia |
|---|---|---|---|
| V1 | Pruebas, linter y puertas en `main` | `TDL_EXIGIR_PRONOSTICOS=1 pytest -q -rs`: **220 aprobadas, 2 omitidas** (solo red); `ruff check .` sin hallazgos; `pipeline.ejecutar`, `pipeline.verificar_oro` y `pipeline.verificar_e0 ... --exigir-datos` con código 0 | *Worktree* de `0c4a682` |
| V2 | CI en GitHub | Ejecuciones con éxito en todos los pasos, incluido el nuevo "El oro regenerado coincide con el oro versionado": [43388517052](https://github.com/Leslie581/observatorio-turistico-colima/actions/runs/43388517052) (push `68d8aaa`), [43389344704](https://github.com/Leslie581/observatorio-turistico-colima/actions/runs/43389344704) (pull_request) y [43389413267](https://github.com/Leslie581/observatorio-turistico-colima/actions/runs/43389413267) (`main`, `0c4a682`) | API pública de Actions |
| V3 | **(1) Ajuste solo con 2016–2023** | Los 8 parámetros publicados en `parametros_transformaciones.json` (mín. 1.459077, máx. 66.339892, μ 44.751796, σ 12.765878, terciles 41.754661 y 51.357863, bordes de ancho igual 23.086015 y 44.712954) coinciden **exactamente** con un recálculo propio que usa solo los 96 meses de entrenamiento (`n = 96`, `ajustado_hasta = 2023-12`). Con los 108 meses serían distintos (μ 45.86, σ 12.54, primer tercil 43.73). El z-score de 2024 es igual a (x − μ<sub>ent</sub>) / σ<sub>ent</sub>, con media 0.78 (no 0, así que no se recalculó). `ajustar_*` rechaza cualquier mes posterior a 2023-12 (`ErrorFuga`, [`transformaciones.py:57-71`](../pipeline/transformaciones.py)); `aplicar_*` no recalcula | Recálculo propio |
| V4 | **(2) Gráficas y estadísticas desde el oro** | `explorar.py` lee solo `cargar_oro_mensual` (líneas 24 a 26 y 277); no lee plata ni bronce. `estadisticas_descriptivas.csv` coincide con el oro (media 45.86; desviación de 2024 5.13). Regenerada en una carpeta temporal, la exploración produce los **10 archivos idénticos byte a byte**, incluidos los 4 PNG | Ejecución con `--salida` temporal y `cmp` |
| V5 | **(3) Comparación del oro regenerado** | `verificar_oro` compara con `git show HEAD:` y se comportó como documenta en 6 casos. Falla (código 2) si se altera un dígito del oro regenerado, si cambia un campo no temporal del `.meta.json` (`filas`), si el diccionario no se regenera, o si el oro **versionado** se edita a mano y el pipeline regenera el correcto. Pasa (código 0) si solo cambian `fecha_proceso_utc` y `corrida`, o si cambia la oferta DENUE, que se excluye a propósito | Pruebas negativas en el *worktree* |
| V6 | **(4) Conflictos con el laboratorio de pronósticos** | Ninguno: el PR #10 no modifica archivos de la integrante B. El cambio en `tests/test_calidad_plantillas.py` solo afecta al PSP de la integrante A. En `main`, `python -m laboratorio.pronosticos.ejecutar --fuente oro` reproduce todas las tablas y figuras versionadas (solo cambia la hora en `ejecucion.json`); sus 25 pruebas se ejecutan en CI | *Worktree* de `0c4a682` |
| V7 | **(5) Reducción por agregación** | Cifras verificadas desde el bronce: Manzanillo 453 → 108 filas (−76.2 %); las 432 de 2 a 5 estrellas → 108 (−75.0 %); Base70 en plata 31,145 → 108 (−99.65 %). Se declara lo que se pierde (detalle por categoría, otros destinos). Cumple el texto citado del requisito ("muestreo, agregación o selección de variables, con el porcentaje de reducción logrado y lo que se pierde") | Recálculo propio; [`transformaciones.md`](../docs/E1/transformaciones.md) §6 |
| V8 | Cifras de `transformaciones.md` §3 y §4 | Coinciden con un recálculo propio: 2024 en min-max 0.671 a 0.923 y en z-score 0.02 a 1.30; niveles de 2024 9 `alto` y 3 `medio` (frecuencia) y 12 `alto` (ancho); entrenamiento 32/32/32 y 6/33/57; mediana 48.11 → 0.72; z mínimo −3.39; asimetría −1.13 | Recálculo propio |

### Hallazgos
**Defectos**
| # | Severidad | Archivo y línea | Descripción | Evidencia |
|---|---|---|---|---|
| D1 | **Mayor (proceso, recurrente)** | PR #10 y PR #9 | El PR #10 se fusionó 37 s después de abrirse, sin la revisión previa que se había pedido. Además, el **PR #9** (rama `e1/eimy-pronosticos`, trabajo de la integrante B) lo **abrió y fusionó la integrante A en 12 s** (07:26:49 → 07:27:01 UTC), con 0 revisiones, 0 comentarios y sin registro en este archivo, y sin la autorización de fusión de la integrante B. Con el PR #8 (Auditoría 3, D1) son tres fusiones seguidas sin revisión, contra `plan_trabajo.md` §3 | API de GitHub: `pulls/9`, `pulls/10` y sus `reviews` |
| D2 | Menor (documentación) | [`docs/E1/pipeline.md:77`](../docs/E1/pipeline.md), [`docs/E1/plan_trabajo.md:87`](../docs/E1/plan_trabajo.md) (y línea 3: "fase L2 en la rama") | Afirman que la comprobación del oro "aún no ha corrido en GitHub", pero ya pasó en las tres ejecuciones de V2, y la fase L2 ya está en `main`. Es el mismo patrón que la Auditoría 3 (D2): el texto se escribió antes del push | V2 |

**Riesgos de cumplimiento de la rúbrica (compartidos)**
| # | Riesgo | Responsable y propuesta |
|---|---|---|
| R1 | **Comparación min-max frente a z-score "con análisis comparativo"** sobre un método: no está hecha. Sin ella, el criterio "Normalización, discretización y reducción" (15 pts) queda incompleto. `transformaciones.md` §7 la asigna, con razón, a la integrante B, y ya no está bloqueada | **Integrante B:** implementarla en `laboratorio/pronosticos/` con `pipeline.transformaciones`, ajustando los parámetros con 2016–2023 |
| R2 | **Gráfica de descomposición** (tendencia, estacionalidad, residuo): no existe en ninguno de los dos laboratorios. La integrante B tiene la descomposición numérica y la justificación aditiva (`pronostico.md` §2.2), pero no la figura que pide la evidencia esperada del criterio "Caracterización y descomposición" | **Integrante B** (la descomposición es suya): añadir la figura a `laboratorio/pronosticos/` sin duplicar las cuatro de la exploración |
| R3 | La oferta DENUE versionada no se compara en CI (por diseño, V5); al acumularse capturas en bronce, `manzanillo_oferta_hospedaje.csv` puede quedar desactualizado sin que nada lo avise | Regenerarla al cerrar E1, o documentar su fecha de corte |

**Observaciones (menores)**
| # | Observación |
|---|---|
| O1 | [`transformaciones.md:31`](../docs/E1/transformaciones.md) compara desviaciones **muestrales** (12.83 con COVID y 8.62 sin COVID, `ddof=1`), mientras que el z-score usa la **poblacional** (σ = 12.7659, `ddof=0`, tabla del §2). Ambas cifras son correctas; conviene decir cuál es cuál |
| O2 | La reducción (V7) se documenta como medición puntual; `transformaciones.md:56` deja pendiente si el pipeline debe imprimirla en cada corrida. Con la evidencia actual el requisito queda cubierto; automatizarla es opcional |
| O3 | Jerarquías conceptuales y discretización supervisada: cobertura parcial, declarada por la autora (`transformaciones.md` §7) |
| O4 | `plan_trabajo.md` §4 dice que en la exploración "faltan la descomposición y la correlación cruzada". La correlación cruzada sí existe en el laboratorio de la integrante B (`correlacion_cruzada.csv`, `pronostico.md` §2.5); solo falta la figura de descomposición (R2) |
| O5 | La afirmación de reproducibilidad de los PNG (`exploracion.md` §0) se confirmó también en otra versión de Python (3.14.3) con la misma versión de matplotlib |
| O6 | Las gráficas usan la paleta propia de la autora y las del laboratorio la suya; para el informe final conviene unificar los colores de COVID y del periodo de prueba |

### Dictamen
**No hay defectos técnicos bloqueantes.** Las transformaciones ajustan sus parámetros solo con 2016–2023 (comprobado contra un recálculo propio), las gráficas y estadísticas salen solo del oro, la comprobación del oro regenerado funciona en CI y detecta los cambios que debe detectar, no hay conflictos con el laboratorio de pronósticos, y la reducción por agregación cumple el requisito citado. Habría recomendado **autorizar la fusión**, con D2 y O1 como correcciones menores. El PR ya estaba fusionado sin revisión: este dictamen es una **validación posterior** de `main` en `0c4a682`. D1 es un defecto de proceso **recurrente** (tres PR seguidos, uno de ellos con trabajo de la integrante B) que el equipo debe atender antes de la etiqueta `e1`. R1 y R2 son pendientes de la integrante B para completar la rúbrica.

### Seguimiento de la Auditoría 4 (2026-11-13, rama `e1/eimy-cierre-estadistico`)
| Hallazgo | Estado | Evidencia |
|---|---|---|
| R1: comparación min-max frente a z-score | **Atendido por la integrante B** (pendiente de revisión de la integrante A) | `laboratorio/pronosticos/escalamiento.py`; [`pronostico.md`](../docs/E1/pronostico.md) §2.7 |
| R2: gráfica de descomposición | **Atendido por la integrante B** (pendiente de revisión de la integrante A) | `laboratorio/pronosticos/resultados/figuras/descomposicion_oro.png`; `pronostico.md` §2.6 |
| D1, D2, R3, O1 a O6 | Pendientes (autora: integrante A) | — |

## Auditoría 5: PR #11 (L3: requerimientos, fiabilidad, seguridad y plan SQA), revisión recíproca posterior
**Tipo:** revisión recíproca **posterior a la fusión**. Se pidió como revisión previa, pero el PR #11 (`e1/leslie-calidad`, commit `809cfa3`) se abrió el 2026-11-13 a las 08:37:41 UTC y `Leslie581` lo fusionó a las 08:37:50 UTC (`1712d17`), **9 s** después, con 0 revisiones. A las 08:38:33 UTC fusionó también el PR #12 (`e1/eimy-cierre-estadistico`, trabajo de la integrante B; `c7302f8`), 13 s después de abrirlo, con 0 revisiones (API pública de GitHub). La revisión empezó unas 6 horas después (08:40 hora de México, 14:40 UTC); los resultados aplican a `main` en `c7302f8`.
**Auditora:** integrante B (`eimymuz`), con asistencia de Claude Code para ejecutar las verificaciones. **Tiempo:** en [`tiempo-integrante-b.csv`](tiempo-integrante-b.csv).
**Alcance:** los 13 archivos que cambian entre `0c4a682` y `809cfa3`. **Método:** lectura; ejecución en un *worktree* de `c7302f8` (Python 3.14.3); recálculo propio de las cifras de fiabilidad desde la bitácora; cotejo con la API pública de GitHub (Actions y la release de `gitleaks`); búsqueda de patrones de secretos en las líneas agregadas. **No** se descargó ni se ejecutó `gitleaks`.

### Resultados verificados
| # | Punto | Resultado | Evidencia |
|---|---|---|---|
| V1 | Pruebas, linter y puertas en `main` | Las 16 pruebas nuevas (`test_fiabilidad.py` 12, `test_requerimientos.py` 4) aprobadas. Suite con `TDL_EXIGIR_PRONOSTICOS=1`: **243 aprobadas, 2 omitidas** (red). `ruff check .` sin hallazgos. `pipeline.ejecutar`, `pipeline.verificar_oro` y `pipeline.verificar_e0 ... --exigir-datos` con código 0 | *Worktree* de `c7302f8` |
| V2 | **(1) 36 requerimientos** | 12 RF + 24 RNF; cada uno con requerimiento, criterio medible, método de verificación y estado con evidencia. Recuento por estado comprobado a mano y por la prueba: 26 cumplidos, 5 parciales, 3 no cumplidos, 1 pendiente, 1 propuesto. Los nuevos de E1 están marcados como PROPUESTO. Cifras comprobadas: RNF-PRI-03 (12 celdas con 1 establecimiento y 28 con menos de 3 en 88), RNF-INT-02 (5 de 5 capturas con 134), RF-06 (4.9e-7) | Lectura; recálculo propio |
| V3 | **(2) Plan SQA frente a la rúbrica** | Contiene los apartados que el PDF enumera para IEEE 730: propósito y alcance (§1), roles (§2), estándares y métricas (§3), pruebas (§4), revisiones y auditorías (§5), reporte de problemas y acciones correctivas (§6), herramientas (§8), control de versiones (§9) y riesgos (§10), más criterios de aceptación de la entrega (§7) | Lectura de [`plan_sqa.md`](../docs/E1/plan_sqa.md) |
| V4 | **(3) Fiabilidad: cifras** | Recalculado desde la bitácora (8 registros, SHA-256 `d16dfd92…e855`, igual al del informe): 6 válidas (5 éxitos, 1 fallo; 2 omitidas por duplicado) → **5/6 = 83.33 %**; incidente del 2026-11-10 00:39:33 cerrado por el éxito que termina a las 00:44:01 → **MTTR 268 s**; ventana **2.84 días**. `python -m pipeline.fiabilidad` regenera `fiabilidad_e1.json` **idéntico byte a byte** | Recálculo propio |
| V5 | **(3) Fiabilidad: interpretación** | Correcta. El 83.3 % se presenta como **tasa de éxito** y se dice expresamente que no es la disponibilidad; el MTTR, como una observación (n = 1); MTBF y A como no estimables, sin valores supuestos; O1 "no cumplido en lo observado y no evaluable" (2.84 de 7 días) | [`fiabilidad.md`](../docs/E1/fiabilidad.md) |
| V6 | Cotejo con Actions | La API lista **5** ejecuciones de `captura-diaria.yml`, todas `success`, presentes en la bitácora. Los 3 `run_id` 42729922838, 42730477358 y 42732765759 responden **404**. Las tres `schedule` se crearon a las 20:28, 20:11 y 20:48 UTC: retrasos de 431, 414 y 451 min frente al cron `17 13 * * *` | API pública |
| V7 | **(4) Origen de `gitleaks` 8.30.1** | La release `v8.30.1` existe, publicada el 2026-03-21 02:17:58 UTC por `zricethezav`, no es *prerelease* ni borrador. `gitleaks_8.30.1_windows_x64.zip` mide 8,438,883 bytes y su SHA-256 `d29144de…2afc4e` coincide con `checksums.txt` y con el *digest* de GitHub, como afirma [`seguridad.md`](../docs/E1/seguridad.md) §3.1 | API de releases y `checksums.txt` |
| V8 | **(5) Compatibilidad con el laboratorio** | El PR #11 no toca archivos de la integrante B. En `main`, `python -m laboratorio.pronosticos.ejecutar --fuente oro` regenera resultados idénticos a los versionados (salvo la hora de `ejecucion.json`). RF-09 y RNF-REP-04 describen correctamente el laboratorio | *Worktree* de `c7302f8` |
| V9 | **(6) Archivos privados, secretos y cambios inesperados** | Solo cambian `calidad/`, `docs/E1/`, `pipeline/fiabilidad.py` y dos pruebas; **ningún cambio** en `data/`, flujos de trabajo, `requirements*.txt`, laboratorios ni extractores. En las 939 líneas agregadas hay 0 correos, rutas locales, tokens de GitHub o AWS, claves privadas, contraseñas o asignaciones de `INEGI_TOKEN`. La única coincidencia con forma de UUID es el marcador `AAAAAAAA-BBBB-…` de `seguridad.md` §3.3, que describe la estructura del valor de relleno, no un valor real. Sin archivos `.env`, de `evidencias_privadas/` ni credenciales | Búsqueda por patrones sobre `git diff 0c4a682 809cfa3` |

### Hallazgos
**Defectos**
| # | Severidad | Archivo y línea | Descripción | Evidencia |
|---|---|---|---|---|
| D1 | **Mayor (proceso, recurrente)** | PR #11 y PR #12 | El PR #11 se fusionó **9 s** después de abrirse, sin la revisión previa que se pidió; el PR #12 (trabajo de la integrante B), 13 s después, sin revisión ni autorización de fusión de su autora. Son **cinco PR seguidos** (#8 a #12) sin revisión previa. El propio plan lo reconoce como no cumplido (O6, Q1, RNF-MAN-03), pero la práctica no cambió. Según `plan_sqa.md` §7 (criterios 5 y 7), la etiqueta `e1` exige revisiones registradas o la excepción declarada en la ficha | API de GitHub: `pulls/11`, `pulls/12` y sus `reviews` |
| D2 | Menor (documentación) | [`docs/E1/plan_sqa.md:37`](../docs/E1/plan_sqa.md) | La fila **O7** tiene 3 columnas en una tabla de 4: falta el `|` entre "0 hallazgos abiertos" y el estado, así que la tabla se muestra mal | Conteo de separadores |
| D3 | Menor (documentación) | [`docs/E1/plan_sqa.md:125`](../docs/E1/plan_sqa.md) (riesgo Q2) | Atribuye a la rúbrica "los 2 incidentes que pide". La rúbrica pide **7 días de bitácora**; el mínimo de 2 incidentes para el MTBF es una regla metodológica de la autora (`fiabilidad.py`, `MINIMO_INCIDENTES_MTBF`). Puede inducir a error a quien evalúe | `fiabilidad.md` cita la rúbrica (pág. 25) sin ese requisito |
| D4 | Menor (documentación desactualizada por fusiones posteriores) | [`requerimientos.md:36`](../docs/E1/requerimientos.md) (RF-09: "25 pruebas"; hoy 32), `:50` y `:84` (RNF-FIA-04 y RNF-MAN-03 citan solo #8 a #10), [`plan_sqa.md:36`](../docs/E1/plan_sqa.md) (O6), `:66` ("Revisión de L2 por B: No registrada"; la Auditoría 4 ya está en `main` desde `c7302f8`) y `:124` (Q1) | Eran ciertas al escribirse; dejaron de serlo con los PR #11 y #12 | `git log`, API |

**Observaciones**
| # | Observación |
|---|---|
| O1 | **El MTBF sí tiene un estimador con un solo fallo.** Con el tiempo de operación T = 245,075 s (2.84 días menos la reparación) y r = 1, el estimador de máxima verosimilitud es T/r = **68.1 h**, con un intervalo de confianza del 90 % (χ², prueba truncada por tiempo) de **14.4 h a 55 días**; A puntual = 0.99891 (0.99484 con la cota inferior). Declararlo "no estimable" es una decisión defendible y está bien documentada, pero la rúbrica pide magnitudes "medidas". Se sugiere publicar la estimación **con su intervalo** junto con la advertencia de que no es estable, en lugar de omitirla. Es una decisión del equipo, no un error |
| O2 | **El MTTR y la diferencia entre 83.3 % y 100 % dependen solo de registros no verificables.** El fallo (`42729922838`) y el éxito que lo cierra (`42730477358`) son dos de los tres `run_id` que dan 404. `fiabilidad.md` §4 declara los tres registros no cotejables, pero no dice que **los dos extremos del único incidente** están entre ellos. Con solo los registros verificables, la tasa sería 4/4. No se propone cambiar la cifra (la bitácora es la fuente definida), sino hacer explícita esa dependencia |
| O3 | El resultado "0 hallazgos" de `gitleaks` es una ejecución local cuyo reporte no se versiona: el origen del binario se pudo verificar (V7), pero el resultado no lo puede comprobar un tercero. Se sugiere versionar un resumen sin valores (versión, commit escaneado, número de hallazgos) o integrar el trabajo de CI de §3.4, aún no probado |
| O4 | `fiabilidad_e1.json` quedará desactualizado con la siguiente ejecución del bot (hoy, hacia las 20:00 UTC). Lleva el SHA-256 de la bitácora para detectarlo, pero CI no lo comprueba. Conviene regenerarlo antes de la etiqueta `e1` |
| O5 | RNF-REP-04 (PARCIAL) pide que alguien distinto de la autora regenere los resultados del laboratorio. Esta auditoría los regeneró idénticos, pero la auditora **es** la autora: no cuenta para ese criterio |
| O6 | Las pruebas nuevas están bien planteadas: `test_requerimientos.py` valida el recuento contra las filas (lo que confirma V2), y `test_fiabilidad.py` usa un corte fijo de 8 registros reales, así que no se romperá cuando crezca la bitácora |
| O7 | Las 9 ejecuciones de `ci.yml` citadas en RNF-FIA-03 y O5 son una foto; hoy hay más (todas en éxito, incluida la del PR #12, [43392852374](https://github.com/Leslie581/observatorio-turistico-colima/actions/runs/43392852374)) |

### Dictamen
**No hay defectos técnicos bloqueantes. Recomendación: aprobar con correcciones menores** (D2, D3 y D4) y considerar O1 a O4 antes de la etiqueta `e1`. Los 36 requerimientos son verificables y su recuento es correcto. El plan SQA cubre la estructura de IEEE 730 que pide el PDF. La interpretación de fiabilidad es correcta y conservadora (83.3 % como tasa de éxito, MTTR de 268 s como observación con n = 1, MTBF y A no estimables con la regla declarada). La evidencia del origen de `gitleaks` 8.30.1 es verificable, y sus limitaciones están bien declaradas. Las pruebas nuevas pasan y no hay conflictos con el laboratorio. No hay secretos, archivos privados ni cambios inesperados. El PR ya estaba fusionado: este dictamen es una **validación posterior** de `main` en `c7302f8`. **D1 sigue siendo el problema principal de E1**: cinco PR seguidos sin revisión previa, incluido uno con trabajo de la integrante B fusionado sin su autorización.

### Respuesta de la autora (A) a la Auditoría 5 (2026-11-13, rama `e1/cierre-documental`)
Redactada por la autora del PR #11; **no modifica el texto de la auditora**. «Corregido» significa corregido **en la rama** `e1/cierre-documental`, **sin commit ni fusión a `main` todavía**; nada se da por cerrado hasta que la corrección esté en `main`.
| Hallazgo | Estado | Evidencia |
|---|---|---|
| D1: cinco PR sin revisión previa | **Abierto.** Acción correctiva y excepción de E1 **propuestas** (no implementadas); protección de `main` **no configurada** (la API pública devuelve `protected: false`) | [`plan_sqa.md`](../docs/E1/plan_sqa.md) §5.1 |
| D2: fila O7 con un separador faltante | **Corregido en la rama** | `plan_sqa.md` §3.1 |
| D3: el mínimo de 2 incidentes no es de la rúbrica | **Corregido en la rama** (criterio metodológico interno) | `plan_sqa.md` Q2; [`fiabilidad.md`](../docs/E1/fiabilidad.md) §2 |
| D4: cifras y listas desactualizadas | **Corregido en la rama**, y vuelto a actualizar con las cifras del 2026-11-13 (21 ejecuciones de CI, PR #7 a #14, 6/7 de tasa de éxito) | `requerimientos.md`, `plan_sqa.md`, `plan_trabajo.md`, `pipeline.md` |
| O1: estimar el MTBF con un fallo | **Atendido en la rama**: cálculo verificado y presentado solo como estimación exploratoria, con intervalo y supuestos; con el corte del 13 de noviembre: MTBF 91.7 h (IC 90 %: 19.3 h a 74.5 días), A 0.9992, igual a la disponibilidad observada por tiempo | `fiabilidad.md` §3.1; `pipeline/fiabilidad.py` y `tests/test_fiabilidad.py` |
| O2: extremos del incidente no corroborados | **Atendido en la rama** (se dice expresamente) | `fiabilidad.md` §4 |
| O3: resultado de `gitleaks` no comprobable por un tercero | **Atendido en la rama**: resumen y reportes versionados, sin secretos ni rutas; sigue siendo una ejecución local y `gitleaks` **no está en CI** | `calidad/evidencia/`; [`seguridad.md`](../docs/E1/seguridad.md) §3.2 |
| O4: `fiabilidad_e1.json` se desactualiza | **Parcial**: regenerado con la captura del 13 de noviembre (20:28 UTC); **abierto** hasta la etiqueta | `fiabilidad.md` §6 |
| O5: reproducción del laboratorio por alguien distinto de la autora | **Atendido por la Auditoría 6** (A regeneró los resultados de B, con tolerancia entre entornos) | Auditoría 6, V7; `requerimientos.md` RNF-REP-04 |
| O6, O7 | Informativos. **La cifra de O7 cambió:** al 2026-11-13 23:20 UTC `ci.yml` suma 21 ejecuciones (17 en éxito, 1 cancelada, **3 fallidas**) | `plan_sqa.md` §6 |
**Hallazgo nuevo de la autora, no incluido en la Auditoría 5:** **el CI de `main` está en rojo desde `06452fd`** (fusión del PR #14, el tablero). Las 3 ejecuciones fallidas son del commit `9489dc5`; por reproducción local, una prueba del tablero (`test_no_hay_secretos_ni_archivos_temporales_en_el_tablero`) falla cuando existe `__pycache__` en `tablero/`. No se leyeron los registros de Actions. **Sin corregir en `main`:** la integrante B publicó una corrección en la rama remota `e1/eimy-tablero` (`80d8b5b`), aún sin fusionar. Detalle en `plan_sqa.md` §6.

## Auditoría 6: PR #12 (cierre estadístico de B), revisión recíproca posterior
**Tipo:** revisión recíproca **posterior a la fusión**. Se pidió como revisión previa a la fusión, pero el PR #12 (`e1/eimy-cierre-estadistico`, commit `c47d4e4`) se abrió el 2026-11-13 a las 08:38:20 UTC y se fusionó a las 08:38:33 UTC (`c7302f8`), **13 s después, con 0 revisiones** (API pública de GitHub). No se presenta como control previo.
**Autora:** integrante B (`eimymuz`). **Auditora:** integrante A (`Leslie581`), con asistencia de Claude Code para ejecutar las verificaciones (la asistencia no cuenta como revisión independiente). **Tiempo de la auditora:** **no registrado** en `tiempo-integrante-a.csv` (lo confirma la integrante A).
**Alcance:** los 18 archivos de `c47d4e4` frente a su padre `0c4a682`. **Método:** `git diff`, lectura del código y de la documentación, ejecución en un *worktree* desacoplado en `c47d4e4` (Python 3.13.15, dependencias fijadas del proyecto), recálculo **independiente** del k-NN y de la descomposición, prueba de fuga con el oro real y comparación con `main`. Ninguna rama de la autora se modificó ni se integró.

### Resultados verificados
| # | Punto pedido | Resultado | Evidencia |
|---|---|---|---|
| V1 | **(1) Usa las funciones de `pipeline/transformaciones.py`** | **Sí.** `escalamiento.py` llama a `tr.ajustar_minmax`, `tr.ajustar_zscore`, `tr.aplicar_*` y `tr.invertir_*`; no reimplementa ninguna fórmula. No modifica `pipeline/` | Líneas 24, 50-61 y 131-138; el commit no toca `pipeline/` |
| V2 | **(2) Parámetros sin datos de 2024** | **Sí.** Los 10 parámetros (5 variables × 2 escalas) tienen `n = 84` y `ajustado_hasta = 2023-12` (84 = 2017-01 a 2023-12; 2016 solo aporta los rezagos de 12 meses). El candado `ErrorFuga` rechaza cualquier ajuste con 2024 | `escalamiento_parametros.json`; la prueba `test_escala_rechaza_ajuste_con_2024` |
| V3 | **(2) Prueba de fuga con el oro REAL** | Se **triplicó todo 2024** y se volvió a ejecutar `comparar_knn`: parámetros de escala, `k` elegido (7, 5, 5) y validación 2023 **idénticos**; el pronóstico de 2024-01 es idéntico; el de 2024-02 cambia (usa el valor observado de enero como rezago, que es el diseño a un paso) | Script propio, en el *worktree* |
| V4 | **(3) La selección de k no usa información de prueba** | **Correcto.** `elegir_k` ajusta la escala y la memoria con 2017-01 a 2022-12 y mide el error en 2023, con k ∈ {1, 3, 5, 7, 9} y menor RMSE (empates: menor k). No ve 2024. Luego reajusta con 2017-2023 | `escalamiento.py:71-82`; V3 (k idéntico al alterar 2024) |
| V5 | **(4) Recálculo independiente del k-NN** | Con solo `numpy`/`pandas` y el oro (sin su código ni mis funciones): mismos `k` (7, 5, 5), **mismas métricas de 2024** (MAE, RMSE y MAPE, diferencia máxima 5.0e-7, por el redondeo de sus CSV a 6 decimales) y **mismos pronósticos mensuales** (4.3e-7). Todos los vecinos de 2024 son meses ≤ 2023-12 | Script propio |
| V6 | **(4) Diseño temporal** | Válido para pronóstico **a un paso**: la memoria son solo meses de entrenamiento (nunca hay un vecino del futuro), los rezagos son t−1 y t−12 y los parámetros no ven 2024. **Limitaciones** en O1 y O2 | V3 y V5 |
| V7 | **(4) Reproducibilidad** | Dos ejecuciones completas del laboratorio (23 y 24 s): **idénticas byte a byte** (salvo la hora de `ejecucion.json`). Los 3 CSV y el JSON nuevos de k-NN y la figura de descomposición coinciden **byte a byte con lo versionado** aun con otra versión de Python (3.13.15 frente a 3.14.3). Ver O3 para los resultados previos | Doble corrida y `sha256` |
| V8 | **(5) Descomposición con los 108 meses** | `descomposicion_componentes.csv` tiene 108 filas (2016-01 a 2024-12); `observado` es igual al oro (diferencia 0); la clásica (`seasonal_decompose`, aditiva, periodo 12) y la STL robusta coinciden con `statsmodels` directo (≤ 5e-7); la clásica tiene 12 meses sin tendencia ni residuo (6 + 6) y la STL 0; ambas son aditivas (observado = T + E + R). Las cifras de §2.6 de `pronostico.md` (fuerzas, desviaciones, residuo mínimo −27.8 y −44.7 en 2020-04, tendencia de 2020-01) coinciden con sus CSV | Recálculo propio |
| V9 | **(5) La descomposición no decide nada** | Es **descriptiva** (incluye 2024); su resultado va solo al CSV, la figura y `resumen.json`; las decisiones (aditiva, d, D) siguen saliendo del entrenamiento (`descomponer`) | `ejecutar.py` paso 7 |
| V10 | **(6) Las métricas previas de SARIMA no cambian** | `resumen.json`: **0 claves quitadas y 0 modificadas**; solo se agregan `comparacion_escalas` y `descomposicion_completa_oro`. `comparacion_modelos_2024.csv`, `pronostico_modelo_elegido.csv`, `candidatos_aicc.csv` y los demás CSV previos **no figuran en el commit**. La fila «sin escalar» del control (MAE 2.376157, RMSE 2.638843, MAPE 4.363464) es idéntica a la del SARIMA de la tabla principal | `git diff` y cotejo de JSON |
| V11 | **(8) Sin archivos privados ni efecto en el oro** | `gitleaks` 8.30.1 sobre solo ese commit: 0 hallazgos. Sin rutas locales, usuarios ni correos en lo agregado. El único binario es `descomposicion_oro.png` (sin metadatos de texto ni rutas). **No toca** `data/`, `pipeline/`, `.github/` ni los requisitos | `git diff --name-only` y `gitleaks git --log-opts` |
| V12 | Pruebas y CI | En `c47d4e4` aislado: **227 aprobadas, 2 omitidas** (red); sus pruebas pasan de 25 a **32** (las 7 nuevas pasan; 5 simuladas y 2 con datos reales); `ruff` limpio. Su CI en GitHub: éxito en push (43392852374) y pull request (43394795003). En `main` (`c7302f8`, con el PR #11 de la integrante A): **243 aprobadas, 2 omitidas**, `ruff`, verificador E0, `pipeline.ejecutar` y `pipeline.verificar_oro` en verde; CI de `main` en éxito (43394817663) | Ejecución propia y API de Actions |

### Hallazgos
**Defectos bloqueantes: ninguno.**
| # | Severidad | Descripción | Evidencia |
|---|---|---|---|
| D1 | **Mayor (proceso, recurrente)** | El PR #12 se fusionó 13 s después de abrirse, sin revisión; el PR #11 (L3, integrante A) se fusionó 9 s después de abrirse, sin revisión. Con los PR #8, #9 y #10 eran **cinco fusiones seguidas sin revisión previa** al momento de la revisión. **Verificado después (2026-11-13, API pública):** el PR #7 (15 s), el #13 (Auditoría 5 de B, 25 s) y el #14 (tablero, 19 s) repiten la práctica, de modo que **los ocho PR de E1 (#7 a #14) se fusionaron sin revisión previa**, contra `plan_trabajo.md` §3. No afecta al resultado técnico, pero impide que esta revisión sea un control previo | API de GitHub: `pulls/7`, `pulls/11`, `pulls/12`, `pulls/13`, `pulls/14` y sus `reviews` (0) |

**Observaciones (menores, no bloqueantes)**
| # | Observación | Propuesta |
|---|---|---|
| O1 | **La validación de k usa un solo año (12 puntos) y el orden se invierte en la prueba:** en 2023 escalar fue mejor (RMSE 5.24 y 5.86 frente a 6.64) y en 2024 fue mejor no escalar (2.99 frente a 4.79 y 5.13). La autora lo reconoce («no hay un ganador estable») y no recomienda una escala. Con esa validación, la elección de k es ruidosa | Mantener la lectura prudente. Opcional: una validación de origen móvil (varios años) si se quiere sostener una conclusión |
| O2 | **El diseño a un paso supone el dato real de t−1 al pronosticar t.** El contrato §4.1 dice que el rezago mínimo operativo de Base70 **no está verificado**. La autora ya aclara que estos errores no son comparables con los del §4 (1 a 12 pasos), pero no menciona ese supuesto de disponibilidad | Añadir una frase en `pronostico.md` §2.7: es una comparación de escalas, no un modelo candidato para el cliente |
| O3 | **Los resultados versionados se generaron con Python 3.14.3 y el CI usa 3.13.** En mi entorno (3.13.15) las métricas **previas** varían hasta 0.0011 (MAE/RMSE/MAPE de `comparacion_modelos_2024.csv`), 0.0038 (AICc), 0.0022 (pronósticos) y, en el control, 0.0087 pp en la diferencia máxima; ningún orden ni conclusión cambia, y no lo introduce este commit. `ejecucion.json` ya registra las versiones | Documentar la tolerancia entre entornos (≈ 1e-2) en la sección de reproducibilidad, o regenerar los resultados con la versión del CI |
| O4 | **Cifras de la autora verificadas:** σ² de la serie min-max ≈ 0.0089 (dice ≈ 0.01); Θ estacional −0.987 en mi entorno frente a −0.981 en el suyo (el mismo fenómeno de O3: el óptimo local de min-max es sensible al entorno) | Ninguna; refuerza su explicación de que la diferencia de min-max es numérica |
| O5 | **Figura `descomposicion_oro.png`:** la leyenda del primer panel roza la curva observada en 2020-04 y el eje del primer panel dice «pp» aunque es un porcentaje | Cosmético |
| O6 | **PSP de la integrante B:** 5 filas nuevas con horarios exactos (02:01 a 02:23, 19 min en total; coherentes con las marcas de GitHub de ese día), etiquetadas `[ASISTIDO POR CLAUDE CODE]`, y los defectos 11 a 13 con 1 minuto de corrección cada uno. Las reglas del proyecto piden que el tiempo registrado sea **personal**, no el de la herramienta; la actividad de 6 minutos para la revisión recíproca del PR #10 y la de 6 minutos para implementar `escalamiento.py` merecen que la autora confirme que reflejan su tiempo | Confirmar con la integrante B; no se modifica su registro |
| O7 | **Defectos 11 a 13 y la Auditoría 4:** justificados. El defecto 12 se confirma en el *diff* (el README decía que la descomposición era de la integrante A y quedó falso al agregar §2.6). El «Seguimiento de la Auditoría 4» marca R1 y R2 como atendidos y **pendientes de revisión de A**: con esta revisión pueden pasar a «atendido y revisado» | Actualizar esas dos filas al trasladar este borrador |
| O8 | `escalamiento.py` importa funciones privadas de `modelos.py` (`_a_timestamp`, `_sarimax`); es un acoplamiento menor | Opcional: exponerlas con nombre público |

### Dictamen
**Aprobado técnicamente, con observaciones menores.** El cierre cumple los ocho puntos revisados: usa las funciones comunes de transformación, ajusta sus parámetros solo con el entrenamiento, elige k sin ver 2024, tiene un diseño temporal válido para un paso y resultados reproducibles, descompone los 108 meses correctamente, no modifica ninguna métrica previa, y no introduce archivos privados ni toca el oro. **No hay defectos bloqueantes** y no se recomienda revertir la fusión. El defecto de proceso D1 (fusiones sin revisión previa) debe atenderse antes de la etiqueta `e1`.

### Seguimiento de la Auditoría 6 (2026-11-13, rama `e1/cierre-documental`)
| Hallazgo | Estado | Evidencia |
|---|---|---|
| D1 | **Abierto** (ocho PR sin revisión previa); excepción **propuesta** | `plan_sqa.md` §5.1 |
| O1 (validación de k con un solo año) | **Aceptada**: `pronostico.md` §2.7 ya dice que no hay un ganador estable | `pronostico.md` §2.7 |
| O2 (supuesto de disponibilidad del dato de t−1) | **Corregido en la rama** por la integrante A **a petición expresa** de la integrante A y en un archivo de la integrante B; **B debe revisarlo** | `pronostico.md` §2.7 |
| O3 (diferencias numéricas entre versiones de Python) | **Corregido en la rama** (misma salvedad): tolerancia de trabajo 1·10⁻² y mayor diferencia observada 0.0086 | `pronostico.md` §8 |
| O4 | **Informativo** | — |
| O5, O6, O8 | **Abiertos** (de B): figura, confirmación de los tiempos del PSP de B y funciones privadas importadas | — |
| O7 (R1 y R2 de la Auditoría 4) | **Pendiente**: las filas del seguimiento de la Auditoría 4 las actualiza B; esta auditoría **revisó** R1 y R2 | Auditoría 4, «Seguimiento» |

## Auditoría 7: PR #15 (cierre del tablero de B), revisión recíproca posterior
**Tipo:** revisión recíproca **posterior a la fusión**. Se pidió como revisión previa, pero cuando se hizo el PR #15 (`e1/eimy-tablero`, commits `80d8b5b` y `eb8f606`) ya estaba en `main`: se abrió el 2026-11-14 a las 02:52:18 UTC y se fusionó a las 02:52:29 UTC (`ac9c88d`), **11 s después, con 0 revisiones**, desde la cuenta `Leslie581` (API pública de GitHub). No se presenta como control previo y no se simula que lo fuera.
**Autora:** integrante B (`eimymuz`). **Auditora:** integrante A (`Leslie581`), con asistencia de Claude Code para ejecutar las verificaciones (la asistencia no cuenta como revisión independiente). **Tiempo de la auditora:** forma parte del cierre documental, cuyo tiempo **aún no se registra** en `tiempo-integrante-a.csv`.
**Alcance:** los 8 archivos de `06452fd` a `ac9c88d` (+423 −29 líneas): `tablero/cargador.py`, `graficas.py`, `streamlit_app.py`, `tests/test_tablero_app.py`, `tests/test_tablero_cargador.py`, `docs/E1/tablero.md` y los dos registros PSP de B. **Método:** `git diff`; clon limpio de `ac9c88d` con Python 3.13.15, las dependencias del CI más las del tablero (`pip check` sin conflictos) y `__pycache__` presente; pruebas negativas con archivos sensibles añadidos a propósito; recálculo independiente de filtros, métricas e intervalos desde los CSV; lectura de la URL pública en el navegador integrado; API de GitHub (pull requests y ejecuciones de Actions). Ninguna rama de la autora se modificó.

### Resultados verificados
| # | Verificación | Resultado |
|---|---|---|
| V1 | La prueba que dejó el CI de `main` en rojo (`test_no_hay_secretos_ni_archivos_temporales_en_el_tablero`) con `tablero/__pycache__` presente | **Pasa.** Clon de `ac9c88d` con las dependencias del CI y del tablero: 291 aprobadas, 2 omitidas (red), `ruff` sin errores |
| V2 | Detección de archivos sensibles | Un `.env`, `.log` o `.bak` **versionado** (`git add -f`) hace fallar la prueba; un `.streamlit/secrets.toml` o un `.txt` con `INEGI_TOKEN=` sin ignorar también. La versión anterior **nunca detectaba `.env`** (`Path('.env').suffix` es vacío); ahora se revisa por nombre. No se debilitó: se añadieron `.pyo`, `.swp`, `.DS_Store` y `secrets.toml`. Un archivo ignorado por Git que existe en el disco **no se marca**, porque no se publicaría |
| V3 | Filtros históricos | Recalculados desde `data/oro/manzanillo_ocupacion_mensual.csv`: 108 (todo), 48 (2016–2019), 16 (covid) y 42 (recuperación) meses con las mismas medias, mínimos y máximos. Enero y febrero de 2020 solo aparecen en «Toda la serie» (está documentado) |
| V4 | Métricas del SARIMA | MAE 2.3762, RMSE 2.6388 y MAPE 4.3635, **idénticos** a `comparacion_modelos_2024.csv` y a lo recalculado desde `pronostico_modelo_elegido.csv`; 12 de 12 meses dentro del intervalo |
| V5 | Proyección 2025 | Media anual 54.62 %; semiancho del intervalo de 12.1 a 21.3 puntos (el texto dice «±12 a ±21»); ningún valor observado en 2025 |
| V6 | PSP de B | Solo se **agregaron** 8 líneas (7 intervalos y el defecto 14); no se modificó ni borró nada anterior. Los 23 intervalos de E1 no se solapan (118 min calculados de inicio y fin; el cálculo es de A, no de B) |
| V7 | Conflictos con la rama `e1/cierre-documental` | Ninguno: ningún archivo del PR coincide con un cambio local de A. Con los cambios de A copiados sobre `ac9c88d`: 314 aprobadas, 2 omitidas, `ruff` sin errores |
| V8 | CI de `main` | `ac9c88d` terminó en **éxito** (ejecución 43548657495). El rojo de `06452fd` quedó corregido por `eb8f606` |

### Hallazgos
**Mayor (de proceso)**
- **D1. El PR se fusionó sin revisión previa.** 11 s después de abrirse y con 0 revisiones. Con los PR #7 a #14, **son nueve PR de E1 sin revisión previa** (#7 a #15), contra `plan_trabajo.md` §3. Es el defecto recurrente D1 de las Auditorías 3 a 6.

**Importantes**
- **D2. La URL pública no sirve la versión nueva.** El 2026-11-14 a las 03:09:35 UTC (17 min después de la fusión) la aplicación de https://tdl-turistico-colima.streamlit.app **no mostraba** el filtro «Antes del COVID», el resumen ejecutivo ni las fechas clave, y **conservaba** la frase que `80d8b5b` reemplazó. A las 02:59:33 UTC pasaba lo mismo. No se pudo ver qué rama configuró Streamlit Cloud (requiere la cuenta propietaria). `docs/E1/tablero.md` dice que la aplicación se redespliega sola al cambiar la rama configurada: **no está demostrado**.
- **D3. Las pruebas de la aplicación no corrían en CI.** `tests/test_tablero_app.py` usaba `pytest.importorskip` y `ci.yml` no instalaba `tablero/requirements.txt`: 19 pruebas se omitían. Ya lo reconocía `tablero.md` §10.
- **D4. El defecto que rompió el CI de `main` no figura en ningún PSP.** El defecto 14 de B es otro (un `import`). La prueba que falló con `__pycache__` llegó en `9489dc5`, cuyo autor en Git es la integrante A; quién lo registra lo decide la integrante A (no se agregó nada al CSV).

**Observaciones**
- **O1.** `.env.example` se marcaba como no publicable (falso positivo).
- **O2.** `inventario_publicable()` omite la prueba si `git` no está disponible (en CI sí lo está).
- **O3.** `docs/E1/tablero.md`: decía 27 pruebas del cargador (hay 29), usaba el nombre anterior del repositorio en los pasos de despliegue y afirmaba «HTTP 200 sin pedir inicio de sesión» (con `curl` sin cookies hay redirecciones; un navegador sí carga la página).
- **O4.** Los intervalos del PSP de B del 13 de noviembre son muy cortos para lo que describen (p. ej., 20:08–20:10 cubre el filtro, las métricas y el resumen ejecutivo). **Los confirma B**; no se modificaron.
- **O5.** La frase «95 de cada 100 casos» simplifica la lectura del intervalo de predicción; va matizada con «no es una garantía». Informativa.

### Dictamen
**Aprobado técnicamente con observaciones.** El código, las cifras y la prueba corregida son correctos. La fusión ocurrió sin revisión previa y la URL pública no refleja la versión integrada.

### Seguimiento de la Auditoría 7 (2026-11-14, rama `e1/cierre-documental`)
«Corregido en la rama» significa que el cambio existe en `e1/cierre-documental` y se comprobó localmente, **sin commit ni fusión a `main` todavía**. Nada se da por cerrado hasta que esté en `main`.
| Hallazgo | Estado | Evidencia |
|---|---|---|
| D1 | **Abierto.** La acción correctiva y la excepción de E1 siguen sin implementarse; `main` no tiene protección (`protected: false`) | [`plan_sqa.md`](../docs/E1/plan_sqa.md) §5.1 |
| D2 | **Cerrado (2026-11-14, 04:25 UTC):** la titular reconfiguró el despliegue desde `main` (Python 3.13); la URL sirve la versión integrada (filtro de periodo, resumen ejecutivo, fechas clave) y las seis pestañas abren sin errores | [`ENTREGA.md`](../docs/E1/ENTREGA.md), «Tablero» |
| D3 | **Corregido en la rama:** `ci.yml` instala `tablero/requirements.txt`, fija `TDL_EXIGIR_TABLERO=1` (sin las dependencias las pruebas fallan) y la caché cubre ese archivo. Comprobado localmente; **ya se ejecutó en GitHub: ejecución 43557153021 de `ci.yml` sobre `4242ea5`: éxito en `calidad`, `auditoria-dependencias`, `bloqueo-tablero` y `secretos`** | `.github/workflows/ci.yml`, `tests/test_ci_workflow.py`, `tests/test_tablero_app.py` |
| D4 | **Resuelto en la rama:** por el historial de Git el commit `9489dc5` es de la integrante A y lo corrigió B en `eb8f606`; se registró como **defecto 22** en `defectos-integrante-a.csv` (sin minutos) | [`psp-e1-integrante-a-respaldo.md`](psp-e1-integrante-a-respaldo.md) |
| O1 | **Corregido en la rama:** una plantilla `.env.example`, `.env.sample` o `.env.template` se permite solo si cada variable está vacía o lleva un marcador evidente; con un valor real, un prefijo de credencial o una cadena larga, la prueba falla (y solo imprime el nombre de la variable). `.env`, `.env.local`, `.env.production` y similares siguen rechazados | `tests/test_tablero_cargador.py` |
| O2, O5 | Informativas | — |
| O3 | **Corregido en la rama** por la integrante A, **en un archivo de B** (B debe revisarlo) | `docs/E1/tablero.md` |
| O4 | **Abierta** (de B) | `calidad/tiempo-integrante-b.csv` |
| Nota | Los textos «el CI de `main` está en rojo» de la respuesta a la Auditoría 5 y de las Auditorías 5 y 6 eran verdaderos en su fecha de corte y se conservan; hoy el CI de `main` está en verde en `ac9c88d` | Ejecución 43548657495 |

## Auditoría 8: PR #16 (cierre documental de A) y commit posterior `372a6ab`, revisión recíproca con cronología mixta
**Tipo:** revisión recíproca de la integrante B sobre el cierre documental de la integrante A. **No fue una revisión previa completa:** una parte se hizo antes de la fusión y otra después (cronología abajo). El PR #16 (`e1/cierre-documental`, commits `4242ea5` y `7f8f315`) se abrió el 2026-11-14 a las 04:38:45 UTC y se fusionó a las 04:38:58 UTC (`628136b`), **13 s después, con 0 revisiones** (API pública de GitHub), desde la cuenta `Leslie581`.
**Autora:** integrante A (`Leslie581`). **Auditora:** integrante B (`eimymuz`), con asistencia de Claude Code para ejecutar las verificaciones (la asistencia no cuenta como revisión independiente). **Tiempo personal de la auditora:** **no registrado**; B no indicó cuánto tiempo dedicó personalmente y no se estima (las horas de la cronología son las de la sesión asistida, no tiempo personal de B).
**Alcance:** `4242ea5` (73 archivos, +5,082 −227 frente a `main` en `f8811ac`), `7f8f315` (10 documentos, +42 −42) y `372a6ab` (21 archivos, +205 −95), además del commit `f8811ac` de A en `main` (`.devcontainer/devcontainer.json`). **Método:** `git diff`; lectura de requerimientos, rúbrica, relatoría, `ENTREGA.md`, plan SQA, ruta de E2 y discretización; *worktree* desacoplado en `4242ea5` con la réplica local del CI (Windows, Python 3.14.3, dependencias fijadas); línea base SHA-256 de los resultados tomada antes de revisar; recuento independiente de estados y de pruebas; API pública de GitHub para el PR y las ejecuciones.

### Cronología real (hora de la Ciudad de México, UTC−6; marcas de archivos y de Git)
| Hora | Hecho | Respecto de la fusión del PR #16 |
|---|---|---|
| 22:26 | Línea base SHA-256 de los 28 resultados versionados de `laboratorio/` y `data/oro/` en `main` (`f8811ac`) | Antes |
| 22:32:21 | A crea `4242ea5` | Antes |
| 22:33:02 | La rama aparece en el remoto; empieza la revisión de `4242ea5` | Antes |
| 22:33 a 22:37:33 | Revisión de `4242ea5` y réplica local del CI (terminó a las 22:37:33). El dictamen («aprobado técnicamente con observaciones menores» y seis correcciones) se entregó **a B** en ese intervalo | Antes, pero **el dictamen no llegó a A ni al PR** |
| 22:37:03 | A crea `7f8f315` | Antes |
| 22:38:45 y 22:38:58 | Se abre y se fusiona el PR #16 (`628136b`), sin revisiones | — |
| 22:39 a 22:41 | Revisión de `7f8f315` | **Después** |
| 22:53:19 | A crea `372a6ab` en `e1/cierre-documental` (no está en `main` al cierre de esta auditoría) | — |
| 22:54 a 22:58 | Revisión de `372a6ab` y sus pruebas | **Antes de integrarse** |

### Resultados verificados
| # | Verificación | Resultado |
|---|---|---|
| V1 | Las transformaciones nuevas no alteran el laboratorio | De los 28 resultados de la línea base, **27 idénticos byte a byte** en `4242ea5`; el único distinto, `data/oro/diccionario_datos.csv`, solo **agrega** 18 líneas (0 borradas). `7f8f315` y `372a6ab` no tocan `laboratorio/pronosticos/` ni `data/`. Pronóstico, métricas y tablero sin cambios |
| V2 | Réplica local del CI sobre `4242ea5` | `ruff` sin hallazgos; **402 aprobadas, 2 omitidas** (red); cobertura **84.03 %** (piso 75 %); `pipeline.ejecutar`, `pipeline.verificar_oro` y el verificador de E0 con código 0. Coincide con lo que reporta A |
| V3 | CI en GitHub | `4242ea5`: ejecución 43557153021, éxito en `calidad`, `secretos`, `bloqueo-tablero` y `auditoria-dependencias`. `7f8f315`: 43557547843, éxito. `main` tras la fusión (`628136b`): 43557697492, éxito |
| V4 | Siete requerimientos nuevos (RF-13 a RF-15, RNF-SEG-06 a RNF-SEG-08 y RNF-MAN-04) | Cada uno es necesario, medible, verificable y rastreable, con su limitación declarada. Cifras cotejadas: bloqueo de 34 paquetes y 946 hashes; manifiesto del bronce de 28 archivos y 3,345,350 bytes; pruebas: 17, 12, 15, 8 y 24. RF-13 decía 13 pruebas y son **16** (corregido en `372a6ab`) |
| V5 | Recuento de estados de `requerimientos.md` | Recuento independiente: **35 cumplidos, 3 parciales, 4 no cumplidos, 1 propuesto** (43). `evaluacion_rubrica.md` decía 34 y 4 (corregido en `372a6ab`) |
| V6 | Discretización supervisada | Cortes ajustados solo con 2016–2023; objetivo de calendario (no circular); el criterio MDL acepta solo uno de los dos cortes y se declara; **no generaliza a 2024** (exactitud 0.50 frente a 0.75) y no se presenta como mejor método. El valor p (0.002) era el mínimo alcanzable con 500 permutaciones: `372a6ab` lo reporta como 1/501 con el límite de resolución explícito. Interpretación y limitaciones correctas |
| V7 | Evaluación de las rúbricas | Prudente: separa lo implementado, lo comprobado en local y lo ejecutado en GitHub, y se declara autoevaluación, no calificación |
| V8 | Relatoría | Los 118 min en 23 intervalos de B son correctos (recalculados de inicio y fin). En `372a6ab` la autoría de `9489dc5` sigue a Git (A) y se aclara la hora local frente a UTC |
| V9 | Cambios de A en archivos de B | `pronostico.md` §2.7 (alcance del k-NN y supuesto del dato de t−1), §8 (tolerancia entre Python 3.13 y 3.14), `tablero.md` y las pruebas del tablero (`.env.example` solo sin credenciales; `TDL_EXIGIR_TABLERO`): **correctos**. Atienden las Auditorías 6 (O2, O3) y 7 (O1, O3) |
| V10 | `f8811ac` (devcontainer) | Usaba Python 3.11 (el CI usa 3.13), instalaba `streamlit` sin versión fijada y desactivaba CORS y XSRF. **Los tres puntos quedan resueltos en `372a6ab`** (3.13, instalación desde el bloqueo con `--require-hashes` y protecciones por defecto) |
| V11 | `7f8f315` | Solo documentación: registra la ejecución 43557153021. Es un reemplazo mecánico que dejó una frase contradictoria (m2) |
| V12 | `372a6ab` | Atiende las correcciones 1, 2, 4, 5 y 6 de la revisión de `4242ea5`; agrega `CODEOWNERS`, la plantilla de PR, la prueba del devcontainer y la nota de E2 (O1). Local (Python 3.14.3, `TDL_EXIGIR_PRONOSTICOS=1` y `TDL_EXIGIR_TABLERO=1`): `ruff` sin hallazgos y **408 aprobadas, 2 omitidas** (red) |

### Hallazgos
**Mayor (de proceso, recurrente)**
- **D1. El PR #16 se fusionó sin revisión previa**, 13 s después de abrirse y antes de que el dictamen de B llegara al PR. Es el **décimo** PR de E1 en esa situación (#7 a #16), contra `plan_trabajo.md` §3 y el plan SQA §5. `CODEOWNERS` (`372a6ab`) no lo impide mientras `main` no tenga protección.

**Menores (documentación; pendientes en `372a6ab`, de A)**
- **m1.** `docs/E1/requerimientos.md:64-65` (RNF-SEG-07 y RNF-SEG-08) siguen diciendo que el CI «aún no se ejecutó en GitHub»; ya se ejecutó (V3).
- **m2.** `docs/E1/seguridad.md:107`: la frase «Lo que no se ha podido verificar» afirma a la vez que el trabajo está «verificado en GitHub» y deja negritas mal cerradas (introducido por `7f8f315`).
- **m3.** `docs/E1/ENTREGA.md:4`: «sin commit ni fusión todavía»; el PR #16 ya está en `main` (`628136b`).

**Observaciones**
- **O1 (E2: la tasa de error como respuesta).** Si las corridas se ejecutan contra una copia local estable de las respuestas ya capturadas, la tasa de error será casi con seguridad **0 en las 16 corridas**: una respuesta sin variación no le da nada que analizar al ANOVA. Antes de correr hay que definir qué es un error y su denominador, y provocar errores de forma controlada (fallas inyectadas y declaradas) o elegir otra respuesta principal. Se documenta sin desarrollar E2; la matriz 2³ no cambia. A lo dejó anotado en [`ruta_experimento_e2.md`](../docs/E1/ruta_experimento_e2.md) §5.
- **O2.** Los documentos fechan el corte el «2026-11-14», que es la fecha UTC; en hora local todo ocurrió el 13 de noviembre, antes del plazo de las 23:59. `ENTREGA.md` y la relatoría lo aclaran.
- **O3.** La copia del bronce (RNF-SEG-06) está en el mismo equipo; A ya lo declara como límite.

### Conformidad de la integrante B (decisiones personales, 2026-11-13)
| Tema | Decisión de B |
|---|---|
| Relatoría | De acuerdo con el contenido, **sujeto a revisar la versión corregida** antes de la aprobación definitiva |
| Plan SQA v1.1 | **Aceptado**, con el **reconocimiento formal de la desviación del proceso de E1**: diez PR (#7 a #16) se fusionaron sin revisión previa. No se atribuye ninguna autorización a los docentes. Acción correctiva acordada: **revisiones previas obligatorias** |
| Ruta de E2 | **De acuerdo** con la ruta de ingeniería (2³ sobre el extractor propio, 16 corridas en 2 bloques), conservando la observación O1 |

### PSP de la integrante B (cierre de E1)
- **Confirmado por B:** los **118 min en 23 intervalos** de [`tiempo-integrante-b.csv`](tiempo-integrante-b.csv), «siempre que correspondan a las actividades que realmente realizó». Atiende la Auditoría 6 (O6) y la Auditoría 7 (O4).
- **No registrado:** el diagnóstico del tablero de 14:38 a 14:42 (B no confirmó haberlo hecho personalmente) y el tiempo de esta revisión (B no lo indicó). No se estiman.
- **Defectos de B en esta auditoría:** ninguno. Los CSV de B no cambian.

### Dictamen
**Aprobado técnicamente con observaciones menores** para la versión `372a6ab` de `e1/cierre-documental`. El código, los datos y los resultados son correctos y no alteran el laboratorio. Quedan tres correcciones menores de documentación (m1 a m3), que no bloquean la entrega. El proceso **no** cumplió la revisión previa en el PR #16 (D1). Cualquier commit posterior a `372a6ab` requiere revisarse antes de darlo por aprobado.
