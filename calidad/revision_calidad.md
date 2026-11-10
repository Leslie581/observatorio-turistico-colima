# Revisión de calidad compartida

Proceso de revisión cruzada y su registro: [`auditorias.md`](auditorias.md). Lista reutilizable: [`lista_verificacion_auditoria.md`](lista_verificacion_auditoria.md). Las auditorías de los primeros commits directos en `main` serán posteriores.

La calidad es obligación de los dos integrantes. En cada entrega uno actúa como **Quality Lead** y revisa el trabajo del otro con la lista de comprobación.

| Entrega | Quality Lead | Revisado | Fecha | Resultado | Evidencia |
|---|---|---|---|---|---|
| E0 | Integrante A (`Leslie581`), para el conjunto del PR #1 | Trabajo de la integrante B (`eimymuz`): PR #1, 7 archivos | 2026-11-09 | Correcciones solicitadas; revisión **posterior** a la fusión; sin aprobación plena. La auditoría recíproca (B revisa a A) sigue pendiente | [Auditoría 1 en `auditorias.md`](auditorias.md#auditoría-1-pr-1-posterior-a-la-fusión) |
| E1 | _por definir_ | | | | |

## Lista de comprobación E0
- [ ] `python -m pytest -q` pasa en una máquina limpia (README, "Reproducir").
- [ ] `python -m pipeline.verificar_e0` sin fallos.
- [ ] Ningún secreto en archivos preparados para commit (búsqueda de `INEGI_TOKEN=` con valor, `.env` ausente).
- [ ] Ningún dato del Sistema de Monitoreo (canal B) en `git ls-files`.
- [ ] Cada integrante tiene su registro de tiempo y de defectos con filas reales (no de ejemplo).
- [ ] `docs/E0/propuesta.md` y `docs/E0/ENTREGA.md` no afirman nada sin enlace a evidencia.
- [ ] La entrevista está registrada o marcada **PENDIENTE** sin datos inventados.
