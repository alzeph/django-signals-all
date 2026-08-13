from django.conf import settings
from django.test.signals import setting_changed

SETTINGS_KEY = "DJANGO_SIGNALS_ALL"

DEFAULTS = {
    "FETCH_UPDATED_IDS": True,
    "MAX_FETCH_IDS_LIMIT": 10_000,
    "ENABLE_RAW_SQL_INTERCEPTOR": True,
    "MONITORED_TABLES": None,
    "EXCLUDED_TABLES": ["django_session", "django_migrations"],
    "SQL_PARSER_ENGINE": "sqlglot",
}


class Settings:
    """Accès paresseux au dict DJANGO_SIGNALS_ALL, invalidé par override_settings."""

    def __init__(self, defaults):
        self.defaults = defaults
        self._cached_attrs = set()

    @property
    def user_settings(self):
        return getattr(settings, SETTINGS_KEY, {})

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError(f"Réglage {SETTINGS_KEY} invalide : {attr!r}")
        try:
            value = self.user_settings[attr]
        except KeyError:
            value = self.defaults[attr]
        self._cached_attrs.add(attr)
        setattr(self, attr, value)
        return value

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()


app_settings = Settings(DEFAULTS)


def _reload_settings(*, setting, **kwargs):
    if setting == SETTINGS_KEY:
        app_settings.reload()


setting_changed.connect(_reload_settings)
