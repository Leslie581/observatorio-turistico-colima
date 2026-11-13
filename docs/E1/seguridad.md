# Seguridad del sistema de información (E1)

Rama `e1/leslie-calidad` · corte **2026-11-13** · Responsable: Leslie Valadez Macías (integrante A).
Requisito (PDF, pág. 16): «búsqueda de secretos en el historial con **gitleaks**, vulnerabilidades de dependencias con **pip-audit**, tokens con el **mínimo permiso** necesario y **respaldo de la capa bronce**». Rúbrica (pág. 25, 15 pts): «gitleaks y pip-audit sin hallazgos abiertos; respaldo probado» frente a «secretos expuestos».
**Este documento no publica ningún valor secreto**: lo que se encontrara se describiría por archivo, tipo y gravedad, nunca por contenido.

## 1. Resumen
| Control | Resultado | Estado |
|---|---|---|
| `gitleaks` v8.30.1 sobre el historial completo | Ejecutado el 2026-11-13: **0 hallazgos** (28 confirmaciones con líneas agregadas, 4.08 MB, todas las referencias) y **0** en el árbol de trabajo (18 rutas). Detalle en §3 | **CUMPLIDO** (una ejecución local; **aún no está en CI**) |
| UUID de `tests/test_base.py` | Valor de relleno (cada grupo repite un solo dígito), usado solo para probar el enmascarado; **no coincide** con el token local; `gitleaks` no lo marca | **Sintético** (§3.3) |
| Búsqueda manual de patrones de secretos (complementaria) | 42 confirmaciones, 60,407 líneas agregadas, 10 patrones: 0 secretos reales; 3 coincidencias en pruebas, valores sintéticos | Evidencia complementaria |
| `pip-audit` | «No known vulnerabilities found» en `requirements.txt`, `requirements-lab.txt` y `requirements-dev.txt` (2026-11-13); trabajo de CI en éxito | **CUMPLIDO** (foto de hoy) |
| Mínimo permiso en los flujos | `ci.yml`: solo lectura; captura: escritura de contenido y el secreto solo en un paso | **CUMPLIDO** (riesgos residuales en §4) |
| Secretos y variables de entorno | El token vive en un secreto de GitHub; ningún valor versionado | **CUMPLIDO** |
| Archivos ignorados por Git | Los nombres sensibles típicos están ignorados (comprobado con `git check-ignore`) | **CUMPLIDO** |
| Respaldo del bronce probado | Restauración desde un clon nuevo: 24 archivos y 3 verificaciones satisfactorias | **CUMPLIDO** (prueba manual; único respaldo: GitHub) |

## 2. Secretos, tokens y variables de entorno
| Elemento | Dónde vive | Uso | Revisión |
|---|---|---|---|
| `INEGI_TOKEN` (token gratuito de DENUE) | **Secreto del repositorio** de GitHub; localmente, un `.env` ignorado por Git | Solo el paso «Captura DENUE» de `captura-diaria.yml` lo recibe (`env:` de ese paso); el extractor lo lee con `os.getenv` y lo enmascara (`***TOKEN***`) en bitácoras y URLs | `tests/test_workflow.py::test_token_solo_en_el_paso_de_captura_y_nunca_se_imprime`; `tests/test_base.py::test_bitacora_oculta_token_en_urls_y_errores`; 0 URL con token en el historial |
| `TDL_CONTACTO` | **Variable** (no secreto) del repositorio | Contacto del User-Agent hacia INEGI | Se revisó que **ningún correo** aparece en el bronce, la bitácora, el oro ni la cuarentena (0 archivos con patrón de correo). El valor de `.env.example` es un marcador de posición (`ejemplo.mx`) |
| `TDL_RED`, `TDL_EXIGIR_PRONOSTICOS`, `TDL_UA` | Variables de ejecución | Habilitan pruebas de red, exigen pruebas estadísticas y cambian el User-Agent | No contienen secretos |
| `.env.example` | Versionado | Plantilla **sin valores secretos** (`INEGI_TOKEN=` vacío) | Es el único archivo de este tipo en `git ls-files` |
**Qué no se puede verificar desde aquí:** que el secreto `INEGI_TOKEN` esté configurado con el valor correcto y rotado (GitHub no lo muestra). Si el valor llegó a escribirse alguna vez en un chat, un correo o un archivo, **debe rotarse en INEGI**.

