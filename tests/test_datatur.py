import json
import pandas as pd
import pytest

from extractores import datatur
from tests.conftest import BRONCE_BASE70, FIXTURES

# Fila literal del reporte oficial 2025-MES_09_Publico.pdf (acumulado ene-sep)
FILA_PDF_REAL = ("MANZANILLO, COL. 4,373 4,328 3,986 -46 -341 -1.0% -7.9% 2,423 2,368 2,352 "
                 "-55 -16 -2.3% -0.7% 55.4 54.7 59.0 -0.7 4.3")


def test_parsear_linea_pdf_real():
    f = datatur.parsear_linea_centro(FILA_PDF_REAL)
    assert f["centro_pdf"] == "MANZANILLO, COL."
    assert (f["disp_a1"], f["ocup_a1"], f["pct_a1"]) == (4328, 2368, 54.7)
    assert f["disp_var_a1a0"] == -7.9 and f["pct_dif_a1a0"] == 4.3


def test_parsear_linea_invalida():
    assert datatur.parsear_linea_centro("Total 70 centros") is None
    assert datatur.parsear_linea_centro("MANZANILLO, COL. 1 2 3") is None


def test_url_reporte_mensual():
    assert datatur.url_reporte_mensual(2025, 9, "pdf").endswith("/2025-MES_09_Publico.pdf")


def test_leer_base70_muestra_real(muestra_real):
    df = muestra_real
    assert list(df.columns[:13]) == datatur.COLUMNAS_BASE70
    assert df["mes"].str.fullmatch(r"\d{2}").all()
    assert df["periodo"].notna().all()
    man = df[df.centro == "Manzanillo"]
    assert man.periodo.nunique() == 24
    ene16 = man[man.periodo == "2016-01-01"]
    assert int(ene16.cuartos_disponibles.sum()) == 110093


def test_leer_base70_rechaza_columnas_faltantes(tmp_path):
    p = tmp_path / "malo.csv"
    p.write_text("anio,mes\n2020,01\n")
    with pytest.raises(ValueError):
        datatur.leer_base70(p)


def test_acumulado_a_mensual_reconstruye_mes(muestra_real):
    # Se construyen acumulados ene-mes a partir de los meses reales de 2016 y se
    # verifica que la conversión inversa recupere cada mes (error < 0.5 %).
    m = muestra_real[(muestra_real.centro == "Manzanillo") & (muestra_real.anio == 2016)]
    mens = m.groupby("mes").agg(disp=("cuartos_disponibles", "sum"),
                                ocup=("cuartos_ocupados_residentes", "sum")).astype(float)
    mens["ocup"] += m.groupby("mes").cuartos_ocupados_no_residentes.sum().astype(float)
    dias = [pd.Period(f"2016-{k}").days_in_month for k in mens.index]
    dias_acum = pd.Series(dias, index=mens.index).cumsum()
    acum = pd.DataFrame({"anio": 2016, "mes": [int(k) for k in mens.index],
                         "disp_prom_acum": (mens.disp.cumsum() / dias_acum).round(0).values,
                         "ocup_prom_acum": (mens.ocup.cumsum() / dias_acum).round(0).values})
    out = datatur.acumulado_a_mensual(acum)
    err = (out.cuartos_disponibles.values - mens.disp.values) / mens.disp.values
    assert abs(err).max() < 0.005
    assert out.derivado_de_acumulado.all()


@pytest.mark.datos
@pytest.mark.skipif(not BRONCE_BASE70.exists(), reason="sin bronce")
def test_bronce_coincide_con_sha_espejo():
    from extractores.base import sha256_archivo
    assert sha256_archivo(BRONCE_BASE70) == datatur.ESPEJO_SHA256


# --- Fuente oficial Base70centros (sin API del portal) -----------------------
class _ExFalso:
    """Sustituye a ExtractorEtico.get con una respuesta fija (sin red)."""
    def __init__(self, tmp_path, contenido, tipo="text/csv"):
        from extractores.base import Bitacora, Respuesta, sha256_bytes
        self.bitacora = Bitacora(tmp_path / "b.jsonl")
        self.pedidas = []
        self._r = Respuesta("u", 200, contenido, tipo, sha256_bytes(contenido), 0.1,
                            {"Last-Modified": "Tue, 15 Jul 2025 21:08:21 GMT"})

    def get(self, url):
        self.pedidas.append(url)
        return self._r


def test_url_oficial_no_usa_api_prohibida_por_robots(tmp_path, monkeypatch):
    import urllib.robotparser
    from extractores import datatur
    monkeypatch.delenv("DATATUR_BASE70_URL", raising=False)
    url = datatur.descubrir_url_base70(_ExFalso(tmp_path, b""))
    assert url == datatur.URL_OFICIAL_BASE70 and "/api/" not in url
    rp = urllib.robotparser.RobotFileParser()  # robots.txt real de www.datos.gob.mx (2026-11-09)
    rp.parse(["User-agent: *", "Disallow: /dataset/rate/", "Disallow: /revision/",
              "Disallow: /dataset/*/history", "Disallow: /api/", "Crawl-Delay: 10"])
    assert not rp.can_fetch("ObservatorioHotelero", "https://www.datos.gob.mx/api/3/action/package_show?id=x")
    assert not hasattr(datatur, "API_PAQUETE")


def test_descarga_oficial_registra_metadatos(tmp_path, monkeypatch):
    from extractores import datatur
    monkeypatch.setattr(datatur, "guardar_bronce",
                        lambda c, f, n, m: (tmp_path / n).write_bytes(c) or (tmp_path / n))
    ex = _ExFalso(tmp_path, (FIXTURES / "base70_muestra_real.tsv").read_bytes())
    ruta, origen = datatur.descargar_base70(ex, permitir_espejo=False)
    assert origen == "oficial" and ex.pedidas == [datatur.URL_OFICIAL_BASE70]
    ev = [json.loads(l) for l in (tmp_path / "b.jsonl").read_text(encoding="utf-8").splitlines()]
    fin = [e for e in ev if e["evento"] == "base70_oficial"][0]
    assert fin["encabezados"]["Last-Modified"].startswith("Tue, 15 Jul 2025")


def test_descarga_rechaza_html_en_lugar_de_csv(tmp_path):
    from extractores import datatur
    ex = _ExFalso(tmp_path, b"<!DOCTYPE html><title>Recurso no disponible</title>", "text/html")
    with pytest.raises(RuntimeError):
        datatur.descargar_base70(ex, permitir_espejo=False)
