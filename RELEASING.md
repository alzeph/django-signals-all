# Release process

**English** | [Français](RELEASING.fr.md)

This document describes how to publish a new version of `django-signals-all`
to PyPI. It is aimed at anyone with the necessary rights on the repository
(not only the original maintainer): following these steps in order should be
enough, without any implicit knowledge of the project beyond what is written
here.

## Who can publish

- Write access to the `alzeph/django-signals-all` GitHub repository (to
  create a branch, a tag, and push to `main`).
- Rights to create/approve a
  [GitHub Release](https://github.com/alzeph/django-signals-all/releases).
  If the `pypi` environment (see below) has reviewers configured, their
  approval is required before `publish.yml` runs.
- No personal PyPI account is required to publish: authorization goes through
  the *trusted publishing* OIDC setup configured once and for all (see
  below), not through an individual token.

## Initial PyPI setup (one-time, already done for this repository)

`django-signals-all` publishes via PyPI's *trusted publishing* (OIDC): no
long-lived token to manage, authorization is tied to this exact repository
and GitHub Actions workflow. This setup only needs to be redone if the
repository is renamed/moved, or if the trusted publisher is revoked.

1. Create a PyPI account if needed.
2. On <https://pypi.org/manage/account/publishing/>, add a *pending trusted
   publisher* (the project does not need to already exist on PyPI):
   - PyPI project name: `django-signals-all`
   - Owner: `alzeph`
   - Repository name: `django-signals-all`
   - Workflow name: `publish.yml`
   - Environment name: `pypi`
3. In the repository's GitHub settings (`Settings > Environments`), create a
   `pypi` environment (protects publishing, allows adding reviewers if
   needed).

## Publishing a version

### 1. Choose the version number

Follow [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`, with
an `rcN` suffix while still in the release candidate phase (see below). If
in doubt about the type of bump, refer to the
[Compatibility policy](CONTRIBUTING.md#compatibility-and-deprecation-policy)
section of CONTRIBUTING.md.

### 2. Prepare a release branch

Do not commit directly to `main`. Create a dedicated branch:

```bash
git checkout -b release/X.Y.Z
```

On this branch:

1. Update `__version__` in `src/django_signals_all/__init__.py` (the package
   version is single-sourced from this file, see `[tool.hatch.version]` in
   `pyproject.toml`).
2. Move the content of `## [Unreleased]` into `CHANGELOG.md` under a new
   `## [X.Y.Z] - YYYY-MM-DD` section, and update the comparison links at the
   bottom of the file.

### 3. Verify locally

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

All of these commands must pass before continuing. They correspond exactly
to what CI (`.github/workflows/ci.yml`) re-checks on the PR.

### 4. Open a PR and merge

```bash
git add -A
git commit -m "Release X.Y.Z"
git push -u origin release/X.Y.Z
gh pr create --base main --title "Release X.Y.Z" --body "See CHANGELOG.md"
```

Wait for CI to pass on the PR, then merge into `main`.

### 5. Tag

Switch back to an up-to-date `main`, then create an **annotated tag** (carries
a message and an author, unlike a lightweight tag — this is the standard
practice for marking a release):

```bash
git checkout main
git pull origin main
git tag -a vX.Y.Z -m "Release X.Y.Z"
git push origin vX.Y.Z
```

### 6. Create the GitHub Release

Create a
[GitHub Release](https://github.com/alzeph/django-signals-all/releases/new)
from the `vX.Y.Z` tag, with release notes taken from `CHANGELOG.md`.
Publishing it triggers `.github/workflows/publish.yml`, which automatically
builds and publishes to PyPI.

- For a pre-release (`rc`, `b`, `a`), check **"Set as a pre-release"** on
  GitHub — PyPI will treat it as a pre-release (not installed by default by
  `pip install django-signals-all`; requires
  `pip install django-signals-all --pre` or pinning the exact version).
- Then verify that the `publish` job in `.github/workflows/publish.yml`
  completes successfully (`gh run watch` or the repository's Actions tab) and
  that the version appears on
  <https://pypi.org/project/django-signals-all/>.

## Release candidate policy before the final 1.0.0

`1.0.0rc1` is a *release candidate*: the API is considered frozen but has not
yet been battle-tested by real-world usage outside of this repository. Before
tagging `1.0.0` (final):

- leave the RC available for at least a few weeks to gather feedback (issues,
  real use cases, possible bugs in the raw SQL module or the `bulk_update`
  signal aggregation);
- only merge bug fixes into `main` during this period, no new feature that
  would change the public API;
- if an API change turns out to be necessary based on feedback, publish
  `1.0.0rc2` rather than modifying `1.0.0rc1` after the fact.

In particular, the `pg_notify` module (roadmap, see README) does not exist
yet and may reshape the existing signals' API if it reveals a need for
cross-cutting consistency — this is another reason not to rush the move to
the final `1.0.0`.

Once `1.0.0` is tagged, see the compatibility policy in
[CONTRIBUTING.md](CONTRIBUTING.md#compatibility-and-deprecation-policy).
