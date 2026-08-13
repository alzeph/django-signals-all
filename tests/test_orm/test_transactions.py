from django.db import transaction
from django.test import TestCase

from django_signals_all.signals import post_bulk_update
from tests.testapp.models import Article


class Boom(Exception):
    pass


class TransactionBehaviorTests(TestCase):
    def setUp(self):
        self.received = []
        post_bulk_update.connect(self._receiver, sender=Article, dispatch_uid="test-tx")
        self.addCleanup(
            post_bulk_update.disconnect, sender=Article, dispatch_uid="test-tx"
        )

    def _receiver(self, sender, **kwargs):
        self.received.append(kwargs)

    def test_signal_not_emitted_on_rollback(self):
        Article.objects.bulk_create([Article(title="a", status="draft")])

        with self.captureOnCommitCallbacks(execute=True) as callbacks:
            try:
                with transaction.atomic():
                    Article.objects.filter(status="draft").update(status="archived")
                    raise Boom
            except Boom:
                pass

        assert callbacks == []
        assert self.received == []
        assert Article.objects.get().status == "draft"

    def test_signal_emitted_after_successful_atomic_commit(self):
        Article.objects.bulk_create([Article(title="a", status="draft")])

        with self.captureOnCommitCallbacks(execute=True):
            with transaction.atomic():
                Article.objects.filter(status="draft").update(status="archived")

        assert len(self.received) == 1
