# Auditoría integral de E1 contra el PDF del proyecto

Corte 2026-11-14 03:15 UTC · Rama `e1/cierre-documental` sobre `main` (`ac9c88d`), sin commit · Fuente: texto del PDF «Proyecto Integrador» (págs. 4–6, 12–17, 23–26, 33) y archivos del repositorio. **No es una calificación**: es una verificación de evidencias hecha por la integrante A con asistencia de Claude Code (no es una revisión independiente). Las notas por criterio están en [`ENTREGA.md`](ENTREGA.md).

Estados: **CUMPLE** (evidencia verificable), **PARCIAL** (existe, pero con una brecha declarada), **NO CUMPLE**, **NO VERIFICABLE** (depende de algo fuera del repositorio).

## 1. Criterios de la rúbrica E1 (págs. 24 a 26)
**Aclaración sobre una versión anterior de este documento:** los criterios «Plan de recopilación» (20), «Captura y serie histórica» (25) y «Arranque de calidad» (15) que aparecen al inicio de la pág. 24 pertenecen a la rúbrica de **E0** (con «Pregunta y cliente» y «Preguntas analíticas» suman 100). No puntúan en E1; la pág. 14 los lista como parte de lo que se construye y se mantienen documentados en [`ENTREGA.md`](ENTREGA.md). La puntuación por materia está en [`evaluacion_rubrica.md`](evaluacion_rubrica.md).
| # | Criterio (puntos) | Estado | Brecha principal |
|---|---|---|---|
| D1 | Valores faltantes (15) | CUMPLE con salvedad | Manzanillo no tiene faltantes; el mecanismo de la celda de Mexicali no se puede determinar con un caso. Diagnóstico y simulación en [`faltantes_y_atipicos.md`](faltantes_y_atipicos.md) |
| D2 | Atípicos y ruido (15) | CUMPLE | Sin Isolation Forest (IQR y z robusto coinciden) |
| D3 | Normalización, discretización y reducción (15) | CUMPLE con salvedades | La discretización supervisada no generaliza a 2024 (12 meses); jerarquías y reducción implementadas |
| D4 | Integración de fuentes (20) | CUMPLE con salvedad | Sin unión mes a mes: las fuentes no se solapan en el tiempo |
| D5 | Puerta de calidad (25) | CUMPLE | — |
| S1 | Caracterización y descomposición (15) | CUMPLE | Evidencia débil a favor de aditiva (6 años) |
| S2 | Estacionariedad y autocorrelación (15) | CUMPLE | — |
| S3 | Cuatro modelos (25) | CUMPLE | Parámetros ETS en la frontera |
| S4 | Selección por error (20) | CUMPLE con salvedades | Un solo año de prueba; el ingenuo gana en MAE y MAPE |
| S5 | Residuos y comunicación (15) | CUMPLE con salvedad | Residuos no normales (intervalos aproximados); el tablero público ya sirve la versión integrada (2026-11-14 04:25 UTC) |
| Q1 | Fiabilidad y disponibilidad (25) | PARCIAL | 3.83 de 7 días y no hay historia real recuperable ([`fiabilidad.md`](fiabilidad.md) §4.2); MTBF y A exploratorios; objetivo del 95 % no cumplido |
| Q2 | Seguridad (15) | CUMPLE con salvedades | Respaldo con restauración probada, bloqueo con hashes y acciones por SHA: comprobados en local; CI nuevo sin ejecutar en GitHub; `main` sin protección; respaldo en el mismo equipo |
| Q3 | Requerimientos (10) | CUMPLE | Los 7 agregados el 2026-11-14 sin revisión de B |
| Q4 | Plan SQA (25) | CUMPLE con salvedades | Nueve PR fusionados sin revisión previa; acción correctiva y excepción de E1 no implementadas |
| Q5 | Integración continua (15) | PARCIAL | `main` en verde en `ac9c88d` tras 3 ejecuciones fallidas; el CI nuevo no se ejecutó en GitHub; sin protección de `main` |
| R | Relatoría de etapa (10 en cada materia) | PARCIAL | [`relatoria-E1.md`](../relatoria-E1.md) está redactada; falta la revisión y conformidad de las dos integrantes |

