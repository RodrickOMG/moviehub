from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.hashers import make_password, check_password


def index(request):
    context = {}
    return render(request, 'index.html', context)


def error_page(request):
    context = {}
    return render(request, '404.html', context)

# Create your views here.


def login(request):
    context = {}
    return render(request, 'login.html', context)


def register(request):
    context = {}
    return render(request, 'register.html', context)