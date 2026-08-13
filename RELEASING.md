# Process de release

## Configuration initiale de PyPI (une seule fois)

`django-signals-all` publie via le *trusted publishing* de PyPI (OIDC) :
aucun token long-lived à gérer, l'autorisation est liée à ce dépôt et à ce
workflow GitHub Actions précis.

1. Créer un compte PyPI si besoin.
2. Sur <https://pypi.org/manage/account/publishing/>, ajouter un
   *pending trusted publisher* (le projet n'a pas besoin d'exister sur
   PyPI au préalable) :
   - PyPI project name : `django-signals-all`
   - Owner : `alzeph`
   - Repository name : `django-signals-all`
   - Workflow name : `publish.yml`
   - Environment name : `pypi`
3. Dans les paramètres GitHub du dépôt (`Settings > Environments`), créer
   un environnement `pypi` (protège la publication, permet d'ajouter des
   reviewers si besoin).

## Publier une version

1. Mettre à jour `__version__` dans `src/django_signals_all/__init__.py`
   (la version du package est single-sourcée depuis ce fichier, voir
   `[tool.hatch.version]` dans `pyproject.toml`).
2. Déplacer le contenu de `## [Unreleased]` dans `CHANGELOG.md` sous une
   nouvelle section `## [X.Y.Z] - AAAA-MM-JJ`, et mettre à jour les liens
   de comparaison en bas de fichier.
3. Vérifier localement :
   ```bash
   uv run ruff check src tests
   uv run ruff format --check src tests
   uv run mypy
   uv run pytest
   docker compose up -d
   DSA_TEST_DB=postgres uv run pytest
   DSA_TEST_DB=mysql uv run pytest
   uv build
   ```
4. Commit ("Release X.Y.Z"), merge sur `main`.
5. Tag et push : `git tag vX.Y.Z && git push origin vX.Y.Z`.
6. Créer une [GitHub Release](https://github.com/alzeph/django-signals-all/releases/new)
   à partir de ce tag. La publier déclenche `.github/workflows/publish.yml`,
   qui build et publie automatiquement sur PyPI.
   - Pour une pré-version (`rc`, `b`, `a`), cocher **"Set as a pre-release"**
     sur GitHub — PyPI la traitera comme une pré-version (non installée par
     défaut par `pip install django-signals-all`, il faudra
     `pip install django-signals-all --pre` ou fixer la version exacte).

## Politique release candidate avant le 1.0.0 final

`1.0.0rc1` est une *release candidate* : l'API est considérée figée mais
n'a pas encore été éprouvée par un usage réel en dehors de ce dépôt.
Avant de tagger `1.0.0` (final) :

- laisser la RC disponible au moins quelques semaines pour recueillir des
  retours (issues, cas d'usage réels, éventuels bugs sur le module SQL brut
  ou l'agrégation des signaux `bulk_update`) ;
- ne merger que des corrections de bug sur `main` pendant cette période,
  pas de nouvelle fonctionnalité qui changerait l'API publique ;
- si un changement d'API s'avère nécessaire suite aux retours, publier
  `1.0.0rc2` plutôt que de modifier `1.0.0rc1` a posteriori.

En particulier, le module `pg_notify` (roadmap, voir README) n'existe pas
encore et pourra faire évoluer l'API des signaux existants s'il révèle un
besoin de cohérence transversale — c'est aussi une raison de ne pas
précipiter le passage en `1.0.0` final.

Une fois `1.0.0` taggé, voir la politique de compatibilité dans
[CONTRIBUTING.md](CONTRIBUTING.md#politique-de-compatibilité-et-dépréciation).
