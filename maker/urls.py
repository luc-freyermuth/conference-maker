from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("download", views.download, name="dl"),
    path("add-module/<int:module_id>", views.add_module, name="add-module"),
    path("move/<int:module_index>/<int:new_index>", views.move_module, name="move-module"),
    path("module/<int:module_index>", views.remove_module, name="remove-module"),
    path("reset", views.reset, name="reset")
]