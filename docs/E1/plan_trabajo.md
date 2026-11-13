# Plan de trabajo E1 · requisitos, organización y calidad

Versión: 2026-11-13 · Contrato de datos **1.0.0 fijado** (L0, PR #7); pipeline integrado en `main` (L1, PR #8); fase L2 en la rama `e1/leslie-l2`. El reparto de responsables sigue siendo propuesto y se confirma con la integrante B.
Fuente de los requisitos: PDF oficial del Proyecto Integrador TRUSTED DATA LAB, sección E1 (págs. 14–17), rúbrica E1 (págs. 24–26) y reglas de entrega (pág. 12). **No se incluyen requisitos de E2 ni E3.**
Responsables: **propuestos**, no asignados; se confirman con Eimy. Fecha de entrega según el PDF: **13 de noviembre de 2026**, antes de las 23:59, con la etiqueta `e1`.

## 1. Matriz de requisitos de E1
Dependencias técnicas: **C** = contrato de datos ([`contrato_datos.md`](contrato_datos.md)); **O** = capa oro; **P** = puerta de calidad de plata; **B** = bitácora de capturas.

### Ingeniería de Datos (rúbrica: 90 puntos)
| Requisito oficial (pts) | Evidencia esperada | Responsable propuesto | Dependencia |
|---|---|---|---|
| Valores faltantes: mecanismo diagnosticado y tratamiento justificado (15) | Sección del contrato y una prueba que muestre el diagnóstico sobre Base70 (1 celda vacía; El Fuerte sin 2024) | Leslie | C |
| Atípicos y ruido: método justificado y decisión por tipo (15) | IQR sobre `ocupacion_pct`; decisión: marcar COVID, cuarentena para ocupados > disponibles | Leslie | C, P |
| Normalización, discretización y reducción, con análisis comparativo (15) | Funciones en `pipeline/transformaciones.py` y comparación min-max frente a z-score en el laboratorio, con parámetros ajustados solo con entrenamiento | Leslie (funciones) y Eimy (comparación en el laboratorio) | C, O |
| Integración de fuentes sin conflictos ni duplicados (20) | Modelo de datos DATATUR + DENUE descrito en el contrato §5 y dataset de contexto `manzanillo_oferta_hospedaje.csv` | Leslie | C |
| Puerta de calidad automática con cuarentena y motivo (25) | `pandera` (o Great Expectations), `data/cuarentena/` y `resumen_<ejecucion>.json` con registros leídos, aceptados y rechazados por regla | Leslie | P |
| Plata y oro pobladas automáticamente, con diccionario de la capa oro | Orquestador `pipeline/ejecutar.py`, `data/oro/diccionario_datos.csv` | Leslie | C |

### Análisis Estadístico (rúbrica: 90 puntos)
| Requisito oficial (pts) | Evidencia esperada | Responsable propuesto | Dependencia |
|---|---|---|---|
| Caracterización y descomposición, aditiva o multiplicativa justificada (15) | Gráfica de la serie y descomposición en tendencia, estacionalidad y residuo, con interpretación | Leslie (exploración y gráficas) | O |
| Estacionariedad y autocorrelación: Dickey-Fuller, ACF y PACF interpretadas, más correlación cruzada con una segunda variable (15) | Notebook con pruebas y lectura de cada gráfica; segunda variable: `pct_cuartos_no_residentes` o `estadia_promedio` | Leslie | O |
| Cuatro modelos: simple, Holt, Holt-Winters y ARIMA/SARIMA con parámetros justificados por ACF, PACF y AIC (25) | Notebook reproducible | Eimy | O |
| Selección por error con datos de prueba: MAE, RMSE y MAPE (20) | Tabla comparativa sobre 2024-01 a 2024-12 | Eimy | O, interfaz |
| Residuos (Ljung-Box, varianza estable) y comunicación: pronóstico con intervalo y frase para el cliente (15); publicado en el tablero | Diagnóstico del ganador y página del tablero (`tablero/`) | Eimy | modelos |

### Calidad en los Sistemas de Información (rúbrica: 90 puntos)
| Requisito oficial (pts) | Evidencia esperada | Responsable propuesto | Dependencia |
|---|---|---|---|
| Fiabilidad y disponibilidad medidas: tasa de éxito, MTBF, MTTR y disponibilidad, comparadas con el objetivo de E0 (25) | Script que lee la bitácora y calcula las métricas, y su resultado. **Aviso:** la rúbrica pide 7 días de bitácora (6 al 13 de noviembre); hay capturas desde el 2026-11-09 (3 programadas del 10 al 12). Se medirá con lo disponible, declarando el periodo real | Leslie | B |
| Seguridad: `gitleaks` y `pip-audit` sin hallazgos abiertos; tokens con el mínimo permiso; respaldo de bronce probado (15) | Reporte de ambas herramientas, revisión de permisos del workflow y prueba de restauración del bronce | Leslie | herramientas instaladas |
| Requerimientos verificables, cada uno con su comprobación (10) | `docs/E1/requerimientos.md` | Leslie redacta, Eimy revisa | — |
| Plan SQA con estructura IEEE 730 adaptado al proyecto (25) | `docs/E1/plan_sqa.md` (propósito, roles, estándares y métricas, revisiones y auditorías, pruebas, reporte de problemas, herramientas, control de versiones, riesgos) | Leslie | — |
| Integración continua: pruebas, linter y puerta de datos en cada push (15) | Workflow `ci.yml` (separado de `captura-diaria.yml`) | Leslie | P |

### Entrega
| Requisito oficial | Evidencia esperada | Responsable propuesto |
|---|---|---|
| Ficha única `docs/E1/ENTREGA.md` con tres apartados y enlaces a la evidencia (pág. 12) | Ficha basada en la de E0 | Leslie (consolida); cada una llena su apartado |
| Relatoría de etapa `docs/relatoria-E1.md`, máx. 2 páginas, con las 6 preguntas (10 pts, cuenta en las tres materias) | Cronología con fechas, responsables y horas tomadas del registro de tiempo | Las dos; se redacta con los PSP |
| Etiqueta `e1` antes de las 23:59 y un solo registro en el formulario | Etiqueta sobre un commit de `main` | Quien integre al final |
| Atender los issues que dejen los docentes antes de la siguiente entrega (pág. 12) | Issues cerrados con commit | Las dos |
| (No calificada, pero necesaria) elegir la ruta del experimento de E2 | Decisión escrita | Las dos |

## 2. Organización de archivos y propiedad (para no pisarse)
Regla: **cada archivo tiene una sola dueña por rama**. Lo compartido se toca en commits pequeños y se integra por pull request.

| Ruta | Contenido | Dueña |
|---|---|---|
| `pipeline/` (`config.py`, `plata_datatur.py`, `plata_denue.py`, `oro.py`, `interfaz.py`, `transformaciones.py`, `ejecutar.py`) | Bronce → plata → oro | Leslie |
| `pipeline/calidad/` (`reglas_datatur.py`, `reglas_denue.py`, `cuarentena.py`) | Reglas de la puerta de calidad | Leslie |
| `tests/test_pipeline_*.py`, `tests/test_calidad_*.py` | Pruebas del pipeline y de la calidad | Leslie |
| `data/plata/`, `data/oro/`, `data/cuarentena/` | Salidas. Se versiona solo el oro público, agregado y reproducible, más los resúmenes de cuarentena (contrato §4.3; `.gitignore` ajustado) | Leslie |
| `laboratorio/exploracion/` | Caracterización, descomposición, estacionariedad, ACF/PACF y gráficas | Leslie |
| `laboratorio/pronosticos/` | Cuatro modelos, selección, residuos | **Eimy** |
| `tests/test_laboratorio_*.py` | Pruebas del laboratorio | Eimy |
| `tablero/` | Página del pronóstico | Eimy (los datos los entrega `interfaz`) |
| `docs/E1/contrato_datos.md`, `requerimientos.md`, `plan_sqa.md` | Contrato, requerimientos y plan SQA | Leslie |
| `docs/E1/pronostico.md` | Metodología y resultados del pronóstico | Eimy |
| `docs/E1/ENTREGA.md`, `docs/relatoria-E1.md` | Ficha y relatoría | Compartidos: una sección por apartado |
| `calidad/tiempo-integrante-a.csv`, `defectos-integrante-a.csv` | PSP de Leslie | Leslie |
| `calidad/tiempo-integrante-b.csv`, `defectos-integrante-b.csv` | PSP de Eimy | Eimy |
| `calidad/auditorias.md`, `calidad/revision_calidad.md` | Registro de revisiones | Cada quien registra **solo** sus revisiones |
| `requirements.in`, `requirements.txt`, `requirements-lab.txt`, `requirements-dev.txt`, `ruff.toml` | Dependencias: núcleo (captura y pipeline), laboratorio y desarrollo, separadas a propósito (ver `pipeline.md` §6) | Leslie las administra; Eimy pide cambios por issue o PR pequeño |
| `extractores/`, `.github/workflows/captura-diaria.yml`, `data/bronce/` | Captura de E0 | **No se modifican** en E1 (el bronce solo lo escribe el bot) |

**Interfaz:** el laboratorio lee únicamente `data/oro/` mediante `pipeline/interfaz.py` (contrato §7). Mientras no exista, Eimy usa la derivación de referencia del contrato y parte de la guía del §0 (esquema exacto, fórmula, partición 96 + 12 meses y reglas de uso de las variables adicionales).
**Ramas:** `e1/leslie-*` y `e1/eimy-*`; integración a `main` por pull request con revisión de la otra integrante.

## 3. Calidad y responsabilidades en E1
- **Quality Lead de E1:** Leslie Valadez Macías (designación para esta entrega). **No se ha realizado ninguna auditoría ni revisión de E1 a esta fecha**; esta sección no registra aprobaciones.
- **PSP individual:** cada integrante anota su propio tiempo y defectos en sus CSV (formato del Kit con `minutos_estimados` para duraciones retrospectivas). Solo actividades y defectos reales, con evidencia (commit, ejecución o archivo). Un defecto se registra solo cuando se introdujo y se corrigió; los hallazgos de una revisión ajena quedan en `calidad/auditorias.md`.
- **Pruebas automatizadas:** cada regla de calidad (R-D01…R-E06) tiene al menos una prueba positiva y una negativa; el oro tiene pruebas de forma (108 filas, orden, sin huecos, `ocupacion_pct` entre 0 y 100). Las pruebas con datos simulados lo declaran y no se presentan como evidencia operativa.
- **Revisión recíproca:** desde E1, todo cambio se integra por pull request revisado por la otra integrante (en E0 hubo fusiones sin revisión previa). El revisor deja hallazgos con archivo y línea en `calidad/auditorias.md`, y registra su propio tiempo.
- **Evidencias para la ficha E1:** salida del pipeline (resumen de cuarentena), pruebas y CI en verde, medición de fiabilidad, reportes de seguridad, planes y requerimientos, notebooks, gráficas y la página del tablero; todo enlazado desde `docs/E1/ENTREGA.md`.
- **Antes de congelar:** `pytest`, `ruff`, la puerta de datos y el verificador de E0 en verde, y revisión recíproca registrada.

## 4. Estado al 2026-11-13 (fases L2 y L3: `main` incluye el PR #10; L3 en la rama `e1/leslie-calidad`)
| Tema | Estado |
|---|---|
| Contrato de datos 1.0.0 y su revisión de documentación r1 | Fijado y corregido (`contrato_datos.md` §9) |
| Plata, puerta de calidad y cuarentena | **Implementado y ejecutado sobre el bronce real** ([`pipeline.md`](pipeline.md)) |
| Oro (108 meses), agregado DENUE, diccionario e interfaz | **Implementado y verificado** contra una derivación independiente |
| Pruebas del pipeline | Implementadas (datos sintéticos y reales declarados como tales) |
| `ci.yml` | **Ejecutado en GitHub con éxito** (trabajos `calidad` y `auditoria-dependencias`, ejecuciones del 2026-11-13 sobre `70a26b9`, `7e64ffa` y `49934ca`; ver [`pipeline.md`](pipeline.md) §6). El paso nuevo «oro regenerado = oro versionado» **aún no ha corrido en GitHub** |
| Dependencias estadísticas | Fijadas en `requirements-lab.txt` (`wrapt` estable 2.5.2); la instalación en Linux/GitHub ya corrió en CI |
| Transformaciones (min-max, z-score, discretización) | **Implementadas** en `pipeline/transformaciones.py`, con parámetros solo del entrenamiento y pruebas de ausencia de fuga ([`transformaciones.md`](transformaciones.md)). La **reducción** que pide E1 (muestreo, agregación o selección de variables, con el porcentaje; **no** PCA, que es de E2) está cubierta por la agregación del contrato §6 (453 → 108 filas, −76.2 %); ver `transformaciones.md` §6. Pendientes: comparación min-max frente a z-score en el laboratorio (integrante B) y jerarquías conceptuales |
| Exploración estadística | **Cuatro gráficas y estadísticas descriptivas** del oro ([`exploracion.md`](exploracion.md)). Faltan la descomposición y la correlación cruzada de la matriz de requisitos |
| Fiabilidad y disponibilidad | **Medidas con lo que hay** ([`fiabilidad.md`](fiabilidad.md)): tasa de éxito 83.3 % (5/6) y MTTR 268 s (n = 1). **MTBF y disponibilidad: no estimables** (1 incidente; 2.84 de 7 días de bitácora) |
| Requerimientos verificables | **Redactados** ([`requerimientos.md`](requerimientos.md)): 36 requerimientos con su criterio y verificación; 26 cumplidos, 5 parciales, 3 no cumplidos, 1 pendiente, 1 propuesto. **Revisión de la integrante B pendiente** |
| Plan SQA | **Borrador 1.0** con la estructura de IEEE 730 ([`plan_sqa.md`](plan_sqa.md)); pendiente de revisión de B |
| Seguridad | `pip-audit` sin hallazgos y restauración del bronce probada ([`seguridad.md`](seguridad.md)). `gitleaks` 8.30.1 ejecutado localmente el 2026-11-13 con **0 hallazgos** (historial y árbol de trabajo); **aún no está integrado en CI** |
| Pendiente (Leslie) | Integrar `gitleaks` en CI, ficha `docs/E1/ENTREGA.md`, relatoría `docs/relatoria-E1.md`, etiqueta `e1`, y completar la medición de fiabilidad cuando haya ≥ 7 días y ≥ 2 incidentes |
| Laboratorio de Eimy | Integrado en `main` (PR #9, `49934ca`); calculó con la capa oro (`--fuente oro`) y su CI pasó. Las pruebas estadísticas son obligatorias en CI (`TDL_EXIGIR_PRONOSTICOS=1`) |
