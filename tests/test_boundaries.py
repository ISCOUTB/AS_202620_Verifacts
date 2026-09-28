"""S9 · Auditoría de erosión ejecutable (ADR-0001, propiedad de datos de S6).

Falla si la generación de código (o una persona) cruza un límite de módulo.
"""
import ast
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "app"


def _imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    nombres: list[str] = []
    for nodo in ast.walk(tree):
        if isinstance(nodo, ast.ImportFrom) and nodo.module:
            nombres.append(nodo.module)
        elif isinstance(nodo, ast.Import):
            nombres.extend(alias.name for alias in nodo.names)
    return nombres


def _modulo_de(path: Path) -> str | None:
    partes = path.relative_to(APP).parts
    return partes[1] if partes[0] == "modules" and len(partes) > 2 else None


def test_un_modulo_solo_importa_el_service_de_otro_modulo() -> None:
    violaciones = []
    for py in (APP / "modules").rglob("*.py"):
        propio = _modulo_de(py)
        for nombre in _imports(py):
            p = nombre.split(".")
            if p[:2] == ["app", "modules"] and len(p) >= 3 and p[2] != propio:
                if p[3:4] != ["service"]:
                    violaciones.append(f"{py.relative_to(APP)} importa {nombre}")

    assert not violaciones, "Cruce de límite de módulo: " + "; ".join(violaciones)


def test_solo_la_api_toca_persistencia_y_los_modulos_no_conocen_la_api() -> None:
    violaciones = []
    for py in (APP / "modules").rglob("*.py"):
        for nombre in _imports(py):
            if nombre.startswith(("app.persistence", "app.api")):
                violaciones.append(f"{py.relative_to(APP)} importa {nombre}")

    assert not violaciones, "; ".join(violaciones)


def test_sqlite3_solo_se_usa_en_el_repositorio() -> None:
    violaciones = [
        str(py.relative_to(APP))
        for py in APP.rglob("*.py")
        if py.name != "repository.py" and "sqlite3" in _imports(py)
    ]

    assert not violaciones, "Acceso directo a SQLite fuera de repository.py: " + "; ".join(violaciones)
