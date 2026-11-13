# Laboratorio de pronósticos E1

Responsable: Eimy Melissa Urbina Meza (integrante B). Metodología y resultados: [`docs/E1/pronostico.md`](../../docs/E1/pronostico.md).

## Ejecutar
```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt -r laboratorio/pronosticos/requirements-pronosticos.txt
.venv/Scripts/python -m laboratorio.pronosticos.ejecutar                 # oro si existe; si no, derivación §7
.venv/Scripts/python -m laboratorio.pronosticos.ejecutar --fuente oro    # evaluación definitiva (exige el oro)
.venv/Scripts/python -m pytest tests/test_laboratorio_pronosticos.py -q
```
La ejecución dura entre 30 y 45 s (búsqueda de 72 SARIMA). Es reproducible: lo único simulado es el intervalo de Holt-Winters con estacionalidad multiplicativa, con semilla fija (`modelos.SEMILLA_SIMULACION`).

**Dependencias:** `statsmodels`, `scipy` y `matplotlib` aún no están en `requirements.txt` (integrante A). Sin ellas, las pruebas se omiten con el motivo `PRUEBAS DE PRONÓSTICOS NO EJECUTADAS`. Con `TDL_EXIGIR_PRONOSTICOS=1`, su falta es un error, que es como debe correr el CI de E1. Detalle: `docs/E1/pronostico.md` §8.

## Fuente de datos
`datos.cargar_serie("auto")` lee `data/oro/manzanillo_ocupacion_mensual.csv` si existe (con `pipeline.interfaz.cargar_oro_mensual` cuando la integrante A lo publique), valida el esquema del contrato 1.0.0 y **compara el oro con la derivación de referencia del contrato §7** (tolerancia 1e-5). Si no coinciden, la ejecución se detiene. Sin oro, usa la derivación §7. `resultados/ejecucion.json` registra qué fuente se usó, las huellas SHA-256 y las versiones.

## Módulos
| Archivo | Contenido |
|---|---|
| `datos.py` | Carga, validación de forma, verificación oro ↔ referencia, partición 96 + 12 |
| `estadistica.py` | Caracterización, descomposición (criterio aditiva/multiplicativa), ADF + KPSS, elección de d y D, ACF/PACF, correlación cruzada sin fuga |
| `modelos.py` | SES, Holt, Holt-Winters (ETS), SARIMA (búsqueda por AICc), métricas, residuos, criterio de selección |
| `ejecutar.py` | Orquestador: tablas, figuras y metadatos en `resultados/` |

## Salidas (`resultados/`)
| Archivo | Qué contiene |
|---|---|
| `comparacion_modelos_2024.csv` | MAE, RMSE, MAPE, sesgo, AICc, cobertura del IP 95 % y pruebas de residuos por modelo |
| `pronosticos_2024_por_modelo.csv` | Proyección retrospectiva 2024 de cada modelo y del ingenuo estacional, con el observado |
| `pronostico_modelo_elegido.csv` | Modelo elegido: 2024 retrospectivo y 2025 futuro, con IP 95 % y columna `tipo` |
| `candidatos_aicc.csv` | Todas las variantes evaluadas por familia y su AICc |
| `estacionariedad_adf_kpss.csv`, `acf_pacf_*.csv`, `correlacion_cruzada.csv` | Pruebas estadísticas (solo entrenamiento) |
| `residuos_modelo_elegido.csv`, `resumen.json`, `ejecucion.json` | Residuos, resumen completo, procedencia y versiones |
| `figuras/*.png` | Identificación SARIMA, comparación 2024, residuos y pronóstico. Cada figura tiene su CSV |

Las gráficas exploratorias de la serie (serie completa, descomposición, ACF/PACF en niveles) corresponden a `laboratorio/exploracion/` (integrante A) y no se duplican aquí.
