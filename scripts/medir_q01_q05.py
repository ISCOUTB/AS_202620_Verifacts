"""S9 · Mide Q-01 (P95 <= 3 s con 10.000 caracteres) y Q-05 (100 % de repetibilidad).

Levanta la API real (uvicorn, 127.0.0.1) con una base de datos temporal y le
envía solicitudes HTTP con un único cliente concurrente, como pide Q-01.
Uso (desde la raíz del repositorio):  python scripts/medir_q01_q05.py
Escribe docs/evidencia/medicion-q01-q05.md con el entorno de esta máquina.
"""
import math
import os
import platform
import shutil
import socket
import statistics
import sys
import tempfile
import threading
import time
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
DATOS = tempfile.mkdtemp(prefix="verifacts-medicion-")
os.environ["VERIFACTS_DATA_DIR"] = DATOS
os.environ.setdefault("LOG_LEVEL", "ERROR")

import httpx  # noqa: E402
import uvicorn  # noqa: E402

from app.main import app  # noqa: E402
from app.persistence.repository import initialize_database  # noqa: E402

LIMITE_Q01_MS = 3000
CORRIDAS = 200
REPETICIONES_Q05 = 100
BASE = "ESTA NOTICIA ES TOTALMENTE CIERTA!!! Todos deben compartirla!!! "
TEXTO_10K = (BASE * (10_000 // len(BASE) + 1))[:10_000]


def puerto_libre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def p95(valores: list[float]) -> float:
    ordenados = sorted(valores)
    return ordenados[math.ceil(0.95 * len(ordenados)) - 1]


def main() -> None:
    initialize_database()
    puerto = puerto_libre()
    servidor = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=puerto, log_level="error"))
    hilo = threading.Thread(target=servidor.run, daemon=True)
    hilo.start()
    url = f"http://127.0.0.1:{puerto}"
    with httpx.Client(timeout=30) as cliente:
        for _ in range(100):
            try:
                if cliente.get(f"{url}/health").status_code == 200:
                    break
            except httpx.HTTPError:
                time.sleep(0.1)
        for _ in range(10):  # calentamiento, no se cuenta
            cliente.post(f"{url}/analysis", json={"text": TEXTO_10K})

        tiempos = []
        for _ in range(CORRIDAS):
            t0 = time.perf_counter()
            r = cliente.post(f"{url}/analysis", json={"text": TEXTO_10K})
            tiempos.append((time.perf_counter() - t0) * 1000)
            assert r.status_code == 200

        resultados = set()
        for _ in range(REPETICIONES_Q05):
            d = cliente.post(f"{url}/analysis", json={"text": TEXTO_10K}).json()
            resultados.add((d["score"], d["classification"], tuple(d["factors"])))
    servidor.should_exit = True
    hilo.join(timeout=5)
    shutil.rmtree(DATOS, ignore_errors=True)

    valor_p95 = p95(tiempos)
    coincidencia = 100.0 if len(resultados) == 1 else 0.0
    q01 = "CUMPLE" if valor_p95 <= LIMITE_Q01_MS else "NO CUMPLE"
    q05 = "CUMPLE" if coincidencia == 100.0 else "NO CUMPLE"
    texto = f"""# Evidencia S9 — medición de Q-01 y Q-05

Generado por `scripts/medir_q01_q05.py` el {datetime.now().isoformat(timespec='seconds')}.

- Entorno: {platform.system()} {platform.release()}, Python {platform.python_version()}, uvicorn en 127.0.0.1, 1 cliente concurrente.
- Entrada: texto de {len(TEXTO_10K)} caracteres, origen `texto`, con persistencia real en SQLite temporal.
- No incluye el origen `url` (depende de un sitio externo, ver ADR-0003).

| Escenario | Medida exigida | Resultado ({CORRIDAS} corridas / {REPETICIONES_Q05} repeticiones) | Veredicto |
|---|---|---|---|
| Q-01 | P95 <= {LIMITE_Q01_MS} ms | P95 = {valor_p95:.1f} ms · mediana = {statistics.median(tiempos):.1f} ms · máx = {max(tiempos):.1f} ms | {q01} |
| Q-05 | 100 % de coincidencia | {coincidencia:.0f} % ({len(resultados)} resultado(s) distinto(s)) | {q05} |
"""
    salida = RAIZ / "docs" / "evidencia" / "medicion-q01-q05.md"
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()
