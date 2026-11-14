# Valores faltantes y atípicos (Ingeniería de Datos, E1)

Corte 2026-11-14 · Responsable: integrante A. Código: [`laboratorio/exploracion/faltantes.py`](../../laboratorio/exploracion/faltantes.py) y [`atipicos.py`](../../laboratorio/exploracion/atipicos.py). Pruebas: [`tests/test_faltantes_atipicos.py`](../../tests/test_faltantes_atipicos.py) (12). Resultados: [`resultados/faltantes/`](../../laboratorio/exploracion/resultados/faltantes/) y [`resultados/atipicos/`](../../laboratorio/exploracion/resultados/atipicos/). Se regeneran con `python -m laboratorio.exploracion.faltantes` y `python -m laboratorio.exploracion.atipicos` (la primera lee la plata que genera `pipeline.ejecutar`).
Requisito (PDF, págs. 14 y 24): «diagnóstico del mecanismo (completamente al azar, al azar o no al azar) y tratamiento justificado: eliminación, imputación por media o mediana, interpolación temporal o KNN» y «atípicos: IQR, puntaje z robusto o Isolation Forest, y una decisión documentada para cada tipo: corregir, marcar o eliminar».

## 1. Valores faltantes
### 1.1 Lo que realmente falta (inventario sobre la plata de Base70, 31,145 filas)
| Hallazgo | Casos | Mecanismo | Tratamiento y por qué |
|---|---|---|---|
| **Manzanillo** (alcance del observatorio) | **0** celdas vacías y 0 periodos ausentes (108 de 108) | No aplica | Ninguno: no se imputa ni se elimina nada |
| Mexicali, `turistas_noche_residentes`, 5 estrellas, 2020-03 | 1 celda | **Indeterminado.** Con una sola celda vacía no se puede contrastar «completamente al azar» frente a «al azar»; coincide con el inicio de la pandemia, pero eso es una coincidencia, no una prueba | Se **marca** (`faltante_turistas_noche`) y no se imputa: la fila queda fuera de las derivadas que usan esa columna. Imputar inventaría un dato de un destino que no es el nuestro |
| El Fuerte, 2024-01 a 2024-12 | 12 periodos ausentes (96 de 108) | **No al azar (ausencia estructural):** faltan todas las columnas de meses consecutivos al final de la serie; el centro dejó de reportar | **No se imputa**: sería inventar un destino que no reportó. El centro queda fuera de las series que exigen 108 meses (regla informativa R-D08) |

### 1.2 Comparación de tratamientos (simulación sobre la serie de Manzanillo, solo 2016-2023)
Como Manzanillo no tiene faltantes, para **justificar qué tratamiento usaríamos si apareciera uno** se ocultan meses de la serie real y se mide qué tan bien los reconstruye cada método. 200 réplicas por mecanismo, semilla 20261113, 2024 **no se usa**. Mecanismos simulados: **completamente al azar** (10 meses), **por bloque** (tres bloques de 3 meses) y **no al azar** (se ocultan los 10 valores más altos: lo que falta depende del propio dato). RMSE y sesgo en puntos porcentuales de ocupación:
| Método | Completamente al azar: RMSE (sesgo) | Por bloque: RMSE (sesgo) | No al azar: RMSE (sesgo) |
|---|---|---|---|
| Media | 12.89 (+0.41) | 13.12 (+0.04) | 18.98 (−18.72) |
| Mediana | 13.39 (+3.86) | 13.42 (+3.50) | 15.49 (−15.18) |
| **Interpolación lineal** | **6.88 (+0.21)** | **9.50 (−0.27)** | **10.73 (−10.21)** |
| Interpolación estacional | 13.35 (+0.16) | 13.25 (+0.10) | 17.28 (−16.45) |
| KNN (k = 3, por vecinos anterior y posterior) | 8.44 (+1.38) | 10.67 (+1.76) | 10.79 (−10.48) |
**Lecturas:**
- La **interpolación lineal** es la mejor en los tres mecanismos. Media, mediana e interpolación estacional dan errores del orden de la desviación de la serie (13 pp), porque la serie tiene la caída de 2020 y el mes del año explica poco (la estacionalidad es débil: fuerza 0.42, [`pronostico.md`](pronostico.md) §2.2).
- **Cuando falta lo más alto (no al azar), ningún método lo corrige:** todos subestiman entre 10 y 19 pp. Por eso un mecanismo no al azar **no se arregla imputando**: hay que marcar el mes, no usarlo en las derivadas y declarar el sesgo.
- Los errores son grandes porque la serie incluye los 16 meses de COVID (la ocupación pasó de 41.8 % en febrero de 2020 a 1.5 % en abril); con meses normales serían menores. No se repitió sin COVID: es una limitación de la simulación.

