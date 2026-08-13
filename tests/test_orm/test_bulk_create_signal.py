from django.test import TestCase

from django_signals_all.signals import post_bulk_create
from tests.testapp.models import Product


class BulkCreateSignalTests(TestCase):
    def setUp(self):
        self.received = []
        post_bulk_create.connect(
            self._receiver, sender=Product, dispatch_uid="test-bulk-create"
        )
        self.addCleanup(
            post_bulk_create.disconnect,
            sender=Product,
            dispatch_uid="test-bulk-create",
        )

    def _receiver(self, sender, objects, using, **kwargs):
        self.received.append({"objects": objects, "using": using})

    def test_bulk_create_emits_signal_with_created_objects(self):
        with self.captureOnCommitCallbacks(execute=True):
            Product.objects.bulk_create(
                [
                    Product(title="p1", price="9.99"),
                    Product(title="p2", price="19.99"),
                ]
            )

        assert len(self.received) == 1
        titles = sorted(p.title for p in self.received[0]["objects"])
        assert titles == ["p1", "p2"]

    def test_bulk_create_ignore_conflicts_still_emits(self):
        with self.captureOnCommitCallbacks(execute=True):
            Product.objects.bulk_create(
                [Product(title="p1", price="9.99")], ignore_conflicts=True
            )

        assert len(self.received) == 1

    def test_no_listener_no_extra_query_and_no_signal(self):
        post_bulk_create.disconnect(sender=Product, dispatch_uid="test-bulk-create")

        with self.captureOnCommitCallbacks(execute=True):
            Product.objects.bulk_create([Product(title="p1", price="9.99")])

        assert self.received == []

    def test_empty_list_still_emits_empty_signal(self):
        with self.captureOnCommitCallbacks(execute=True):
            Product.objects.bulk_create([])

        assert len(self.received) == 1
        assert self.received[0]["objects"] == []
