from collections.abc import Callable

from django.dispatch import receiver

from .backends.utils import get_backend
from .signals import internal_signal
from .structs import Event, Scope, Status

_backend = None

def _get_backend():
    """Lazy backend initialization"""
    global _backend
    if _backend is None:
        _backend = get_backend()
    return _backend

def publish(user_id: str|int, event_type: str, detail: dict | None = None):
    """
    Publish an event to all connected clients.

    Args:
        user_id: ID of the user (str or int)
        event_type: String identifier for the event type
        detail: Dict with event details (optional)

    Returns:
        The published event dict
    """
    event = Event(type=event_type, detail=detail or {}, scope=Scope.USER, user_id=str(user_id))
    event.persist()
    _get_backend().publish(event)

    return event


def publish_global(event_type: str, detail: dict | None = None):
    """
    Publish a global event to all connected clients.

    Args:
        event_type: String identifier for the event type
        detail: Dict with event details (optional)

    Returns:
        The published event dict

    Example:
        publish_global('system_announcement', {'message': 'Server maintenance at midnight'})
        publish_global('news_update', {'headline': 'Breaking News!'})
        publish_global('simple_event')
    """
    event = Event(type=event_type, detail=detail or {}, scope=Scope.PUBLIC)
    event.persist()
    _get_backend().publish(event)

    return event


def publish_system(event_type: str, detail: dict | None = None):
    """
    Publish a system event (sent to backend subscribers, not to SSE clients).
    """
    event = Event(type=event_type, detail=detail or {}, scope=Scope.SYSTEM)
    event.persist()
    _get_backend().publish(event)

    return event


def subscribe(callback: Callable[[Event], None]) -> Callable:
    """
    Subscribe to all events from the backend.
    Can be used as a decorator or regular function.
    """
    def wrapped(sender, event, **kwargs):
        callback(event)
        event.update_status(status=Status.DISPATCHED)

    return receiver(internal_signal, weak=False)(wrapped)
