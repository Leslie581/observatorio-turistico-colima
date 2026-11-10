# Verificación de E0: pruebas, estado de cada requisito y GitHub Actions

Corte 2026-11-09. Estados: **VERIFICADO** (ejecutado aquí y pasó) · **IMPLEMENTADO SIN PROBAR** · **DOCUMENTADO** · **FALLIDO** · **PENDIENTE** · **NO VERIFICABLE** (no se puede comprobar desde este entorno).
Nada del prototipo se cuenta como prueba de este repositorio sin haberse vuelto a ejecutar.

## 1. Pruebas ejecutadas el 2026-11-09 (Windows, Python 3.13.15, venv limpio con `requirements.txt`)

| Comprobación | Resultado | Estado |
|---|---|---|
| `python -m pytest -q -rs` | 57 aprobadas, 2 omitidas (requieren `TDL_RED=1` y token; **no cuentan como aprobadas**); 0 fallos | VERIFICADO |
| Cobertura (`--cov=extractores --cov=pipeline`) | 80 % global (`captura_denue` 76 %, `denue` 94 %, `verificar_e0` 88 %) | VERIFICADO (informativa; el umbral de 60 % del Sello es de E1) |
| Importación de módulos | `base`, `denue`, `datatur`, `captura_denue`, `verificar_e0` | VERIFICADO |
| `pip check` | Sin requisitos rotos | VERIFICADO |
| `python -m pipeline.verificar_e0 --solo historico` | Archivo existe y no vacío, fechas válidas, sin duplicados, periodos consecutivos, 108 periodos (mínimo 36), 2016-01 a 2024-12, hash y tamaño = ficha. Probado también con CSV sintéticos negativos (hueco, duplicado, fecha inválida, <36, vacío, hash distinto) sin tocar el original | VERIFICADO |
| `… --solo integridad` | SHA-256 y tamaño de `Base70centros.csv` = ficha (`a8ca3f9b…d671`) | VERIFICADO |
| Hash de `Base70centros.csv` contra la descarga oficial en navegador | Idéntico (2026-11-09 15:52 UTC; `docs/fuentes/evidencias/`) | VERIFICADO (verifica contenido, no autoriza nada) |
| Hash del blob en el índice de Git | Igual al del archivo (sin conversión CRLF) | VERIFICADO |
| `… --solo privacidad` | `sin_datos`: **0 archivos reales del DENUE**; no demuestra que la sanitización funcione sobre datos reales | PENDIENTE (hasta la primera captura real) |
| Pruebas de sanitización (personales, `Nombre` y domicilio) y captura con extractor simulado | Elimina teléfono, correo, sitio web, razón social; no duplica el mismo día; falla explícitamente sin token; el token no aparece en bitácora ni fichas | VERIFICADO (simulado) |
| Escaneo de secretos en archivos preparados para commit | Sin tokens reales; solo el token ficticio de una prueba | VERIFICADO |
| `tests/test_workflow.py` sobre `captura-diaria.yml` | Estructura: solo DENUE; token solo en el paso de captura; el paso final (`if: always()`) falla si captura o verificación obligatoria no fueron `success`; la evidencia se sube antes; el bronce solo se publica si la verificación pasó | VERIFICADO (estructura, **no** ejecución en GitHub) |
| Captura DENUE real desde este repositorio | No se ejecutó: no hay `INEGI_TOKEN` en este entorno y no se pidió | PENDIENTE |
| Prueba de red (`TDL_RED=1`) | No ejecutada | PENDIENTE |
| Disponibilidad de la captura (objetivo O1) | Sin bitácora real | PENDIENTE |
| Descarga automática de Base70 | El servidor responde 403 a scripts; no se evade | NO VERIFICABLE por diseño |

## 2. Estado de GitHub Actions (no confundir niveles)

| Nivel | Estado |
|---|---|
| Workflow **implementado** (`.github/workflows/captura-diaria.yml`) | Sí |
| **Prueba local** de la lógica que el workflow ejecuta (pytest + captura simulada) | Sí (sección 1) |
| **Ejecución manual real en GitHub** (`workflow_dispatch`) | **VERIFICADO en la bitácora**: 42729922838 (fallo: sin `INEGI_TOKEN`), 42730477358 y 42733335021 (éxito, 134/134), 42732765759 y 42733220215 (omitidas por duplicado). El color de cada job se confirma en la página de la ejecución |
| **Ejecución programada real en GitHub** (`schedule`) | **PENDIENTE**: ninguna ejecución con `disparador: schedule` todavía (la primera es ≈ 13:17 UTC) |
| Repositorio remoto | `main` publicado; las ejecuciones las lanzó el equipo desde GitHub (esta herramienta no tiene `gh` ni acceso autenticado) |

Cambios tras la revisión independiente: el paso final evalúa **captura y verificación obligatoria**; la verificación usa `--exigir-datos` (sin archivos que inspeccionar = fallo); `disponibilidad` es informativa; bash con `pipefail` para que `| tee` no oculte fallos; `pytest -rs` lista las omitidas; el bronce no se publica si la verificación falla (la bitácora sí).

Características del workflow: `workflow_dispatch` (con `forzar`) y `schedule` diario 13:17 UTC; dependencias fijadas; `concurrency` (un solo escritor); el secreto `INEGI_TOKEN` solo está en el entorno del paso de captura; permisos `contents: write` únicamente para guardar bitácora y bronce sanitizado; la bitácora se guarda también cuando falla; evidencia en el resumen de la ejecución y en un artefacto (30 días); la ejecución termina en rojo si la captura falla; no hay captura de DATATUR.
Límites conocidos: si `main` tiene protección de rama, el `git push` del workflow fallará (hay que permitir al bot o usar una rama de datos); GitHub desactiva los workflows programados tras 60 días sin actividad en el repositorio; las acciones se referencian por etiqueta (`@v4`), no por SHA.

### Pasos para obtener la evidencia desde su cuenta
1. Crear/confirmar el repositorio y subir `main` (decisión suya; yo no hice push).
2. *Settings → Secrets and variables → Actions*: secreto **`INEGI_TOKEN`** (token gratuito de INEGI) y variable **`TDL_CONTACTO`** (correo del equipo para el User-Agent).
3. *Actions → captura-diaria-denue → Run workflow* (rama `main`). Debe terminar en verde; abrir el resumen y confirmar `resultado: exito`, `registros ≈ esperado_cuantificar`.
4. Verificar que apareció el commit del bot con `calidad/bitacora_capturas.jsonl` y `data/bronce/denue/AAAA-MM-DD/…`; que esos JSON **no** contienen `Telefono`, `Correo_e`, `Sitio_internet` ni `Razon_social`; y que el token no aparece en ningún log.
5. Repetir con *Run workflow* el mismo día: debe registrar `omitida_duplicada` sin consultar la API.
6. Al día siguiente (≈ 07:17 hora de Ciudad de México) comprobar que corrió sola por `schedule` (`disparador: schedule` en la bitácora). Guardar los enlaces de las ejecuciones en `docs/E0/ENTREGA.md`.
7. Si algo falla, **conservar** la ejecución roja y la bitácora; son evidencia para el registro de defectos.

## 3. Comandos para reproducir (PowerShell)
Ver la sección “Reproducir” del [README](../../README.md).
