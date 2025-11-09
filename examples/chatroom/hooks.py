from datetime import datetime

from django.http import HttpRequest

from djangorealtime.structs import Event


def on_receive_hook(event: Event) -> Event | None:
    """
    Called once when an event is received from the backend.
    Adds timestamp to all chat messages.
    """
    if event.type == 'chat_message':
        event.detail['timestamp'] = datetime.now().isoformat()

    return event


def before_send_hook(event: Event, request: HttpRequest) -> Event | None:
    """
    Called before sending to each client.
    Adds user context to events.
    """
    # Add user info if authenticated
    if request.user.is_authenticated:
        event.detail['viewer_username'] = request.user.username

    return event
