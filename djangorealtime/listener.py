import threading
from uuid import uuid4

from django.db import connection

from djangorealtime.backends.utils import get_backend
from djangorealtime.hooks import execute_on_receive_hook
from djangorealtime.signals import internal_signal
from djangorealtime.structs import Event
from djangorealtime.thread_pool import submit_task
from djangorealtime.utils import logger


class Listener:
    def __init__(self):
        self.instance_id = uuid4()
        self.backend = get_backend()
        self._thread = None

    def start(self):
        """Start listener in a background thread"""
        self._thread = threading.Thread(target=self._listen, daemon=True)
        self._thread.start()

    def _listen(self):
        logger.info(f"Starting listener: {self.instance_id}")

        for payload in self.backend.listen('djangorealtime'):
            submit_task(self._handle_event, payload)

    def _handle_event(self, payload):
        try:
            event = Event.from_json(payload)

            # Execute on-receive hook with parsed data
            processed_event = execute_on_receive_hook(event)
            if processed_event is None:
                return  # Hook aborted the event

            internal_signal.send(sender=self.instance_id, event=processed_event)
        except Exception as e:
            logger.error(f"Error handling event: {e}", exc_info=True)
        finally:
            connection.close()


