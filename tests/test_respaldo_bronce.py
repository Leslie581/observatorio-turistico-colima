"""Respaldo de la capa bronce con manifiesto SHA-256 y restauración (pipeline/respaldo.py).

Las pruebas con un bronce de juguete son SINTÉTICAS y lo declaran; las de «real» usan el bronce versionado SOLO de lectura
y escriben únicamente en carpetas temporales. Ninguna prueba toca ``data/bronce``.
"""
import json
import zipfile
from pathlib import Path

import pytest

from pipeline import respaldo as r
from pipeline.verificar_e0 import integridad

RAIZ = Path(__file__).resolve().parent.parent
BRONCE = RAIZ / "data" / "bronce"
MANIFIESTO_VERSIONADO = RAIZ / "calidad" / "evidencia" / "bronce-manifiesto-20261114.json"
con_bronce = pytest.mark.skipif(not (BRONCE / "datatur" / "Base70centros.csv").exists(), reason="sin bronce")


@pytest.fixture
def juguete(tmp_path):
    """SINTÉTICO: un bronce mínimo de tres archivos en dos carpetas."""
    b = tmp_path / "bronce"
    (b / "denue" / "2026-11-09").mkdir(parents=True)
    (b / "datatur").mkdir()
    (b / "datatur" / "a.csv").write_bytes(b"periodo,x\n2016-01,1\n")
    (b / "denue" / "2026-11-09" / "b.json").write_bytes(b'[{"id": 1}]')
    (b / "denue" / "2026-11-09" / "b.json.meta.json").write_bytes(b'{"sha256": "x"}')
    return b


def _hashes(carpeta: Path) -> dict:
    return {p.relative_to(carpeta).as_posix(): r.sha256_archivo(p) for p in sorted(carpeta.rglob("*")) if p.is_file()}


# ------------------------------------------------------------------ ida y vuelta (SINTÉTICAS)
def test_el_manifiesto_lista_cada_archivo_con_tamano_y_sha256(juguete):
    m = r.generar_manifiesto(juguete)
    assert [e["ruta"] for e in m["archivos"]] == ["datatur/a.csv", "denue/2026-11-09/b.json", "denue/2026-11-09/b.json.meta.json"]
    assert m["total_archivos"] == 3 and m["total_bytes"] == sum(e["bytes"] for e in m["archivos"])
    assert all(len(e["sha256"]) == 64 for e in m["archivos"]) and m["algoritmo"] == "sha256"


def test_crear_verificar_y_restaurar_devuelve_los_mismos_bytes(juguete, tmp_path):
    antes = _hashes(juguete)
    res = r.crear_respaldo(juguete, tmp_path / "respaldo", "bronce")
    assert r.verificar_respaldo(res["zip"], res["manifiesto"]) == {"ok": True, "archivos": 3, "fallos": []}
    rest = r.restaurar(res["zip"], res["manifiesto"], tmp_path / "restaurado", juguete)
    assert rest["ok"] and rest["restaurados"] == 3
    assert _hashes(tmp_path / "restaurado") == antes                                      # bytes idénticos a los originales
    assert _hashes(juguete) == antes                                                      # el original no se tocó


def test_el_zip_es_determinista(juguete, tmp_path):
    a = r.crear_respaldo(juguete, tmp_path / "a", "bronce")
    b = r.crear_respaldo(juguete, tmp_path / "b", "bronce")
    assert a["zip"].read_bytes() == b["zip"].read_bytes()
    assert json.loads(a["manifiesto"].read_text("utf-8"))["zip"]["sha256"] == r.sha256_archivo(a["zip"])


