# Evaluación de E1 contra las rúbricas oficiales (autoevaluación por materia, sobre 100)

Corte 2026-11-14 04:50 UTC (2026-11-13, 22:50, hora de la Ciudad de México) · Fuente: rúbrica E1 del PDF «Proyecto Integrador» (págs. 24 a 26) y la escala del TecNM (Excelente 95–100, Notable 85–94, Bueno 75–84, Suficiente 70–74, Insuficiente < 70). **Es una autoevaluación de la integrante A con asistencia de Claude Code: no es la calificación oficial**; los docentes pueden puntuar distinto. En E1 cada materia califica sobre 100: **90 puntos de sus criterios propios más 10 de la relatoría**, que se califica una vez y cuenta en las tres. La **defensa individual** (factor 1.0, 0.8 o 0.5 en el panel del 17 y 18 de noviembre) **no está incluida**.
**Criterios de esta versión.** (1) Los criterios «Plan de recopilación» (20), «Captura y serie histórica» (25) y «Arranque de calidad» (15) del inicio de la pág. 24 son de la rúbrica de **E0** (con «Pregunta y cliente» y «Preguntas analíticas» suman 100): no puntúan en E1. (2) **No se descuenta por requisitos adicionales que el PDF no exige** (protección de `main` en los criterios de seguridad, respaldo en otro proveedor, Isolation Forest —el PDF dice «IQR, puntaje z robusto **o** Isolation Forest»—, una unión mes a mes que los datos no permiten). (3) Se descuenta solo por lo que el criterio de la rúbrica pide y no está, o por una limitación real que la propia rúbrica nombra («valores supuestos», «parámetros al azar», «secretos expuestos»).
**Evidencia.** *Impl.* = existe en el repositorio. *Local* = ejecutado en esta máquina (suite de 408 aprobadas y 2 omitidas, cobertura 84 %, `ruff`, `gitleaks`, `pip-audit`, verificación de E0 y regeneración de las capas). *GitHub* = verificado en GitHub Actions o en la API pública: `ci.yml` pasó con los cuatro trabajos en las ejecuciones 43557153021 (`4242ea5`), 43557547843 y 43557683882 (`7f8f315`) y 43557697492 (`main`, `628136b`); la URL pública se leyó el 2026-11-14 a las 04:25 UTC.

## Ingeniería de Datos (CMD-2602)
| Criterio (puntos) | Puntos | Evidencia | Qué impide el máximo | Impl. | Local | GitHub |
|---|---|---|---|---|---|---|
| Valores faltantes (15) | **14** | [`faltantes_y_atipicos.md`](faltantes_y_atipicos.md) §1: inventario real, diagnóstico por caso, simulación de 5 tratamientos con 3 mecanismos y decisión | El mecanismo de la única celda vacía (Mexicali) **no se puede determinar** con un solo caso: límite de los datos, no un trabajo faltante | Sí | Sí | Sí (CI) |
| Atípicos y ruido (15) | **15** | [`faltantes_y_atipicos.md`](faltantes_y_atipicos.md) §2: IQR y z robusto (coinciden), decisión documentada por tipo | — | Sí | Sí | Sí (CI) |
| Normalización, discretización y reducción (15) | **15** | [`transformaciones.md`](transformaciones.md) §2 a §8 y [`pronostico.md`](pronostico.md) §2.7: min-max y z-score comparados; ancho, frecuencia y **supervisada** comparadas; reducción −75.0 % / −99.65 % impresa por el pipeline; jerarquías | Que la supervisada no generalice a 2024 es un **hallazgo declarado**, no un faltante | Sí | Sí | Sí (CI) |
| Integración de fuentes (20) | **18** | [`pipeline.md`](pipeline.md) §3.1 y §5: un modelo con dimensiones comunes (`dim_tiempo`, `dim_geografia`, `dim_ubicacion_denue`), claves foráneas comprobadas en cada corrida, conflictos de nombre, fecha, unidad y duplicados resueltos | La resolución de entidades es a nivel municipio: DATATUR no trae establecimientos, así que no hay correspondencia hotel a hotel con DENUE | Sí | Sí | Sí (CI) |
| Puerta de calidad (25) | **25** | [`pipeline/calidad/`](../../pipeline/calidad/), [`contrato_datos.md`](contrato_datos.md) §2.3 y §3: `pandera` y 14 reglas, cuarentena con regla y motivo (2 filas de 31,147), nada se borra en silencio, capas plata y oro automáticas con diccionario de 45 entradas | — | Sí | Sí | **Sí** (`pipeline.ejecutar` y `verificar_oro` en el CI de GitHub) |
| **Subtotal de criterios propios** | **87 / 90** | | | | | |

