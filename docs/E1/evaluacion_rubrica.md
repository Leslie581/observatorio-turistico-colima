# Evaluación de E1 contra las rúbricas oficiales (autoevaluación por materia, sobre 100)

Corte 2026-11-14 · Fuente: rúbrica E1 del PDF «Proyecto Integrador» (págs. 24 a 26) y la escala del TecNM (Excelente 95–100, Notable 85–94, Bueno 75–84, Suficiente 70–74, Insuficiente < 70). **Es una autoevaluación de la integrante A con asistencia de Claude Code: no es la calificación oficial** y los docentes pueden puntuar distinto. En E1 cada materia califica sobre 100: **90 puntos de sus criterios propios más 10 de la relatoría**, que se califica una vez y cuenta en las tres. La **defensa individual** (factor 1.0, 0.8 o 0.5 en el panel del 17 y 18 de noviembre) **no está incluida**.
Nota sobre la rúbrica: los criterios «Plan de recopilación» (20), «Captura y serie histórica» (25) y «Arranque de calidad» (15) que el PDF muestra al inicio de la pág. 24 pertenecen a la rúbrica de **E0** (junto con «Pregunta y cliente» y «Preguntas analíticas» suman 100); **no puntúan en E1** y aquí no se cuentan, aunque la pág. 14 los lista como parte de lo que se construye y [`ENTREGA.md`](ENTREGA.md) los documenta.

**Cómo se distingue la evidencia.** *Implementado* = existe en el repositorio. *Local* = lo comprobé ejecutándolo en esta máquina (suite de 402 aprobadas y 2 omitidas, `ruff`, `gitleaks`, `pip-audit`, verificación de E0 y regeneración de las capas; cobertura 84 %). *GitHub* = verificado en GitHub Actions o en la API pública. **El CI nuevo se ejecutó en GitHub el 2026-11-14 sobre el commit `4242ea5` y pasó** (ejecución 43557153021 de `ci.yml` sobre `4242ea5`: éxito en `calidad`, `auditoria-dependencias`, `bloqueo-tablero` y `secretos`); las columnas «GitHub» de abajo reflejan lo verificado antes de esa ejecución y se actualizan donde se indica.

## Ingeniería de Datos (CMD-2602)
| Criterio (puntos) | Puntos | Evidencia | Implementado | Local | GitHub |
|---|---|---|---|---|---|
| Valores faltantes (15) | **13** | [`faltantes_y_atipicos.md`](faltantes_y_atipicos.md) §1: inventario real, diagnóstico por caso y simulación de 5 tratamientos con 3 mecanismos. Manzanillo no tiene faltantes; el mecanismo de la celda de Mexicali **no se puede determinar** | Sí | Sí | **Sí** (run 43557153021, `4242ea5`) |
| Atípicos y ruido (15) | **14** | [`faltantes_y_atipicos.md`](faltantes_y_atipicos.md) §2: IQR y z robusto coinciden en 3 meses de COVID; decisión por tipo (cuarentena, marcar y conservar). Sin Isolation Forest | Sí | Sí | **Sí** (run 43557153021, `4242ea5`) |
| Normalización, discretización y reducción (15) | **14** | Las tres con comparación: [`transformaciones.md`](transformaciones.md) §2 a §8 y [`pronostico.md`](pronostico.md) §2.7 (min-max frente a z-score); discretización por ancho, frecuencia y **supervisada** (§8; no generaliza a 2024 y se declara); reducción −75.0 % / −99.65 % que el pipeline imprime; jerarquías en el oro | Sí | Sí | **Sí** (run 43557153021, `4242ea5`) |
| Integración de fuentes (20) | **17** | [`pipeline.md`](pipeline.md) §3.1 y §5: DATATUR y DENUE unidos por dimensiones comunes (`dim_tiempo`, `dim_geografia`, `dim_ubicacion_denue`) con claves foráneas comprobadas; conflictos de nombre, fecha, unidad y duplicados resueltos. **No hay unión mes a mes**: las fuentes no se solapan en el tiempo (2016–2024 frente a 2026) | Sí | Sí | **Sí** (run 43557153021, `4242ea5`) |
| Puerta de calidad (25) | **24** | [`pipeline/calidad/`](../../pipeline/calidad/), [`contrato_datos.md`](contrato_datos.md) §2.3 y §3: `pandera` + 14 reglas, cuarentena con regla y motivo (2 filas rechazadas de 31,147), nada se borra en silencio; capas plata y oro automáticas con diccionario de 45 entradas | Sí | Sí | **Sí** (ejecuciones de `ci.yml` con `pipeline.ejecutar` y `verificar_oro`; `main` en verde en `ac9c88d`, run 43548657495) |
| **Subtotal de criterios propios** | **82 / 90** | | | | |

