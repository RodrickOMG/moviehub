from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader


def index(request):
    context = {}
    return render(request, 'index.html', context)


def error_page(request):
    context = {}
    return render(request, '404.html', context)

# Create your views here.
