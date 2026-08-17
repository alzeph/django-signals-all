# Contributing to django-signals-all

**English** | [Français](CONTRIBUTING.fr.md)

Thanks for wanting to contribute! This guide describes how to set up the
development environment and what is expected of a pull request.

## Setup

The project uses [uv](https://docs.astral.sh/uv/) for dependency and virtual
environment management.

```bash
uv sync
```

## Checks before proposing a PR

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy
uv run pytest --cov=django_signals_all --cov-report=term-missing
```

The `pytest` suite runs against SQLite by default. To also run it against
PostgreSQL and MySQL (required for any change to the `django_signals_all.sql`
module, whose behavior depends on the SQL dialect):

```bash
docker compose up -d
DSA_TEST_DB=postgres uv run pytest
DSA_TEST_DB=mysql uv run pytest
```

These same checks run in CI (`.github/workflows/ci.yml`) and must all pass
before a PR is mergeable:

- **ruff**: lint and formatting
- **mypy** (`strict = true`, with `django-stubs`): typing must stay precise,
  including in code that touches the ORM and Django signals
- **pytest**: against the three supported databases (SQLite, PostgreSQL,
  MySQL) and against Django 4.2/5.0/5.1/5.2; test coverage is locked at 100%
  (`--cov-fail-under=100`) — every new code branch must be tested

If `pre-commit` is installed (`uv run pre-commit install`), ruff and mypy run
automatically before each commit.

## Compatibility

`django_signals_all` targets **Python 3.12+** and **Django 4.2+** (current LTS
and later versions). Any PR must remain compatible with these minimum
versions; do not introduce an implicit dependency on a newer version without
discussing it in an issue first.

## Code style

- No comment that explains the *what* (the code should be self-explanatory)
  — only the *why* when it is non-obvious (hidden constraints, undocumented
  Django behavior, workaround for a known bug).
- No abstraction or feature added beyond what the change requires.
- Any change to the raw SQL module (`django_signals_all.sql`) must be tested
  against all three databases: the behavior of `sqlglot` and the DB-API
  drivers genuinely diverges from one dialect to another (see the notes in
  `sql/engines/sqlglot_engine.py`).

## Commits and PRs

- A clear commit message that explains the *why* of the change.
- One PR = one subject. Prefer several small PRs over a single catch-all PR.
- Describe in the PR description what changes and how it is tested.

## Compatibility and deprecation policy

`django_signals_all` follows [Semantic Versioning](https://semver.org/).
Starting with version `1.0.0`:

- a **major** (`X.0.0`) may break compatibility;
- a **minor** (`1.X.0`) adds features without breaking anything;
- a **patch** (`1.0.X`) contains only bug fixes.

Before `1.0.0` (versions `0.x.y`), no API stability guarantee is given.

After `1.0.0`, any deprecated public API:

1. keeps working and raises an explicit `DeprecationWarning` for at least one
   full minor version;
2. is documented in `CHANGELOG.md` under a `### Deprecated` section;
3. is only removed in a subsequent major version, never in a minor or patch.

## Reporting a bug or proposing a feature

Open an [issue](https://github.com/alzeph/django-signals-all/issues) using the
appropriate template. For a security vulnerability, see
[SECURITY.md](SECURITY.md) instead of a public issue.
