# Transformaciones de la variable objetivo (E1)

Rama `e1/leslie-l2` · 2026-11-13 · Responsable: Leslie Valadez Macías (integrante A). Código: [`pipeline/transformaciones.py`](../../pipeline/transformaciones.py). Pruebas: [`tests/test_pipeline_transformaciones.py`](../../tests/test_pipeline_transformaciones.py). Cifras de la corrida real: [`parametros_transformaciones.json`](../../laboratorio/exploracion/resultados/parametros_transformaciones.json) y [`transformaciones_ocupacion.csv`](../../laboratorio/exploracion/resultados/transformaciones_ocupacion.csv) (se regeneran con `python -m laboratorio.exploracion.explorar`).

## 1. Regla central: ajustar con el entrenamiento, aplicar a la prueba
La partición del contrato (D2) es **entrenamiento 2016-01 a 2023-12 (96 meses)** y **prueba 2024-01 a 2024-12 (12 meses)**. Cada transformación tiene dos pasos separados:
1. `ajustar_*(entrenamiento)` calcula los parámetros y **rechaza** (`ErrorFuga`) cualquier serie que contenga un solo mes posterior a 2023-12, o que no tenga índice mensual (sin fechas no se puede garantizar que no haya fuga).
2. `aplicar_*(x, parámetros)` usa los parámetros ya fijados y **no recalcula nada**, de modo que 2024 se transforma con los parámetros de 2016–2023.

Los parámetros son objetos inmutables que guardan cuántos meses y hasta qué periodo se ajustaron. `transformar_serie_oro(serie)` hace el flujo completo (partición del contrato, ajuste, aplicación a ambos conjuntos).

## 2. Qué se implementó
| Transformación | Fórmula | Parámetros (solo 2016–2023) |
|---|---|---|
| **Min-max** | `(x − mín) / (máx − mín)` | mín = 1.459077 (2020-04), máx = 66.339892 |
| **Z-score** | `(x − μ) / σ`, con σ poblacional (`ddof=0`, como `StandardScaler`) | μ = 44.7518, σ = 12.7659 |
| **Discretización por frecuencia igual** (por defecto) | 3 niveles ordinales (`bajo`, `medio`, `alto`) con bordes en los terciles del entrenamiento | bordes 41.7547 y 51.3579 |
| **Discretización por ancho igual** | 3 intervalos de igual ancho entre el mín y el máx del entrenamiento | bordes 23.0860 y 44.7130 |

Intervalos `[borde_i, borde_i+1)`. Los extremos son abiertos: un valor de prueba fuera del rango de entrenamiento cae en el nivel extremo, no genera un nivel nuevo. Los faltantes se conservan como faltantes (no se imputan) y el entrenamiento no admite faltantes. Las inversas (`invertir_minmax`, `invertir_zscore`) devuelven a puntos porcentuales los valores transformados, por ejemplo, para expresar un pronóstico en la escala original.

**Nota: desviación estándar poblacional frente a muestral.** El z-score de este módulo usa la desviación **poblacional** (`ddof=0`, divide entre n, como `StandardScaler`): σ = **12.7659** en el entrenamiento (n = 96). La desviación **muestral** (`ddof=1`, divide entre n − 1) es **12.8329**, un 0.5 % mayor. Las tablas descriptivas de [`exploracion.md`](exploracion.md) usan la **muestral** (12.83 en el entrenamiento, 12.60 en los 108 meses). Sin los meses de COVID (80 meses de entrenamiento) valen 8.5704 (poblacional) y 8.6244 (muestral). Ambas son correctas; **no deben mezclarse** en una misma comparación, y el z-score del §2 se calcula con la poblacional.

