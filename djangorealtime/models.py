from django.contrib.postgres.indexes import GinIndex, Index
from django.db import models
from django.db.models.expressions import RawSQL


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

    @classmethod
    def append_activity_with_lock(cls, event_id, status_label, user_id=None):
        from django.db import transaction

        from djangorealtime.structs import Status

        with transaction.atomic():
            # Lock row to prevent concurrent modifications
            current = cls.objects.select_for_update().get(id=event_id)

            # Check if new status is a progression from current status
            new_status = Status(status_label)
            current_status = Status(current.status)
            should_update_status = new_status.is_progression_from(current_status)

            # Build jsonb_build_object call conditionally based on user_id
            if user_id is not None:
                jsonb_fields = "'status', %s, 'timestamp', NOW(), 'user_id', %s"
                params = [status_label, user_id]
            else:
                jsonb_fields = "'status', %s, 'timestamp', NOW()"
                params = [status_label]

            update_args = {
                "data_store": RawSQL(
                    f"""
                    jsonb_set(
                        COALESCE(data_store, '{{}}'::jsonb),
                        '{{activity}}',
                        COALESCE(data_store->'activity', '[]'::jsonb) ||
                            jsonb_build_object({jsonb_fields}),
                        true
                    )
                    """,
                    params,
                ),
            }

            # Only update status field if it's a progression
            if should_update_status:
                update_args["status"] = status_label

            cls.objects.filter(id=event_id).update(**update_args)

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

