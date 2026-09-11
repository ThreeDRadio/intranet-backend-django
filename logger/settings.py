import logging
import sys

import sentry_sdk
from sentry_sdk.integrations.logging import (
    LoggingIntegration,
    ignore_logger,
    ignore_logger_for_sentry_logs,
)
from split_settings.tools import include, optional

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
WORDPRESS_URL = "https://threedradio.com/wp-json/wp/v2"

include(
    "settings/base.py",
    "settings/installed_apps.py",
    "settings/downloads.py",
    optional("local_settings.py"),
    scope=globals(),
)

IS_TESTING = "test" in sys.argv

if not IS_TESTING:
    sentry_logging = LoggingIntegration(
        level=logging.INFO,
        event_level=logging.ERROR,
        capture_sentry_logs=True,
        sentry_logs_level=logging.INFO,
    )

    ignore_logger("django.server")
    ignore_logger("django.utils.autoreload")
    ignore_logger_for_sentry_logs("django.server")
    ignore_logger_for_sentry_logs("django.utils.autoreload")

    sentry_sdk.init(
        send_default_pii=False,
        integrations=[sentry_logging],
    )
