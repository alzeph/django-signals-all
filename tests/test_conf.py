from django.test import SimpleTestCase, override_settings

from django_signals_all.conf import app_settings


class ConfSettingsTests(SimpleTestCase):
    def test_defaults(self):
        assert app_settings.FETCH_UPDATED_IDS is True
        assert app_settings.MAX_FETCH_IDS_LIMIT == 10_000
        assert app_settings.ENABLE_RAW_SQL_INTERCEPTOR is True
        assert app_settings.MONITORED_TABLES is None
        assert app_settings.EXCLUDED_TABLES == ["django_session", "django_migrations"]
        assert app_settings.SQL_PARSER_ENGINE == "sqlglot"

    def test_override_settings_updates_value(self):
        with override_settings(DJANGO_SIGNALS_ALL={"FETCH_UPDATED_IDS": False}):
            assert app_settings.FETCH_UPDATED_IDS is False

        assert app_settings.FETCH_UPDATED_IDS is True

    def test_partial_override_keeps_other_defaults(self):
        with override_settings(DJANGO_SIGNALS_ALL={"MAX_FETCH_IDS_LIMIT": 5}):
            assert app_settings.MAX_FETCH_IDS_LIMIT == 5
            assert app_settings.FETCH_UPDATED_IDS is True

    def test_invalid_setting_name_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            _ = app_settings.NOT_A_REAL_SETTING

    def test_unrelated_setting_change_does_not_reload(self):
        # Accède à FETCH_UPDATED_IDS pour le mettre en cache, puis change un
        # réglage Django sans rapport (DEBUG) : le cache ne doit pas être
        # invalidé, seul DJANGO_SIGNALS_ALL doit déclencher un reload().
        assert app_settings.FETCH_UPDATED_IDS is True
        with override_settings(DEBUG=True):
            assert app_settings.FETCH_UPDATED_IDS is True
