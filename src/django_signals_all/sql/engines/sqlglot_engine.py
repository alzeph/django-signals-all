import logging
import re

import sqlglot
from sqlglot import exp

from django_signals_all.sql.engines.base import ParsedStatement

logger = logging.getLogger("django_signals_all.sql")

_VENDOR_TO_DIALECT = {
    "postgresql": "postgres",
    "mysql": "mysql",
    "sqlite": "sqlite",
}

_NAMED_PLACEHOLDER_RE = re.compile(r"%\(\w+\)s")
_POSITIONAL_PLACEHOLDER_RE = re.compile(r"%s")


def _normalize_placeholders(sql: str) -> str:
    # sqlglot interprète parfois "%s" comme l'opérateur modulo (surtout en
    # dialecte MySQL), ce qui fait échouer le parsing d'un INSERT/UPDATE
    # paramétré au style DB-API. On neutralise les styles de placeholders
    # Django (%s, %(nom)s, ?) avant analyse ; le SQL transmis au signal
    # reste, lui, inchangé.
    sql = _NAMED_PLACEHOLDER_RE.sub("?", sql)
    sql = _POSITIONAL_PLACEHOLDER_RE.sub("?", sql)
    return sql


class SqlglotEngine:
    """Moteur de parsing basé sur l'AST sqlglot (multi-dialecte)."""

    def parse(self, sql: str, vendor: str) -> ParsedStatement | None:
        dialect = _VENDOR_TO_DIALECT.get(vendor)
        try:
            tree = sqlglot.parse_one(_normalize_placeholders(sql), dialect=dialect)
        except Exception:
            # sqlglot lève des exceptions variées (ParseError, TokenError,
            # ValueError...) sur du SQL non standard ou spécifique au moteur.
            # On ne doit jamais faire planter l'application hôte pour ça.
            logger.warning(
                "django_signals_all: échec du parsing sqlglot du SQL brut",
                exc_info=True,
            )
            return None

        if isinstance(tree, exp.Insert):
            operation = "INSERT"
        elif isinstance(tree, exp.Update):
            operation = "UPDATE"
        elif isinstance(tree, exp.Delete):
            operation = "DELETE"
        else:
            return None

        target = tree.this
        if isinstance(target, exp.Schema):
            target = target.this
        table = target.name if isinstance(target, exp.Table) else None

        return ParsedStatement(operation=operation, table=table)
