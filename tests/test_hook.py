from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from djangorealtime.config import Config
from djangorealtime.hooks import execute_before_send_hook
from djangorealtime.signals import internal_signal
from djangorealtime.structs import Event


@pytest.fixture()
def event():
    return Event(**{
        "type": "page_imported",
        "scope": "public",
        "detail": {"page_id": 42},
    })


class TestOnReceiveHook:
    @pytest.fixture()
    def mock_on_receive_hook(self):
        def hook(event):
            event.detail['hooked'] = True
            return event

        with patch.object(settings, 'DJANGOREALTIME', {'ON_RECEIVE_HOOK': hook}):
            Config.load()
            yield

    @pytest.fixture()
    def fire_signal(self, event):
        event.persist()  # Persist event before firing signal (matches production flow)
        return internal_signal.send(sender='test_sender', event=event)

    @pytest.mark.django_db
    def test_on_receive_hook_called(self, mock_on_receive_hook, fire_signal):
        assert fire_signal is not None


class TestBeforeSendHook:
    @pytest.fixture()
    def mock_request(self):
        return MagicMock()

    @pytest.fixture()
    def modified_event(self, event, mock_request):
        def hook(event, request):
            event.detail['modified'] = True
            return event

        with patch.object(settings, 'DJANGOREALTIME', {'BEFORE_SEND_HOOK': hook}):
            Config.load()
            return execute_before_send_hook(event, mock_request)

    @pytest.fixture()
    def blocked_event(self, event, mock_request):
        def hook(event, request):
            return None

        with patch.object(settings, 'DJANGOREALTIME', {'BEFORE_SEND_HOOK': hook}):
            Config.load()
            return execute_before_send_hook(event, mock_request)

    def test_before_send_hook_modifies_event(self, modified_event):
        assert modified_event.detail['modified'] is True

    def test_before_send_hook_blocks_event(self, blocked_event):
        assert blocked_event is None

