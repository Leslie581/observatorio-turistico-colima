> **GUÍA INTERNA SUPERADA (2026-11-10).** Documento de coordinación entre las integrantes; sus pendientes ya se atendieron o se actualizaron. El estado vigente está en [`docs/E0/ENTREGA.md`](docs/E0/ENTREGA.md) y en [`calidad/auditorias.md`](calidad/auditorias.md).

# Guía para cerrar E0: lo que te toca a ti

Corte: 2026-11-10. Repositorio: https://github.com/Leslie581/observatorio-turistico-colima (rama `main`, último commit al escribir esto: `12b1df8`).
Esta guía es práctica y va paso a paso. **Regla de oro: escribe solo lo que realmente pasó. No inventes entrevistas, tiempos, defectos ni auditorías.** Si algo no lo puedes respaldar, déjalo en blanco o como `_pendiente_`.

---

## 1. Qué ya está hecho y publicado en `main` (parte técnica de tu compañera/o A)

| Qué | Dónde |
|---|---|
| Estructura del Kit TDL y README | raíz del repositorio |
| Histórico: **108 meses** de Manzanillo (2016-01 a 2024-12), licencia CC BY 4.0, hash verificado | `data/bronce/datatur/` |
| Segunda fuente (DENUE, INEGI) capturada en GitHub Actions: 134 de 134 establecimientos, sin datos personales | `data/bronce/denue/`, `calidad/bitacora_capturas.jsonl` |
| Workflow de captura diaria (manual + programado) | `.github/workflows/captura-diaria.yml` |
| Propuesta E0 (preguntas E1/E2/E3, fuentes, limitaciones) **sin la entrevista** | `docs/E0/propuesta.md` |
| Ficha para los tres docentes | `docs/E0/ENTREGA.md` |
| Permisos y fuentes (DATATUR, DENUE) | `docs/fuentes/` |
| 3 objetivos de calidad medibles, riesgos e incidencias | `calidad/objetivos.md`, `calidad/riesgos.md` |
| PSP de A: 720 min **estimados retrospectivamente** y 11 defectos corregidos | `calidad/tiempo-integrante-a.csv`, `calidad/defectos-integrante-a.csv` |
| Lista de verificación de auditoría y registro de auditorías (vacío) | `calidad/lista_verificacion_auditoria.md`, `calidad/auditorias.md` |
| 87 pruebas automáticas (2 omitidas por requerir red) | `tests/` |

**Cifra honesta que no se debe maquillar:** la disponibilidad de la captura medida es **66.7 % (2 de 3)** frente al objetivo de **95 %**. Está documentada como "no cumplido todavía".

---

## 2. Lo que te falta a ti

| # | Tarea | Archivo | Estado |
|---|---|---|---|
| A | Registrar **tu entrevista** | `docs/E0/propuesta.md`, sección 8 | Pendiente |
| B | Tu **PSP individual** (tiempo y defectos) | `calidad/tiempo-integrante-b.csv`, `calidad/defectos-integrante-b.csv` | Plantillas vacías |
| C | **Auditoría cruzada** de la parte técnica de A | `calidad/auditorias.md` (+ lista de verificación) | Ninguna registrada |
| D | **Nombres** del equipo | `docs/E0/ENTREGA.md` línea 3 y `docs/E0/propuesta.md` línea 3 | Dicen `_integrantes por completar_` |
| E | **Responsable de revisión de calidad** de E0 | `calidad/revision_calidad.md` (tabla, fila E0) | `_por definir_` |

### A. La entrevista (`docs/E0/propuesta.md`, sección "8. Entrevista de validación")
El expediente exige: al menos **15 minutos**, con alguien del sector, **cinco preguntas**, las respuestas y lo que aprendieron.
Llena **las tres tablas de esa sección**:
1. **Datos de la entrevista:** entrevistado (solo rol y tipo de negocio; **sin nombre, teléfono ni correo** salvo que dé su permiso por escrito), fecha y duración reales, quién entrevistó y quién tomó notas, si autorizó que lo citen.
2. **Las 5 preguntas y respuestas.** Las preguntas de la tabla son un borrador sugerido: si hiciste otras, **reemplázalas por las que de verdad hiciste**. Resume las respuestas con fidelidad; usa citas textuales solo si hubo consentimiento.
3. **"Qué aprendimos / cómo cambia el alcance".** Si contradice alguna hipótesis de las secciones 1, 2 o 4 de la propuesta, ajusta esas secciones **solo en lo necesario** y avisa a A.
Al terminar, **cambia el título** de la sección 8 (quita "PENDIENTE DE INTEGRAR") y borra el aviso para quien integre. **No dejes texto inventado "de relleno".**

