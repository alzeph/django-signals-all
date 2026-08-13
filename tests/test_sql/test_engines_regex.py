import pytest

from django_signals_all.sql.engines.regex_engine import RegexEngine
from django_signals_all.sql.engines.sqlglot_engine import SqlglotEngine

regex_engine = RegexEngine()
sqlglot_engine = SqlglotEngine()


@pytest.mark.parametrize(
    ("sql", "operation", "table"),
    [
        ("INSERT INTO crm_client (name) VALUES (%s)", "INSERT", "crm_client"),
        ("UPDATE crm_client SET name = %s WHERE id = %s", "UPDATE", "crm_client"),
        ("DELETE FROM crm_client WHERE id = %s", "DELETE", "crm_client"),
        ("insert into crm_client(name) values ('x')", "INSERT", "crm_client"),
    ],
)
def test_detects_dml_operation_and_table(sql, operation, table):
    result = regex_engine.parse(sql, "postgresql")

    assert result is not None
    assert result.operation == operation
    assert result.table == table


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM crm_client",
        "CREATE TABLE crm_client (id integer)",
        "ALTER TABLE crm_client ADD COLUMN age integer",
    ],
)
def test_ignores_non_dml_statements(sql):
    assert regex_engine.parse(sql, "postgresql") is None


def test_quoted_identifier():
    result = regex_engine.parse('UPDATE "crm_client" SET name = %s', "postgresql")

    assert result.table == "crm_client"


def test_backtick_quoted_identifier_mysql_style():
    result = regex_engine.parse("UPDATE `crm_client` SET name = %s", "mysql")

    assert result.table == "crm_client"


def test_schema_qualified_table():
    result = regex_engine.parse("UPDATE public.crm_client SET name = %s", "postgresql")

    assert result.table == "crm_client"


def test_invalid_sql_does_not_raise_and_returns_none():
    assert regex_engine.parse("ceci n'est pas du SQL", "postgresql") is None


def test_cte_is_a_known_limitation_of_the_regex_engine():
    # Contrairement au moteur sqlglot, le moteur regex ne comprend pas les
    # CTE : il ne reconnaît pas le mot-clé de tête "WITH" et ne détecte donc
    # pas la table cible. C'est une limitation documentée, pas un bug.
    sql = (
        "WITH recent AS (SELECT id FROM crm_client) "
        "UPDATE crm_client SET name = 'x' FROM recent WHERE crm_client.id = recent.id"
    )

    assert regex_engine.parse(sql, "postgresql") is None


@pytest.mark.parametrize(
    "sql",
    [
        "INSERT INTO crm_client (name) VALUES (%s)",
        "UPDATE crm_client SET name = %s WHERE id = %s",
        "DELETE FROM crm_client WHERE id = %s",
    ],
)
def test_both_engines_agree_on_simple_statements(sql):
    regex_result = regex_engine.parse(sql, "postgresql")
    sqlglot_result = sqlglot_engine.parse(sql, "postgresql")

    assert regex_result == sqlglot_result
