# Ruta del experimento de E2 (preparación; no se califica en E1)

Corte 2026-11-14 · Redacta: integrante A. **Conformidad de la integrante B: pendiente** (la decisión «de las dos» que pide [`plan_trabajo.md`](plan_trabajo.md) §1 exige que B la confirme). PDF, pág. 16: «elijan la ruta de su experimento. Si es la ruta negocio, confirmen esta semana el acuerdo con su cliente» y pág. 17: «un experimento factorial real. Elijan una de dos rutas (la eligieron en E1)».

## 1. Decisión: ruta ingeniería sobre el extractor propio
| Elemento | Decisión | Evidencia |
|---|---|---|
| Ruta | **Ingeniería**: diseño 2³ sobre nuestro propio extractor | [`propuesta.md`](../E0/propuesta.md) §4 (E2) ya la fijó en E0 |
| Por qué no la ruta negocio | Requiere un cliente real con una campaña o un proceso, y **ese cliente no existe hoy**; la entrevista de E0 tiene registro parcial y la encuesta fue exploratoria. No hay acuerdo que confirmar | [`propuesta.md`](../E0/propuesta.md) §4 y [`verificacion.md`](../E0/verificacion.md) |
| Pregunta | ¿Qué configuración del extractor da menor tiempo de procesamiento y menor tasa de error? | [`propuesta.md`](../E0/propuesta.md) §4 |
| Lenguaje | Es el **único** experimento controlado (asignamos los niveles y aleatorizamos): admite lenguaje causal **sobre el extractor**, no sobre el turismo | [`propuesta.md`](../E0/propuesta.md) §4 |

## 2. Diseño ya fijado (lo que E2 solo tiene que correr)
| Elemento | Valor |
|---|---|
| Factores (2 niveles) | `procesos` (1 / 4), `analizador` (json / orjson) y `formato` de salida (csv / parquet). **Los niveles definitivos se confirman en E2**; `orjson` y `parquet` no están en las dependencias de hoy |
| Respuestas | Segundos de procesamiento y tasa de error |
| Réplicas y bloqueo | 2 réplicas completas = 2 bloques (día 1 y día 2, la fuente de variación que no controlamos); cada tratamiento aparece una vez por bloque |
| Aleatorización | Orden de las 8 corridas aleatorizado dentro de cada bloque, semilla fija 20261113 |
| Matriz | [`laboratorio/experimento/resultados/matriz_2x3.csv`](../../laboratorio/experimento/resultados/matriz_2x3.csv): 16 corridas, generada por [`laboratorio/experimento/matriz.py`](../../laboratorio/experimento/matriz.py) |
| Comprobaciones | [`tests/test_experimento_e2.py`](../../tests/test_experimento_e2.py) (5): 8 tratamientos por bloque, diseño balanceado y ortogonal (columnas de efectos principales e interacciones sin correlación), orden reproducible y distinto por bloque, niveles coherentes con los códigos, archivo al día |
| Análisis previsto | ANOVA factorial al 5 %, supuestos con los residuos y corrida de confirmación (propuesta §4). Pág. 17 pide además un diseño de dos factores con tres niveles o más en uno, y la comparación 2⁴ completo frente a 2⁴⁻¹, que se resuelven en E2 |

## 3. Seguridad de la ejecución
Se correrá **contra una copia local de las respuestas ya capturadas** (`data/bronce/denue/`, capturas reales con sus fichas y hashes) o contra una API propia, **nunca saturando un sitio ajeno** (pág. 17). El respaldo del bronce con manifiesto ([`seguridad.md`](seguridad.md) §6) permite repetir el experimento sobre los mismos bytes.

## 4. Lo que NO está hecho
- **No se corrió ninguna corrida ni se midió ningún tiempo**: la matriz es solo la estructura.
- **Los niveles `orjson` y `parquet` no se han implementado ni se han agregado a las dependencias**; si no son viables se cambian en E2.
- **La conformidad de la integrante B** y la confirmación con los docentes de que esta ruta cumple lo que piden en E2.
- El experimento de E2 se ejecuta en una sola semana (23 al 27 de noviembre): conviene implementar los factores antes.

## 5. Observación de la revisión cruzada: la tasa de error como variable de respuesta
La integrante B señaló, en su revisión de `4242ea5`, un punto sobre la **tasa de error** como respuesta del experimento de E2. **El texto literal es de su Auditoría 8** (la registra ella; aquí no se transcribe ni se duplica). Lo que sigue es lo que la integrante A deja anotado **sin desarrollar el experimento**, como lectura de A que B puede corregir con su redacción:
- **Hay que definir «error» antes de correr** (qué se cuenta: respuesta que no se puede interpretar, registro que la puerta de calidad rechaza, archivo de salida inválido) y **el denominador** (errores por registro procesado o por corrida). Sin esa definición la respuesta no es medible.
- **Contra una copia local estable** de las respuestas ya capturadas es probable que la tasa de error sea **cero o casi cero en casi todas las corridas**. Una respuesta sin variación no sirve para un ANOVA; habría que **provocar errores de forma controlada** (por ejemplo, con respuestas alteradas a propósito y declaradas sintéticas) o dejar el tiempo de procesamiento como respuesta principal y la tasa de error como secundaria.
- **Una proporción no es normal** y con pocas corridas (16) los supuestos del ANOVA se ven comprometidos; al analizarla hay que revisar los residuos y considerar una transformación o un modelo para proporciones.
- **Decisión pendiente para E2** (no se toma aquí): qué es un error, si se provocan errores y cuál es la respuesta principal. La matriz 2³ ([`matriz_2x3.csv`](../../laboratorio/experimento/resultados/matriz_2x3.csv)) no cambia por esto.
