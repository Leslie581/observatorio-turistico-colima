# Contrato de datos E1 · bronce → plata → oro

Versión del contrato: **1.0.0 (fijada el 2026-11-13)** · 2026-11-13 · Rama `e1/leslie-contrato-datos` · Responsable: Leslie Valadez Macías (integrante A, datos). Consumidora principal: Eimy Melissa Urbina Meza (integrante B, pronósticos).
**Estado: fijado (1.0.0).** Lo descrito en §1 y en las verificaciones de §1.1 se **midió sobre los archivos reales** de `data/bronce/` el 2026-11-13; lo de §2 a §7 es el diseño aprobado, **implementado en `pipeline/`** (rama `e1/leslie-pipeline`, 2026-11-13). Decisiones tomadas (D1 a D7, con sus condiciones) y riesgos abiertos: §8. Correcciones posteriores a la primera fijación: §9. Los cambios incompatibles se acuerdan antes de implementarse (§7).

## 0. Para Eimy: lo mínimo para empezar
**Qué leer:** un solo archivo, `data/oro/manzanillo_ocupacion_mensual.csv` (se genera con `python -m pipeline.ejecutar`; la derivación de §7 da la misma serie con diferencias menores de 1e-6, por el redondeo a 6 decimales). **No leas bronce ni plata.**
**Esquema exacto** (columnas en este orden, CSV UTF-8, `,`, finales de línea LF, 108 filas, `periodo` ascendente y sin huecos, números con 6 decimales):
`periodo`, `fecha_inicio`, `ocupacion_pct`, `cuartos_disponibles`, `cuartos_ocupados`, `cuartos_ocupados_residentes`, `cuartos_ocupados_no_residentes`, `pct_cuartos_no_residentes`, `llegadas_turistas`, `turistas_noche`, `estadia_promedio`, `densidad_ocupacion`, `d_covid`, `d_oferta_2017`, `diag_atipico_iqr`, `categorias_incluidas`, `n_categorias_fuente`, `sha256_bronce`, `ejecucion`, `version_contrato`.
**Variable objetivo (fórmula exacta):** para cada mes y las categorías `2 estrellas`, `3 estrellas`, `4 estrellas` y `5 estrellas` de Manzanillo,
`ocupacion_pct = 100 × Σ(cuartos_ocupados_residentes + cuartos_ocupados_no_residentes) / Σ(cuartos_disponibles)`.
Es un cociente de sumas (cuartos-noche), **no** un promedio de porcentajes por categoría (ambos difieren hasta 12.8 puntos, §1.1).
**Partición temporal:** entrenamiento `2016-01` a `2023-12` (**96 meses**); prueba `2024-01` a `2024-12` (**12 meses**). Nada de 2024 se usa para ajustar, normalizar ni elegir parámetros.
**Quiebres que debes señalar, no borrar:** `d_oferta_2017` (1 desde 2017-06) y `d_covid` (1 de 2020-03 a 2021-06). Los valores extremos de 2020-04 a 2020-06 son reales: no se eliminan.
**Variables adicionales:** `pct_cuartos_no_residentes`, `estadia_promedio` y `densidad_ocupacion` son **exploratorias**. No son regresores por defecto (riesgo de correlación mecánica y de disponibilidad, §4.1). Para ARIMA/SARIMA con exógenas solo se permiten **rezagadas** y justificadas.
**Interfaz** (`pipeline/interfaz.py`, implementada en la rama `e1/leslie-pipeline`; `cargar_oro_mensual` valida el archivo antes de entregarlo): `cargar_oro_mensual(ruta=None)`, `serie_objetivo(df=None)`, `partir_entrenamiento_prueba(serie, h=12)`. Tu código vive en `laboratorio/pronosticos/` y tus pruebas en `tests/test_laboratorio_*.py`.
**Si algo no cuadra con el contrato**, avisa antes de adaptarlo por tu cuenta: se corrige aquí con un incremento de versión.

## 1. Diagnóstico de las fuentes reales

