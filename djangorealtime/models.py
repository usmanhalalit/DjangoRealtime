from django.contrib.postgres.indexes import GinIndex, Index
from django.db import models


class Event(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    type = models.CharField(max_length=255)
    scope = models.CharField(max_length=32)
    detail = models.JSONField()
    user_id = models.CharField(max_length=64, null=True)
    status = models.CharField(max_length=32)
    data_store = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            Index(fields=['user_id'], name='djr_event_user_id_idx'),
            Index(fields=['type'], name='djr_event_type_idx'),
            Index(fields=['status'], name='djr_event_status_idx'),
            Index(fields=['-created_at'], name='djr_event_created_at_idx'),
            GinIndex(
                fields=['detail'],
                name='djr_event_detail_gin',
                opclasses=['jsonb_path_ops']
            ),
            GinIndex(
                name='djr_event_data_store_gin',
                fields=['data_store'],
                opclasses=['jsonb_path_ops'],
            ),
        ]

    def __str__(self):
        return f"{self.type} ({self.id})"

    @property
    def private_data(self) -> dict:
        """Access private data stored in data_store (not sent to frontend)."""
        return self.data_store.get('private_data', {})

    def add_activity(self, status_label, user_id=None):
        """Add an activity record and update status if it's a progression."""
        from django.db import transaction

        from djangorealtime.structs import Status

        with transaction.atomic():
            EventActivity.objects.create(
                event=self,
                status=status_label,
                user_id=str(user_id) if user_id else None,
            )
            new_status = Status(status_label)
            current_status = Status(self.status)
            if new_status.is_progression_from(current_status):
                self.status = status_label
                self.save(update_fields=['status'])

    def data_store_update(self, key, value):
        """Merge a value into a key in data_store (shallow merge)."""
        current_data = self.data_store.get(key, {})
        new_data = {**current_data, **value}
        self.data_store[key] = new_data
        self.save()

    def replay(self):
        """
        Replay this event by republishing it with the same ID.
        Publishes to backend and new activity will be logged to data_store.

        Returns:
            The Event struct that was published
        """
        from djangorealtime.backends.utils import get_backend
        from djangorealtime.structs import Event as EventStruct
        from djangorealtime.structs import Scope

        # Create Event struct with same ID and data
        event = EventStruct(
            id=self.id,
            type=self.type,
            scope=Scope(self.scope),
            detail=self.detail,
            user_id=self.user_id,
        )

        self.status = 'new'
        self.save()

        backend = get_backend()
        backend.publish(event)

        return event


class EventActivity(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='activities')
    status = models.CharField(max_length=32)
    # event receiver user_id
    user_id = models.CharField(max_length=64, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Event activities'
        indexes = [
            Index(fields=['event', '-created_at'], name='djr_activity_event_created_idx'),
        ]

    def __str__(self):
        return f"{self.status} ({self.event_id})"

