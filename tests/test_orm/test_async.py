import asyncio
from collections.abc import Coroutine
from typing import Any

from asgiref.sync import sync_to_async
from django.db import connections
from django.test import TransactionTestCase

from django_signals_all.signals import (
    post_bulk_create,
    post_bulk_model_update,
    post_bulk_update,
)
from tests.testapp.models import Article, Order, Product


def _run(coro: Coroutine[Any, Any, Any]) -> None:
    async def wrapper() -> None:
        try:
            await coro
        finally:
            # sync_to_async(thread_sensitive=True) (utilisé en interne par
            # aupdate/abulk_*) exécute l'appel sur un thread dédié où Django
            # ouvre sa propre connexion DB. En dehors du cycle
            # requête/réponse, rien ne la referme automatiquement, ce qui
            # bloque le DROP DATABASE de fin de suite sous PostgreSQL
            # ("database is being accessed by other users"). On la ferme
            # explicitement sur ce même thread.
            await sync_to_async(connections.close_all, thread_sensitive=True)()

    asyncio.run(wrapper())


class AsyncOrmSignalTests(TransactionTestCase):
    """Vérifie que les variantes async de Django (aupdate, abulk_create,
    abulk_update) déclenchent bien nos signaux.

    Django implémente ces méthodes comme `await sync_to_async(self.<sync>)`
    (voir django/db/models/query.py), donc elles délèguent à nos méthodes
    surchargées sans code supplémentaire de notre part — ces tests
    garantissent que ça reste vrai.

    TransactionTestCase (pas TestCase) est nécessaire ici : sync_to_async()
    exécute l'appel dans un autre thread, ce qui entre en conflit avec la
    transaction englobante ouverte par TestCase sur SQLite ("database is
    locked"). TransactionTestCase committe réellement, donc les callbacks
    transaction.on_commit() s'exécutent naturellement, sans avoir besoin de
    captureOnCommitCallbacks (qui n'existe d'ailleurs que sur TestCase).
    """

    def setUp(self):
        self.update_events: list[dict] = []
        self.create_events: list[dict] = []
        self.model_update_events: list[dict] = []
        post_bulk_update.connect(
            self._update_receiver, sender=Article, dispatch_uid="test-async-update"
        )
        post_bulk_create.connect(
            self._create_receiver, sender=Product, dispatch_uid="test-async-create"
        )
        post_bulk_model_update.connect(
            self._model_update_receiver, sender=Order, dispatch_uid="test-async-bmu"
        )
        self.addCleanup(
            post_bulk_update.disconnect,
            sender=Article,
            dispatch_uid="test-async-update",
        )
        self.addCleanup(
            post_bulk_create.disconnect,
            sender=Product,
            dispatch_uid="test-async-create",
        )
        self.addCleanup(
            post_bulk_model_update.disconnect,
            sender=Order,
            dispatch_uid="test-async-bmu",
        )

    def _update_receiver(self, sender, **kwargs):
        self.update_events.append(kwargs)

    def _create_receiver(self, sender, **kwargs):
        self.create_events.append(kwargs)

    def _model_update_receiver(self, sender, **kwargs):
        self.model_update_events.append(kwargs)

    def test_aupdate_emits_post_bulk_update(self):
        Article.objects.bulk_create([Article(title="a", status="draft")])

        _run(Article.objects.filter(status="draft").aupdate(status="archived"))

        assert len(self.update_events) == 1
        assert self.update_events[0]["update_kwargs"] == {"status": "archived"}

    def test_abulk_create_emits_post_bulk_create(self):
        _run(Product.objects.abulk_create([Product(title="p1", price="9.99")]))

        assert len(self.create_events) == 1
        assert self.create_events[0]["objects"][0].title == "p1"

    def test_abulk_update_emits_post_bulk_model_update(self):
        Order.objects.bulk_create([Order(reference="o1", status="pending")])
        orders = list(Order.objects.filter(reference="o1"))
        orders[0].status = "shipped"

        _run(Order.objects.abulk_update(orders, ["status"]))

        assert len(self.model_update_events) == 1
        assert self.model_update_events[0]["fields_updated"] == ["status"]
