# Propuesta E0 · Observatorio Turístico y Hotelero de Manzanillo, Colima

**Proyecto integrador TRUSTED DATA LAB** · Equipo: Leslie Valadez Macias (integrante A) y Eimy Melissa Urbina Meza (integrante B) · Versión: 2026-11-10
**Nombre comercial:** por definir. (“StayMetrics” fue únicamente el prototipo previo.)

> **En un minuto.** Mediremos y pronosticaremos la ocupación hotelera de Manzanillo con datos oficiales de SECTUR (108 meses, 2016–2024) y describiremos su oferta de hospedaje con el directorio del INEGI, que capturamos cada día. Servirá a quienes administran o invierten en hoteles de Manzanillo para ver patrones y riesgos, **no** para fijar precios ni decidir inversiones por sí solo. La validación con usuarios (una entrevista de registro parcial y una encuesta exploratoria, §8) es limitada: lo que decimos sobre el cliente sigue siendo **hipótesis**.

## 1. Sector, región y usuarios
- **Sector:** hospedaje turístico (hoteles y moteles de categoría turística). **Región:** municipio y centro turístico de Manzanillo, Colima.
- **Usuarios previstos (hipótesis):** propietarios, administradores y gerentes de hoteles, e inversionistas o asesores del mercado hotelero del puerto. Una asociación hotelera o una dependencia de turismo son clientes alternativos.
- **Por qué pagarían (hipótesis):** comparar la ocupación propia con el mercado, anticipar la temporada baja y distinguir demanda nacional y extranjera exige reunir y limpiar datos dispersos; un reporte confiable ahorra ese trabajo. **No está verificado** que alguien pague por ello (en la encuesta la disposición a pagar es mayormente condicional); el modelo de negocio se trabaja en E4.

## 2. Problema y pregunta central
**Problema.** Las cifras públicas existen, pero están dispersas, con cambios de marco (p. ej. 2017) y sin una medida de su confiabilidad. Un gerente que quiere saber si un mes fue “bueno” no tiene una referencia comparable ni un pronóstico con su margen de error.

**Pregunta central:**
> **¿Cómo ha evolucionado la ocupación hotelera de Manzanillo entre 2016 y 2024 (último mes publicado y verificado: diciembre de 2024), qué patrón estacional tiene y con qué error puede pronosticarse la de los siguientes 12 meses, de modo que propietarios, administradores, gerentes e inversionistas hoteleros cuenten con una referencia confiable del mercado local?**

Es descriptiva y predictiva; no causal ni de precios. La comparación con otros destinos es un análisis complementario de E3. **Producto final:** un observatorio (tablero público, reporte y dataset documentado). E0 solo construye la base (pregunta, fuentes, captura, calidad); el tablero, el pronóstico y los análisis aún **no existen**.

## 3. Alcance real de los indicadores
Con Base70centros (SECTUR/DataTur; mensual, por centro y categoría de 2 a 5 estrellas) se calculan: cuartos disponibles y ocupados (residentes y no residentes), llegadas y turistas-noche, y de ahí **% de ocupación, estadía promedio, densidad de ocupación y proporción de no residentes**. No podemos afirmar:
- **Precios, ingresos o rentabilidad:** ninguna fuente actual los trae, por lo que **no habrá recomendaciones de precios, inversión ni rentabilidad**.
- Datos de **hoteles individuales:** son de centro turístico y categoría. El DENUE describe la oferta (cuántos, de qué tamaño, dónde), pero **no se asigna ocupación a un hotel**.
- “Residentes / no residentes” solo aproximan nacionales y extranjeros.
- Que la serie llegue más allá de 2024-12, ni que sea comparable sin cuidado: hay un cambio de marco en 2017 y la caída por COVID (2020-03 a 2021-06). SECTUR puede revisar cifras retroactivamente.

## 4. Preguntas analíticas para las siguientes entregas
Solo se **formulan** ahora; no se ejecutan análisis nuevos en E0.

