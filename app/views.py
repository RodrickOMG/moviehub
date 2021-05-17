from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.hashers import make_password, check_password
from . import models, utilities
from django.core import paginator
from django.db.models import Sum
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
    like_flag = False
    try:
        if not request.session['is_login']:
            pass
        else:
            user_id = request.session['user_id']
            like_model = models.Like.objects.all().filter(user_id_id=user_id, movie_id_id=movie_id).first()
            utilities.browser_history(user_id, movie_id)
            if like_model:
                like_flag = True
            else:
                pass
    except:
        pass
    single_movie = models.Movie.objects.filter(movie_id=movie_id).first()
    movie_title = single_movie.movie_title
    genres_original = single_movie.genres
    genres = genres_original.replace("|", " | ")
    summary = single_movie.summary
    release_date = single_movie.release_date
    stars_original = single_movie.stars
    stars = stars_original.replace("|", " | ")
    director = single_movie.director
    time = single_movie.time
    poster_url = single_movie.poster_url
    rating = single_movie.rating
    rating_count = single_movie.rating_count
    recommended_movies_df = re.get_movie_recommendation(movie_id)
    recommended_movies = utilities.get_recommended_movies_info(recommended_movies_df)
    context = {
        'movie_id': movie_id,
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
        'like': like_flag,
    }
    return render(request, 'single.html', context)


def profile(request):
    try:
        if not request.session['is_login']:
            return render(request, 'notlogin.html')
        else:
            user_id = request.session['user_id']
            rating_count = models.Rating.objects.all().filter(user_id_id=user_id).count()
            all_scores = models.Rating.objects.filter(user_id_id=user_id).aggregate(rating_score_sum=Sum('rating'))
            fav_movie_list = utilities.get_fav_movie_list(user_id)
            rating_movie_list = utilities.get_rating_movie_list(user_id)
            history_movie_list = utilities.get_browsing_history_movie_list(user_id)
            if len(fav_movie_list) >= 20:
                fav_movie_list = fav_movie_list[0:20]
            if len(history_movie_list) >= 20:
                history_movie_list = history_movie_list[0:20]
            else:
                pass
            rating_score_sum = all_scores['rating_score_sum']
            if rating_score_sum:
                avg_score = round(rating_score_sum / rating_count, 2)
            else:
                avg_score = 0
            context = {
                'username': request.session['username'],
                'rating_count': rating_count,
                'avg_score': avg_score,
                'fav_movie_list': fav_movie_list,
                'rating_movie_list': rating_movie_list,
                'history_movie_list': history_movie_list,
            }
            return render(request, 'profile.html', context)
    except:
        return render(request, '404.html')


def like(request):
    try:
        if not request.session['is_login']:
            return render(request, 'notlogin.html')
        else:
            user_id = request.session['user_id']
            movie_id = request.GET.get('movieId')
            like_model = models.Like.objects.all().filter(user_id_id=user_id, movie_id_id=movie_id).first()
            if not like_model:
                utilities.like_movie(user_id, movie_id)
            return movie(request, movie_id)
    except:
        return render(request, 'notlogin.html')
    # print(request.GET.get('movieId'))
    # return movie(request, request.GET.get('movieId'))


def dislike(request):
        user_id = request.session['user_id']
        movie_id = request.GET.get('movieId')
        like_model = models.Like.objects.all().filter(user_id_id=user_id, movie_id_id=movie_id).first()
        if like_model:
            utilities.dislike_movie(user_id, movie_id)
        return movie(request, movie_id)


def favorite(request):
    try:
        if not request.session['is_login']:
            return render(request, 'notlogin.html')
        else:
            user_id = request.session['user_id']
            rating_count = models.Rating.objects.all().filter(user_id_id=user_id).count()
            all_scores = models.Rating.objects.filter(user_id_id=user_id).aggregate(rating_score_sum=Sum('rating'))
            fav_movie_id_list = models.Like.objects.all().order_by('-timestamp').filter(user_id_id=user_id)
            fav_movie_list = []
            if fav_movie_id_list:
                for movie_like in fav_movie_id_list:
                    movie_id = movie_like.movie_id_id
                    fav_movie_list.append(models.Movie.objects.all().filter(movie_id=movie_id).first())
            else:
                pass
            rating_score_sum = all_scores['rating_score_sum']
            avg_score = round(rating_score_sum / rating_count, 2)
            context = {
                'username': request.session['username'],
                'rating_count': rating_count,
                'avg_score': avg_score,
                'fav_movie_list': fav_movie_list,
            }
            return render(request, 'favorite.html', context)
    except:
        return render(request, 'notlogin.html')