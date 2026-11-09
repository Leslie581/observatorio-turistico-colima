"""Comprueba la ESTRUCTURA del workflow. No demuestra que funcione en GitHub: eso requiere una ejecución real."""
from pathlib import Path

import pytest
import yaml

RUTA = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "captura-diaria.yml"
INFORMATIVOS = {"disponibilidad"}  # pasos con continue-on-error que no deben fallar la ejecución


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


def test_los_pasos_obligatorios_con_continue_on_error_se_evaluan_al_final(pasos):
    final = pasos[-1]
    assert final["if"] == "always()"
    texto = str(final)
    obligatorios = [p["id"] for p in pasos if p.get("continue-on-error") and p["id"] not in INFORMATIVOS]
    assert set(obligatorios) == {"captura", "verificar"}
    for i in obligatorios:
        assert f"steps.{i}.outcome" in texto
    assert "exit 1" in final["run"]


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
