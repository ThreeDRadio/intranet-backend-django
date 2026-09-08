import os

from split_settings.tools import include, optional
import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "threed",
        "USER": "test_user",
        "PASSWORD": "test_password",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

WORDPRESS_USER = ""
WORDPRESS_API_KEY = ""

include(
    "settings/base.py",
    "settings/installed_apps.py",
    "settings/downloads.py",
    optional("local_settings.py"),
    scope=globals(),
)


# Set up Sentry logging levels
sentry_logging = LoggingIntegration(
    level=logging.INFO,        # Captures INFO and above as breadcrumbs
    event_level=logging.ERROR  # Captures ERROR and above as Sentry events
)

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    # Don't keep anything.
    send_default_pii=False,
    integrations=[sentry_logging],
)