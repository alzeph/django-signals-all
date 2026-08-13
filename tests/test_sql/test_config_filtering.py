from django.test import TestCase, override_settings

from django_signals_all.signals import raw_sql_executed
from tests.test_sql._helpers import post_sql


class ConfigFilteringTests(TestCase):
    def setUp(self):
        self.received = []
        raw_sql_executed.connect(self._receiver, dispatch_uid="test-filtering")
        self.addCleanup(raw_sql_executed.disconnect, dispatch_uid="test-filtering")

    def _receiver(self, sender, **kwargs):
        self.received.append(sender)

    def test_excluded_table_is_skipped(self):
        with override_settings(DJANGO_SIGNALS_ALL={"EXCLUDED_TABLES": ["crm_client"]}):
            post_sql("INSERT INTO crm_client (name) VALUES (?)", params=["Ada"])

        assert self.received == []

    def test_monitored_tables_blocks_unlisted_table(self):
        with override_settings(
            DJANGO_SIGNALS_ALL={"MONITORED_TABLES": ["testapp_order"]}
        ):
            post_sql("INSERT INTO crm_client (name) VALUES (?)", params=["Ada"])

        assert self.received == []

    def test_monitored_tables_lets_listed_table_through(self):
        with override_settings(DJANGO_SIGNALS_ALL={"MONITORED_TABLES": ["crm_client"]}):
            post_sql("INSERT INTO crm_client (name) VALUES (?)", params=["Ada"])

        assert self.received == ["crm_client"]

    def test_regex_engine_can_be_selected(self):
        with override_settings(DJANGO_SIGNALS_ALL={"SQL_PARSER_ENGINE": "regex"}):
            post_sql("INSERT INTO crm_client (name) VALUES (?)", params=["Ada"])

        assert self.received == ["crm_client"]

    def test_default_excludes_django_migrations_table(self):
        post_sql(
            "INSERT INTO django_migrations (app, name, applied) VALUES (?, ?, ?)",
            params=["testapp", "9999_fake", "2030-01-01 00:00:00"],
        )

        assert self.received == []
