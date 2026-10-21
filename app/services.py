"""Reglas de negocio y traducción de errores de acceso a datos."""
import mysql.connector

from app import db
from app.config import Settings


class DatabaseUnavailable(Exception):
    pass


class ProcedureNotFound(Exception):
    pass


class DatabaseQueryError(Exception):
    pass


def _ensure_configured(settings: Settings) -> None:
    missing = settings.missing_database_settings()
    if missing:
        raise DatabaseUnavailable("Configuración de base de datos incompleta: " + ", ".join(missing))


def check_database(settings: Settings) -> None:
    _ensure_configured(settings)
    try:
        db.check_connection(settings)
    except mysql.connector.Error as exc:
        raise DatabaseUnavailable("No fue posible conectar con MySQL.") from exc


def get_automoviles(settings: Settings) -> list[dict]:
    _ensure_configured(settings)
    try:
        return db.fetch_automoviles(settings)
    except mysql.connector.Error as exc:
        if getattr(exc, "errno", None) == 1305:
            raise ProcedureNotFound("El procedimiento configurado no existe o no está accesible.") from exc
        if isinstance(exc, (mysql.connector.InterfaceError, mysql.connector.OperationalError)):
            raise DatabaseUnavailable("No fue posible conectar con MySQL.") from exc
        raise DatabaseQueryError("MySQL rechazó la consulta del procedimiento.") from exc
