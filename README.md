# Observatorio de Ocupación Hotelera de Colima (Manzanillo)

Proyecto integrador **Trusted Data Lab** (Ingeniería de Datos · Análisis Estadístico para Ciencia de Datos · Calidad en los Sistemas de Información). Nombre comercial por definir («StayMetrics» fue solo el prototipo).

**Qué observa:** ocupación hotelera mensual de Manzanillo (SECTUR/DataTur, 2016–2024) y la oferta de hospedaje (INEGI, DENUE, captura diaria).
**Para quién:** propietarios, administradores, gerentes e inversionistas hoteleros (hipótesis por validar).
**Estado:** **E1 entregada** (etiqueta `e1` sobre `134c333`; no se mueve). Tablero: <https://tdl-turistico-colima.streamlit.app>. Las mejoras posteriores a la entrega viven en la rama `e1/mejoras-postentrega` y se describen en [`docs/E1/mejoras_postentrega.md`](docs/E1/mejoras_postentrega.md). Siguen vigentes las limitaciones declaradas: la disponibilidad de la captura (85.7 %, 6 de 7 ejecuciones) **no** alcanza el objetivo de 95 %, `main` **no** tiene protección de rama activada y no existe aún una copia externa del bronce.

## Documentación
| Documento | Contenido |
|---|---|
| [`docs/E1/ENTREGA.md`](docs/E1/ENTREGA.md) | Ficha de entrega de E1, con enlaces a evidencias |
| [`docs/relatoria-E1.md`](docs/relatoria-E1.md) | Relatoría (2 páginas): qué hicimos, tiempo por bloque, desviaciones y aprendizajes |
| [`docs/E1/evaluacion_rubrica.md`](docs/E1/evaluacion_rubrica.md) | Autoevaluación contra las tres rúbricas, con limitaciones |
| [`docs/E1/pipeline.md`](docs/E1/pipeline.md), [`contrato_datos.md`](docs/E1/contrato_datos.md) | Pipeline bronce → plata → oro, reglas de calidad y contrato de datos 1.0.0 |
| [`docs/E1/pronostico.md`](docs/E1/pronostico.md), [`exploracion.md`](docs/E1/exploracion.md) | Pronóstico, modelos y exploración |
| [`docs/E1/plan_sqa.md`](docs/E1/plan_sqa.md), [`seguridad.md`](docs/E1/seguridad.md), [`fiabilidad.md`](docs/E1/fiabilidad.md) | Plan de calidad (con las 12 desviaciones), seguridad y fiabilidad de la captura |
| [`calidad/`](calidad/README.md) | Registros PSP individuales, auditorías, riesgos, bitácora de capturas |
| [`docs/E0/`](docs/E0/ENTREGA.md), [`docs/fuentes/`](docs/fuentes/README.md) | Entrega E0, plan de recopilación y permisos de las fuentes |

## Estructura
```
.github/workflows/   ci.yml (pruebas, seguridad, dependencias) y captura-diaria.yml (DENUE: programada + manual)
.github/rulesets/    proteger-main.json (preparada, sin activar)
docs/                E0/, E1/ (entrega), fuentes/; E2/ a E4/ reservadas
calidad/             PSP (tiempo y defectos por integrante), auditorías, riesgos, bitácora de capturas
extractores/         captura ética de DENUE y DataTur
pipeline/            bronce → plata → oro con cuarentena, verificaciones y respaldo del bronce
data/                bronce/, plata/, oro/, cuarentena/
laboratorio/         pronosticos/, exploracion/, experimento/, encuesta_e0/
notebooks/           pronostico_e1.ipynb (reutiliza los módulos de laboratorio)
tablero/             tablero Streamlit
tests/               pytest
```

## Reproducir E1 desde una instalación limpia
Requisitos: Python 3.13 y Git. Los comandos de PowerShell (Windows); en Linux/macOS cambie `.\.venv\Scripts\python.exe` por `.venv/bin/python`. Son los mismos que ejecuta el CI.

```powershell
git clone https://github.com/Leslie581/tdl-turistico-colima ; cd tdl-turistico-colima
git checkout e1                                # la entrega; omita para la rama de trabajo
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-lab.txt -r requirements-dev.txt -r tablero/requirements.txt
```

**1. Pipeline de datos** (bronce → plata → oro; sale con código 2 si la puerta de calidad no deja una salida confiable) y verificación del oro contra el versionado:
```powershell
.\.venv\Scripts\python.exe -m pipeline.ejecutar
.\.venv\Scripts\python.exe -m pipeline.verificar_oro
.\.venv\Scripts\python.exe -m pipeline.verificar_e0 --solo historico --solo integridad --solo privacidad --exigir-datos
```

**2. Laboratorio** (pronósticos, exploración y, en la rama de mejoras, intervalos y ruido; escriben en `laboratorio/*/resultados/`):
```powershell
.\.venv\Scripts\python.exe -m laboratorio.pronosticos.ejecutar --fuente oro
.\.venv\Scripts\python.exe -m laboratorio.exploracion.explorar
.\.venv\Scripts\python.exe -m laboratorio.pronosticos.intervalos     # rama e1/mejoras-postentrega; ≈ 1 min
.\.venv\Scripts\python.exe -m laboratorio.exploracion.ruido          # rama e1/mejoras-postentrega
```

**3. Pruebas y calidad** (el CI exige cobertura ≥ 75 %):
```powershell
.\.venv\Scripts\python.exe -m ruff check .
$env:TDL_EXIGIR_PRONOSTICOS = "1" ; $env:TDL_EXIGIR_TABLERO = "1"     # sin estas variables, las pruebas que faltan de dependencias se omiten
.\.venv\Scripts\python.exe -m pytest -q -rs --cov=pipeline --cov=extractores --cov=laboratorio --cov=tablero --cov-fail-under=75
Remove-Item Env:\TDL_EXIGIR_PRONOSTICOS, Env:\TDL_EXIGIR_TABLERO
```

**4. Tablero** (<http://localhost:8501>):
```powershell
.\.venv\Scripts\python.exe -m streamlit run tablero/streamlit_app.py
```
Para instalar solo el tablero con el cierre exacto y *hashes*: `pip install --require-hashes -r tablero/requirements.lock.txt`.

**5. Captura DENUE real** (opcional; requiere un token gratuito de INEGI que no se sube a Git):
```powershell
Copy-Item .env.example .env ; notepad .env      # llenar INEGI_TOKEN y TDL_CONTACTO
.\.venv\Scripts\python.exe -m extractores.captura_denue                  # repetirla el mismo día no consulta la API; --forzar la repite
```
Solo `INEGI_TOKEN` y `TDL_CONTACTO` son configuración; **nunca** se versiona `.env`.

## Reglas del proyecto que el código aplica
Respeto a `robots.txt`; User-Agent identificable; pausa ≥ 1 s entre peticiones al mismo dominio; sin evadir bloqueos (un HTTP 403 se registra y no se elude); cero datos personales en bronce; datos con permiso incierto fuera del repositorio (ver `docs/fuentes/datatur.md`).

## Datos y licencias
- `data/bronce/datatur/Base70centros.csv`: SECTUR, **CC BY 4.0**, sin modificaciones ([atribución](data/bronce/datatur/LEEME.md)).
- DENUE: *Fuente: INEGI, DENUE*, términos de libre uso del INEGI, sin campos personales.
- Código: licencia por definir por el equipo.
- Declaración de IA generativa: ver [`docs/relatoria-E1.md`](docs/relatoria-E1.md) y [`docs/E0/ENTREGA.md`](docs/E0/ENTREGA.md).
