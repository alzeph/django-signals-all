# Changelog

Toutes les modifications notables de ce projet sont documentées ici.

Le format suit [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [Unreleased]

### Added

- Module ORM (`django_signals_all.orm`) : `BulkSignalQuerySet` et
  `BulkSignalManager` interceptent `update()`, `bulk_create()` et
  `bulk_update()` pour émettre `post_bulk_update`, `post_bulk_create` et
  `post_bulk_model_update`, envoyés via `transaction.on_commit`.
- Module SQL brut (`django_signals_all.sql`) : `RawSQLSignalMiddleware`
  analyse le SQL exécuté via `cursor.execute()`/`executemany()`
  (`connection.execute_wrapper`) et émet `raw_sql_executed` (`sender` =
  nom de table) sur les `INSERT`/`UPDATE`/`DELETE`, avec un moteur de
  parsing `sqlglot` (par défaut, multi-dialecte) et un moteur `regex`
  léger en alternative configurable.
- Configuration via le dict `DJANGO_SIGNALS_ALL` dans `settings.py` :
  `FETCH_UPDATED_IDS`, `MAX_FETCH_IDS_LIMIT`, `ENABLE_RAW_SQL_INTERCEPTOR`,
  `MONITORED_TABLES`, `EXCLUDED_TABLES`, `SQL_PARSER_ENGINE`.
- Suite de tests validée sur SQLite, PostgreSQL et MySQL (`docker-compose.yml`
  et CI multi-SGBD).
- Package entièrement typé (`mypy --strict` avec `django-stubs`).

[Unreleased]: https://github.com/alzeph/django-signals-all/compare/main...HEAD
