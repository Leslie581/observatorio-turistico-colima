# Tablero de E1 · Observatorio de Ocupación Hotelera de Colima (Manzanillo)

Rama `e1/eimy-tablero` · 2026-11-13 · Responsable: integrante B (Eimy Melissa Urbina Meza). **El nombre del observatorio es provisional.**
Aplicación: [`tablero/streamlit_app.py`](../../tablero/streamlit_app.py) (Streamlit y Altair). Pruebas: [`tests/test_tablero_cargador.py`](../../tests/test_tablero_cargador.py) y [`tests/test_tablero_app.py`](../../tests/test_tablero_app.py).

## 1. Estado
| Elemento | Estado |
|---|---|
| Aplicación (MVP) | **Implementada y probada en local** (arranque, lectura desde otro directorio, cifras y gráficas, vista de escritorio y de móvil) |
| Despliegue en Streamlit Community Cloud | **NO desplegado** a la fecha de este documento. Los pasos están en §7; lo debe iniciar una persona con su cuenta de GitHub |
| URL pública | **Ninguna todavía.** No se afirma que esté publicada hasta verificarla |

## 2. Qué muestra
Seis pestañas, completamente en español:
| Pestaña | Contenido |
|---|---|
| **Resumen** | Ocupación hotelera mensual 2016–2024 desde la capa oro, con el periodo de COVID y el año de prueba sombreados; cuatro indicadores |
| **Pronóstico 2024** | SARIMA elegido y su **intervalo de predicción del 95 %** frente a los valores reales de 2024 (comparación retrospectiva, entrenado solo con 2016–2023) |
| **Comparación de modelos** | SES, Holt, Holt-Winters, SARIMA y la **referencia ingenua estacional**: MAE, RMSE y MAPE, y las proyecciones de 2024 elegibles |
| **Proyección 2025** | Proyección con su intervalo del 95 %, **rotulada como proyección histórica calculada con datos hasta diciembre de 2024** |
| **Cómo leerlo** | Explicación sencilla del intervalo, de los resultados y de las limitaciones |
| **Fuentes y datos** | Fuente, licencia, cobertura temporal, fecha de generación de los resultados, entrenamiento y prueba, versiones |

**Cómo se presenta 2025.** El CSV del laboratorio rotula ese tramo como `proyeccion_futura`, rótulo correcto cuando se calculó. El tablero lo muestra como **«Proyección 2025 (calculada con datos hasta diciembre de 2024)»** y dice expresamente que **no es un pronóstico vigente** (aviso superior, aviso de la pestaña y texto explicativo): al generarse los resultados (noviembre de 2026), 2025 ya había transcurrido y la fuente usada no trae datos observados de 2025, por lo que **no se puede comparar con la realidad**. No se modificó ningún archivo de resultados.

**Honestidad sobre la referencia ingenua.** El SARIMA tiene menor RMSE que la referencia ingenua (2.64 frente a 2.75), pero **no menor MAE (2.38 frente a 2.20) ni MAPE (4.36 % frente a 4.01 %)**. El tablero lo dice así y aclara que, con 12 meses de prueba, no hay un ganador claro; el SARIMA se eligió entre los cuatro modelos obligatorios y la referencia no participa en esa elección (criterio del laboratorio, [`pronostico.md`](pronostico.md) §4).

## 3. Arquitectura
```
data/oro/manzanillo_ocupacion_mensual.csv (+ .meta.json) ─┐
laboratorio/pronosticos/resultados/*.csv, *.json ─────────┤  (solo lectura, versionados)
                                                          ▼
              tablero/cargador.py  ── valida y prepara ──► tablero/graficas.py ──► tablero/streamlit_app.py
              (pandas, numpy)                              (Altair)                 (Streamlit: interfaz y textos)
```
| Archivo | Función |
|---|---|
| [`tablero/cargador.py`](../../tablero/cargador.py) | Carga y **valida** los datos; calcula las métricas de coherencia y los textos para el cliente a partir de los datos. **No importa Streamlit** (solo pandas y numpy), por lo que se prueba en cualquier entorno |
| [`tablero/graficas.py`](../../tablero/graficas.py) | Las gráficas Altair (paleta apta para daltonismo, etiquetas en español, intervalo como franja `y`–`y2`) |
| [`tablero/streamlit_app.py`](../../tablero/streamlit_app.py) | La interfaz: pestañas, indicadores, textos y diseño responsivo |
| [`tablero/requirements.txt`](../../tablero/requirements.txt) | Dependencias **mínimas y fijadas**: `streamlit==1.67.0`, `altair==6.3.0`, `pandas==3.0.5`, `numpy==2.5.3` |
| [`.streamlit/config.toml`](../../.streamlit/config.toml) | Tema y sin telemetría de uso (`gatherUsageStats = false`) |