## Análisis Estadístico para Ciencia de Datos
| Criterio (puntos) | Puntos | Evidencia | Qué impide el máximo | Impl. | Local | GitHub |
|---|---|---|---|---|---|---|
| Caracterización y descomposición (15) | **15** | [`exploracion.md`](exploracion.md), [`pronostico.md`](pronostico.md) §2.1, §2.2 y §2.6: aditiva con criterio explícito y su límite declarado | — | Sí | Sí | Sí (CI) |
| Estacionariedad y autocorrelación (15) | **15** | [`pronostico.md`](pronostico.md) §2.3 a §2.5: ADF y KPSS (d = 1, D = 1), ACF y PACF interpretadas, correlación cruzada | — | Sí | Sí | Sí (CI) |
| Cuatro modelos (25) | **24** | [`pronostico.md`](pronostico.md) §3: SES, Holt, Holt-Winters (por AICc) y SARIMA (72 combinaciones con ACF, PACF y AICc) | Los parámetros de los tres modelos ETS quedan en la frontera (α = 1, β = 0, γ = 0) por el salto de nivel del COVID: justificados por AICc, pero poco informativos | Sí | Sí | Sí (CI) |
| Selección por error (20) | **19** | [`pronostico.md`](pronostico.md) §4: MAE, RMSE y MAPE sobre 2024 con criterio fijado antes; ganador por RMSE y residuos | El SARIMA elegido **no supera** al ingenuo estacional en MAE ni en MAPE (se declara) y la prueba es de 12 meses | Sí | Sí | Sí (CI) |
| Residuos y comunicación (15) | **14** | [`pronostico.md`](pronostico.md) §5 y §6: Ljung-Box p = 0.273 y 0.685 (aprobado); frase para el cliente e intervalo de ±12 a ±21 pp; tablero público con el pronóstico (verificado el 2026-11-14 04:25 UTC) | Residuos **no normales**: los intervalos gaussianos son aproximados | Sí | Sí | **Sí** (URL pública) |
| **Subtotal de criterios propios** | **87 / 90** | | | | | |

## Calidad en los Sistemas de Información (IFC-1008)
| Criterio (puntos) | Puntos | Evidencia | Qué impide el máximo | Impl. | Local | GitHub |
|---|---|---|---|---|---|---|
| Fiabilidad y disponibilidad (25) | **14** | [`fiabilidad.md`](fiabilidad.md): tasa de éxito 85.7 % (6/7), MTTR 268 s (n = 1), MTBF y disponibilidad solo exploratorios | **La bitácora cubre 3.83 de 7 días** y no hay historia real recuperable (§4.2); el objetivo del 95 % no se cumple. Solo más ejecuciones lo cambian (7 días hacia el 2026-11-17) | Sí | Sí | Sí (6 ejecuciones cotejadas con la API) |
| Seguridad (15) | **15** | [`seguridad.md`](seguridad.md): `gitleaks` y `pip-audit` sin hallazgos abiertos (también en las transitivas del tablero y en el CI), respaldo del bronce con manifiesto y **restauración probada**, mínimo permiso en los tokens (`ci.yml` solo lee, sin credenciales persistentes), bloqueo con hashes y acciones por SHA | — (la copia del respaldo fuera del equipo y la protección de `main` no las pide el criterio) | Sí | Sí | **Sí** (trabajos `secretos`, `auditoria-dependencias` y `bloqueo-tablero`) |
| Requerimientos (10) | **9** | [`requerimientos.md`](requerimientos.md): 43 requerimientos con criterio medible y verificación (35 cumplidos, 3 parciales, 4 no cumplidos, 1 propuesto) | Los 7 agregados el 2026-11-14 no tienen una revisión de B **registrada** como tal (la registra ella en su Auditoría 8) | Sí | Sí | Sí |
| Plan SQA (25) | **23** | [`plan_sqa.md`](plan_sqa.md) v1.1: estructura IEEE 730 adaptada, roles, métricas, revisiones y auditorías (1 a 7; la 8 es de B), reporte de problemas, acción correctiva preparada | **Los 10 PR de E1 se fusionaron sin revisión previa registrada** (la regla del propio plan): incumplimiento real del proceso | Sí | Sí | Sí (API de GitHub) |
| Integración continua (15) | **14** | [`ci.yml`](../../.github/workflows/ci.yml): `ruff`, `pytest` con cobertura (piso 75 %; medida 84 %), puerta de datos, `verificar_oro`, verificador de E0, `gitleaks`, auditoría y bloqueo del tablero; en verde en `main` (`628136b`, ejecución 43557697492) | 3 ejecuciones fallidas (`9489dc5`, ya corregidas) y `main` aún **sin protección** que impida fusionar algo roto («un cambio que rompe algo no entra», pág. 16) | Sí | Sí | **Sí** (ejecuciones citadas arriba) |
| **Subtotal de criterios propios** | **75 / 90** | | | | | |

