from django.dispatch import Signal

post_bulk_update = Signal()
post_bulk_create = Signal()
post_bulk_model_update = Signal()
raw_sql_executed = Signal()