### 1.1 DATATUR · `data/bronce/datatur/Base70centros.csv`
| Aspecto | Hallazgo (medido) |
|---|---|
| Formato | TSV UTF-8 sin BOM, finales de línea CRLF, 31,147 filas de datos y 13 columnas; SHA-256 `a8ca3f9b…d671` (igual a su ficha) |
| Columnas | `anio`, `mes` (texto `01`..`12`), `tipo_centro`, `subtipo_centro`, `centro`, `categoria` y 7 conteos: `cuartos_disponibles`, `cuartos_ocupados_residentes`, `cuartos_ocupados_no_residentes`, `llegada_turistas_residentes`, `llegada_turistas_no_residentes`, `turistas_noche_residentes`, `turistas_noche_no_residentes` |
| Identificador de destino | No hay código: el destino es el **texto** `centro` (64 valores). `Manzanillo` aparece con una sola grafía, tipo `Centros de Playa` / subtipo `Tradicionales` |
| Periodicidad y cobertura | Mensual, 2016-01 a 2024-12. **Manzanillo: 108 periodos, sin huecos y sin duplicados** `(anio, mes, categoria)`; 453 filas |
| Categorías de Manzanillo | `2`, `3`, `4` y `5 estrellas`: 108 meses cada una. **`1 estrella`: solo 21 meses (2016-01 a 2017-09)** y desaparece: la composición del total cambia en 2017-10 |
| Unidades | Los `cuartos_*` son **totales mensuales en cuartos-noche**; `llegada_*` son personas; `turistas_noche_*` son personas-noche. Se ve en que la oferta diaria implícita (`cuartos_disponibles` / días del mes) es del orden de 3,373 cuartos al día en 2016-01 con 2 a 5 estrellas (3,551 con las 5 categorías) |
| Faltantes (todo el archivo) | **1 celda vacía** de 31,147 × 7: `turistas_noche_residentes` de Mexicali, 5 estrellas, 2020-03. **El Fuerte** no tiene los 12 meses de 2024 (96 periodos). 4 centros incluyen la categoría `Sin categoría`. **Manzanillo: sin faltantes** |
| Rangos y anomalías | 0 negativos. **2 filas con ocupados > disponibles**, ambas de Ciudad Juárez, 2 estrellas: 2021-07 y 2022-06. Manzanillo: 0 |
| Variable objetivo | `ocupacion_pct` = 100 × (ocupados residentes + no residentes) / disponibles, agregando categorías. Con **2 a 5 estrellas**: media 45.86, mín. 1.46 (2020-04), máx. 66.34 |
| Quiebres visibles (**2 a 5 estrellas**) | **Oferta diaria implícita:** +30.5 % en 2017-06 y +17.0 % en 2017-11 (cambio de marco, no crecimiento; en el total mensual de cuartos-noche son +26.3 % y +13.2 %). **COVID:** 2020-03 a 2021-06, ocupación media 25.55 % frente a 49.39 % en el resto. Atípicos por IQR: 2020-04, 2020-05 y 2020-06 (eventos reales, no errores) |
| Viabilidad para pronóstico | **Sí.** 108 meses útiles (supera los 36 exigidos). Series homogéneas más cortas: 2018-01 a 2024-12 (84 meses) y 2021-07 a 2024-12 (42 meses) |

### 1.1b Verificación de la variable objetivo (2026-11-13)
Comprobada con las columnas reales, mes a mes, sobre Manzanillo:
| Comprobación | Resultado |
|---|---|
| Fórmula | `100 × Σ(ocupados residentes + no residentes) / Σ(disponibles)` sumando las categorías `2` a `5 estrellas` de cada mes. En esta base **no hay una fila “Total”** ni categorías agregadas (0 filas con “total”); las categorías son solo `1` a `5 estrellas` |
| Duplicados | 0 repetidos `(periodo, categoria)`; los 108 meses tienen exactamente las 4 categorías |
| Ponderada frente a promedio simple | El promedio simple de los porcentajes por categoría difiere de la fórmula ponderada hasta **12.82 puntos** (2023-09) y en 90 de 108 meses más de 0.5 puntos. Por eso **no se promedian porcentajes** |
| Integridad | Ocupados ≤ disponibles en todas las filas; sin nulos ni divisiones por cero |
| Punto de control externo | Con todas las categorías de Manzanillo, enero a septiembre de 2023 da 4,373.5 cuartos disponibles al día, 2,423.8 ocupados al día y 55.42 % de ocupación. El prototipo documentó 4,373, 2,423 y 55.4 % como cifras del reporte oficial `2025-MES_09_Publico.pdf` (esa cifra del PDF **no se re-verificó aquí**) |
| Partición | 2016-01 a 2023-12 = 96 meses; 2024-01 a 2024-12 = 12 meses |
**Por qué se excluye `1 estrella`:** solo existe en 21 meses (2016-01 a 2017-09) y desaparece desde 2017-10; aportaba 4.73 % de los cuartos disponibles de ese tramo. Incluirla cambia la serie hasta **2.26 puntos** (media de −1.47 puntos en esos 21 meses) y **mezcla un cambio de composición con la variación real**; desde 2017-10 ambas definiciones son idénticas. Con `2 a 5 estrellas` la composición es constante en los 108 meses.


