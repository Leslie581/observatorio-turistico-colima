# Análisis reproducible de la encuesta E0

Reproduce las cifras **automatizables** de [`docs/E0/encuesta/informe_encuesta_e0.md`](../../docs/E0/encuesta/informe_encuesta_e0.md) a partir del CSV original de Google Forms. La metodología, las versiones del formulario y la privacidad están en [`docs/E0/encuesta/LEEME.md`](../../docs/E0/encuesta/LEEME.md).

## Ejecución
Desde la raíz del repositorio (PowerShell o bash):
```
python laboratorio/encuesta_e0/analisis_encuesta.py                 # ruta por defecto
python laboratorio/encuesta_e0/analisis_encuesta.py --csv RUTA.csv   # ruta explícita
```
Ruta del CSV, por orden de prioridad:
1. `--csv`.
2. La variable de entorno `TDL_ENCUESTA_CSV`.
3. `evidencias_privadas/encuesta_e0/respuestas_original.csv`, relativa a la raíz del repositorio (carpeta ignorada por Git).

El CSV **no está en el repositorio**: solo el equipo tiene la copia privada.

## Dependencias
Solo la biblioteca estándar de Python (3.10 o superior). No usa `pandas` ni requiere instalar nada. No está en `tests/` ni en el workflow, así que no corre en GitHub Actions.

## Qué comprueba antes de calcular
- **Integridad:** el SHA-256 completo del CSV debe ser el documentado en el LEEME §7. Si no coincide, termina con código 2 sin dar cifras. `--permitir-otro-hash` analiza otro archivo y marca el resultado como **no correspondiente al informe**.
- **Estructura:** 38 columnas; títulos exactos de cada columna usada (incluidas las dos con título duplicado); columnas que deben estar vacías.
- **Versiones del formulario:** se infieren con las columnas exclusivas de V2 y V3 (LEEME §2), se comprueba que sean sucesivas en el tiempo y que nadie responda una pregunta que no existía en su versión.
- **Catálogos:** cada respuesta cerrada se interpreta solo con las opciones de su versión. Una opción de otra versión, o texto no reconocido, detiene el análisis. Las equivalencias entre versiones están declaradas en el código (`HERRAMIENTAS`, `CANALES`), igual que en el LEEME §4.
- **Consentimiento:** se analizan solo los envíos con "Sí, acepto participar"; el envío sin consentimiento debe estar vacío.

## Salida
JSON en la salida estándar, **solo con agregados**: frecuencias, denominadores y porcentajes (redondeo a 0.1 por mitades hacia arriba). Para cada pregunta, el denominador distingue:
- `respondieron`;
- `omitidas`: la pregunta existía y se dejó en blanco;
- `ausentes_estructurales`: la pregunta no existía en esa versión;
- `indeterminadas`: no puede saberse si existía en esa versión.

Nunca se imprimen respuestas individuales, texto libre, marcas temporales ni filas. La ubicación se clasifica por regla, sin nombres de lugares. El script no escribe archivos.

## Limitaciones
- **No se reproducen automáticamente** los temas de texto libre: §5.2 (evidencia cualitativa de V1), §5.4 (texto libre), §5.7 (sugerencias), "3 informativas de 4", "7 proponen algo", y las precisiones de §5.3 sobre qué sistema pagan y la aclaración sobre comisiones. Son **codificación manual**; el script solo informa su `n` (`texto_libre_codificacion_manual`).
- Reglas sobre texto libre: "¿Usan estadísticas…?" y "¿Pagan alguna herramienta?" se clasifican por la **primera palabra** (sí/no). La disposición a pagar (Tabla 9) se clasifica con una regla explícita (`clasificar_pagaria`) que reproduce la lectura manual. Las menciones de V1 a diciembre, Semana Santa y septiembre son conteos por **palabra clave**; que septiembre aparezca como mes bajo se verificó leyendo.
- **Disponibilidad indeterminada:** en tres preguntas no se sabe si existían en V2 (`paga_herramienta`, `col21`, `deberia_ofrecer_texto`). El informe trató el vacío de V2 en "¿Pagan alguna herramienta?" como "sin respuesta"; el script lo reporta como `indeterminadas`. El denominador (`n = 9`) es el mismo.
- Las versiones y los catálogos son **inferidos** de las respuestas: una opción que nadie eligió no aparece en el catálogo.
