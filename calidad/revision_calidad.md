# Revisión de calidad compartida

Proceso de revisión cruzada y su registro: [`auditorias.md`](auditorias.md). Lista reutilizable: [`lista_verificacion_auditoria.md`](lista_verificacion_auditoria.md). Las auditorías de los primeros commits directos en `main` serán posteriores.

La calidad es obligación de los dos integrantes. En cada entrega uno actúa como **Quality Lead** y revisa el trabajo del otro con la lista de comprobación.

| Entrega | Quality Lead | Revisado | Fecha | Resultado | Evidencia |
|---|---|---|---|---|---|
| E0 | Sin Quality Lead único designado: cada integrante es responsable de la revisión del conjunto que auditó. Auditoría 1: Leslie Valadez Macias (integrante A). Auditoría 2: Eimy Melissa Urbina Meza (integrante B) | Auditoría 1: PR #1 de la integrante B (7 archivos). Auditoría 2: parte técnica de la integrante A (commits directos en `main`) | 2026-11-09 | Ambas **posteriores** a la integración; ambas con **correcciones solicitadas y sin aprobación plena** (A→B: 2 solicitar corrección, 3 aprobar con observaciones, 1 condicionada; B→A: 5 mayores y 13 menores, sin críticos). Parte de los hallazgos de ENTREGA y de la prueba de plantillas se atendió en `e0/cierre-final` | [Auditoría 1](auditorias.md#auditoría-1-pr-1-posterior-a-la-fusión) · [Auditoría 2](auditorias.md#auditoría-2-parte-técnica-de-a-auditoría-interna-posterior) |
| E1 | _se definirá en E1_ | | | | |

## Lista de comprobación E0
- [ ] `python -m pytest -q` pasa en una máquina limpia (README, "Reproducir").
- [ ] `python -m pipeline.verificar_e0 --solo historico --solo integridad --solo privacidad --exigir-datos` sin fallos (la disponibilidad se reporta aparte: O1 es un objetivo, hoy no cumplido, y no un control de aceptación).
- [ ] Ningún secreto en archivos preparados para commit (búsqueda de `INEGI_TOKEN=` con valor, `.env` ausente).
- [ ] Ningún dato del Sistema de Monitoreo (canal B) en `git ls-files`.
- [ ] Cada integrante tiene su registro de tiempo y de defectos con filas reales (no de ejemplo).
- [ ] `docs/E0/propuesta.md` y `docs/E0/ENTREGA.md` no afirman nada sin enlace a evidencia.
- [ ] La entrevista está registrada o marcada **PENDIENTE** sin datos inventados.
