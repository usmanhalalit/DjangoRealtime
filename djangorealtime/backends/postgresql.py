from collections.abc import Generator

from django.db import connection

from ..retry import retry_generator
from ..structs import Event
from ..utils import logger
from .base import BaseRealtimeBackend


class PostgreSqlBackend(BaseRealtimeBackend):
    def __init__(self, **options):
        super().__init__(**options)
        self.channel_name = options.get('channel', 'djangorealtime')
        self._connection = None

    def connect(self) -> None:
        # Close any existing broken connection
        connection.close()

        connection.ensure_connection()
        self._connection = connection.connection

    def publish(self, event: Event) -> None:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT pg_notify(%s, %s);",
                [self.channel_name, event.to_json()]
            )

    @retry_generator(delay=1, max_delay=60, backoff=2)
    def listen(self, channel: str) -> Generator[str, None, None]:
        logger.info(f"Connecting to PostgreSQL channel: {self.channel_name}")
        self.connect()

        with self._connection.cursor() as cursor:
            cursor.execute(f"LISTEN {self.channel_name};")

        logger.info(f"Listening on channel: {self.channel_name}")

        for notify in self._connection.notifies():
            yield notify.payload

        # Connection closed - raise to trigger retry
        logger.error("PostgreSQL connection closed, reconnecting...")
        self._connection = None
        raise ConnectionError("PostgreSQL connection closed unexpectedly")
