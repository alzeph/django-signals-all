# Changelog

**English** | [Français](CHANGELOG.fr.md)

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.0.0rc2] - 2026-08-13

Hardening only (no public API change), per the release candidate policy.

### Added

- Tests covering Django's async variants (`aupdate`, `abulk_create`,
  `abulk_update`): they delegate to our overridden methods via
  `sync_to_async`, which already worked but was not verified.
- CI: compatibility matrix against Django 4.2, 5.0, 5.1, and 5.2 (in addition
  to the version pinned in `uv.lock`), and Python 3.12/3.13 matrix.
- Test coverage measured and locked at 100% (`pytest-cov`,
  `--cov-fail-under=100`).
- PyPI classifiers `Framework :: Django :: 6.0` and `6.1`, versions already
  tested but missing from the classifiers until now.

### Fixed

- Async method tests were not explicitly closing the DB connection opened by
  `sync_to_async` on its dedicated thread, which otherwise blocked the
  end-of-suite `DROP DATABASE` under PostgreSQL.
- Stray whitespace in `__version__` (`" 1.0.0rc1"`), silently tolerated by
  version parsing but incorrect in the source.

## [1.0.0rc1] - 2026-08-13

First public release (release candidate). No prior version was published to
PyPI — `0.x` development stayed internal to this repository.

### Added

- ORM module (`django_signals_all.orm`): `BulkSignalQuerySet` and
  `BulkSignalManager` intercept `update()`, `bulk_create()`, and
  `bulk_update()` to emit `post_bulk_update`, `post_bulk_create`, and
  `post_bulk_model_update`, sent via `transaction.on_commit`.
- Raw SQL module (`django_signals_all.sql`): `RawSQLSignalMiddleware` parses
  SQL executed through `cursor.execute()`/`executemany()`
  (`connection.execute_wrapper`) and emits `raw_sql_executed` (`sender` =
  table name) on `INSERT`/`UPDATE`/`DELETE`, with a `sqlglot` parsing engine
  (default, multi-dialect) and a lightweight `regex` engine as a configurable
  alternative.
- Configuration via the `DJANGO_SIGNALS_ALL` dict in `settings.py`:
  `FETCH_UPDATED_IDS`, `MAX_FETCH_IDS_LIMIT`, `ENABLE_RAW_SQL_INTERCEPTOR`,
  `MONITORED_TABLES`, `EXCLUDED_TABLES`, `SQL_PARSER_ENGINE`.
- Test suite validated against SQLite, PostgreSQL, and MySQL
  (`docker-compose.yml` and multi-database CI).
- Fully typed package (`mypy --strict` with `django-stubs`).

[Unreleased]: https://github.com/alzeph/django-signals-all/compare/v1.0.0rc2...HEAD
[1.0.0rc2]: https://github.com/alzeph/django-signals-all/compare/v1.0.0rc1...v1.0.0rc2
[1.0.0rc1]: https://github.com/alzeph/django-signals-all/releases/tag/v1.0.0rc1
