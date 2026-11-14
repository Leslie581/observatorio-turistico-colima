# Relatoría E1 · Observatorio de Ocupación Hotelera de Colima (Manzanillo)

Equipo: Leslie Valadez Macías (A) y Eimy Melissa Urbina Meza (B) · Periodo: 2026-11-12 a 2026-11-13 · **Conformidad: A, conforme; B, conforme de forma definitiva** al aprobar el [PR #19](https://github.com/Leslie581/tdl-turistico-colima/pull/19) (`ceb9d97`), versión entregada (etiqueta `e1` sobre `134c333`)
Horas de la Ciudad de México (UTC−6) salvo indicación; GitHub registra en UTC (el PR #15 se fusionó el 14-nov 02:52 UTC = 13-nov 20:52 local).

## 1. Qué nos propusimos
Que los datos de DATATUR y DENUE viajen de bronce a oro sin intervención, con una puerta de calidad que muestre cuántos registros rechaza y por qué; publicar un pronóstico de ocupación hotelera de Manzanillo elegido por su error en datos de prueba; y medir (no suponer) la fiabilidad de la captura contra el objetivo de 95 % de éxito.

## 2. Qué hicimos
| Fecha | Qué | Quién | Evidencia |
|---|---|---|---|
| 12-nov | Contrato de datos 1.0.0 y plan de trabajo | A | PR #7, `f18e93a` |
| 12–13-nov | Laboratorio estadístico y de pronósticos; evaluación con el oro; cierre estadístico y Auditoría 5 | B | `02057b1`, `18d75eb`, `c47d4e4`, `2aceafc` |
| 13-nov | Pipeline plata/oro con puerta de calidad; exploración, transformaciones y CI; calidad, seguridad y plan SQA | A | `70a26b9`, `de42284`, `809cfa3` |
| 13-nov | Tablero (MVP) y su cierre con la corrección del CI | Git: A (`9489dc5`) y B (`80d8b5b`, `eb8f606`) | `9489dc5`, `80d8b5b`, `eb8f606` |
| 13-nov | Cierre documental: Auditorías 6 y 7, `gitleaks` y pruebas del tablero en CI, y lo que la auditoría contra el PDF mostró que faltaba (jerarquías, discretización supervisada, faltantes, respaldo del bronce, bloqueo con hashes) | A, con Claude Code | rama `e1/cierre-documental` |

**Autoría de `9489dc5`.** Git registra a Leslie Valadez como autora y comitente del MVP del tablero (`9489dc5`) y a `eimymuz` como autora de `80d8b5b` y `eb8f606`. Git no dice quién redactó qué dentro de `9489dc5`: la documentación lo atribuía a un trabajo de B y el commit se publicó desde la cuenta de A. Aquí solo se afirma lo que Git registra; la contribución técnica de cada una consta en su PSP y en su defensa.

**Tiempo por bloque (PSP).** Ningún tiempo de A se midió: sus **1,380 min de E1** son estimaciones retrospectivas de su dedicación personal: contrato y laboratorio (L0 y L1) 240, pipeline (L2) 150, calidad y tablero (L3) 270, cierre documental 720; con E0, 2,130 min ([CSV](../calidad/tiempo-integrante-a.csv)). B: 118 min en 23 intervalos con inicio y fin ([CSV](../calidad/tiempo-integrante-b.csv)), confirmados en su Auditoría 8 y en el PR #19.

## 3. Qué decidimos y por qué
- **Elegir por RMSE con Ljung-Box como filtro**, fijado antes de comparar: ganó SARIMA(1,1,1)(0,1,1)₁₂ + `d_covid` (RMSE 2.64 pp). Se descartó elegir por MAE, que habría favorecido al ingenuo estacional (2.20 contra 2.38).
- **No unir DATATUR con DENUE fila a fila**: miden cosas distintas y no se solapan en el tiempo; se integran por dimensiones comunes.
- **Marcar, no eliminar, los meses de COVID**: son un evento real, modelado con `d_covid`.
- **MTBF solo exploratorio**: con un incidente y 3.83 días de bitácora no es una medición.

## 4. Qué salió mal y cómo lo corregimos
- **Doce PR de E1 se fusionaron sin revisión previa** (once hacia `main`, #7 a #16 y #18, en 9 a 68 s, y el #17 por error hacia la rama de integración), aunque el plan lo prohibía; el #18, el cierre definitivo, llegó a `main` 12 s después de abrirse sin la aprobación de B prevista. La protección de `main` **no está configurada**.
- **El CI de `main` estuvo en rojo** (3 de 30 ejecuciones) por una prueba del tablero que dependía de `__pycache__` (defecto 22 de A); B la corrigió en `eb8f606` y `main` volvió a verde; el CI nuevo pasó en GitHub (ejecuciones 43557153021 y 43557683882).
- **La URL pública servía una versión anterior** (03:09 UTC del 14-nov); tras reconfigurar el despliegue desde `main`, a las 04:25 UTC sirve la integrada.
- **La bitácora no llega a 7 días** (3.83): éxito 85.7 % (6/7), objetivo del 95 % **no cumplido**; no hay historia real recuperable de Actions.
- **Faltaban requisitos del PDF** que la auditoría final detectó y se implementaron; la discretización supervisada **no generalizó a 2024** (exactitud 0.50 frente a 0.75) y se declara así.

## 5. Qué aprendimos
**Ingeniería de Datos.** Un contrato con reglas numeradas muestra el rechazo: de 31,147 filas, 2 fueron a cuarentena (R-D06). «No imputar» exige decirlo: Manzanillo no tiene faltantes y con una celda en otro destino no se diagnostica el mecanismo.
**Análisis Estadístico.** Con un solo año de prueba el ganador no es estable: el SARIMA gana en RMSE, el ingenuo en MAE y MAPE. Los intervalos son de ±12 a ±21 pp porque el entrenamiento incluye COVID.
**Calidad.** Medir expone lo que se suponía: un incidente da un intervalo del MTBF de 19.3 h a 74.5 días. Y una regla sin control no se cumple: la incumplimos diez veces.

## 6. Evidencias
[`ENTREGA.md`](E1/ENTREGA.md) · [`auditorias.md`](../calidad/auditorias.md) (1 a 8) · [`evaluacion_rubrica.md`](E1/evaluacion_rubrica.md) · [`fiabilidad.md`](E1/fiabilidad.md) · [`pronostico.md`](E1/pronostico.md) · [`plan_sqa.md`](E1/plan_sqa.md) §5.1 · defectos [A](../calidad/defectos-integrante-a.csv) y [B](../calidad/defectos-integrante-b.csv) · [PR #7 a #19](https://github.com/Leslie581/tdl-turistico-colima/pulls?q=is%3Apr) · figuras: [pronóstico](../laboratorio/pronosticos/resultados/figuras/pronostico_modelo_elegido.png), [modelos](../laboratorio/pronosticos/resultados/figuras/comparacion_modelos_2024.png), [residuos](../laboratorio/pronosticos/resultados/figuras/residuos_modelo_elegido.png) · [tablero](https://tdl-turistico-colima.streamlit.app) · [Actions](https://github.com/Leslie581/tdl-turistico-colima/actions) · mejoras posteriores a la entrega: final de [`ENTREGA.md`](E1/ENTREGA.md) (no alteran lo entregado).

## Uso de IA generativa
Claude Code (Anthropic), en ambas cuentas: código, pruebas, documentación, auditorías y verificaciones. Está marcado en los PSP de B y en las auditorías; no cuenta como revisión independiente.
