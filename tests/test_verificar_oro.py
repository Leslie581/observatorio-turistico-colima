"""Comprobación «oro regenerado == oro versionado» (pipeline/verificar_oro.py).

Las pruebas con repositorios git temporales son SINTÉTICAS y lo declaran; la última usa el bronce real y el oro versionado real
(copiados a una carpeta temporal: no se escribe en data/).
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from pipeline import verificar_oro as v
from pipeline.ejecutar import ejecutar

RAIZ = Path(__file__).resolve().parent.parent
BRONCE = RAIZ / "data" / "bronce"
META_EJEMPLO = {"archivo": "x.csv", "filas": 108, "sha256_csv": "aa", "sha256_bronce": "bb", "ejecucion": "oro-bb-v1.0.0",
                "corrida": "e1-111111111111", "fecha_proceso_utc": "2026-11-13T00:00:00+00:00", "version_contrato": "1.0.0"}


def _git(raiz, *args):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", "-C", str(raiz), *args],
                   check=True, capture_output=True)


def _repo(tmp_path, meta=None):
    """SINTÉTICO: repositorio git con un oro versionado mínimo."""
    raiz = tmp_path / "repo"
    (raiz / "data" / "oro").mkdir(parents=True)
    (raiz / "data/oro/manzanillo_ocupacion_mensual.csv").write_bytes(b"periodo,ocupacion_pct\n2016-01,48.35\n")
    (raiz / "data/oro/diccionario_datos.csv").write_bytes(b"columna,descripcion\nocupacion_pct,x\n")
    (raiz / "data/oro/manzanillo_ocupacion_mensual.meta.json").write_text(json.dumps(meta or META_EJEMPLO), encoding="utf-8")
    (raiz / "data/oro/manzanillo_oferta_hospedaje.csv").write_bytes(b"dia,n\n2026-11-09,134\n")
    (raiz / "data/oro/manzanillo_oferta_hospedaje.meta.json").write_text("{}", encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(raiz)], check=True)
    _git(raiz, "add", "-A")
    _git(raiz, "commit", "-q", "-m", "oro")
    return raiz


def test_oro_sin_cambios_coincide(tmp_path):
    r = v.comparar(_repo(tmp_path))
    assert r["ok"] and r["diferencias"] == [] and v.NO_COMPARADOS[0] in r["no_comparados"]


def test_un_valor_distinto_en_el_csv_se_detecta(tmp_path):
    raiz = _repo(tmp_path)
    (raiz / "data/oro/manzanillo_ocupacion_mensual.csv").write_bytes(b"periodo,ocupacion_pct\n2016-01,48.36\n")
    r = v.comparar(raiz)
    assert not r["ok"] and r["diferencias"][0]["archivo"].endswith("manzanillo_ocupacion_mensual.csv")


def test_un_cambio_en_el_diccionario_se_detecta(tmp_path):
    raiz = _repo(tmp_path)
    (raiz / "data/oro/diccionario_datos.csv").write_bytes(b"columna,descripcion\nocupacion_pct,otra\n")
    assert [d["archivo"] for d in v.comparar(raiz)["diferencias"]] == ["data/oro/diccionario_datos.csv"]


def test_la_marca_de_tiempo_y_la_corrida_de_los_metadatos_no_cuentan(tmp_path):
    raiz = _repo(tmp_path)
    nuevo = dict(META_EJEMPLO, fecha_proceso_utc="2030-01-01T00:00:00+00:00", corrida="e1-999999999999")
    (raiz / "data/oro/manzanillo_ocupacion_mensual.meta.json").write_text(json.dumps(nuevo), encoding="utf-8")
    assert v.comparar(raiz)["ok"]


def test_un_campo_estable_de_los_metadatos_distinto_si_cuenta(tmp_path):
    raiz = _repo(tmp_path)
    nuevo = dict(META_EJEMPLO, sha256_csv="zz", fecha_proceso_utc="2030-01-01T00:00:00+00:00")
    (raiz / "data/oro/manzanillo_ocupacion_mensual.meta.json").write_text(json.dumps(nuevo), encoding="utf-8")
    d = v.comparar(raiz)["diferencias"]
    assert len(d) == 1 and d[0]["campos"] == ["sha256_csv"]


def test_la_oferta_denue_no_se_exige_porque_crece_con_las_capturas_diarias(tmp_path):
    raiz = _repo(tmp_path)
    (raiz / "data/oro/manzanillo_oferta_hospedaje.csv").write_bytes(b"dia,n\n2026-11-09,134\n2026-11-10,134\n")
    (raiz / "data/oro/manzanillo_oferta_hospedaje.meta.json").write_text('{"filas": 2}', encoding="utf-8")
    assert v.comparar(raiz)["ok"]


def test_archivo_no_regenerado_o_no_versionado_es_diferencia(tmp_path):
    raiz = _repo(tmp_path)
    (raiz / "data/oro/diccionario_datos.csv").unlink()
    assert "no lo regeneró" in v.comparar(raiz)["diferencias"][0]["motivo"]
    sin_git = tmp_path / "otro"
    (sin_git / "data" / "oro").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(sin_git)], check=True)
    _git(sin_git, "commit", "-q", "--allow-empty", "-m", "vacio")
    assert all("no está versionado" in d["motivo"] for d in v.comparar(sin_git)["diferencias"])


@pytest.mark.datos
@pytest.mark.skipif(not (BRONCE / "datatur" / "Base70centros.csv").exists(), reason="sin bronce")
def test_con_datos_reales_el_oro_regenerado_coincide_con_el_versionado(tmp_path):
    """Bronce real + oro versionado real, en una copia: regenerar el oro y compararlo con lo versionado."""
    raiz = tmp_path / "copia"
    shutil.copytree(BRONCE, raiz / "data" / "bronce")
    shutil.copytree(RAIZ / "data" / "oro", raiz / "data" / "oro")
    subprocess.run(["git", "init", "-q", str(raiz)], check=True)
    _git(raiz, "add", "data/oro")
    _git(raiz, "commit", "-q", "-m", "oro versionado")
    assert ejecutar(raiz, ahora="2030-01-01T00:00:00+00:00")["estado"] == "ok"  # otra hora: no debe importar
    r = v.comparar(raiz)
    assert r["ok"], r["diferencias"]
    # y si el código produjera otro oro, el CI fallaría: se altera una celda del versionado y se vuelve a comparar
    csv = raiz / "data/oro/manzanillo_ocupacion_mensual.csv"
    csv.write_bytes(csv.read_bytes().replace(b"2016-01,2016-01-01,48.359551", b"2016-01,2016-01-01,48.359552", 1))
    assert not v.comparar(raiz)["ok"]


# ---------------------------------------------------------------- dimensiones de las jerarquías conceptuales (SINTÉTICAS)
def test_las_dimensiones_aun_no_versionadas_se_informan_como_pendientes_y_no_como_diferencia(tmp_path):
    raiz = _repo(tmp_path)
    (raiz / "data/oro/dim_tiempo.csv").write_bytes(b"periodo\n2016-01\n")          # existe en el área de trabajo, no en el commit
    r = v.comparar(raiz)
    assert r["ok"] and "data/oro/dim_tiempo.csv" not in [d["archivo"] for d in r["diferencias"]]
    assert set(r["pendientes_de_versionar"]) == set(v.ESTRICTOS_SI_VERSIONADOS)


def test_una_dimension_versionada_se_compara_byte_a_byte_y_si_falta_es_diferencia(tmp_path):
    raiz = _repo(tmp_path)
    for n in ("dim_tiempo.csv", "dim_geografia.csv"):
        (raiz / "data/oro" / n).write_bytes(b"a,b\n1,2\n")
    _git(raiz, "add", "-A")
    _git(raiz, "commit", "-q", "-m", "dimensiones")
    assert v.comparar(raiz)["ok"] and v.comparar(raiz)["pendientes_de_versionar"] == []
    (raiz / "data/oro/dim_tiempo.csv").write_bytes(b"a,b\n1,3\n")
    assert [d["archivo"] for d in v.comparar(raiz)["diferencias"]] == ["data/oro/dim_tiempo.csv"]
    (raiz / "data/oro/dim_tiempo.csv").write_bytes(b"a,b\n1,2\n")
    (raiz / "data/oro/dim_geografia.csv").unlink()
    d = v.comparar(raiz)["diferencias"]
    assert [x["archivo"] for x in d] == ["data/oro/dim_geografia.csv"] and "no lo regeneró" in d[0]["motivo"]
