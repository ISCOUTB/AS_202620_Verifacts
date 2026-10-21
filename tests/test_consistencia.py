"""Verifica contra la implementación las garantías de consistencia de VeriFacts.

Cada prueba corresponde a una fila de la tabla "operación → garantía" de
docs/arc42/08-conceptos-transversales.md (sección 8.6). Las dos últimas
documentan límites conocidos (no son una promesa): si algún día se corrigen,
la prueba debe actualizarse junto con el documento.
"""
from fastapi.testclient import TestClient

from app.main import app
from app.persistence.repository import count_analyses, get_analysis


client = TestClient(app)

TEXTO = "Texto de prueba de consistencia: Todos deben leerlo!!!"


def _crear(texto: str = TEXTO) -> dict:
    response = client.post("/analysis", json={"text": texto})

    assert response.status_code == 200

    return response.json()


# --- Operación 1: POST /analysis (crear) -----------------------------------


def test_post_deja_el_registro_confirmado_y_legible_desde_otra_conexion() -> None:
    """Atomicidad y durabilidad: cuando la API responde, el registro ya está
    confirmado (commit) y una conexión nueva lo ve completo."""
    creado = _crear()

    guardado = get_analysis(creado["id"])

    assert guardado is not None
    assert guardado["content"] == TEXTO
    assert guardado["score"] == creado["score"]
    assert guardado["classification"] == creado["classification"]
    assert guardado["factors"] == creado["factors"]
    assert guardado["created_at"] == creado["created_at"]


def test_post_no_es_idempotente_pero_el_calculo_es_determinista() -> None:
    """Hoy un reintento crea un registro nuevo (MF-05 pendiente), aunque el
    resultado calculado es idéntico (Q-05)."""
    antes = count_analyses()

    primero = _crear()
    segundo = _crear()

    assert primero["id"] != segundo["id"]
    assert count_analyses() == antes + 2
    assert (primero["score"], primero["classification"], primero["factors"]) == (
        segundo["score"],
        segundo["classification"],
        segundo["factors"],
    )


# --- Operación 2: GET /analysis/{id} (consultar) ---------------------------


def test_get_por_id_es_repetible_y_no_modifica_el_estado() -> None:
    creado = _crear()
    antes = count_analyses()

    primera = client.get(f"/analysis/{creado['id']}")
    segunda = client.get(f"/analysis/{creado['id']}")

    assert primera.status_code == segunda.status_code == 200
    assert primera.json() == segunda.json()
    assert count_analyses() == antes


def test_get_de_id_inexistente_responde_404_sin_crear_registros() -> None:
    antes = count_analyses()

    response = client.get("/analysis/999999999")

    assert response.status_code == 404
    assert count_analyses() == antes


# --- Operación 3: GET /analysis (listado paginado) -------------------------


def test_listado_informa_el_total_almacenado_en_la_cabecera() -> None:
    _crear()

    response = client.get("/analysis?limit=5")

    assert response.status_code == 200
    assert int(response.headers["X-Total-Count"]) == count_analyses()
    assert len(response.json()) <= 5


def test_limite_conocido_paginacion_por_offset_puede_repetir_un_elemento() -> None:
    """Límite documentado (8.6): lista y total son consultas separadas y el
    OFFSET se desplaza si se inserta entre dos páginas."""
    _crear()
    _crear()

    pagina_1 = client.get("/analysis?limit=2&offset=0").json()
    _crear()
    pagina_2 = client.get("/analysis?limit=2&offset=2").json()

    assert pagina_1[1]["id"] == pagina_2[0]["id"]
