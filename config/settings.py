import os
from pathlib import Path

from dotenv import load_dotenv


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


# ============================================================
# HELPER
# ============================================================

def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


# ============================================================
# SECURITY
# ============================================================

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "insecure-dev-key-change-me",
)

DEBUG = os.environ.get(
    "DJANGO_DEBUG",
    "false",
).lower() == "true"


ALLOWED_HOSTS = [
    "sih-web-app-v4ze.onrender.com",
    "localhost",
    "127.0.0.1",
]


CSRF_TRUSTED_ORIGINS = [
    "https://sih-web-app-v4ze.onrender.com",
]


# ============================================================
# INSTALLED APPS
# ============================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",

    "accounts.apps.AccountsConfig",
    "core.apps.CoreConfig",
    "facilities.apps.FacilitiesConfig",
    "programmes.apps.ProgrammesConfig",
    "blog.apps.BlogConfig",
    "public.apps.PublicConfig",
    "staff.apps.StaffConfig",
]


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    "core.middleware.AuditAccessLogMiddleware",
    "core.middleware.SecurityHeadersMiddleware",
]


# ============================================================
# URL CONFIGURATION
# ============================================================

ROOT_URLCONF = "config.urls"


# ============================================================
# TEMPLATES
# ============================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site_globals",
            ],
        },
    },
]


# ============================================================
# WSGI / ASGI
# ============================================================

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# ============================================================
# DATABASE
# ============================================================
#
# Django's default SQLite database.
#
# No DATABASE_URL
# No PostgreSQL
# No DB_HOST
# No DB_PORT
# No database server required
#
# The database file will be:
#
# BASE_DIR / "db.sqlite3"
#
# ============================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ============================================================
# PASSWORD VALIDATION
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ============================================================
# CUSTOM USER MODEL
# ============================================================

AUTH_USER_MODEL = "accounts.User"

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"


# ============================================================
# INTERNATIONALIZATION
# ============================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = os.environ.get(
    "DJANGO_TIME_ZONE",
    "Africa/Lagos",
)

USE_I18N = True
USE_TZ = True


# ============================================================
# STATIC FILES
# ============================================================

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"


# ============================================================
# MEDIA FILES
# ============================================================

MEDIA_URL = os.environ.get(
    "MEDIA_URL",
    "/media/",
)

MEDIA_ROOT = BASE_DIR / "media"


# ============================================================
# SESSION / COOKIE SECURITY
# ============================================================

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = "Lax"

X_FRAME_OPTIONS = "DENY"


# ============================================================
# PRODUCTION SECURITY
# ============================================================

if not DEBUG:

    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )

    SECURE_CONTENT_TYPE_NOSNIFF = True

    use_ssl = (
        os.environ.get(
            "DJANGO_SECURE_SSL",
            "false",
        ).lower()
        == "true"
    )

    if use_ssl:

        SECURE_SSL_REDIRECT = True

        SESSION_COOKIE_SECURE = True
        CSRF_COOKIE_SECURE = True

        SECURE_HSTS_SECONDS = _env_int(
            "DJANGO_HSTS_SECONDS",
            31536000,
        )

        SECURE_HSTS_INCLUDE_SUBDOMAINS = True
        SECURE_HSTS_PRELOAD = True


# ============================================================
# DEFAULT PRIMARY KEY
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ============================================================
# FILE UPLOAD LIMIT
# ============================================================

MAX_UPLOAD_SIZE_MB = _env_int(
    "MAX_UPLOAD_SIZE_MB",
    8,
)

DATA_UPLOAD_MAX_MEMORY_SIZE = (
    MAX_UPLOAD_SIZE_MB * 1024 * 1024
)


# ============================================================
# AI ASSISTANT
# ============================================================

AI_PROVIDER = os.environ.get(
    "AI_PROVIDER",
    "rules",
)

AI_API_KEY = os.environ.get(
    "AI_API_KEY",
    "",
)

AI_MODEL = os.environ.get(
    "AI_MODEL",
    "",
)


# ============================================================
# EMAIL
# ============================================================

NOTIFICATION_EMAIL_ENABLED = (
    os.environ.get(
        "NOTIFICATION_EMAIL_ENABLED",
        "false",
    ).lower()
    == "true"
)

DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL",
    "no-reply@spak.local",
)

EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)

EMAIL_HOST = os.environ.get(
    "EMAIL_HOST",
    "",
)

EMAIL_PORT = _env_int(
    "EMAIL_PORT",
    587,
)

EMAIL_HOST_USER = os.environ.get(
    "EMAIL_HOST_USER",
    "",
)

EMAIL_HOST_PASSWORD = os.environ.get(
    "EMAIL_HOST_PASSWORD",
    "",
)

EMAIL_USE_TLS = (
    os.environ.get(
        "EMAIL_USE_TLS",
        "false",
    ).lower()
    == "true"
)


# ============================================================
# LOGGING
# ============================================================

_LOG_DIR = BASE_DIR / "logs"

_root_handlers = [
    "console",
]

try:
    os.makedirs(
        _LOG_DIR,
        exist_ok=True,
    )

    with open(
        _LOG_DIR / "spak.log",
        "a",
    ):
        pass

    _root_handlers.append("file")

except OSError:
    _root_handlers = [
        "console",
    ]


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "simple": {
            "format": (
                "{levelname} "
                "{asctime} "
                "{message}"
            ),
            "style": "{",
        },
    },

    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": _LOG_DIR / "spak.log",
            "maxBytes": 5_000_000,
            "backupCount": 3,
            "formatter": "simple",
        },

        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },

    "root": {
        "handlers": _root_handlers,
        "level": "INFO",
    },
}
