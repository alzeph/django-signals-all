from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from django_signals_all.signals import post_bulk_update
from tests.testapp.models import Article


class UpdateSignalTests(TestCase):
    def setUp(self):
        self.received = []
        post_bulk_update.connect(
            self._receiver, sender=Article, dispatch_uid="test-update"
        )
        self.addCleanup(
            post_bulk_update.disconnect, sender=Article, dispatch_uid="test-update"
        )

    def _receiver(self, sender, updated_ids, update_kwargs, using, **kwargs):
        self.received.append(
            {
                "updated_ids": updated_ids,
                "update_kwargs": update_kwargs,
                "using": using,
            }
        )

    def test_update_emits_signal_with_ids_and_kwargs(self):
        # bulk_create() ne renseigne pas toujours le pk des objets retournés
        # (ex. MySQL, qui ne supporte pas RETURNING) : on relit depuis la base
        # pour connaître les IDs réellement attendus, plutôt que de se fier
        # aux instances retournées par bulk_create().
        Article.objects.bulk_create(
            [Article(title=f"a{i}", status="draft") for i in range(3)]
        )
        expected_ids = set(
            Article.objects.filter(status="draft").values_list("pk", flat=True)
        )

        with self.captureOnCommitCallbacks(execute=True):
            Article.objects.filter(status="draft").update(status="archived")

        assert len(self.received) == 1
        event = self.received[0]
        assert set(event["updated_ids"]) == expected_ids
        assert event["update_kwargs"] == {"status": "archived"}
        assert event["using"] == "default"

    def test_update_zero_rows_still_emits_with_empty_ids(self):
        with self.captureOnCommitCallbacks(execute=True):
            Article.objects.filter(status="nonexistent").update(status="archived")

        assert len(self.received) == 1
        assert self.received[0]["updated_ids"] == []

    def test_no_listener_skips_extra_query(self):
        post_bulk_update.disconnect(sender=Article, dispatch_uid="test-update")
        Article.objects.bulk_create([Article(title="a", status="draft")])

        with CaptureQueriesContext(connection) as ctx:
            with self.captureOnCommitCallbacks(execute=True):
                Article.objects.filter(status="draft").update(status="archived")

        assert len(ctx.captured_queries) == 1
        assert ctx.captured_queries[0]["sql"].upper().startswith("UPDATE")

    def test_fetch_updated_ids_false_skips_extra_query(self):
        Article.objects.bulk_create([Article(title="a", status="draft")])

        with self.settings(DJANGO_SIGNALS_ALL={"FETCH_UPDATED_IDS": False}):
            with CaptureQueriesContext(connection) as ctx:
                with self.captureOnCommitCallbacks(execute=True):
                    Article.objects.filter(status="draft").update(status="archived")

        assert len(ctx.captured_queries) == 1
        assert self.received[0]["updated_ids"] == []

    def test_max_fetch_ids_limit_truncates(self):
        Article.objects.bulk_create(
            [Article(title=f"a{i}", status="draft") for i in range(5)]
        )

        with self.settings(DJANGO_SIGNALS_ALL={"MAX_FETCH_IDS_LIMIT": 2}):
            with self.captureOnCommitCallbacks(execute=True):
                Article.objects.filter(status="draft").update(status="archived")

        assert len(self.received[0]["updated_ids"]) == 2

    def test_chained_filter_exclude_update_still_emits(self):
        Article.objects.bulk_create(
            [
                Article(title="keep", status="draft"),
                Article(title="skip", status="draft"),
            ]
        )

        with self.captureOnCommitCallbacks(execute=True):
            (
                Article.objects.filter(status="draft")
                .exclude(title="skip")
                .update(status="archived")
            )

        assert len(self.received) == 1
        assert len(self.received[0]["updated_ids"]) == 1
