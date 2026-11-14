import logging
import sys

from corsheaders.defaults import default_headers
import sentry_sdk
from sentry_sdk.integrations.logging import (
    LoggingIntegration,
    ignore_logger,
    ignore_logger_for_sentry_logs,
)
from split_settings.tools import include, optional

from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")
DEBUG = env("DEBUG")
DATABASES = {
    "default": env.db(
        "LOGGER_DB_URL",
        default="postgres://test_user:test_password@localhost:5432/threed",
        engine="django.db.backends.postgresql_psycopg2",
    ),
    "msglist": env.db(
        "MSGLIST_DB_URL",
        default="postgres://test_user:test_password@localhost:5432/msglist",
        engine="django.db.backends.postgresql_psycopg2",
    ),
}
DATABASE_ROUTERS = ["message_bank.routers.MessageBankRouter"]
WORDPRESS_USER = env("WORDPRESS_USER")
WORDPRESS_API_KEY = env("WORDPRESS_API_KEY")
WORDPRESS_URL = "https://threedradio.com/wp-json/wp/v2"
# Internals
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
CORS_ORIGIN_WHITELIST = env.list(
    "CORS_ORIGIN_WHITELIST", default=["https://localhost", "https://127.0.0.1"]
)
CORS_ALLOW_HEADERS = list(default_headers) + env.list(
    "CORS_ALLOW_HEADERS_ADDITIONAL", default=[]
)
API_PREFIX = env("API_PREFIX", default="/")
CORS_ORIGIN_ALLOW_ALL = env.bool("CORS_ORIGIN_ALLOW_ALL", default=False)
DOWNLOAD_BASE_PATH = env("DOWNLOAD_BASE_PATH", default="/")
DOWNLOAD_X_SENDFILE = env.bool("DOWNLOAD_X_SENDFILE", default=False)
STATIC_URL = env("STATIC_URL", default="/static/")

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
