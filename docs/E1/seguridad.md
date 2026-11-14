# Seguridad del sistema de información (E1)

Rama `e1/leslie-calidad` · corte **2026-11-13** · Responsable: Leslie Valadez Macías (integrante A).
Requisito (PDF, pág. 16): «búsqueda de secretos en el historial con **gitleaks**, vulnerabilidades de dependencias con **pip-audit**, tokens con el **mínimo permiso** necesario y **respaldo de la capa bronce**». Rúbrica (pág. 25, 15 pts): «gitleaks y pip-audit sin hallazgos abiertos; respaldo probado» frente a «secretos expuestos».
**Este documento no publica ningún valor secreto**: lo que se encontrara se describiría por archivo, tipo y gravedad, nunca por contenido.

## 1. Resumen
| Control | Resultado | Estado |
|---|---|---|
| `gitleaks` v8.30.1 sobre el historial completo | Ejecutado el 2026-11-13: **0 hallazgos** en el historial y en el árbol de trabajo (18 rutas); **reproducido y versionado** sobre `main` (`c7302f8`): 46 confirmaciones en el alcance, 30 con líneas agregadas, 0 hallazgos. Resumen verificable en [`calidad/evidencia/`](../../calidad/evidencia/gitleaks-8.30.1-resumen.json). **Automático en CI:** el trabajo `secretos` de `ci.yml` lo ejecuta en cada push y pull request (§3.4). Detalle en §3 | **CUMPLIDO** (ejecución local verificada; el trabajo de CI está implementado y **pasó en GitHub**: ejecución 43557153021 de `ci.yml` sobre `4242ea5`: éxito en `calidad`, `auditoria-dependencias`, `bloqueo-tablero` y `secretos`) |
| UUID de `tests/test_base.py` | Valor de relleno (cada grupo repite un solo dígito), usado solo para probar el enmascarado; **no coincide** con el token local; `gitleaks` no lo marca | **Sintético** (§3.3) |
| Búsqueda manual de patrones de secretos (complementaria) | 42 confirmaciones, 60,407 líneas agregadas, 10 patrones: 0 secretos reales; 3 coincidencias en pruebas, valores sintéticos | Evidencia complementaria |
| `pip-audit` | «No known vulnerabilities found» en `requirements.txt`, `requirements-lab.txt`, `requirements-dev.txt` y `tablero/requirements.txt`, este último **con sus dependencias transitivas** (§5). Automático en el trabajo `auditoria-dependencias` de `ci.yml` | **CUMPLIDO** (foto de hoy; el CI ampliado pasó en GitHub: ejecución 43557153021 de `ci.yml` sobre `4242ea5`: éxito en `calidad`, `auditoria-dependencias`, `bloqueo-tablero` y `secretos`) |
| Mínimo permiso en los flujos | `ci.yml`: solo lectura; captura: escritura de contenido y el secreto solo en un paso | **CUMPLIDO** (riesgos residuales en §4) |
| Secretos y variables de entorno | El token vive en un secreto de GitHub; ningún valor versionado | **CUMPLIDO** |
| Archivos ignorados por Git | Los nombres sensibles típicos están ignorados (comprobado con `git check-ignore`) | **CUMPLIDO** |
| Respaldo del bronce probado | Restauración desde un clon nuevo (2026-11-13, manual) **y** copia adicional con manifiesto SHA-256 y restauración automatizada en un directorio temporal (2026-11-14): 28 archivos, 3,345,350 bytes (§6) | **CUMPLIDO** (la copia está en el mismo equipo: no es independiente) |
| Dependencias del tablero con hashes | `tablero/requirements.lock.txt`: 34 paquetes y 946 hashes SHA-256; se instala con `--require-hashes` sin conflictos y `pip-audit` no halla vulnerabilidades (§5) | **CUMPLIDO** (local y GitHub: ejecución 43557153021 de `ci.yml` sobre `4242ea5`: éxito en `calidad`, `auditoria-dependencias`, `bloqueo-tablero` y `secretos`) |
| Acciones de GitHub fijadas por SHA | `actions/checkout`, `setup-python` y `upload-artifact` fijadas por commit verificado en `ci.yml` y `captura-diaria.yml` (§4) | **CUMPLIDO** (local y GitHub: ejecución 43557153021 de `ci.yml` sobre `4242ea5`: éxito en `calidad`, `auditoria-dependencias`, `bloqueo-tablero` y `secretos`) |

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
**Las ejecuciones de esta sección son locales y manuales.** El trabajo `secretos` de CI (§3.4) las repite de forma automática en cada push y pull request.