### 1.3 Decisión
1. **Manzanillo no tiene faltantes: no se imputa ni se elimina nada.** Esta es la decisión vigente.
2. Si en una captura futura faltara un mes de la serie de Manzanillo: **marcarlo, interpolar linealmente solo para visualizar y NO usar el valor imputado para ajustar modelos**, y declararlo; nunca eliminar el mes sin análisis.
3. Faltantes de otros destinos (Mexicali, El Fuerte): marcar y excluir de las derivadas; no imputar.
**Límites:** el mecanismo de la celda de Mexicali **no se puede determinar**; la simulación usa una sola serie y tres mecanismos estilizados; KNN se implementó con una sola variable (los vecinos anterior y posterior), no con un conjunto de variables.

## 2. Atípicos y ruido
IQR 1.5 (la regla que el pipeline ya aplicaba en `diag_atipico_iqr`) frente al **puntaje z robusto** (mediana y MAD, umbral 3.5 de Iglewicz y Hoaglin) sobre los 108 meses:
| Método | Meses señalados | Cuáles |
|---|---|---|
| IQR 1.5 (límites 18.04 % y 75.94 %) | 3 | 2020-04, 2020-05, 2020-06 |
| Puntaje z robusto > 3.5 | 3 | 2020-04 (−4.67), 2020-05 (−4.55), 2020-06 (−4.00) |
Los dos métodos **coinciden** exactamente y los tres meses son de COVID (`d_covid`, regla de calendario). No se usó Isolation Forest (requiere una biblioteca que el proyecto no tiene y con una serie univariada no aportaría más que los dos métodos anteriores).
### Decisión por tipo
| Tipo | Decisión | Dónde se aplica |
|---|---|---|
| Error de captura (ocupados > disponibles) | **Cuarentena** con regla y motivo | R-D06 en el pipeline (en Manzanillo: 0 casos; 2 casos en Ciudad Juárez) |
| Evento real (COVID) | **Marcar y conservar:** no es un error, es el hallazgo; se modela con la variable de calendario `d_covid` | `diag_atipico_iqr` en el oro y `d_covid` en el pronóstico |
| Ruido (variación mes a mes sin causa) | **Conservar sin suavizar:** la serie es la medición y el pronóstico lo absorbe en su varianza | [`pronostico.md`](pronostico.md) §5 |
| Valor sin causa conocida | **Marcar y revisar** contra la fuente; no se elimina sin evidencia | — (hoy ninguno) |
**Límite:** el diagnóstico de atípicos es sobre la serie univariada de Manzanillo; no se revisaron los atípicos de los otros 63 centros.

### 2.1 Ruido, estacionalidad y eventos reales (ampliación posterior a la entrega, 2026-11-14)
Con la descomposición STL robusta versionada (108 meses; [`ruido.py`](../../laboratorio/exploracion/ruido.py), resultados en `laboratorio/exploracion/resultados/ruido/`): tendencia 23.9 %, estacionalidad 27.7 % y residuo 40.9 % de la varianza. **El residuo está dominado por COVID:** 5 de los 7 meses de residuo extremo (|z robusto| > 3.5) son 2020-03 a 2020-07 y, sin COVID, la desviación del residuo baja de 8.06 a 2.87 pp (estacionalidad 60.4 %, residuo 11.4 %). Los otros dos extremos (positivos) son 2017-04, que [`pronostico.md`](pronostico.md) §5 asocia a la Semana Santa (efecto de calendario que ningún modelo incluye), y 2019-08, **sin causa conocida**. Todos se marcan y se conservan.
**Límite:** el residuo mezcla ruido de medición y variación real; sin una segunda fuente no se puede separar ni afirmar que haya errores de captura.
