# Encuesta de validación de usuarios (E0): metodología y tratamiento de datos

Corte: 2026-11-09. Resultados en [`informe_encuesta_e0.md`](informe_encuesta_e0.md).

> **Qué es y qué no es.** Es un **cuestionario autoadministrado** (Google Forms) que se usa como **evidencia complementaria de validación de usuarios**. **No es la entrevista individual** de E0 (no registra duración, entrevistador ni notas), que se documenta por separado en [`../Entrevistas/entrevista_01.md`](../Entrevistas/entrevista_01.md). Según lo comunicado por el colaborador externo que aplicó la entrevista, la persona entrevistada también respondió esta encuesta. **No se ha verificado** a qué envío corresponde, no se añade como participante adicional y las cifras de la encuesta no se recalculan ni se le atribuyen.

## 1. Instrumento y recopilación
| Aspecto | Valor |
|---|---|
| Herramienta | Google Forms, exportado a CSV (UTF-8) |
| Título del formulario | "StayMetrics" (nombre del prototipo; el nombre comercial del observatorio sigue por definir) |
| Fecha de recopilación | 2026-11-09 (todos los envíos, por la tarde-noche) |
| Población a la que se dirigió | Personas vinculadas al hospedaje turístico (hoteles, resorts, rentas vacacionales y similares) |
| Muestreo | **Por conveniencia**; no probabilístico. No hay marco muestral ni tasa de respuesta conocida |
| Envíos recibidos | **11** |
| Envíos con consentimiento de participación | **10**. El envío sin consentimiento no contiene ninguna otra respuesta |
| Consentimiento recogido | Solo para **participar voluntariamente**. **No** se pidió autorización para citar ni para publicar respuestas individuales |
| Estructura del CSV | 38 columnas: marca temporal, consentimiento y 36 preguntas. 5 preguntas están vacías en todos los envíos |

## 2. Tres versiones del formulario
El formulario se modificó mientras se respondía. Por el patrón de columnas con datos, se distinguen tres versiones sucesivas:

| Versión | Envíos con consentimiento | Características |
|---|---:|---|
| **V1** | 4 (más el envío sin consentimiento) | Preguntas abiertas largas sobre estacionalidad, organización, dificultades y necesidades de información |
| **V2** | 1 | Transición: añade listas cerradas de meses, dificultades y acciones |
| **V3** | 5 | Mayoría de opciones cerradas; añade frecuencia de desviaciones, reacción, precios, información difícil de conseguir y barreras de uso |

Consecuencia: **cada pregunta tiene su propio denominador** (entre 4 y 10). En el informe, todo porcentaje indica su `n`.

Las versiones son **inferidas**: la exportación no registra a qué versión respondió cada envío. El envío sin consentimiento no tiene respuestas, así que se asigna a V1 por su hora de envío.

## 3. Inconsistencias detectadas y cómo se trataron
| # | Inconsistencia | Tratamiento |
|---|---|---|
| I1 | Dos columnas tienen el **mismo título** ("¿En qué decisiones consultaría una plataforma como StayMetrics?"). Una contiene texto libre sobre decisiones (solo V1) y la otra una **lista de funcionalidades** | La primera se analiza como "decisiones" (cualitativo) y la segunda como "funcionalidades de interés" |
| I2 | La columna "¿Qué podría hacer que NO la usara o la usara poco?" contiene, en V1, **relatos de ocupaciones distintas a lo esperado** (parece que se cambió el título de una pregunta ya respondida). La pregunta original del relato quedó vacía | V1 se trata como evidencia cualitativa de desviaciones y V3 como "barreras de uso" (n = 5). No se mezclan |
| I3 | Una respuesta a "¿Consideraría pagar…?" no responde a la pregunta | Se clasifica como "no pertinente" y se excluye del denominador (n = 9) |
| I4 | La pregunta "meses con MÁS huéspedes" se respondió en V1 con texto libre que a veces también menciona los meses bajos | Las listas cerradas (V2/V3, n = 6) se cuantifican; el texto de V1 solo se resume de forma cualitativa |
| I5 | La pregunta de consentimiento dice "entrevista", pero el instrumento es un formulario | Se documenta como encuesta, no como entrevista |
| I6 | Las opciones cambian de redacción entre versiones | Se agrupan según la tabla de la sección 4 |
| I7 | Hay una opción que contiene comas: "Estadísticas oficiales (DataTur, Secretaría de Turismo, asociaciones)" | Se cuenta por coincidencia con el catálogo de opciones, no separando por comas |
| I8 | La escala de utilidad (1 a 5) no trae las etiquetas de sus extremos en el CSV | Solo se reportan frecuencias y media/mediana, sin interpretar el significado de cada valor |
| I9 | Un participante declara no participar en las decisiones ni tener información sobre ellas, pero responde preguntas de gestión | Se conserva (no hay criterio previo para excluirlo); se advierte como limitación |
| I10 | 4 de los 10 participantes están fuera del municipio de Manzanillo (3 en Jalisco, 1 sin municipio especificado) | Se conservan en el total; el subgrupo de Manzanillo (n = 6) se reporta aparte cuando es pertinente |