| Entrega | Pregunta | Variable / factores / grupos | Técnica y criterio medible | Limitaciones |
|---|---|---|---|---|
| **E1** | ¿Cuál será el % de ocupación mensual de Manzanillo en los siguientes 12 meses y con qué intervalo? | `% de ocupación` (ocupados/disponibles), 108 meses | Descomposición, ADF, ACF/PACF; suavizamiento exponencial, Holt, Holt-Winters y ARIMA/SARIMA. Gana el menor MAPE sobre los últimos 12 meses reservados (también MAE y RMSE); intervalo de predicción del 95 % | Serie hasta 2024-12; tratar 2017 y COVID (recorte o indicadora); los resultados exploratorios del prototipo se reharán |
| **E2** | ¿Qué configuración de **nuestro propio extractor** da menor tiempo y menos errores? | Diseño 2³, ≥ 2 réplicas, orden aleatorizado, bloqueo por día/máquina: procesos (1/4), analizador (html.parser/lxml o json/orjson), formato (CSV/Parquet). Respuestas: segundos y tasa de error | Factorial y ANOVA al 5 %, supuestos con residuos y corrida de confirmación | **Ruta ingeniería**, contra copia local o API propia, nunca saturando un sitio ajeno; niveles definitivos en E2; la ruta negocio requiere un cliente real que no existe hoy |
| **E3** | ¿Los subtipos de centros de playa (integralmente planeados, tradicionales, otros) se distinguen por su perfil de ocupación y demanda? | ≥ 3 grupos (5, 7 y 7 centros en el prototipo, por re-verificar), unidades centro-año; respuestas: % de ocupación, estadía, llegadas por cuarto, % no residentes | PCA y contraste entre grupos con un método que cumpla sus supuestos (Pillai con permutaciones u otro robusto) | **MANOVA no está validado** (§7); grupos pequeños; residentes/no residentes es una aproximación |

**Controlado frente a observacional.** El **único** experimento controlado previsto es el factorial de E2 sobre nuestro extractor (asignamos niveles y aleatorizamos), por lo que admite lenguaje causal sobre el extractor. **E1 y E3 son observacionales**: describen y pronostican, no demuestran causas.

## 5. Fuentes y condiciones de acceso
Detalle y origen de cada afirmación en [`docs/fuentes/`](../fuentes/README.md).

| Fuente | Uso | Acceso y condiciones | Estado (2026-11-10) |
|---|---|---|---|
| **DATATUR · Base70centros** (SECTUR) | Histórico mensual 2016-01 a 2024-12 (Manzanillo: 108 meses; 64 centros) | Datos abiertos, **CC BY 4.0**. El servidor bloquea scripts (HTTP 403): se descarga con navegador y se verifica por SHA-256 | En bronce, con hash igual al archivo oficial |
| **INEGI · DENUE** | Segunda fuente, **captura diaria** (hospedaje SCIAN 721) | API con token gratuito; libre uso con crédito a INEGI. Se eliminan nombre, razón social, contacto y domicilio antes de guardar | Capturas reales en GitHub Actions (134 de 134): 2 manuales y **3 programadas (`schedule`)** en verde, del 10 al 12 de noviembre |
| DATATUR · Sistema de Monitoreo (2022–2026) | Habría extendido la serie | Endpoint interno; términos de gob.mx restringen la difusión; **autorización no confirmada**. No es fuente automatizada autorizada | **Suspendida**; el histórico utilizable termina en 2024-12 |

**Decisión pendiente:** pedir autorización a SECTUR/DataTur para el Sistema de Monitoreo o trabajar solo con Base70 (recomendado; `docs/fuentes/datatur.md` §7).

**Verificado:** 108 meses sin huecos; integridad del bronce; privacidad del DENUE sobre 10 archivos reales; bitácora de 8 ejecuciones, con ejecución `schedule` confirmada. **Pendiente:** bitácora de 7 días (en curso); disponibilidad **83.3 % (5 de 6) al 2026-11-12, por debajo del objetivo de 95 %** (66.7 % al crear la etiqueta); consentimiento y validación docente de la entrevista; decisión sobre DATATUR 2025–2026.

