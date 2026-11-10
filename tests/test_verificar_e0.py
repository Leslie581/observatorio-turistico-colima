import json

from extractores.base import guardar_bronce
from pipeline import verificar_e0 as v

ENC = "anio\tmes\ttipo_centro\tcentro\tcategoria\tcuartos_disponibles\r\n"


def _csv(tmp_path, filas, con_ficha=True, centro="Manzanillo", contenido=None):
    """Escribe un Base70 sintético en tmp_path/datatur (nunca toca el CSV histórico real)."""
    if contenido is None:
        contenido = ENC + "".join(f"{a}\t{m:02d}\tPlaya\t{centro}\t{c}\t100\r\n" for a, m, c in filas)
    if con_ficha:
        guardar_bronce(contenido.encode("utf-8"), "datatur", "Base70centros.csv", {"url": "u"}, bronce=tmp_path)
    else:
        (tmp_path / "datatur").mkdir(exist_ok=True)
        (tmp_path / "datatur" / "Base70centros.csv").write_bytes(contenido.encode("utf-8"))
    return tmp_path


def _meses(n, inicio=(2020, 1)):
    a, m = inicio
    for _ in range(n):
        yield (a, m, "3 estrellas")
        a, m = (a + 1, 1) if m == 12 else (a, m + 1)


def test_historico_real_se_valida_sin_modificarlo():
    ruta = v.BRONCE / "datatur" / "Base70centros.csv"
    antes = ruta.read_bytes()
    r = v.historico()
    assert r["ok"] and r["estado"] == "satisfactoria" and r["periodos"] == 108 and r["huecos_en_rango"] == []
    assert all(r["checks"].values())
    assert ruta.read_bytes() == antes


def test_historico_sintetico_valido(tmp_path):
    r = v.historico(_csv(tmp_path, list(_meses(36))))
    assert r["ok"] and r["periodos"] == 36


def test_historico_rechaza_serie_larga_con_un_hueco(tmp_path):
    filas = [f for f in _meses(48) if (f[0], f[1]) != (2021, 6)]  # 47 periodos: suficientes, pero falta uno
    r = v.historico(_csv(tmp_path, filas))
    assert r["periodos"] == 47 and r["checks"]["minimo_periodos"] is True
    assert r["huecos_en_rango"] == ["2021-06"] and not r["ok"] and r["estado"] == "fallida"


def test_historico_rechaza_menos_de_36(tmp_path):
    r = v.historico(_csv(tmp_path, list(_meses(35))))
    assert not r["ok"] and r["checks"]["minimo_periodos"] is False and r["checks"]["sin_huecos_periodos_consecutivos"]


def test_historico_rechaza_duplicados(tmp_path):
    filas = list(_meses(36)) + [(2020, 1, "3 estrellas")]
    r = v.historico(_csv(tmp_path, filas))
    assert not r["ok"] and r["filas_duplicadas"] == 2 and r["checks"]["sin_duplicados"] is False


def test_historico_misma_fecha_con_otra_categoria_no_es_duplicado(tmp_path):
    filas = list(_meses(36)) + [(2020, 1, "4 estrellas")]
    assert v.historico(_csv(tmp_path, filas))["ok"]


def test_historico_rechaza_fechas_invalidas(tmp_path):
    filas = list(_meses(36)) + [(2023, 13, "3 estrellas")]
    r = v.historico(_csv(tmp_path, filas))
    assert not r["ok"] and r["checks"]["fechas_validas"] is False and r["filas_con_fecha_invalida"] == 1


def test_historico_rechaza_archivo_inexistente_vacio_y_sin_centro(tmp_path):
    assert v.historico(tmp_path)["checks"]["archivo_existe"] is False
    r = v.historico(_csv(tmp_path, [], contenido=""))
    assert not r["ok"] and r["checks"]["archivo_no_vacio"] is False
    otro = tmp_path / "otro"
    otro.mkdir()
    r = v.historico(_csv(otro, list(_meses(36)), centro="Tijuana"))
    assert not r["ok"] and r["checks"]["centro_con_filas"] is False


def test_historico_detecta_hash_distinto_o_ficha_ausente(tmp_path):
    base = _csv(tmp_path, list(_meses(36)))
    ruta = base / "datatur" / "Base70centros.csv"
    ruta.write_bytes(ruta.read_bytes() + b" ")
    assert not v.historico(base)["checks"]["hash_y_tamano_coinciden_con_ficha"]
    sin = tmp_path / "sin"
    sin.mkdir()
    assert not v.historico(_csv(sin, list(_meses(36)), con_ficha=False))["ok"]


def test_integridad_detecta_archivo_alterado_y_archivo_sin_ficha(tmp_path):
    ruta = guardar_bronce(b"a,b\n1,2\n", "f", "x.csv", {"url": "u"}, bronce=tmp_path)
    assert v.integridad(tmp_path)["ok"] is True
    ruta.write_bytes(b"a,b\n9,9\n")
    assert v.integridad(tmp_path)["ok"] is False
    (tmp_path / "f" / "otro.csv").write_text("x", encoding="utf-8")
    assert "otro.csv" in v.integridad(tmp_path)["archivos_sin_ficha"]


def test_integridad_sin_archivos_es_sin_datos_no_satisfactoria(tmp_path):
    r = v.integridad(tmp_path)
    assert r["ok"] is None and r["estado"] == "sin_datos"


