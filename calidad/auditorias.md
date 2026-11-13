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
