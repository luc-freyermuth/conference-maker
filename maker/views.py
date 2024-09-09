from django.shortcuts import render
from django.http import HttpResponse
import os
from django.http import Http404
from django.template import loader
from .win32_powerpoint_builder import merge_presentations
from datetime import datetime
from .models import ConferenceModule, ConferenceModuleTag
from django.views.decorators.http import require_POST
from django.template import loader
import numpy as np
from itertools import groupby
import math
import random

# Create your views here.
def index(request):
    print(request)
    modules = ConferenceModule.objects.all()
    return render(request, "maker/index.html", context={
        "modules": modules,
        "conference": render_conference(request.session.get("conference", []))
    })

@require_POST
def add_module(request, module_id):
    conference = request.session.get("conference", [])
    conference.append(module_id)
    request.session["conference"] = conference
    return HttpResponse(render_conference(conference))

@require_POST
def reset(request):
    conference = []
    request.session["conference"] = conference
    return HttpResponse(render_conference(conference))

def download(request):
    shows = request.session.get("conference", [])
    files = ['assets/Base.pptx'] + [ConferenceModule.objects.get(id=id).file.path for id in shows]
    created_file_path = merge_presentations(files, f"out/out_{datetime.now().strftime('%m_%d_%Y %H_%M_%S')}.pptx")
    if os.path.exists(created_file_path):
        with open(created_file_path, 'rb') as fh:
            response = HttpResponse(fh.read())
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(created_file_path)
            return response
    raise Http404

def render_conference(conference):
    template = loader.get_template("maker/conference.html")
    modules = [ConferenceModule.objects.get(id=id) for id in conference]
    modules_data = [
        {
            "image_url": module.image.url,
            "title": module.title,
            "description": module.description,
            "duration_minutes": module.duration_minutes,
            "tags_categories": [ { "category": k, "tags_details": list(v) } for k, v in groupby([{ "tag": cm.tag, "importance": math.floor(cm.tag_category_importance * 100) } for cm in ConferenceModuleTag.objects.order_by('tag__category').filter(conference_module=module.id).select_related('tag', 'tag__category')], lambda t:t["tag"].category.name) ]
        } for module in modules
    ]
    total_duration = np.sum([module.duration_minutes for module in modules])
    grp = groupby([{ "tag": cm.tag, "duration_minutes": cm.tag_category_importance * cm.conference_module.duration_minutes } for cm in ConferenceModuleTag.objects.order_by('tag__category', 'tag__name').filter(conference_module__in=[module.id for module in modules]).select_related('tag', 'tag__category', 'conference_module')], lambda t:t["tag"].category.name)
    categories_tags_repartition = [ { "category": k, "tags_details": [{"k": ka, "v": list(va)} for ka, va in groupby(v, lambda item: item["tag"].name)] } for k, v in grp ]
    print(categories_tags_repartition)
    return template.render({ "modules": modules_data, "stats": {
        "duration_minutes": total_duration,
        "chart": random.random()
    } })
