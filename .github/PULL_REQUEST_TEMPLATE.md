## Résumé

<!-- Que change cette PR, et pourquoi ? -->

## Test

<!-- Comment ce changement est-il testé ? Sur quels SGBD ? -->

## Checklist

- [ ] `uv run ruff check src tests` passe
- [ ] `uv run ruff format --check src tests` passe
- [ ] `uv run mypy` passe
- [ ] `uv run pytest --cov=django_signals_all --cov-fail-under=100` passe (SQLite)
- [ ] Si le changement touche `django_signals_all.sql` : testé aussi avec
      `DSA_TEST_DB=postgres` et `DSA_TEST_DB=mysql` (`docker compose up -d`)
- [ ] `CHANGELOG.md` mis à jour si le changement est visible pour les utilisateurs