**Decisiones de diseño**
- **Solo lee archivos versionados.** No reentrena modelos, no ejecuta `pipeline`, no consulta red ni servicios externos, no usa tokens ni secretos, y no depende de rutas absolutas (la raíz se calcula desde la ubicación de `cargador.py`, así que funciona desde cualquier directorio).
- **No muestra datos de DENUE ni agregados de establecimientos.** No lee `data/bronce/`, `data/plata/` ni `manzanillo_oferta_hospedaje.csv`; una prueba lo comprueba. El agregado de oferta tiene celdas con un solo establecimiento (RNF-PRI-03 de [`requerimientos.md`](requerimientos.md)) y por eso queda fuera.
- **No calcula estadística nueva.** Las métricas, los intervalos y la referencia ingenua vienen del laboratorio; el tablero solo **recalcula, para validar,** que coincidan.
- **Falla de forma segura.** Si un archivo falta o una cifra no es coherente, la aplicación muestra un mensaje de error y **ninguna cifra**.

## 4. Fuentes de datos y cobertura
| Archivo leído | Contenido |
|---|---|
| `data/oro/manzanillo_ocupacion_mensual.csv` y su ficha `.meta.json` | Ocupación mensual de Manzanillo (hoteles de 2 a 5 estrellas, cociente de sumas), **108 meses, 2016-01 a 2024-12**; atribución y licencia |
| `laboratorio/pronosticos/resultados/comparacion_modelos_2024.csv` | MAE, RMSE y MAPE de los cuatro modelos en 2024 |
| `.../pronosticos_2024_por_modelo.csv` | Proyección retrospectiva de 2024 de cada modelo y de la referencia ingenua |
| `.../pronostico_modelo_elegido.csv` | SARIMA elegido: 2024 (retrospectiva) y 2025 (proyección), con intervalos del 95 % |
| `.../resumen.json` y `.../ejecucion.json` | Modelo elegido, referencia ingenua, partición, y fecha y versiones de generación |
**Fuente original:** DataTur, Secretaría de Turismo (SECTUR), *Ocupación hotelera en los 70 destinos principales monitoreados*, licencia **CC BY 4.0** (atribución mostrada en la pestaña «Fuentes y datos»). **Fecha de generación de los resultados:** la de `ejecucion.json` (13 de noviembre de 2026, 02:20 hora de la Ciudad de México; 08:20 UTC), no la de apertura del tablero.

## 5. Validaciones que hace el cargador
La carga lanza `ErrorDatos` (y el tablero no muestra cifras) si ocurre cualquiera de estas condiciones:
- Falta un archivo, una columna o una clave, o un JSON es inválido.
- La capa oro no tiene exactamente 108 meses consecutivos de 2016-01 a 2024-12, tiene periodos repetidos o ocupaciones fuera de 0 a 100.
- Falta un modelo, o un mes de 2024 en los pronósticos.
- Un intervalo de predicción no cumple **límite inferior ≤ media ≤ límite superior**.
- La proyección de 2025 trae valores observados.
- **Coherencia con el laboratorio y con la capa oro:** el valor observado de los pronósticos difiere del de la capa oro; el MAE, RMSE o MAPE recalculado desde los pronósticos difiere de la tabla del laboratorio (tolerancia 1e-4, los CSV redondean a 6 decimales); la cobertura del intervalo recalculada difiere de la del laboratorio; o la partición no es 2016-01 a 2023-12.

## 6. Ejecución local
Desde la raíz del repositorio, en PowerShell (Windows):
```powershell
python -m venv .venv-tablero
.\.venv-tablero\Scripts\python.exe -m pip install -r tablero/requirements.txt
.\.venv-tablero\Scripts\python.exe -m streamlit run tablero/streamlit_app.py
```
Se abre en `http://localhost:8501`. Funciona también desde otro directorio (`streamlit run <ruta>/tablero/streamlit_app.py`). Para las pruebas del tablero, instalar además `pytest` y ejecutar `python -m pytest tests/test_tablero_cargador.py tests/test_tablero_app.py`.

**Pruebas y alcance.** `test_tablero_cargador.py` (20 pruebas; solo pandas y numpy) corre en cualquier entorno, incluida la captura diaria. `test_tablero_app.py` (8 pruebas: estructura de las gráficas, intervalos y arranque con `streamlit.testing`) **se omite** si no están `altair` y `streamlit`; **el CI actual no los instala, así que ahí se omite** (el flujo de CI no se modificó). Sus resultados: ver §9.

