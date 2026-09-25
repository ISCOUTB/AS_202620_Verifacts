"""
Ejecuta `sam local invoke` N veces contra VeriFactsFunction, capturando el
"Init Duration" que reporta el emulador de Lambda (aws-lambda-rie) en cada
corrida.

USO (desde serverless-prototype/):
    python medir_cold_start.py --runs 30
    python medir_cold_start.py --runs 30 --event events/analysis_event.json --out cold_start_analysis.csv

Cada invocación de `sam local invoke` levanta un contenedor Docker nuevo,
así que cada corrida es, por diseño, un cold start.

LIMITACIÓN CONOCIDA: esto mide el cold start "de aplicación" (arranque del
intérprete + imports + construcción de la app FastAPI dentro del contenedor
local), no el cold start "de infraestructura" real de AWS (aprovisionamiento
de red, descarga de la imagen desde el servicio de Lambda, etc.), que no
puede reproducirse sin desplegar a una cuenta real de AWS. Ver ADR-0005.
"""
import argparse
import csv
import re
import statistics
import subprocess
import sys

INIT_RE = re.compile(r"Init Duration:\s*([\d.]+)\s*ms")
DURATION_RE = re.compile(r"(?<!Init )Duration:\s*([\d.]+)\s*ms")
BILLED_RE = re.compile(r"Billed Duration:\s*([\d.]+)\s*ms")


def run_once(event_path: str) -> dict | None:
    result = subprocess.run(
        ["sam", "local", "invoke", "VeriFactsFunction", "--event", event_path],
        capture_output=True,
        text=True,
        shell=(sys.platform == "win32"),
    )
    log = result.stdout + "\n" + result.stderr

    init_match = INIT_RE.search(log)
    if not init_match:
        print("No se encontró 'Init Duration' en esta corrida; últimas líneas:")
        print(log[-1500:])
        return None

    duration_match = DURATION_RE.search(log)
    billed_match = BILLED_RE.search(log)

    return {
        "init_duration_ms": float(init_match.group(1)),
        "duration_ms": float(duration_match.group(1)) if duration_match else None,
        "billed_duration_ms": float(billed_match.group(1)) if billed_match else None,
    }


def percentile(data: list[float], p: float) -> float:
    data_sorted = sorted(data)
    k = (len(data_sorted) - 1) * (p / 100)
    f = int(k)
    c = min(f + 1, len(data_sorted) - 1)
    if f == c:
        return data_sorted[f]
    return data_sorted[f] + (data_sorted[c] - data_sorted[f]) * (k - f)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=30)
    parser.add_argument("--event", default="events/health_event.json")
    parser.add_argument("--out", default="cold_start_results.csv")
    args = parser.parse_args()

    results = []
    for i in range(1, args.runs + 1):
        print(f"Corrida {i}/{args.runs}...", end=" ", flush=True)
        row = run_once(args.event)
        if row is None:
            print("SIN DATOS")
            continue
        print(f"Init Duration = {row['init_duration_ms']:.1f} ms")
        results.append(row)

    if not results:
        print("No se obtuvo ninguna medición válida.")
        sys.exit(1)

    init_values = [r["init_duration_ms"] for r in results]
    duration_values = [r["duration_ms"] for r in results if r["duration_ms"] is not None]

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["init_duration_ms", "duration_ms", "billed_duration_ms"])
        writer.writeheader()
        writer.writerows(results)

    print("\n--- Init Duration (arranque del runtime, ms) ---")
    print(f"n        = {len(init_values)}")
    print(f"mínimo   = {min(init_values):.1f}")
    print(f"mediana  = {statistics.median(init_values):.1f}")
    print(f"P95      = {percentile(init_values, 95):.1f}")
    print(f"máximo   = {max(init_values):.1f}")

    if duration_values:
        print("\n--- Duration (ejecución de la función, ms) ---")
        print("Nota: en esta función, los imports pesados (trafilatura) ocurren")
        print("dentro del handler, no en el arranque del módulo, así que el costo")
        print("real de 'arrancar en frío' aparece aquí, no en Init Duration.")
        print(f"n        = {len(duration_values)}")
        print(f"mínimo   = {min(duration_values):.1f}")
        print(f"mediana  = {statistics.median(duration_values):.1f}")
        print(f"P95      = {percentile(duration_values, 95):.1f}")
        print(f"máximo   = {max(duration_values):.1f}")

    print(f"\nResultados guardados en {args.out}")


if __name__ == "__main__":
    main()