### 1.2 DENUE · `data/bronce/denue/<fecha>/…_BuscarAreaAct.json`
| Aspecto | Hallazgo (medido) |
|---|---|
| Capturas | 5 archivos (4 fechas; el 2026-11-09 tiene dos capturas del mismo día). Cada uno: lista JSON de **134** registros y **23 campos**; `Cuantificar` = 134 |
| Estabilidad | Las 5 capturas tienen **los mismos 134 `CLEE` y 0 celdas distintas**: es una foto, no una serie temporal |
| Campos | `CLEE`, `Id`, `Clase_actividad`, `CLASE_ACTIVIDAD_ID`, `Estrato`, `Tipo_vialidad`, `Colonia`, `CP`, `Ubicacion`, `Tipo`, `Longitud`, `Latitud`, `AGEB`, `Manzana`, `AreaGeo`, `Tipo_Asentamiento`, `Fecha_Alta` y claves SCIAN (`SECTOR`, `SUBSECTOR`, `RAMA`, `SUBRAMA`); `tipo_corredor_industrial` y `nom_corredor_industrial` vacíos en los 134 |
| Identificadores | `CLEE` (único, 134/134) e `Id` (único). Sin duplicados dentro de una captura |
| Municipio y actividad | `AreaGeo` 06007xxxx (Manzanillo, Colima); SCIAN subsector 721. Clases: hoteles sin otros servicios 43, con otros servicios 42, departamentos y casas amueblados 22, cabañas y villas 12, pensiones y casas de huéspedes 9, moteles 6 |
| Tamaño | `Estrato` es **personal ocupado**, no cuartos: `0 a 5` 63, `6 a 10` 30, `11 a 30` 27, `31 a 50` 5, `51 a 100` 4, `101 a 250` 1, `251 y más` 4 |
| Faltantes | Ninguno, salvo los dos campos de corredor industrial. Coordenadas: 134/134 numéricas dentro de Manzanillo |
| `Fecha_Alta` | Formato `AAAA-MM`, de 2010-07 a 2026-04. Solo hay **altas**, no bajas |
| Privacidad | Ya se excluyen del bronce `Nombre`, `Razon_social`, contacto y domicilio (`Calle`, números, edificio, local). Verificado: ninguno de esos campos aparece en los 5 archivos |

## 2. Capa plata
Reglas generales: una función pura por dataset; **nunca se escribe en bronce**; cada fila de plata lleva su procedencia; CSV UTF-8, `,` como separador, finales de línea **LF** (el pipeline debe forzar `lineterminator="\n"`), fechas ISO `AAAA-MM-DD` y periodos `AAAA-MM`.

### 2.1 `data/plata/datatur_base70.csv`
Clave de unicidad: `(periodo, centro, categoria)`. Una fila por fila válida de Base70 (todos los centros, para que E3 no requiera reprocesar).
| Columna | Tipo | Unidad / regla |
|---|---|---|
| `periodo` | texto `AAAA-MM` | de `anio` y `mes`; mes 01–12 |
| `centro`, `tipo_centro`, `subtipo_centro`, `categoria` | texto | sin espacios en los extremos; valores tal cual |
| `cuartos_disponibles`, `cuartos_ocupados_residentes`, `cuartos_ocupados_no_residentes` | entero ≥ 0 | cuartos-noche al mes |
| `llegada_turistas_residentes`, `llegada_turistas_no_residentes` | entero ≥ 0 | personas |
| `turistas_noche_residentes`, `turistas_noche_no_residentes` | entero ≥ 0, **nulo permitido** | personas-noche |
| `faltante_turistas_noche` | booleano | verdadero si alguno de los dos es nulo |
| `fila_origen`, `sha256_bronce` | entero, texto | línea del CSV de bronce y huella del archivo |

