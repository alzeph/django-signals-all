import contextlib
import threading
from collections.abc import Callable
from typing import Any

from django.db import connections
from django.http import HttpRequest, HttpResponse

from django_signals_all.conf import app_settings
from django_signals_all.signals import raw_sql_executed
from django_signals_all.sql.engines.base import ParseEngine
from django_signals_all.sql.engines.regex_engine import RegexEngine
from django_signals_all.sql.engines.sqlglot_engine import SqlglotEngine

_ENGINES: dict[str, ParseEngine] = {
    "sqlglot": SqlglotEngine(),
    "regex": RegexEngine(),
}
_DEFAULT_ENGINE_KEY = "sqlglot"

_DML_KEYWORDS = {"INSERT", "UPDATE", "DELETE"}

_local = threading.local()


class RawSQLSignalMiddleware:
    """Émet raw_sql_executed pour les INSERT/UPDATE/DELETE exécutés en SQL brut.

    Encadre chaque requête HTTP d'un connection.execute_wrapper par base de
    données, conformément au design prévu par Django pour cette API (elle
    n'est pas censée rester active en dehors d'un bloc `with`).
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if not app_settings.ENABLE_RAW_SQL_INTERCEPTOR:
            return self.get_response(request)

        with contextlib.ExitStack() as stack:
            for connection in connections.all():
                stack.enter_context(connection.execute_wrapper(self._wrap))
            return self.get_response(request)

    def _wrap(
        self,
        execute: Callable[[str, Any, bool, dict[str, Any]], Any],
        sql: str,
        params: Any,
        many: bool,
        context: dict[str, Any],
    ) -> Any:
        result = execute(sql, params, many, context)

        if getattr(_local, "in_progress", False):
            return result
        if not raw_sql_executed.receivers:
            return result

        keyword = sql.lstrip()[:6].upper()
        if keyword not in _DML_KEYWORDS:
            return result

        connection = context["connection"]
        engine = _ENGINES.get(
            app_settings.SQL_PARSER_ENGINE, _ENGINES[_DEFAULT_ENGINE_KEY]
        )

        _local.in_progress = True
        try:
            parsed = engine.parse(sql, connection.vendor)
            if parsed is None or parsed.table is None:
                return result

            table = parsed.table
            if table in (app_settings.EXCLUDED_TABLES or []):
                return result

            monitored = app_settings.MONITORED_TABLES
            if monitored is not None and table not in monitored:
                return result

            raw_sql_executed.send(
                sender=table,
                operation=parsed.operation,
                sql=sql,
                params=params,
                using=connection.alias,
            )
        finally:
            _local.in_progress = False

        return result
