# Pipeline bronce → plata → oro (E1, contrato 1.0.0)

Rama `e1/leslie-pipeline` · 2026-11-13 · Responsable: Leslie Valadez Macías (integrante A). Diseño y definiciones: [`contrato_datos.md`](contrato_datos.md). Lo medido en este documento sale de **una corrida real sobre el bronce del repositorio** del 2026-11-13; los casos de falla se probaron con datos **sintéticos** (se dice en cada prueba).

## 1. Cómo se ejecuta
```powershell
.\.venv\Scripts\python.exe -m pipeline.ejecutar          # bronce -> plata -> oro, con puerta de calidad y cuarentena
.\.venv\Scripts\python.exe -m pipeline.verificar_oro      # el oro regenerado coincide con el versionado (tras ejecutar; exige git)
.\.venv\Scripts\python.exe -m laboratorio.exploracion.explorar   # gráficas y estadísticas del oro (requiere requirements-lab.txt)
.\.venv\Scripts\python.exe -m pytest -q -rs               # pruebas
.\.venv\Scripts\python.exe -m pipeline.verificar_e0 --solo historico --solo integridad --solo privacidad --exigir-datos
```
Códigos de salida: **0** correcto · **2** la puerta de calidad impide una salida confiable (no se escribe plata ni oro; queda `data/cuarentena/resumen_fallida-<fecha>.json` con la regla y el motivo) · **1** error inesperado. El pipeline **nunca escribe en `data/bronce/`** (probado). Las salidas son deterministas: la misma entrada da los mismos archivos byte a byte; solo cambian las marcas de tiempo de los `.meta.json` y del resumen.

## 2. Módulos
| Archivo | Función |
|---|---|
| `pipeline/config.py` | Constantes del contrato (categorías, periodos, partición, atribuciones) |
| `pipeline/plata_datatur.py` | Base70 → `data/plata/datatur_base70.csv`; verifica el SHA-256 contra la ficha del bronce |
| `pipeline/plata_denue.py` | Capturas DENUE → `data/plata/denue_establecimientos.csv`, una captura por día local |
| `pipeline/calidad/reglas_datatur.py`, `reglas_denue.py` | Reglas R-D01…R-D08 y R-E01…R-E06 |
| `pipeline/calidad/cuarentena.py` | Rechazados con regla, motivo, fila de origen y hash; resumen con cuenta cuadrada |
| `pipeline/oro.py` | Oro mensual (20 columnas), agregado DENUE, diccionario y esquema `pandera` |
| `pipeline/jerarquias.py` | Jerarquías conceptuales: `dim_tiempo`, `dim_geografia` y `dim_ubicacion_denue`, su esquema `pandera`, sus claves foráneas y su parte del diccionario (§3.1) |
| `pipeline/interfaz.py` | `cargar_oro_mensual`, `serie_objetivo`, `partir_entrenamiento_prueba` para el laboratorio |
| `pipeline/ejecutar.py` | Orquestador; escribe solo cuando todo se calculó y validó |
| `pipeline/transformaciones.py` | Min-max, z-score y discretización con parámetros ajustados solo con 2016–2023 ([`transformaciones.md`](transformaciones.md)) |
| `pipeline/discretizacion_supervisada.py` | Discretización supervisada por entropía (Fayyad e Irani) sin fuga ([`transformaciones.md`](transformaciones.md) §8) |
| `pipeline/respaldo.py` | Copia adicional del bronce con manifiesto SHA-256, verificación y restauración en un directorio temporal ([`seguridad.md`](seguridad.md) §6) |
| `pipeline/bloqueo.py` | Archivo de bloqueo con hashes del tablero (`tablero/requirements.lock.txt`; [`seguridad.md`](seguridad.md) §5) |
| `pipeline/verificar_oro.py` | Compara el oro regenerado con el versionado en git (puerta de CI) |
| `laboratorio/exploracion/explorar.py` | Cuatro gráficas y estadísticas descriptivas del oro ([`exploracion.md`](exploracion.md)) |
| `laboratorio/exploracion/discretizacion.py` | Comparación de la discretización por ancho, frecuencia y supervisada ([`transformaciones.md`](transformaciones.md) §8) |
| `laboratorio/experimento/matriz.py` | Matriz del diseño 2³ de E2 (preparación; [`ruta_experimento_e2.md`](ruta_experimento_e2.md)) |

