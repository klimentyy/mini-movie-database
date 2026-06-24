from typing import Optional

from django.apps import AppConfig
from django.db.backends.signals import connection_created
from django.dispatch import receiver
from unidecode import unidecode


def remove_accents(input_str: Optional[str]) -> str:
    return unidecode(input_str).lower() if input_str else ""


@receiver(connection_created)
def extend_sqlite_functions(sender, connection, **kwargs):
    if connection.vendor == "sqlite":
        connection.ensure_connection()
        raw_sqlite_conn = connection.connection
        if raw_sqlite_conn:
            connection.connection.create_function("remove_accents", 1, remove_accents)


class MoviesConfig(AppConfig):
    name = "movies"
