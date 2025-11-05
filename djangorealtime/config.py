"""
Configuration for DjangoRealtime.

All settings are configured via the DJANGOREALTIME dict in Django settings.

Example in settings.py:
    DJANGOREALTIME = {
        'BACKEND': 'djangorealtime.backends.postgresql.PostgreSqlBackend',
        'AUTO_LISTEN': True,
        'ENABLE_EVENT_STORAGE': True,
        'EVENT_MODEL': 'djangorealtime.Event',
        'ON_RECEIVE_HOOK': callable,
        'BEFORE_SEND_HOOK': callable,
    }
"""

from django.conf import settings


class Config:
    """Configuration container for DjangoRealtime settings."""

    # Default values
    BACKEND = None
    AUTO_LISTEN = True
    ENABLE_EVENT_STORAGE = True
    EVENT_MODEL = 'djangorealtime.Event'
    ON_RECEIVE_HOOK = None
    BEFORE_SEND_HOOK = None

    @classmethod
    def load(cls):
        """Load configuration from Django settings."""
        config_dict = getattr(settings, 'DJANGOREALTIME', {})

        cls.BACKEND = config_dict.get('BACKEND', None)
        cls.AUTO_LISTEN = config_dict.get('AUTO_LISTEN', True)
        cls.ENABLE_EVENT_STORAGE = config_dict.get('ENABLE_EVENT_STORAGE', True)
        cls.EVENT_MODEL = config_dict.get('EVENT_MODEL', 'djangorealtime.Event')
        cls.ON_RECEIVE_HOOK = config_dict.get('ON_RECEIVE_HOOK', None)
        cls.BEFORE_SEND_HOOK = config_dict.get('BEFORE_SEND_HOOK', None)
