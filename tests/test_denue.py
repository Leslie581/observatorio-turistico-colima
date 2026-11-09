import pytest

from extractores import denue

# Registros SINTÉTICOS con los nombres de campo documentados por INEGI.
SINTETICOS = [
    {"CLEE": "A1", "Id": "1", "Nombre": "HOTEL PRUEBA", "Razon_social": "PERSONA X",
     "Clase_actividad": "Hoteles con otros servicios integrados", "Estrato": "11 a 30 personas",
     "Telefono": "3140000000", "Correo_e": "x@y.mx", "Latitud": "19.05", "Longitud": "-104.31",
     "Ubicacion": "MANZANILLO, Manzanillo, COLIMA"},
    {"CLEE": "A2", "Id": "2", "Nombre": "RESTAURANTE", "Clase_actividad": "Restaurantes a la carta",
     "Estrato": "0 a 5 personas", "Latitud": "19.06", "Longitud": "-104.30"},
    {"CLEE": "A3", "Id": "3", "Nombre": "CABANAS LEJOS", "Clase_actividad": "Cabañas, villas y similares",
     "Estrato": "0 a 5 personas", "Latitud": "25.0", "Longitud": "-100.0"},
    {"CLEE": "A1", "Id": "1", "Nombre": "HOTEL PRUEBA", "Clase_actividad": "Hoteles con otros servicios integrados",
     "Estrato": "11 a 30 personas", "Latitud": "19.05", "Longitud": "-104.31"},
]


def test_normalizar_filtra_y_protege_privacidad():
    v, q = denue.normalizar(SINTETICOS)
    assert list(v.clee) == ["A1"]
    assert not {"telefono", "correo_e", "razon_social"} & set(v.columns)
    motivos = ";".join(q.motivo_rechazo)
    assert "clase_fuera_de_catalogo" in motivos and "coordenadas_fuera_de_colima" in motivos
    assert "duplicado" in motivos
    assert bool(v.comparable_datatur.iloc[0])


def test_resumen_no_asigna_ocupacion_individual():
    v, _ = denue.normalizar(SINTETICOS)
    r = denue.resumen_agregado(v)
    assert r["establecimientos"] == 1 and "ocupacion" not in str(r).lower()
    assert r["personal_ocupado_min"] == 11


def test_token_obligatorio(monkeypatch):
    monkeypatch.delenv("INEGI_TOKEN", raising=False)
    with pytest.raises(denue.TokenNoConfigurado):
        denue._token()


def test_token_enmascarado():
    assert "SECRETO" not in denue._enmascarar("https://x/Ficha/1/SECRETO", "SECRETO")


# --- Respuesta cruda, errores y controles (sin red; formas documentadas) -----
def test_respuesta_no_lista_se_rechaza():
    assert denue.interpretar_respuesta(b"") == []
    assert denue.interpretar_respuesta(b'[{"Id": "1"}]') == [{"Id": "1"}]
    for malo in (b"<html>error</html>", b'{"error": "token invalido"}'):
        with pytest.raises(denue.RespuestaDenueInvalida):
            denue.interpretar_respuesta(malo)


def test_total_cuantificar():
    assert denue.total_cuantificar([{"AE": "721", "AG": "06007", "Total": "312"}]) == 312
    assert denue.total_cuantificar({"error": "x"}) is None


def test_validar_detecta_duplicados_y_completitud():
    v, q = denue.normalizar(SINTETICOS)
    r = denue.validar(SINTETICOS, v, q, esperado=3)
    controles = {c["control"]: c for c in r["controles"]}
    assert not controles["duplicados"]["ok"] and controles["duplicados"]["valor"] == 1
    assert controles["completitud_vs_cuantificar"]["ok"]  # 3 únicos / 3 esperados
    assert not r["ok"]


def test_respuestas_crudas_se_guardan_intactas_y_sin_token(tmp_path):
    from extractores.base import Bitacora, ExtractorEtico, Respuesta, sha256_bytes
    cuerpo = b'[{"AE":"721","AG":"06007","Total":"1"}]'

    class Ex(ExtractorEtico):
        def get(self, url, **kw):
            return Respuesta(url, 200, cuerpo, "application/json", sha256_bytes(cuerpo), 0.1, {})

    cli = denue.ClienteDenue(Ex(bitacora=Bitacora(tmp_path / "b.jsonl")), token="SECRETO123")
    assert denue.total_cuantificar(cli.cuantificar()) == 1
    rutas = denue.guardar_respuestas_crudas(cli, "T1", bronce=tmp_path)
    assert rutas[0].read_bytes() == cuerpo
    meta = (str(rutas[0]) + ".meta.json")
    assert "SECRETO123" not in open(meta, encoding="utf-8").read()