## 3. Reglas de calidad implementadas
`pandera` valida el esquema bruto de Base70 (R-D01) y el esquema del oro; las reglas por fila son máscaras de pandas con identificador propio. Ningún registro se descarta en silencio: `leidos = aceptados + rechazados` (si no cuadra, la ejecución falla con la regla `CUENTA`).
| Regla | Efecto | Resultado en la corrida real |
|---|---|---|
| R-D01 esquema exacto | Detiene el lote | Superada |
| R-D02 fecha válida | Fila a cuarentena | 0 |
| R-D03 clave `(anio, mes, centro, categoria)` única | Repetidas a cuarentena (se conserva la primera) | 0 |
| R-D04 conteos enteros ≥ 0 (los de turistas-noche pueden venir vacíos) | Fila a cuarentena | 0 |
| R-D05 disponibles > 0 | Fila a cuarentena | 0 |
| R-D06 ocupados ≤ disponibles | Fila a cuarentena | **2** (Ciudad Juárez, 2 estrellas: 2021-07 y 2022-06) |
| R-D07 faltantes de turistas-noche | **Se marcan, no se imputan** | **1** (Mexicali, 5 estrellas, 2020-03) |
| R-D08 cobertura por centro | Informativa | El Fuerte: 96 periodos |
| R-E01 `CLEE` e `Id` no vacíos y `CLEE` único; esquema mínimo | Fila (o lote) a cuarentena | 0 |
| R-E02 completitud frente a `Cuantificar` (0.98 a 1.02) | Rechaza el lote | 0 lotes |
| R-E03 municipio 06007, subsector 721, clase del catálogo | Fila a cuarentena | 0 |
| R-E04 coordenadas numéricas dentro de Colima | Fila a cuarentena | 0 |
| R-E05 campos excluidos por privacidad | **Incidente: detiene todo** | Ninguno presente |
| R-E06 `Fecha_Alta` con formato válido y no posterior a la captura | Fila a cuarentena | 0 |
Reglas con **0 rechazos reales** solo se probaron con datos sintéticos: aún no se ha visto un lote DENUE real que falle.

### 3.1 Jerarquías conceptuales (capa oro)
El PDF (pág. 15) pide «discretización y jerarquías conceptuales» con ejemplos como colonia → municipio → estado. `pipeline.ejecutar` las construye en cada corrida, **sin tocar el oro mensual** (20 columnas, contrato 1.0.0), como tres dimensiones que se enlazan por clave:
| Dimensión (archivo en `data/oro/`) | Jerarquía | Filas | De dónde sale cada nivel |
|---|---|---|---|
| `dim_tiempo.csv` | año → trimestre → mes (`periodo` es la clave del oro mensual) | 108 (36 trimestres, 9 años) | Solo de `periodo` (AAAA-MM): sin supuestos |
| `dim_geografia.csv` | estado → municipio → centro turístico (+ `tipo_centro` y `subtipo_centro`) | 1 (Manzanillo) | `centro`, `tipo_centro` y `subtipo_centro` de Base70; `municipio_clave` 06007 de DENUE (regla R-E03); el estado es el prefijo `06`; **los nombres Colima y Manzanillo son la tabla fija de un renglón del contrato §5** |
| `dim_ubicacion_denue.csv` | estado → municipio → localidad → colonia | 49 pares localidad-colonia (3 localidades) en la corrida del 2026-11-14 | `municipio_clave`, `localidad` y `colonia` de DENUE; sin conteos, coordenadas ni CLEE |
**Qué NO se afirma.** Base70 no trae el estado ni el municipio de los otros 63 centros turísticos: esos niveles solo existen para Manzanillo, el alcance del observatorio; no se inventan para los demás. Dos valores de `colonia` son numéricos (`10` y `22`, localidad MANZANILLO): así vienen en DENUE y se conservan.
**Controles** (`pipeline/jerarquias.py`, esquema `pandera` y `verificar_integridad`): claves y rangos válidos; los periodos del oro mensual y de `dim_tiempo` coinciden; cada mes tiene un solo trimestre y cada trimestre pertenece a un solo año; el trimestre es consistente con el mes; el centro es el objetivo y su municipio pertenece a su entidad; los establecimientos de DENUE son del municipio 06007; sin duplicados. Si alguno falla, la puerta de calidad detiene la corrida (código 2) y no se escribe nada. Las 18 columnas están en [`diccionario_datos.csv`](../../data/oro/diccionario_datos.csv) (ahora 45 entradas).
**Evidencia:** [`tests/test_pipeline_jerarquias.py`](../../tests/test_pipeline_jerarquias.py) (13 pruebas: corrida sobre el bronce real en una carpeta temporal, claves foráneas, cada trimestre con 3 meses, determinismo byte a byte, diccionario completo, el oro mensual intacto y las fallas). `verificar_oro` compara `dim_tiempo.csv` y `dim_geografia.csv` byte a byte cuando ya están versionados; `dim_ubicacion_denue.csv` no, porque crece con las capturas.