### B. Tu PSP (`calidad/`)
Formato del Kit (ya con la columna extra `minutos_estimados` al final):
- `tiempo-integrante-b.csv` → `fecha, inicio, fin, interrupcion_min, fase, actividad, minutos_estimados`
  - `fecha`: AAAA-MM-DD. `inicio`/`fin`: HH:MM (24 h), **solo si tienes el horario real**. `interrupcion_min`: minutos de pausa.
  - `fase`: planeacion, diseno, codigo, revision, pruebas, documentacion o entrevista.
  - Si **no** tienes horario y solo recuerdas la duración: deja `inicio`, `fin` e `interrupcion_min` **vacíos**, anota la duración en `minutos_estimados` y escribe `[ESTIMADO RETROSPECTIVO]` al principio de `actividad`. Así lo hizo A. **No inventes horarios.**
  - Registra **solo tu trabajo** y solo lo que puedas respaldar (tu entrevista, la redacción, tu auditoría).
- `defectos-integrante-b.csv` → `numero, fecha, tipo, fase_introducido, fase_eliminado, minutos_correccion, defecto_origen, descripcion`
  - `tipo`: documentacion, sintaxis, construccion, asignacion, interfaz, verificacion, datos, funcion, sistema o entorno.
  - Registra defectos **reales** que hayas encontrado o corregido tú. Si no hubo ninguno, **déjalo vacío**: cero defectos es válido.
  - `minutos_correccion`: solo si tienes una estimación defendible; si no, vacío.
  - Los riesgos y lo pendiente **no** son defectos: van en `calidad/riesgos.md`.
- **No renombres** estos archivos (`...-integrante-b.csv`): las pruebas automáticas y varios documentos dependen de esos nombres.
- La guía completa de columnas está en `calidad/README.md`.

### C. La auditoría cruzada de A (`calidad/auditorias.md`)
Auditarás los cambios técnicos de A. Como A los publicó **directamente en `main`**, tu auditoría es **posterior** y así debe quedar escrita (no como revisión previa a integrar).
1. Copia el bloque de `calidad/lista_verificacion_auditoria.md` y recórrelo **ejecutando** lo que dice (no solo leyendo). Comandos en la sección 5.
2. Revisa a fondo al menos: `extractores/captura_denue.py`, `extractores/denue.py` (qué campos se eliminan), `pipeline/verificar_e0.py`, `.github/workflows/captura-diaria.yml`, `docs/fuentes/datatur.md` y `docs/E0/ENTREGA.md`.
3. Anota **cada hallazgo** con severidad (crítico / mayor / menor), archivo y evidencia. Si no encuentras nada, escribe que no hubo hallazgos; **no inventes** hallazgos para que se vea trabajo.
4. Agrega **una fila** a la tabla de `calidad/auditorias.md` (conjunto de cambios, autora, auditora, tipo "posterior", fecha, hallazgos, correcciones, estado). A atenderá las correcciones; tú no editas su código.
5. **Tus** tiempos y defectos de revisión van en **tus** CSV (B). Los de corrección, en los de A. No se duplican.
6. Cuando termines tus cambios, avisa a A: **A debe auditar los tuyos** (entrevista, PSP, nombres), con la misma lista.

### D. Nombres
Reemplaza `_integrantes por completar_` en `docs/E0/ENTREGA.md` (línea 3) y en `docs/E0/propuesta.md` (línea 3). Pónganse de acuerdo en el formato.

### E. Responsable de revisión de calidad
En `calidad/revision_calidad.md`, fila **E0**: Quality Lead, quién fue revisado, fecha, resultado y evidencia (enlace al commit o al renglón de `auditorias.md`). **Llénala solo después de hacer la auditoría de C.** Si tú audita a A en esta entrega, tú eres la responsable de esa revisión.

---

## 3. Qué NO debes modificar (para no pisar el trabajo de A)
- `extractores/`, `pipeline/`, `tests/`, `.github/workflows/`, `requirements*.txt`, `pytest.ini`, `.gitignore`, `.gitattributes`.
- `data/` y `calidad/bitacora_capturas.jsonl` (los escribe el bot de GitHub Actions; no los edites a mano).
- `calidad/tiempo-integrante-a.csv`, `calidad/defectos-integrante-a.csv`, `calidad/psp-integrante-a-por-confirmar.md`.
- `calidad/objetivos.md` (la disponibilidad de 66.7 % no se retoca) y `calidad/riesgos.md`, salvo que de verdad detectes un riesgo nuevo (avisa a A).
- `docs/fuentes/` y `docs/E0/migracion.md`, `docs/E0/verificacion.md`.
- **Nunca** subas archivos `.env`, tokens ni datos del Sistema de Monitoreo Hotelero de DATATUR. **Nunca** uses `git push --force`.
- En `ENTREGA.md` y `propuesta.md` toca **solo** lo de las secciones A y D.

