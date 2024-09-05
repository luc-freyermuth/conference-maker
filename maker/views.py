from django.shortcuts import render
from django.http import HttpResponse
import os
from django.http import Http404
from django.template import loader
from .win32_powerpoint_builder import merge_presentations
from datetime import datetime
from .models import ConferenceModule
from django.views.decorators.http import require_POST
from django.template import loader
import numpy as np

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
    modules =  [ConferenceModule.objects.get(id=id) for id in conference]
    total_duration = np.sum([module.duration_minutes for module in modules])
    return template.render({ "modules": modules, "stats": {
        "duration_minutes": total_duration
    } })