# ------------------------------------------------------------------ detección de daños (SINTÉTICAS)
def test_un_zip_alterado_se_detecta_y_no_se_restaura(juguete, tmp_path):
    res = r.crear_respaldo(juguete, tmp_path / "respaldo", "bronce")
    datos = bytearray(res["zip"].read_bytes())
    datos[len(datos) // 2] ^= 0xFF                                                        # un byte cambiado
    res["zip"].write_bytes(bytes(datos))
    try:
        v = r.verificar_respaldo(res["zip"], res["manifiesto"])
    except zipfile.BadZipFile:
        v = {"ok": False}
    assert v["ok"] is False
    with pytest.raises((r.ErrorRespaldo, zipfile.BadZipFile)):
        r.restaurar(res["zip"], res["manifiesto"], tmp_path / "restaurado", juguete)
    assert not (tmp_path / "restaurado").exists() or not any((tmp_path / "restaurado").iterdir())


def test_un_manifiesto_con_un_hash_distinto_o_un_archivo_de_mas_se_detecta(juguete, tmp_path):
    res = r.crear_respaldo(juguete, tmp_path / "respaldo", "bronce")
    m = json.loads(res["manifiesto"].read_text("utf-8"))
    m["archivos"][0]["sha256"] = "0" * 64
    falso = tmp_path / "falso.json"
    falso.write_text(json.dumps(m), encoding="utf-8")
    v = r.verificar_respaldo(res["zip"], falso)
    assert not v["ok"] and any("distinto" in f["motivo"] for f in v["fallos"])
    m2 = json.loads(res["manifiesto"].read_text("utf-8"))
    m2["archivos"].append({"ruta": "falta.csv", "bytes": 1, "sha256": "1" * 64})
    otro = tmp_path / "otro.json"
    otro.write_text(json.dumps(m2), encoding="utf-8")
    assert any(f["motivo"] == "falta en el zip" for f in r.verificar_respaldo(res["zip"], otro)["fallos"])


def test_un_zip_con_un_archivo_no_declarado_se_detecta(juguete, tmp_path):
    res = r.crear_respaldo(juguete, tmp_path / "respaldo", "bronce")
    with zipfile.ZipFile(res["zip"], "a") as z:
        z.writestr("intruso.txt", "x")
    v = r.verificar_respaldo(res["zip"], res["manifiesto"])
    assert not v["ok"] and any("no declara" in f["motivo"] for f in v["fallos"])


# ------------------------------------------------------------------ seguridad de la operación (SINTÉTICAS)
def test_no_sobrescribe_un_respaldo_existente(juguete, tmp_path):
    r.crear_respaldo(juguete, tmp_path / "respaldo", "bronce")
    with pytest.raises(r.ErrorRespaldo, match="no se sobrescribe"):
        r.crear_respaldo(juguete, tmp_path / "respaldo", "bronce")


def test_no_restaura_sobre_una_carpeta_con_archivos_ni_dentro_del_bronce(juguete, tmp_path):
    res = r.crear_respaldo(juguete, tmp_path / "respaldo", "bronce")
    ocupada = tmp_path / "ocupada"
    ocupada.mkdir()
    (ocupada / "dato.txt").write_text("importante", encoding="utf-8")
    with pytest.raises(r.ErrorRespaldo, match="no está vacío"):
        r.restaurar(res["zip"], res["manifiesto"], ocupada, juguete)
    assert (ocupada / "dato.txt").read_text(encoding="utf-8") == "importante"
    with pytest.raises(r.ErrorRespaldo, match="dentro ni contener"):
        r.restaurar(res["zip"], res["manifiesto"], juguete / "datatur", juguete)
    with pytest.raises(r.ErrorRespaldo, match="dentro ni contener"):
        r.crear_respaldo(juguete, juguete / "copia", "bronce")


def test_un_zip_con_ruta_que_sale_de_la_carpeta_se_rechaza(tmp_path):
    zip_malo, man = tmp_path / "malo.zip", tmp_path / "malo.json"
    with zipfile.ZipFile(zip_malo, "w") as z:
        z.writestr("../fuera.txt", "x")
    import hashlib
    man.write_text(json.dumps({"algoritmo": "sha256", "archivos": [{"ruta": "../fuera.txt", "bytes": 1, "sha256": hashlib.sha256(b"x").hexdigest()}]}), encoding="utf-8")
    with pytest.raises(r.ErrorRespaldo, match="peligrosa"):
        r.restaurar(zip_malo, man, tmp_path / "destino", tmp_path / "bronce_inexistente")
    assert not (tmp_path / "fuera.txt").exists()


def test_bronce_vacio_o_inexistente_no_se_respalda(tmp_path):
    with pytest.raises(r.ErrorRespaldo):
        r.generar_manifiesto(tmp_path / "no_existe")
    (tmp_path / "vacio").mkdir()
    with pytest.raises(r.ErrorRespaldo, match="nada que respaldar"):
        r.generar_manifiesto(tmp_path / "vacio")


# ------------------------------------------------------------------ con el bronce REAL (solo lectura)
@con_bronce
def test_prueba_de_restauracion_con_el_bronce_real_en_un_directorio_temporal():
    antes = _hashes(BRONCE)
    res = r.probar(BRONCE)
    assert res["ok"] is True and res["archivos"] >= 28
    assert res["verificacion_del_zip"] and res["restauracion"] and res["restaurado_igual_al_manifiesto"] and res["bronce_igual_al_manifiesto"]
    assert _hashes(BRONCE) == antes                                                       # el bronce original no cambió ni un byte


@con_bronce
def test_el_manifiesto_coincide_con_las_fichas_de_integridad_del_bronce():
    """Dos fuentes independientes de hash: el manifiesto y los .meta.json que escribió el extractor."""
    m = r.generar_manifiesto(BRONCE)
    por_ruta = {e["ruta"]: e["sha256"] for e in m["archivos"]}
    assert integridad(BRONCE)["ok"] is True
    for ficha in BRONCE.rglob("*.meta.json"):
        datos = ficha.relative_to(BRONCE).as_posix()[: -len(".meta.json")]
        assert por_ruta[datos] == json.loads(ficha.read_text(encoding="utf-8"))["sha256"], datos


@con_bronce
def test_el_manifiesto_versionado_sigue_valiendo_aunque_el_bot_agregue_capturas():
    """El bronce solo crece: todo lo declarado el 2026-11-14 conserva su SHA-256; lo nuevo son capturas posteriores."""
    assert MANIFIESTO_VERSIONADO.is_file()
    v = r.comparar_con_origen(MANIFIESTO_VERSIONADO, BRONCE)
    assert v["ok"] is True and v["modificados"] == [] and v["ausentes"] == []
    m = json.loads(MANIFIESTO_VERSIONADO.read_text(encoding="utf-8"))
    assert m["total_archivos"] == 28 and any(e["ruta"] == "datatur/Base70centros.csv" for e in m["archivos"])
    assert not any(k in json.dumps(m) for k in ("Users", "Leslie", "@"))                    # sin rutas privadas ni correos


# ------------------------------------------------------------------ línea de comandos
def test_la_linea_de_comandos_crea_verifica_y_restaura(juguete, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(r, "BRONCE", juguete)
    destino = tmp_path / "copia"
    assert r.main(["crear", "--destino", str(destino), "--nombre", "t"]) == 0
    assert r.main(["verificar", "--zip", str(destino / "t.zip"), "--manifiesto", str(destino / "t.manifiesto.json")]) == 0
    assert r.main(["restaurar", "--zip", str(destino / "t.zip"), "--manifiesto", str(destino / "t.manifiesto.json"), "--destino", str(tmp_path / "rest")]) == 0
    assert _hashes(tmp_path / "rest") == _hashes(juguete)
    assert r.main(["crear", "--destino", str(destino), "--nombre", "t"]) == 2                 # no sobrescribe: error controlado
    assert '"ok": false' in capsys.readouterr().out.lower() or "no se sobrescribe" in capsys.readouterr().out


def test_la_linea_de_comandos_prueba_la_restauracion_completa(juguete, monkeypatch, capsys):
    monkeypatch.setattr(r, "BRONCE", juguete)
    assert r.main(["probar"]) == 0
    assert '"ok": true' in capsys.readouterr().out