## Análisis Estadístico para Ciencia de Datos
| Criterio (puntos) | Puntos | Evidencia | Implementado | Local | GitHub |
|---|---|---|---|---|---|
| Caracterización y descomposición (15) | **14** | [`exploracion.md`](exploracion.md), [`pronostico.md`](pronostico.md) §2.1, §2.2 y §2.6: aditiva con criterio explícito; la evidencia a favor es débil (6 años) y se dice | Sí | Sí | Sí (pruebas en `main` verde) |
| Estacionariedad y autocorrelación (15) | **14** | [`pronostico.md`](pronostico.md) §2.3 a §2.5: ADF y KPSS (d = 1, D = 1), ACF y PACF interpretadas, correlación cruzada con tres variables (ninguna exógena significativa en ambos escenarios) | Sí | Sí | Sí |
| Cuatro modelos (25) | **23** | [`pronostico.md`](pronostico.md) §3: SES, Holt, Holt-Winters (por AICc) y SARIMA (72 combinaciones, parámetros justificados con ACF, PACF y AICc). Los parámetros de los ETS quedan en la frontera (efecto del COVID) | Sí | Sí | Sí |
| Selección por error (20) | **18** | [`pronostico.md`](pronostico.md) §4: MAE, RMSE y MAPE sobre 2024 con criterio fijado antes de comparar. **Un solo año de prueba** y el ingenuo estacional supera al SARIMA en MAE y MAPE: se declara | Sí | Sí | Sí |
| Residuos y comunicación (15) | **14** | [`pronostico.md`](pronostico.md) §5 y §6: Ljung-Box p = 0.273 y 0.685 (aprobado); frase para el cliente e intervalo de ±12 a ±21 pp; tablero con el pronóstico. Residuos **no normales** (intervalos aproximados). La URL pública sirve la versión integrada (verificada el 2026-11-14 04:25 UTC, seis pestañas sin errores) | Sí | Sí | **Sí** (URL pública) |
| **Subtotal de criterios propios** | **83 / 90** | | | | |

## Calidad en los Sistemas de Información (IFC-1008)
| Criterio (puntos) | Puntos | Evidencia | Implementado | Local | GitHub |
|---|---|---|---|---|---|
| Fiabilidad y disponibilidad (25) | **14** | [`fiabilidad.md`](fiabilidad.md): tasa de éxito 85.7 % (6/7, IC 95 % 42.1–99.6 %), MTTR 268 s (n = 1). **La bitácora cubre 3.83 de 7 días** y no hay historia real recuperable (§4.2); MTBF y disponibilidad solo exploratorios; el objetivo del 95 % **no se cumple** | Sí (medición) | Sí | Sí (6 ejecuciones cotejadas con la API) |
| Seguridad (15) | **13** | [`seguridad.md`](seguridad.md): `gitleaks` 8.30.1 sin hallazgos y `pip-audit` sin vulnerabilidades (incluidas las transitivas del tablero, 34 paquetes); respaldo del bronce con manifiesto y **restauración probada** (28 archivos); bloqueo con hashes; acciones por SHA; `persist-credentials: false`. Faltan la protección de `main` y un respaldo fuera del equipo | Sí | Sí | **Sí** (run 43557153021, `4242ea5`) |
| Requerimientos (10) | **9** | [`requerimientos.md`](requerimientos.md): 43 requerimientos con criterio medible, verificación y estado (34 cumplidos, 4 parciales, 4 no cumplidos, 1 propuesto); los 7 agregados el 2026-11-14 aún no los revisa B | Sí | Sí | Sí (los 36 originales revisados en la Auditoría 5) |
| Plan SQA (25) | **22** | [`plan_sqa.md`](plan_sqa.md) v1.1: estructura IEEE 730 adaptada, roles, métricas, revisiones y auditorías (1 a 7), pruebas, reporte de problemas, riesgos. **Incumplido:** los 9 PR de E1 se fusionaron sin revisión previa y la acción correctiva sigue sin implementarse | Sí | Sí | Sí (API de GitHub) |
| Integración continua (15) | **12** | [`ci.yml`](../../.github/workflows/ci.yml): `ruff`, `pytest` con cobertura (piso 75 %; medida 84 %), puerta de datos, `verificar_oro`, verificador de E0, `gitleaks`, auditoría y bloqueo del tablero. `main` en verde (`ac9c88d`), pero con 3 ejecuciones fallidas del commit `9489dc5` y **sin protección que impida fusionar algo roto**; el CI nuevo verificado en GitHub (ejecución 43557153021 de `ci.yml` sobre `4242ea5`: éxito en `calidad`, `auditoria-dependencias`, `bloqueo-tablero` y `secretos`) | Sí | Sí | **Sí** (run 43557153021, `4242ea5`); sigue sin haber protección de `main` |
| **Subtotal de criterios propios** | **70 / 90** | | | | |

