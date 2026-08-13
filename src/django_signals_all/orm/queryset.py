from django.db import models, transaction

from django_signals_all.conf import app_settings
from django_signals_all.signals import (
    post_bulk_create,
    post_bulk_model_update,
    post_bulk_update,
)


class BulkSignalQuerySet(models.QuerySet):
    """QuerySet émettant post_bulk_update/post_bulk_create/post_bulk_model_update.

    Les signaux sont envoyés via transaction.on_commit pour ne jamais être émis
    au titre d'une mutation finalement annulée par un rollback.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._signals_all_in_bulk_update = False

    def _clone(self):
        clone = super()._clone()
        clone._signals_all_in_bulk_update = self._signals_all_in_bulk_update
        return clone

    def update(self, **kwargs):
        # bulk_update() ré-entre ici via self.using(self.db).filter(...).update(...) ;
        # dans ce cas le signal agrégé post_bulk_model_update suffit, on ne veut pas
        # émettre en plus un post_bulk_update par batch interne.
        if self._signals_all_in_bulk_update:
            return super().update(**kwargs)

        if not post_bulk_update.has_listeners(sender=self.model):
            return super().update(**kwargs)

        updated_ids = []
        if app_settings.FETCH_UPDATED_IDS:
            limit = app_settings.MAX_FETCH_IDS_LIMIT
            updated_ids = list(self.values_list("pk", flat=True)[:limit])

        rows_updated = super().update(**kwargs)

        db = self.db
        transaction.on_commit(
            lambda: post_bulk_update.send(
                sender=self.model,
                updated_ids=updated_ids,
                update_kwargs=kwargs,
                using=db,
            ),
            using=db,
        )
        return rows_updated

    def bulk_create(self, objs, **kwargs):
        created = super().bulk_create(objs, **kwargs)

        if post_bulk_create.has_listeners(sender=self.model):
            db = self.db
            created_objects = list(created)
            transaction.on_commit(
                lambda: post_bulk_create.send(
                    sender=self.model, objects=created_objects, using=db
                ),
                using=db,
            )
        return created

    def bulk_update(self, objs, fields, **kwargs):
        self._signals_all_in_bulk_update = True
        try:
            rows_updated = super().bulk_update(objs, fields, **kwargs)
        finally:
            self._signals_all_in_bulk_update = False

        if post_bulk_model_update.has_listeners(sender=self.model):
            db = self.db
            updated_instances = list(objs)
            fields_updated = list(fields)
            transaction.on_commit(
                lambda: post_bulk_model_update.send(
                    sender=self.model,
                    updated_instances=updated_instances,
                    fields_updated=fields_updated,
                    using=db,
                ),
                using=db,
            )
        return rows_updated
