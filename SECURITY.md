# Security policy

**English** | [Français](SECURITY.fr.md)

## Supported versions

`django-signals-all` is in the pre-release `1.0.0rc1`: only the latest
published version receives security fixes.

| Version    | Supported |
| ---------- | --------- |
| 1.0.0rcN   | Yes       |
| < 1.0.0rc1 | No        |

## Reporting a vulnerability

Please **do not** open a public issue for a security flaw.

The `django_signals_all.sql` module parses SQL that may be influenced by
sensitive application code paths: any flaw that allows bypassing
`EXCLUDED_TABLES`/`MONITORED_TABLES`, triggering a denial of service through
parsing, or executing code via a poorly isolated receiver is considered a
security vulnerability.

Please report privately via
[GitHub Security Advisories](https://github.com/alzeph/django-signals-all/security/advisories/new)
on this repository. Failing that, contact the author directly at
hervecedricyouan@gmail.com.

Please include:

- a description of the issue and its potential impact;
- steps to reproduce it;
- the version of `django-signals-all`, of Django, and the database involved.

We acknowledge reports within 72 hours and aim for a fix or a substantive
response within 30 days depending on severity.