## Relatoría de etapa (10 puntos, una vez, cuenta en las tres materias)
| Criterio | Puntos | Evidencia | Implementado | Local | GitHub |
|---|---|---|---|---|---|
| Específica, honesta y verificable, con las seis preguntas | **8** | [`relatoria-E1.md`](../relatoria-E1.md): fechas, números y nombres; incluye lo que salió mal (fusiones sin revisión, CI en rojo, bitácora corta, URL desactualizada); cada afirmación remite a un commit, PR, prueba o documento. **Falta la revisión y conformidad de B**, y los tiempos de A son estimaciones | Sí | Sí | — |

## Resultado
| Materia | Criterios propios (90) | Relatoría (10) | **Total sobre 100** | Nivel TecNM |
|---|---|---|---|---|
| Ingeniería de Datos | 82 | 8 | **90** | Notable |
| Análisis Estadístico para Ciencia de Datos | 83 | 8 | **91** | Notable |
| Calidad en los Sistemas de Información | 70 | 8 | **78** | Bueno |

## Puntos descontados y cuáles se pueden recuperar antes del cierre (2026-11-13, 23:59)
| Criterio | Hoy | Recuperable | Qué lo permite | Quién | Viable hoy |
|---|---|---|---|---|---|
| Integración continua | 12 / 15 | hasta +3 | La primera ejecución verde en GitHub del CI nuevo (en el PR) y la protección de `main` | Leslie (protección: [`seguridad.md`](seguridad.md) §7) | Sí, si el CI pasa |
| Seguridad | 13 / 15 | hasta +2 | CI nuevo verde (`secretos`, bloqueo, auditoría), protección de `main` y el respaldo copiado fuera del equipo | Leslie | Sí |
| Plan SQA | 22 / 25 | hasta +2 | La **primera revisión previa real** (Eimy revisa este PR antes de fusionarlo, registrada como auditoría) y la protección de `main`; los 9 PR ya fusionados no se pueden deshacer | Eimy y Leslie | Sí |
| Requerimientos | 9 / 10 | +1 | Que Eimy revise los 7 requerimientos agregados el 2026-11-14 | Eimy | Sí |
| Relatoría (cuenta en las tres materias) | 8 / 10 | hasta +2 | Conformidad de Eimy y registro del tiempo del cierre documental | Eimy y Leslie | Sí |
| Fiabilidad y disponibilidad | 14 / 25 | **no hoy** | Solo más ejecuciones de captura: 7 días de bitácora hacia el 2026-11-17; no hay historia real recuperable | — | **No** |
| Integración de fuentes | 17 / 20 | **no** | La unión mes a mes es imposible: las fuentes no se solapan en el tiempo | — | No |
| Valores faltantes / Atípicos | 13 y 14 | ≈ +1 | Isolation Forest (requiere una biblioteca que el proyecto no tiene) y más casos de faltantes: no antes del cierre | — | No |
| Estadística (selección y modelos) | 18 y 23 | **no** | Un solo año de prueba y el ingenuo estacional supera al SARIMA en MAE y MAPE: es la realidad de los datos, no un defecto corregible | — | No |
**Techo realista de hoy** si todo lo «Sí» sale bien: Calidad hasta ≈ 90 (de 78), Ingeniería de Datos hasta ≈ 92 y Análisis Estadístico hasta ≈ 93 (+2 por la relatoría). Nada de esto está garantizado: el CI de GitHub pasó en la rama, pero falta el del PR y la revisión de Eimy.

## Qué bajaría la calificación
Que el CI nuevo falle en GitHub; que la etiqueta `e1` no exista antes de las 23:59 del 13 de noviembre o que el enlace no se registre en el formulario (pág. 5: «Lo que llegue después se evalúa sobre 70 en las tres materias»); y la defensa individual si cualquiera de las dos no puede explicar lo entregado (factor 0.8 o 0.5).
**Lo que esta evaluación no puede verificar:** el registro en el formulario, los colaboradores del repositorio (la titular informó que los tres docentes ya tienen acceso), los issues de los docentes por otros medios y la configuración interna de Streamlit Community Cloud.
