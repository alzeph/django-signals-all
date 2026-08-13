from django.urls import path

from tests import views

urlpatterns = [
    path("run-sql/", views.run_sql, name="run-sql"),
]