### 2.2 `data/plata/denue_establecimientos.csv`
Clave de unicidad: `(fecha_captura_local, clee)`; si hay más de una captura el mismo día se conserva la **última** y se registra `capturas_del_dia`.
Columnas: `fecha_captura_local` (zona America/Mexico_City, a partir de `capturado_utc` de la ficha), `clee`, `id`, `clase_actividad`, `scian_clase` (de `CLASE_ACTIVIDAD_ID`, texto de 6 dígitos), `estrato`, `personal_min`, `personal_max` (derivados de `Estrato`; `251 y más` → máximo nulo), `colonia`, `cp`, `localidad` (de `Ubicacion`), `municipio_clave` (`AreaGeo[:5]` = `06007`), `ageb`, `manzana`, `tipo_asentamiento`, `latitud`, `longitud`, `fecha_alta` (primer día del mes), `capturas_del_dia`, `ejecucion`, `archivo_bronce`, `sha256_bronce`.
Se descartan: `Tipo`, `SECTOR`, `SUBSECTOR`, `RAMA`, `SUBRAMA` y los dos campos de corredor industrial (constantes o vacíos), y `Tipo_vialidad` (detalle de domicilio que el proyecto ya minimiza). Es una reducción de columnas documentada.

### 2.3 Reglas de validación y limpieza (puerta de calidad)
Herramienta: **pandera** (instalada y en uso en el pipeline: `pipeline/calidad/`). Cada regla tiene identificador; el rechazo produce una fila de cuarentena.
| ID | Dataset | Regla | Si falla |
|---|---|---|---|
| R-D01 | Base70 | Columnas exactas y tipos (§1.1) | Se detiene el lote (esquema cambiado) |
| R-D02 | Base70 | `mes` en 01–12 y `anio` entero 2016–2030 | Fila a cuarentena |
| R-D03 | Base70 | Clave `(periodo, centro, categoria)` única | Duplicados a cuarentena (se conserva la primera) |
| R-D04 | Base70 | Conteos ≥ 0 y enteros | Fila a cuarentena |
| R-D05 | Base70 | `cuartos_disponibles` > 0 | Fila a cuarentena |
| R-D06 | Base70 | ocupados (res. + no res.) ≤ disponibles | Fila a cuarentena (hoy: Ciudad Juárez 2021-07 y 2022-06) |
| R-D07 | Base70 | Faltantes: se **marcan**, no se imputan en plata | `faltante_turistas_noche`; hoy: Mexicali 2020-03 |
| R-D08 | Base70 | Cobertura por centro: 108 periodos | Informativo: El Fuerte queda con 96 y se excluye de series que exigen 108 |
| R-E01 | DENUE | `CLEE` e `Id` no vacíos; `CLEE` único por captura | Fila a cuarentena |
| R-E02 | DENUE | Total de registros / `Cuantificar` entre 0.98 y 1.02 | Se rechaza el lote completo |
| R-E03 | DENUE | `AreaGeo` empieza con `06007`; subsector 721; clase dentro del catálogo SCIAN 721 | Fila a cuarentena |
| R-E04 | DENUE | Latitud y longitud numéricas dentro de Colima | Fila a cuarentena |
| R-E05 | DENUE | Ninguno de los campos excluidos por privacidad (lista en `extractores/denue.py`) | Se rechaza el lote completo y se registra como incidente de seguridad |
| R-E06 | DENUE | `Fecha_Alta` con formato `AAAA-MM` y no posterior a la captura | Fila a cuarentena |

**Faltantes (diagnóstico requerido por la rúbrica).** En Manzanillo no hay ninguno. En el resto del archivo solo existe 1 celda vacía (Mexicali, 2020-03), cuyo mecanismo **no se puede determinar con un solo caso** (coincide con el inicio de la pandemia); y 12 meses ausentes de El Fuerte, que son una ausencia estructural (probablemente no registrada, “no al azar”). Tratamiento: **no imputar en E1**; marcar y excluir la fila de las derivadas que la usan.
**Duplicados.** Base70: 0. DENUE: las repeticiones entre capturas son esperadas (fotos); se resuelven por la clave `(fecha_captura_local, clee)`.
**Atípicos.** Método: IQR 1.5 sobre `ocupacion_pct`. Decisión: **marcar, no corregir ni eliminar**, 2020-04 a 2020-06 (COVID, evento real); filas con ocupados > disponibles: **cuarentena** (error de captura). **Ampliado el 2026-11-14:** el diagnóstico de faltantes con simulación de tratamientos y la comparación del IQR con el puntaje z robusto están en [`faltantes_y_atipicos.md`](faltantes_y_atipicos.md) (los dos métodos coinciden en los 3 meses de COVID).

