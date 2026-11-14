# Mejoras posteriores a la entrega de E1

**Fecha:** 2026-11-13 / 14 (hora local), **después** de la entrega: etiqueta `e1` sobre `134c333`, formulario ya registrado. Rama `e1/mejoras-postentrega`, sin fusionar. **No reemplaza ninguna métrica ni documento entregado:** las cifras originales de E1 (SARIMA elegido por RMSE en 2024, intervalos gaussianos, 12 desviaciones, tiempos del PSP) siguen siendo las de la entrega; lo de aquí es adicional y está fechado como posterior. Implementó A; **B debe revisar la rama antes de cualquier fusión**.

## 1. Qué se agregó
| Mejora | Dónde | Resultado verificable |
|---|---|---|
| Intervalos de predicción sin normalidad (bootstrap de bloques de residuos, bloque 6, B = 1,000, semilla 20261114) y validación de origen móvil (17 orígenes 2018-12 a 2022-12, h = 12; nunca se usa 2024) | [`intervalos.py`](../../laboratorio/pronosticos/intervalos.py) → [`resultados/intervalos/`](../../laboratorio/pronosticos/resultados/intervalos/) | §2 |
| Esquema pandera de la plata de DENUE (R-E07): tipos, rangos, unicidad `(fecha, clee)`, catálogo SCIAN, municipio, caja geográfica, `personal_min ≤ personal_max`; reutiliza las constantes de R-E01 a R-E06 y detiene la corrida con `ErrorPuertaCalidad` | [`reglas_denue.py`](../../pipeline/calidad/reglas_denue.py), [`plata_denue.py`](../../pipeline/plata_denue.py) | La plata real lo cumple; 9 pruebas ([`test_esquema_plata_denue.py`](../../tests/test_esquema_plata_denue.py)) detectan cada violación sintética |
| Análisis cuantitativo del ruido | [`ruido.py`](../../laboratorio/exploracion/ruido.py) → [`resultados/ruido/`](../../laboratorio/exploracion/resultados/ruido/) | §3 |
| Notebook reproducible que reutiliza los módulos | [`notebooks/pronostico_e1.ipynb`](../../notebooks/pronostico_e1.ipynb) | Una prueba ejecuta todas sus celdas |
| Protección de `main` preparada, **no activada** | [`.github/rulesets/proteger-main.json`](../../.github/rulesets/proteger-main.json) | §5 |

## 2. Intervalos del 95 %: gaussiano frente a bootstrap
| Evaluación | Gaussiano (E1) | Bootstrap de bloques |
|---|---|---|
| 2024 (12 meses): cobertura / ancho medio | 1.00 / 40.4 pp | 1.00 / 47.1 pp |
| Origen móvil, 204 meses, todos: cobertura / ancho | 0.770 / ≈46 pp | 0.750 / ≈53 pp |
| Origen móvil sin COVID, 140 meses: cobertura | 0.950 | 0.914 |

**Lectura honesta:** el bootstrap **no mejora** la cobertura; es más ancho y queda algo por debajo del 95 % nominal sin COVID. Su valor es **no suponer normalidad** (Jarque-Bera rechaza, p < 0.001): cambia un supuesto fallido por otro más débil (residuos intercambiables por bloques). La autocorrelación de los residuos en el rezago 1 es 0.056 (n = 83). Ninguno incorpora incertidumbre de parámetros. El gaussiano de E1 no se retira; se muestran ambos.

**Selección de modelo (origen móvil, sin COVID):** Holt-Winters tiene mejor RMSE (9.05 frente a 9.67) y MAPE (15.9 frente a 16.4) que el SARIMA elegido; SARIMA gana en MAE (7.35 frente a 7.50). **La selección de E1 con un solo año de prueba no es estable.** No se cambia el elegido oficial (se conservan los cuatro modelos); se declara la limitación.

**Datos recientes (2025-2026):** búsqueda acotada del 2026-11-13: la ficha de datos.gob.mx de Base70 indica última actualización el 28-may-2025, igual que `docs/fuentes/datatur.md`; el Sistema de Monitoreo restringe el acceso automático por sus términos. **No hay datos oficiales 2025-2026 en la fuente permitida.** Se proyecta 2025-01 a 2027-12 con ambos intervalos ([`proyeccion_2025_2027.csv`](../../laboratorio/pronosticos/resultados/intervalos/proyeccion_2025_2027.csv)): es una **proyección histórica con datos hasta 2024-12, no un pronóstico actualizado**; la incertidumbre crece con el horizonte (2027-12: gaussiano 34.1–95.7 %, bootstrap 31.0–92.6 %) y no hay forma de saber si 2025 ya la contradijo. El tablero **no** se actualizó con estos resultados.

## 3. Ruido, estacionalidad y eventos reales
Con la descomposición STL ya versionada (108 meses): tendencia 23.9 %, estacionalidad 27.7 % y residuo 40.9 % de la varianza, pero **el residuo está dominado por COVID**: 5 de los 7 meses de residuo extremo (|z robusto| > 3.5) son 2020-03 a 2020-07 y, sin COVID, la desviación del residuo baja de 8.06 a 2.87 pp (estacionalidad 60.4 %, residuo 11.4 %). Los 2 extremos restantes (2017-04 y 2019-08, positivos) **no tienen causa conocida**: se marcan y conservan; el calendario (Semana Santa) es una hipótesis por verificar, no un hallazgo. **Límite:** el residuo mezcla ruido de medición y variación real; sin una segunda fuente no se puede separar ni afirmar que haya errores de captura.

