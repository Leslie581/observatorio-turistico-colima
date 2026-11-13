# DENUE (INEGI): fuente programada

Corte: 2026-11-09. Origen: **[V]** leído hoy en la página citada · **[P]** evidencia del prototipo.

## Qué es y cómo se accede
- **Directorio Estadístico Nacional de Unidades Económicas**, API REST con token gratuito: `https://www.inegi.org.mx/app/api/denue/v1/consulta/…` [V] https://www.inegi.org.mx/servicios/api_denue.html describe la API como una vía para "crear aplicaciones que muestren la información directamente de las bases de datos del INEGI".
- Consulta usada: subsector SCIAN 721 (alojamiento temporal), Colima (06), Manzanillo (007). Métodos `Cuantificar` (total esperado) y `BuscarAreaAct` (registros, paginados de 1000).
- Formato: JSON (lista de objetos). Estructura (campos de la API): CLEE, Id, Nombre, Clase_actividad, Estrato, domicilio, coordenadas, claves SCIAN, AGEB, manzana, Fecha_Alta (y los campos personales de la sección siguiente).
- Frecuencia: la API se consulta **una vez al día**; el directorio en sí se actualiza con menor frecuencia (no verificado: la periodicidad de actualización de INEGI no está documentada en lo que revisamos). Las capturas diarias idénticas se conservan porque forman la bitácora de capturas; el contenido repetido se detecta por SHA-256 en la ficha.
- Autenticación: `INEGI_TOKEN` (secreto). El token va en la URL de la API; el código lo enmascara en bitácoras y fichas (`***TOKEN***`).

## Términos de uso
[V] https://www.inegi.org.mx/inegi/terminos.html — "Términos de Libre Uso de la Información del INEGI": permiten copiar, distribuir, difundir, adaptar, extraer y explotar comercialmente la información, **con crédito**: "Fuente: INEGI, [producto]" y fecha de actualización, y avisando que los análisis propios no son del INEGI.
- Atribución que usa este repositorio: *Fuente: INEGI, Directorio Estadístico Nacional de Unidades Económicas (DENUE), API de consulta; captura del equipo en la fecha indicada en cada ficha.*
- `robots.txt` de `www.inegi.org.mx`: el extractor lo lee en cada ejecución y bloquea si no lo puede verificar (no se reprodujo su contenido en este documento: **PENDIENTE** archivarlo como evidencia en la primera ejecución real; queda en `logs/bitacora.jsonl` como evento `robots_leido`).
- Límites de cuota: **no documentados** en lo que revisamos. El extractor hace como máximo 2–3 solicitudes por ejecución, con pausa ≥ 1.5 s.

## Datos personales y minimización
Campos reales de `BuscarAreaAct` (revisados sobre los 134 registros del prototipo, solo lectura) y decisión aplicada en `denue.sanitizar_crudo` **antes** de escribir en bronce:

| Campos | Decisión | Justificación |
|---|---|---|
| `Telefono`, `Correo_e`, `Sitio_internet` (29, 71 y 38 de 134 registros con valor en el prototipo) | **Excluir** | Contacto; puede ser personal |
| `Razon_social` | **Excluir** | Puede ser el nombre de una persona física (se observó al menos un caso) |
| `Nombre` | **Excluir** (decisión del equipo, 2026-11-09) | Nombre comercial; en micronegocios puede ser el de una persona (p. ej. “BUNGALOWS EL REFUGIO DE NAYO AYALA” en la muestra del prototipo) y no se detecta automáticamente. La trazabilidad la dan `CLEE` e `Id` |
| `Calle`, `Num_Exterior`, `Num_Interior`, `EDIFICIO`, `EDIFICIO_PISO`, `numero_local` | **Excluir** (minimización) | La ubicación para el análisis la dan coordenadas, AGEB, manzana, colonia y CP; en micronegocios (63 de 134 tienen 0 a 5 personas) el domicilio puede ser una vivienda |
| `CLEE`, `Id`, `Clase_actividad`, `CLASE_ACTIVIDAD_ID` y claves SCIAN, `Estrato` | Conservar | Identifican y clasifican el establecimiento; necesarios para conteos y oferta |
| `Longitud`, `Latitud`, `AGEB`, `Manzana`, `Colonia`, `CP`, `Ubicacion`, `AreaGeo`, `Tipo_Asentamiento`, `tipo_corredor_industrial`, `nom_corredor_industrial` | Conservar | Unión espacial y mapa de E2; información pública del directorio |
| `Tipo`, `Fecha_Alta` | Conservar | Tipo de establecimiento y antigüedad |

**Riesgo residual:** las coordenadas, junto con AGEB, manzana y clase, siguen ubicando con precisión un establecimiento; se conservan porque son el insumo del análisis geoespacial y el INEGI las publica. Sin `Nombre`, un establecimiento se identifica por `CLEE`/`Id` (el nombre se puede consultar en el DENUE público si algún análisis lo necesita; no se redistribuye aquí).

El bronce del DENUE **no es byte a byte la respuesta de la API**: es la respuesta menos los campos excluidos. La ficha guarda `sha256_respuesta_original`, `campos_personales_eliminados` (incluye `Nombre`) y `campos_domicilio_eliminados`. Los crudos del prototipo (`data/bronce/denue/crudo/`) **no se migraron**.

**Cómo leer las verificaciones.** Una prueba con datos simulados demuestra el comportamiento del código en esos casos; una captura real comprueba el resultado sobre datos auténticos; y `pipeline.verificar_e0 --solo privacidad` sobre **cero** archivos devuelve `sin_datos`, que **no** demuestra nada sobre datos reales. Al 2026-11-10 hay 4 archivos DENUE reales publicados por el bot y la privacidad es satisfactoria sobre ellos.

## Estado
| Elemento | Estado |
|---|---|
| Cliente DENUE y controles (7) | Migrado del prototipo, 134/134 con token real en Windows [P] |
| Sanitización previa al bronce, captura diaria idempotente, bitácora de ejecuciones | **IMPLEMENTADO**, probado con respuestas simuladas |
| Corridas reales | **VERIFICADO**: capturas manuales en GitHub Actions (134 de 134) y una local |
| Corrida programada (`schedule`) en GitHub Actions | **VERIFICADO**: 3 ejecuciones exitosas del 10 al 12 de noviembre (ver `docs/E0/verificacion.md`) |