## 4. Agrupación de opciones equivalentes entre versiones
| Categoría usada en el informe | Redacciones originales agrupadas |
|---|---|
| Sistema o software de administración hotelera (PMS) | "Software de administración hotelera" (V1) · "Sistema de administración hotelera" (V2/V3) |
| Hojas de cálculo (Excel) | "Excel u hojas de cálculo" · "Hojas de cálculo (Excel)" |
| Reportes de plataformas de reservación | "Plataformas como Booking o Airbnb" · "Reportes de plataformas de reservación" |
| Reservación directa | "Reservaciones directamente en el establecimiento" · "Reservaciones directas" |

Las opciones que **solo existían en una versión** se reportan con el denominador de esa versión (por ejemplo, "Estadísticas oficiales" o "Calendarios de eventos": n = 6, V2/V3). Que V2 ofreciera el mismo catálogo de herramientas que V3 se **infiere** de que su respuesta usa la redacción de V3; la exportación no conserva el catálogo de opciones. Las categorías de perfil se generalizaron así:
- **Ubicación:** Manzanillo · Colima, municipio no especificado · fuera de Colima.
- **Tipo:** hotel o resort · renta vacacional · bungalows.
- **Puesto:** propietario o anfitrión · dirección o administración · operativo.

## 5. Criterios de inclusión y exclusión
- **Incluidos:** los 10 envíos con "Sí, acepto participar".
- **Excluido:** 1 envío con "No acepto participar". Solo se cuenta en el total de envíos y no se analiza (además, no tiene respuestas).
- **No se eliminó ni se editó ningún registro** del archivo original. No se detectaron filas idénticas. Al no haber identificadores, no puede descartarse que una persona haya respondido más de una vez.

## 6. Valores faltantes
- **Faltante estructural:** la pregunta no existía en la versión que respondió esa persona. No cuenta en el denominador.
- **Omisión:** la pregunta existía, pero se dejó en blanco (eran opcionales). Se reporta como "sin respuesta".
- **Un vacío nunca se interpreta como "no" ni como respuesta negativa.**
- Las 5 preguntas vacías en todos los envíos no se analizan.

## 7. Privacidad y publicación
| Medida | Estado |
|---|---|
| Identificadores directos (nombre, correo, teléfono, sitio web, nombre del establecimiento) | **No existen** en el CSV (revisión manual y por patrones) |
| Archivo original | **Fuera de Git**, en `evidencias_privadas/encuesta_e0/respuestas_original.csv` (carpeta ignorada por `.gitignore`). SHA-256 `84c36f9015b698c80702ada33921d19be93dd6e4f3858282aa355632d7ccadc8`, 26 941 bytes. Se conserva sin modificaciones |
| Cuasi-identificadores (hora exacta, combinación de ubicación, tipo, puesto y antigüedad, detalles del texto libre) | **No se publican.** Con n = 10 la mayoría de esas combinaciones son únicas |
| Respuestas individuales y citas textuales | **No se publican** (no hay consentimiento para citar). Solo se publican **estadísticas agregadas** y temas resumidos |
| Tablas cruzadas | No se publican celdas que, combinando perfil y respuestas, describan a una sola persona |
| Información comercial (precios, herramientas pagadas, gastos) | Solo de forma agregada |

> El repositorio está en una carpeta sincronizada con OneDrive: `evidencias_privadas/` queda fuera de GitHub, pero **no fuera de OneDrive**. El equipo decide si conservar ahí el original o moverlo a otra ubicación privada.

## 8. Reproducibilidad
Las frecuencias de las preguntas cerradas, la utilidad y la Tabla 1 se calcularon de forma automática desde el archivo original (privado), con las reglas de las secciones 3 a 6. Quien tenga el original puede verificarlas comparando primero su SHA-256 con el de la sección 7.

Los conteos de **temas del texto libre** (secciones 5.2, 5.4 y 5.7 del informe) provienen de una **codificación manual**: cada idea de una respuesta se asigna a un tema y los temas no son excluyentes. No se reproducen automáticamente.
