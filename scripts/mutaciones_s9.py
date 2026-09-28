"""S9 · Demuestra que las pruebas nuevas fallan cuando deben.

Aplica un defecto a la vez sobre una COPIA temporal del repositorio y ejecuta:
  - la suite previa (sin las pruebas de S9), y
  - las pruebas nuevas de S9.
Uso (desde la raíz del repositorio):  python scripts/mutaciones_s9.py
"""
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
NUEVAS = ["tests/test_scoring_boundaries.py", "tests/test_boundaries.py"]

MUTACIONES = [
    ("M1 frontera `<` -> `<=` en 30", "app/modules/scoring/service.py",
     "if score < UMBRAL_RIESGO_MEDIO:", "if score <= UMBRAL_RIESGO_MEDIO:"),
    ("M2 umbral alto 60 -> 50", "app/modules/scoring/service.py",
     "UMBRAL_RIESGO_ALTO = 60 ", "UMBRAL_RIESGO_ALTO = 50 "),
    ("M3 sin tope de 100", "app/modules/scoring/service.py",
     "min(score, MAX_SCORE)", "score"),
    ("M4 peso sensacionalismo 20 -> 25", "app/modules/analysis/analyzer.py",
     "points=20", "points=25"),
    ("M5 scoring importa analyzer.py (cruza límite)", "app/modules/scoring/service.py",
     "from app.modules.analysis.service import Finding",
     "from app.modules.analysis.analyzer import Finding"),
]


def correr(destino: Path, args: list[str]) -> str:
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *args],
                       cwd=destino, capture_output=True, text=True)
    return "PASA (no detecta)" if r.returncode == 0 else "FALLA (detecta)"


def main() -> None:
    filas = []
    for nombre, archivo, viejo, nuevo in MUTACIONES:
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / "repo"
            shutil.copytree(RAIZ, destino, ignore=shutil.ignore_patterns(
                ".git", "frontend", "node_modules", "__pycache__", ".venv", "data", "serverless-prototype"))
            ruta = destino / archivo
            texto = ruta.read_text(encoding="utf-8")
            assert texto.count(viejo) == 1, f"{nombre}: patrón no encontrado exactamente una vez"
            ruta.write_text(texto.replace(viejo, nuevo), encoding="utf-8")
            previa = correr(destino, [f"--ignore={n}" for n in NUEVAS])
            nueva = correr(destino, NUEVAS)
        filas.append((nombre, previa, nueva))
        print(f"{nombre:52} | suite previa: {previa:18} | pruebas S9: {nueva}")

    salida = RAIZ / "docs" / "evidencia" / "mutaciones-s9.md"
    salida.parent.mkdir(parents=True, exist_ok=True)
    lineas = [f"# Evidencia S9 — defectos inducidos ({date.today().isoformat()})", "",
              "Generado por `scripts/mutaciones_s9.py`. Cada defecto se aplica solo, sobre una copia temporal.", "",
              "| Defecto inducido | Suite previa a S9 | Pruebas nuevas de S9 |", "|---|---|---|"]
    lineas += [f"| {n} | {p} | {q} |" for n, p, q in filas]
    salida.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"\nEscrito: {salida.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