## 4. Resultado de la corrida real
| Etapa | Cifras |
|---|---|
| Base70 | 31,147 leídas · **31,145 aceptadas** · **2 rechazadas** · 1 marcada |
| DENUE | 5 capturas, 670 registros leídos · 670 aceptados · 0 rechazados · 134 reemplazados por una captura posterior del mismo día (fotos idénticas) |
| Plata | `datatur_base70.csv` 31,145 filas · `denue_establecimientos.csv` 536 filas (4 días × 134) |
| Oro | `manzanillo_ocupacion_mensual.csv` **108 filas** (2016-01 a 2024-12, 20 columnas) · `manzanillo_oferta_hospedaje.csv` 88 filas · `diccionario_datos.csv` |
| Serie objetivo | Mín. 1.46 (2020-04) · máx. 66.34 · media 45.86 · atípicos IQR marcados: 2020-04, 2020-05 y 2020-06 |
| Cotejo | El oro coincide con una derivación independiente desde bronce (diferencia máxima 4.9e-7, por el redondeo a 6 decimales) |
Se versionan solo el oro y el resumen de cuarentena (contrato §4.3); la plata y la cuarentena detallada (`rechazados.csv`) se regeneran y están en `.gitignore`.

## 5. Integración DATATUR + DENUE: decisiones y límites
- **Solo contexto agregado por municipio.** `manzanillo_oferta_hospedaje.csv` cuenta establecimientos por día de captura, clase SCIAN y estrato, **sin `CLEE` ni coordenadas**, y no se vincula con la ocupación de ningún establecimiento ni se usa como regresor.
- **Por qué no hay una unión estadística directa.** DATATUR mide ocupación de un centro turístico por categoría de estrellas, en cuartos-noche mensuales; DENUE lista establecimientos con **personal ocupado** (no cuartos) y solo tiene **una foto** (las capturas de 4 días son idénticas) y solo altas. No existe una serie mensual de oferta DENUE.
- **Conflictos resueltos:** el destino `Manzanillo` (texto) se vincula con la clave `06007` por una equivalencia fija; las fechas (`AAAA`+`MM`, `AAAA-MM`, ISO UTC) se llevan a `AAAA-MM` / `AAAA-MM-DD`; los duplicados entre capturas se resuelven por `(fecha_captura_local, clee)`; las unidades no se convierten entre sí.
- **Alternativa defendible:** mostrar la oferta DENUE como contexto en el tablero y usar las coordenadas (solo en plata local) para el análisis geoespacial de E2.
- **Modelo de datos integrado (2026-11-14).** Las dos fuentes quedan unidas por **dimensiones comunes**, no por una tabla pegada: el oro mensual de DATATUR se enlaza con `dim_tiempo` por `periodo` y con `dim_geografia` por el centro turístico Manzanillo; el agregado de oferta de DENUE se enlaza con `dim_geografia` por `municipio_clave` (06007) y su ubicación fina (localidad y colonia) vive en `dim_ubicacion_denue`. El pipeline **comprueba esas claves foráneas** en cada corrida (`verificar_integridad`) y una prueba las revisa con el bronce real. Conflictos resueltos: nombre de destino frente a clave INEGI (la equivalencia fija de arriba), tres formatos de fecha, unidades (cuartos-noche frente a establecimientos y personal: **sin convertir**) y duplicados por `(fecha_captura_local, clee)`. **Límite que se mantiene:** las dos fuentes **no se solapan en el tiempo** (DATATUR llega a 2024-12 y DENUE empieza en 2026-11), así que no existe una unión **mes a mes** entre ocupación y oferta, y por eso no se construye una; hacerlo sería inventar una relación.

