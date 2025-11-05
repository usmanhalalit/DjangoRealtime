import asyncio

from .structs import Event, Scope


class RequestQueue(asyncio.Queue):
    """Async queue for SSE request session"""

    def __init__(self, user_id: str, maxsize=100):
        super().__init__(maxsize)
        self.user_id = user_id

    def should_receive(self, event: Event):
        """Only receive events for this user or broadcasts"""
        if event.scope == Scope.PUBLIC:
            return True
        if event.scope == Scope.SYSTEM:
            return False
        if event.scope == Scope.USER and event.user_id is None:
            return False
        return str(event.user_id) == str(self.user_id)
