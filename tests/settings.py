import os

SECRET_KEY = "django-signals-all-test-suite"
DEBUG = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django_signals_all",
    "tests.testapp",
]

MIDDLEWARE = [
    "django_signals_all.sql.middleware.RawSQLSignalMiddleware",
]

ROOT_URLCONF = "tests.urls"

DB_BACKEND = os.environ.get("DSA_TEST_DB", "sqlite")

if DB_BACKEND == "postgres":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DSA_PG_NAME", "django_signals_all"),
            "USER": os.environ.get("DSA_PG_USER", "django_signals_all"),
            "PASSWORD": os.environ.get("DSA_PG_PASSWORD", "django_signals_all"),
            "HOST": os.environ.get("DSA_PG_HOST", "localhost"),
            "PORT": os.environ.get("DSA_PG_PORT", "5432"),
        },
        "secondary": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DSA_PG_NAME", "django_signals_all") + "_secondary",
            "USER": os.environ.get("DSA_PG_USER", "django_signals_all"),
            "PASSWORD": os.environ.get("DSA_PG_PASSWORD", "django_signals_all"),
            "HOST": os.environ.get("DSA_PG_HOST", "localhost"),
            "PORT": os.environ.get("DSA_PG_PORT", "5432"),
        },
    }
elif DB_BACKEND == "mysql":
    # "localhost" force le client MySQL à utiliser un socket Unix local plutôt
    # que TCP, même avec un PORT explicite : on force donc 127.0.0.1 par défaut.
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ.get("DSA_MYSQL_NAME", "django_signals_all"),
            "USER": os.environ.get("DSA_MYSQL_USER", "root"),
            "PASSWORD": os.environ.get("DSA_MYSQL_PASSWORD", "django_signals_all"),
            "HOST": os.environ.get("DSA_MYSQL_HOST", "127.0.0.1"),
            "PORT": os.environ.get("DSA_MYSQL_PORT", "3306"),
        },
        "secondary": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ.get("DSA_MYSQL_NAME", "django_signals_all")
            + "_secondary",
            "USER": os.environ.get("DSA_MYSQL_USER", "root"),
            "PASSWORD": os.environ.get("DSA_MYSQL_PASSWORD", "django_signals_all"),
            "HOST": os.environ.get("DSA_MYSQL_HOST", "127.0.0.1"),
            "PORT": os.environ.get("DSA_MYSQL_PORT", "3306"),
        },
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        },
        "secondary": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        },
    }
