from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("add-module/<int:module_id>", views.add_module, name="add-module"),
    path("move/<int:module_index>/<int:new_index>", views.move_module, name="move-module"),
    path("module/<int:module_index>", views.remove_module, name="remove-module"),
    path("reset", views.reset, name="reset"),

    path("export", views.export, name="export"),
    path("request-import", views.request_import, name="import"),
    path("import", views.do_import, name="import"),
    
    path("download", views.download, name="dl")
]