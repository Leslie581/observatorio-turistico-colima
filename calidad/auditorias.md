# Registro de auditorías cruzadas

Proceso acordado:
1. Cuando A termina sus cambios, B los audita; cuando B termina los suyos, A los audita.
2. Quien audita documenta los hallazgos y es la responsable de revisión de calidad de ese conjunto de cambios.
3. La autora atiende las correcciones.
4. Cada quien registra **sus propios** tiempos y defectos (los de revisión los registra quien revisa; los de corrección, la autora). Un mismo defecto/tiempo no se registra dos veces.
5. Integración final con evidencia de revisión, preferentemente un pull request cuando se trabaje en ramas.
6. Los primeros commits directos en `main` se auditan **después** de integrarse; se anota como "auditoría posterior" y **no** se presenta como revisión previa.

Usar [`lista_verificacion_auditoria.md`](lista_verificacion_auditoria.md). No se llenan aprobaciones ni firmas hasta que ocurra la auditoría real.

| # | Conjunto de cambios | Autora | Auditora | Tipo (posterior / PR) | Fecha | Hallazgos | Correcciones (commit) | Estado |
|---|---|---|---|---|---|---|---|---|
| _ninguna registrada_ | | | | | | | | |
