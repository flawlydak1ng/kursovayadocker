import pytest

from app import MemoryRepo, create_app


@pytest.fixture()
def client():
    app = create_app(MemoryRepo())
    app.config.update(TESTING=True)
    return app.test_client()


def test_health_ok(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_version_has_env_and_version(client):
    data = client.get("/api/version").get_json()
    assert set(data) == {"version", "env"}


def test_add_and_list_note(client):
    created = client.post("/api/notes", json={"text": "первая заметка"})
    assert created.status_code == 201
    notes = client.get("/api/notes").get_json()
    assert notes == [{"id": 1, "text": "первая заметка"}]


def test_empty_text_is_rejected(client):
    response = client.post("/api/notes", json={"text": "   "})
    assert response.status_code == 400


def test_delete_note(client):
    note_id = client.post("/api/notes", json={"text": "x"}).get_json()["id"]
    assert client.delete(f"/api/notes/{note_id}").status_code == 204
    assert client.delete(f"/api/notes/{note_id}").status_code == 404
