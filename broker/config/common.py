import os
from os.path import join
from configurations import Configuration
import psycopg2

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Common(Configuration):
    INSTALLED_APPS = (
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        # Third party apps
        "rest_framework",  # utilities for rest apis
        "rest_framework_json_api",  # add json api compliance
        "rest_framework.authtoken",  # token authentication
        "django_filters",  # for filtering rest endpoints
        "silk",  # for API troubleshooting
        # Your apps
        "broker.users",
        "broker.blockchains",
    )

    # https://docs.djangoproject.com/en/2.0/topics/http/middleware/
    MIDDLEWARE = (
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        "silk.middleware.SilkyMiddleware",
    )

    ALLOWED_HOSTS = ["*"]
    ROOT_URLCONF = "broker.urls"
    SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
    # WSGI_APPLICATION

    # Email
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

    ADMINS = (("Author", "mxyakovenko9@gmail.com"),)

    # Postgres
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["DJANGO_POSTGRES_DB"],
            "USER": os.environ["DJANGO_POSTGRES_USER"],
            "PASSWORD": os.environ["DJANGO_POSTGRES_PASSWORD"],
            "HOST": os.environ["DJANGO_POSTGRES_HOST"],
            "PORT": int(os.getenv("DJANGO_POSTGRES_PORT", 5432)),
            "CONN_MAX_AGE": int(os.getenv("DJANGO_POSTGRES_CONN_MAX_AGE", 600)),
            "ATOMIC_REQUESTS": True,
            "OPTIONS": {
                "isolation_level": psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED,
            },
        }
    }

    # General
    APPEND_SLASH = False
    TIME_ZONE = "UTC"
    LANGUAGE_CODE = "en-us"
    # If you set this to False, Django will make some optimizations so as not
    # to load the internationalization machinery.
    USE_I18N = False
    USE_L10N = True
    USE_TZ = True
    LOGIN_REDIRECT_URL = "/"

    # Storages
    # https://docs.djangoproject.com/en/5.2/ref/settings/#storages
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/2.0/howto/static-files/
    STATIC_ROOT = os.path.normpath(join(os.path.dirname(BASE_DIR), "static"))
    STATICFILES_DIRS = [f"{BASE_DIR}/templates", "templates"]
    STATIC_URL = "/static/"

    STATICFILES_FINDERS = (
        "django.contrib.staticfiles.finders.FileSystemFinder",
        "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    )

    # Media files
    MEDIA_ROOT = join(os.path.dirname(BASE_DIR), "media")
    MEDIA_URL = "/media/"

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": STATICFILES_DIRS,
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

    # Set DEBUG to False as a default for safety
    # https://docs.djangoproject.com/en/dev/ref/settings/#debug
    DEBUG = os.getenv("DJANGO_DEBUG", "no").lower() in ("true", "1", "yes")

    # Password Validation
    # https://docs.djangoproject.com/en/2.0/topics/auth/passwords/#module-django.contrib.auth.password_validation
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

    # Logging
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "django.server": {
                "()": "django.utils.log.ServerFormatter",
                "format": "[%(server_time)s] %(message)s",
            },
            "verbose": {
                "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"
            },
            "simple": {"format": "%(levelname)s %(message)s"},
        },
        "filters": {
            "require_debug_true": {
                "()": "django.utils.log.RequireDebugTrue",
            },
        },
        "handlers": {
            "django.server": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "django.server",
            },
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "simple",
            },
            "mail_admins": {
                "level": "ERROR",
                "class": "django.utils.log.AdminEmailHandler",
            },
        },
        "loggers": {
            "django": {
                "handlers": ["console"],
                "propagate": True,
            },
            "django.server": {
                "handlers": ["django.server"],
                "level": "INFO",
                "propagate": False,
            },
            "django.request": {
                "handlers": ["mail_admins", "console"],
                "level": "ERROR",
                "propagate": False,
            },
            "django.db.backends": {"handlers": ["console"], "level": "INFO"},
        },
    }

    # Custom user app
    AUTH_USER_MODEL = "users.User"

    # Django Rest Framework
    REST_FRAMEWORK = {
        "DEFAULT_PAGINATION_CLASS": "rest_framework_json_api.pagination.JsonApiPageNumberPagination",
        "PAGE_SIZE": int(os.getenv("DJANGO_PAGINATION_LIMIT", 10)),
        "EXCEPTION_HANDLER": "rest_framework_json_api.exceptions.exception_handler",
        "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S%z",
        "DEFAULT_PARSER_CLASSES": ("rest_framework_json_api.parsers.JSONParser",),
        "DEFAULT_RENDERER_CLASSES": (
            "rest_framework_json_api.renderers.JSONRenderer",
            # If you're performance testing, you will want to use the browseable API
            # without forms, as the forms can generate their own queries.
            # If performance testing, enable:
            # 'example.utils.BrowsableAPIRendererWithoutForms',
            # Otherwise, to play around with the browseable API, enable:
            "rest_framework_json_api.renderers.BrowsableAPIRenderer",
        ),
        "DEFAULT_FILTER_BACKENDS": (
            "rest_framework_json_api.filters.QueryParameterValidationFilter",
            "rest_framework_json_api.filters.OrderingFilter",
            "rest_framework_json_api.django_filters.DjangoFilterBackend",
            "rest_framework.filters.SearchFilter",
        ),
        "SEARCH_PARAM": "filter[search]",
        "DEFAULT_METADATA_CLASS": "rest_framework_json_api.metadata.JSONAPIMetadata",
        "DEFAULT_PERMISSION_CLASSES": [
            "rest_framework.permissions.IsAuthenticated",
        ],
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "rest_framework.authentication.SessionAuthentication",
            "rest_framework.authentication.TokenAuthentication",
        ),
        "TEST_REQUEST_RENDERER_CLASSES": (
            "rest_framework_json_api.renderers.JSONRenderer",
        ),
        "TEST_REQUEST_DEFAULT_FORMAT": "vnd.api+json",
    }
