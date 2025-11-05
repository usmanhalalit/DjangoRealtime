import pytest

from djangorealtime.models import Event as EventModel
from djangorealtime.structs import Scope

from .conftest import do_publish


@pytest.mark.django_db(transaction=True)
class TestPublish:
    def test_event(self, collect_events):
        event = do_publish()
        assert event.type == 'page_imported'

    def test_collected_events(self, collect_events):
        do_publish()
        assert len(collect_events) >= 3  # At least 1 of each type
        assert collect_events[0].type == 'page_imported'
        assert collect_events[0].detail['page_id'] == 42
        assert collect_events[0].user_id == '2'

    def test_global_event(self, collect_events):
        do_publish()
        global_events = [e for e in collect_events if e.type == 'global_event']
        assert len(global_events) > 0
        assert global_events[0].detail['info'] == 'test'
        assert global_events[0].user_id is None

    def test_system_event(self, collect_events):
        do_publish()
        system_events = [e for e in collect_events if e.type == 'server_restart']
        assert len(system_events) > 0
        assert system_events[0].scope == Scope.SYSTEM

    def test_database_persistence_with_activity(self, collect_events):
        event = do_publish()
        db_event = EventModel.objects.get(id=event.id)
        assert db_event.type == 'page_imported'
        assert db_event.user_id == '2'
        assert len(db_event.data_store['activity']) > 0
        assert 'status' in db_event.data_store['activity'][0]
        assert 'timestamp' in db_event.data_store['activity'][0]




