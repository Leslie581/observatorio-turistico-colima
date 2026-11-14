# Entrega E1 · Observatorio de Ocupación Hotelera de Colima (Manzanillo; nombre provisional)

Equipo: Leslie Valadez Macías (integrante A, `Leslie581`) y Eimy Melissa Urbina Meza (integrante B, `eimymuz`) · Etiqueta: `e1` (**no creada todavía**) · Tablero: https://tdl-turistico-colima.streamlit.app (responde en público y sirve la versión integrada, véase «Tablero»)
Repositorio: https://github.com/Leslie581/tdl-turistico-colima (el nombre anterior, `observatorio-turistico-colima`, redirige) · Corte: **2026-11-14** (verificación local entre las 03:10 y las 05:00 UTC; 2026-11-13, 21:10 a 23:00, hora de la Ciudad de México) · Estado: rama `e1/cierre-documental` sobre `main` (`ac9c88d`), **sin commit ni fusión todavía**

## Resumen en tres líneas
1. Los datos viajan de bronce a oro sin intervención ([`pipeline.md`](pipeline.md)): 31,147 filas de DATATUR leídas, 2 rechazadas a cuarentena con su motivo, 108 meses de oro para Manzanillo; el tablero publica el pronóstico elegido por su error en 2024 (SARIMA, RMSE 2.64 pp), que **no supera** a la referencia ingenua estacional en MAE ni en MAPE ([`pronostico.md`](pronostico.md) §4).
2. Calidad medida, no supuesta, y con resultados que **no cumplen** todos los objetivos: tasa de éxito de la captura 85.7 % (6 de 7; objetivo 95 %), bitácora de **3.83 de 7 días**, MTBF y disponibilidad solo como estimación exploratoria ([`fiabilidad.md`](fiabilidad.md)); **diez de diez PR de E1 (#7 a #16) se fusionaron sin revisión previa registrada en GitHub** y `main` no tiene protección ([`plan_sqa.md`](plan_sqa.md) §5.1). El CI de `main` está en **verde** (`ac9c88d`) tras haber estado en rojo con el PR #14.
3. **La entrega no está cerrada**: faltan la revisión cruzada de Eimy y la integración definitiva, la etiqueta `e1`, el registro en el formulario, el tiempo del cierre documental en el PSP, la ejecución en GitHub del CI nuevo (ya pasó; véase arriba) y los demás pendientes de la sección final.

> Esta ficha enlaza solo evidencias que existen en la rama. **PARCIAL**, **NO CUMPLIDO** y **PENDIENTE** significan lo que dicen. La auditoría contra la rúbrica del PDF está en [`auditoria_integral_pdf.md`](auditoria_integral_pdf.md).

## Ingeniería de Datos
| Criterio de la rúbrica E1 | Evidencia (enlace) | Estado | Nota del equipo |
|---|---|---|---|
| *Plan de recopilación* (criterio de la rúbrica de **E0**, pág. 24; la pág. 14 lo lista como parte de lo que se construye) | [`docs/fuentes/README.md`](../fuentes/README.md), [`datatur.md`](../fuentes/datatur.md), [`denue.md`](../fuentes/denue.md) | CUMPLE con una salvedad | El contenido del `robots.txt` de INEGI no está archivado; los permisos de DATATUR están separados en confirmados, restringidos y no aclarados |
| *Captura y serie histórica* (criterio de la rúbrica de **E0**; listado en la pág. 14) | [`captura-diaria.yml`](../../.github/workflows/captura-diaria.yml), [`Base70centros.csv`](../../data/bronce/datatur/Base70centros.csv) (108 meses), [`data/bronce/denue/`](../../data/bronce/denue/), [`bitacora_capturas.jsonl`](../../calidad/bitacora_capturas.jsonl) | CUMPLE | La ejecución programada (`schedule`) tiene 4 ejecuciones exitosas (10 a 13 de noviembre); GitHub las retrasa varias horas respecto al cron |
| **Valores faltantes** (15): mecanismo diagnosticado y tratamiento justificado | [`faltantes_y_atipicos.md`](faltantes_y_atipicos.md) §1, [`contrato_datos.md`](contrato_datos.md) §2.3, [`test_faltantes_atipicos.py`](../../tests/test_faltantes_atipicos.py) | CUMPLE con una salvedad | Manzanillo **no tiene faltantes**; Mexicali (1 celda): mecanismo **indeterminado**; El Fuerte (12 meses): no al azar, no se imputa. Simulación de 5 tratamientos con 3 mecanismos: la interpolación lineal es la mejor, pero **ninguna corrige lo no al azar** |
| **Atípicos y ruido** (15): método justificado y decisión por tipo | [`faltantes_y_atipicos.md`](faltantes_y_atipicos.md) §2, [`contrato_datos.md`](contrato_datos.md) §2.3 | CUMPLE | IQR 1.5 y puntaje z robusto coinciden en 2020-04 a 2020-06 (COVID: **marcar y conservar**); ocupados > disponibles van a cuarentena; ruido: conservar. Sin Isolation Forest |
| **Normalización, discretización y reducción** (15), con análisis comparativo | [`transformaciones.md`](transformaciones.md) §2 a §8; min-max frente a z-score: [`pronostico.md`](pronostico.md) §2.7; discretización por ancho, frecuencia y **supervisada**: [`comparacion_metodos.csv`](../../laboratorio/exploracion/resultados/discretizacion_supervisada/comparacion_metodos.csv); jerarquías: [`pipeline.md`](pipeline.md) §3.1 | CUMPLE con salvedades | Las tres aplicadas con parámetros solo del entrenamiento; reducción −75.0 % (y −99.65 %) que el pipeline imprime. La supervisada separa mejor la temporada alta en el ajuste (p = 1/501 ≈ 0.002: límite de resolución de 500 permutaciones, 0 excedencias) pero **no generaliza a 2024** (12 meses); sin ganador estable entre min-max y z-score |
| **Integración de fuentes** (20): conflictos resueltos, sin duplicados | [`contrato_datos.md`](contrato_datos.md) §5, [`pipeline.md`](pipeline.md) §3.1 y §5, [`dim_geografia.csv`](../../data/oro/dim_geografia.csv), [`dim_tiempo.csv`](../../data/oro/dim_tiempo.csv), [`test_pipeline_jerarquias.py`](../../tests/test_pipeline_jerarquias.py) | CUMPLE con una salvedad | Modelo de datos con dimensiones comunes y claves foráneas comprobadas en cada corrida; nombres, fechas, unidades y duplicados resueltos. **No hay unión mes a mes** porque las fuentes no se solapan en el tiempo (2016–2024 frente a 2026) |
| **Puerta de calidad** (25): validación automática, cuarentena y motivo | [`pipeline/calidad/`](../../pipeline/calidad/), [`contrato_datos.md`](contrato_datos.md) §3, [`resumen de cuarentena`](../../data/cuarentena/resumen_e1-e6c9a995c9ed.json), [`pipeline.md`](pipeline.md) §4 | CUMPLE | `pandera` + reglas R-D01 a R-E06; 2 filas rechazadas con regla y motivo; nada se borra en silencio |
| Capas plata y oro automáticas con diccionario | [`diccionario_datos.csv`](../../data/oro/diccionario_datos.csv) (45 entradas), [`pipeline.md`](pipeline.md) §1 y §4, `pipeline.verificar_oro` | CUMPLE | El oro regenerado coincide con el versionado (comprobación en `ci.yml`); las jerarquías se regeneran en cada corrida |

## Análisis Estadístico para Ciencia de Datos
| Criterio de la rúbrica E1 | Evidencia (enlace) | Estado | Nota del equipo |
|---|---|---|---|
| **Caracterización y descomposición** (15) | [`exploracion.md`](exploracion.md), [`pronostico.md`](pronostico.md) §2.1, §2.2 y §2.6 | CUMPLE | Aditiva, con criterio explícito (errores equivalentes; correlación amplitud–nivel −0.47). La evidencia a favor de aditiva es **débil** (6 años, dominada por 2020) |
| **Estacionariedad y autocorrelación** (15) | [`pronostico.md`](pronostico.md) §2.3 a §2.5 | CUMPLE | ADF y KPSS (d = 1, D = 1 es estacionaria); ACF y PACF interpretadas; correlación cruzada con tres variables: ninguna exógena significativa en ambos escenarios, no se incorporan |
| **Cuatro modelos** (25) | [`pronostico.md`](pronostico.md) §3, [`candidatos_aicc.csv`](../../laboratorio/pronosticos/resultados/candidatos_aicc.csv) | CUMPLE | SES, Holt, Holt-Winters (por AICc) y SARIMA (72 combinaciones por AICc); los parámetros SARIMA se justifican con ACF, PACF y AICc |
| **Selección por error** (20): MAE, RMSE y MAPE en datos de prueba | [`pronostico.md`](pronostico.md) §4, [`comparacion_modelos_2024.csv`](../../laboratorio/pronosticos/resultados/comparacion_modelos_2024.csv) | CUMPLE con salvedades | Criterio fijado antes de comparar. **Un solo año de prueba:** el ganador no es estable y el ingenuo estacional tiene menor MAE y MAPE |
| **Residuos y comunicación** (15): Ljung-Box, intervalo explicado al cliente | [`pronostico.md`](pronostico.md) §5 y §6, [`residuos_modelo_elegido.csv`](../../laboratorio/pronosticos/resultados/residuos_modelo_elegido.csv), [`pronostico_modelo_elegido.csv`](../../laboratorio/pronosticos/resultados/pronostico_modelo_elegido.csv) | CUMPLE con salvedades | Ljung-Box p = 0.273 y 0.685; residuos **no normales** (intervalos aproximados); frase para el cliente en §6; intervalos de ±12 a ±21 pp |
| Pronóstico publicado en el tablero | [`tablero.md`](tablero.md), [`tablero/`](../../tablero/), [Auditoría 7](../../calidad/auditorias.md) | CUMPLE | Verificado en la URL pública el 2026-11-14 04:25 UTC (véase «Tablero») |

## Calidad en los Sistemas de Información
| Criterio de la rúbrica E1 | Evidencia (enlace) | Estado | Nota del equipo |
|---|---|---|---|
| *Arranque de calidad* (criterio de la rúbrica de **E0**; la pág. 14 lo lista): registros individuales, bitácora activa, tres objetivos medibles | [`tiempo-integrante-a.csv`](../../calidad/tiempo-integrante-a.csv), [`defectos-integrante-a.csv`](../../calidad/defectos-integrante-a.csv), [`tiempo-integrante-b.csv`](../../calidad/tiempo-integrante-b.csv), [`defectos-integrante-b.csv`](../../calidad/defectos-integrante-b.csv), [`bitacora_capturas.jsonl`](../../calidad/bitacora_capturas.jsonl), [`objetivos.md`](../../calidad/objetivos.md) | **PARCIAL** | A: tiempos **estimados retrospectivamente, no medidos** (E0 750 min; E1 660 min registrados hasta ahora: L0 y L1 240, L2 150 y L3 270); **falta registrar el cierre documental** ([`psp-e1-integrante-a-respaldo.md`](../../calidad/psp-e1-integrante-a-respaldo.md)). Defectos: A 22, B 14. Los tiempos de B los confirma B (Auditoría 7, O4) |
| **Fiabilidad y disponibilidad** (25): MTBF, MTTR y disponibilidad con 7 días de bitácora | [`fiabilidad.md`](fiabilidad.md), [`fiabilidad_e1.json`](../../calidad/fiabilidad_e1.json), [`pipeline/fiabilidad.py`](../../pipeline/fiabilidad.py), [`test_fiabilidad.py`](../../tests/test_fiabilidad.py) | **PARCIAL** | Medidas con lo que hay: éxito 85.7 % (6/7, IC 95 % 42.1–99.6 %), MTTR 268 s (n = 1, extremos no corroborados). La bitácora cubre **3.83 de 7 días**; MTBF y disponibilidad solo exploratorios (un incidente). **No cumple el objetivo del 95 %** |
| **Seguridad** (15): `gitleaks` y `pip-audit` sin hallazgos; respaldo probado | [`seguridad.md`](seguridad.md), [`calidad/evidencia/`](../../calidad/evidencia/), [`test_evidencia_gitleaks.py`](../../tests/test_evidencia_gitleaks.py), [`test_respaldo_bronce.py`](../../tests/test_respaldo_bronce.py), [`test_bloqueo_tablero.py`](../../tests/test_bloqueo_tablero.py) | CUMPLE con salvedades | `gitleaks` 8.30.1 sin hallazgos (local y automatizado en CI); `pip-audit` sin vulnerabilidades, también en las transitivas del tablero; **respaldo del bronce con manifiesto SHA-256 y restauración automatizada probada** (28 archivos); bloqueo con hashes del tablero; acciones fijadas por SHA. Salvedades: el CI nuevo **verificado en GitHub (ejecución 43557153021 de `ci.yml` sobre `4242ea5`: éxito en `calidad`, `auditoria-dependencias`, `bloqueo-tablero` y `secretos`)**, la copia del bronce **está en el mismo equipo** y `main` **no tiene protección** |
| **Requerimientos** (10): verificables, cada uno con su comprobación | [`requerimientos.md`](requerimientos.md), [`test_requerimientos.py`](../../tests/test_requerimientos.py) | CUMPLE | 43: 35 cumplidos, 3 parciales, 4 no cumplidos, 0 pendientes, 1 propuesto (los 7 últimos aún sin revisión de B) |
| **Plan SQA** (25): estructura IEEE 730 adaptada | [`plan_sqa.md`](plan_sqa.md), [`auditorias.md`](../../calidad/auditorias.md) (Auditorías 1 a 7) | CUMPLE con salvedades | Plan completo (versión 1.1). La acción correctiva de D1 y la excepción de E1 están **preparadas** (plantilla de PR y CODEOWNERS en `.github/`); faltan la conformidad personal de ambas y la protección de `main` |
| **Integración continua** (15): pruebas, linter y puerta de datos en cada push | [`ci.yml`](../../.github/workflows/ci.yml), [`test_ci_workflow.py`](../../tests/test_ci_workflow.py), [`pipeline.md`](pipeline.md) §6 | **PARCIAL** | `main` está en **verde** (`ac9c88d`: ejecución 43548657495; `628136b`, tras fusionar el PR #16: 43557697492); de 30 ejecuciones, 3 fallaron (`9489dc5`, corregidas en `eb8f606`). `ci.yml` de esta rama instala las dependencias del tablero y **exige** sus pruebas, mide cobertura (piso de 75 %; medida 84 %), audita el bloqueo y las transitivas del tablero, ejecuta `gitleaks` y fija las acciones por SHA; la suite local da **408 aprobadas y 2 omitidas** (las 2 de red). **Ejecución en GitHub: `ci.yml` pasó en GitHub con los cuatro trabajos (`calidad`, `auditoria-dependencias`, `bloqueo-tablero` y `secretos`) en éxito: ejecución 43557153021 (`4242ea5`), 43557547843 (push) y 43557683882 (pull request) de `7f8f315`, 43557697492 (push a `main`, `628136b`) y 43558845112 (`372a6ab`)** |

## Relatoría de etapa
[`docs/relatoria-E1.md`](../relatoria-E1.md) (máximo dos páginas; **pendiente de la revisión y conformidad de ambas integrantes**).

## Tablero
- URL: https://tdl-turistico-colima.streamlit.app. Verificada el 2026-11-14 a las 04:25 UTC (2026-11-13, 22:25, hora de la Ciudad de México) en el navegador integrado: la aplicación, desplegada desde `main` con Python 3.13 (declarado por la titular del repositorio), muestra el filtro de periodo, el resumen ejecutivo, las fechas clave y los indicadores 45.9 %, 54.7 %, 1.5 % y 12 de 12; las seis pestañas abren sin errores y la frase que reemplazó el PR #15 ya no aparece.
- Historial: el 2026-11-14 a las 03:09 UTC la URL todavía servía una versión anterior ([Auditoría 7](../../calidad/auditorias.md), D2); la titular corrigió el despliegue y la lectura de las 04:25 UTC lo confirma.
- El tablero de `main` coincide con los CSV del laboratorio (recálculo independiente: Auditoría 7, V3 a V5). **No verificado:** vista en un teléfono, ni que el despliegue siga la rama `main` en cada cambio futuro (la configuración de Streamlit Cloud no se puede leer desde el repositorio).
- Streamlit Community Cloud puede dejar la aplicación en reposo; no es un servicio con disponibilidad garantizada.
- Evaluación contra las rúbricas oficiales por materia (autoevaluación, no calificación): [`evaluacion_rubrica.md`](evaluacion_rubrica.md).

## Issues de la entrega anterior
La API pública de GitHub (2026-11-14) devuelve **0 issues** en el repositorio (ninguno abierto ni cerrado). No hay observaciones de los docentes registradas como issues; si las dejaron por otro medio, el equipo no las ha recibido. **PENDIENTE:** confirmar con los docentes.

## Uso de IA generativa
Ambas integrantes usaron Claude Code (Anthropic) para escribir y revisar código, pruebas y documentos, ejecutar verificaciones y redactar auditorías; los PSP de B lo marcan fila por fila. La asistencia **no cuenta como revisión independiente**. Cada integrante debe poder explicar lo que entrega en la defensa del 17 y 18 de noviembre.

## Pendientes declarados
### A. Obligatorios para la entrega (PDF, págs. 5 y 12; antes de las 23:59 del 13 de noviembre)
| Pendiente | Estado | Quién |
|---|---|---|
| Fusionar el PR de las correcciones **después** de que B lo revise y lo apruebe en GitHub (primera revisión previa real) y de que su CI esté en verde | Pendiente | B revisa; A fusiona con autorización |
| **Etiqueta `e1`** sobre un commit de `main` (con esta ficha y la relatoría dentro) | **No creada** | A, con autorización |
| **Registro del enlace de la etiqueta en el formulario de entregas** (un solo registro; cuenta para las tres materias) | **No verificable** desde el repositorio | A |
| Los tres docentes como colaboradores del repositorio | **Declarado por la titular** (2026-11-13); no verificable desde la API pública | A (comprobarlo en Settings → Collaborators) |
| Relatoría y registros PSP **de cada integrante** (el tiempo y los defectos son individuales) | Relatoría redactada, 2 páginas verificadas; **PSP de A: falta el tiempo del cierre documental; PSP de B y su Auditoría 8: los registra B en su rama** | A y B, cada una lo suyo |
| Conformidad personal de cada integrante con el plan SQA v1.1 y el reconocimiento de los diez PR sin revisión previa | **A: registrada** (2026-11-13); **B: pendiente** ([`plan_sqa.md`](plan_sqa.md) §5.1) | B |

### B. Mejoras opcionales (no las exige el PDF)
| Mejora | Estado |
|---|---|
| Protección de `main` con los cuatro trabajos como comprobaciones obligatorias | No activada; **no hacerla antes de la etiqueta** ([`seguridad.md`](seguridad.md) §7: bloquea la captura diaria salvo bypass) |
| Copia del respaldo del bronce fuera del equipo | Pendiente de A ([`seguridad.md`](seguridad.md) §6.2) |
| Hashes para las otras tres listas de dependencias; fijar las imágenes por *digest* | No implementados |
| Revisión de B sobre los 7 requerimientos agregados el 2026-11-14 | En su Auditoría 8 |
| Isolation Forest, unión mes a mes, nuevas fuentes | No aplican / no viables |

### C. Incumplimientos históricos que ya no se pueden corregir antes de la entrega
| Incumplimiento | Evidencia |
|---|---|
| Los **diez PR de E1 (#7 a #16)** se fusionaron sin revisión previa registrada en GitHub, contra `plan_trabajo.md` §3 | [`plan_sqa.md`](plan_sqa.md) §5.1; Auditorías 3 a 7 |
| El CI de `main` estuvo en rojo (3 ejecuciones del commit `9489dc5`) | [`plan_sqa.md`](plan_sqa.md) §6; corregido en `eb8f606` |
| La bitácora cubre **3.83 de 7 días**: MTBF y disponibilidad solo exploratorios; el objetivo del 95 % no se cumple. La ventana del PDF (6 al 13 de noviembre) no se puede completar hacia atrás | [`fiabilidad.md`](fiabilidad.md) §4.2 |
| El mecanismo de la única celda vacía de Base70 (Mexicali) no se puede determinar | [`faltantes_y_atipicos.md`](faltantes_y_atipicos.md) §1 |
| Un solo año de prueba (12 meses) y el ingenuo estacional supera al SARIMA en MAE y MAPE | [`pronostico.md`](pronostico.md) §4 |

### D. Para después de E1
Regenerar [`fiabilidad_e1.json`](../../calidad/fiabilidad_e1.json) con las capturas nuevas; repetir `gitleaks` y la lectura de la URL del tablero sobre el commit etiquetado; correr el experimento de E2 ([`ruta_experimento_e2.md`](ruta_experimento_e2.md): ruta ingeniería, **confirmada por A**, pendiente de B).
