"""Notes API - небольшой REST-сервис для демонстрации тестовых сред."""
import os

from flask import Flask, jsonify, request


class MemoryRepo:
    """Хранилище в памяти. Используется в юнит-тестах, без базы данных."""

    def __init__(self):
        self._items = {}
        self._seq = 0

    def list(self):
        return [self._items[key] for key in sorted(self._items)]

    def add(self, text):
        self._seq += 1
        item = {"id": self._seq, "text": text}
        self._items[self._seq] = item
        return item

    def delete(self, note_id):
        return self._items.pop(note_id, None) is not None

    def ping(self):
        return True


class PgRepo:
    """Хранилище в PostgreSQL (драйвер psycopg 3)."""

    def __init__(self, dsn):
        self._dsn = dsn

    def _connect(self):
        import psycopg

        return psycopg.connect(self._dsn, connect_timeout=3)

    def list(self):
        with self._connect() as conn:
            rows = conn.execute("SELECT id, text FROM notes ORDER BY id").fetchall()
        return [{"id": row[0], "text": row[1]} for row in rows]

    def add(self, text):
        with self._connect() as conn:
            row = conn.execute(
                "INSERT INTO notes (text) VALUES (%s) RETURNING id, text", (text,)
            ).fetchone()
        return {"id": row[0], "text": row[1]}

    def delete(self, note_id):
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM notes WHERE id = %s", (note_id,))
            return cur.rowcount > 0

    def ping(self):
        with self._connect() as conn:
            conn.execute("SELECT 1")
        return True


def create_app(repo=None):
    app = Flask(__name__)
    version = os.environ.get("APP_VERSION", "dev")
    env_name = os.environ.get("ENV_NAME", "local")
    if repo is None:
        repo = PgRepo(os.environ["DATABASE_URL"])

    @app.get("/api/health")
    def health():
        try:
            repo.ping()
        except Exception:  # noqa: BLE001 - любая ошибка БД означает "degraded"
            return jsonify(status="degraded"), 503
        return jsonify(status="ok")

    @app.get("/api/version")
    def get_version():
        return jsonify(version=version, env=env_name)

    @app.get("/api/notes")
    def list_notes():
        return jsonify(repo.list())

    @app.get("/api/stats")
    def stats():
        return jsonify(count=len(repo.list()))

    @app.post("/api/notes")
    def add_note():
        payload = request.get_json(silent=True) or {}
        text = str(payload.get("text", "")).strip()
        if not text:
            return jsonify(error="text is required"), 400
        return jsonify(repo.add(text)), 201

    @app.delete("/api/notes/<int:note_id>")
    def delete_note(note_id):
        if not repo.delete(note_id):
            return jsonify(error="not found"), 404
        return "", 204

    return app
