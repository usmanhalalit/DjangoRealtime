from datetime import datetime

from django.http import HttpRequest

from djangorealtime.structs import Event


def on_receive_hook(event: Event) -> Event | None:
    """Process event when received from backend (runs once)."""
    print(f"[ON_RECEIVE_HOOK] Event received: {event.type}")
    event.detail['received_at'] = datetime.now().isoformat()
    return event


def before_send_hook(event: Event, request: HttpRequest) -> Event | None:
    """Process event before sending to each client (runs per frontend connection)."""
    user_info = "anonymous"
    if hasattr(request, 'user') and request.user.is_authenticated:
        user_info = request.user.email

    print(f"[BEFORE_SEND_HOOK] Sending {event.type} to {user_info}")

    # Add user-specific data
    modified_event = Event(
        type=event.type,
        detail={
            **event.detail,
            'sent_to': user_info,
            'sent_at': datetime.now().isoformat()
        },
        scope=event.scope,
        user_id=event.user_id
    )

    return modified_event
