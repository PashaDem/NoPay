from os import environ
from pathlib import Path

from celery.schedules import crontab

ASGI_APPLICATION = "nopay.asgi.application"

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = environ.get("DJANGO_SECRET_KEY")

DEBUG = True

ALLOWED_HOSTS = ["*"]

APPS = (
    "user_auth.apps.UserAuthConfig",
    "qrcode_app.apps.QrcodeAppConfig",
    "advertisement.apps.AdvertisementConfig",
    "feature_toggles.apps.FeatureTogglesConfig",
)

INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "rest_framework.authtoken",
    "drf_spectacular",
    "django_extensions",
    "django_celery_results",
    "django_celery_beat",
    "channels",
    *APPS,
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "nopay.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
CORS_ALLOW_ALL_ORIGINS = True

WSGI_APPLICATION = "nopay.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": environ.get("POSTGRES_DB"),
        "USER": environ.get("POSTGRES_USER"),
        "PASSWORD": environ.get("POSTGRES_PASSWORD"),
        "HOST": environ.get("POSTGRES_HOST"),
        "PORT": environ.get("POSTGRES_PORT"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Donwloading files into celery
DOWNLOAD_DIR = "/usr/src/app/files/"

# REST SETTINGS

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # 'rest_framework.authentication.BasicAuthentication',
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# Minio settings
MINIO_HOST = "minio:9000"
MINIO_DJANGO_USER = environ.get("MINIO_DJANGO_USER")
MINIO_DJANGO_PASSWORD = environ.get("MINIO_DJANGO_PASSWORD")
MINIO_BUCKET_NAME = "qrcodes"

# Celery
CELERY_BROKER_URL = "redis://redis:6379"
CELERY_RESULT_BACKEND = "redis://redis:6379"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# Cache settings
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

QRCODE_EXPIRATION_HOURS = environ.get("QRCODE_EXPIRATION_TIME", 2)

CELERY_BEAT_SCHEDULE = {
    "clear_not_relevant_qrcodes": {
        "task": "qrcode_app.tasks.clear_not_relevant_qrcodes",
        "schedule": crontab(hour=f"*/{QRCODE_EXPIRATION_HOURS}"),
    },
}

NOTIFICATIONS_CHECK_TIMEOUT_SEC = int(
    environ.get("NOTIFICATIONS_CHECK_TIMEOUT_SEC", 30)
)
