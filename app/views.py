from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.hashers import make_password, check_password
from . import models, utilities
from django.core import paginator
from . import recommendation as re


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
    index = request.GET.get('index')
    sort_option = request.GET.get('sort')
    genres_option = request.GET.get('genres')
    print(index, sort_option, genres_option)
    if index is None:
        index = 1
    if sort_option is None:
        sort_option = '1'
    if genres_option is None:
        genres_option = '1'
    genres = utilities.get_genres_type(genres_option)
    if sort_option == '1':
        movie_list = models.Movie.objects.all().order_by('-rating').filter(rating_count__gt=20, genres__contains=genres)
    elif sort_option == '2':
        movie_list = models.Movie.objects.all().order_by('rating').filter(rating_count__gt=20, genres__contains=genres)
    elif sort_option == '3':
        movie_list = models.Movie.objects.all().order_by('-popularity').filter(rating_count__gt=20, genres__contains=genres)
    elif sort_option == '4':
        movie_list = models.Movie.objects.all().order_by('popularity').filter(rating_count__gt=20, genres__contains=genres)
    else:
        movie_list = models.Movie.objects.all().order_by('-rating').filter(rating_count__gt=20, genres__contains=genres)
    if len(movie_list) >= 250:
        movie_list = movie_list[0:250]
    else:
        movie_list = movie_list[0:len(movie_list)]
    pag = paginator.Paginator(movie_list, 20)
    if index == '':
        index = 1
    page = pag.page(index)
    context = {
        'page': page,
        'sort_selected': sort_option,
        'genres_selected': genres_option,
    }
    return render(request, 'topmovies.html', context)


def movie(request, movie_id):
    single_movie = models.Movie.objects.filter(movie_id=movie_id).first()
    movie_title = single_movie.movie_title
    genres = single_movie.genres
    summary = single_movie.summary
    release_date = single_movie.release_date
    stars = single_movie.stars
    director = single_movie.director
    time = single_movie.time
    poster_url = single_movie.poster_url
    rating = single_movie.rating
    rating_count = single_movie.rating_count
    recommended_movies_df = re.get_movie_recommendation(movie_id)
    recommended_movies = utilities.get_recommended_movies_info(recommended_movies_df)
    context = {
        'movie_title': movie_title,
        'genres': genres,
        'summary': summary,
        'release_date': release_date,
        'stars': stars,
        'director': director,
        'time': time,
        'poster_url': poster_url,
        'rating': rating,
        'rating_count': rating_count,
        'recommended_movies': recommended_movies,
    }
    return render(request, 'single.html', context)