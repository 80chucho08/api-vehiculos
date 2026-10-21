from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app import services


def settings(**kwargs):
    values = dict(db_host="host", db_port=3306, db_name="db", db_user="user", db_password="pw", db_procedure_automoviles="obtener_autos")
    values.update(kwargs)
    return Settings(**values)


def test_health_does_not_need_database():
    client = TestClient(create_app(Settings()))
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_db_health_success(monkeypatch):
    monkeypatch.setattr(services.db, "check_connection", lambda _settings: None)
    response = TestClient(create_app(settings())).get("/health/db")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}


def test_db_health_missing_configuration():
    response = TestClient(create_app(Settings())).get("/health/db")
    assert response.status_code == 503
    assert "DB_HOST" in response.json()["detail"]


def test_automoviles_returns_procedure_records(monkeypatch):
    expected = [{"id": 7, "marca": "Toyota"}]
    monkeypatch.setattr(services.db, "fetch_automoviles", lambda _settings: expected)
    response = TestClient(create_app(settings())).get("/api/automoviles")
    assert response.status_code == 200
    assert response.json() == expected


def test_automoviles_reports_unavailable(monkeypatch):
    def fail(_settings):
        raise services.DatabaseUnavailable("No fue posible conectar con MySQL.")
    monkeypatch.setattr(services, "get_automoviles", fail)
    response = TestClient(create_app(settings())).get("/api/automoviles")
    assert response.status_code == 503
    assert response.json()["error"] == "database_unavailable"


def test_procedure_not_found_response(monkeypatch):
    def fail(_settings):
        raise services.ProcedureNotFound("No existe.")
    monkeypatch.setattr(services, "get_automoviles", fail)
    response = TestClient(create_app(settings())).get("/api/automoviles")
    assert response.status_code == 502
    assert response.json()["error"] == "procedure_not_found"
