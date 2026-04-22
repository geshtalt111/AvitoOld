import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def load_env_file(path):
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


load_env_file(BASE_DIR / ".env")


SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-change-me-for-real-project")
DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() == "true"
SERVE_MEDIA = os.environ.get("DJANGO_SERVE_MEDIA", "false").lower() == "true"

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "testserver",
    "avitoold-production.up.railway.app",
    "*",
]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "board",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "market_board.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "market_board.wsgi.application"
ASGI_APPLICATION = "market_board.asgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("SQLITE_PATH", str(BASE_DIR / "db.sqlite3")),
    }
}


AUTH_PASSWORD_VALIDATORS = []


LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True


STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = os.environ.get("MEDIA_ROOT", str(BASE_DIR / "media"))

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "listing_list"
LOGOUT_REDIRECT_URL = "listing_list"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

csrf_trusted_origins_value = os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in csrf_trusted_origins_value.split(",") if origin.strip()
]
if "https://avitoold-production.up.railway.app" not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append("https://avitoold-production.up.railway.app")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


AI_API_URL = os.environ.get(
    "AI_API_URL",
    os.environ.get("OPENROUTER_API_URL", "https://api.openai.com/v1/chat/completions"),
)
AI_API_KEY = os.environ.get("AI_API_KEY", os.environ.get("OPENROUTER_API_KEY", ""))
AI_MODEL = os.environ.get("AI_MODEL", os.environ.get("OPENROUTER_MODEL", "gpt-4o-mini"))
AI_SITE_URL = os.environ.get("AI_SITE_URL", os.environ.get("OPENROUTER_SITE_URL", "http://127.0.0.1:8000"))
AI_APP_NAME = os.environ.get("AI_APP_NAME", os.environ.get("OPENROUTER_APP_NAME", "Phone Helper Board"))

AUTO_CREATE_SUPERUSER = os.environ.get("AUTO_CREATE_SUPERUSER", "false").lower() == "true"
AUTO_CREATE_SUPERUSER_USERNAME = os.environ.get("AUTO_CREATE_SUPERUSER_USERNAME", "admin")
AUTO_CREATE_SUPERUSER_EMAIL = os.environ.get("AUTO_CREATE_SUPERUSER_EMAIL", "admin@example.com")
AUTO_CREATE_SUPERUSER_PASSWORD = os.environ.get("AUTO_CREATE_SUPERUSER_PASSWORD", "admin123456")
