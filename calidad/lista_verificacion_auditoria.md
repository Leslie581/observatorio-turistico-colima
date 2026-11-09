# Lista de verificación de auditoría cruzada (reutilizable)

Copiar el bloque a un issue o a `auditorias.md` por cada conjunto de cambios. Marcar solo lo que se comprobó; lo no comprobado se deja vacío o con "N/A" y motivo.

```
Conjunto de cambios (commits/PR): ______   Autora: ______   Auditora: ______   Fecha: ______
Tipo: [ ] commits directos en main (auditoría POSTERIOR)  [ ] pull request (revisión previa a integrar)

Funcionalidad
[ ] Hace lo que dice el issue/criterio de aceptación (probado ejecutándolo, no solo leyéndolo)
[ ] Manejo de errores: fallos de red/403/429/sin token terminan en error registrado, sin datos parciales silenciosos
[ ] Respeta robots.txt, pausa >= 1 s, User-Agent honesto; no evade bloqueos
Pruebas
[ ] `python -m pytest -q` pasa en entorno limpio; hay pruebas para lo nuevo
[ ] `python -m pipeline.verificar_e0` sin fallos
Documentación
[ ] README/docs actualizados; sin afirmaciones sin evidencia; hipótesis marcadas como tales
[ ] Estados correctos: VERIFICADO / IMPLEMENTADO SIN PROBAR / DOCUMENTADO / PENDIENTE
Trazabilidad
[ ] Cada archivo de bronce con .meta.json y SHA-256 coincidente; fuente, fecha y licencia citadas
[ ] Commits atribuidos a quien los hizo; registros PSP de esta actividad hechos por cada quien (sin duplicar)
Seguridad y ética
[ ] Sin secretos, .env ni tokens en archivos ni historial; logs sin credenciales
[ ] Sin datos personales en bronce; sin datos de permiso incierto (canal B de DATATUR) en Git
Cumplimiento E0
[ ] Los criterios de docs/E0/ENTREGA.md afectados siguen siendo ciertos
Hallazgos (uno por línea: severidad crítico/mayor/menor, archivo, descripción, evidencia): ______
Resultado: [ ] sin hallazgos  [ ] correcciones requeridas  -> atendidas en commit: ______
```