## 3. `gitleaks`
### 3.1 Herramienta y verificación de origen
| Punto | Resultado |
|---|---|
| Herramienta y versión | `gitleaks` **8.30.1** (`gitleaks version` → `8.30.1`) |
| Origen | Repositorio oficial `gitleaks/gitleaks` en GitHub, [release v8.30.1](https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1), marcada como la última, no es *prerelease* ni borrador; publicada el 2026-03-21 02:17 UTC por la cuenta del mantenedor del proyecto (`zricethezav`) |
| Archivo descargado | `gitleaks_8.30.1_windows_x64.zip` (8,438,883 bytes) y `gitleaks_8.30.1_checksums.txt`, desde las URL de esa release, a una carpeta nueva y vacía fuera del repositorio |
| SHA-256 | `d29144deff3a68aa93ced33dddf84b7fdc26070add4aa0f4513094c8332afc4e`. **Coinciden tres valores:** el calculado localmente, el de `checksums.txt` de la release y el *digest* que calcula GitHub para ese archivo |
| Firma | El ejecutable **no está firmado con Authenticode** (`NotSigned`), algo habitual en este binario. No se verificó una firma criptográfica del publicador |
| Instalación | **Sin instalador.** El zip contenía solo `LICENSE`, `README.md` y `gitleaks.exe` (se revisaron las rutas antes de extraer). Se ejecutó desde la carpeta temporal, sin agregarlo al `PATH` y **sin cambiar ningún control de seguridad de Windows** (no fue bloqueado) |
| Qué prueban y qué no | Los tres *hash* salen del mismo origen (GitHub): confirman que el archivo es el de la release y no se corrompió, pero **no prueban por sí solos la identidad del autor**. El binario y el reporte **no se versionan** |

### 3.2 Ejecución, alcance y resultado real
**Fecha:** 2026-11-13, 02:23 a 02:24 hora de la Ciudad de México (08:23 a 08:24 UTC). **Reglas:** el conjunto por defecto de la versión 8.30.1 (el repositorio no tiene `.gitleaks.toml`; no se desactivó ninguna regla). `--redact` (100 %): ningún valor aparece en la consola ni en el reporte, que se guardó fuera del repositorio.
**Comandos:**
```bash
gitleaks version
gitleaks git . --log-opts="--all" --redact --no-banner --report-format json --report-path <fuera del repositorio>
gitleaks dir <ruta> --redact --no-banner --report-format json --report-path <fuera del repositorio>   # una vez por cada ruta versionada
```
| Alcance | Resultado |
|---|---|
| **Historial Git** (`git`, todas las referencias: 19 ramas locales y remotas; 42 confirmaciones) | `28 commits scanned`, ~4.08 MB, **`no leaks found`**, código de salida **0**, reporte `[]` |
| **Árbol de trabajo**, incluidos los cambios de L3 sin confirmar (`dir`, 18 rutas: `docs`, `calidad`, `pipeline`, `tests`, `laboratorio`, `extractores`, `.github`, `data` —8.57 MB— y 10 archivos de la raíz) | **`no leaks found`** en las 18 rutas |
**Hallazgos: 0.** Por eso no hay credenciales posibles que clasificar por archivo, tipo ni gravedad.
**Por qué 28 y no 42 confirmaciones:** 13 son fusiones (no tienen diff propio) y 1 (`18232f0`) solo **elimina** un archivo (+0 líneas agregadas; una ejecución sobre esa sola confirmación da «0 commits scanned»). El contenido que eliminó se agregó antes en `55bc6b4`, que sí se escaneó.
**Lo que NO se escaneó (límites):** `.venv/` y los archivos ignorados por Git; el `.env` local (no versionado, contiene el token real: fuera del alcance por diseño); los secretos y los registros de ejecución de GitHub Actions; los artefactos de Actions (retención de 30 días); issues y comentarios de pull request; los objetos del repositorio inalcanzables desde cualquier referencia. **Que `gitleaks` no encuentre nada no demuestra que no haya un secreto en esos lugares ni uno que sus reglas no reconozcan.**
**Es una ejecución local, única y manual.** No está integrada en CI, así que no se repetirá sola con cada cambio.

