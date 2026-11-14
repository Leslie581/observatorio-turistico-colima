"""Estructura de ci.yml y garantía de que la captura diaria NO depende de las librerías opcionales del laboratorio.

Comprueba la ESTRUCTURA de los archivos; no demuestra que el flujo funcione en GitHub (eso exige una ejecución real).
"""
import importlib.util
import re
from pathlib import Path

import pytest
import yaml

RAIZ = Path(__file__).resolve().parent.parent
CI = RAIZ / ".github" / "workflows" / "ci.yml"
CAPTURA = RAIZ / ".github" / "workflows" / "captura-diaria.yml"


def _carga(ruta):
    return yaml.safe_load(ruta.read_text(encoding="utf-8"))


def _comandos(wf, job):
    return "\n".join(p.get("run", "") for p in wf["jobs"][job]["steps"])


def test_ci_corre_en_cada_push_y_pull_request_con_permisos_minimos():
    wf = _carga(CI)
    assert set(wf.get("on", wf.get(True))) == {"push", "pull_request"}
    assert wf["permissions"] == {"contents": "read"}
    assert "secrets." not in CI.read_text(encoding="utf-8").replace("# ", "")  # sin secretos


def test_ci_exige_las_pruebas_de_pronosticos_y_corre_linter_pruebas_y_puerta_de_datos():
    wf = _carga(CI)
    assert wf["jobs"]["calidad"]["env"]["TDL_EXIGIR_PRONOSTICOS"] == "1"
    cmd = _comandos(wf, "calidad")
    for esperado in ("-r requirements-lab.txt", "ruff check", "pytest -q -rs", "pipeline.ejecutar", "pipeline.verificar_e0"):
        assert esperado in cmd, esperado
    assert cmd.index("ruff check") < cmd.index("pytest") < cmd.index("pipeline.ejecutar")
    assert not any(p.get("continue-on-error") for p in wf["jobs"]["calidad"]["steps"])  # un cambio que rompe algo no entra


def test_la_auditoria_de_dependencias_va_aparte_y_no_bloquea_el_job_de_calidad():
    wf = _carga(CI)
    assert "pip_audit" in _comandos(wf, "auditoria-dependencias") and "pip_audit" not in _comandos(wf, "calidad")


def test_ci_comprueba_que_el_oro_regenerado_coincide_con_el_versionado_despues_de_regenerarlo():
    wf = _carga(CI)
    pasos = wf["jobs"]["calidad"]["steps"]
    cmds = [p.get("run", "") for p in pasos]
    i_regenera = next(i for i, c in enumerate(cmds) if "pipeline.ejecutar" in c)
    i_compara = next(i for i, c in enumerate(cmds) if "pipeline.verificar_oro" in c)
    assert i_regenera < i_compara, "se compara DESPUÉS de regenerar el oro"
    assert not pasos[i_compara].get("continue-on-error") and not pasos[i_compara].get("if")  # corre siempre y bloquea


def test_cada_modulo_python_que_invoca_ci_existe():
    """Un `python -m pipeline.x` con un módulo inexistente haría fallar el CI en GitHub; se detecta aquí, antes de publicar."""
    cmd = " ".join(_comandos(_carga(CI), j) for j in _carga(CI)["jobs"])
    modulos = set(re.findall(r"python -m ([\w.]+)", cmd)) - {"pip", "pytest", "ruff", "pip_audit"}
    assert {"pipeline.ejecutar", "pipeline.verificar_oro", "pipeline.verificar_e0"} <= modulos
    for m in modulos:
        assert importlib.util.find_spec(m) is not None, f"CI invoca un módulo inexistente: {m}"


def test_los_archivos_de_requisitos_que_instala_ci_existen():
    cmd = " ".join(_comandos(_carga(CI), j) for j in _carga(CI)["jobs"])
    archivos = set(re.findall(r"-r (requirements[\w.-]*\.txt)", cmd))
    assert {"requirements.txt", "requirements-lab.txt", "requirements-dev.txt"} <= archivos
    for a in archivos:
        assert (RAIZ / a).is_file(), a


def test_la_exigencia_de_pruebas_estadisticas_no_se_anula_en_ningun_paso():
    """TDL_EXIGIR_PRONOSTICOS vale "1" en el job y ningún paso lo redefine (un paso podría desactivarla en silencio)."""
    wf = _carga(CI)
    assert wf["jobs"]["calidad"]["env"]["TDL_EXIGIR_PRONOSTICOS"] == "1"
    assert not any("TDL_EXIGIR_PRONOSTICOS" in p.get("env", {}) or "TDL_EXIGIR_PRONOSTICOS" in p.get("run", "")
                   for p in wf["jobs"]["calidad"]["steps"])
    assert "TDL_EXIGIR_PRONOSTICOS" not in str(wf["jobs"]["auditoria-dependencias"])


def test_el_ci_pasa_el_oro_a_la_comprobacion_sin_exigir_metadatos_con_hora():
    """Propiedad de la comprobación que invoca ci.yml: ignora los campos de tiempo y la oferta que crece a diario."""
    from pipeline import verificar_oro as v

    assert set(v.CAMPOS_VARIABLES_META) == {"fecha_proceso_utc", "corrida"}
    assert all(r.endswith(".csv") for r in v.ESTRICTOS) and not any("oferta" in r for r in (*v.ESTRICTOS, v.META))


