from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from asgiref.sync import sync_to_async

from djangorealtime import views
from djangorealtime.structs import Event, Scope


@pytest.fixture()
def event():
    return Event(**{
        "type": "page_imported",
        "scope": "public",
        "detail": {"page_id": 42},
    })

@pytest_asyncio.fixture()
async def event_stream_gen():
    request = MagicMock(spec=['method'])
    gen = views.event_stream(request)
    await gen.__anext__()
    yield gen
    views.sse_connections.clear()

@pytest_asyncio.fixture()
async def dispatch_event():
    """Helper to persist and dispatch an event (simulates production flow without backend)"""
    async def _dispatch(event):
        await sync_to_async(event.persist)()
        await sync_to_async(views._on_event)(sender='test', event=event)
    return _dispatch


class TestQueue:
    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_placeholder(self, event_stream_gen, event, dispatch_event):
        await dispatch_event(event)
        queue = next(iter(views.sse_connections))
        queue_item = queue.get_nowait()
        assert queue_item.type == 'page_imported'


class TestUserFiltering:
    @pytest_asyncio.fixture()
    async def user_queue(self):
        request = MagicMock()
        request.user.pk = 123
        gen = views.event_stream(request)
        await gen.__anext__()
        yield next(iter(views.sse_connections))
        views.sse_connections.clear()

    @pytest_asyncio.fixture()
    async def matching_event(self, user_queue, dispatch_event):
        event = Event(type='page_imported', scope=Scope.USER, user_id='123', detail={'page_id': 42})
        await dispatch_event(event)
        return user_queue.get_nowait()

    @pytest_asyncio.fixture()
    async def non_matching_event(self, user_queue, dispatch_event):
        event = Event(type='page_imported', scope=Scope.USER, user_id='456', detail={'page_id': 42})
        await dispatch_event(event)
        return user_queue

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_matching_user_receives_event(self, matching_event):
        assert matching_event.user_id == '123'

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_different_user_no_event(self, non_matching_event):
        assert non_matching_event.empty()


class TestEvent:
    def test_event_to_dict(self, event):
        event_dict = event.to_dict()
        assert event_dict['type'] == 'page_imported'
        assert event_dict['detail']['page_id'] == 42

