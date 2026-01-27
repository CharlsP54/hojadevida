from pathlib import Path
import os
from decouple import config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# Seguridad / Entorno
# =========================
SECRET_KEY = config("SECRET_KEY", default="django-insecure-cv-key")
DEBUG = config("DEBUG", default=False, cast=bool)

# Detectar entorno
IN_RENDER = bool(os.environ.get("RENDER"))

# =========================
# Hosts permitidos
# =========================
# En producción, aceptamos el dominio de Render y localhost
ALLOWED_HOSTS = ["*"] # Dejamos * temporalmente para asegurar que no sea error de dominio

# =========================
# CSRF Trusted Origins
# =========================
CSRF_TRUSTED_ORIGINS = ["https://*.onrender.com"]

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
    "cv", # Tu app principal
]

# =========================
# Middleware
# =========================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware", # Vital para Render
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "hojadevida.urls"

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
# Base de datos
# =========================
# Usamos un fallback seguro por si olvidas poner la variable en local
default_db = "sqlite:///" + str(BASE_DIR / "db.sqlite3")

DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL", default=default_db),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# =========================
# Passwords
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
# Static & Media
# =========================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# CAMBIO IMPORTANTE: Usamos CompressedStaticFilesStorage
# La versión "Manifest" da error 500 si falta algún archivo referenciado. Esta es más segura.
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =========================
# Seguridad Producción
# =========================
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True