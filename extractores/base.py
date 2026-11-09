"""Extractor ético y trazable del Observatorio Turístico y Hotelero de Manzanillo (TDL).

Basado en el extractor del Kit de arranque TDL. Agrega:
- sesión HTTP con timeouts y reintentos limitados (espera exponencial);
- User-Agent identificable configurable por variable de entorno;
- respeto a robots.txt y a una pausa mínima por dominio (>= 1 s);
- bitácora JSONL de cada petición (URL, estado HTTP, bytes, SHA-256, error);
- conservación de los originales en la capa bronce con un archivo .meta.json.

Nunca evade CAPTCHA, autenticación ni restricciones: si robots.txt prohíbe
una ruta se lanza PermissionError y se registra el bloqueo.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import time
import urllib.robotparser
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

RAIZ = Path(__file__).resolve().parent.parent
BRONCE = RAIZ / "data" / "bronce"
LOGS = RAIZ / "logs"

UA_POR_DEFECTO = "ObservatorioHotelero-TDL/0.1 (proyecto academico; contacto: {contacto})"

log = logging.getLogger("observatorio")


def ahora_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_bytes(contenido: bytes) -> str:
    return hashlib.sha256(contenido).hexdigest()


def sha256_archivo(ruta: Path) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 16), b""):
            h.update(bloque)
    return h.hexdigest()


def ocultar_credenciales(valor):
    """Evita que tokens de URL o variables de entorno queden en bitácoras."""
    if isinstance(valor, dict):
        return {k: ocultar_credenciales(v) for k, v in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [ocultar_credenciales(v) for v in valor]
    if isinstance(valor, str):
        token = os.getenv("INEGI_TOKEN", "")
        if token:
            valor = valor.replace(token, "***TOKEN***")
        valor = re.sub(r"(?i)(/consulta/[^\s\"']+/)([0-9a-f]{8}-[0-9a-f-]{27,})", r"\1***TOKEN***", valor)
    return valor


class Bitacora:
    """Registro JSONL append-only de eventos de captura."""

    def __init__(self, ruta: Path | None = None, ejecucion_id: str | None = None):
        self.ruta = Path(ruta or LOGS / "bitacora.jsonl")
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        self.ejecucion_id = ejecucion_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    def registrar(self, evento: str, **datos) -> dict:
        datos = ocultar_credenciales(datos)
        fila = {"ts": ahora_utc(), "ejecucion": self.ejecucion_id, "evento": evento, **datos}
        with open(self.ruta, "a", encoding="utf-8") as f:
            f.write(json.dumps(fila, ensure_ascii=False, default=str) + "\n")
        log.info("%s %s", evento, {k: v for k, v in datos.items() if k != "detalle"})
        return fila


@dataclass
class Respuesta:
    url: str
    estado: int
    contenido: bytes
    tipo: str
    sha256: str
    segundos: float
    encabezados: dict = field(default_factory=dict)


class ExtractorEtico:
    def __init__(
        self,
        bitacora: Bitacora | None = None,
        pausa: float = 1.5,
        intentos: int = 3,
        timeout: tuple[float, float] = (10, 60),
        user_agent: str | None = None,
        respetar_robots: bool = True,
    ):
        if pausa < 1.0:
            raise ValueError("La pausa mínima entre peticiones al mismo dominio es 1 s (regla TDL)")
        self.pausa = pausa
        self.intentos = max(1, min(intentos, 5))  # reintentos limitados
        self.timeout = timeout
        contacto = os.getenv("TDL_CONTACTO") or "definir TDL_CONTACTO"
        self.ua = (user_agent or os.getenv("TDL_UA") or UA_POR_DEFECTO).replace("{contacto}", contacto)
        self.respetar_robots = respetar_robots
        self.bitacora = bitacora or Bitacora()
        self.robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}
        self.ultimo: dict[str, float] = {}
        self.inalcanzables: dict[str, str] = {}
        self.robots_indeterminados: dict[str, int] = {}
        self.sesion = requests.Session()
        self.sesion.headers["User-Agent"] = self.ua

    # ------------------------------------------------------------------ robots
    def _reglas(self, url: str):
        p = urlparse(url)
        base = f"{p.scheme}://{p.netloc}"
        if base in self.inalcanzables:
            raise ConnectionError(f"Dominio inalcanzable en esta ejecución: {p.netloc} "
                                  f"({self.inalcanzables[base]})")
        if base not in self.robots:
            rp = urllib.robotparser.RobotFileParser()
            try:
                r = self.sesion.get(base + "/robots.txt", timeout=self.timeout)
                if r.status_code == 200:
                    rp.parse(r.text.splitlines())
                    self.bitacora.registrar("robots_leido", dominio=p.netloc, estado=200)
                elif r.status_code in (401, 403):
                    # Sin reglas accesibles no se puede concluir que la ruta
                    # concreta esté prohibida; se bloquea por precaución.
                    self.robots_indeterminados[base] = r.status_code
                    self.bitacora.registrar("robots_acceso_indeterminado", dominio=p.netloc, estado=r.status_code)
                    raise PermissionError(f"No se pudo verificar robots.txt de {p.netloc}: HTTP {r.status_code}")
                elif r.status_code in (404, 410):
                    rp.allow_all = True
                    self.bitacora.registrar("robots_ausente", dominio=p.netloc, estado=r.status_code)
                else:
                    self.bitacora.registrar("robots_estado_inesperado", dominio=p.netloc, estado=r.status_code)
                    raise ConnectionError(f"robots.txt de {p.netloc} respondió HTTP {r.status_code}")
            except requests.RequestException as e:
                # Sin robots.txt alcanzable no sabemos las reglas; el dominio
                # tampoco será alcanzable para la descarga. Se registra y se propaga.
                self.bitacora.registrar("robots_error", dominio=p.netloc, error=repr(e))
                self.inalcanzables[base] = type(e).__name__
                raise
            self.robots[base] = rp
        return self.robots[base]

    def permitido(self, url: str) -> bool:
        if not self.respetar_robots:
            return True
        return self._reglas(url).can_fetch(self.ua, url)

    # ------------------------------------------------------------------- get
    def get(self, url: str, **kwargs) -> Respuesta:
        return self._solicitar("GET", url, **kwargs)

    def post(self, url: str, datos=None, encabezados: dict | None = None, **kwargs) -> Respuesta:
        """POST con las mismas reglas que get(): robots.txt, pausa, reintentos limitados y bitácora.

        Se usa para formularios públicos (p. ej. el generador de reportes de DataTur).
        La bitácora registra el método y los NOMBRES de los campos, nunca cookies.
        """
        return self._solicitar("POST", url, data=datos, headers=encabezados or {}, **kwargs)

    def _solicitar(self, metodo: str, url: str, **kwargs) -> Respuesta:
        if self.respetar_robots and not self.permitido(url):
            self.bitacora.registrar("bloqueado_robots", url=url)
            raise PermissionError(f"robots.txt no permite {url}")
        dominio = urlparse(url).netloc
        demora = 0.0
        if self.respetar_robots:
            demora = self._reglas(url).crawl_delay(self.ua) or 0
        pausa = max(self.pausa, float(demora))
        ultimo_error: Exception | None = None
        for i in range(self.intentos):
            espera = pausa - (time.time() - self.ultimo.get(dominio, 0))
            if espera > 0:
                time.sleep(espera)
            t0 = time.perf_counter()
            try:
                r = self.sesion.request(metodo, url, timeout=self.timeout, **kwargs)
            except requests.RequestException as e:
                self.ultimo[dominio] = time.time()
                ultimo_error = e
                self.bitacora.registrar("http_error", metodo=metodo, url=url, intento=i + 1, error=repr(e))
                time.sleep(pausa * 2**i)
                continue
            seg = time.perf_counter() - t0
            self.ultimo[dominio] = time.time()
            self.bitacora.registrar(
                "http", metodo=metodo, url=url, intento=i + 1, estado=r.status_code,
                bytes=len(r.content), segundos=round(seg, 3),
                tipo=r.headers.get("Content-Type", ""),
            )
            if r.status_code == 429 or r.status_code >= 500:
                ultimo_error = requests.HTTPError(f"HTTP {r.status_code}")
                time.sleep(pausa * 2**i)
                continue
            r.raise_for_status()
            enc = {k: r.headers[k] for k in ("Content-Type", "Content-Length", "Content-Encoding",
                                             "Last-Modified", "ETag", "Date") if k in r.headers}
            return Respuesta(url, r.status_code, r.content, r.headers.get("Content-Type", ""),
                             sha256_bytes(r.content), seg, enc)
        raise RuntimeError(f"Sin respuesta válida de {url} tras {self.intentos} intentos: {ultimo_error!r}")


def guardar_bronce(contenido: bytes, fuente: str, nombre: str, metadatos: dict,
                   bronce: Path = BRONCE) -> Path:
    """Guarda el original intacto y su ficha de metadatos de captura.

    Idempotente: si ya existe un archivo con el mismo SHA-256 no se duplica,
    pero la nueva captura se añade a ``capturas`` en el .meta.json. Si el
    archivo existente venía de una copia y la nueva captura es oficial con el
    mismo hash, la ficha se promueve a ``origen = 'oficial'`` y la procedencia
    anterior se conserva en ``procedencia_anterior`` (no se borra evidencia).
    """
    destino_dir = Path(bronce) / fuente
    destino_dir.mkdir(parents=True, exist_ok=True)
    digest = sha256_bytes(contenido)
    destino = destino_dir / nombre
    captura = {"capturado_utc": ahora_utc(), **metadatos}
    if destino.exists() and sha256_archivo(destino) == digest:
        meta_ruta = Path(str(destino) + ".meta.json")
        meta = json.loads(meta_ruta.read_text(encoding="utf-8")) if meta_ruta.exists() else {
            "archivo": destino.name, "sha256": digest, "bytes": len(contenido)}
        meta.setdefault("capturas", []).append(captura)
        if metadatos.get("origen") == "oficial" and meta.get("origen") != "oficial":
            anterior = {k: v for k, v in meta.items() if k not in ("archivo", "sha256", "bytes", "capturas")}
            meta = {"archivo": meta.get("archivo", destino.name), "sha256": digest,
                    "bytes": len(contenido), **captura, "procedencia_anterior": anterior,
                    "capturas": meta["capturas"]}
        meta_ruta.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        return destino
    if destino.exists():  # mismo nombre, contenido nuevo: versionar
        sello = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        destino = destino_dir / f"{destino.stem}__{sello}{destino.suffix}"
    destino.write_bytes(contenido)
    meta = {"archivo": destino.name, "sha256": digest, "bytes": len(contenido),
            **captura, "capturas": [captura]}
    Path(str(destino) + ".meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return destino
