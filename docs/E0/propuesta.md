# Propuesta E0 · Observatorio Turístico y Hotelero de Manzanillo, Colima

**Proyecto integrador TRUSTED DATA LAB** · Equipo: _integrantes por completar_ · Versión: 2026-11-09 (borrador para revisión del equipo)
**Nombre comercial:** por definir. (“StayMetrics” fue únicamente el prototipo previo.)

> **Cómo leer este documento en un minuto.** Vamos a medir y pronosticar la ocupación hotelera de Manzanillo con datos oficiales de SECTUR (108 meses, 2016–2024) y a describir su oferta de hospedaje con el directorio del INEGI, que capturamos cada día. Servirá a quienes administran o invierten en hoteles de Manzanillo para ver patrones y riesgos, **no** para fijar precios ni decidir inversiones por sí solo. La entrevista con un usuario real está **pendiente**; todo lo que dice este documento sobre el cliente es hipótesis hasta hacerla.

## 1. Sector, región y usuarios
- **Sector:** hospedaje turístico (hoteles y moteles de categoría turística).
- **Región:** municipio y centro turístico de Manzanillo, Colima.
- **Usuarios previstos (hipótesis a validar en la entrevista):** propietarios, administradores y gerentes de hoteles, e inversionistas o asesores que evalúan el mercado hotelero del puerto. Una asociación hotelera o una dependencia de turismo son clientes alternativos.
- **Por qué pagarían (hipótesis):** hoy comparar la ocupación propia contra el mercado, anticipar la temporada baja y entender qué parte de la demanda es nacional o extranjera exige reunir y limpiar datos dispersos. Un reporte confiable, con la calidad de los datos demostrada, ahorra ese trabajo. **No hemos verificado** que alguien pague por ello; el modelo de negocio se trabaja en E4.

## 2. Problema y pregunta central
**Problema.** Las cifras públicas existen, pero están dispersas, con cambios de marco (por ejemplo en 2017) y sin una medida de su confiabilidad. Un gerente que quiere saber si un mes fue “bueno” no tiene una referencia comparable ni un pronóstico con su margen de error.

**Pregunta central:**
> **¿Cómo ha evolucionado la ocupación hotelera de Manzanillo entre 2016 y 2024 (último mes publicado y verificado: diciembre de 2024), qué patrón estacional tiene y con qué error puede pronosticarse la de los siguientes 12 meses, de modo que propietarios, administradores, gerentes e inversionistas hoteleros cuenten con una referencia confiable del mercado local?**

La pregunta es descriptiva y predictiva. No es causal y no pregunta cuánto cobrar. La comparación con otros destinos de playa no es parte de la pregunta central: es un análisis complementario de E3.

**Producto final.** El resultado de las cinco semanas será un **observatorio** (tablero público, reporte de inteligencia y dataset documentado) para esos usuarios: sirve para ver el comportamiento histórico y estacional de la ocupación, un pronóstico con su intervalo y la composición de la oferta de hospedaje. E0 solo construye la base: pregunta, fuentes, captura e indicadores de calidad. El tablero, el pronóstico y los análisis aún **no existen**.

## 3. Alcance real de los indicadores
Qué sí podemos calcular con los datos que tenemos (Base70centros, SECTUR/DataTur; mensual, por centro y categoría de 2 a 5 estrellas):
cuartos disponibles; cuartos ocupados de residentes y no residentes; llegadas de turistas y turistas-noche (residentes y no residentes); y de ahí **porcentaje de ocupación, estadía promedio, densidad de ocupación y proporción de no residentes**.

Qué **no** podemos afirmar:
- No hay precios (tarifas) en ninguna fuente actual: **no habrá recomendaciones de precios**.
- No hay ingresos, costos ni rentabilidad por hotel: **no habrá recomendaciones de inversión ni de rentabilidad**.
- Los datos son de **centro turístico y categoría**, no de hoteles individuales. El DENUE describe la oferta (cuántos establecimientos, de qué tamaño y dónde), pero **no se asigna ocupación a un hotel concreto**.
- “Residentes / no residentes” aproximan nacionales y extranjeros; no son equivalentes exactos.
- La serie termina en 2024-12 (ver sección 5). Dos quiebres obligan a cuidado al comparar: el cambio de marco de 2017 y la caída por COVID (2020-03 a 2021-06).
- Las cifras de SECTUR pueden revisarse retroactivamente (aviso de la propia ficha).

## 4. Preguntas analíticas para las siguientes entregas
Solo se **formulan** ahora; no se ejecutan análisis nuevos en E0.

