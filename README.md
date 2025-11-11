# DjangoRealtime

Add realtime capabilities to your Django web app in no time.
No WebSockets, no Channels, no processes to run, no Redis. Just set up and go!

Django + PostgreSQL = Realtime Updates in Browser

## Live Demo
Check out the live demo at and chat in 90s-style chatroom:

[**Chat room**](https://djr.nofuss.site/chat/)

Built with HTMX and 6 lines of vanilla JavaScript! Code is in [examples/chatroom](examples/chatroom).


## Basic Usage

```python
from djangorealtime import publish

publish(user_id=user.id, event_type='task_complete', detail={'task_id': 123, 'status': 'success'})
```

Browsers receive it instantly ✨:

```javascript
window.addEventListener('djr:task_complete', (e) => {
    console.log(e.detail);  // {task_id: 123, status: 'success'}
});
```

## How it works

Built on HTTP Server-Sent Events (SSE) and PostgreSQL pub/sub. Everything is auto-configured:

- **Secure by default** - events are user-scoped by default, not broadcast to everyone
- **Works everywhere** - SSE is your standard HTTP, no WebSocket complexity
- **Scales across workers** - multiple Django processes can communicate via PostgreSQL
- **Zero fluff** - runs on your existing Django + PostgreSQL stack
- **Automatic reconnection** - handles network interruptions seamlessly
- **Event persistence** - events stored in database for reliability and replay
- **Django admin integration** - view and replay events from the admin panel
- **Sync or async views** - keep using sync views, only make sure to use asgi server

## Table of Contents

- [Installation](#installation)
  - [Database Migration](#database-migration)
  - [Frontend Setup](#frontend-setup)
- [Usage](#usage)
  - [Publishing Events](#publishing-events)
    - [User-Scoped Events](#user-scoped-events)
    - [Global Events](#global-events)
    - [System Events](#system-events)
  - [Listening to Events](#listening-to-events)
- [Advanced Features](#advanced-features)
  - [Filtering events for entity](#filtering-events-for-entity)
  - [Listening from Backend](#listening-from-backend)
  - [Event Storage](#event-storage)
  - [Hooks](#hooks)
- [Configuration](#configuration)
  - [Performance and Scalability](#performance-and-scalability)
  - [Settings](#settings)
  - [Manual JavaScript Connection](#manual-javascript-connection)

## Installation

```bash
pip install djrealtime
```

Add to Django:

```python
INSTALLED_APPS = [
    # ...
    'djangorealtime',
]
```

Include URLs for automatic endpoint setup:

```python
urlpatterns = [
    path('realtime/', include('djangorealtime.urls')),
    # ...
]
```

### Database Migration
To create the necessary table, run:
```bash
python manage.py migrate djangorealtime
```

You don't need this step if you disable event storage in [Settings](#settings).

### Frontend Setup
Add this in your base HTML template in `<head>`.
This will add the necessary JavaScript to automatically connect and listen for events:

```html
{% load djangorealtime_tags %}
{% djangorealtime_js %}
```

___

## Usage

### Publishing Events

#### User-Scoped Events
```python
from djangorealtime import publish

publish(user_id=user.id, event_type='task_complete', detail={'task_id': 123, 'status': 'success'})
```

These events are only sent to the specified user who is logged in using Django's authentication system.
`user_id` is the primary key of _your_ user model. It can be string or integer.


#### Global Events
```python
from djangorealtime import publish_global
publish_global(event_type='turn_off_lights', detail={'time': '10:00 PM'})
```

These events are broadcast to all connected clients or browsers, regardless of authentication.

#### System Events
```python
from djangorealtime import publish_system
publish_system(event_type='server_restart', detail={'reason': 'maintenance'})
```

These events are sent to internal system processes only, not to browsers. Like another Django instance or a 
Django management command listening for events.


### Listening to Events
In your JavaScript code, listen to events using DOM events or the helper method. Just listen on `window`
using the `djr:` prefix before your event type.
```javascript
window.addEventListener('djr:task_complete', (e) => {
    console.log(e.detail);  // {task_id: 123, status: 'success'}
});
```

___

## Advanced Features

### Filtering events for entity
You can filter events by entity using a special `:id` field in the `detail` dictionary.
This allows you to listen to both general and specific events. Nifty!

```python
publish(user_id=user.id, event_type='page_imported', detail={':id': 42}) # say, page with ID 42
```

```javascript
// Listen to specific page_imported event for page ID 42
window.addEventListener('djr:page_imported:42', (e) => {
    console.log('Page 42 was imported', e.detail);
});
// djr:page_imported will also be fired
```

### Listening from Backend
You can also listen to events from other backend processes, like Django management commands. You can
subscribe to all events using the `subscribe` decorator.

```python
from djangorealtime import subscribe, Event

@subscribe
def on_event(event: Event):
    print(f"Received {event.scope} event: {event.type} with detail: {event.detail}")
```

### Event Storage
PostgreSQL pub/sub is not persistent. But we built on top of it to provide reliable event storage out of the box.

All events are efficiently stored in your Django database by default. 

There is a limit of 8kB payload per event due to PostgreSQL NOTIFY limitations. We do not think you should even
be passing a fraction of that in normal usage. Use references or IDs in the event detail to keep it light.

Events including detail are stored in the database, so make sure not to pass sensitive information directly.

Set `'ENABLE_EVENT_STORAGE': False` in [settings](#settings) to disable event storage if you don't need it.

#### Django Admin
DjangoRealtime seamlessly integrates with Django admin to provide a simple interface to view events and activities.
You can filter events by type, scope etc. And wait, there's more! You can even replay events directly from the admin interface.

#### Replaying Events
Event model of DjangoRealtime has a `replay()` method to resend the event.

```python
from djangorealtime.models import Event
event = Event.objects.get(id=1)
event.replay()  # Resends the event
```

Or you can replay from Django admin by selecting events and choosing "Replay selected events" action.

### Hooks
You can define custom callback functions to be executed on certain events.

**`ON_RECEIVE_HOOK`**

Called when an event is received by the listener, before any processing. Returning `None` aborts further processing.

```python
from djangorealtime import Event
from datetime import datetime

def on_receive_hook(event: Event) -> Event | None:
    print(f"[ON_RECEIVE_HOOK] Event received: {event.type}")
    event.detail['received_at'] = datetime.now().isoformat()
    return event
```

**`BEFORE_SEND_HOOK`**
Called before sending an event to each client. You can modify or abort the event here.

```python
from djangorealtime import Event
from django.http import HttpRequest

def before_send_hook(event: Event, request: HttpRequest) -> Event | None:
    user_info = "anonymous"
    if hasattr(request, 'user') and request.user.is_authenticated:
        user_info = request.user.email

    print(f"[BEFORE_SEND_HOOK] Sending {event.type} to {user_info}")
    return event
```

Hooks can be set in `DJANGOREALTIME` [settings](#settings).

___

## Configuration

### Performance and Scalability
DjangoRealtime is designed to be lightweight and efficient. We have production apps using DjangoRealtime at scale.

You can use multiple Django instances behind a load balancer. Each instance will have its own listener process.
All Django instances communicate via your PostgreSQL instance.

Please note, a listener will always maintain a single persistent database connection to PostgreSQL. It is optimised for low
database connection count, so it closes the connection after operations.

We've seen very low latency with all features enabled. If you want even lower latency, you can disable event storage by
having `'ENABLE_EVENT_STORAGE': False` in [settings](#settings).

All events use a single PostgreSQL channel. Then we demultiplex events in the listener process based on `type`.

### Settings
All of the settings are optional. Add to your Django `settings.py`:

```python
DJANGOREALTIME = {
    'AUTO_LISTEN': True,  # Auto-start a non-blocking listener thread with web server(default: True)
    'EVENT_MODEL': 'djangorealtime.models.Event',  # If you want to use a custom event model
    'ENABLE_EVENT_STORAGE': True,  # Enable/disable event storage in DB (default: True)

    'ON_RECEIVE_HOOK': callback_function,  # Custom callback on receiving an event
    'BEFORE_SEND_HOOK': callback_function,  # Custom callback before sending an event to clients
}
```
Note: `AUTO_LISTEN`, only, by choice, starts to listen when a web server is running. It does not start automatically 
when running management commands. This is to avoid unnecessary connections when not needed.

If you have a long-running management command like a queue worker that needs to listen to system events, you can start
the listener manually:
```python
from djangorealtime import Listener
listener = Listener()
listener.start()  # Non-blocking
```

Note: you don't need to start an additional listener for publishing an event from another process.
You only need a listener if you want to listen to events on that process.

### Manual JavaScript Connection
By default, JavaScript connection is auto-established when you include the JS snippet using `{% djangorealtime_js %}` tag.
SSE connections are automatically reconnected on network interruptions. In a rare case, some browsers may give up,
we've added another exponential backoff reconnection strategy.

If you want to manually connect, use: `{% djangorealtime_js auto_connect=False %}` and then:

```javascript
DjangoRealtime.connect({
    endpoint: '/realtime/sse/',  // Default
});
```

By default, your HTTP session cookie is used for authentication, like any other AJAX request. If you need token-based
auth etc. pass as query parameters with `endpoint`.
```javascript
DjangoRealtime.connect({
    endpoint: `/realtime/sse/?id_token=${jwt}`,
});
```

Custom headers are not supported in official EventSource SSE helper.

___

## Troubleshooting
Some platforms like DigitalOcean App Platform enforce cache headers that break SSE connections.
Especially if you are using their CDN or domain like *.ondigitalocean.app
You can simply use a proxy like Cloudflare in front of your app. Or you can disable edge caching for SSE endpoint.

## Local Development

For local development, DjangoRealtime supports both ASGI and WSGI servers:

DjangoRealtime works seamlessly with Django's built-in development server (`runserver`), which runs in WSGI mode.
The library automatically detects when you're using `runserver` with WSGI and uses makeshift adapter to support SSE.

## My Production Apps Using DjangoRealtime
- [Canvify](https://canvify.app) - Import Canva designs into Shopify stores
- [EmbedAny](https://embedany.com) - Embed any external content into your Shopify store


## Requirements

- Django >= 5.0
  - With ASGI server (like Hypercorn, Daphne, Uvicorn etc.)
  - psycopg3
- Python >= 3.10
- PostgreSQL >= 14

## Licence
DjangoRealtime is released under the [MIT Licence](LICENSE).
