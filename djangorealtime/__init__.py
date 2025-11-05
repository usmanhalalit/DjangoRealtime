"""
DjangoRealtime - Real-time events for Django using PostgreSQL LISTEN/NOTIFY

Basic usage:
    from djangorealtime import publish, publish_global

    # Publish to specific user
    publish(user_id=123, event_type='notification', detail={'message': 'Hello'})

    # Publish to all users
    publish_global(event_type='announcement', detail={'message': 'System update'})
"""

# Main API
# Core components
from .listener import Listener
from .publisher import publish, publish_global, publish_system, subscribe
from .structs import Event, Scope, Status

__version__ = '0.1.0'

__all__ = [
    'Event',
    'Listener',
    'Scope',
    'Status',
    'publish',
    'publish_global',
    'publish_system',
    'subscribe',
]