## 3. Cuarentena
- Ubicación: `data/cuarentena/<fuente>/<corrida>/rechazados.csv` y `data/cuarentena/resumen_<corrida>.json`, con `fuente` = `datatur_base70` o `denue_establecimientos` y `corrida` = `e1-` más 12 caracteres del hash de las entradas (determinista). El bronce **no se modifica nunca**.
- Cada fila rechazada conserva **todas** las columnas originales más: `regla_id`, `motivo_rechazo` (texto legible), `fila_origen`, `archivo_bronce`, `sha256_bronce`, `fecha_proceso_utc`. Los lotes rechazados completos (R-D01, R-E02, R-E05) dejan solo el resumen y el motivo.
- El resumen JSON cuenta, por regla: registros leídos, aceptados y rechazados. Es la evidencia que muestra “cuántos registros rechazó y por qué”. **Ningún registro se borra en silencio**: lo leído = aceptado + rechazado + marcado.

## 4. Capa oro
### 4.1 Dataset principal: `data/oro/manzanillo_ocupacion_mensual.csv`
Una fila por mes, **108 filas esperadas**, ordenadas por `periodo` ascendente, sin huecos. Clave: `periodo`.
| Columna | Tipo | Definición |
|---|---|---|
| `periodo` | texto `AAAA-MM` (clave) | mes de referencia |
| `fecha_inicio` | fecha | primer día del mes |
| `ocupacion_pct` | decimal 0–100 (**variable objetivo**), 6 decimales | `100 × Σ(cuartos_ocupados_residentes + cuartos_ocupados_no_residentes) / Σ(cuartos_disponibles)` de las categorías **2 a 5 estrellas** de Manzanillo en ese mes. Cociente de sumas, no promedio de porcentajes |
| `cuartos_disponibles`, `cuartos_ocupados`, `cuartos_ocupados_residentes`, `cuartos_ocupados_no_residentes` | entero | suma de las 4 categorías, cuartos-noche al mes |
| `pct_cuartos_no_residentes` | decimal 0–100 | 100 × no residentes / `cuartos_ocupados` |
| `llegadas_turistas`, `turistas_noche` | entero | suma de residentes y no residentes |
| `estadia_promedio` | decimal | `turistas_noche` / `llegadas_turistas` (noches) |
| `densidad_ocupacion` | decimal | `turistas_noche` / `cuartos_ocupados` (personas por cuarto) |
| `d_covid` | 0/1 | 1 de 2020-03 a 2021-06 (regla de calendario, conocida de antemano) |
| `d_oferta_2017` | 0/1 | 1 desde 2017-06 (primer salto de la oferta; calendario). El segundo salto (2017-11) **no** tiene columna en 1.0.0; ver la nota de abajo |
| `diag_atipico_iqr` | 0/1 | **solo diagnóstico**: se calcula con toda la serie, **no usar como regresor** |
| `categorias_incluidas`, `n_categorias_fuente` | texto, entero | `2-5 estrellas` y 4 |
| `sha256_bronce`, `ejecucion`, `version_contrato` | texto | procedencia y versión |

Además: `data/oro/manzanillo_ocupacion_mensual.meta.json` (filas, periodo mínimo y máximo, hash de bronce, versión del contrato, fecha de proceso) y `data/oro/diccionario_datos.csv` (columna, tipo, unidad, definición, fuente, regla de cálculo), que es el diccionario exigido por la rúbrica.
**Segundo salto de oferta (2017-11, +17.0 %).** No hay un indicador específico en 1.0.0. Verificado con 2 a 5 estrellas: la ocupación, que es un cociente, **no muestra un cambio de nivel** en esas fechas (media 2017-06 a 2017-10: 48.5 % frente a 47.6 % en los mismos meses de 2016; 2017-11 a 2018-03: 51.9 % frente a 52.1 %), así que no afecta a los modelos de ocupación. La regla de calendario `periodo >= 2017-11` la puede derivar cualquier consumidor (por ejemplo, para analizar la oferta absoluta, que sí está en `cuartos_disponibles`). Si se necesita como columna del oro, será un cambio de esquema (1.1.0) y no se hace ahora para no invalidar el laboratorio, validado contra 1.0.0.