def test_privacidad_detecta_campos_personales_y_de_domicilio(tmp_path):
    d = tmp_path / "denue" / "2026-11-10"
    d.mkdir(parents=True)
    (d / "a_BuscarAreaAct.json").write_text(json.dumps([{"Id": "1", "Correo_e": "x@y.mx"}]), encoding="utf-8")
    (d / "b_BuscarAreaAct.json").write_text(json.dumps([{"Id": "2", "Calle": "X"}]), encoding="utf-8")
    (d / "c_BuscarAreaAct.json").write_text(json.dumps([{"Id": "3"}]), encoding="utf-8")
    r = v.privacidad(tmp_path)
    assert r["ok"] is False and r["archivos_denue_revisados"] == 3
    assert {i["campos"][0] for i in r["infractores"]} == {"correo_e", "calle"}


def test_privacidad_sin_archivos_reales_no_es_satisfactoria(tmp_path):
    r = v.privacidad(tmp_path)
    assert r["ok"] is None and r["estado"] == "sin_datos" and "NO hay archivos reales" in r["aviso"]


def test_privacidad_archivos_limpios_son_satisfactorios(tmp_path):
    d = tmp_path / "denue" / "2026-11-10"
    d.mkdir(parents=True)
    (d / "a_BuscarAreaAct.json").write_text(json.dumps([{"Id": "1", "CLEE": "X", "Estrato": "6 a 10 personas"}]), encoding="utf-8")
    assert v.privacidad(tmp_path)["estado"] == "satisfactoria"


def test_disponibilidad(tmp_path):
    b = tmp_path / "b.jsonl"
    assert v.disponibilidad(b)["ok"] is None
    filas = [{"resultado": "exito", "fecha_local": f"2026-11-{d:02d}"} for d in range(10, 20)]
    filas += [{"resultado": "omitida_duplicada", "fecha_local": "2026-11-19"}]
    b.write_text("\n".join(json.dumps(f) for f in filas), encoding="utf-8")
    r = v.disponibilidad(b)
    assert r["ok"] and r["ejecuciones"] == 10 and r["tasa_exito"] == 1.0
    b.write_text("\n".join(json.dumps(f) for f in filas[:9] + [{"resultado": "fallo", "fecha_local": "2026-11-20"}]),
                 encoding="utf-8")
    assert v.disponibilidad(b)["ok"] is False  # 9/10 = 0.9 < 0.95


def test_codigo_de_salida_trata_sin_datos_segun_la_bandera():
    informe = {"privacidad": {"ok": None}, "historico": {"ok": True}}
    assert v.codigo_salida(informe) == 0
    assert v.codigo_salida(informe, exigir_datos=True) == 1
    assert v.codigo_salida({"x": {"ok": False}}) == 1


# --- Disponibilidad informativa: indicador por debajo del objetivo frente a error técnico ---
def _bitacora_50(tmp_path):
    b = tmp_path / "b.jsonl"
    filas = [{"resultado": "fallo", "fecha_local": "2026-11-09"}, {"resultado": "exito", "fecha_local": "2026-11-09"}]
    contenido = "\n".join(json.dumps(f) for f in filas)
    b.write_text(contenido, encoding="utf-8")
    return b, contenido


def test_disponibilidad_50_por_ciento_se_calcula_igual_y_no_cumple_el_objetivo(tmp_path):
    b, _ = _bitacora_50(tmp_path)
    r = v.disponibilidad(b)
    assert (r["ejecuciones"], r["exitosas"], r["tasa_exito"], r["objetivo"]) == (2, 1, 0.5, 0.95)
    assert r["objetivo_cumplido"] is False and r["estado"] == "fallida"


def test_informativo_no_falla_por_estar_bajo_el_objetivo_pero_no_informativo_si(tmp_path, monkeypatch, capsys):
    b, _ = _bitacora_50(tmp_path)
    monkeypatch.setattr(v, "BITACORA", b)
    monkeypatch.setitem(v.COMPROBACIONES, "disponibilidad", lambda: v.disponibilidad(b))
    assert v.main(["--solo", "disponibilidad", "--informativo"]) == 0
    salida = json.loads(capsys.readouterr().out)
    assert salida["disponibilidad"]["tasa_exito"] == 0.5 and salida["disponibilidad"]["objetivo_cumplido"] is False
    assert v.main(["--solo", "disponibilidad"]) == 1


def test_error_tecnico_del_verificador_es_bloqueante_incluso_en_modo_informativo(tmp_path, monkeypatch, capsys):
    corrupta = tmp_path / "b.jsonl"
    corrupta.write_text("esto no es json\n", encoding="utf-8")
    monkeypatch.setitem(v.COMPROBACIONES, "disponibilidad", lambda: v.disponibilidad(corrupta))
    assert v.main(["--solo", "disponibilidad", "--informativo"]) == 2
    salida = json.loads(capsys.readouterr().out)
    assert salida["disponibilidad"]["estado"] == "error" and "JSONDecodeError" in salida["disponibilidad"]["error"]


def test_las_comprobaciones_obligatorias_siguen_fallando_con_codigo_1(tmp_path, monkeypatch):
    monkeypatch.setitem(v.COMPROBACIONES, "integridad", lambda: {"ok": False, "estado": "fallida"})
    assert v.main(["--solo", "integridad"]) == 1
    assert v.main(["--solo", "integridad", "--exigir-datos"]) == 1


def test_el_modo_informativo_no_cambia_los_datos_historicos(tmp_path):
    b, contenido = _bitacora_50(tmp_path)
    v.disponibilidad(b)
    assert b.read_text(encoding="utf-8") == contenido
