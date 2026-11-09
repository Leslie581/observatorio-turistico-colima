# Objetivos de calidad (E0) — alimentan el plan SQA de E1

Cada objetivo tiene métrica, umbral, fuente de datos y forma de verificar. Se evalúan con la bitácora de capturas de la semana del 9 al 13 de noviembre (E1) y se revisan en E2.

| ID | Objetivo | Métrica y umbral | Cómo se mide | Estado hoy |
|---|---|---|---|---|
| **O1** | **Disponibilidad de la captura programada** | Ejecuciones exitosas / ejecuciones exitosas + fallidas ≥ **95 %** en cualquier ventana de 7 días. Se excluyen las omitidas por duplicado. | `python -m pipeline.verificar_e0 --solo disponibilidad` sobre `calidad/bitacora_capturas.jsonl`; MTBF, MTTR y disponibilidad formal en E1 | PENDIENTE (sin ejecuciones reales) |
| **O2** | **Completitud e integridad de lo capturado** | (a) Registros únicos del DENUE / total de `Cuantificar` entre 0.98 y 1.02 en el 100 % de las capturas exitosas. (b) 100 % de los archivos de bronce con `.meta.json` cuyo SHA-256 y tamaño coinciden. | (a) control `completitud_vs_cuantificar` registrado en la bitácora; (b) `python -m pipeline.verificar_e0 --solo integridad` | (b) VERIFICADO hoy para Base70; (a) PENDIENTE |
| **O3** | **Cero datos personales y defectos trazables** | (a) 0 campos personales o de domicilio (teléfono, correo, sitio web, razón social, calle y números) en `data/bronce/`. (b) 100 % de los defectos registrados con tipo PSP, fase de origen, fase de remoción y minutos; sin filas vacías. | (a) `python -m pipeline.verificar_e0 --solo privacidad`; (b) revisión del Quality Lead sobre los CSV de `calidad/` | (a) PENDIENTE: sin archivos DENUE reales, el verificador devuelve `sin_datos`; (b) PENDIENTE |

Justificación de pertinencia: O1 es el ejemplo del propio Kit y sustenta la medición de fiabilidad de E1; O2 protege la serie y el pronóstico de datos corruptos o incompletos; O3 cumple la regla de ética (LFPDPPP) y el registro PSP.
Los umbrales se fijan hoy y **no se ajustan después de ver los resultados** sin dejar constancia en el registro de cambios.
