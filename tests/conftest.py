import getpass
import os
import time

import django
import pytest
from django.conf import settings

from djangorealtime import Listener, publish, publish_global, subscribe

# Configure Django before tests are collected
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test-secret-key',
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'djangorealtime',
        ],
        MIDDLEWARE=[
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
        ],
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.environ.get('POSTGRES_DB', 'djangorealtime-test'),
                'USER': os.environ.get('POSTGRES_USER', os.getenv('PGUSER', getpass.getuser())),
                'PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''),
                'HOST': os.environ.get('POSTGRES_HOST', '127.0.0.1'),
                'PORT': os.environ.get('POSTGRES_PORT', '5432'),
            }
        },
        ROOT_URLCONF='',
        DJANGOREALTIME={
            'AUTO_LISTEN': False,  # Don't start listener in tests
        },
    )
    django.setup()


@pytest.fixture(scope='session', autouse=True)
def django_settings():
    yield settings


# Shared fixtures for end-to-end tests
COLLECTED_EVENTS = []


def do_publish():
    from djangorealtime import publish_system
    event = publish(2, 'page_imported', {'page_id': 42, ':id': 42})
    time.sleep(0.1)
    publish_global('global_event', {'info': 'test'})
    time.sleep(0.1)
    publish_system('server_restart', {'reason': 'maintenance'})
    time.sleep(0.1)
    return event


@pytest.fixture
def start_listener():
    listener = Listener()
    listener.start()
    time.sleep(0.1)
    yield listener


@subscribe
def _test_handler(event):
    """Global test event collector"""
    COLLECTED_EVENTS.append(event)

@pytest.fixture
def collect_events(start_listener):
    COLLECTED_EVENTS.clear()
    yield COLLECTED_EVENTS
    COLLECTED_EVENTS.clear()
