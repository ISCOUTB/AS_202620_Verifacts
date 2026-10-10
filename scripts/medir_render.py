"""Mide GET /health y POST /analysis en Render con el mismo payload de 10.000 caracteres.

Uso (desde la raíz del repo):
  python scripts/medir_render.py --modo caliente --runs 50 --out docs/evidencia/render_caliente.csv
  python scripts/medir_render.py --modo frio --runs 3 --out docs/evidencia/render_frio.csv

El modo frío espera 20 minutos entre corridas (Render gratuito duerme tras ~15 min sin tráfico).
"""
import argparse
import csv
import platform
import statistics
import time
from datetime import datetime, timezone

import httpx

from payload_10k import payload_10k

URL = "https://verifacts-api.onrender.com"
ESPERA_FRIO_SEGUNDOS = 20 * 60


def p95(valores: list[float]) -> float:
    ordenados = sorted(valores)
    indice = max(0, int(round(0.95 * len(ordenados))) - 1)
    return ordenados[indice]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--modo", choices=["frio", "caliente"], required=True)
    ap.add_argument("--runs", type=int, default=30)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    texto = payload_10k()
    filas: list[tuple[int, str, int, float]] = []

    with httpx.Client(timeout=120) as cliente:
        if args.modo == "caliente":
            cliente.get(f"{URL}/health")  # calentamiento, no se registra

        for i in range(args.runs):
            if args.modo == "frio" and i > 0:
                print(f"Esperando {ESPERA_FRIO_SEGUNDOS // 60} min sin tráfico...")
                time.sleep(ESPERA_FRIO_SEGUNDOS)

            for operacion in ("GET /health", "POST /analysis"):
                inicio = time.perf_counter()
                if operacion == "GET /health":
                    r = cliente.get(f"{URL}/health")
                else:
                    r = cliente.post(f"{URL}/analysis", json={"text": texto})
                ms = (time.perf_counter() - inicio) * 1000
                filas.append((i, operacion, r.status_code, round(ms, 1)))
                print(f"corrida {i + 1}/{args.runs} · {operacion} · HTTP {r.status_code} · {ms:.1f} ms")

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(["corrida", "operacion", "http", "ms"])
        escritor.writerows(filas)

    print("\n--- MANIFIESTO (copiar a docs/evidencia/comparacion-s10.md) ---")
    print("fecha_utc:", datetime.now(timezone.utc).isoformat())
    print("cliente:", platform.platform(), "| Python", platform.python_version())
    print("modo:", args.modo, "| corridas:", args.runs, "| payload: 10000 caracteres")
    for operacion in ("GET /health", "POST /analysis"):
        valores = [f[3] for f in filas if f[1] == operacion]
        print(
            f"{operacion}: n={len(valores)} "
            f"mediana={statistics.median(valores):.1f} ms "
            f"p95={p95(valores):.1f} ms max={max(valores):.1f} ms"
        )


if __name__ == "__main__":
    main()
