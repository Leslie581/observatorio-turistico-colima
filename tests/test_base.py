import json
import urllib.robotparser

import pytest

from extractores.base import Bitacora, ExtractorEtico, guardar_bronce, sha256_bytes


def test_pausa_minima_regla_tdl(tmp_path):
    with pytest.raises(ValueError):
        ExtractorEtico(bitacora=Bitacora(tmp_path / "b.jsonl"), pausa=0.5)


def test_reintentos_limitados(tmp_path):
    ex = ExtractorEtico(bitacora=Bitacora(tmp_path / "b.jsonl"), intentos=50)
    assert ex.intentos == 5


def test_robots_bloquea_ruta_prohibida_y_registra(tmp_path):
    bit = Bitacora(tmp_path / "b.jsonl")
    ex = ExtractorEtico(bitacora=bit)
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(["User-agent: *", "Disallow: /Reportes/"])
    ex.robots["https://ejemplo.gob.mx"] = rp
    assert ex.permitido("https://ejemplo.gob.mx/datos.csv")
    with pytest.raises(PermissionError):
        ex.get("https://ejemplo.gob.mx/Reportes/Menu.aspx")
    eventos = [json.loads(l)["evento"] for l in (tmp_path / "b.jsonl").read_text().splitlines()]
    assert "bloqueado_robots" in eventos


def test_dominio_inalcanzable_no_reintenta_robots(tmp_path):
    ex = ExtractorEtico(bitacora=Bitacora(tmp_path / "b.jsonl"))
    ex.inalcanzables["https://caido.gob.mx"] = "ProxyError"
    with pytest.raises(ConnectionError):
        ex.permitido("https://caido.gob.mx/x")


def test_user_agent_identificable(tmp_path, monkeypatch):
    monkeypatch.setenv("TDL_CONTACTO", "equipo@ejemplo.mx")
    ex = ExtractorEtico(bitacora=Bitacora(tmp_path / "b.jsonl"))
    assert "ObservatorioHotelero" in ex.sesion.headers["User-Agent"]
    assert "equipo@ejemplo.mx" in ex.sesion.headers["User-Agent"]


def test_guardar_bronce_idempotente_y_versiona(tmp_path):
    a = guardar_bronce(b"uno", "f", "x.csv", {"url": "u"}, bronce=tmp_path)
    b = guardar_bronce(b"uno", "f", "x.csv", {"url": "u"}, bronce=tmp_path)
    assert a == b and len(list((tmp_path / "f").glob("x*.csv"))) == 1
    c = guardar_bronce(b"dos", "f", "x.csv", {"url": "u"}, bronce=tmp_path)
    assert c != a and c.exists()
    meta = json.loads((str(c) + ".meta.json") and open(str(c) + ".meta.json").read())
    assert meta["sha256"] == sha256_bytes(b"dos") and meta["url"] == "u"


def test_bronce_misma_huella_registra_captura_y_promueve_a_oficial(tmp_path):
    a = guardar_bronce(b"datos", "f", "x.csv", {"url": "copia", "origen": "espejo_no_oficial"}, bronce=tmp_path)
    b = guardar_bronce(b"datos", "f", "x.csv", {"url": "oficial", "origen": "oficial",
                                                "estado_http": 200}, bronce=tmp_path)
    assert a == b and len(list((tmp_path / "f").glob("x*.csv"))) == 1
    meta = json.loads(open(str(a) + ".meta.json", encoding="utf-8").read())
    assert meta["origen"] == "oficial" and meta["url"] == "oficial"
    assert meta["procedencia_anterior"]["url"] == "copia"  # la evidencia previa se conserva
    assert [c["origen"] for c in meta["capturas"]] == ["espejo_no_oficial", "oficial"]


def test_bitacora_oculta_token_en_urls_y_errores(tmp_path, monkeypatch):
    token = "11111111-2222-3333-4444-555555555555"
    monkeypatch.setenv("INEGI_TOKEN", token)
    b = Bitacora(tmp_path / "segura.jsonl")
    b.registrar("http", url="https://www.inegi.org.mx/app/api/denue/v1/consulta/Cuantificar/721/06007/0/" + token,
               error="fallo con " + token)
    salida = (tmp_path / "segura.jsonl").read_text(encoding="utf8")
    assert token not in salida and "***TOKEN***" in salida
