from django.test import TestCase

from django_signals_all.signals import post_bulk_update
from tests.testapp.models import Article


class MultiDatabaseTests(TestCase):
    databases = {"default", "secondary"}

    def setUp(self):
        self.received = []
        post_bulk_update.connect(
            self._receiver, sender=Article, dispatch_uid="test-multi-db"
        )
        self.addCleanup(
            post_bulk_update.disconnect, sender=Article, dispatch_uid="test-multi-db"
        )

    def _receiver(self, sender, using, **kwargs):
        self.received.append(using)

    def test_signal_scheduled_on_correct_alias(self):
        Article.objects.using("secondary").bulk_create(
            [Article(title="a", status="draft")]
        )

        with self.captureOnCommitCallbacks(using="secondary", execute=True):
            Article.objects.using("secondary").filter(status="draft").update(
                status="archived"
            )

        assert self.received == ["secondary"]

    def test_default_db_untouched(self):
        Article.objects.using("secondary").bulk_create(
            [Article(title="a", status="draft")]
        )

        with self.captureOnCommitCallbacks(using="secondary", execute=True):
            Article.objects.using("secondary").filter(status="draft").update(
                status="archived"
            )

        assert Article.objects.using("default").count() == 0
