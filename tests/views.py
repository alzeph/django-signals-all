import json

from django.db import connections
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def run_sql(request):
    """Vue de test : exécute le SQL brut fourni pour exercer le middleware."""
    payload = json.loads(request.body or "{}")
    alias = payload.get("using", "default")
    sql = payload["sql"]
    params = payload.get("params", [])
    many = payload.get("many", False)

    with connections[alias].cursor() as cursor:
        if many:
            cursor.executemany(sql, params)
        else:
            cursor.execute(sql, params)

    return JsonResponse({"ok": True})
