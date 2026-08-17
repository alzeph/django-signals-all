# Changelog

[English](CHANGELOG.md) | **Français**

Toutes les modifications notables de ce projet sont documentées ici.

Le format suit [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [Unreleased]

## [1.0.0rc2] - 2026-08-13

Durcissement uniquement (aucun changement d'API publique), conformément à
la politique release candidate.

### Added

- Tests couvrant les variantes async de Django (`aupdate`, `abulk_create`,
  `abulk_update`) : elles délèguent à nos méthodes surchargées via
  `sync_to_async`, ce qui fonctionnait déjà mais n'était pas vérifié.
- CI : matrice de compatibilité contre Django 4.2, 5.0, 5.1 et 5.2 (en plus
  de la version verrouillée dans `uv.lock`), et matrice Python 3.12/3.13.
- Couverture de tests mesurée et verrouillée à 100 % (`pytest-cov`,
  `--cov-fail-under=100`).
- Classifiers PyPI `Framework :: Django :: 6.0` et `6.1`, versions
  effectivement testées mais absentes des classifiers jusqu'ici.

### Fixed

- Les tests des méthodes async fermaient explicitement la connexion DB
  ouverte par `sync_to_async` sur son thread dédié, qui bloquait sinon le
  `DROP DATABASE` de fin de suite sous PostgreSQL.
- Espace superflu dans `__version__` (`" 1.0.0rc1"`), silencieusement
  toléré par le parsing de version mais incorrect dans la source.

## [1.0.0rc1] - 2026-08-13

Première version publique (release candidate). Aucune version antérieure
n'a été publiée sur PyPI — le développement `0.x` est resté interne à ce
dépôt.

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

[Unreleased]: https://github.com/alzeph/django-signals-all/compare/v1.0.0rc2...HEAD
[1.0.0rc2]: https://github.com/alzeph/django-signals-all/compare/v1.0.0rc1...v1.0.0rc2
[1.0.0rc1]: https://github.com/alzeph/django-signals-all/releases/tag/v1.0.0rc1
