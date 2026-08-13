from django.db import models

from django_signals_all.orm.queryset import BulkSignalQuerySet

BulkSignalManager = models.Manager.from_queryset(BulkSignalQuerySet)
