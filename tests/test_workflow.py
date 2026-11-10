"""Comprueba la ESTRUCTURA del workflow. No demuestra que funcione en GitHub: eso requiere una ejecución real."""
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

RUTA = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "captura-diaria.yml"


@pytest.fixture(scope="module")
def wf():
    return yaml.safe_load(RUTA.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def pasos(wf):
    return wf["jobs"]["capturar"]["steps"]


def _por_id(pasos, i):
    return next(p for p in pasos if p.get("id") == i)


def test_disparadores_y_permisos(wf):
    on = wf.get("on", wf.get(True))
    assert set(on) == {"schedule", "workflow_dispatch"}
    assert on["schedule"][0]["cron"].count(" ") == 4
    assert wf["permissions"] == {"contents": "write"}
    assert wf["concurrency"]["cancel-in-progress"] is False
    assert wf["defaults"]["run"]["shell"] == "bash"


def test_solo_captura_denue_nunca_datatur(pasos):
    comandos = "\n".join(p.get("run", "") for p in pasos).replace("pipeline.verificar_e0", "")
    assert "extractores.captura_denue" in comandos
    for prohibido in ("monitoreo", "Ajax", "datatur", "extractores.main"):
        assert prohibido not in comandos


def test_token_solo_en_el_paso_de_captura_y_nunca_se_imprime(wf, pasos):
    for p in pasos:
        if p.get("id") == "captura":
            assert "INEGI_TOKEN" in p["env"]
        else:
            assert "INEGI_TOKEN" not in str(p.get("env", {})) and "INEGI_TOKEN" not in p.get("run", "")
    assert "INEGI_TOKEN" not in str(wf["jobs"]["capturar"].get("env", {}))
    assert "secrets." not in "\n".join(p.get("run", "") for p in pasos)


def test_todo_paso_con_continue_on_error_se_evalua_en_el_paso_final(pasos):
    final = pasos[-1]
    assert final["if"] == "always()"
    ids = [p["id"] for p in pasos if p.get("continue-on-error")]
    assert set(ids) == {"captura", "verificar", "disponibilidad"}
    for i in ids:
        assert f"steps.{i}.outcome" in str(final)
    assert "exit 1" in final["run"]


def test_disponibilidad_es_informativa_pero_no_oculta_errores_tecnicos(pasos):
    d = _por_id(pasos, "disponibilidad")
    assert "--informativo" in d["run"] and "logs/disponibilidad.json" in d["run"]
    verificar = _por_id(pasos, "verificar")
    assert "--informativo" not in verificar["run"] and "--exigir-datos" in verificar["run"]  # la obligatoria sigue bloqueante


def test_el_resumen_muestra_si_el_objetivo_se_cumple(pasos):
    r = next(p for p in pasos if p.get("name") == "Resumen de la ejecución")
    assert "objetivo_cumplido" in r["run"] and "NO CUMPLIDO" in r["run"] and "ERROR TÉCNICO" in r["run"]


@pytest.mark.skipif(shutil.which("bash") is None, reason="sin bash")
@pytest.mark.parametrize("captura,verificar,disponibilidad,sale_en_rojo", [
    ("success", "success", "success", False),   # disponibilidad 50 % con captura válida: el verificador salió 0
    ("failure", "success", "success", True),    # fallo real de captura
    ("success", "failure", "success", True),    # fallo de la verificación obligatoria
    ("success", "success", "failure", True),    # error técnico del verificador de disponibilidad
    ("skipped", "success", "success", True),
])
def test_logica_real_del_paso_final(pasos, captura, verificar, disponibilidad, sale_en_rojo):
    # Las variables van dentro del script (no por entorno): en Windows `bash` puede ser el de WSL y no las hereda.
    exportar = f'export R_CAPTURA={captura} R_VERIFICAR={verificar} R_DISPONIBILIDAD={disponibilidad}\n'
    # bytes con LF: en Windows el modo texto convertiría a CRLF y bash fallaría con `fi`
    r = subprocess.run(["bash", "-e"], input=(exportar + pasos[-1]["run"]).encode("utf-8"), capture_output=True)
    r.stdout, r.stderr = r.stdout.decode("utf-8", "replace"), r.stderr.decode("utf-8", "replace")
    assert f"captura={captura} verificacion={verificar}" in r.stdout  # el script vio los valores
    assert (r.returncode != 0) is sale_en_rojo, r.stdout + r.stderr


def test_la_evidencia_se_guarda_antes_del_paso_final(pasos):
    usos = [p.get("uses", "") for p in pasos]
    i_art = next(i for i, u in enumerate(usos) if u.startswith("actions/upload-artifact"))
    assert pasos[i_art]["if"] == "always()" and i_art < len(pasos) - 1
    assert "logs/bitacora.jsonl" in pasos[i_art]["with"]["path"]
    assert "logs/verificacion.json" in pasos[i_art]["with"]["path"]


def test_el_bronce_solo_se_publica_si_la_verificacion_paso(pasos):
    guardar = next(p for p in pasos if "Guardar bit" in p.get("name", ""))
    assert guardar["if"] == "always()"
    assert "steps.verificar.outcome" in str(guardar["env"])
    run = guardar["run"]
    assert run.index('"$R_VERIFICAR" = "success"') < run.index("git add data/bronce/denue")
    assert run.count("git add data/bronce/denue") == 1


def test_la_verificacion_exige_datos(pasos):
    v = _por_id(pasos, "verificar")
    for texto in ("--exigir-datos", "privacidad", "integridad", "historico"):
        assert texto in v["run"]


def test_las_pruebas_listan_omitidas(pasos):
    p = next(p for p in pasos if p.get("name") == "Pruebas sin red")
    assert "-rs" in p["run"]
