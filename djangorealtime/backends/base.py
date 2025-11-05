from abc import ABC, abstractmethod
from collections.abc import Generator

from ..structs import Event


class BaseRealtimeBackend(ABC):
    def __init__(self, **options):
        self.options = options

    @abstractmethod
    def publish(self, event: Event) -> None:
        raise NotImplementedError

    @abstractmethod
    def listen(self, channel: str) -> Generator[str, None, None]:
        raise NotImplementedError
