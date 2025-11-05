from django.utils.module_loading import import_string

from ..config import Config


def get_backend():
    """
    Get the configured realtime backend instance.

    Returns the backend based on DJANGOREALTIME['BACKEND'] setting,
    defaults to PostgreSQL backend.
    """
    backend_config = Config.BACKEND or 'djangorealtime.backends.postgresql.PostgreSqlBackend'

    if isinstance(backend_config, dict):
        backend_path = backend_config['CLASS']
        options = backend_config.get('OPTIONS', {})
        backend_class = import_string(backend_path)
        return backend_class(**options)

    backend_class = import_string(backend_config)
    return backend_class()