### 3.3 Búsqueda manual complementaria y el UUID de `tests/test_base.py`
- **Búsqueda manual** (script propio, 10 patrones, líneas agregadas de las 42 confirmaciones): 0 coincidencias para 8 patrones y **3 candidatas** en 2 archivos de pruebas (introducidas en `ef6d23bd50ca`). **`gitleaks` no marcó ninguna de las tres.** No sustituye a `gitleaks`.
- **Evaluación del UUID** (valor no mostrado), realizada el 2026-11-13:
  | Evidencia | Resultado |
  |---|---|
  | Estructura | Cada uno de los 5 grupos repite **un solo dígito** (`AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE`): un patrón de relleno, no un UUID aleatorio |
  | Uso en la prueba | `test_bitacora_oculta_token_en_urls_y_errores`: lo asigna con `monkeypatch.setenv("INEGI_TOKEN", …)`, escribe solo en `tmp_path` y comprueba que **no** aparezca en la bitácora y que sí aparezca `***TOKEN***`. No hace llamadas de red |
  | Apariciones | 1 en todo el repositorio versionado (solo esa prueba) |
  | Comparación con el token real | **No coincide** con el `INEGI_TOKEN` disponible en la máquina (`.env` y entorno). La comparación se hizo en memoria y **no se imprimió ningún valor** |
  | `gitleaks` | No lo marca |
  **Conclusión: claramente sintético**, por su estructura y por su uso. **Límite:** no se puede comparar con el valor del secreto guardado en GitHub (GitHub no lo muestra); aun así, un valor de relleno de dígitos repetidos no es un token plausible. No hace falta rotar nada por este valor. Mejora opcional: sustituirlo por un texto evidentemente falso (como `TOKEN-DE-PRUEBA-…`) para que ningún escáner lo vuelva a señalar; la confirmación antigua permanecería en el historial.
- La otra coincidencia (`tests/test_captura_denue.py:40`, valor por defecto `TOKEN-DE-PRUEBA-123`) es evidentemente sintética.

### 3.4 Integración en CI (pendiente; plantilla **no probada** en GitHub)
La versión y el *hash* del binario de Linux salen de la misma release verificada (`gitleaks_8.30.1_checksums.txt`):
```yaml
secretos:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
      with: { fetch-depth: 0 }          # historial completo; con el valor por defecto (1) no sirve
    - name: gitleaks 8.30.1 (binario fijado y verificado)
      run: |
        curl -sSL -o gitleaks.tgz "https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz"
        echo "551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb  gitleaks.tgz" | sha256sum -c -
        tar xzf gitleaks.tgz gitleaks
        ./gitleaks git . --log-opts="--all" --redact --no-banner
```
Va como un trabajo aparte (como `auditoria-dependencias`) para que un aviso nuevo no bloquee todos los push. Si una futura ejecución marca un falso positivo, se resuelve con `.gitleaksignore` por huella y un comentario que explique por qué es sintético, no silenciando una regla completa. Tras agregarlo hay que **verificar su primera ejecución real** antes de afirmar que funciona.

