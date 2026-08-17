# Contribuer à django-signals-all

[English](CONTRIBUTING.md) | **Français**

Merci de vouloir contribuer ! Ce guide décrit comment mettre en place
l'environnement de développement et les attentes pour une pull request.

## Mise en place

Le projet utilise [uv](https://docs.astral.sh/uv/) pour la gestion des
dépendances et de l'environnement virtuel.

```bash
uv sync
```

## Vérifications avant de proposer une PR

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy
uv run pytest --cov=django_signals_all --cov-report=term-missing
```

La suite `pytest` tourne par défaut sur SQLite. Pour la faire tourner aussi
contre PostgreSQL et MySQL (nécessaire pour toute modification du module
`django_signals_all.sql`, dont le comportement dépend du dialecte SQL) :

```bash
docker compose up -d
DSA_TEST_DB=postgres uv run pytest
DSA_TEST_DB=mysql uv run pytest
```

Ces mêmes vérifications tournent dans la CI (`.github/workflows/ci.yml`) et
doivent toutes passer avant qu'une PR soit mergeable :

- **ruff** : lint et formatage
- **mypy** (`strict = true`, avec `django-stubs`) : le typage doit rester
  précis, y compris sur le code qui touche à l'ORM et aux signaux Django
- **pytest** : sur les trois SGBD supportés (SQLite, PostgreSQL, MySQL) et
  contre Django 4.2/5.0/5.1/5.2 ; la couverture de tests est verrouillée à
  100 % (`--cov-fail-under=100`) — toute nouvelle branche de code doit être
  testée

Si `pre-commit` est installé (`uv run pre-commit install`), ruff et mypy
tournent automatiquement avant chaque commit.

## Compatibilité

`django_signals_all` cible **Python 3.12+** et **Django 4.2+** (LTS
courante et versions suivantes). Toute PR doit rester compatible avec ces
versions minimales ; ne pas introduire de dépendance implicite à une
version plus récente sans en discuter d'abord dans une issue.

## Style de code

- Pas de commentaire qui explique le *quoi* (le code doit être lisible par
  lui-même) — seulement le *pourquoi* quand c'est non évident (contraintes
  cachées, comportement Django non documenté, contournement d'un bug connu).
- Pas d'abstraction ou de fonctionnalité ajoutée au-delà de ce que demande
  le changement.
- Toute modification du module SQL brut (`django_signals_all.sql`) doit être
  testée sur les trois SGBD : le comportement de `sqlglot` et des drivers
  DB-API diverge réellement d'un dialecte à l'autre (voir les notes dans
  `sql/engines/sqlglot_engine.py`).

## Commits et PR

- Un message de commit clair, qui explique le *pourquoi* du changement.
- Une PR = un sujet. Préférer plusieurs petites PR à une seule PR fourre-tout.
- Décrire dans la description de la PR ce qui change et comment c'est testé.

## Politique de compatibilité et dépréciation

`django_signals_all` suit le [Semantic Versioning](https://semver.org/lang/fr/).
À partir de la version `1.0.0` :

- un **major** (`X.0.0`) peut casser la compatibilité ;
- un **minor** (`1.X.0`) ajoute des fonctionnalités sans rien casser ;
- un **patch** (`1.0.X`) ne contient que des corrections de bug.

Avant `1.0.0` (versions `0.x.y`), aucune garantie de stabilité de l'API
n'est donnée.

Après `1.0.0`, toute API publique dépréciée :

1. continue de fonctionner et lève un `DeprecationWarning` explicite
   pendant au moins une version mineure complète ;
2. est documentée dans `CHANGELOG.md` sous une section `### Deprecated` ;
3. n'est retirée que dans un major suivant, jamais dans un minor ou un
   patch.

## Signaler un bug ou proposer une fonctionnalité

Ouvrez une [issue](https://github.com/alzeph/django-signals-all/issues) en
utilisant le template approprié. Pour une faille de sécurité, voir
[SECURITY.md](SECURITY.fr.md) plutôt qu'une issue publique.