## 6. Dependencias y CI
| Archivo | Contenido | Quién lo instala |
|---|---|---|
| `requirements.txt` | Núcleo: captura, pipeline y `pandera` (28 paquetes fijados) | El workflow diario de captura |
| `requirements-lab.txt` | `statsmodels`, `scipy`, `matplotlib` (14 paquetes fijados) | Solo `ci.yml` y quien trabaje en el laboratorio |
| `requirements-dev.txt` | `ruff` y `pip-audit` | `ci.yml` |
| `tablero/requirements.txt` | `streamlit`, `altair`, `pandas`, `numpy` (4 dependencias directas fijadas; las transitivas las resuelve `pip`) | `ci.yml` y Streamlit Community Cloud |
- **Por qué están separados:** el workflow de captura corre las pruebas con `requirements.txt`; si las librerías del laboratorio estuvieran ahí, una falla de instalación de `scipy` o `statsmodels` detendría la captura diaria. El núcleo incluye `pandera` porque las pruebas del pipeline lo importan.
- **Compatibilidad comprobada en esta máquina** (Python 3.13.15, Windows 11, `pandas 3.0.5`): `pandera 0.36.0` valida con `pandas 3.0.5`; `statsmodels 0.15.0`, `scipy 1.18.1` y `matplotlib 3.11.2` se importan; `pip check` sin conflictos; `pip-audit` sin vulnerabilidades conocidas en `requirements.txt` y `requirements-lab.txt` (corrida local del 2026-11-13). **No** se probó la instalación desde cero en Linux ni en GitHub.
- `wrapt` (dependencia de `formulaic`): pip había resuelto `2.6.0.dev1`, una versión previa. Se sustituyó por la estable `2.5.2`, que cumple el requisito de `formulaic` (`wrapt>=1.17.0rc1` en Python 3.13); con ella `pip check` sale limpio e importan `formulaic`, `statsmodels`, `scipy` y `matplotlib` (2026-11-13). Nota: en esta máquina el Control de aplicaciones de Windows bloquea de forma intermitente alguna DLL de `statsmodels` (p. ej. `_kalman_smoother`); es un límite del entorno local, no de las versiones, y obliga a validar el laboratorio en CI/Linux.
- **`ci.yml`:** en cada push y pull request corre, en el trabajo `calidad`, el linter (`ruff`), las pruebas con `-rs` (con las dependencias del laboratorio **y del tablero** instaladas), el pipeline, la comprobación «oro regenerado = oro versionado» y el verificador de E0; en trabajos aparte, `auditoria-dependencias` (`pip-audit` de las cuatro listas, con las dependencias transitivas del tablero) y `secretos` (`gitleaks` sobre el historial completo, [`seguridad.md`](seguridad.md) §3.4). Las dependencias se instalan juntas, con una sola resolución de `pip`, y la caché de `pip` cubre `tablero/requirements.txt`. **El CI nuevo (tablero obligatorio, `secretos`, auditoría ampliada) está en esta rama y no se ha ejecutado todavía en GitHub.** **Ejecuciones reales en GitHub (2026-11-13, consultadas en la API pública de Actions):** los dos trabajos (`calidad` y `auditoria-dependencias`) terminaron en éxito para el commit `70a26b9` (push y pull request), para `main` en `7e64ffa` (fusión del PR #8) y para la rama y la fusión del laboratorio de Eimy (PR #9, `main` en `49934ca`). Ejemplo: [ejecución 43381255086](https://github.com/Leslie581/observatorio-turistico-colima/actions/runs/43381255086). Eso confirma que la instalación fijada y los pasos funcionan en Linux con Python 3.13. **No se leyeron los registros de esas ejecuciones** (requieren sesión); solo su resultado por trabajo y paso.
- **La comprobación del oro (`pipeline/verificar_oro.py`) corre en CI y pasó en GitHub:** el paso «El oro regenerado coincide con el oro versionado» terminó en **éxito** en las ejecuciones [43388517052](https://github.com/Leslie581/tdl-turistico-colima/actions/runs/43388517052) (push de `68d8aaa`), [43389344704](https://github.com/Leslie581/tdl-turistico-colima/actions/runs/43389344704) (pull request), [43389413267](https://github.com/Leslie581/tdl-turistico-colima/actions/runs/43389413267) (`main`, `0c4a682`), [43392852374](https://github.com/Leslie581/tdl-turistico-colima/actions/runs/43392852374) y [43394795003](https://github.com/Leslie581/tdl-turistico-colima/actions/runs/43394795003) (rama de Eimy, `c47d4e4`) y [43394817663](https://github.com/Leslie581/tdl-turistico-colima/actions/runs/43394817663) (`main`, `c7302f8`), consultadas en la API pública el 2026-11-13. Eso ocurrió en Linux con Python 3.13, así que el oro regenerado coincide con el versionado también allí (no hubo la diferencia de último decimal entre Windows y Linux que se temía). Corte 2026-11-14 03:14 UTC: `ci.yml` suma **25 ejecuciones: 21 en éxito, 1 cancelada por la política de concurrencia y 3 fallidas**. Las 3 fallidas son del commit `9489dc5` del tablero (push, pull request y push de `main` en `06452fd`) y **no** son del paso del oro: una prueba del tablero dependía de `__pycache__`. La corrigió `eb8f606` (PR #15) y `main` (`ac9c88d`, ejecución [43548657495](https://github.com/Leslie581/tdl-turistico-colima/actions/runs/43548657495)) terminó en **éxito**. Los registros detallados de las ejecuciones fallidas no se leyeron (requieren sesión): la causa se confirmó reproduciéndola en un clon limpio (Auditoría 7, V1).
- **`TDL_EXIGIR_PRONOSTICOS=1`:** en el job `calidad`, las pruebas del laboratorio (`tests/test_laboratorio_pronosticos.py`, integrada en `main` con el PR #9, y `tests/test_exploracion.py`) **fallan** si faltan `statsmodels`, `scipy` o `matplotlib`, en vez de omitirse. La captura diaria no instala esas librerías y omite esas pruebas. Ningún paso redefine la variable (hay una prueba que lo comprueba).
- **`TDL_EXIGIR_TABLERO=1`:** en el trabajo `calidad`, las pruebas de la aplicación del tablero (`tests/test_tablero_app.py`) **fallan** si faltan `altair` o `streamlit`, en vez de omitirse. La captura diaria no instala el tablero y omite esas pruebas. Ningún paso redefine la variable (hay una prueba que lo comprueba).
- **`gitleaks` en CI:** el trabajo `secretos` de `ci.yml` lo ejecuta con el binario 8.30.1 fijado por versión y verificado por *hash*, sobre el historial completo y con `--redact` ([`seguridad.md`](seguridad.md) §3.4). Está implementado en esta rama y verificado localmente (control positivo y escaneo sin hallazgos), pero **su primera ejecución en GitHub llegará con el push**. Los escaneos locales del 2026-11-13 (versión 8.30.1) dieron 0 hallazgos en el historial y en el árbol de trabajo: [`seguridad.md`](seguridad.md) §3.

## 7. Pruebas
`tests/test_pipeline_plata.py` (esquema, tipos, duplicados, faltantes y cada regla de calidad), `test_pipeline_oro.py` (fórmula de cociente de sumas, 108 periodos, columnas, diccionario), `test_pipeline_interfaz.py` (partición 96 + 12 y ausencia de fuga), `test_pipeline_reproducibilidad.py` (byte a byte, bronce intacto, fallo controlado), `test_pipeline_real.py` (el pipeline sobre el bronce real y contra una derivación independiente) y `test_ci_workflow.py` (propiedades técnicas de `ci.yml`: orden de los pasos, que los módulos y archivos que invoca existan, que la exigencia de pruebas estadísticas no se anule y que la captura diaria no dependa de librerías opcionales). `test_pipeline_transformaciones.py` (ausencia de fuga temporal), `test_exploracion.py` (cifras y PNG) y `test_verificar_oro.py` (comparación con git, con repositorios sintéticos y con el bronce y el oro reales) completan la fase L2. Las de `plata`, `oro`, `interfaz` y `reproducibilidad` usan datos **sintéticos** y lo declaran; no son evidencia operativa.
