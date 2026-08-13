import re

from django_signals_all.sql.engines.base import ParsedStatement

_PATTERN = re.compile(
    r"""^\s*
    (?:
        (?P<insert>INSERT\s+INTO)
        |(?P<update>UPDATE)
        |(?P<delete>DELETE\s+FROM)
    )
    \s+
    (?P<table>[`"\[]?\w+[`"\]]?(?:\.[`"\[]?\w+[`"\]]?)?)
    """,
    re.IGNORECASE | re.VERBOSE,
)


class RegexEngine:
    """Moteur de repérage léger par expression régulière, sans dépendance."""

    def parse(self, sql: str, vendor: str) -> ParsedStatement | None:
        match = _PATTERN.match(sql)
        if match is None:
            return None

        if match.group("insert"):
            operation = "INSERT"
        elif match.group("update"):
            operation = "UPDATE"
        else:
            operation = "DELETE"

        table = match.group("table").rsplit(".", maxsplit=1)[-1].strip('`"[]')
        return ParsedStatement(operation=operation, table=table)