## Relatoría de etapa (10 puntos, una vez, cuenta en las tres materias)
| Criterio | Puntos | Evidencia | Qué impide el máximo | Impl. | Local | GitHub |
|---|---|---|---|---|---|---|
| Específica, honesta y verificable, con las seis preguntas (10) | **8** | [`relatoria-E1.md`](../relatoria-E1.md): fechas, números y nombres; incluye lo que salió mal; cada afirmación remite a un commit, PR, prueba o documento; **exportada a PDF A4 (11 pt, márgenes de 2 cm): 2 páginas** | Falta la **conformidad de las dos integrantes** y los tiempos de A son estimaciones retrospectivas | Sí | Sí | — |

## Resultado
| Materia | Criterios propios (90) | Relatoría (10) | **Total sobre 100** | Nivel TecNM |
|---|---|---|---|---|
| Ingeniería de Datos | 87 | 8 | **95** | Excelente |
| Análisis Estadístico para Ciencia de Datos | 87 | 8 | **95** | Excelente |
| Calidad en los Sistemas de Información | 75 | 8 | **83** | Bueno |

Los 3 puntos de criterios propios que faltan en las dos primeras materias son límites de los datos (una celda, un año de prueba, residuos no normales) o resultados que la rúbrica exige reportar con honestidad: no se recuperan con más trabajo. En Calidad la brecha grande es la **fiabilidad (−11)**, seguida del **proceso de revisión (−2)**.

## Puntos descontados y cuáles se pueden recuperar
| Criterio | Hoy | Recuperable | Qué lo permite | Quién | ¿Depende solo de nosotras? |
|---|---|---|---|---|---|
| Relatoría | 8 / 10 | hasta +2 | Conformidad de ambas integrantes y registro del tiempo del cierre documental en el PSP de A | Leslie y Eimy | **Sí** |
| Requerimientos | 9 / 10 | +1 | Que la Auditoría 8 de B deje registrada su revisión de los 7 requerimientos nuevos | Eimy | **Sí** |
| Plan SQA | 23 / 25 | hasta +2 | La **primera revisión previa real**: que el PR de estas correcciones se revise y se apruebe en GitHub **antes** de fusionarlo; la conformidad de ambas con la acción correctiva (tabla en [`plan_sqa.md`](plan_sqa.md) §5.1) y activar la protección de `main`. Los 10 PR ya fusionados no se pueden deshacer | Leslie y Eimy | **Sí** (la protección requiere ser propietaria) |
| Integración continua | 14 / 15 | +1 | Protección de `main` con los cuatro trabajos como comprobaciones obligatorias ([`seguridad.md`](seguridad.md) §7, con la advertencia sobre la captura diaria) | Leslie | **Sí** |
| Fiabilidad y disponibilidad | 14 / 25 | **no hoy** | Más ejecuciones de captura (7 días hacia el 2026-11-17) y, para el MTBF, un segundo incidente real; no hay historia recuperable ni se inventa | — | **No**: depende de que pasen los días |
| Valores faltantes, integración, cuatro modelos, selección y residuos | −1 cada uno | **no** | Límites de los datos (una celda; sin establecimientos en DATATUR; ETS en la frontera; 12 meses de prueba; residuos no normales) | — | **No** |

## Qué bajaría la calificación
Que no exista la etiqueta `e1` antes de las 23:59 del 13 de noviembre o que el enlace no se registre en el formulario (pág. 5: «Lo que llegue después se evalúa sobre 70 en las tres materias»); que el CI falle en el PR de correcciones; y la defensa individual si cualquiera de las dos no puede explicar lo entregado (factor 0.8 o 0.5).
**Lo que esta evaluación no puede verificar:** el registro en el formulario, los colaboradores del repositorio (la titular informó que los tres docentes ya tienen acceso), los issues de los docentes por otros medios y la configuración interna de Streamlit Community Cloud.