| Entrega | Pregunta | Variable / factores / grupos | Técnica | Notas honestas |
|---|---|---|---|---|
| **E1** | ¿Cuál será el porcentaje de ocupación mensual de Manzanillo en los siguientes 12 meses y con qué intervalo? | Variable: `% de ocupación` (cuartos ocupados / disponibles) de Manzanillo, 108 meses | Descomposición, estacionariedad (ADF), ACF/PACF; suavizamiento exponencial, Holt, Holt-Winters y ARIMA/SARIMA; selección con los últimos meses como prueba por MAE, RMSE y MAPE | **Medible:** gana el modelo con menor MAPE sobre los últimos 12 meses reservados como prueba (se reportan también MAE y RMSE) y se publica con intervalo de predicción del 95 %. Limitaciones: la serie termina en 2024-12; hay que tratar 2017 y COVID (recorte o variable indicadora); los resultados exploratorios del prototipo no son de este repositorio y se reharán. |
| **E2** | ¿Qué combinación de configuración de **nuestro propio extractor** (procesos, analizador HTML/JSON, formato de salida) da menor tiempo y menos errores? | Tres factores de dos niveles (diseño 2³, ≥ 2 réplicas por tratamiento, orden aleatorizado, bloqueo por día/máquina): procesos (1 / 4), analizador (html.parser / lxml o json / orjson) y formato de salida (CSV / Parquet). Respuestas: segundos de procesamiento y tasa de error (%) | Factorial, ANOVA, supuestos con residuos, corrida de confirmación | **Medible:** efectos principales e interacciones significativos al 5 % (ANOVA), supuestos con residuos y una corrida de confirmación de la combinación óptima. Limitaciones: **ruta ingeniería**, contra copia local o API propia (nunca saturando un sitio ajeno); los niveles definitivos se fijan en E2; la ruta negocio requiere un acuerdo con un cliente real que **no existe** hoy. |
| **E3** | ¿Los tipos de destino de playa (integralmente planeados, tradicionales, otros) y ciudades se distinguen por su perfil de ocupación y composición de la demanda? | Grupos (≥ 3): subtipos de centros de playa — Integralmente Planeados, Tradicionales y Otros (5, 7 y 7 centros en el prototipo, por re-verificar) —, con unidades centro-año; respuestas: % de ocupación, estadía promedio, llegadas por cuarto y % de no residentes | PCA y comparación multivariada | **Medible:** varianza explicada por los componentes y contraste entre grupos con un método que cumpla sus supuestos (Pillai con permutaciones u otro robusto). Limitaciones: **MANOVA todavía no está validado** (ver sección 7); grupos pequeños; “residentes / no residentes” es una aproximación. |

**Experimentos controlados frente a análisis observacionales.** El **único** experimento controlado previsto es el factorial de E2 sobre nuestro extractor: nosotros asignamos los niveles y aleatorizamos el orden, por lo que sí admite lenguaje causal sobre el extractor. **Todo el análisis de ocupación (E1 y E3) es observacional**: describe y pronostica, y no demuestra que algo “cause” la ocupación. No se presentarán resultados observacionales como efectos causales.

## 5. Fuentes y condiciones de acceso
Detalle completo, con el origen de cada afirmación, en [`docs/fuentes/`](../fuentes/README.md).

| Fuente | Uso | Acceso y condiciones | Estado |
|---|---|---|---|
| **DATATUR · Base70centros** (SECTUR) | Serie histórica mensual 2016-01 a 2024-12 (Manzanillo: 108 meses; 64 centros) | Datos abiertos, **licencia CC BY 4.0** (leída hoy en datos.gob.mx). El servidor bloquea scripts (HTTP 403); se descarga con navegador y se verifica por SHA-256. | Archivo en bronce con hash verificado contra la descarga oficial |
| **INEGI · DENUE** | Segunda fuente, **captura diaria** (oferta de hospedaje SCIAN 721 en Manzanillo) | API REST con token gratuito; términos de libre uso con crédito a INEGI. Se eliminan nombre, razón social, teléfono, correo, sitio web y domicilio antes de guardar. | **Captura real ejecutada en GitHub Actions** (manual): 134 de 134 establecimientos, bronce sanitizado y bitácora publicados por el bot. Ejecución **programada** (`schedule`) aún sin evidencia |
| DATATUR · Sistema de Monitoreo (2022–2026) | Habría extendido la serie | Endpoint interno sin documentación; términos de gob.mx restringen la difusión pública; **autorización no confirmada**. **No es una fuente automatizada autorizada.** | **Suspendida**; ni se captura periódicamente ni se publica. Hasta que se aclare, **el histórico utilizable termina en diciembre de 2024** |

**Decisión pendiente del equipo:** si se solicita autorización a SECTUR/DataTur para el Sistema de Monitoreo o se trabaja solo con Base70 (recomendado, ver `docs/fuentes/datatur.md` §7).

### Qué está verificado y qué sigue pendiente (corte 2026-11-09)
| Verificado | Pendiente |
|---|---|
| Base70 en bronce: 108 meses de Manzanillo sin huecos, hash igual al archivo oficial, licencia CC BY 4.0 leída | Entrevista; token de INEGI y primera corrida real del DENUE |
| Captura DENUE real en GitHub (manual): 134/134, sin campos personales (verificador de privacidad sobre 4 archivos reales); prevención de duplicados observada en la bitácora; 69 pruebas locales | Ejecución programada (`schedule`); bitácora de 7 días; disponibilidad actual **66.7 % (2 de 3), por debajo del objetivo de 95 %** |
| Planes y permisos de las fuentes documentados | Entrevista (la integra la compañera); decisión sobre DATATUR 2025–2026; registros PSP con datos reales |

