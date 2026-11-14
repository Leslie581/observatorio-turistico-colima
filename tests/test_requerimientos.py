"""Consistencia de docs/E1/requerimientos.md: que la tabla sea verificable y que el recuento no quede desactualizado.

No comprueba que cada requerimiento SE CUMPLA (eso lo hacen las pruebas y verificaciones que cita); comprueba que el documento
esté bien formado: identificadores únicos, las cinco columnas con contenido, un estado válido y un recuento igual a las filas.
"""
import re
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DOC = RAIZ / "docs" / "E1" / "requerimientos.md"
ESTADOS = ("NO CUMPLIDO", "CUMPLIDO", "PARCIAL", "PENDIENTE", "PROPUESTO")  # NO CUMPLIDO antes que CUMPLIDO


def _filas():
    out = []
    for linea in DOC.read_text(encoding="utf-8").splitlines():
        if re.match(r"\| \*\*R(F|NF)-", linea):
            celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
            out.append(celdas)
    return out


def _estado(celda):
    limpio = re.sub(r"\*+", "", celda)
    return next(e for e in ESTADOS if limpio.startswith(e))


def test_cada_requerimiento_tiene_cinco_columnas_con_contenido_y_un_estado_valido():
    filas = _filas()
    assert len(filas) >= 30
    for f in filas:
        assert len(f) == 5, f[0]
        assert all(len(c) > 3 for c in f), f"celda vacía o trivial en {f[0]}"
        _estado(f[4])  # lanza StopIteration si el estado no es uno de los definidos


def test_los_identificadores_son_unicos_y_siguen_el_formato():
    ids = [re.sub(r"\*+", "", f[0]) for f in _filas()]
    assert len(ids) == len(set(ids))
    assert all(re.fullmatch(r"R(F-\d{2}|NF-[A-Z]{3}-\d{2})", i) for i in ids), ids


def test_el_recuento_del_documento_coincide_con_las_filas():
    filas = _filas()
    cuenta = Counter((_estado(f[4]), "RF" if f[0].startswith("| **RF") or re.sub(r"\*+", "", f[0]).startswith("RF-") else "RNF") for f in filas)
    texto = DOC.read_text(encoding="utf-8")
    for estado, etiqueta in (("CUMPLIDO", "CUMPLIDO"), ("PARCIAL", "PARCIAL"), ("NO CUMPLIDO", "NO CUMPLIDO"),
                             ("PENDIENTE", "PENDIENTE"), ("PROPUESTO", "PROPUESTO (sin conclusión)")):
        fila = re.search(rf"^\| {re.escape(etiqueta)} \| (\d+) \| (\d+) \| (\d+) \|", texto, re.M)
        assert fila, etiqueta
        rf, rnf, total = (int(x) for x in fila.groups())
        assert (rf, rnf) == (cuenta[(estado, "RF")], cuenta[(estado, "RNF")]), f"recuento desactualizado para {estado}"
        assert total == rf + rnf
    total = re.search(r"^\| \*\*Total\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \| \*\*(\d+)\*\* \|", texto, re.M)
    assert total and int(total.group(3)) == len(filas)


def test_lo_no_comprobado_no_figura_como_cumplido():
    """Reglas de honestidad del documento: lo que no se cumple o no existe no figura como cumplido."""
    por_id = {re.sub(r"\*+", "", f[0]): _estado(f[4]) for f in _filas()}
    assert por_id["RNF-SEG-01"] == "CUMPLIDO"         # gitleaks 8.30.1 se ejecutó el 2026-11-13 (seguridad.md §3)
    assert por_id["RNF-DIS-01"] == "NO CUMPLIDO"      # 85.7 % y ventana insuficiente
    assert por_id["RF-10"] == "CUMPLIDO"              # el tablero está en main y la URL pública sirve la versión integrada (2026-11-14)
    assert por_id["RNF-DIS-02"] == "PROPUESTO"        # un solo incidente: sin conclusión
