# DATATUR (SECTUR): permisos, procedencia y estado del histórico

Corte: 2026-11-09. Este documento separa **lo confirmado**, **las restricciones expresas** y **lo no aclarado**, y cita el origen de cada afirmación.
Origen: **[V]** leído hoy por nosotros en la página pública indicada · **[P]** evidencia del prototipo (carpeta `staymetrics-prototipo`, de solo lectura) · **[H]** hash calculado hoy sobre archivos reales.
No se contactó a ninguna institución ni se solicitó autorización.

## 1. Tres canales distintos (no confundirlos)

| Canal | Qué es | Método | Datos | Estado de uso |
|---|---|---|---|---|
| **A. Base70centros.csv** (datos.gob.mx → `repodatos.atdt.gob.mx`) | Conjunto de datos abiertos de SECTUR, 64 centros, mensual 2016-01 a 2024-12 | Descarga por enlace "Descargar" del portal | 2,740,171 bytes | **Licencia CC BY 4.0 declarada** → redistribución con atribución |
| **B. Sistema de Monitoreo Hotelero** (`monitoreohotelero.sectur.gob.mx`) | Generador interactivo de reportes; el prototipo lo automatizó con `POST /Reportes/Ajax.aspx` | Endpoint **interno**, no API pública | Manzanillo 2022-01 a 2026-09, 21 indicadores | **Automatización y publicación NO autorizadas / sin aclarar** |
| **C. Reportes mensuales PDF/ZIP** (`datatur.sectur.gob.mx/Documentoscompartidos/monitoreo/`) | Acumulados enero-mes | GET de archivos | No se descargó ninguno en el repositorio definitivo | **Sin analizar a fondo** (ver 4) |

## 2. Lo confirmado

| # | Afirmación | Origen |
|---|---|---|
| C1 | La ficha de Base70 en datos.gob.mx declara administrador SECTUR y licencia **Creative Commons Attribution 4.0**, creada 14-mar-2025, última actualización 28-may-2025, con el aviso "Algunas bases de datos pueden incluir actualizaciones retroactivas". | [V] https://www.datos.gob.mx/dataset/ocupacion_hotelera_70_destinos_principales_monitoreados_datatur (2026-11-09) |
| C2 | `Base70centros.csv` oficial, descargado con un navegador, pesa 2,740,171 bytes, `Last-Modified: 15-jul-2025`, SHA-256 `a8ca3f9b…d671`, **idéntico** al archivo de `data/bronce/datatur/`. | [H] `docs/fuentes/evidencias/verificacion_base70_20261109_B.json` (hoy) y [P] `evidencias/datatur_oficial/verificacion_navegador_20261109T015542Z.json` (ayer) |
| C3 | Manzanillo tiene **108 meses** (2016-01 a 2024-12), sin huecos, en el bronce. | [H] `python -m pipeline.verificar_e0 --solo historico` |
| C4 | El Sistema de Monitoreo no publica `robots.txt` (HTTP 404). | [P] `robots_monitoreohotelero_20261109.json` y `01_robots.raw` (404) |
| C5 | El acceso del prototipo a (B) funcionó: 4 solicitudes HTTP 200 y un CSV reconstruido **idéntico byte a byte** (SHA-256 `93a28907…4063`) a la exportación manual del sitio. | [P] `diagnostico_monitoreo_20261109T044723Z`; [H] hashes recalculados hoy: coinciden |
| C6 | `www.datos.gob.mx/robots.txt` prohíbe `/api/` (Crawl-Delay 10); por eso no se usa la API CKAN del portal. | [P] `verificacion_navegador…json` |

## 3. Restricciones expresas

| # | Restricción | Origen |
|---|---|---|
| R1 | Términos del portal gob.mx: se autoriza a "visualizar y descargar los materiales … solamente para su uso personal y no para un uso comercial", y el usuario "no deberá modificar, reproducir o mostrar pública o comercialmente los materiales, ni podrá distribuir o utilizarlos con algún propósito público o comercial". | [V] https://www.gob.mx/terminos (2026-11-09) |
| R2 | `repodatos.atdt.gob.mx` responde **HTTP 403 "Access Denied"** (CDN) a scripts (`requests`, `curl.exe`) aunque el navegador recibe 200. El cuerpo de 443 bytes de esa respuesta es la página de error. **No se evade** (no se cambia el User-Agent ni se emula un navegador). | [P] `ejecucion_windows_20261109T021035Z/datatur_oficial/` |

## 4. Situaciones no aclaradas (incertidumbre registrada)

| # | Pregunta abierta | Por qué no se puede resolver con lo disponible |
|---|---|---|
| N1 | ¿Los términos de gob.mx (R1) aplican a `monitoreohotelero.sectur.gob.mx` y a su generador? | Es un subdominio .gob.mx, pero no localizamos términos propios del sistema. R1 restringe la difusión pública. |
| N2 | ¿Se permite automatizar `Ajax.aspx`? | Es un endpoint interno, sin documentación pública. HTTP 200 y ausencia de robots.txt **no son autorización**. R1 habla de uso personal; no menciona la automatización. |
| N3 | ¿Puede publicarse en un repositorio público el contenido del Sistema de Monitoreo (canal B)? | R1 lo restringe expresamente. Sin autorización escrita, no. |
| N4 | ¿Los reportes PDF/ZIP (canal C) pueden descargarse de forma automatizada y redistribuirse? | Mismos términos de gob.mx; no se revisó su robots.txt en este repositorio. No se usan. |
| N5 | ¿Base70 incluye cifras posteriores a 2024-12? | El archivo vigente termina en 2024-12 [H]. La serie 2025-2026 solo existe en el canal B (y C). |
| N6 | ¿El canal de adquisición del bronce (copia de terceros en GitHub) afecta la licencia? | No: la licencia es del contenido, y el hash demuestra que el contenido es el oficial. Pero la ficha del bronce conserva `origen: espejo_no_oficial` porque describe el canal real. |

