from django.shortcuts import render
from django.http import HttpResponse
import os
from django.http import Http404
from django.template import loader
from .win32_powerpoint_builder import merge_presentations
from datetime import datetime
from .models import ConferenceModule

# Create your views here.
def index(request):
    print(request)
    modules = ConferenceModule.objects.all()
    return render(request, "maker/index.html", context={
        "modules": modules
    })

def download(request):
    shows = request.POST.getlist('val')
    files = [ConferenceModule.objects.get(id=id).file.path for id in shows]
    created_file_path = merge_presentations(files, f"out/out_{datetime.now().strftime('%m_%d_%Y %H_%M_%S')}.pptx")
    if os.path.exists(created_file_path):
        with open(created_file_path, 'rb') as fh:
            response = HttpResponse(fh.read())
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(created_file_path)
            return response
    raise Http404