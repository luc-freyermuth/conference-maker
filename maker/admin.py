from django.contrib import admin
from .models import ConferenceModule, Tag, TagCategory, ConferenceModuleTag

# Register your models here.
admin.site.register(ConferenceModule, list_display=['title', 'description', 'duration_minutes'])
admin.site.register(TagCategory, list_display=['name'])
admin.site.register(Tag, list_display=['name', 'category'])
admin.site.register(ConferenceModuleTag, list_display=['conference_module', 'tag', 'tag_category_importance'])