def test_la_captura_diaria_no_instala_las_dependencias_opcionales_del_laboratorio():
    wf = _carga(CAPTURA)
    cmd = _comandos(wf, "capturar")
    assert "-r requirements.txt" in cmd
    assert "requirements-lab" not in cmd and "requirements-dev" not in cmd and "TDL_EXIGIR_PRONOSTICOS" not in str(wf)


def test_el_nucleo_de_requirements_no_incluye_librerias_del_laboratorio():
    nucleo = (RAIZ / "requirements.txt").read_text(encoding="utf-8").lower()
    for opcional in ("statsmodels", "scipy", "matplotlib", "ruff", "pip-audit"):
        assert f"\n{opcional}==" not in nucleo
    assert "\npandera==" in nucleo and "\npandas==" in nucleo


@pytest.mark.parametrize("archivo", ["requirements-lab.txt", "requirements-dev.txt"])
def test_dependencias_opcionales_estan_fijadas_con_version_exacta(archivo):
    lineas = [x for x in (RAIZ / archivo).read_text(encoding="utf-8").splitlines() if x and not x.startswith("#")]
    assert lineas and all("==" in x for x in lineas)


# ---------------------------------------------------------------- tablero, auditoría con transitivas y gitleaks (cierre de E1)
def test_ci_instala_las_dependencias_del_tablero_y_exige_sus_pruebas():
    wf = _carga(CI)
    cmd = _comandos(wf, "calidad")
    assert "-r tablero/requirements.txt" in cmd and (RAIZ / "tablero" / "requirements.txt").is_file()
    assert cmd.index("-r tablero/requirements.txt") < cmd.index("pytest")                      # se instala antes de las pruebas
    assert wf["jobs"]["calidad"]["env"]["TDL_EXIGIR_TABLERO"] == "1"                          # sin las dependencias, FALLA (no se omite)
    assert not any("TDL_EXIGIR_TABLERO" in p.get("env", {}) or "TDL_EXIGIR_TABLERO" in p.get("run", "")
                   for p in wf["jobs"]["calidad"]["steps"])                                   # ningún paso la anula
    assert "TDL_EXIGIR_TABLERO" not in str(wf["jobs"]["auditoria-dependencias"]) and "TDL_EXIGIR_TABLERO" not in str(wf["jobs"]["secretos"])


def test_la_cache_de_pip_cubre_los_requisitos_del_tablero():
    pasos = _carga(CI)["jobs"]["calidad"]["steps"]
    rutas = next(p["with"]["cache-dependency-path"] for p in pasos if p.get("uses", "").startswith("actions/setup-python"))
    assert {"requirements*.txt", "tablero/requirements.txt"} <= set(rutas.split())


def test_la_auditoria_cubre_el_tablero_con_su_bloqueo_y_con_las_transitivas_resueltas():
    wf = _carga(CI)
    audit = [p["run"] for p in wf["jobs"]["auditoria-dependencias"]["steps"] if "pip_audit" in p.get("run", "")]
    assert len(audit) == 3
    fijadas, bloqueo, resueltas = audit
    for archivo in ("requirements.txt", "requirements-lab.txt", "requirements-dev.txt"):
        assert f"-r {archivo}" in fijadas
    assert "--no-deps" in fijadas                                                              # listas ya congeladas con su cierre
    assert "-r tablero/requirements.lock.txt" in bloqueo and "--require-hashes" in bloqueo      # el cierre EXACTO, con hashes
    assert "-r tablero/requirements.txt" in resueltas and "--no-deps" not in resueltas         # lo que podría instalar Streamlit Cloud hoy
    assert not any(p.get("continue-on-error") for p in wf["jobs"]["auditoria-dependencias"]["steps"])


def test_el_bloqueo_del_tablero_se_instala_con_hashes_obligatorios_en_ci():
    wf = _carga(CI)
    cmd = _comandos(wf, "bloqueo-tablero")
    assert "--require-hashes -r tablero/requirements.lock.txt" in cmd and "pip check" in cmd
    assert (RAIZ / "tablero" / "requirements.lock.txt").is_file()
    assert not any(p.get("continue-on-error") for p in wf["jobs"]["bloqueo-tablero"]["steps"])


def test_gitleaks_corre_en_ci_con_binario_fijado_y_verificado():
    wf = _carga(CI)
    job = wf["jobs"]["secretos"]
    assert wf["permissions"] == {"contents": "read"} and "permissions" not in job              # solo lectura, heredado
    assert job["steps"][0]["with"]["fetch-depth"] == 0                                         # historial completo
    cmd = _comandos(wf, "secretos")
    assert "gitleaks/releases/download/v8.30.1/" in cmd and "gitleaks_8.30.1_linux_x64.tar.gz" in cmd
    assert re.search(r"echo \"[0-9a-f]{64}  gitleaks\.tgz\" \| sha256sum -c -", cmd)           # hash verificado antes de extraer
    assert cmd.index("sha256sum -c") < cmd.index("tar xzf")
    assert "git ." in cmd and "--log-opts=\"--all\"" in cmd and "--redact" in cmd              # historial completo, sin imprimir valores
    assert not any(p.get("continue-on-error") for p in job["steps"])                           # un hallazgo rompe el CI
    assert all(p.get("uses", "actions/").startswith("actions/") for p in job["steps"])         # sin acciones de terceros


