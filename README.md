# django-signals-all

[![CI](https://github.com/alzeph/django-signals-all/actions/workflows/ci.yml/badge.svg)](https://github.com/alzeph/django-signals-all/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/django-signals-all.svg)](https://pypi.org/project/django-signals-all/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](pyproject.toml)

Des signaux Django garantis, peu importe comment vous modifiez vos données.

## Le problème

Les opérations en masse (`bulk_create`, `bulk_update`, `QuerySet.update()`) et le SQL
brut (`cursor.execute()`) exécutent du SQL direct. Elles contournent `Model.save()` et
ne déclenchent aucun signal Django, ce qui casse l'invalidation de cache, la
réindexation de recherche et la traçabilité des audit logs.

`django_signals_all` fournit deux niveaux de capture :

1. **ORM (`django_signals_all.orm`)** — un `QuerySet`/`Manager` personnalisé qui émet
   des signaux applicatifs pour `update()`, `bulk_create()` et `bulk_update()`.
2. **SQL brut (`django_signals_all.sql`)** — un middleware basé sur
   `connection.execute_wrapper` qui analyse le SQL exécuté via un curseur et émet un
   signal sur les `INSERT`/`UPDATE`/`DELETE`.

Un troisième module, `pg_notify` (triggers PostgreSQL `LISTEN`/`NOTIFY` pour capturer
les mutations effectuées hors de l'application Django), est prévu en roadmap et n'est
pas encore implémenté.

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

## Module ORM

Le modèle doit utiliser `BulkSignalManager` comme manager :

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
    """Déclenché même par Article.objects.filter(...).update(...)."""
    cache.delete_many([f"article:{pk}" for pk in updated_ids])


@receiver(post_bulk_create, sender=Article)
def index_on_bulk_create(sender, objects, using, **kwargs):
    """Déclenché après Article.objects.bulk_create([...])."""
    search_engine.index_many(objects)
```

`Manager.bulk_update()` découpe ses mises à jour en plusieurs requêtes SQL internes
(`batch_size`) ; ces requêtes internes n'émettent pas `post_bulk_update` — seul un
`post_bulk_model_update` unique et agrégé est envoyé, avec l'ensemble des instances et
des champs modifiés :

```python
from django_signals_all.signals import post_bulk_model_update


@receiver(post_bulk_model_update, sender=Order)
def track_bulk_status_change(sender, updated_instances, fields_updated, using, **kwargs):
    if "status" in fields_updated:
        for order in updated_instances:
            audit_log.record(order)
```

Tous les signaux ORM sont envoyés via `transaction.on_commit()` : ils ne sont jamais
émis pour une mutation finalement annulée par un rollback.

## Module SQL brut

Le signal `raw_sql_executed` utilise le **nom de la table** comme `sender`, pas comme
un kwarg de filtrage arbitraire (`@receiver(signal, table_name=...)` n'est pas une API
Django valide — `receiver()`/`Signal.connect()` ne filtrent que sur `sender`) :

```python
import logging
from django.dispatch import receiver
from django_signals_all.signals import raw_sql_executed

logger = logging.getLogger("security")


@receiver(raw_sql_executed, sender="crm_client")
def audit_raw_sql_on_crm_client(sender, operation, sql, params, using, **kwargs):
    if operation in ("UPDATE", "DELETE"):
        logger.warning("Mutation SQL brute (%s) sur %s : %s", operation, sender, sql)
```

## Configuration

```python
# settings.py
DJANGO_SIGNALS_ALL = {
    # Module ORM : récupérer les PK impactées avant un update() en masse.
    "FETCH_UPDATED_IDS": True,
    "MAX_FETCH_IDS_LIMIT": 10_000,

    # Module SQL brut.
    "ENABLE_RAW_SQL_INTERCEPTOR": True,
    "MONITORED_TABLES": None,  # ou une liste blanche, ex. ["users_user", "crm_client"]
    "EXCLUDED_TABLES": ["django_session", "django_migrations"],
    "SQL_PARSER_ENGINE": "sqlglot",  # ou "regex"
}
```

Si aucun receiver n'est connecté à un signal, la bibliothèque évite le travail
supplémentaire correspondant (pas de requête pour récupérer les IDs, pas de parsing
SQL).

## Limitations connues

- Le moteur `regex` ne comprend pas les CTE (`WITH ... UPDATE ...`) : il ne détecte pas
  la table cible dans ce cas. Utilisez le moteur `sqlglot` (par défaut) si votre
  application en dépend.
- Le parsing SQL est du best-effort : une requête que le moteur configuré ne sait pas
  analyser est ignorée silencieusement (avec un log de niveau `warning` pour
  `sqlglot`), jamais une exception propagée à l'application.
- Le module `pg_notify` n'existe pas encore dans cette version.

## Développement

```bash
uv sync --group dev

uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy

# SQLite (par défaut, pas de dépendance externe)
uv run pytest

# PostgreSQL et MySQL (nécessite Docker)
docker compose up -d
DSA_TEST_DB=postgres uv run pytest
DSA_TEST_DB=mysql uv run pytest
```

La CI (`.github/workflows/ci.yml`) exécute lint, typecheck (mypy `strict`) et la suite
complète sur les trois SGBD à chaque push.

Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour contribuer,
[CHANGELOG.md](CHANGELOG.md) pour l'historique des versions, et
[RELEASING.md](RELEASING.md) pour le process de publication.

## Licence

[MIT](LICENSE)