## 3. Resultado con los datos reales (descriptivo)
- **2024 queda dentro del rango de entrenamiento:** min-max entre 0.671 y 0.923 (ningún mes fuera de [0, 1]); z-score entre 0.02 y 1.30.
- **Frecuencia igual:** el entrenamiento se reparte 32/32/32 por construcción; 2024 cae en 0 `bajo`, 3 `medio` y 9 `alto`.
- **Ancho igual:** el entrenamiento queda 6 `bajo`, 33 `medio` y 57 `alto`; los 12 meses de 2024 caen en `alto`.
- El desbalance de 2024 en los niveles **no es un error**: refleja que 2024 (media 54.73 %) está por encima de la media de entrenamiento (44.75 %). Es una observación sobre los datos, no una explicación.

## 4. Cuándo conviene cada una y sus limitaciones
**Min-max.** Conviene cuando el método necesita una escala acotada o comparable entre variables (redes, métodos basados en distancias, comparación de gráficas en [0, 1]). *Limitaciones:* depende de dos valores extremos; aquí el mínimo es el mes más bajo del COVID (1.46 %), de modo que un mes típico (mediana de entrenamiento 48.11 %) queda en 0.72 y la zona habitual de la serie se comprime en la parte alta del intervalo. Un valor posterior fuera del rango de entrenamiento sale de [0, 1] y **no se recorta** (recortar escondería el cambio); la fórmula es sensible a un solo atípico.

**Z-score.** Conviene para modelos lineales, regresión penalizada, PCA y para expresar «cuántas desviaciones se aleja un mes de lo habitual en el entrenamiento». *Limitaciones:* μ y σ incluyen los meses de COVID. Sin ellos, la media de entrenamiento es 48.59 % frente a 44.75 %, y la desviación pasa de **12.7659 a 8.5704 en la versión poblacional** (la que usa el z-score) o de **12.8329 a 8.6244 en la muestral** (véase la nota sobre la desviación estándar). El mes más bajo queda en −3.39. No normaliza la forma: la serie tiene asimetría negativa (−1.13 en entrenamiento), así que z-score no la vuelve «normal». Tampoco corrige tendencia ni estacionalidad.

**Discretización.** Conviene cuando se necesita una lectura ordinal para el cliente («ocupación baja, media o alta») o para métodos que trabajan con categorías. *Limitaciones:* pierde información (dos meses de 42 % y 51 % comparten nivel) y los bordes dependen del periodo de entrenamiento, que incluye COVID. **Por frecuencia igual** es más estable ante extremos, pero sus niveles significan «relativo a 2016–2023», no un umbral de negocio. **Por ancho igual** es fácil de explicar pero lo domina el mínimo extremo: deja pocos meses en `bajo` y casi toda la serie en `alto`. La elección de k = 3 y de los métodos es un criterio de trabajo documentado aquí; si el cliente fija umbrales propios, se sustituyen los bordes (no es una regla del contrato).

**Qué no cambia el modelo.** Los modelos de series de tiempo del laboratorio (Holt-Winters, ARIMA/SARIMA) no necesitan reescalar la serie; la comparación del efecto de min-max frente a z-score sobre un método sensible a la escala la hizo la integrante B en [`pronostico.md`](pronostico.md) §2.7 (un k-NN como instrumento de comparación, no como modelo operativo, y un control del SARIMA que confirma que, con diferencias, la escala no cambia el pronóstico). Aquí solo se entregan las funciones y la garantía de que no hay fuga.

## 5. Pruebas de ausencia de fuga temporal
Todas están en `tests/test_pipeline_transformaciones.py` (series sintéticas, declaradas, y el oro real en la última):
- Ajustar con la serie completa (108 meses) lanza `ErrorFuga` en las cuatro funciones de ajuste, y basta **un mes** de 2024 para detectarlo.
- Un índice sin fechas se rechaza.
- **Los parámetros no dependen de los valores de 2024:** se desplaza la prueba en +500 puntos y los parámetros, la transformación del entrenamiento y los bordes salen idénticos.
- La prueba se transforma con los parámetros del entrenamiento: su min-max y su z-score coinciden con la fórmula calculada con 2016–2023, y su z-score **no** tiene media 0 (señal de que no se recalculó).
- Una prueba extrema (+1000) no mueve los bordes y cae en el nivel extremo.
- Con el oro real, los parámetros tienen n = 96 y `ajustado_hasta = 2023-12`.
- Se comprobó que el candado es el que detecta la fuga: al desactivarlo a propósito en una copia, fallaron 6 pruebas; luego se restauró el archivo original.