**Reproducción versionada (2026-11-13, 19:24 UTC).** Se repitió el escaneo con el mismo binario y se conservó una evidencia **sin secretos ni rutas privadas** en [`calidad/evidencia/`](../../calidad/evidencia/):
| Archivo | Contenido |
|---|---|
| [`gitleaks-8.30.1-resumen.json`](../../calidad/evidencia/gitleaks-8.30.1-resumen.json) | Versión, origen y *hash* del binario (el SHA-256 del zip coincide con `checksums.txt`), fecha, reglas, comandos con rutas genéricas, alcance, resultado, lo no escaneado, limitaciones y cómo reproducir |
| `gitleaks-8.30.1-reporte-historial_de_main.json` y `…-reporte-todas_las_referencias.json` | Los reportes de `gitleaks` (`[]`: sin hallazgos), con su SHA-256 anotado en el resumen |
| Escaneo | Alcance | Confirmaciones en el alcance / escaneadas | Resultado |
|---|---|---|---|
| `historial_de_main` | Historia alcanzable desde `c7302f8a8265be3a7c4fdd02a896d3af4220bfb9` (reproducible por cualquiera con el mismo binario) | 46 / 30 | **0 hallazgos**, salida 0 |
| `todas_las_referencias` | `--all`: todas las ramas visibles ese día, incluidas las de B aún sin integrar | 47 / 31 | **0 hallazgos**, salida 0 |
La diferencia entre las confirmaciones del alcance y las escaneadas son las fusiones y las confirmaciones que no agregan líneas. El primer escaneo de §3.2 (42 / 28, antes de integrar los PR #11 y #12) y este dan el mismo resultado. Una prueba (`tests/test_evidencia_gitleaks.py`) comprueba que el resumen sea coherente con los reportes y que no contenga rutas privadas, nombres ni correos. **Antes de la etiqueta `e1` hay que repetir el escaneo sobre el commit a etiquetar** (los archivos de esta evidencia se regeneran con el mismo procedimiento).

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

### 3.4 Integración en CI
El trabajo **`secretos`** de [`ci.yml`](../../.github/workflows/ci.yml) ejecuta `gitleaks` en cada push y pull request:
```yaml
secretos:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
      with: { fetch-depth: 0 }          # historial completo; con el valor por defecto (1) no se revisaría el pasado
    - name: Instalar gitleaks 8.30.1 (binario fijado y verificado)
      run: |
        curl -sSfL -o gitleaks.tgz "https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz"
        echo "551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb  gitleaks.tgz" | sha256sum -c -
        tar xzf gitleaks.tgz gitleaks
    - run: ./gitleaks git . --log-opts="--all" --redact --no-banner --exit-code 1
```
| Punto | Verificación |
|---|---|
| Versión y *hash* | v8.30.1; `551f6fc8…70eb` para `gitleaks_8.30.1_linux_x64.tar.gz`. **Coinciden tres valores:** el de `gitleaks_8.30.1_checksums.txt` de la release, el *digest* que calcula GitHub para ese archivo y el calculado al descargarlo (2026-11-13). Una prueba (`tests/test_ci_workflow.py`) exige que el *hash* de `ci.yml` aparezca en este documento |
| Sin terceros | Solo acciones oficiales de GitHub (`actions/checkout`); sin `gitleaks-action` y sin licencias ni tokens adicionales; permisos `contents: read` |
| Historial completo | `fetch-depth: 0` y `--log-opts="--all"`: las mismas opciones del escaneo local; `--redact` evita imprimir valores en el registro |
| Un hallazgo rompe el CI | Sale con código 1; el paso no tiene `continue-on-error` (una prueba lo comprueba) |
| **Control positivo (local)** | En un repositorio temporal con un *token* sintético con formato `ghp_…` (generado al vuelo, no versionado), el mismo comando con el binario de Windows 8.30.1 detectó 1 hallazgo, salió con código 1 y no imprimió el valor |
| Sin hallazgos en este repositorio | El mismo comando sobre este repositorio (35 confirmaciones): `no leaks found`, salida 0 |
| Trabajo aparte | Como `auditoria-dependencias`, para que un aviso nuevo no oculte el resultado de las pruebas |
**Verificación en GitHub:** el trabajo `secretos` **se ejecutó en GitHub Actions** (Linux) y terminó en éxito en las ejecuciones 43557153021 (`4242ea5`), 43557547843 y 43557683882 (`7f8f315`), 43557697492 (`main`, `628136b`) y 43558845112 (`372a6ab`). **Límite:** el control positivo (el *token* sintético detectado) se hizo solo en local con el binario de Windows; en GitHub se comprobó que el trabajo pasa sin hallazgos, no que detecte un secreto en ese entorno. Si marcara un falso positivo, se resolvería con `.gitleaksignore` por huella y un comentario que explique por qué es sintético, no silenciando una regla.

## 4. Permisos de los flujos de trabajo
| Flujo | Permisos | Disparadores | Secretos | Revisión |
|---|---|---|---|---|
| `ci.yml` | `contents: read` (solo lectura) | `push` y `pull_request` | Ninguno (`tests/test_ci_workflow.py` lo comprueba) | Sin `pull_request_target`, de modo que un PR de un fork no ve secretos |
| `captura-diaria.yml` | `contents: write` | `schedule` y `workflow_dispatch` | `INEGI_TOKEN`, solo en el paso de captura | El permiso de escritura es **necesario** (el bot guarda la bitácora y el bronce); es el mínimo para ese trabajo. Las entradas del usuario (`inputs.forzar`) y `GITHUB_REF_NAME` llegan al *shell* por variables de entorno, no interpoladas en el comando (sin inyección de comandos) |
**Riesgos residuales (abiertos):**
1. **Acciones fijadas por SHA de commit (corregido el 2026-11-14).** Antes se fijaban por etiqueta (`@v4`, `@v5`), que puede moverse. Ahora: `actions/checkout@11d5960a…` (v4.4.0), `actions/setup-python@a26af69b…` (v5.6.0) y `actions/upload-artifact@ea165f8d…` (v4.6.2). Cada SHA se verificó por dos vías: `git ls-remote` sobre el repositorio de la acción y la API de GitHub (commit existente, con firma verificada). Una prueba ([`tests/test_ci_workflow.py`](../../tests/test_ci_workflow.py)) exige SHA de 40 caracteres, versión en el comentario y solo acciones oficiales de GitHub. **Límite:** fijar por SHA impide que la etiqueta se mueva, pero no actualiza la acción; hay que revisar versiones nuevas a mano.
2. **Rama `main` sin protección (verificado).** La API pública de GitHub devuelve para `main` `protected: false` y ninguna regla ni *ruleset* activo (consulta del 2026-11-13, 19:14 UTC): **no hay protección configurada**. Los PR #7 a #16 se fusionaron sin revisiones. Activarla (revisión obligatoria y CI en verde) **no está implementada** y requiere permisos de administración; con `main` protegida habría que dar una excepción al bot de captura (riesgo R2 de [`riesgos.md`](../../calidad/riesgos.md)).
3. **Dependencias sin `--require-hashes` (parcialmente corregido).** El tablero ya tiene su archivo de bloqueo con hashes (§5). **Siguen sin hashes** `requirements.txt`, `requirements-lab.txt` y `requirements-dev.txt` (versiones fijadas con `==`, pero un paquete reemplazado en el índice con el mismo número de versión no se detectaría).
4. **`persist-credentials` (corregido el 2026-11-14 en `ci.yml`).** Los cuatro `checkout` de `ci.yml` usan `persist-credentials: false`: el flujo solo lee y no deja el token en `.git/config`. `captura-diaria.yml` lo conserva porque el bot necesita empujar (permiso `contents: write`, el mínimo para ese trabajo; un solo secreto, `INEGI_TOKEN`, en un solo paso).

5. **Contenedor de desarrollo (`.devcontainer/devcontainer.json`, agregado en `f8811ac`) revisado el 2026-11-13.** La versión original usaba una imagen de Python 3.11, hacía `apt upgrade`, instalaba `streamlit` **sin versión** y arrancaba el servidor con `--server.enableCORS false --server.enableXsrfProtection false` (desactiva dos protecciones de Streamlit sin una justificación técnica documentada: es la plantilla genérica de Codespaces). **Se cambió** a la imagen de Python 3.13 (`1-3.13-bookworm`, como el resto del proyecto), a instalar solo desde `tablero/requirements.lock.txt` con `--require-hashes` y a arrancar `streamlit run tablero/streamlit_app.py` con las protecciones por defecto (habilitadas). **No se probó dentro de un Codespace**: si la vista previa fallara por el proxy, se debe documentar la causa antes de desactivar cualquiera de las dos protecciones. Cuatro pruebas lo comprueban ([`tests/test_devcontainer.py`](../../tests/test_devcontainer.py)). La imagen base se fija por etiqueta de versión (`1-3.13-bookworm`), **no por *digest***.

## 5. Dependencias (`pip-audit`)
- **Herramienta:** `pip-audit 2.10.1`, fijada en `requirements-dev.txt` y usada en el trabajo `auditoria-dependencias` de `ci.yml`.
- **Resultado local del 2026-11-13** (`python -m pip_audit -r <archivo> --no-deps --disable-pip`): **«No known vulnerabilities found»** para `requirements.txt` (28 paquetes), `requirements-lab.txt` (14) y `requirements-dev.txt` (20). Esas listas ya son un *freeze* con su cierre transitivo.
- **El tablero y sus dependencias transitivas.** [`tablero/requirements.txt`](../../tablero/requirements.txt) fija solo **4 dependencias directas** (`streamlit`, `altair`, `pandas`, `numpy`); las demás las resuelve `pip` (también Streamlit Community Cloud al desplegar). Con `--no-deps` solo se auditarían esas 4, así que el trabajo de CI **resuelve y audita el cierre completo** (`python -m pip_audit -r tablero/requirements.txt`, sin `--no-deps`). Resultado local del 2026-11-13: **«No known vulnerabilities found»**, tanto con la resolución como al auditar el *freeze* de **34 paquetes** de un entorno nuevo con solo ese archivo, que se conserva en [`calidad/evidencia/tablero-cierre-transitivo-2026-11-13.txt`](../../calidad/evidencia/tablero-cierre-transitivo-2026-11-13.txt). **Límite:** audita lo que `pip` resuelve el día de la ejecución, que puede no ser lo que Streamlit Cloud instale otro día; fijar el cierre completo en un archivo de bloqueo (idealmente con *hashes*) lo eliminaría y no está implementado.
- **Archivo de bloqueo con hashes del tablero (2026-11-14).** [`tablero/requirements.lock.txt`](../../tablero/requirements.lock.txt) fija el cierre transitivo exacto (los mismos 34 paquetes en Windows y en Linux, comprobado con la resolución de `pip` para cada plataforma) con **946 hashes SHA-256**, los publicados por PyPI para cada versión. Se generó con [`pipeline/bloqueo.py`](../../pipeline/bloqueo.py) a partir de `pip freeze` de un entorno nuevo con solo `tablero/requirements.txt`. Comprobaciones: (1) `pip install --require-hashes -r tablero/requirements.lock.txt` en un entorno limpio instaló los 34 paquetes sin conflictos (`pip check` y las cuatro importaciones principales correctas); (2) `pip-audit -r tablero/requirements.lock.txt --require-hashes --disable-pip` dio «No known vulnerabilities found»; (3) [`tests/test_bloqueo_tablero.py`](../../tests/test_bloqueo_tablero.py) (8 pruebas, sin red) comprueba la estructura, que cada directa esté con su versión exacta y que el bloqueo coincida con el cierre versionado en [`calidad/evidencia/`](../../calidad/evidencia/tablero-cierre-transitivo-2026-11-13.txt); y (4) el trabajo `bloqueo-tablero` de `ci.yml` repite la instalación con hashes en Linux (**verificado en GitHub (ejecución 43557153021 de `ci.yml` sobre `4242ea5`: éxito en `calidad`, `auditoria-dependencias`, `bloqueo-tablero` y `secretos`)**). **Límites:** los hashes prueban que el archivo no cambió desde que se generó el bloqueo, no que el paquete sea benigno; **Streamlit Community Cloud sigue instalando desde `tablero/requirements.txt`** (4 directas), no desde el bloqueo; y el bloqueo hay que regenerarlo cuando cambie una versión.
- **Alcance y límites generales:** audita las versiones contra la base de vulnerabilidades en la fecha de la consulta; una vulnerabilidad publicada mañana no aparece hoy. Va en un trabajo aparte para que un aviso nuevo no bloquee todos los push; la rúbrica pide **cerrar** los hallazgos, así que cualquier aviso futuro exige actualizar la dependencia o documentar una excepción.

## 6. Respaldo y restauración de la capa bronce
### 6.1 Qué respaldo existía y si servía para recuperar lo crudo
- **Existentes al 2026-11-13:** (a) el repositorio de GitHub (el bronce está versionado: los 28 archivos de `data/bronce/` están en Git) y (b) la copia local de trabajo. No había una copia con manifiesto ni una restauración automatizada.
- **¿Permite recuperar el dato crudo?** Sí, mientras el repositorio exista: la prueba manual del 2026-11-13 restauró desde un clon nuevo 24 archivos (hoy son 28: el bot agrega capturas) con integridad, histórico y privacidad satisfactorios, y el SHA-256 de `Base70centros.csv` del clon coincide con el local. **Límites:** era una prueba manual y puntual, dependía de una sola cuenta y de un solo proveedor, y no había forma de comprobar que lo recuperado fuera **exactamente** lo capturado sin recurrir a las fichas `.meta.json` que viajan en el mismo repositorio.

### 6.2 Copia adicional con manifiesto y restauración probada (2026-11-14)
Código: [`pipeline/respaldo.py`](../../pipeline/respaldo.py) (biblioteca estándar). Pruebas: [`tests/test_respaldo_bronce.py`](../../tests/test_respaldo_bronce.py) (15).
| Comando | Qué hace |
|---|---|
| `python -m pipeline.respaldo crear --destino <carpeta>` | Escribe `<nombre>.zip` (determinista: fechas fijas y orden alfabético) y `<nombre>.manifiesto.json` con ruta, tamaño y SHA-256 de cada archivo y el SHA-256 del zip. No sobrescribe un respaldo existente y no escribe dentro de `data/bronce/` |
| `python -m pipeline.respaldo verificar --zip … --manifiesto …` | Comprueba el hash del zip, que estén **exactamente** los archivos del manifiesto y el hash de cada uno |
| `python -m pipeline.respaldo restaurar --zip … --manifiesto … --destino <carpeta vacía>` | Verifica y extrae; se niega a restaurar sobre una carpeta con archivos o dentro del bronce, y rechaza rutas que salgan de la carpeta (*zip-slip*); luego recalcula cada hash |
| `python -m pipeline.respaldo probar` | Crea, verifica y restaura en un **directorio temporal** y compara lo restaurado con el manifiesto y con el bronce |
**Resultado real (2026-11-14):**
- Se creó la copia en `Documents\Proyectos\respaldo_bronce_20261114\` (fuera del repositorio): `bronce-20261114.zip` y `bronce-20261114.manifiesto.json`; **28 archivos, 3,345,350 bytes**.
- `verificar`: 28 archivos, 0 fallos. `restaurar` en una carpeta temporal: 28 restaurados, 0 fallos, y la carpeta se eliminó después. `probar`: restauración idéntica al manifiesto y **el bronce original sin un solo byte de cambio** (la prueba lo comprueba con los hashes antes y después).
- El manifiesto se versionó en [`calidad/evidencia/bronce-manifiesto-20261114.json`](../../calidad/evidencia/bronce-manifiesto-20261114.json) (sin rutas privadas ni correos). Como el bronce solo crece, una prueba comprueba que **todo lo declarado conserva su SHA-256** aunque el bot agregue capturas.
- Se probaron las fallas: un zip alterado, un hash del manifiesto distinto, un archivo faltante o de más, un destino con archivos, un destino dentro del bronce y un zip con ruta peligrosa; todas se detectan o se rechazan.
**Cómo copiarla a un almacenamiento independiente.** Copiar los **dos archivos** de `C:\Users\Leslie Valadez\Documents\Proyectos\respaldo_bronce_20261114\` (`bronce-20261114.zip` y `bronce-20261114.manifiesto.json`) a otro disco o proveedor y, **en el destino**, comprobarlos con `python -m pipeline.respaldo verificar --zip <zip> --manifiesto <manifiesto>` o comparando el SHA-256 del zip con el campo `zip.sha256` del manifiesto (`725b499c5d16c062e273666b07d06b314cedebc670e2f4446b80e5e03a6127b2`). El manifiesto también está versionado en `calidad/evidencia/bronce-manifiesto-20261114.json`.
**Límites:** la copia está **en el mismo equipo** que el repositorio local; no es independiente. Para serlo hay que copiar el zip y el manifiesto a otro disco o proveedor (y el manifiesto versionado permite comprobar cualquier copia). No se probó restaurar el estado de un día anterior más allá de lo que contenga el zip, ni se automatizó la copia periódica.

## 7. Limitaciones y acciones abiertas
La verificación en GitHub de `secretos`, de la auditoría ampliada, de `bloqueo-tablero` y de los SHA de las acciones **ya se hizo** (ejecución 43557153021 del commit `4242ea5` y las posteriores; véase §3 y §5). Lo que sigue abierto:
1. **Protección de `main`: preparada, no activada** (hoy `protected: false`; activarla requiere permisos de administración de la propietaria). Desde el 2026-11-14 existe [`.github/rulesets/proteger-main.json`](../../.github/rulesets/proteger-main.json): PR obligatorio con 1 aprobación y revisión del propietario del código, los cuatro trabajos de CI como comprobaciones obligatorias (`calidad`, `auditoria-dependencias`, `bloqueo-tablero`, `secretos`), bloqueo de *force push* y de borrado de la rama. **Compatibilidad con la captura diaria:** `captura-diaria.yml` empuja a `main` con `GITHUB_TOKEN`; con «Require a pull request» ese empuje **se rechazaría** y la captura dejaría de guardar su bronce, por eso el archivo incluye una excepción para la aplicación GitHub Actions (`actor_id` 15368) y se entrega con `enforcement: "disabled"` (importarlo no bloquea nada; el modo de evaluación solo existe en planes Enterprise). La prueba [`test_ruleset_main.py`](../../tests/test_ruleset_main.py) comprueba que los cuatro trabajos exigidos existen en `ci.yml` y que el empuje de la captura es el descrito. **No se verificó** que GitHub acepte esa excepción para ese actor en un repositorio personal. Pasos (propietaria): (1) *Settings → Rules → Rulesets → New ruleset → Import a ruleset*, y elegir ese archivo; (2) revisar que el objetivo sea la rama predeterminada y que la lista de *bypass* muestre «GitHub Actions» (si no, agregarla); (3) cambiar *Enforcement status* a **Active**; (4) *Actions → captura-diaria → Run workflow* y confirmar que «Guardar bitácora…» termina en verde con un commit `captura DENUE …` en `main`; **si falla con «protected branch», volver a Disabled** y no activarla hasta resolverlo (alternativa: que la captura empuje a una rama aparte y se fusione por PR); (5) probar con un PR de prueba que *Merge* queda bloqueado sin aprobación ni CI en verde. **Plan B si el paso 4 falla** (GitHub puede no ofrecer «GitHub Actions» en la lista de *bypass* de un repositorio personal; no está comprobado): (a) crear un *fine-grained personal access token* de la propietaria, limitado a este repositorio con permiso *Contents: Read and write*, y guardarlo como secreto `CAPTURA_TOKEN`; (b) en `captura-diaria.yml` usar ese token en el `checkout` (campo `token:`) para que el empuje lo haga la propietaria; (c) en el ruleset, en *Bypass list*, agregar el rol **Repository admin** con modo *Always*; (d) repetir el paso 4. Es el cambio más pequeño (un secreto y una línea del flujo), pero la excepción pasa a ser la propietaria y no el bot, y el token caduca (hay que renovarlo). **No debe declararse cumplido el requisito de protección hasta completar los pasos 3 a 5 con la regla activa.**
**Límite:** sin organización, la propietaria puede añadirse al *bypass*; la regla protege contra descuidos (los PR #7 a #18), no contra mala fe.
2. **Hashes para `requirements.txt`, `requirements-lab.txt` y `requirements-dev.txt`** (hoy solo el tablero los tiene) y una política para que Streamlit Cloud use el bloqueo.
3. **Copia del bronce fuera del equipo: no existe** (la de §6.2 está en el mismo disco). Para que lo sea: copiar el `.zip` y el `.manifiesto.json` (generados con `python -m pipeline.respaldo crear --destino <carpeta>`) a un medio fuera de este equipo y de GitHub, anotar fecha y lugar, comprobarlos allí con `python -m pipeline.respaldo verificar --zip … --manifiesto …` y restaurar en una carpeta vacía con `restaurar`. **Hasta que la propietaria lo confirme, el proyecto no declara copia externa;** la copia periódica tampoco está automatizada.
4. Opcional: reemplazar el UUID sintético de `tests/test_base.py` por un texto evidentemente falso (§3.3).
