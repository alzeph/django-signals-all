import json

from django.db import connections
from django.test import Client


def post_sql(sql, params=None, using="default", many=False):
    # Les tests écrivent leur SQL avec le style de placeholder sqlite ("?")
    # pour rester portables ; on l'adapte au style attendu par le backend
    # réellement ciblé (postgres/mysql utilisent "%s").
    if connections[using].vendor != "sqlite":
        sql = sql.replace("?", "%s")

    client = Client()
    return client.post(
        "/run-sql/",
        data=json.dumps(
            {"sql": sql, "params": params or [], "using": using, "many": many}
        ),
        content_type="application/json",
    )