**Variables adicionales (D7, aceptadas provisionalmente).** Todas existen o se derivan de columnas reales; ninguna tiene nulos ni denominadores cero en los 108 meses. **Ninguna es regresor predictivo por defecto.**
| Variable | Fórmula | Unidad | Rango observado (108 meses, descriptivo) | Disponibilidad y riesgos |
|---|---|---|---|---|
| `pct_cuartos_no_residentes` | 100 × `cuartos_ocupados_no_residentes` / `cuartos_ocupados` | % | 0.38 – 16.24 | Comparte numerador y denominador con el objetivo (`ocupacion_pct` = componente residente + no residente sobre los mismos disponibles). Correlación contemporánea con el objetivo 0.191 (solo entrenamiento), pero **−0.022 sin los meses de COVID**: el vínculo lo genera la pandemia |
| `estadia_promedio` | `turistas_noche` / `llegadas_turistas` | noches | 1.68 – 3.04 | Se publica en el mismo reporte y mes que el objetivo, así que **no se conoce antes** de él. Correlación con el objetivo 0.223 (solo entrenamiento; 0.111 sin COVID) |
| `densidad_ocupacion` | `turistas_noche` / `cuartos_ocupados` | personas por cuarto | 1.41 – 3.00 | Tiene `cuartos_ocupados` en el denominador, el mismo numerador del objetivo: **dependencia mecánica**. Correlación 0.650 (solo entrenamiento; 0.516 sin COVID) |
**Todas las correlaciones de esta tabla usan solo el entrenamiento (2016-01 a 2023-12, 96 meses)**; la versión inicial las calculaba con los 108 meses, incluida la prueba, y esas cifras no deben usarse para elegir regresores. Los rangos observados describen los 108 meses y no se usan para ajustar nada.

**Riesgos comunes.** (1) **Correlación mecánica:** el objetivo es casi idéntico a su componente residente (`cuartos_ocupados_residentes` / `cuartos_disponibles` correlaciona 0.994 con él, solo entrenamiento), así que **no deben usarse como regresores los componentes del mismo mes**. (2) **Disponibilidad:** Base70 se publica con rezago (la versión usada, de julio de 2025, termina en 2024-12); el rezago mínimo operativo **no está verificado**. (3) **Uso permitido en E1:** correlación cruzada **exploratoria** (requisito de E1) y, si se justifica, regresores **rezagados**; con rezago 1 las correlaciones con el objetivo (solo entrenamiento) son 0.181, 0.102 y 0.403. No hay variable climática: no se capturó.

### 4.2 Restricciones contra fuga de información
1. El oro **no contiene transformaciones ajustadas con toda la serie** (media, desviación, mínimos, máximos). Normalizar (min-max, z-score) se hace en el laboratorio, ajustando los parámetros **solo con el tramo de entrenamiento**.
2. **Partición aprobada (D2):** entrenamiento 2016-01 a 2023-12 (**96 meses**) y prueba 2024-01 a 2024-12 (**12 meses**). Constante `H_PRUEBA = 12`. No se imputa ni se suaviza con datos posteriores al corte.
3. Cualquier regresor debe estar disponible **antes** del mes que se pronostica (rezagos, calendario). `diag_atipico_iqr` queda prohibido como regresor, y las variables adicionales de §4.1 no entran como regresores sin justificación escrita.
4. El oro se regenera completo; no se editan filas a mano.

### 4.3 Qué se versiona en Git (D5, aprobada)
Solo datos **públicos, agregados, pequeños y reproducibles**: `data/oro/*.csv`, `data/oro/*.json` (incluye el diccionario y el `.meta.json`). El `.meta.json` lleva la atribución obligatoria de la fuente (SECTUR/DataTur, CC BY 4.0, e INEGI, libre uso con crédito), el hash de bronce y la versión del contrato. **No se versionan**: `data/plata/`, `data/cuarentena/` (salvo `resumen_<ejecucion>.json`, que son conteos), archivos Parquet ni nada de `evidencias_privadas/`. Los datos con coordenadas o a nivel de establecimiento (DENUE) permanecen en plata local.

