"""
Django settings for hojadevida project.
"""

from pathlib import Path
import os

from decouple import config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# Seguridad / Entorno
# =========================

SECRET_KEY = config("SECRET_KEY", default="dev-secret-key")
DEBUG = config("DEBUG", default=False, cast=bool)

# =========================
# Hosts (FIX definitivo para Azure)
# =========================
# En Azure usa: ALLOWED_HOSTS="*"
raw_hosts = config("ALLOWED_HOSTS", default="").strip()

if not raw_hosts:
    # Si no definiste nada, dejamos abierto para evitar caídas por probes internos
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = [h.strip() for h in raw_hosts.split(",") if h.strip()]
    # Si alguien puso "*" en la lista, normalizamos a ["*"] (Django lo acepta así)
    if "*" in ALLOWED_HOSTS:
        ALLOWED_HOSTS = ["*"]
    else:
        # Agrega el hostname que Azure expone automáticamente
        website_hostname = os.environ.get("WEBSITE_HOSTNAME")
        if website_hostname and website_hostname not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(website_hostname)

# =========================
# CSRF Trusted Origins
# =========================
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="").split(",")
CSRF_TRUSTED_ORIGINS = [o.strip() for o in CSRF_TRUSTED_ORIGINS if o.strip()]

# En Azure, si NO lo defines, Django puede bloquear POST/login/admin.
# Lo ideal es definirlo en variables, por ejemplo:
# CSRF_TRUSTED_ORIGINS="https://hojadevidaa-xxxxx.azurewebsites.net"
# Si quieres fallback automático:
website_hostname = os.environ.get("WEBSITE_HOSTNAME")
if website_hostname:
    auto_origin = f"https://{website_hostname}"
    if auto_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(auto_origin)

# =========================
# Apps
# =========================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cv",
]

# =========================
# Middleware
# =========================

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

ROOT_URLCONF = "hojadevida.urls"

# =========================
# Templates
# =========================

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

WSGI_APPLICATION = "hojadevida.wsgi.application"

# =========================
# Base de datos (solo por DATABASE_URL)
# =========================
DATABASE_URL = config(
    "DATABASE_URL",
    default="postgresql://postgres:postgres123@localhost:5432/x"
)

DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        ssl_require=not DEBUG,   # en Azure normalmente True
    )
}

# =========================
# Validación de passwords
# =========================

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# =========================
# Internacionalización
# =========================

LANGUAGE_CODE = "es"
TIME_ZONE = "America/Guayaquil"
USE_I18N = True
USE_TZ = True

# =========================
# Static files (WhiteNoise)
# =========================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media (en App Service no es persistente sin storage externo)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =========================
# Ajustes producción (Azure)
# =========================

if not DEBUG:
    # Azure pasa el proto real por X-Forwarded-Proto
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    # Redirección a HTTPS (puedes apagarla con variable si quieres)
    SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # HSTS: puedes subirlo luego; por ahora suave para no bloquearte
    SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=60, cast=int)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    X_FRAME_OPTIONS = "DENY"
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "same-origin"

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {"console": {"class": "logging.StreamHandler"}},
        "root": {"handlers": ["console"], "level": "INFO"},
    }

