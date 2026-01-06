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

# Detecta si está corriendo en Azure App Service
IN_AZURE = bool(os.environ.get("WEBSITE_SITE_NAME") or os.environ.get("WEBSITE_HOSTNAME"))

# =========================
# Hosts permitidos
# =========================
# Lee ALLOWED_HOSTS desde variables (separadas por coma)
raw_hosts = config("ALLOWED_HOSTS", default="").strip()

if raw_hosts:
    ALLOWED_HOSTS = [h.strip() for h in raw_hosts.split(",") if h.strip()]
else:
    ALLOWED_HOSTS = []

# Si estás en Azure y NO estás en DEBUG, lo más estable es permitir todos los hosts
# para evitar fallas por IPs internas (169.254.x.x) usadas por health checks/probes.
if IN_AZURE and not DEBUG:
    ALLOWED_HOSTS = ["*"]
else:
    # En local, agrega defaults razonables
    if not ALLOWED_HOSTS:
        ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

    # Agrega el hostname que Azure asigna (si existe)
    website_hostname = os.environ.get("WEBSITE_HOSTNAME")
    if website_hostname:
        ALLOWED_HOSTS.append(website_hostname)

    # Quita duplicados manteniendo orden
    seen = set()
    ALLOWED_HOSTS = [x for x in ALLOWED_HOSTS if not (x in seen or seen.add(x))]

# =========================
# CSRF Trusted Origins
# =========================
raw_csrf = config("CSRF_TRUSTED_ORIGINS", default="").strip()
CSRF_TRUSTED_ORIGINS = [o.strip() for o in raw_csrf.split(",") if o.strip()]

# Si estás en Azure, agrega el dominio https://<app>.azurewebsites.net automáticamente
# (Esto ayuda cuando entras por el dominio de Azure)
if IN_AZURE:
    website_hostname = os.environ.get("WEBSITE_HOSTNAME")
    if website_hostname:
        origin = f"https://{website_hostname}"
        if origin not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(origin)

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
DATABASE_URL = config(
    "DATABASE_URL",
    default="postgresql://postgres:postgres123@localhost:5432/x"
)

DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        ssl_require=(IN_AZURE and not DEBUG),
    )
}

# =========================
# Validación de passwords (admin/users)
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
# Static files
# =========================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =========================
# Seguridad en producción (Azure)
# =========================
if IN_AZURE and not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

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
