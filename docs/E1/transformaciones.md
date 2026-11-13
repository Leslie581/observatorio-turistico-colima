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

## 3. Resultado con los datos reales (descriptivo)
- **2024 queda dentro del rango de entrenamiento:** min-max entre 0.671 y 0.923 (ningún mes fuera de [0, 1]); z-score entre 0.02 y 1.30.
- **Frecuencia igual:** el entrenamiento se reparte 32/32/32 por construcción; 2024 cae en 0 `bajo`, 3 `medio` y 9 `alto`.
- **Ancho igual:** el entrenamiento queda 6 `bajo`, 33 `medio` y 57 `alto`; los 12 meses de 2024 caen en `alto`.
- El desbalance de 2024 en los niveles **no es un error**: refleja que 2024 (media 54.73 %) está por encima de la media de entrenamiento (44.75 %). Es una observación sobre los datos, no una explicación.

## 4. Cuándo conviene cada una y sus limitaciones
**Min-max.** Conviene cuando el método necesita una escala acotada o comparable entre variables (redes, métodos basados en distancias, comparación de gráficas en [0, 1]). *Limitaciones:* depende de dos valores extremos; aquí el mínimo es el mes más bajo del COVID (1.46 %), de modo que un mes típico (mediana de entrenamiento 48.11 %) queda en 0.72 y la zona habitual de la serie se comprime en la parte alta del intervalo. Un valor posterior fuera del rango de entrenamiento sale de [0, 1] y **no se recorta** (recortar escondería el cambio); la fórmula es sensible a un solo atípico.

**Z-score.** Conviene para modelos lineales, regresión penalizada, PCA y para expresar «cuántas desviaciones se aleja un mes de lo habitual en el entrenamiento». *Limitaciones:* μ y σ incluyen los meses de COVID (sin ellos, la media de entrenamiento es 48.59 % y la desviación 8.62 %, frente a 44.75 % y 12.83 %); el mes más bajo queda en −3.39. No normaliza la forma: la serie tiene asimetría negativa (−1.13 en entrenamiento), así que z-score no la vuelve «normal». Tampoco corrige tendencia ni estacionalidad.

**Discretización.** Conviene cuando se necesita una lectura ordinal para el cliente («ocupación baja, media o alta») o para métodos que trabajan con categorías. *Limitaciones:* pierde información (dos meses de 42 % y 51 % comparten nivel) y los bordes dependen del periodo de entrenamiento, que incluye COVID. **Por frecuencia igual** es más estable ante extremos, pero sus niveles significan «relativo a 2016–2023», no un umbral de negocio. **Por ancho igual** es fácil de explicar pero lo domina el mínimo extremo: deja pocos meses en `bajo` y casi toda la serie en `alto`. La elección de k = 3 y de los métodos es un criterio de trabajo documentado aquí; si el cliente fija umbrales propios, se sustituyen los bordes (no es una regla del contrato).

**Qué no cambia el modelo.** Los modelos de series de tiempo del laboratorio (Holt-Winters, ARIMA/SARIMA) no necesitan reescalar la serie; la comparación del efecto de min-max frente a z-score sobre un método sensible a la escala corresponde al laboratorio de la integrante B. Aquí solo se entregan las funciones y la garantía de que no hay fuga.

## 5. Pruebas de ausencia de fuga temporal
Todas están en `tests/test_pipeline_transformaciones.py` (series sintéticas, declaradas, y el oro real en la última):
- Ajustar con la serie completa (108 meses) lanza `ErrorFuga` en las cuatro funciones de ajuste, y basta **un mes** de 2024 para detectarlo.
- Un índice sin fechas se rechaza.
- **Los parámetros no dependen de los valores de 2024:** se desplaza la prueba en +500 puntos y los parámetros, la transformación del entrenamiento y los bordes salen idénticos.
- La prueba se transforma con los parámetros del entrenamiento: su min-max y su z-score coinciden con la fórmula calculada con 2016–2023, y su z-score **no** tiene media 0 (señal de que no se recalculó).
- Una prueba extrema (+1000) no mueve los bordes y cae en el nivel extremo.
- Con el oro real, los parámetros tienen n = 96 y `ajustado_hasta = 2023-12`.
- Se comprobó que el candado es el que detecta la fuga: al desactivarlo a propósito en una copia, fallaron 6 pruebas; luego se restauró el archivo original.

## 6. Pendiente
- **Reducción de dimensionalidad** (el tercer elemento de ese criterio de la rúbrica): no está implementada; las variables adicionales del oro son provisionales (contrato D7).
- La comparación min-max frente a z-score «con análisis comparativo» sobre un modelo la hace el laboratorio.