def test_el_hash_de_gitleaks_coincide_con_el_documentado():
    hash_ci = re.search(r"echo \"([0-9a-f]{64})  gitleaks\.tgz\"", _comandos(_carga(CI), "secretos")).group(1)
    seguridad = (RAIZ / "docs" / "E1" / "seguridad.md").read_text(encoding="utf-8")
    assert hash_ci in seguridad                                                                # un solo valor, el de la release verificada


# ---------------------------------------------------------------- acciones fijadas por SHA de commit (cierre de E1)
SHAS_VERIFICADOS = {   # tag -> commit; verificados el 2026-11-14 con `git ls-remote` y con la API de GitHub (commits con firma verificada)
    "actions/checkout": ("11d5960a326750d5838078e36cf38b85af677262", "v4.4.0"),
    "actions/setup-python": ("a26af69be951a213d495a4c3e4e4022e16d87065", "v5.6.0"),
    "actions/upload-artifact": ("ea165f8d65b6e75b540449e92b4886f43607fa02", "v4.6.2"),
}


def _usos(ruta):
    return re.findall(r"^\s*-?\s*uses:\s*(\S+)\s*(?:#\s*(\S+))?\s*$", ruta.read_text(encoding="utf-8"), flags=re.M)


@pytest.mark.parametrize("ruta", [CI, CAPTURA], ids=["ci.yml", "captura-diaria.yml"])
def test_toda_accion_esta_fijada_por_sha_de_commit_verificado(ruta):
    usos = _usos(ruta)
    assert usos, "el flujo no usa acciones"
    for accion, comentario in usos:
        nombre, _, ref = accion.partition("@")
        assert re.fullmatch(r"[0-9a-f]{40}", ref), f"{accion}: no está fijada por SHA (una etiqueta puede moverse)"
        assert nombre in SHAS_VERIFICADOS and SHAS_VERIFICADOS[nombre] == (ref, comentario), f"{accion} # {comentario}: SHA o versión no verificados"


def test_ninguna_accion_de_terceros_y_el_workflow_no_usa_etiquetas_moviles():
    for ruta in (CI, CAPTURA):
        texto = ruta.read_text(encoding="utf-8")
        assert not re.search(r"uses:\s*\S+@v\d", texto)                                   # ni @v4 ni @v5
        assert all(a.startswith("actions/") for a, _ in _usos(ruta))                       # solo acciones oficiales de GitHub


def test_las_pruebas_miden_cobertura_con_un_piso_y_pytest_cov_esta_fijado():
    cmd = _comandos(_carga(CI), "calidad")
    assert "--cov-fail-under=75" in cmd and all(f"--cov={m}" in cmd for m in ("pipeline", "extractores", "laboratorio", "tablero"))
    assert cmd.index("pytest") < cmd.index("pipeline.ejecutar")
    assert "\npytest-cov==" in (RAIZ / "requirements.txt").read_text(encoding="utf-8")


def test_ci_no_deja_el_token_guardado_en_git_config():
    """Mínimo permiso: ci.yml solo lee, así que ninguna llamada a checkout persiste las credenciales."""
    wf = _carga(CI)
    assert wf["permissions"] == {"contents": "read"}
    checkouts = [p for j in wf["jobs"].values() for p in j["steps"] if p.get("uses", "").startswith("actions/checkout@")]
    assert len(checkouts) == 4 and all(p["with"]["persist-credentials"] is False for p in checkouts)
    assert not [j for j in wf["jobs"].values() if "permissions" in j]                       # ningún trabajo amplía los permisos


def test_la_captura_diaria_conserva_solo_el_permiso_de_escritura_que_necesita():
    wf = _carga(CAPTURA)
    assert wf["permissions"] == {"contents": "write"}                                       # el bot guarda la bitácora y el bronce
    texto = CAPTURA.read_text(encoding="utf-8")
    assert texto.count("secrets.") == 1 and "secrets.INEGI_TOKEN" in texto                  # un solo secreto, el del extractor


def test_la_accion_correctiva_de_revision_recíproca_esta_preparada_en_el_repositorio():
    """Plantilla de PR con la lista de revisión y CODEOWNERS con las dos integrantes; la protección de `main` requiere administración."""
    plantilla = (RAIZ / ".github" / "pull_request_template.md").read_text(encoding="utf-8")
    for exigido in ("no** fusiona", "antes** de fusionar", "calidad/auditorias.md", "PSP", "secretos"):
        assert exigido in plantilla, exigido
    owners = [x for x in (RAIZ / ".github" / "CODEOWNERS").read_text(encoding="utf-8").splitlines() if x.strip() and not x.startswith("#")]
    assert owners == ["*  @Leslie581 @eimymuz"]
