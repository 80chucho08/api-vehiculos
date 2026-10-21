"""Acceso a MySQL mediante mysql-connector-python."""
from contextlib import contextmanager
from typing import Iterator

import mysql.connector

from app.config import Settings


@contextmanager
def connection(settings: Settings) -> Iterator[mysql.connector.MySQLConnection]:
    conn = mysql.connector.connect(
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        connection_timeout=settings.db_connect_timeout,
    )
    try:
        yield conn
    finally:
        conn.close()


def check_connection(settings: Settings) -> None:
    with connection(settings) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        finally:
            cursor.close()


def fetch_automoviles(settings: Settings) -> list[dict]:
    """Ejecuta solo el procedimiento configurado y convierte su primer result set."""
    with connection(settings) as conn:
        cursor = conn.cursor()
        try:
            cursor.callproc(settings.db_procedure_automoviles)
            records: list[dict] = []
            for result in cursor.stored_results():
                columns = result.column_names
                records.extend(dict(zip(columns, row)) for row in result.fetchall())
                result.close()
            return records
        finally:
            cursor.close()
