import pytest

from app.config import Settings, validate_procedure_name


@pytest.mark.parametrize("name", ["sp_obtener_autos", "catalogo.consultar_autos", "_autos2"])
def test_valid_procedure_names(name):
    assert validate_procedure_name(name) == name


@pytest.mark.parametrize("name", ["x; DROP TABLE autos", "proc()", "db.proc.extra", "1proc", "`proc`"])
def test_invalid_procedure_names(name):
    with pytest.raises(ValueError):
        validate_procedure_name(name)


def test_settings_from_environment(monkeypatch):
    monkeypatch.setenv("APP_PORT", "5100")
    monkeypatch.setenv("DB_PROCEDURE_AUTOMOVILES", "catalogo.listar")
    monkeypatch.setenv("CORS_ORIGINS", "https://frontend.example, http://localhost:5173")
    config = Settings.from_env(load_file=False)
    assert config.app_port == 5100
    assert config.db_procedure_automoviles == "catalogo.listar"
    assert config.cors_origins == ("https://frontend.example", "http://localhost:5173")


def test_wildcard_cors_is_rejected(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "*")
    with pytest.raises(ValueError):
        Settings.from_env(load_file=False)
