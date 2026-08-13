import pytest

from django_signals_all.sql.engines.sqlglot_engine import SqlglotEngine

engine = SqlglotEngine()


@pytest.mark.parametrize("vendor", ["postgresql", "mysql", "sqlite"])
@pytest.mark.parametrize(
    ("sql", "operation", "table"),
    [
        ("INSERT INTO crm_client (name) VALUES (%s)", "INSERT", "crm_client"),
        ("UPDATE crm_client SET name = %s WHERE id = %s", "UPDATE", "crm_client"),
        ("DELETE FROM crm_client WHERE id = %s", "DELETE", "crm_client"),
    ],
)
def test_detects_dml_operation_and_table_across_dialects(vendor, sql, operation, table):
    result = engine.parse(sql, vendor)

    assert result is not None
    assert result.operation == operation
    assert result.table == table


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM crm_client",
        "CREATE TABLE crm_client (id integer)",
        "ALTER TABLE crm_client ADD COLUMN age integer",
        "EXPLAIN SELECT * FROM crm_client",
    ],
)
def test_ignores_non_dml_statements(sql):
    assert engine.parse(sql, "postgresql") is None


def test_quoted_identifier():
    result = engine.parse('UPDATE "crm_client" SET name = %s', "postgresql")

    assert result.operation == "UPDATE"
    assert result.table == "crm_client"


def test_schema_qualified_table():
    result = engine.parse("UPDATE public.crm_client SET name = %s", "postgresql")

    assert result.operation == "UPDATE"
    assert result.table == "crm_client"


def test_cte_update_detects_target_table_not_cte_alias():
    sql = (
        "WITH recent AS (SELECT id FROM crm_client) "
        "UPDATE crm_client SET name = 'x' "
        "FROM recent WHERE crm_client.id = recent.id"
    )

    result = engine.parse(sql, "postgresql")

    assert result.operation == "UPDATE"
    assert result.table == "crm_client"


def test_mysql_style_positional_placeholder_does_not_crash():
    # sqlglot interprète "%s" comme un modulo dans certains contextes MySQL ;
    # la normalisation interne doit éviter le ParseError.
    result = engine.parse("INSERT INTO users_user (name) VALUES (%s)", "mysql")

    assert result.operation == "INSERT"
    assert result.table == "users_user"


def test_invalid_sql_does_not_raise_and_returns_none():
    assert engine.parse("ceci n'est pas du SQL valide ; ; ;", "postgresql") is None


def test_unknown_vendor_falls_back_without_crashing():
    result = engine.parse("UPDATE crm_client SET name = 'x'", "oracle")

    assert result.operation == "UPDATE"
    assert result.table == "crm_client"