## 5. Integración DATATUR + DENUE
| Tema | Decisión |
|---|---|
| Nivel compatible | **Municipio de Manzanillo (06007)**, descriptivo y agregado. DATATUR mide un centro turístico por categoría de estrellas, en cuartos-noche; DENUE lista establecimientos, con personal ocupado y coordenadas |
| Vinculación posible | **Solo una dimensión de contexto**: `data/oro/manzanillo_oferta_hospedaje.csv`, con conteos por `scian_clase` y `estrato` a la fecha de captura (`fecha_captura_local`, `municipio_clave`, `clase_actividad`, `estrato`, `establecimientos`, `personal_min_total`) y **sin coordenadas ni `clee`** (versión pública agregada) |
| Resolución de conflictos | Nombre de destino: `Manzanillo` (texto) ↔ `06007` (clave INEGI) con una tabla fija de equivalencia de un renglón; fechas: `AAAA`+`MM` (texto) ↔ `AAAA-MM` ↔ ISO UTC, todas llevadas a `AAAA-MM`/`AAAA-MM-DD`; unidades: cuartos-noche ↔ establecimientos y personal, **sin convertir una a la otra**; duplicados: por `(fecha_captura_local, clee)` |
| Limitaciones temporales | DENUE tiene **una sola foto** (4 días con contenido idéntico) y solo altas; no existe una serie mensual de oferta. No es un regresor del pronóstico |
| Limitaciones geográficas | DENUE cubre todo el municipio; DATATUR, el centro turístico. Pueden no coincidir |
| Prohibido | Asignar ocupación a un establecimiento, estimar cuartos por hotel a partir del personal, o relacionar una variable mensual de DATATUR con un conteo de DENUE como si fuera una serie |
| Alternativa defendible | Presentar la oferta DENUE como contexto en el tablero (conteos por clase y tamaño) junto a la serie; para E2 se usa con coordenadas en la capa plata (no pública) |
| Derivada válida con cautela | Establecimientos dados de alta por año (`fecha_alta`), indicando que **no incluye bajas** |

## 6. Transformaciones que pide la rúbrica de E1 (dónde viven)
| Requisito | Diseño |
|---|---|
| Normalización y estandarización (min-max y z-score) con análisis comparativo | En el laboratorio, ajustadas con el entrenamiento (§4.2). Funciones puras reutilizables en `pipeline/transformaciones.py` |
| Discretización y jerarquías | `ocupacion_nivel` (bajo, medio, alto) por **terciles del entrenamiento** y, desde el 2026-11-14, la discretización supervisada (§8 de [`transformaciones.md`](transformaciones.md)). **Jerarquías implementadas** como dimensiones aparte del oro mensual: `dim_tiempo` (año → trimestre → mes), `dim_geografia` (estado → municipio → centro turístico) y `dim_ubicacion_denue` (estado → municipio → localidad → colonia); véase [`pipeline.md`](pipeline.md) §3.1 |
| Reducción de datos | Agregación de categoría × mes a mes (**453 → 108 filas en Manzanillo, −76.2 %**; 31,147 → 108 si se parte de todo Base70, −99.65 %), descartando las columnas constantes de DENUE. Se pierde el detalle por categoría de estrellas |
| Integración de fuentes | §5 |
| Puerta de calidad con cuarentena | §2.3 y §3 |
| Capas plata y oro automáticas con diccionario | §2, §4 y el diccionario de §4.1 |

## 7. Interfaz entre el módulo de datos y el estadístico
- **Contrato de lectura:** el laboratorio de pronósticos **solo lee** `data/oro/manzanillo_ocupacion_mensual.csv` (y su `.meta.json`); no importa nada de plata ni de bronce.
- **Módulo de interfaz** (implementado): `pipeline/interfaz.py` con
  - `cargar_oro_mensual(ruta=None) -> DataFrame` indexado por `PeriodIndex` mensual (`periodo`), ordenado, con las columnas de §4.1;
  - `serie_objetivo(df=None) -> Series` (`ocupacion_pct`);
  - `partir_entrenamiento_prueba(serie, h=12) -> (entrenamiento, prueba)`.
  La derivación de referencia, útil para contrastar el oro de forma independiente y **verificada el 2026-11-13** (devuelve 108 meses; mín. 1.46, máx. 66.34, media 45.86):
```python
from extractores.datatur import leer_base70
df = leer_base70("data/bronce/datatur/Base70centros.csv")
m = df[(df.centro == "Manzanillo") & df.categoria.isin(["2 estrellas", "3 estrellas", "4 estrellas", "5 estrellas"])]
g = m.groupby("periodo")[["cuartos_disponibles", "cuartos_ocupados_residentes", "cuartos_ocupados_no_residentes"]].sum().astype(float)
serie = (100 * (g.cuartos_ocupados_residentes + g.cuartos_ocupados_no_residentes) / g.cuartos_disponibles).rename("ocupacion_pct")
serie.index = serie.index.to_period("M")
```
- **Cambios al contrato:** se anuncian con un incremento de `version_contrato` y una nota en este archivo; los cambios incompatibles (renombrar o quitar columnas) se acuerdan antes de la implementación.

