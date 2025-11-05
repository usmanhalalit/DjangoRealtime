import json
import sys
import uuid
from dataclasses import asdict, dataclass
from enum import Enum

from django.apps import apps

from .config import Config

# StrEnum is only available in Python 3.11+
if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    class StrEnum(str, Enum):
        """Compatibility StrEnum for Python 3.10"""
        pass


@dataclass
class Struct:
    def to_dict(self, exclude_private=True):
        result = asdict(self)
        if exclude_private:
            result = {k: v for k, v in result.items() if not k.startswith('_')}
        return result

    def to_json(self, exclude_private=True):
        return json.dumps(self.to_dict(exclude_private=exclude_private))

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls(**data)


class Scope(StrEnum):
    PUBLIC = 'public'
    USER = 'user'
    SYSTEM = 'system'


class Status(StrEnum):
    NEW = 'new'
    DISPATCHED = 'dispatched'
    SENT = 'sent'
    DELIVERED = 'delivered'
    READ = 'read'
    ERROR = 'error'

    def is_progression_from(self, other: 'Status') -> bool:
        """Check if this status is a forward progression from another status"""
        members = list(Status)
        return members.index(self) > members.index(other)


@dataclass
class Event(Struct):
    type: str
    scope: Scope
    detail: dict
    user_id: str = None
    id: str = None
    skip_storage: bool = False

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())

    def persist(self, status: Status = Status.NEW):
        if self.skip_storage or not Config.ENABLE_EVENT_STORAGE:
            return None
        event_model = apps.get_model(Config.EVENT_MODEL)
        m = event_model.objects.create(
            id=self.id,
            type=self.type,
            scope=self.scope,
            detail=self.detail,
            user_id=self.user_id,
            status=status.value,
            data_store={
                'activity': [],
            },
        )
        return m

    def update_status(self, status: Status, user_id: str | None = None):
        if self.skip_storage or not Config.ENABLE_EVENT_STORAGE:
            return None

        event_model = apps.get_model(Config.EVENT_MODEL)

        event_model.append_activity_with_lock(
            event_id=self.id,
            status_label=status.value,
            user_id=user_id
        )

        return None
