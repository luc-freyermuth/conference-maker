from django.shortcuts import render
from django.http import HttpResponse
import os
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def index(request):
    response =  HttpResponse("<form method='POST' action='download'><button>Download</button></form>")
    return response

# DO NOT KEEP THIS
@csrf_exempt
def download(request):
    path = "assets/Base.pptx"
    if os.path.exists(path):
        with open(path, 'rb') as fh:
            response = HttpResponse(fh.read())
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(path)
            return response
    raise Http404