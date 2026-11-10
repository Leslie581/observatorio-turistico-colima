# Inventario de migración (prototipo → repositorio definitivo)

Origen: carpeta del prototipo (`staymetrics-prototipo`, **solo lectura**; no se modificó nada). Destino: este repositorio. Corte 2026-11-09.
Estado de validación (tras migrar, en el repositorio definitivo): **VERIFICADO** = se ejecutó aquí y pasó · **IMPLEMENTADO SIN PROBAR** · **DOCUMENTADO** · **PENDIENTE**. Comando: `python -m pytest -q` (91 pasan, 2 omitidas por requerir red y token, al 2026-11-10).

## 1. Migrado

| Origen | Destino | Motivo | Cambios | Dependencias | Prueba | Estado |
|---|---|---|---|---|---|---|
| `extractores/base.py` | `extractores/base.py` | Extractor ético del Kit (robots.txt, User-Agent honesto, pausa ≥ 1 s, reintentos, bitácora, bronce con metadatos, enmascarado de token) | Solo nombres: User-Agent `ObservatorioHotelero-TDL/0.1`, variables `TDL_CONTACTO`/`TDL_UA`, logger `observatorio`. Lógica intacta. | requests | `tests/test_base.py` | VERIFICADO |
| `extractores/denue.py` | `extractores/denue.py` | Segunda fuente: cliente DENUE y 7 controles | **Añadido** `sanitizar_crudo`: `guardar_respuestas_crudas` elimina teléfono, correo, sitio web, razón social y detalle de domicilio **antes** de escribir bronce (campos conservados y justificación en `docs/fuentes/denue.md`), y guarda `sha256_respuesta_original`. Razón: la regla del proyecto es cero datos personales en bronce y el prototipo guardaba los crudos con ellos. | pandas | `tests/test_denue.py`, `tests/test_captura_denue.py` | VERIFICADO (con respuestas simuladas) |
| `extractores/datatur.py` | `extractores/datatur.py` | Lectura y validación de `Base70centros.csv`; importación local con procedencia | Solo el nombre en la docstring. Se conservan el espejo y las descargas de reportes PDF **sin usar** (ninguna ruta de este repositorio las invoca). | pandas (pdfplumber solo si se parsean PDF) | `tests/test_datatur.py` | VERIFICADO (sin red) |
| `tests/conftest.py`, `test_base.py`, `test_denue.py`, `test_datatur.py` | `tests/…` | Pruebas de extracción reutilizadas | Variable de entorno `TDL_RED`; nombre en una aserción | pytest | idem | VERIFICADO |
| `tests/test_integracion_red.py` | `tests/test_integracion_red.py` | Pruebas con red | **Reescrito**: solo DENUE. Se quitaron las pruebas que consultaban reportes PDF, el robots del Sistema de Monitoreo y la descarga de Base70 (403) | requests, token | idem | IMPLEMENTADO SIN PROBAR (necesita `TDL_RED=1` y token) |
| `tests/fixtures/base70_muestra_real.tsv` | idem | Subconjunto real y sin modificar de Base70 (CC BY 4.0) | Ninguno | — | `test_datatur.py` | VERIFICADO |
| `data/bronce/datatur/Base70centros.csv` y `.meta.json` | idem | **Histórico ≥ 36 periodos** (108 en Manzanillo) | Ninguno (byte a byte, SHA-256 `a8ca3f9b…d671`; `.gitattributes` evita conversión de finales de línea) | — | `pipeline.verificar_e0 --solo historico/integridad` | VERIFICADO |
| `.env.example`, `.gitignore`, `requirements.txt` | idem | Configuración | Rehechos: variables `TDL_*`, exclusiones de datos no autorizados, dependencias **fijadas** y reducidas a lo que E0 usa (sin scipy, sklearn, matplotlib, openpyxl, pdfplumber) | — | `pip check`, instalación en venv limpio | VERIFICADO |

## 2. Nuevo en el repositorio definitivo (no existía en el prototipo)