## 4. Permisos de los flujos de trabajo
| Flujo | Permisos | Disparadores | Secretos | Revisión |
|---|---|---|---|---|
| `ci.yml` | `contents: read` (solo lectura) | `push` y `pull_request` | Ninguno (`tests/test_ci_workflow.py` lo comprueba) | Sin `pull_request_target`, de modo que un PR de un fork no ve secretos |
| `captura-diaria.yml` | `contents: write` | `schedule` y `workflow_dispatch` | `INEGI_TOKEN`, solo en el paso de captura | El permiso de escritura es **necesario** (el bot guarda la bitácora y el bronce); es el mínimo para ese trabajo. Las entradas del usuario (`inputs.forzar`) y `GITHUB_REF_NAME` llegan al *shell* por variables de entorno, no interpoladas en el comando (sin inyección de comandos) |
**Riesgos residuales (abiertos):**
1. **Acciones fijadas por etiqueta, no por *hash*** (`actions/checkout@v4`, `setup-python@v5`, `upload-artifact@v4`): una etiqueta puede moverse. Son solo acciones oficiales de GitHub, no de terceros; fijar por *hash* de confirmación reduciría el riesgo.
2. **Rama `main` sin protección verificable.** La API pública no revela la protección de rama (requiere autenticación de administrador). Los PR #8, #9 y #10 se fusionaron sin revisiones. Con `main` protegida habría que dar una excepción al bot de captura (riesgo R2 de [`riesgos.md`](../../calidad/riesgos.md)).
3. **Dependencias sin `--require-hashes`**: las versiones están fijadas con `==`, pero no sus *hashes*; un paquete reemplazado en el índice con el mismo número de versión no se detectaría.
4. **`persist-credentials` por defecto** en `checkout` (necesario para que el bot empuje); en `ci.yml`, donde solo se lee, podría desactivarse.

## 5. Dependencias (`pip-audit`)
- **Herramienta:** `pip-audit 2.10.1`, fijada en `requirements-dev.txt` y usada en el trabajo `auditoria-dependencias` de `ci.yml`.
- **Resultado local del 2026-11-13** (`python -m pip_audit -r <archivo> --no-deps --disable-pip`): **«No known vulnerabilities found»** para `requirements.txt` (28 paquetes), `requirements-lab.txt` (14) y `requirements-dev.txt` (20). El trabajo de CI terminó en éxito en las ejecuciones de ese día.
- **Alcance y límites:** audita las versiones **fijadas** contra la base de vulnerabilidades en la fecha de la consulta; una vulnerabilidad publicada mañana no aparece hoy. Va en un trabajo aparte para que un aviso nuevo no bloquee todos los push; la rúbrica pide **cerrar** los hallazgos, así que cualquier aviso futuro exige actualizar la dependencia o documentar una excepción.

## 6. Respaldo y restauración de la capa bronce
- **Respaldos existentes:** (a) el repositorio de GitHub (el bronce está versionado, salvo los datos que no se publican por ética, `.gitignore`) y (b) la copia local. No hay una copia independiente verificada en otro proveedor.
- **Prueba de restauración (2026-11-13), repetible:**
  ```bash
  git clone --depth 1 https://github.com/Leslie581/observatorio-turistico-colima.git <carpeta_vacia>
  python -c "from pathlib import Path; from pipeline.verificar_e0 import integridad, historico, privacidad; \
b = Path('<carpeta_vacia>/data/bronce'); print(integridad(b)['estado'], historico(b)['estado'], privacidad(b)['estado'])"
  ```
  (el código verificador es el del proyecto local, no el del clon.)
- **Resultado:** clon de `0c4a682`; **24 archivos** de bronce restaurados; integridad (SHA-256 y tamaño contra cada ficha), histórico y privacidad **satisfactorios**; el SHA-256 de `Base70centros.csv` del clon (`a8ca3f9b…`) es idéntico al local.
- **Limitaciones:** la prueba es **manual y puntual** (no está automatizada en CI); el único respaldo remoto es GitHub (si la cuenta o el repositorio se pierden, no hay otra copia); no se probó restaurar el estado de un día anterior (solo el actual).

## 7. Pendientes de seguridad
1. **Integrar `gitleaks` en CI** (§3.4) y verificar su primera ejecución real; hoy es una ejecución local única.
2. **Decidir la protección de `main`** (revisión obligatoria + CI) y la excepción para el bot.
3. **Fijar las acciones por *hash*** y valorar `--require-hashes`.
4. **Copia independiente del bronce** (otro proveedor o disco) y prueba periódica de restauración.
5. Opcional: reemplazar el UUID sintético de `tests/test_base.py` por un texto evidentemente falso (§3.3).