## 6. Plan de recopilación
1. **Histórico (bronce).** `Base70centros.csv` completo, sin modificar, con `.meta.json` y atribución. Verificación reproducible: `python -m pipeline.verificar_e0 --solo historico` (108 meses de Manzanillo, sin huecos).
2. **Captura diaria (bronce).** GitHub Actions ejecuta `captura-diaria.yml` cada día 07:17 (Ciudad de México): consulta `Cuantificar` y `BuscarAreaAct` del DENUE, guarda las respuestas sanitizadas por fuente y fecha con SHA-256, y añade una línea a `calidad/bitacora_capturas.jsonl` (éxito, fallo u omisión por duplicado). Una segunda ejecución el mismo día no vuelve a consultar la API.
3. **Ética.** User-Agent identificable, pausa ≥ 1.5 s, reintentos limitados con espera exponencial, lectura de `robots.txt` y detención si no puede verificarse. No se evaden bloqueos.
4. **Calidad desde el inicio.** Registros individuales de tiempo y defectos (formato PSP del Kit), tres objetivos medibles ([`calidad/objetivos.md`](../../calidad/objetivos.md)) y revisión compartida con Quality Lead por entrega.
5. **Siguientes capas (no se implementan en E0).** Plata (validación, cuarentena con motivo) y oro (diccionario de datos) en E1; fuente especializada geoespacial con el DENUE en E2.

## 7. Limitaciones y riesgos
- **Serie corta en el extremo:** termina en 2024-12 mientras no se resuelva el acceso a 2025–2026; el pronóstico de E1 será un ejercicio sobre el histórico, no una cifra actualizada.
- **DENUE cambia poco:** la captura diaria demuestra la máquina de captura y la bitácora, pero la fuente no varía a diario; no aporta una serie diaria de ocupación.
- **Captura programada aún sin evidencia de `schedule`:** hay ejecuciones manuales reales en GitHub (bitácora `calidad/bitacora_capturas.jsonl`), pero ninguna disparada por el calendario todavía; ver `docs/E0/verificacion.md`.
- **Fiabilidad:** la bitácora necesita al menos 7 días para medirla en E1.
- **MANOVA (E3) no validado.** En el prototipo, un análisis exploratorio con tres destinos arrojó una prueba no válida porque fallaron los supuestos: colinealidad fuerte entre variables (r = 0.96), covarianzas heterogéneas (Box’s M, p < 0.001), no normalidad multivariada y autocorrelación mensual de hasta 0.92. Hay que resolver esos problemas (otras variables, observaciones anuales o trimestrales, más centros por grupo, estadísticos robustos o permutaciones) **antes** de publicar cualquier resultado multivariado. No se avanza en ello en E0.
- **Equipo de 2 personas:** cada integrante debe poder explicar cualquier parte.
- **Uso de IA generativa:** el código y los borradores de este repositorio se prepararon con asistentes (Claude Code); el equipo debe revisar y poder defender lo que entrega.

## 8. Entrevista de validación — **SECCIÓN QUE COMPLETA LA COMPAÑERA (PENDIENTE DE INTEGRAR)**
> **Aviso para quien integre:** el equipo informa que la entrevista ya se realizó, pero **su registro todavía no está en este repositorio**. Esta sección la completa la persona que la hizo, desde su copia, **solo con lo que realmente ocurrió** (entrevistado, fecha, duración ≥ 15 min, respuestas y aprendizajes). Nada de lo que aparece abajo es una respuesta real. Quien no hizo la entrevista no debe llenarla ni resumirla.

Requisitos del expediente: al menos 15 minutos, con alguien del sector, cinco preguntas, respuestas y lo aprendido.

| Campo | Valor |
|---|---|
| Entrevistado (rol y tipo de negocio; evitar datos personales si no autoriza) | _pendiente_ |
| Fecha y duración | _pendiente_ |
| Quién entrevistó y quién tomó notas | _pendiente_ |
| Consentimiento para citar | _pendiente_ |

| # | Pregunta (borrador sugerido, editable) | Respuesta |
|---|---|---|
| 1 | ¿Qué decisión de su hotel le gustaría tomar con mejores datos sobre la ocupación de Manzanillo? | _pendiente_ |
| 2 | ¿Qué información usa hoy para comparar su ocupación con el mercado, y qué le falta? | _pendiente_ |
| 3 | ¿Qué le sería útil saber con 3 a 12 meses de anticipación? | _pendiente_ |
| 4 | ¿Con qué frecuencia necesitaría el reporte y en qué formato? | _pendiente_ |
| 5 | ¿Qué tendría que contener para confiar en él, y pagaría por ello (quién y cuánto)? | _pendiente_ |

| Qué aprendimos | Cómo cambia esto la pregunta o el alcance |
|---|---|
| _pendiente_ | _pendiente_ |

Las respuestas deberán ajustar las secciones 1, 2 y 4 si contradicen las hipótesis actuales.