## 4. Datos: faltantes, discretización, integración y trazabilidad
- **Faltantes.** Manzanillo no tiene (0 celdas, 108 de 108). La justificación vigente ([`faltantes_y_atipicos.md`](faltantes_y_atipicos.md) §1) no fuerza MCAR/MAR: la celda de Mexicali queda como **indeterminada** y la ausencia de El Fuerte (12 meses finales) es **estructural, no al azar**; ambas se marcan sin imputar, y la simulación sobre Manzanillo compara tratamientos solo para decidir qué hacer si apareciera uno. No se cambió.
- **Discretización.** Está aplicada en `pipeline/transformaciones.py` (ancho y frecuencia, con cortes ajustados solo con 2016-2023) y `pipeline/discretizacion_supervisada.py` (entropía), con resultados en `laboratorio/exploracion/resultados/`. **No se llevan al oro:** el oro 1.0.0 tiene 20 columnas contratadas con Estadística y el tablero; los cortes dependen de un entrenamiento (riesgo de fuga si se publican como dato) y la discretización supervisada usa un objetivo de calendario cuyo p de permutación (1/501 ≈ 0.002) es solo el límite de resolución y no generaliza a 2024. Aportan valor como descripción, no como columna del oro. No se modificó el esquema de Oro.
- **Integración y modelo común.** No se inventó ninguna relación temporal entre fuentes: DataTur (ocupación mensual 2016-2024) y DENUE (oferta, capturas desde 2026) **no tienen periodos coincidentes**; se relacionan solo por entidad geográfica (`dim_geografia`, `municipio_clave` 06007) y calendario (`dim_tiempo`). No se agregó ningún cruce nuevo.
- **Trazabilidad.** Cada fila de la plata de DENUE conserva `archivo_bronce` y `sha256_bronce`; la cuarentena registra regla y motivo (`data/cuarentena/`); R-E07 usa el mismo formato de error. El diccionario (45 entradas) no cambió porque no cambió ninguna columna.

## 5. Protección de `main` (preparada, NO activada)
**Análisis de compatibilidad.** `captura-diaria.yml` tiene `contents: write` y hace `git push origin HEAD:main` con `GITHUB_TOKEN` (commit `captura DENUE … [skip ci]`). Con «Require a pull request» o «Require status checks» activos, ese empuje **se rechazaría** y la captura diaria dejaría de guardar su bronce. Por eso [`proteger-main.json`](../../.github/rulesets/proteger-main.json) incluye una excepción para la aplicación GitHub Actions (`actor_id` 15368, tipo `Integration`) y se entrega con `enforcement: "disabled"`: **importarlo no bloquea nada**. Lo que sí se verificó ([`test_ruleset_main.py`](../../tests/test_ruleset_main.py)): los cuatro trabajos exigidos (`calidad`, `auditoria-dependencias`, `bloqueo-tablero`, `secretos`) existen en `ci.yml`, y el empuje de la captura es el descrito. **No se verificó** que GitHub acepte esa excepción para ese actor en un repositorio personal; por eso el paso 4 prueba la captura antes de dar por buena la regla.

**Pasos manuales (usted, con permisos de administración):**
1. GitHub → repositorio → *Settings* → *Rules* → *Rulesets* → *New ruleset* → *Import a ruleset* → elegir `.github/rulesets/proteger-main.json`. Queda **desactivado**.
2. Revisar que el objetivo sea la rama predeterminada y que la lista de *bypass* muestre «GitHub Actions». Si no aparece, agréguela a mano.
3. Cambiar *Enforcement status* a **Active** y guardar.
4. *Actions* → *captura-diaria* → *Run workflow*; confirmar que el paso «Guardar bitácora…» termina en verde y aparece un commit `captura DENUE …` en `main`. **Si falla con «protected branch»:** volver a **Disabled** y no activar hasta resolverlo (alternativa: que la captura empuje a una rama `captura` y se fusione por PR).
5. Probar con un PR de prueba: sin aprobación de la otra integrante y sin CI en verde, *Merge* debe quedar bloqueado.

**Límite:** sin organización, la propietaria del repositorio puede añadirse al *bypass*; la regla es una barrera contra descuidos (como los PR #7 a #18), no contra mala fe.

## 6. Respaldo independiente del bronce
Hoy existe una copia **local** (`respaldo_bronce_20261114`, mismo disco, zip SHA-256 `725b499c…27b2`); **no es una copia externa y no debe presentarse como tal.** Para que lo sea:
1. `python -m pipeline.respaldo crear --destino <carpeta>` (genera `.zip` y `.manifiesto.json`).
2. Copiar ambos archivos a un medio **fuera de este equipo y de GitHub** (unidad externa o nube personal) y anotar fecha y lugar.
3. Desde otro equipo o carpeta: `python -m pipeline.respaldo verificar --zip … --manifiesto …` y `restaurar … --destino <carpeta vacía>`; deben terminar sin diferencias.
4. Registrar aquí la fecha y el lugar. **Hasta entonces el proyecto sigue sin copia externa confirmada.**

## 7. Acciones correctivas posteriores (2026-11-13/14)
Pruebas nuevas (esquema DENUE, intervalos, ruido, notebook, ruleset), README reescrito con pasos de reproducción, relatoría con enlaces y tiempo por bloque. **No se corrigen ni reescriben** las doce desviaciones ni las limitaciones históricas de fiabilidad: siguen vigentes.
