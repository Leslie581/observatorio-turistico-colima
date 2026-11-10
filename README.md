# Observatorio Turístico y Hotelero de Manzanillo, Colima

Proyecto integrador **TRUSTED DATA LAB** (Ingeniería de Datos · Análisis Estadístico para Ciencia de Datos · Calidad en los Sistemas de Información). Nombre comercial: por definir (“StayMetrics” fue solo el prototipo).

**Qué observa:** ocupación hotelera mensual de Manzanillo (SECTUR/DataTur, 2016–2024) y la oferta de hospedaje (INEGI, DENUE, captura diaria).
**Para quién:** propietarios, administradores, gerentes e inversionistas hoteleros (hipótesis por validar).
**Estado:** entrega **E0 en preparación**, ver [`docs/E0/ENTREGA.md`](docs/E0/ENTREGA.md) y lo pendiente en [`docs/E0/verificacion.md`](docs/E0/verificacion.md). No se ha creado la etiqueta `e0`. Sin tablero público todavía.

## Documentación
| Documento | Contenido |
|---|---|
| [`docs/E0/propuesta.md`](docs/E0/propuesta.md) | Propuesta (sector, pregunta, preguntas E1–E3, fuentes, limitaciones, entrevista de registro parcial y encuesta) |
| [`docs/E0/ENTREGA.md`](docs/E0/ENTREGA.md) | Ficha para los tres docentes, con enlaces a evidencia |
| [`docs/E0/verificacion.md`](docs/E0/verificacion.md) | Pruebas ejecutadas, estado de GitHub Actions y pasos para evidenciarlo |
| [`docs/E0/migracion.md`](docs/E0/migracion.md) | Qué se reutilizó del prototipo y qué no |
| [`docs/E0/issues_propuestos.md`](docs/E0/issues_propuestos.md) | Issues propuestos para E0 |
| [`docs/fuentes/`](docs/fuentes/README.md) | Plan de recopilación; permisos de DATATUR; DENUE |
| [`calidad/`](calidad/README.md) | Registros PSP individuales, objetivos de calidad, bitácora de capturas |

## Estructura
```
.github/workflows/   captura-diaria.yml (DENUE: programada + manual)
docs/                E0/ (entrega), fuentes/ (plan y permisos), E1/ .. E4/ (reservadas)
calidad/             registros de defectos y de tiempo (uno por integrante), objetivos, bitácora de capturas
extractores/         base.py (extractor ético), denue.py, datatur.py, captura_denue.py
pipeline/            verificar_e0.py (E0); bronce→plata→oro llegará en E1
data/                bronce/ (datatur, denue), plata/, oro/, cuarentena/
laboratorio/         encuesta_e0/ (análisis de la encuesta) y notebooks (E1–E3)
tablero/             tablero (E4)
tests/               pytest
requirements.in / requirements.txt   dependencias (fijadas)
```
**Diferencias con el Kit oficial:** se conservan los nombres del Kit (`docs/`, `calidad/`, `extractores/`, `pipeline/`, `data/{bronce,plata,oro,cuarentena}`, `laboratorio/`, `tablero/`, `tests/`, `.github/workflows/`). Añadidos: `docs/fuentes/` (plan de recopilación y análisis de permisos), `pytest.ini`, `requirements.in`, `.gitattributes` (conserva byte a byte los datos). El Kit nombra la raíz `tdl-<equipo>/`; aquí es el nombre del repositorio. El flujo de integración continua del Kit es de E1 y no existe todavía. Las carpetas aún sin uso llevan `.gitkeep`.

## Reproducir (PowerShell, Windows)
```powershell
git clone https://github.com/Leslie581/observatorio-turistico-colima ; cd observatorio-turistico-colima
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Pruebas y verificaciones (sin red)
.\.venv\Scripts\python.exe -m pytest -q -rs
.\.venv\Scripts\python.exe -m pipeline.verificar_e0

# Captura DENUE real (requiere token gratuito de INEGI; no se sube a Git)
Copy-Item .env.example .env ; notepad .env      # llenar INEGI_TOKEN y TDL_CONTACTO
.\.venv\Scripts\python.exe -m extractores.captura_denue
# Repetirla el mismo día no consulta la API; --forzar la repite

# Pruebas con red (opcional)
$env:TDL_RED = "1" ; .\.venv\Scripts\python.exe -m pytest -q -rs tests\test_integracion_red.py ; Remove-Item Env:\TDL_RED
```
Solo `INEGI_TOKEN` y `TDL_CONTACTO` son configuración; **nunca** se versiona `.env`.

## Reglas del proyecto que el código aplica
Respeto a `robots.txt`; User-Agent identificable; pausa ≥ 1 s entre peticiones al mismo dominio; sin evadir bloqueos (un HTTP 403 se registra y no se elude); cero datos personales en bronce; datos con permiso incierto fuera del repositorio (ver `docs/fuentes/datatur.md`).

## Datos y licencias
- `data/bronce/datatur/Base70centros.csv`: SECTUR, **CC BY 4.0**, sin modificaciones ([atribución](data/bronce/datatur/LEEME.md)).
- DENUE: *Fuente: INEGI, DENUE*, términos de libre uso del INEGI, sin campos personales.
- Código: licencia por definir por el equipo.
- Declaración de IA generativa: ver `docs/E0/ENTREGA.md`.
