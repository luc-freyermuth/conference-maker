from django.contrib import admin
from .models import ConferenceModule

# Register your models here.
admin.site.register(ConferenceModule, list_display=['title', 'description'])