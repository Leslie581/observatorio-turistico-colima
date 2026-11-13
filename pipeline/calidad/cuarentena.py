"""Cuarentena: separa y documenta los registros rechazados (contrato §3). Nunca modifica bronce.

Cada fila rechazada conserva TODAS sus columnas originales más: regla_id, motivo_rechazo, fila_origen,
archivo_bronce, sha256_bronce y fecha_proceso_utc. Un mismo registro puede incumplir varias reglas y
aparece una vez por regla; en el resumen se cuenta también por registro único, de modo que
``leidos = aceptados + rechazados`` (nada se descarta en silencio).
"""
from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd


class ErrorPuertaCalidad(Exception):
    """El lote no puede producir una salida confiable; la ejecución debe detenerse (código 2)."""

    def __init__(self, regla: str, mensaje: str):
        super().__init__(f"[{regla}] {mensaje}")
        self.regla = regla
        self.mensaje = mensaje


def escribir_atomico(ruta: Path, contenido: bytes) -> None:
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    tmp = ruta.with_name(ruta.name + ".tmp")
    tmp.write_bytes(contenido)
    os.replace(tmp, ruta)


def csv_bytes(df: pd.DataFrame, **kw) -> bytes:
    """CSV UTF-8 con finales de línea LF (el repositorio conserva los datos byte a byte)."""
    return df.to_csv(index=False, lineterminator="\n", na_rep="", **kw).encode("utf-8")


class Cuarentena:
    def __init__(self, fecha_proceso_utc: str):
        self.fecha_proceso_utc = fecha_proceso_utc
        self._filas: dict[str, list[pd.DataFrame]] = defaultdict(list)
        self._leidos: Counter = Counter()
        self._unicos: dict[str, set] = defaultdict(set)
        self._por_regla: dict[str, Counter] = defaultdict(Counter)
        self._marcados: dict[str, Counter] = defaultdict(Counter)
        self.lotes_rechazados: list[dict] = []
        self.informativo: dict = {}

    # --- registro
    def leidos(self, fuente: str, n: int) -> None:
        self._leidos[fuente] += int(n)

    def rechazar(self, fuente: str, regla_id: str, motivo: "str | pd.Series", filas: pd.DataFrame,
                 archivo_bronce: str, sha256: str) -> None:
        """``filas`` debe traer ``fila_origen``; ``motivo`` puede ser texto o una Serie alineada."""
        if filas.empty:
            return
        f = filas.copy()
        f.insert(0, "regla_id", regla_id)
        f.insert(1, "motivo_rechazo", motivo if isinstance(motivo, str) else motivo.loc[f.index].values)
        f["archivo_bronce"] = archivo_bronce
        f["sha256_bronce"] = sha256
        f["fecha_proceso_utc"] = self.fecha_proceso_utc
        self._filas[fuente].append(f)
        self._por_regla[fuente][regla_id] += len(f)
        self._unicos[fuente].update((archivo_bronce, int(x)) for x in f["fila_origen"])

    def marcar(self, fuente: str, nombre: str, n: int) -> None:
        self._marcados[fuente][nombre] += int(n)

    def rechazar_lote(self, fuente: str, regla_id: str, motivo: str, archivo_bronce: str, registros: int = 0) -> None:
        self.lotes_rechazados.append({"fuente": fuente, "regla_id": regla_id, "motivo": motivo,
                                      "archivo_bronce": archivo_bronce, "registros_del_lote": int(registros)})
        # los registros de un lote rechazado se cuentan como rechazados (no se pierden de la cuenta)
        self._por_regla[fuente][regla_id] += int(registros)
        self._unicos[fuente].update((archivo_bronce, i) for i in range(1, int(registros) + 1))

    # --- salidas
    def resumen(self) -> dict:
        out = {}
        for fuente in sorted(set(self._leidos) | set(self._por_regla) | set(self._marcados)):
            leidos = self._leidos[fuente]
            rechazados = len(self._unicos[fuente])
            out[fuente] = {"leidos": leidos, "aceptados": leidos - rechazados, "rechazados": rechazados,
                           "rechazos_por_regla": dict(sorted(self._por_regla[fuente].items())),
                           "marcados": dict(sorted(self._marcados[fuente].items()))}
            assert out[fuente]["aceptados"] >= 0, "rechazados mayores que leídos: la cuenta no cuadra"
        return {"fuentes": out, "lotes_rechazados": self.lotes_rechazados, "informativo": self.informativo,
                "fecha_proceso_utc": self.fecha_proceso_utc}

    def escribir(self, carpeta: Path, ejecucion: str) -> list[Path]:
        carpeta = Path(carpeta)
        escritos = []
        for fuente, frames in self._filas.items():
            df = pd.concat(frames, ignore_index=True)
            ruta = carpeta / fuente / ejecucion / "rechazados.csv"
            escribir_atomico(ruta, csv_bytes(df))
            escritos.append(ruta)
        ruta = carpeta / f"resumen_{ejecucion}.json"
        escribir_atomico(ruta, (json.dumps(self.resumen(), ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
        escritos.append(ruta)
        return escritos
