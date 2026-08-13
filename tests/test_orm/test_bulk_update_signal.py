from django.test import TestCase

from django_signals_all.signals import post_bulk_model_update, post_bulk_update
from tests.testapp.models import Order


class BulkUpdateSignalTests(TestCase):
    def setUp(self):
        self.model_update_events = []
        self.plain_update_events = []
        post_bulk_model_update.connect(
            self._model_update_receiver, sender=Order, dispatch_uid="test-bmu"
        )
        post_bulk_update.connect(
            self._plain_update_receiver, sender=Order, dispatch_uid="test-bu"
        )
        self.addCleanup(
            post_bulk_model_update.disconnect, sender=Order, dispatch_uid="test-bmu"
        )
        self.addCleanup(
            post_bulk_update.disconnect, sender=Order, dispatch_uid="test-bu"
        )

    def _model_update_receiver(
        self, sender, updated_instances, fields_updated, using, **kwargs
    ):
        self.model_update_events.append(
            {"updated_instances": updated_instances, "fields_updated": fields_updated}
        )

    def _plain_update_receiver(self, sender, **kwargs):
        self.plain_update_events.append(kwargs)

    def test_bulk_update_emits_single_aggregated_signal(self):
        # bulk_create() ne renseigne pas toujours le pk des objets retournés
        # (ex. MySQL, sans support de RETURNING) : bulk_update() exige des
        # objets avec pk, donc on relit les instances depuis la base.
        Order.objects.bulk_create(
            [Order(reference=f"o{i}", status="pending") for i in range(5)]
        )
        orders = list(Order.objects.filter(status="pending"))
        for order in orders:
            order.status = "shipped"

        with self.captureOnCommitCallbacks(execute=True):
            Order.objects.bulk_update(orders, ["status"], batch_size=2)

        assert len(self.model_update_events) == 1
        event = self.model_update_events[0]
        assert len(event["updated_instances"]) == 5
        assert event["fields_updated"] == ["status"]

        # bulk_update() découpe en plusieurs UPDATE internes (batch_size=2) : ils ne
        # doivent pas déclencher de post_bulk_update parasite.
        assert self.plain_update_events == []

    def test_bulk_update_no_listener_no_signal(self):
        post_bulk_model_update.disconnect(sender=Order, dispatch_uid="test-bmu")
        Order.objects.bulk_create([Order(reference="o1", status="pending")])
        orders = list(Order.objects.filter(reference="o1"))
        orders[0].status = "shipped"

        with self.captureOnCommitCallbacks(execute=True):
            Order.objects.bulk_update(orders, ["status"])

        assert self.model_update_events == []

    def test_plain_update_still_works_outside_bulk_update(self):
        Order.objects.bulk_create([Order(reference="o1", status="pending")])

        with self.captureOnCommitCallbacks(execute=True):
            Order.objects.filter(status="pending").update(status="shipped")

        assert len(self.plain_update_events) == 1
        assert self.model_update_events == []