## 2. Requisitos de la entrega (PDF, págs. 4–6 y 12–13)
| Requisito | Estado | Evidencia o brecha |
|---|---|---|
| Una sola ficha `docs/E1/ENTREGA.md` con tres apartados | CUMPLE (en la rama) | [`ENTREGA.md`](ENTREGA.md) |
| Etiqueta `e1` antes de las 23:59 del día de entrega | **NO CUMPLE todavía** | No existe; no se creará sin autorización |
| Enlace registrado en el formulario de entregas | NO VERIFICABLE | Fuera del repositorio |
| Repositorio con ambos integrantes | CUMPLE | Contribuyentes `Leslie581` y `eimymuz` |
| Los tres docentes como colaboradores | DECLARADO, no verificable | La titular informó el 2026-11-13 que los tres ya tienen acceso; la API pública no lista colaboradores |
| Issues de los docentes con etiqueta de materia | NO VERIFICABLE | Hay 0 issues públicos (2026-11-14) |
| Relatoría ≤ 2 páginas con las seis preguntas en orden | PARCIAL | 730 palabras (≈ 1.8 páginas estimadas: ~80 líneas de 45 por página), con las seis preguntas en orden; falta la conformidad de las integrantes |
| Registros PSP individuales, uno de los dos con la revisión | PARCIAL | Véase C3 |
| Uso de IA declarado | CUMPLE | En `ENTREGA.md` y en la relatoría |
| Preparación de E2: ruta del experimento (no se califica) | PARCIAL | [`ruta_experimento_e2.md`](ruta_experimento_e2.md): ruta ingeniería y matriz 2³; falta la conformidad de B |
| Tablero con URL pública | CUMPLE | Verificada el 2026-11-14 a las 04:25 UTC (2026-11-13, 22:25, hora de la Ciudad de México) en el navegador integrado: la aplicación, desplegada desde `main` con Python 3.13 (declarado por la titular del repositorio), muestra el filtro de periodo, el resumen ejecutivo, las fechas clave y los indicadores 45.9 %, 54.7 %, 1.5 % y 12 de 12; las seis pestañas abren sin errores y la frase que reemplazó el PR #15 ya no aparece. No se probó en un teléfono |
| Panel de medio término (17 y 18 de noviembre) | PENDIENTE | Defensa individual |

## 3. Hallazgos de esta auditoría que no estaban en las Auditorías 1 a 6
1. **Los criterios «Plan de recopilación», «Captura» y «Arranque de calidad» son de E0, no de E1.** Una versión anterior de esta auditoría y de `ENTREGA.md` los puntuaba como de E1; se corrigió.
2. **La ventana de bitácora del PDF (6 al 13 de noviembre) no se puede completar**: el flujo de captura se creó el 2026-11-09 19:10 UTC y las 3 ejecuciones más antiguas de la bitácora ya no existen en la API (404). No se pudo recuperar nada más sin inventarlo.
3. **La URL pública del tablero servía una versión anterior** a las 03:09 UTC (17 min después de fusionar el PR #15; D2 de la [Auditoría 7](../../calidad/auditorias.md)). **Resuelto:** la titular reconfiguró el despliegue desde `main` y a las 04:25 UTC la URL sirve la versión integrada.
4. **`docs/E1/tablero.md`** tenía cifras y enlaces desactualizados; se corrigieron en esta rama (Auditoría 7, O3) y B debe revisarlos.
5. **Faltaban en E1** y se implementaron el 2026-11-14: jerarquías conceptuales, discretización supervisada, diagnóstico de faltantes con comparación de tratamientos, z robusto para atípicos, reducción con porcentajes impresos por el pipeline y copia del bronce con manifiesto y restauración.
6. **Cobertura de pruebas** (medida con `pytest --cov`): 84 % sobre `pipeline`, `extractores`, `laboratorio` y `tablero`; huecos: `laboratorio/pronosticos/ejecutar.py` (0 %, orquestación por línea de comandos), `extractores/base.py` y `datatur.py` (rutas de red).
7. **Protección de `main`:** la API pública devuelve `protected: false` (2026-11-14); no se puede configurar sin permisos de administración. **Permisos de los tokens:** `ci.yml` solo lee y ya no persiste credenciales; `captura-diaria.yml` conserva solo `contents: write` y un secreto.
8. **Plazo:** la etiqueta `e1` debe existir antes de las 23:59 del 13 de noviembre (pág. 5); si no, se evalúa sobre 70.

Los hallazgos de proceso (fusiones sin revisión; CI en rojo con el PR #14 y su corrección) están en [`plan_sqa.md`](plan_sqa.md) §5.1 y §6 y en las Auditorías 5 a 7.
