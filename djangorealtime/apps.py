import os
import sys

from django.apps import AppConfig

from djangorealtime.config import Config
from djangorealtime.listener import Listener


class DjangorealtimeConfig(AppConfig):
    name = 'djangorealtime'

    def ready(self):
        # Load configuration from Django settings
        Config.load()

        # Check if auto-listen is enabled (defaults to True)
        auto_listen = Config.AUTO_LISTEN

        # Only start listener if auto_listen is True and running under a web server
        if auto_listen and self._is_running_server():
            listener = Listener()
            listener.start()

    def _is_running_server(self):
        """Check if we're running as a web server (not a management command)"""

        # Check for runserver in command line args
        if len(sys.argv) > 1 and 'runserver' in sys.argv:
            # Only start in the worker process, not the reloader
            return os.environ.get('RUN_MAIN') == 'true'

        # Check for ASGI handlers (for production servers)
        return 'django.core.handlers.asgi' in sys.modules

