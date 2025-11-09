# DjangoRealtime Example Project

This Django project demonstrates DjangoRealtime with two example apps:

## Apps

### 1. Playground - SSE Testing Tool
A simple tool to test Server-Sent Events functionality.
- **URL**: `/`
- **Features**: Send test messages, view event stream, connection status

### 2. Chatroom - 90's Style Group Chat
A retro-styled chatroom built with pure HTMX and DjangoRealtime.
- **URL**: `/chat/`
- **Features**: Real-time group chat, with history 
- **Tech**: HTMX + DjangoRealtime

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL
- [Task](https://taskfile.dev/) (optional but recommended)

### Setup

```bash
# Install dependencies
task install

# Create database and run migrations
task db:create
task migrate

# Run the server
task run
```

Or use the all-in-one command:
```bash
task dev
```

### Manual Setup

```bash
# Install dependencies
uv pip install -r requirements.txt

# Create database
psql postgres -c "CREATE DATABASE djangorealtime-test;"

# Run migrations (from parent directory)
cd /path/to/djangorealtime
python examples/manage.py migrate

# Run server (from parent directory)
python -m hypercorn examples.asgi:application --bind 0.0.0.0:8000 --reload
```

## Available Commands

```bash
task install          # Install dependencies
task db:create        # Create PostgreSQL database
task db:drop          # Drop PostgreSQL database
task db:reset         # Reset database (drop, create, migrate)
task migrate          # Run migrations
task makemigrations   # Create migrations
task superuser        # Create superuser
task shell            # Open Django shell
task run              # Run development server
task dev              # Full setup and run
task clean            # Clean Python cache files
```

## URLs

- `/` - Homepage (index of example apps)
- `/playground/` - Playground (SSE tester)
- `/chat/` - Chatroom
- `/admin/` - Django admin
- `/realtime/` - DjangoRealtime SSE endpoint

## Configuration

Database settings in `examples/settings.py`:
- **Database**: `djangorealtime-test`
- **Host**: `127.0.0.1`
- **Port**: `5432`

## Architecture

Both apps use DjangoRealtime's event-based architecture:
- Events stored in `djangorealtime.models.Event`
- PostgreSQL pub/sub for real-time delivery
- SSE for client connections
- No polling required!
