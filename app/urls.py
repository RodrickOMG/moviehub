from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    re_path(r'index.html', views.index),
    path('404', views.error_page, name='404'),
    re_path(r'404.html', views.error_page),
]