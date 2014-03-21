# Create your views here.
from main.models import Movie as Movvie ,Review
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world. You're at the poll index.")

def all(request):
    movies = Movvie.objects.all()

    return render_to_response('index.html',
                              {"movs": movies},
                               context_instance=RequestContext(request))