## 7. Despliegue en Streamlit Community Cloud
**Esto no se ha hecho.** Requiere iniciar sesión y autorizar el acceso a GitHub, y eso lo debe hacer una persona con su propia cuenta.
1. Fusionar primero el pull request de esta rama a `main` (con la revisión recíproca) para desplegar desde `main`. Para una prueba previa se puede desplegar desde la rama `e1/eimy-tablero`.
2. Entrar a <https://share.streamlit.io> e **iniciar sesión con GitHub** (la cuenta debe tener acceso al repositorio `Leslie581/observatorio-turistico-colima`, que es público).
3. Pulsar **Create app** → **Deploy a public app from GitHub**. Si Streamlit pide **autorizar el acceso a GitHub** (instalar su aplicación de GitHub o dar permiso sobre el repositorio), aceptar solo para este repositorio. Si la cuenta no tiene permisos de escritura sobre el repositorio, lo hace la propietaria (`Leslie581`).
4. Completar el formulario: **Repository** `Leslie581/observatorio-turistico-colima`; **Branch** `main` (o `e1/eimy-tablero` para la prueba previa); **Main file path** `tablero/streamlit_app.py`.
5. Abrir **Advanced settings** y elegir **Python 3.13** (la versión con la que se probó). **No** agregar secretos: el tablero no los usa.
6. Elegir una **App URL** sencilla (por ejemplo, `observatorio-ocupacion-manzanillo`, si está disponible) y pulsar **Deploy**.
7. Esperar la instalación. En el registro debe verse que instala `streamlit==1.67.0`, `altair==6.3.0`, `pandas==3.0.5` y `numpy==2.5.3`, **no** las dependencias del laboratorio ni `pandera`. Si instalara el `requirements.txt` de la raíz del repositorio, indica que no detectó `tablero/requirements.txt`; ese archivo debe quedar junto al archivo principal.
8. **Verificar la URL pública** (guía en §8) y enviar el enlace para anotarlo en la ficha de entrega.
**Si falla:** ver el registro de la aplicación («Manage app»). Causas probables: Python distinto de 3.13, la rama o la ruta del archivo principal mal escritas, o el repositorio sin acceso para la cuenta.

## 8. Verificación a realizar sobre la URL pública (pendiente)
Abrir la URL en el navegador y en un teléfono, y comprobar que: la página carga sin mensaje de error; el título y el aviso superior se ven; las seis pestañas abren; las gráficas de «Resumen», «Pronóstico 2024» (con la franja del intervalo), «Comparación de modelos» (barras y líneas) y «Proyección 2025» se dibujan; los indicadores muestran 45.9 %, 54.7 %, 1.5 % y 12 de 12; la pestaña «Proyección 2025» muestra el aviso de proyección histórica; y «Fuentes y datos» muestra la fecha de generación. Registrar la fecha y la URL verificadas.

## 9. Verificación realizada en local (2026-11-13)
- **Arranque:** el servidor inició desde un directorio ajeno al repositorio y respondió; la prueba de arranque con `streamlit.testing` no produjo excepciones.
- **Cifras:** los 4 indicadores y las tablas coinciden con el laboratorio (el cargador recalcula las métricas desde los pronósticos y las compara).
- **Intervalos:** el del 95 % se dibuja como franja entre el límite inferior y el superior (una prueba lo comprueba en la especificación de la gráfica); en 2024 los 12 valores reales caen dentro.
- **Vista:** revisada a mano en escritorio y en móvil (375 × 812): los indicadores se apilan, las pestañas se desplazan, las leyendas son legibles. **Es una revisión visual, no una prueba automatizada.**
- **Privacidad y secretos:** una prueba comprueba que el código no lee DENUE, bronce ni plata, no usa secretos, red ni rutas absolutas; y `gitleaks` 8.30.1 no encontró hallazgos en los archivos nuevos.

## 10. Limitaciones
- **Los datos terminan en diciembre de 2024:** no hay 2025 ni 2026 observados; la proyección de 2025 no se puede evaluar.
- **Un solo año de prueba (12 meses):** no permite afirmar que un modelo sea mejor que otro de forma estable; el SARIMA no supera a la referencia ingenua en MAE ni en MAPE.
- **Intervalos muy amplios** (de ±12 a ±21 puntos porcentuales en 2025) porque el entrenamiento incluye COVID.
- **Resultados precalculados:** el tablero no se actualiza solo; para nuevos datos hay que regenerar el laboratorio y volver a versionar los resultados. Los resultados se generaron con Python 3.14.3; con otras versiones aparecen diferencias numéricas pequeñas (hasta 0.0086), sin cambio de conclusiones ([`pronostico.md`](pronostico.md) §8).
- **Una categoría agregada:** hoteles de 2 a 5 estrellas de Manzanillo en conjunto; no hay desglose ni datos de establecimientos.
- **Pruebas de la aplicación no están en el CI** (se omiten allí), y la revisión de móvil fue visual.
- **Streamlit Community Cloud** puede poner la aplicación en reposo por inactividad y tardar unos segundos en reactivarla; no es un servicio con disponibilidad garantizada.
- **Nombre provisional:** el nombre del observatorio puede cambiar.