## 6. Reducción de datos: qué exige E1 y qué hay
**Requisito (PDF del Proyecto Integrador, pág. 15, Ingeniería de Datos; rúbrica, pág. 24: «Normalización, discretización y reducción», 15 puntos, «las tres aplicadas con análisis comparativo»):** «Reducción de datos: muestreo, agregación o selección de variables, con el porcentaje de reducción logrado y lo que se pierde». **E1 no exige una técnica de reducción de dimensionalidad como PCA**; los componentes principales y MANOVA aparecen como contenido de **E2** (págs. 5 y 12 del PDF). Por eso no se implementó PCA: con una sola variable objetivo y variables adicionales aún provisionales (contrato D7) no habría una justificación estadística, y adelantar E2 sería trabajo sin propósito.

**Lo que cubre el proyecto (agregación y selección de variables), con cifras verificadas sobre la plata real (2026-11-13):**
| Reducción | Antes | Después | Porcentaje | Lo que se pierde |
|---|---|---|---|---|
| Agregación categoría × mes a mes (Manzanillo), contrato §6 | 453 filas | 108 | **−76.2 %** | El detalle por categoría de estrellas. Esas 453 filas incluyen 21 de 1 estrella que se excluyen; las 432 filas de 2 a 5 estrellas pasan a 108 (−75.0 %) |
| Desde todo Base70 (plata) | 31,145 filas (31,147 leídas) | 108 | **−99.65 %** | Los demás destinos y categorías (alcance del proyecto: Manzanillo) |

La selección de variables del oro (el objetivo, sus componentes y tres variables adicionales **provisionales**, decisión D7) y la exclusión de columnas constantes de DENUE están descritas en [`contrato_datos.md`](contrato_datos.md) §4 y §6. **Desde el 2026-11-14 el pipeline informa estos porcentajes en cada corrida** (`pipeline.ejecutar`, clave `reduccion`): 31,145 filas de plata de Base70, 432 filas de Manzanillo de 2 a 5 estrellas y 108 del oro mensual, es decir **−75.0 %** por la agregación categoría × mes y **−99.65 %** desde toda la plata; lo que se pierde es el detalle por categoría de estrellas y los demás destinos. Una prueba ([`test_pipeline_jerarquias.py`](../../tests/test_pipeline_jerarquias.py)) fija esas cifras. (El −76.2 % de la tabla incluye las 21 filas de 1 estrella que el oro excluye.)

