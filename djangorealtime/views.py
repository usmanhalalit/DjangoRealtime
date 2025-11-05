import asyncio
import contextlib
import json

from django.db import connection
from django.http import StreamingHttpResponse

from djangorealtime.hooks import execute_before_send_hook
from djangorealtime.publisher import subscribe
from djangorealtime.queues import RequestQueue
from djangorealtime.structs import Event, Scope, Status
from djangorealtime.thread_pool import run_in_thread

sse_connections = set()


@subscribe
def _on_event(event: Event):
    """Handle events and broadcast to connected clients"""
    if event.scope == Scope.SYSTEM:
        return
    for queue in sse_connections:
        if queue.should_receive(event):
            with contextlib.suppress(asyncio.QueueFull):
                queue.put_nowait(event)


def _get_user_id(request):
    if not hasattr(request, 'user') or not hasattr(request.user, 'pk'):
        return None
    user_id = request.user.pk
    return str(user_id) if user_id is not None else None


def _process_event(event, request, user_id):
    try:
        processed = execute_before_send_hook(event, request)
        if not processed:
            return None

        event.update_status(status=Status.SENT, user_id=user_id)

        detail = processed.detail or {}
        detail['type'] = processed.type
        return f"data: {json.dumps(detail)}\n\n"
    finally:
        connection.close()


async def event_stream(request):
    request_user_id = await run_in_thread(_get_user_id, request)
    queue = RequestQueue(user_id=request_user_id)
    sse_connections.add(queue)

    try:
        yield f"data: {json.dumps({'type': 'connected'})}\n\n"
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=1)
            except asyncio.TimeoutError:
                yield ": heartbeat\n\n"
                continue

            # message = await sync_to_async(_process_event)(event, request)
            message = await run_in_thread(_process_event, event, request, request_user_id)
            # message = await _process_event(event, request)
            if message:
                yield message
    finally:
        sse_connections.discard(queue)


async def sse_view(request):
    return StreamingHttpResponse(
        event_stream(request),
        content_type='text/event-stream',
        headers={'Cache-Control': 'no-cache'}
    )


def async_generator_to_sync(async_gen_func):  # pragma: no cover
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            async_gen = async_gen_func(*args, **kwargs)
            while True:
                chunk = loop.run_until_complete(async_gen.__anext__())
                yield chunk
        finally:
            loop.close()

    return wrapper


def sse_view_sync(request):  # pragma: no cover
    return StreamingHttpResponse(
        async_generator_to_sync(event_stream)(request),
        content_type='text/event-stream',
        headers={'Cache-Control': 'no-cache'}
    )
