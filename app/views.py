from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.hashers import make_password, check_password
from . import models, utilities


def index(request):
    context = {}
    return render(request, 'index.html', context)


def error_page(request):
    context = {}
    return render(request, '404.html', context)

# Create your views here.


def login(request):
    if request.method == "GET":
        pass
        return render(request, 'login.html')
    elif request.method == "POST":
        context = {'message': ''}
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password)
        user = models.User.objects.filter(username=username).first()
        if user:
            if user.password == password:
                context['message'] = 'Successfully Login'
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['username'] = user.username
                return redirect('/moviehub/index/')
            else:
                context['message'] = 'Wrong password'
        else:
            context['message'] = 'User does not exist.'
        return render(request, 'login.html', context)


def register(request):
    if request.method == "GET":
        pass
        return render(request, 'register.html')
    elif request.method == "POST":
        context = {'username_message': '', 'password_message': '', 'password_confirm_message': '', 'email_message': ''}
        username = request.POST.get('r_username')
        if len(username) > 12:
            context['username_message'] = 'Username should no longer than 12 characters'
            return render(request, 'register.html', context)
        user = models.User.objects.filter(username=username).first()
        if user:
            context['username_message'] = 'User already exists.'
            return render(request, 'register.html', context)
        password = request.POST.get('r_password')
        if len(password) < 4:
            context['password_message'] = 'Password should more than 4 characters'
            return render(request, 'register.html', context)
        password_confirm = request.POST.get('password_confirm')
        if password_confirm != password:
            context['password_confirm_message'] = 'Password does not match.'
            return render(request, 'register.html', context)
        email = request.POST.get('email')
        if not utilities.check_email(email):
            context['email_message'] = 'Email format is incorrect.'
            return render(request, 'register.html', context)
        user = models.User.objects.filter(email=email).first()
        if user:
            context['email_message'] = 'Email already exists.'
            return render(request, 'register.html', context)
        gender = request.POST.get('gender')
        age = request.POST.get('age')
        occupation = request.POST.get('occupation')
        utilities.create_user(username, password, email, gender, age, occupation)
        context['message'] = 'Successfully Login'
        request.session['is_login'] = True
        user = models.User.objects.filter(username=username).first()
        request.session['user_id'] = user.id
        request.session['username'] = user.username
        return redirect('/moviehub/index/')


def logout(request):
    """登出"""
    # if not request.session.get('is_login', None):
    #     return redirect('/index/')
    # 清空session
    request.session.flush()
    # del request.session['user_id'] 清除某一个session 键
    return redirect('/moviehub/index/')


def contact(request):
    return render(request, 'contact.html')


def topmovies(request):
    return render(request, 'topmovies.html')