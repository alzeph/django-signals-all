# Process de release

[English](RELEASING.md) | **Français**

Ce document décrit comment publier une nouvelle version de
`django-signals-all` sur PyPI. Il s'adresse à toute personne ayant les
droits nécessaires sur le dépôt (pas seulement au mainteneur d'origine) :
suivre ces étapes dans l'ordre doit suffire, sans connaissance implicite du
projet au-delà de ce qui est écrit ici.

## Qui peut publier

- Un accès en écriture sur le dépôt GitHub `alzeph/django-signals-all`
  (pour créer une branche, un tag, et pousser sur `main`).
- Les droits pour créer/approuver une [GitHub Release](https://github.com/alzeph/django-signals-all/releases).
  Si l'environnement `pypi` (voir plus bas) a des reviewers configurés, leur
  approbation est nécessaire avant que `publish.yml` ne s'exécute.
- Aucun compte PyPI personnel n'est requis pour publier : l'autorisation
  passe par le *trusted publishing* OIDC configuré une fois pour toutes
  (voir ci-dessous), pas par un token individuel.

## Configuration initiale de PyPI (une seule fois, déjà faite pour ce dépôt)

`django-signals-all` publie via le *trusted publishing* de PyPI (OIDC) :
aucun token long-lived à gérer, l'autorisation est liée à ce dépôt et à ce
workflow GitHub Actions précis. Cette configuration n'est à refaire que si
le dépôt est renommé/déplacé, ou si le trusted publisher est révoqué.

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

### 1. Choisir le numéro de version

Suivre le [Semantic Versioning](https://semver.org/lang/fr/) : `MAJOR.MINOR.PATCH`,
avec un suffixe `rcN` tant qu'on est en phase de release candidate (voir
plus bas). En cas de doute sur le type de bump, se référer à la section
[Politique de compatibilité](CONTRIBUTING.fr.md#politique-de-compatibilité-et-dépréciation)
de CONTRIBUTING.md.

### 2. Préparer une branche de release

Ne pas committer directement sur `main`. Créer une branche dédiée :

```bash
git checkout -b release/X.Y.Z
```

Sur cette branche :

1. Mettre à jour `__version__` dans `src/django_signals_all/__init__.py`
   (la version du package est single-sourcée depuis ce fichier, voir
   `[tool.hatch.version]` dans `pyproject.toml`).
2. Déplacer le contenu de `## [Unreleased]` dans `CHANGELOG.md` sous une
   nouvelle section `## [X.Y.Z] - AAAA-MM-JJ`, et mettre à jour les liens
   de comparaison en bas de fichier.

### 3. Vérifier localement

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy
uv run pytest --cov=django_signals_all --cov-fail-under=100
docker compose up -d
DSA_TEST_DB=postgres uv run pytest
DSA_TEST_DB=mysql uv run pytest
docker compose down
uv build
```

Toutes ces commandes doivent passer avant de continuer. Elles correspondent
exactement à ce que la CI (`.github/workflows/ci.yml`) revérifie sur la PR.

### 4. Ouvrir une PR et merger

```bash
git add -A
git commit -m "Release X.Y.Z"
git push -u origin release/X.Y.Z
gh pr create --base main --title "Release X.Y.Z" --body "Voir CHANGELOG.md"
```

Attendre que la CI passe sur la PR, puis merger dans `main`.

### 5. Tagger

Se remettre sur `main` à jour, puis créer un **tag annoté** (porte un
message et un auteur, contrairement à un tag léger — c'est la pratique
standard pour marquer une release) :

```bash
git checkout main
git pull origin main
git tag -a vX.Y.Z -m "Release X.Y.Z"
git push origin vX.Y.Z
```

### 6. Créer la GitHub Release

Créer une [GitHub Release](https://github.com/alzeph/django-signals-all/releases/new)
à partir du tag `vX.Y.Z`, avec les notes de version reprises de
`CHANGELOG.md`. La publier déclenche `.github/workflows/publish.yml`, qui
build et publie automatiquement sur PyPI.

- Pour une pré-version (`rc`, `b`, `a`), cocher **"Set as a pre-release"**
  sur GitHub — PyPI la traitera comme une pré-version (non installée par
  défaut par `pip install django-signals-all`, il faudra
  `pip install django-signals-all --pre` ou fixer la version exacte).
- Vérifier ensuite que le job `publish` de `.github/workflows/publish.yml`
  se termine avec succès (`gh run watch` ou l'onglet Actions du dépôt) et
  que la version apparaît sur <https://pypi.org/project/django-signals-all/>.

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
[CONTRIBUTING.md](CONTRIBUTING.fr.md#politique-de-compatibilité-et-dépréciation).
