from django.shortcuts import render
from django.http import HttpResponse
import os
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from django.template import loader
from .win32_powerpoint_builder import merge_presentations
from datetime import datetime

import pythoncom

OPTIONS = ["GP_1.pptx", "GP_2.pptx", "EE_1.pptx", "EE_2.pptx", "LY_1.pptx"]

# Create your views here.
def index(request):
    print(request)
    response =  HttpResponse("<form method='POST' action='download'><button>Download</button></form>")
    template = loader.get_template("maker/index.html")
    context = {
        "options": OPTIONS,
    }
    return HttpResponse(template.render(context, request))

# DO NOT KEEP THIS
@csrf_exempt
def download(request):
    shows = request.POST.getlist('val')
    files = [f"modules_files/{show}" for show in shows]
    pythoncom.CoInitialize()
    created_file_path = merge_presentations(files, f"out/out_{datetime.now().strftime('%m_%d_%Y %H_%M_%S')}.pptx")
    if os.path.exists(created_file_path):
        with open(created_file_path, 'rb') as fh:
            response = HttpResponse(fh.read())
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(created_file_path)
            return response
    raise Http404