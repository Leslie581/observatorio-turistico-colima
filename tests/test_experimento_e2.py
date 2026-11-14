"""Matriz del diseño 2^3 de E2 (laboratorio/experimento/matriz.py): estructura, balance, ortogonalidad y reproducibilidad."""
import numpy as np

from laboratorio.experimento import matriz as mz


def test_hay_16_corridas_8_tratamientos_por_bloque_y_cada_uno_una_vez():
    m = mz.matriz()
    assert len(m) == 16 and set(m.bloque) == set(mz.BLOQUES)
    for _, g in m.groupby("bloque"):
        assert sorted(g.tratamiento) == list(range(1, 9)) and sorted(g.corrida) == list(range(1, 9))


def test_el_diseno_es_balanceado_y_ortogonal():
    m = mz.matriz()
    cod = m[["procesos_cod", "analizador_cod", "formato_cod"]].to_numpy()
    assert (cod.sum(axis=0) == 0).all()                                              # cada factor: 8 corridas en -1 y 8 en +1
    producto = cod.T @ cod
    assert np.array_equal(producto, 16 * np.eye(3, dtype=int))                       # columnas ortogonales (sin confusión entre efectos)
    inter = np.column_stack([cod[:, 0] * cod[:, 1], cod[:, 0] * cod[:, 2], cod[:, 1] * cod[:, 2], cod.prod(axis=1)])
    assert (inter.sum(axis=0) == 0).all() and np.allclose(np.corrcoef(np.column_stack([cod, inter]).T), np.eye(7), atol=1e-12)


def test_el_orden_se_aleatoriza_dentro_de_cada_bloque_y_es_reproducible():
    a, b = mz.matriz(), mz.matriz()
    assert a.equals(b)                                                               # misma semilla, misma matriz
    assert not a.equals(mz.matriz(semilla=1))                                        # otra semilla, otro orden
    primero, segundo = (g.sort_values("corrida").tratamiento.tolist() for _, g in a.groupby("bloque"))
    assert primero != sorted(primero) and primero != segundo                         # no es el orden estándar y cada bloque se aleatoriza aparte


def test_los_niveles_corresponden_a_los_codigos():
    m = mz.matriz()
    for nombre, (bajo, alto) in mz.FACTORES.items():
        assert (m.loc[m[f"{nombre}_cod"] == -1, nombre] == bajo).all() and (m.loc[m[f"{nombre}_cod"] == 1, nombre] == alto).all()


def test_el_archivo_versionado_esta_al_dia(tmp_path):
    mz.escribir(tmp_path / "m.csv")
    assert (tmp_path / "m.csv").read_bytes() == mz.SALIDA.read_bytes().replace(b"\r\n", b"\n")
