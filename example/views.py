import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from djangorealtime.publisher import publish, publish_global


def test_page(request):
    return render(request, 'test_sse.html')


@require_http_methods(["POST"])
@csrf_exempt  # For testing
def send_test_message(request):
    """Endpoint to receive test messages and broadcast them via SSE"""
    data = json.loads(request.body)
    event_type = data.get('type', 'test_event')
    detail = {
        'message': data.get('message', ''),
        'sender': 'test_ui'
    }

    # Check if global publish is requested
    is_global = data.get('is_global', False)

    if is_global:
        publish_global(event_type, detail)
    else:
        publish(request.user.id, event_type, detail)

    return JsonResponse({'status': 'success', 'message': 'Event published'})