| Archivo | Para qué | Estado |
|---|---|---|
| `extractores/captura_denue.py` | Captura diaria idempotente del DENUE, bitácora de ejecuciones, código de salida | VERIFICADO (simulado y en 2 capturas reales manuales de GitHub Actions) |
| `pipeline/verificar_e0.py` | Histórico (existencia, fechas, duplicados, huecos, ≥ 36, hash), integridad, privacidad, disponibilidad; distingue satisfactoria / fallida / sin_datos | VERIFICADO |
| `.github/workflows/captura-diaria.yml`, `tests/test_workflow.py` | Workflow programado + manual; pruebas de su estructura (usa PyYAML, añadido a las dependencias) | IMPLEMENTADO SIN PROBAR en GitHub |
| `calidad/*`, `docs/**` | Registros PSP vacíos, objetivos, propuesta, ficha, fuentes | DOCUMENTADO |

## 3. No migrado (con motivo)

| Origen | Motivo | Cuándo se reconsidera |
|---|---|---|
| `extractores/monitoreo.py` y `tests/test_monitoreo.py`, `tests/fixtures/monitoreo/*` | Automatiza el endpoint interno `Ajax.aspx`; autorización no confirmada y los términos de gob.mx restringen la difusión pública (los fixtures son respuestas reales del generador). No se deja código listo para activar. | Si el equipo decide la opción 2 de `docs/fuentes/datatur.md` §7 y llega autorización escrita |
| `extractores/main.py` | Orquestador acoplado a Base70, reportes PDF, monitoreo y a `validacion/calidad.py`. Se sustituye por `captura_denue.py` (más simple, sin esas fuentes). | — |
| `validacion/calidad.py` (12 validaciones, cuarentena, capa validada) | Es la puerta de calidad bronce→plata: pertenece a **E1** | E1 |
| `analisis/viabilidad.py`, `resultados/*`, `tests/test_viabilidad.py`, `tests/test_calidad.py` | Experimentos estadísticos exploratorios (E1–E3) | E1–E3 |
| `DataturReportePublico_original.csv`, `data/bronce/datatur_monitoreo/*`, `evidencias/diagnostico_monitoreo_*`, `evidencias/monitoreo_exportacion_manual/` | Canal B: publicación no autorizada. Se documentan hashes y procedimiento en `docs/fuentes/datatur.md` §6 | Con autorización |
| `data/bronce/denue/crudo/*`, `data/validada/denue_*.csv` | Contienen teléfono, correo, sitio web y razón social | No se migran; el bronce se regenera sanitizado |
| `data/validada/*`, `data/cuarentena/*` | Capas derivadas (E1) y reescritas con otro fin de línea por la puerta de calidad | E1 |
| `logs/bitacora.jsonl`, `evidencias/ejecucion_windows_*` | Logs del prototipo; el segundo contiene 445 KB de metadatos y salidas de pruebas con rutas locales | — |
| `.github/workflows/captura.yml`, `prueba_extraccion.yml` | `captura.yml` descarga Base70 de un servidor que responde 403 a scripts, usa el espejo en caso de fallo, ejecuta DATATUR y hace `git push` de `data logs resultados`; `prueba_extraccion.yml` consulta DATATUR/Open-Meteo. Se reemplazan por `captura-diaria.yml` | — |
| `docs/*` del prototipo, `INFORME_PARA_CLAUDE.md`, `salida_validacion.txt` | Informes de viabilidad con otra finalidad; su contenido útil se reescribió citando origen en `docs/fuentes/`. Evita duplicar. | — |
| `.venv`, `.pytest_cache`, `__pycache__`, `*.pyc` | Entornos y cachés | Nunca |
| `pruebas_externas/*` | Scripts de diagnóstico del endpoint interno y de verificación en Windows | — |

## 4. Hallazgos del prototipo que cambian lo reutilizable
- Las afirmaciones “108 meses = oficial” se apoyaban en un hash calculado con el navegador y transcrito; hoy se repitió la verificación y coincide (`docs/fuentes/evidencias/`).
- El archivo `evidencias/ejecucion_windows_…/datatur_oficial/Base70centros.csv` (443 bytes) **no son datos**: es la página “Access Denied” del CDN.
- La prueba pytest con red del extractor de monitoreo **no tiene evidencia entregada** en el prototipo (su propio informe lo reconoce).
- `captura.yml` del prototipo nunca se ejecutó en GitHub.
