from django.db import models

from django_signals_all.orm.manager import BulkSignalManager


class Article(models.Model):
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, default="draft")
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    objects = BulkSignalManager()


class Product(models.Model):
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    objects = BulkSignalManager()


class Order(models.Model):
    reference = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default="pending")
    discount = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    objects = BulkSignalManager()


class Client(models.Model):
    name = models.CharField(max_length=100)

    objects = BulkSignalManager()

    class Meta:
        db_table = "crm_client"
