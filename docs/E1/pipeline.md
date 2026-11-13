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
| `pipeline/interfaz.py` | `cargar_oro_mensual`, `serie_objetivo`, `partir_entrenamiento_prueba` para el laboratorio |
| `pipeline/ejecutar.py` | Orquestador; escribe solo cuando todo se calculó y validó |
| `pipeline/transformaciones.py` | Min-max, z-score y discretización con parámetros ajustados solo con 2016–2023 ([`transformaciones.md`](transformaciones.md)) |
| `pipeline/verificar_oro.py` | Compara el oro regenerado con el versionado en git (puerta de CI) |
| `laboratorio/exploracion/explorar.py` | Cuatro gráficas y estadísticas descriptivas del oro ([`exploracion.md`](exploracion.md)) |

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

## 6. Dependencias y CI
| Archivo | Contenido | Quién lo instala |
|---|---|---|
| `requirements.txt` | Núcleo: captura, pipeline y `pandera` (28 paquetes fijados) | El workflow diario de captura |
| `requirements-lab.txt` | `statsmodels`, `scipy`, `matplotlib` (14 paquetes fijados) | Solo `ci.yml` y quien trabaje en el laboratorio |
| `requirements-dev.txt` | `ruff` y `pip-audit` | `ci.yml` |
- **Por qué están separados:** el workflow de captura corre las pruebas con `requirements.txt`; si las librerías del laboratorio estuvieran ahí, una falla de instalación de `scipy` o `statsmodels` detendría la captura diaria. El núcleo incluye `pandera` porque las pruebas del pipeline lo importan.
- **Compatibilidad comprobada en esta máquina** (Python 3.13.15, Windows 11, `pandas 3.0.5`): `pandera 0.36.0` valida con `pandas 3.0.5`; `statsmodels 0.15.0`, `scipy 1.18.1` y `matplotlib 3.11.2` se importan; `pip check` sin conflictos; `pip-audit` sin vulnerabilidades conocidas en `requirements.txt` y `requirements-lab.txt` (corrida local del 2026-11-13). **No** se probó la instalación desde cero en Linux ni en GitHub.
- `wrapt` (dependencia de `formulaic`): pip había resuelto `2.6.0.dev1`, una versión previa. Se sustituyó por la estable `2.5.2`, que cumple el requisito de `formulaic` (`wrapt>=1.17.0rc1` en Python 3.13); con ella `pip check` sale limpio e importan `formulaic`, `statsmodels`, `scipy` y `matplotlib` (2026-11-13). Nota: en esta máquina el Control de aplicaciones de Windows bloquea de forma intermitente alguna DLL de `statsmodels` (p. ej. `_kalman_smoother`); es un límite del entorno local, no de las versiones, y obliga a validar el laboratorio en CI/Linux.
- **`ci.yml`:** en cada push y pull request corre linter (`ruff`), pruebas con `-rs`, el pipeline, la comprobación «oro regenerado = oro versionado» y el verificador de E0; `pip-audit` va en un trabajo aparte. **Ejecuciones reales en GitHub (2026-11-13, consultadas en la API pública de Actions):** los dos trabajos (`calidad` y `auditoria-dependencias`) terminaron en éxito para el commit `70a26b9` (push y pull request), para `main` en `7e64ffa` (fusión del PR #8) y para la rama y la fusión del laboratorio de Eimy (PR #9, `main` en `49934ca`). Ejemplo: [ejecución 43381255086](https://github.com/Leslie581/observatorio-turistico-colima/actions/runs/43381255086). Eso confirma que la instalación fijada y los pasos funcionan en Linux con Python 3.13. **No se leyeron los registros de esas ejecuciones** (requieren sesión); solo su resultado por trabajo y paso.
- **La comprobación del oro (`pipeline/verificar_oro.py`) aún no ha corrido en GitHub:** se añadió después de esas ejecuciones y se probó solo en local (incluida una prueba con el bronce y el oro reales). Su primera ejecución real será la de esta rama; si el oro difiriera entre Windows y Linux (por ejemplo, en el último decimal de un cociente), ese paso lo mostrará y habrá que investigarlo, no ignorarlo.
- **`TDL_EXIGIR_PRONOSTICOS=1`:** en el job `calidad`, las pruebas del laboratorio (`tests/test_laboratorio_pronosticos.py`, integrada en `main` con el PR #9, y `tests/test_exploracion.py`) **fallan** si faltan `statsmodels`, `scipy` o `matplotlib`, en vez de omitirse. La captura diaria no instala esas librerías y omite esas pruebas. Ningún paso redefine la variable (hay una prueba que lo comprueba).
- `gitleaks` no está en el flujo (es un binario externo; pendiente).

## 7. Pruebas
`tests/test_pipeline_plata.py` (esquema, tipos, duplicados, faltantes y cada regla de calidad), `test_pipeline_oro.py` (fórmula de cociente de sumas, 108 periodos, columnas, diccionario), `test_pipeline_interfaz.py` (partición 96 + 12 y ausencia de fuga), `test_pipeline_reproducibilidad.py` (byte a byte, bronce intacto, fallo controlado), `test_pipeline_real.py` (el pipeline sobre el bronce real y contra una derivación independiente) y `test_ci_workflow.py` (propiedades técnicas de `ci.yml`: orden de los pasos, que los módulos y archivos que invoca existan, que la exigencia de pruebas estadísticas no se anule y que la captura diaria no dependa de librerías opcionales). `test_pipeline_transformaciones.py` (ausencia de fuga temporal), `test_exploracion.py` (cifras y PNG) y `test_verificar_oro.py` (comparación con git, con repositorios sintéticos y con el bronce y el oro reales) completan la fase L2. Las de `plata`, `oro`, `interfaz` y `reproducibilidad` usan datos **sintéticos** y lo declaran; no son evidencia operativa.
