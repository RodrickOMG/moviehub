from django.urls import path, re_path
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf.urls import url

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index, name='index'),
    path('404/', views.error_page, name='404'),
    re_path(r'404.html', views.error_page),
    path('login/', views.login, name='login'),
    re_path(r'login.html', views.login),
    path('register/', views.register, name='register'),
    re_path(r'register.html', views.register),
    path('logout/', views.logout, name='logout'),
    path('contact/', views.contact, name='contact'),
    re_path(r'contact.html', views.contact),
    url(r'^topmovies/$', views.topmovies),
    url(r'^movie/(\d*)$', views.movie),
]