## 8. Decisiones tomadas y riesgos abiertos
Decisiones aprobadas por la integrante A el 2026-11-13, con las condiciones indicadas. La integrante B las revisó al escribir su laboratorio y las encontró conformes, con dos observaciones sobre las cifras de §1.1 y el indicador de 2017-11 ([`pronostico.md`](pronostico.md) §1).
| # | Decisión | Resolución | Condición cumplida |
|---|---|---|---|
| D1 | Variable objetivo | **2 a 5 estrellas**, cociente de sumas | Fórmula comprobada con las columnas reales; no es un promedio de porcentajes; exclusión de `1 estrella` documentada (§1.1b); sin duplicados ni totales |
| D2 | Partición | Entrenamiento 2016–2023 (96 meses), prueba 2024 (12 meses) | Conteo verificado |
| D3 | 2017 y COVID | Se **conservan y se señalan** con `d_oferta_2017` y `d_covid`; los extremos legítimos de 2020 no se eliminan | Atípicos solo marcados (`diag_atipico_iqr`) |
| D4 | Formato | CSV + JSON como formato principal; Parquet queda fuera | — |
| D5 | Versionado | Se versiona `data/oro/` solo si es público, agregado, pequeño y reproducible (§4.3) | Cambio mínimo de `.gitignore` en esta rama |
| D6 | DENUE | Solo como **contexto agregado** a nivel municipio; sin atribuir ocupación a hoteles | §5 |
| D7 | Variables adicionales | Aceptadas **provisionalmente**, sin convertirlas en regresores | Fórmulas, unidades, disponibilidad y riesgos en §4.1 |

### Riesgos abiertos
| # | Riesgo | Propuesta |
|---|---|---|
| R1 | **Fecha límite:** el PDF fija E1 para el 13 de noviembre | Priorizar la puerta de datos, el oro y el diccionario; declarar lo que no se alcance |
| R2 | **Fiabilidad con 7 días de bitácora:** hay capturas desde el 2026-11-09 (3 programadas del 10 al 12) | Calcular con lo disponible y declarar el periodo real; no completar con simulaciones |
| R3 | Dependencias nuevas (`pandera`, `statsmodels`, `matplotlib`, `scipy`, `pip-audit`, `ruff`) | La resolución con `pandas 3.0.5` funciona en simulación (`pip --dry-run`); **falta comprobar que se importen** en esta máquina (el Control de aplicaciones de Windows ya bloqueó `pandas 3.1.1`) |
| R4 | `gitleaks` es un binario externo | Verificar si puede ejecutarse localmente o solo en CI |
| R5 | Base70 es una versión del 15-jul-2025 y puede tener revisiones retroactivas | Se verifica el hash antes de procesar |

## 9. Registro de cambios
| Fecha | Cambio | Versión del esquema |
|---|---|---|
| 2026-11-13 | Contrato fijado (L0), con las condiciones D1 a D7 | **1.0.0** |
| 2026-11-13 | **Revisión de documentación r1** (L1), a partir de las tres observaciones de la integrante B, verificadas con los datos: (1) las cifras de oferta y COVID de §1.1 se habían calculado con las 5 categorías y se recalcularon con 2 a 5 estrellas; (2) se documenta que el segundo salto de oferta (2017-11) no tiene indicador y por qué no hace falta; (3) las correlaciones de §4.1 se recalcularon solo con el entrenamiento | **1.0.0** (sin cambio) |
| 2026-11-13 | Aclaración de implementación: `ejecucion` del oro es un identificador determinista de entrada + contrato (`oro-<12 hex del hash de bronce>-v1.0.0`), no un instante; el instante va en `meta.json` | 1.0.0 (sin cambio) |
| 2026-11-14 | **Se agregan tres dimensiones** al oro (`dim_tiempo.csv`, `dim_geografia.csv` y `dim_ubicacion_denue.csv`) y 18 entradas al diccionario. **El oro mensual no cambia** (mismas 20 columnas, mismo contenido byte a byte): son archivos nuevos, no una versión nueva del esquema | 1.0.0 |

**Por qué la versión del esquema sigue en 1.0.0.** La versión (`version_contrato`) identifica el **esquema, las fórmulas y las decisiones** del oro, y el laboratorio de pronósticos valida el archivo contra `1.0.0`. Las tres correcciones corrigen cifras descriptivas y aclaran reglas, sin tocar columnas, fórmulas ni decisiones, de modo que subir la versión habría invalidado sin motivo el trabajo ya validado. Un cambio de columnas, de fórmula o de una decisión (por ejemplo, un indicador `d_oferta_2017_11`) incrementará la versión (1.1.0 o 2.0.0) y se acordará antes con la integrante B.
