# django-signals-all

[![CI](https://github.com/alzeph/django-signals-all/actions/workflows/ci.yml/badge.svg)](https://github.com/alzeph/django-signals-all/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/django-signals-all.svg)](https://pypi.org/project/django-signals-all/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](pyproject.toml)

**English** | [Français](README.fr.md)

> **Release candidate.** `django-signals-all` is at `1.0.0rc1`: the API is
> considered frozen but has not yet been battle-tested by real-world usage
> outside of this repository. Feedback (issues, use cases, bugs) is welcome
> before tagging the final `1.0.0` release — see [RELEASING.md](RELEASING.md).

Guaranteed Django signals, no matter how you mutate your data.

## The problem

Bulk operations (`bulk_create`, `bulk_update`, `QuerySet.update()`) and raw SQL
(`cursor.execute()`) run SQL directly. They bypass `Model.save()` and never fire
any Django signal, which breaks cache invalidation, search reindexing, and audit
log traceability.

`django_signals_all` provides two levels of capture:

1. **ORM (`django_signals_all.orm`)** — a custom `QuerySet`/`Manager` that emits
   application signals for `update()`, `bulk_create()`, and `bulk_update()`.
2. **Raw SQL (`django_signals_all.sql`)** — a middleware based on
   `connection.execute_wrapper` that parses SQL executed through a cursor and
   emits a signal on `INSERT`/`UPDATE`/`DELETE`.

A third module, `pg_notify` (PostgreSQL `LISTEN`/`NOTIFY` triggers to capture
mutations made outside the Django application), is on the roadmap and not yet
implemented.

## Installation

```bash
uv add django-signals-all
```

```python
# settings.py
INSTALLED_APPS = [
    ...,
    "django_signals_all",
]

MIDDLEWARE = [
    ...,
    "django_signals_all.sql.middleware.RawSQLSignalMiddleware",
]
```

## ORM module

The model must use `BulkSignalManager` as its manager:

```python
# models.py
from django.db import models
from django_signals_all.orm.manager import BulkSignalManager


class Article(models.Model):
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, default="draft")

    objects = BulkSignalManager()
```

```python
# receivers.py
from django.dispatch import receiver
from django.core.cache import cache
from django_signals_all.signals import post_bulk_update, post_bulk_create
from .models import Article


@receiver(post_bulk_update, sender=Article)
def invalidate_cache_on_bulk_update(sender, updated_ids, update_kwargs, using, **kwargs):
    """Fired even by Article.objects.filter(...).update(...)."""
    cache.delete_many([f"article:{pk}" for pk in updated_ids])


@receiver(post_bulk_create, sender=Article)
def index_on_bulk_create(sender, objects, using, **kwargs):
    """Fired after Article.objects.bulk_create([...])."""
    search_engine.index_many(objects)
```

`Manager.bulk_update()` splits its updates into several internal SQL queries
(`batch_size`); these internal queries do not emit `post_bulk_update` —
instead, a single aggregated `post_bulk_model_update` is sent, with the full
set of updated instances and fields:

```python
from django_signals_all.signals import post_bulk_model_update


@receiver(post_bulk_model_update, sender=Order)
def track_bulk_status_change(sender, updated_instances, fields_updated, using, **kwargs):
    if "status" in fields_updated:
        for order in updated_instances:
            audit_log.record(order)
```

All ORM signals are sent via `transaction.on_commit()`: they are never emitted
for a mutation that ends up rolled back.

## Raw SQL module

The `raw_sql_executed` signal uses the **table name** as its `sender`, not as
an arbitrary filtering kwarg (`@receiver(signal, table_name=...)` is not a
valid Django API — `receiver()`/`Signal.connect()` only filter on `sender`):

```python
import logging
from django.dispatch import receiver
from django_signals_all.signals import raw_sql_executed

logger = logging.getLogger("security")


@receiver(raw_sql_executed, sender="crm_client")
def audit_raw_sql_on_crm_client(sender, operation, sql, params, using, **kwargs):
    if operation in ("UPDATE", "DELETE"):
        logger.warning("Raw SQL mutation (%s) on %s: %s", operation, sender, sql)
```

## Configuration

```python
# settings.py
DJANGO_SIGNALS_ALL = {
    # ORM module: fetch impacted PKs before a bulk update().
    "FETCH_UPDATED_IDS": True,
    "MAX_FETCH_IDS_LIMIT": 10_000,

    # Raw SQL module.
    "ENABLE_RAW_SQL_INTERCEPTOR": True,
    "MONITORED_TABLES": None,  # or an allowlist, e.g. ["users_user", "crm_client"]
    "EXCLUDED_TABLES": ["django_session", "django_migrations"],
    "SQL_PARSER_ENGINE": "sqlglot",  # or "regex"
}
```

If no receiver is connected to a signal, the library skips the corresponding
extra work (no query to fetch IDs, no SQL parsing).

## Known limitations

- The `regex` engine does not understand CTEs (`WITH ... UPDATE ...`): it does
  not detect the target table in that case. Use the `sqlglot` engine (default)
  if your application relies on this.
- SQL parsing is best-effort: a query that the configured engine cannot parse
  is silently skipped (with a `warning`-level log for `sqlglot`), never an
  exception propagated to the application.
- The `pg_notify` module does not exist yet in this version.

## Development

```bash
uv sync --group dev

uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy

# SQLite (default, no external dependency)
uv run pytest --cov=django_signals_all --cov-report=term-missing

# PostgreSQL and MySQL (requires Docker)
docker compose up -d
DSA_TEST_DB=postgres uv run pytest
DSA_TEST_DB=mysql uv run pytest
```

CI (`.github/workflows/ci.yml`) runs lint, type checking (mypy `strict`), and
the full test suite against all three databases on every push.

See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute,
[CHANGELOG.md](CHANGELOG.md) for the version history, and
[RELEASING.md](RELEASING.md) for the release process.

## License

[MIT](LICENSE)