## 6. Plan de recopilación y calidad
1. **Histórico (bronce):** `Base70centros.csv` completo, sin modificar, con `.meta.json` y atribución; verificable con `python -m pipeline.verificar_e0 --solo historico`.
2. **Captura diaria (bronce):** `captura-diaria.yml` corre cada día a las 07:17 hora de Ciudad de México (13:17 UTC): consulta `Cuantificar` y `BuscarAreaAct`, guarda las respuestas sanitizadas por fuente y fecha con SHA-256 y añade una línea a `calidad/bitacora_capturas.jsonl` (éxito, fallo u omisión por duplicado).
3. **Ética:** User-Agent identificable, pausa ≥ 1.5 s, reintentos limitados, lectura de `robots.txt` y detención si no puede verificarse; no se evaden bloqueos.
4. **Calidad:** registros individuales de tiempo y defectos (formato PSP del Kit), tres objetivos medibles ([`calidad/objetivos.md`](../../calidad/objetivos.md): O1 disponibilidad ≥ 95 %, O2 completitud e integridad, O3 cero datos personales y defectos trazables) y auditorías internas posteriores ([`calidad/auditorias.md`](../../calidad/auditorias.md)).
5. **Siguientes capas (no en E0):** plata y oro en E1; fuente geoespacial con el DENUE en E2.

## 7. Limitaciones y riesgos
- **Serie corta en el extremo:** el pronóstico de E1 será un ejercicio sobre el histórico hasta 2024-12.
- **DENUE cambia poco:** la captura diaria demuestra la máquina de captura y la bitácora, no una serie diaria de ocupación.
- **Disponibilidad y programación:** 83.3 % (5 de 6) al 2026-11-12, con un único fallo inicial (falta de token); la fiabilidad con ≥ 7 días se mide en E1.
- **MANOVA (E3) no validado.** En el prototipo, un análisis exploratorio con tres destinos falló sus supuestos: colinealidad (r = 0.96), covarianzas heterogéneas (Box’s M, p < 0.001), no normalidad multivariada y autocorrelación de hasta 0.92. Hay que resolverlo (otras variables, observaciones anuales o trimestrales, más centros por grupo, estadísticos robustos o permutaciones) **antes** de publicar resultados multivariados; no se avanza en E0.
- **IA generativa:** el código y los borradores se prepararon con Claude Code; cada integrante debe poder explicar y defender lo que entrega.

## 8. Validación con usuarios
### 8.1 Entrevista individual — **registro parcial**
Registro: [`Entrevistas/entrevista_01.md`](Entrevistas/entrevista_01.md). El expediente exige al menos 15 minutos, alguien del sector, cinco preguntas, respuestas y aprendizajes.

| Campo | Valor |
|---|---|
| Fecha y modalidad | 2026-11-09, llamada telefónica, con un administrador de alojamiento (perfil anónimo) |
| Duración | Aproximadamente 15 minutos, **reportada**, sin comprobante |
| Quién hizo qué | Preguntas del equipo; entrevista aplicada por un **colaborador externo**; sus respuestas llegaron verbalmente a la integrante B, que las anotó en apuntes privados (registro secundario, no literal) |
| Respuestas | En apuntes privados; **publicación pendiente de consentimiento** |
| Validez para E0 | **Pendiente de confirmar con los docentes** |
| Relación con la encuesta | La persona entrevistada habría respondido también la encuesta; **no verificado**, no se cuenta como participante adicional |

Mientras falten el consentimiento y la confirmación docente, el requisito de entrevista **no se da por cumplido**.

### 8.2 Encuesta StayMetrics (evidencia complementaria)
Cuestionario autoadministrado (Google Forms): 11 envíos, **10 con consentimiento**; muestra por conveniencia (6 de 10 en Manzanillo; 3 de 10 hoteles o resorts de Manzanillo); tres versiones del formulario ([`encuesta/LEEME.md`](encuesta/LEEME.md)). Es **validación exploratoria, no representativa**, y no sustituye a la entrevista. Solo se publican agregados; el archivo original está fuera del repositorio. Resultados: [`encuesta/informe_encuesta_e0.md`](encuesta/informe_encuesta_e0.md); cálculo: [`laboratorio/encuesta_e0/`](../../laboratorio/encuesta_e0/README.md).

| Qué aprendimos (observado) | Efecto en la propuesta |
|---|---|
| Interés en pronósticos de ocupación (8 de 10) y en referencias históricas | Sin cambios en la pregunta central |
| La confianza en los datos es la barrera más citada (4 de 5) | Sin cambios; coincide con documentar procedencia y error del pronóstico (E1) |
| Se pide análisis de precios y competencia tanto como pronóstico (8 de 10), pero no hay tarifas | Se mantiene el límite de §3; cuestión abierta para el equipo |
| Solo 3 de 10 son hoteles o resortes de Manzanillo y la disposición a pagar es mayormente condicional | Usuarios previstos siguen siendo hipótesis; **cliente y modelo de negocio no validados** |
