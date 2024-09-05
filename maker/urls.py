from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("download", views.download, name="dl"),
    path("add-module/<int:module_id>", views.add_module, name="add-module"),
    path("reset", views.reset, name="reset")
]