## 7. Qué quedaba pendiente y cómo se cerró (2026-11-14)
- **Jerarquías conceptuales:** **implementadas** en el pipeline y la capa oro (`dim_tiempo`, `dim_geografia` y `dim_ubicacion_denue`); véase [`pipeline.md`](pipeline.md) §3.1. Ya no es una cobertura parcial.
- **Comparación min-max frente a z-score «con análisis comparativo»:** la hizo la integrante B (PR #12) en [`pronostico.md`](pronostico.md) §2.7 con las funciones de este módulo y parámetros solo de 2016–2023 (n = 84 filas, porque 2016 aporta los rezagos). Su conclusión es prudente: sin un ganador estable entre min-max y z-score, y escalar **no** mejora un método por sí mismo. Se verificó con un recálculo independiente y una prueba de fuga con el oro real (Auditoría 6 de la integrante A, [`auditorias.md`](../../calidad/auditorias.md)).
- **Discretización supervisada** (el PDF, pág. 16, pide «por ancho, por frecuencia y supervisada»): **implementada** en §8, comparada con las otras dos. Las dos primeras no cambiaron.

## 8. Discretización supervisada y comparación con ancho y frecuencia
Código: [`pipeline/discretizacion_supervisada.py`](../../pipeline/discretizacion_supervisada.py) y [`laboratorio/exploracion/discretizacion.py`](../../laboratorio/exploracion/discretizacion.py). Resultados: [`laboratorio/exploracion/resultados/discretizacion_supervisada/`](../../laboratorio/exploracion/resultados/discretizacion_supervisada/) (`comparacion_metodos.csv` y `resumen.json`). Pruebas: [`tests/test_discretizacion_supervisada.py`](../../tests/test_discretizacion_supervisada.py) (17). Se regenera con `python -m laboratorio.exploracion.discretizacion`.

### 8.1 Qué se discretiza, con qué objetivo y por qué no es circular
| Elemento | Decisión |
|---|---|
| Variable discretizada | `ocupacion_pct`, en tres niveles (`bajo`, `medio`, `alto`), igual que los otros dos métodos |
| Variable objetivo (la «supervisión») | `temporada_alta` = 1 si el mes es **julio, agosto o diciembre**; 0 en los demás. Es una regla de **calendario** (vacaciones escolares de verano y de fin de año). La Semana Santa se excluye porque cae en marzo o abril según el año |
| Pregunta de negocio | ¿A partir de qué ocupación un mes «se parece» a uno de temporada alta? Un operador la usa para decidir tarifas, personal y expectativas |
| Por qué no es circular | El objetivo se define **solo con el calendario**: no usa ningún valor de ocupación, así que no se deriva de la variable que se discretiza. La regla se fijó **antes** de calcular ningún corte (no se ajustó viendo los datos) y una prueba comprueba que solo depende del índice mensual |
| Alternativas descartadas | Discretizar `densidad_ocupacion` o `llegadas_turistas` con la ocupación como clase: el contrato (D7) ya señala dependencia mecánica con el objetivo, y la clase saldría de la misma serie. Discretizar `pct_cuartos_no_residentes` o `estadia_promedio` con terciles de ocupación: correlación de 0.19 y 0.22 con la ocupación y relación no monótona, de modo que no hay una pregunta de negocio clara |
| Método | Entropía de Shannon con el criterio de longitud mínima de descripción de Fayyad e Irani (1993): el algoritmo parte el rango en el corte de mayor ganancia de información, repite en el segmento más informativo hasta tener 3 niveles y exige al menos 8 meses por nivel. Se reporta además si el criterio MDL **acepta** cada corte |

### 8.2 Cómo se evita la fuga de información
1. Los cortes se ajustan **solo con 2016-01 a 2023-12**. `ajustar_supervisada` reutiliza el candado de [`transformaciones.py`](../../pipeline/transformaciones.py): lanza `ErrorFuga` si recibe un solo mes posterior a 2023-12 o un índice que no es mensual.
2. **2024 solo evalúa** los cortes ya fijados. Una prueba reescribe 2024 con otros valores (coherentes con la puerta de calidad) y comprueba que los cortes, las ganancias, el criterio MDL y el valor p no cambian.
3. **Escenario principal «sin COVID»:** 80 de los 96 meses (se excluyen los 16 de `d_covid`, regla de calendario del contrato), porque en 2020 y 2021 los meses de temporada alta tuvieron una ocupación anómala que distorsionaría el corte. Como sensibilidad se reporta «todo el entrenamiento» (96 meses).

### 8.3 Resultados (cortes en puntos porcentuales de ocupación)
| Escenario | Método | Cortes | Meses por nivel (ajuste) | Ganancia en el ajuste (bits) | Exactitud en el ajuste | Ganancia en 2024 (bits) | Exactitud en 2024 |
|---|---|---|---|---|---|---|---|
| Sin COVID (80) | Ancho igual | 40.05 \| 53.20 | 15 / 41 / 24 | 0.086 | 0.738 | 0.175 | 0.750 |
| Sin COVID (80) | Frecuencia igual | 45.48 \| 52.31 | 27 / 26 / 27 | 0.094 | 0.738 | 0.123 | 0.750 |
| Sin COVID (80) | **Supervisada** | **48.64 \| 55.37** | 34 / 30 / 16 | **0.200** | **0.812** | 0.078 | **0.500** |
| Todo el entrenamiento (96) | Ancho igual | 23.09 \| 44.71 | 6 / 33 / 57 | 0.058 | 0.750 | 0.000 | 0.750 |
| Todo el entrenamiento (96) | Frecuencia igual | 41.75 \| 51.36 | 32 / 32 / 32 | 0.065 | 0.750 | 0.123 | 0.750 |
| Todo el entrenamiento (96) | **Supervisada** | **48.64 \| 55.37** | 50 / 30 / 16 | **0.156** | 0.812 | 0.078 | 0.500 |
Referencia: predecir siempre «no es temporada alta» da una exactitud de 0.738 en el ajuste (sin COVID) y de 0.750 en 2024 (9 de 12 meses). La exactitud de un nivel se calcula con la clase mayoritaria de cada nivel **en el ajuste**, aplicada a 2024 sin reajustar.

### 8.4 Lectura, ventajas y limitaciones
- **Ventaja:** en el ajuste, la supervisada separa la temporada alta con más del doble de información que las otras (0.200 bits frente a 0.086 y 0.094) y es el único método que supera a la referencia de exactitud (0.812 frente a 0.738). El **valor p de permutación es 1/501 ≈ 0.002**: se calculó con la corrección (b + 1) / (B + 1) con B = 500 permutaciones de la clase (semilla 20261113, reajustando los cortes cada vez) y **b = 0**: ninguna permutación igualó o superó la ganancia observada. Es el **límite de resolución** del procedimiento (el valor más pequeño que puede dar con 500 permutaciones), no un valor exacto: indica que la asociación no es un artefacto de que la supervisada optimice sus cortes, pero no permite decir «p = 0.002» como una probabilidad precisa. Se reporta como `p_valor_minimo_alcanzable = 0.001996` en `resumen.json`. El resultado es **robusto al COVID**: los dos cortes (48.64 y 55.37) son los mismos con y sin esos meses.
- **El criterio MDL acepta solo el segundo corte** (el que separa los meses de más de 55.37 % de ocupación); el primero (48.64) **no** pasa el criterio: con el tamaño de muestra, la separación entre «bajo» y «medio» es débil. Hay un solo corte plenamente justificado estadísticamente.
- **Limitación principal: no generaliza a 2024.** En el año de prueba la supervisada obtiene una exactitud de 0.50 (peor que la referencia de 0.75) y menos información (0.078 bits). Pero **12 meses, de los cuales 3 son de temporada alta, no permiten concluir nada**: una sola clasificación equivocada cambia la exactitud en 8 puntos. 2024 también tuvo una ocupación media más alta y menos variable que el entrenamiento (54.7 % frente a 44.8 %), y la regla de calendario no capta la Semana Santa. **No se afirma que la supervisada sea mejor; se afirma que es otra lectura, coherente con el calendario en el ajuste, que hay que volver a evaluar cuando haya más años.**
- **Limitaciones generales:** el objetivo (julio, agosto y diciembre) es una convención de calendario, no una medición de la demanda. **Los datos no respaldan el mes de agosto:** en el entrenamiento su ocupación media es de 44.3 %, de las más bajas, frente a 53.8 % de julio y 53.3 % de diciembre; se dejó en la regla porque se fijó antes de ver los cortes y cambiarla ahora sería ajustar el objetivo a los datos. Es probable que eso explique parte de la separación débil. Además, los cortes describen la ocupación **agregada** de hoteles de 2 a 5 estrellas de Manzanillo, y los métodos de ancho y de frecuencia no usan la clase al cortar, así que la comparación mide cuánta información sobre la temporada conserva cada partición, no qué método «acierta» el calendario.
- **No cambia nada de lo anterior:** los bordes de ancho y de frecuencia siguen siendo los de [`parametros_transformaciones.json`](../../laboratorio/exploracion/resultados/parametros_transformaciones.json) (una prueba lo comprueba), el pronóstico, las métricas y el tablero no usan la discretización supervisada, y el oro mensual no se modificó.