**Nota de método.** Integridad de contenido (hash) ≠ autorización. En Base70 la autorización viene de la licencia CC BY 4.0 (C1), no del hash.

## 5. Decisión aplicada en este repositorio

| Dato | ¿En el repositorio público? | Justificación |
|---|---|---|
| `data/bronce/datatur/Base70centros.csv` + ficha (108 meses de Manzanillo, 64 centros) | **Sí**, sin modificar, con atribución en `data/bronce/datatur/LEEME.md` | CC BY 4.0 (C1) + hash idéntico al oficial (C2) |
| Salida del Sistema de Monitoreo (HTML, CSV, exportación manual, diagnósticos `.raw`, capa validada derivada) | **No** (`.gitignore`). Solo se publican **metadatos y hashes** (sección 6) | R1, N1–N3 |
| Fixtures de pruebas con respuestas reales del generador | **No migrados** | Mismo motivo |
| Código `extractores/monitoreo.py` y sus 21 pruebas | **No migrados todavía** (ver `docs/E0/migracion.md`) | No se activa ni se deja listo para activar sin decisión del equipo |
| Captura periódica de DATATUR en GitHub Actions | **No existe** | N2 |

### Requisito de histórico (≥ 36 periodos en bronce)
**Satisfecho con Base70** (108 meses, 2016-01 a 2024-12), pues se publica el archivo completo. No depende del canal B. Limitación: la serie termina en 2024-12; cualquier extensión a 2025-2026 requiere resolver N1–N4.
Quiebres que ya conoce el equipo: cambio de marco en 2017 y COVID 2020-03 a 2021-06 [P] `docs/cobertura_historica.md` del prototipo (no re-verificado hoy salvo C3).

## 6. Metadatos y hashes del material no publicado (canal B)

Los archivos siguen en la carpeta del prototipo (solo lectura) y deben conservarse fuera del repositorio público (copia local del equipo).

| Archivo (prototipo) | Bytes | SHA-256 | Procedimiento de adquisición |
|---|---:|---|---|
| `DataturReportePublico_original.csv` | 127,786 | `93a2890730def288ffe7efc9acea781e23a3492fa48896bcd24c72913ff84063` | Exportación **manual** desde el navegador, reporte 481, Manzanillo, 2022-2026, 21 indicadores, 9 categorías (UTF-16 LE sin BOM). Fecha exacta de exportación no registrada. |
| `data/bronce/datatur_monitoreo/reporte481_manzanillo_2022-2026.html` | 1,170,986 | `3ff8808385a1e2191136287ecd1ad3c9b02a252579526ac3d5693f688cc26e7d` | Respuesta de `POST /Reportes/Ajax.aspx` obtenida con Python (diagnóstico y extractor integrado, 2026-11-09). |
| `…_csv_sitio.csv` | 127,786 | `93a2890730def288ffe7efc9acea781e23a3492fa48896bcd24c72913ff84063` | CSV reconstruido con la regla del sitio; idéntico a la exportación manual (C5). |

**Cómo reobtenerlo (manual, uso personal):** abrir el Sistema de Monitoreo Hotelero → reporte 481 "Ocupación en hoteles y moteles por centro turístico, corte mensual" → centro Manzanillo, 2022-2026, 12 meses, 21 indicadores, 9 categorías → "Ver Reporte" → exportar CSV. Comparar el SHA-256 con la tabla anterior (puede cambiar si SECTUR revisa cifras).

## 7. Alternativas legales propuestas (requieren **su aprobación**)

| Opción | Qué implica | Pros | Contras |
|---|---|---|---|
| **1. Quedarse con Base70 (recomendada para E0–E3)** | Serie 2016-01 a 2024-12, licencia CC BY 4.0, ya cumple 36 periodos | Sin riesgo legal; reproducible | Termina en 2024-12; el pronóstico no cubre 2025-2026 |
| **2. Solicitar autorización escrita a SECTUR/DataTur** (la envía el equipo, no la IA) para automatizar y publicar el reporte 481 | Posibilita 2022-2026 y capturas periódicas | Resuelve N1–N3 | Puede no llegar a tiempo; hay que guardar la respuesta como evidencia |
| **3. Usar el canal B solo como verificación privada** (exportación manual, no publicada), publicando únicamente cifras agregadas con aval | Contrasta 2022-2024 con Base70 (360/360 conteos coinciden [P]) | Valor de calidad | R1 restringe "mostrar públicamente"; hay que acotar qué se publica |
| **4. Segunda fuente programada distinta de DATATUR** (DENUE, ya implementado; opcionalmente Open-Meteo como variable exógena tras revisar sus términos) | Cumple "captura diaria" sin tocar canal B | Términos claros (INEGI libre uso) | DENUE es un directorio que cambia poco (ver `docs/fuentes/denue.md`) |
