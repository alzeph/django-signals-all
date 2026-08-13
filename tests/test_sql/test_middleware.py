from unittest.mock import patch

from django.test import TestCase, override_settings

from django_signals_all.signals import raw_sql_executed
from tests.test_sql._helpers import post_sql
from tests.testapp.models import Client as ClientModel


class _AlwaysNoneEngine:
    """Simule un moteur de parsing qui ne reconnaît jamais le SQL fourni."""

    def parse(self, sql, vendor):
        return None


class RawSQLMiddlewareTests(TestCase):
    def setUp(self):
        self.received = []
        raw_sql_executed.connect(self._receiver, dispatch_uid="test-raw-sql")
        self.addCleanup(raw_sql_executed.disconnect, dispatch_uid="test-raw-sql")

    def _receiver(self, sender, operation, sql, params, using, **kwargs):
        self.received.append(
            {"table": sender, "operation": operation, "sql": sql, "using": using}
        )

    def test_insert_via_raw_cursor_emits_signal(self):
        response = post_sql("INSERT INTO crm_client (name) VALUES (?)", params=["Ada"])

        assert response.status_code == 200
        assert len(self.received) == 1
        assert self.received[0]["table"] == "crm_client"
        assert self.received[0]["operation"] == "INSERT"
        assert self.received[0]["using"] == "default"

    def test_update_via_raw_cursor_emits_signal(self):
        ClientModel.objects.create(name="Ada")

        response = post_sql(
            "UPDATE crm_client SET name = ? WHERE name = ?", params=["Grace", "Ada"]
        )

        assert response.status_code == 200
        assert len(self.received) == 1
        assert self.received[0]["operation"] == "UPDATE"

    def test_delete_via_raw_cursor_emits_signal(self):
        ClientModel.objects.create(name="Ada")

        response = post_sql("DELETE FROM crm_client WHERE name = ?", params=["Ada"])

        assert response.status_code == 200
        assert len(self.received) == 1
        assert self.received[0]["operation"] == "DELETE"

    def test_select_does_not_emit_signal(self):
        response = post_sql("SELECT * FROM crm_client")

        assert response.status_code == 200
        assert self.received == []

    def test_no_listener_no_signal(self):
        raw_sql_executed.disconnect(dispatch_uid="test-raw-sql")

        response = post_sql("INSERT INTO crm_client (name) VALUES (?)", params=["Ada"])

        assert response.status_code == 200
        assert self.received == []

    def test_executemany_emits_signal(self):
        response = post_sql(
            "INSERT INTO crm_client (name) VALUES (?)",
            params=[["Ada"], ["Grace"]],
            many=True,
        )

        assert response.status_code == 200
        assert len(self.received) == 1
        assert self.received[0]["operation"] == "INSERT"

    def test_interceptor_disabled_via_settings(self):
        with override_settings(
            DJANGO_SIGNALS_ALL={"ENABLE_RAW_SQL_INTERCEPTOR": False}
        ):
            response = post_sql(
                "INSERT INTO crm_client (name) VALUES (?)", params=["Ada"]
            )

        assert response.status_code == 200
        assert self.received == []

    def test_unrecognized_sql_by_parser_does_not_crash_or_emit(self):
        # Simule un SQL que le moteur configuré ne sait pas analyser (parse()
        # retourne None) : la requête HTTP doit aboutir normalement et aucun
        # signal ne doit être émis.
        with patch.dict(
            "django_signals_all.sql.middleware._ENGINES",
            {"sqlglot": _AlwaysNoneEngine()},
        ):
            response = post_sql(
                "INSERT INTO crm_client (name) VALUES (?)", params=["Ada"]
            )

        assert response.status_code == 200
        assert self.received == []

    def test_receiver_running_sql_does_not_recurse_infinitely(self):
        def side_effect_receiver(sender, **kwargs):
            # Un receiver qui exécute lui-même du SQL ne doit pas redéclencher
            # raw_sql_executed pour cette requête interne.
            ClientModel.objects.create(name="from-receiver")

        raw_sql_executed.connect(
            side_effect_receiver, dispatch_uid="test-raw-sql-side-effect"
        )
        self.addCleanup(
            raw_sql_executed.disconnect, dispatch_uid="test-raw-sql-side-effect"
        )

        response = post_sql("INSERT INTO crm_client (name) VALUES (?)", params=["Ada"])

        assert response.status_code == 200
        assert len(self.received) == 1
