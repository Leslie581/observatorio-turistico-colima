"""Pruebas sin red de la captura diaria y de la sanitización de datos personales."""
import json
from datetime import datetime, timezone

from extractores import captura_denue, denue
from extractores.base import Bitacora, ExtractorEtico, Respuesta, sha256_bytes

CUANT = b'[{"AE":"721","AG":"06007","Total":"2"}]'


def _registro(i, **extra):
    r = {"CLEE": f"0600772111100052300{i}", "Id": str(100 + i), "Nombre": f"HOTEL {i}",
         "Razon_social": f"PERSONA FISICA {i}", "Clase_actividad": "Hoteles sin otros servicios integrados",
         "Estrato": "11 a 30 personas", "CLASE_ACTIVIDAD_ID": "721112", "Telefono": "3140000000",
         "Correo_e": f"h{i}@ejemplo.mx", "Sitio_internet": "www.ejemplo.mx",
         "Longitud": "-104.32", "Latitud": "19.09",
         "Calle": "OLAS ALTAS", "Num_Exterior": "14", "Num_Interior": "2", "EDIFICIO": "", "numero_local": "",
         "AGEB": "0329", "Colonia": "PLAYA AZUL"}
    r.update(extra)
    return r


BUSCAR = json.dumps([_registro(1), _registro(2)], ensure_ascii=False).encode("utf-8")


class ExFalso(ExtractorEtico):
    """Responde sin red: Cuantificar -> total 2; BuscarAreaAct -> dos registros."""
    def __init__(self, *a, falla=None, **kw):
        super().__init__(*a, **kw)
        self.falla, self.llamadas = falla, []

    def get(self, url, **kw):
        self.llamadas.append(url)
        if self.falla:
            raise RuntimeError(self.falla.replace("{url}", url))
        cuerpo = CUANT if "Cuantificar" in url else BUSCAR
        return Respuesta(url, 200, cuerpo, "application/json", sha256_bytes(cuerpo), 0.01, {})


def _correr(tmp_path, monkeypatch, ahora, forzar=False, token="TOKEN-DE-PRUEBA-123", **kw):
    if token:
        monkeypatch.setenv("INEGI_TOKEN", token)
    else:
        monkeypatch.delenv("INEGI_TOKEN", raising=False)
    ex = ExFalso(bitacora=Bitacora(tmp_path / "http.jsonl"), **kw)
    fila = captura_denue.ejecutar(forzar=forzar, bronce=tmp_path / "data" / "bronce",
                                  bitacora_ejecuciones=tmp_path / "ej.jsonl",
                                  bitacora_http=tmp_path / "http.jsonl", ex=ex, ahora=ahora)
    return fila, ex


AHORA = datetime(2026, 11, 10, 15, 0, tzinfo=timezone.utc)  # 09:00 en Ciudad de México


def test_sanitizar_elimina_campos_personales_y_conserva_el_resto():
    cuerpo, info = denue.sanitizar_crudo(BUSCAR)
    datos = json.loads(cuerpo)
    assert len(datos) == 2
    assert not {k.lower() for r in datos for k in r} & {"telefono", "correo_e", "sitio_internet", "razon_social"}
    assert "Nombre" not in datos[0] and datos[0]["CLEE"] and datos[0]["Id"]
    assert info["campos_personales_eliminados"] == ["Correo_e", "Nombre", "Razon_social", "Sitio_internet", "Telefono"]
    assert info["campos_domicilio_eliminados"] == ["Calle", "EDIFICIO", "Num_Exterior", "Num_Interior", "numero_local"]
    assert {"Latitud", "Longitud", "AGEB", "Colonia", "Estrato", "CLASE_ACTIVIDAD_ID"} <= set(datos[0])
    assert "Calle" not in datos[0]
    assert info["registros_con_campos_eliminados"] == 2


def test_sanitizar_no_toca_respuestas_sin_campos_personales():
    cuerpo, info = denue.sanitizar_crudo(CUANT)
    assert cuerpo == CUANT and info["campos_personales_eliminados"] == []


def test_captura_exitosa_escribe_bronce_sin_datos_personales_y_registra(tmp_path, monkeypatch):
    fila, _ = _correr(tmp_path, monkeypatch, AHORA)
    assert fila["resultado"] == "exito" and fila["registros"] == 2 and fila["esperado_cuantificar"] == 2
    crudos = list((tmp_path / "data" / "bronce" / "denue" / "2026-11-10").glob("*_BuscarAreaAct.json"))
    assert len(crudos) == 1
    texto = crudos[0].read_text(encoding="utf-8").lower()
    assert "telefono" not in texto and "correo_e" not in texto and "persona fisica" not in texto and "hotel 1" not in texto
    assert "olas altas" not in texto and "num_exterior" not in texto
    meta = json.loads((crudos[0].parent / (crudos[0].name + ".meta.json")).read_text(encoding="utf-8"))
    assert meta["sha256_respuesta_original"] == sha256_bytes(BUSCAR)
    assert meta["sha256"] == sha256_bytes(crudos[0].read_bytes())
    assert "TOKEN-DE-PRUEBA-123" not in json.dumps(meta)
    linea = (tmp_path / "ej.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(linea) == 1 and json.loads(linea[0])["resultado"] == "exito"


def test_no_duplica_captura_del_mismo_dia(tmp_path, monkeypatch):
    _correr(tmp_path, monkeypatch, AHORA)
    fila, ex = _correr(tmp_path, monkeypatch, AHORA.replace(hour=20))
    assert fila["resultado"] == "omitida_duplicada" and ex.llamadas == []
    fila3, ex3 = _correr(tmp_path, monkeypatch, AHORA.replace(hour=21), forzar=True)
    assert fila3["resultado"] == "exito" and len(ex3.llamadas) == 2


def test_dia_local_no_utc(tmp_path, monkeypatch):
    # 03:00 UTC del 11 aún es 21:00 del día 10 en Ciudad de México
    assert captura_denue.fecha_local(datetime(2026, 11, 11, 3, 0, tzinfo=timezone.utc)) == "2026-11-10"


def test_sin_token_falla_explicitamente_y_no_pide_nada(tmp_path, monkeypatch):
    fila, ex = _correr(tmp_path, monkeypatch, AHORA, token=None)
    assert fila["resultado"] == "fallo" and fila["error"].startswith("sin_token") and ex.llamadas == []


def test_error_de_red_se_registra_sin_token(tmp_path, monkeypatch):
    fila, _ = _correr(tmp_path, monkeypatch, AHORA, falla="fallo en {url}")
    assert fila["resultado"] == "fallo"
    assert "TOKEN-DE-PRUEBA-123" not in json.dumps(fila)
    assert "TOKEN-DE-PRUEBA-123" not in (tmp_path / "ej.jsonl").read_text(encoding="utf-8")
