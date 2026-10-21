"""Carga y validación de configuración desde variables de entorno."""
from dataclasses import dataclass
import os
import re

from dotenv import load_dotenv

_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)?$")


def validate_procedure_name(name: str) -> str:
    """Acepta un nombre SQL simple, opcionalmente calificado por esquema."""
    if not _IDENTIFIER.fullmatch(name):
        raise ValueError("DB_PROCEDURE_AUTOMOVILES debe ser un identificador SQL válido (nombre o esquema.nombre).")
    return name


@dataclass(frozen=True)
class Settings:
    app_name: str = "API Automoviles"
    app_host: str = "0.0.0.0"
    app_port: int = 5000
    app_env: str = "development"
    db_host: str = ""
    db_port: int = 3306
    db_name: str = ""
    db_user: str = ""
    db_password: str = ""
    db_connect_timeout: int = 5
    db_procedure_automoviles: str = ""
    cors_origins: tuple[str, ...] = ("http://localhost:5173",)

    @classmethod
    def from_env(cls, *, load_file: bool = True) -> "Settings":
        if load_file:
            load_dotenv()
        def integer(key: str, default: int) -> int:
            try:
                return int(os.getenv(key, str(default)))
            except ValueError as exc:
                raise ValueError(f"{key} debe ser un número entero.") from exc

        procedure = os.getenv("DB_PROCEDURE_AUTOMOVILES", "").strip()
        if procedure and not procedure.startswith("REEMPLAZAR_"):
            validate_procedure_name(procedure)
        origins = tuple(x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if x.strip())
        if "*" in origins:
            raise ValueError("CORS_ORIGINS no admite '*' como origen.")
        settings = cls(
            app_name=os.getenv("APP_NAME", "API Automoviles"),
            app_host=os.getenv("APP_HOST", "0.0.0.0"),
            app_port=integer("APP_PORT", 5000),
            app_env=os.getenv("APP_ENV", "development"),
            db_host=os.getenv("DB_HOST", "").strip(),
            db_port=integer("DB_PORT", 3306),
            db_name=os.getenv("DB_NAME", "").strip(),
            db_user=os.getenv("DB_USER", "").strip(),
            db_password=os.getenv("DB_PASSWORD", ""),
            db_connect_timeout=integer("DB_CONNECT_TIMEOUT", 5),
            db_procedure_automoviles=procedure,
            cors_origins=origins,
        )
        if not 1 <= settings.app_port <= 65535 or not 1 <= settings.db_port <= 65535:
            raise ValueError("Los puertos deben estar entre 1 y 65535.")
        if settings.db_connect_timeout < 1:
            raise ValueError("DB_CONNECT_TIMEOUT debe ser mayor que cero.")
        return settings

    def missing_database_settings(self) -> list[str]:
        required = ("DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD", "DB_PROCEDURE_AUTOMOVILES")
        return [key for key in required if not getattr(self, key.lower()) or getattr(self, key.lower()).startswith("REEMPLAZAR_")]