---

## 4. Configuración inicial (una sola vez, PowerShell)
```powershell
git clone https://github.com/Leslie581/observatorio-turistico-colima
cd observatorio-turistico-colima
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```
Necesitas ser **colaboradora** del repositorio (A debe invitarte desde GitHub: Settings → Collaborators).

## 5. Cómo verificar, hacer commit y publicar sin afectar a A
**Siempre empieza actualizando:**
```powershell
git pull --rebase origin main
```
(El bot de GitHub Actions sube capturas a `main` todos los días; por eso conviene actualizar antes de empezar y antes de publicar.)

**Trabaja** en tus archivos. Antes de hacer commit, **verifica**:
```powershell
.\.venv\Scripts\python.exe -m pytest -q -rs
.\.venv\Scripts\python.exe -m pipeline.verificar_e0
git status --short
git diff --check
```
Debe decir `87 passed, 2 skipped` (o más pasadas si A agregó pruebas) y el verificador sin fallos (`privacidad` y `historico` en `satisfactoria`). `git status --short` debe mostrar **solo tus archivos**. Revisa que no haya `.env` ni nombres/teléfonos del entrevistado.

**Commit y push** (mensajes en español, describe qué hiciste y quién):
```powershell
git add docs/E0/propuesta.md docs/E0/ENTREGA.md calidad/tiempo-integrante-b.csv calidad/defectos-integrante-b.csv calidad/auditorias.md calidad/revision_calidad.md
git commit -m "docs: registrar entrevista, PSP de la integrante B y auditoria de E0"
git pull --rebase origin main
git push origin main
```
(Haz `git add` solo de los archivos que realmente cambiaste. Puedes dividirlo en varios commits: entrevista, PSP, auditoría.)
Si `git push` es rechazado porque alguien subió algo, repite `git pull --rebase origin main` y vuelve a hacer `git push origin main`. Si aparece un **conflicto**, no lo resuelvas a ciegas: detente y avísale a A.

---

## 6. Qué queda por cerrar entre las dos
| # | Pendiente | Quién |
|---|---|---|
| 1 | Entrevista integrada en la propuesta (sección 8) | B |
| 2 | PSP de B con datos reales | B |
| 3 | Auditoría de B a la parte técnica de A, y auditoría de A a los cambios de B | B y A |
| 4 | Nombres en `ENTREGA.md` y `propuesta.md`; responsable de revisión de calidad | Las dos |
| 5 | Confirmar en GitHub (pestaña Actions) que las ejecuciones `42732765759`, `42733220215` y `42733335021` terminaron en verde | Las dos |
| 6 | Primera ejecución **programada** (`schedule`, ≈ 13:17 UTC / 07:17 hora local): comprobar que corrió sola (`"disparador": "schedule"` en la bitácora) y agregar su enlace a `ENTREGA.md` si ocurre | A |
| 7 | Comprobar que existe la variable `TDL_CONTACTO` en Settings → Secrets and variables → Actions | A |
| 8 | Agregar a los **tres docentes** como colaboradores del repositorio | A |
| 9 | Decisión sobre DATATUR 2025–2026 (ver `docs/fuentes/datatur.md`, sección 7); sin autorización no se automatiza ni se publica | Las dos |
| 10 | Revisar juntas `ENTREGA.md`: cada afirmación con evidencia; la disponibilidad dice 66.7 % frente a 95 %, sin afirmar cumplimiento | Las dos |
| 11 | Elegir la licencia del código | Las dos |
| 12 | Crear la etiqueta `e0` **solo al final**, cuando todo lo anterior esté hecho y verificado, y registrar el enlace en el formulario de entregas | A (o quien acuerden) |

> **Plazo:** el expediente fijaba E0 para el 6 de noviembre de 2026. Consulten con los docentes cómo se trata la entrega tardía (el expediente indica que lo que llegue después se evalúa sobre 70).
> **IA generativa:** el código y los borradores se prepararon con Claude Code (Anthropic). Cada una debe poder explicar y defender lo que entrega; la declaración ya está en `docs/E0/ENTREGA.md`.
