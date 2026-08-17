## Summary

<!-- What does this PR change, and why? -->

## Testing

<!-- How was this change tested? On which databases? -->

## Checklist

- [ ] `uv run ruff check src tests` passes
- [ ] `uv run ruff format --check src tests` passes
- [ ] `uv run mypy` passes
- [ ] `uv run pytest --cov=django_signals_all --cov-fail-under=100` passes (SQLite)
- [ ] If the change touches `django_signals_all.sql`: also tested with
      `DSA_TEST_DB=postgres` and `DSA_TEST_DB=mysql` (`docker compose up -d`)
- [ ] `CHANGELOG.md` updated if the change is user-visible
