from .config import Config


def execute_on_receive_hook(event):
    """
    Execute hook when event is received from backend (before signal emission).

    Args:
        event: Event object with event data

    Returns:
        - None: abort the event
        - Event: continue with original or modified event
    """
    hook = Config.ON_RECEIVE_HOOK
    if not hook:
        return event

    result = hook(event)
    if result is False or result is None:
        return None  # Abort
    return result if result else event


def execute_before_send_hook(event, request):
    """
    Execute hook before sending event to each client.
    Runs for EVERY client connection individually.

    Args:
        event: Event object about to be sent
        request: The Django request object for this SSE connection

    Returns:
        - None or False: don't send to this client
        - Event: send this (possibly modified) event to client
    """
    hook = Config.BEFORE_SEND_HOOK
    if not hook:
        return event

    result = hook(event, request)
    if result is False or result is None:
        return None  # Don't send to this client
    return result if result else event
