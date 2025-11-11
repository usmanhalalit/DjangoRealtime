from datetime import datetime

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from djangorealtime.models import Event
from djangorealtime.publisher import publish_global


def index(request):
    """Main chat room view"""
    if not request.user.is_authenticated:
        return redirect('chatroom:login')

    # Load recent chat messages from stored events
    recent_messages = Event.objects.filter(
        type='chat_message'
    ).order_by('-created_at')[:50]

    # Keep reversed order for flex-col-reverse (newest first in HTML)
    messages = list(recent_messages)

    return render(request, 'chatroom/chat.html', {
        'user': request.user,
        'messages': messages,
    })


def login_view(request):
    """Simple login view for demo purposes"""
    if request.method == 'POST':
        username = request.POST.get('username')

        if not username:
            return render(request, 'chatroom/login.html', {'error': 'Username required'})

        user, _ = User.objects.get_or_create(username=username)

        # Log them in without password (demo only!)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        return redirect('chatroom:index')

    return render(request, 'chatroom/login.html')


@require_http_methods(["POST"])
@login_required
def send_message(request):
    """
    HTMX endpoint to send a chat message.
    Publishes event via SSE - HTMX will refresh to show new messages.
    """
    message_text = request.POST.get('message', '').strip()

    if not message_text:
        return HttpResponse('', status=204)

    # Create message data
    message_data = {
        'username': request.user.username,
        'message': message_text,
        'timestamp': datetime.now().isoformat(),
    }

    # Publish to all connected clients via SSE
    publish_global('chat_message', message_data)

    # Return empty response - HTMX will trigger refresh via SSE
    return HttpResponse('', status=204)


@login_required
def get_messages(request):
    """
    HTMX endpoint to fetch messages partial.
    Triggered on page load and when SSE events arrive.
    Supports pagination via offset parameter.
    """
    # Get pagination parameters
    offset = int(request.GET.get('offset', 0))
    limit = 20

    # Fetch messages with pagination
    messages_queryset = Event.objects.filter(
        type='chat_message'
    ).order_by('-created_at')[offset:offset + limit]

    messages = list(messages_queryset)

    # Calculate next offset for infinite scroll
    next_offset = offset + limit if len(messages) == limit else None

    return render(request, 'chatroom/partials/messages_list.html', {
        'messages': messages,
        'current_user': request.user,
        'next_offset': next_offset,
    })
