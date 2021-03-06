import re
import pymysql
import time
from . import models
from django.db.models import Q


def check_email(email):
    if email is not None:
        c = re.compile(r'^\w+@(\w+\.)+(com|cn|net)$')
        s = c.search(email)
        if s:
            return True
        else:
            return False
    else:
        return False


def create_user(username, password, email, gender, age, occupation, fav_genres):
    register_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    db = pymysql.connect(host="localhost", user="root", password="123456", database="moviehub", charset="utf8")
    if gender == 'F':
        profile_pic = '../../static/images/user/default/girl-1.png'
    elif gender == 'M':
        profile_pic = '../../static/images/user/default/boy-1.png'
    else:
        profile_pic = '../../static/images/user/default/spiderman.png'
    cursor = db.cursor()
    sql = "INSERT INTO app_user (username,age,gender,occupation,profile_pic,password,register_time,email,fav_genres) values" \
          "  (%s,%s,%s,%s,%s,%s,%s,%s,%s);"
    cursor.execute(sql,
                   [username, age, gender, occupation, profile_pic, password, register_time, email, fav_genres])
    db.commit()
    cursor.close()
    db.close()


def get_rating_user_count(movie_id):
    db = pymysql.connect(host="localhost", user="root", password="123456", database="moviehub", charset="utf8")
    cursor = db.cursor()
    sql = 'SELECT * FROM app_rating where movie_id_id="%s";' % movie_id
    cursor.execute(sql)
    rating_results = cursor.fetchall()
    return len(rating_results)


def get_recommended_movies_info(movie_df):
    recommended_movies_json = []
    for row in movie_df.itertuples():
        movie_id = getattr(row, 'movieId')
        distance = getattr(row, 'Distance')
        movie = models.Movie.objects.filter(movie_id=movie_id).first()
        movie_title = movie.movie_title
        poster_url = movie.poster_url
        json = {'movie_id': movie_id, 'movie_title': movie_title, 'poster_url': poster_url, 'distance': distance}
        recommended_movies_json.append(json)
    recommended_movies_json.reverse()
    return recommended_movies_json


def get_genres_type(genres_option):
    if genres_option == '1':
        return ''
    else:
        return genres_option


def like_movie(user_id, movie_id):
    like_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    db = pymysql.connect(host="localhost", user="root", password="123456", database="moviehub", charset="utf8")
    cursor = db.cursor()
    sql = "INSERT INTO app_like (user_id_id, movie_id_id, timestamp) values" \
          "  (%s,%s,%s);"
    cursor.execute(sql,
                   [user_id, movie_id, like_time])
    db.commit()
    cursor.close()
    db.close()


def dislike_movie(user_id, movie_id):
    db = pymysql.connect(host="localhost", user="root", password="123456", database="moviehub", charset="utf8")
    cursor = db.cursor()
    sql = "DELETE FROM app_like WHERE movie_id_id=%s and user_id_id=%s;" % (movie_id, user_id)
    cursor.execute(sql)
    db.commit()
    cursor.close()
    db.close()


def get_fav_movie_list(user_id):
    fav_movie_id_list = models.Like.objects.all().order_by('-timestamp').filter(user_id_id=user_id)
    fav_movie_list = []
    if fav_movie_id_list:
        for movie_like in fav_movie_id_list:
            movie_id = movie_like.movie_id_id
            fav_movie_list.append(models.Movie.objects.all().filter(movie_id=movie_id).first())
    return fav_movie_list


def get_rating_movie_list(user_id):
    ratings_list = models.Rating.objects.all().order_by('-timestamp').filter(user_id_id=user_id)
    rating_movie_list = []
    if ratings_list:
        for rating_model in ratings_list:
            rating_movie = {'movie_id': rating_model.movie_id_id, 'movie_title': models.Movie.objects.all().filter(
                movie_id=rating_model.movie_id_id).first().movie_title, 'rating_date': rating_model.timestamp,
                            'rating': rating_model.rating}
            rating_movie_list.append(rating_movie)
            if len(rating_movie_list) > 20:
                break
    return rating_movie_list


def get_browsing_history_movie_list(user_id):
    history_movie_id_list = models.History.objects.all().order_by('-timestamp').filter(user_id_id=user_id)
    history_movie_list = []
    if history_movie_id_list:
        for movie_history in history_movie_id_list:
            movie_id = movie_history.movie_id_id
            history_movie_list.append(models.Movie.objects.all().filter(movie_id=movie_id).first())
    return history_movie_list


def browser_history(user_id, movie_id):
    browser_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    history_model = models.History.objects.all().filter(movie_id_id=movie_id, user_id_id=user_id).first()
    db = pymysql.connect(host="localhost", user="root", password="123456", database="moviehub", charset="utf8")
    cursor = db.cursor()
    if history_model:
        count = history_model.count
        count = count+1
        sql = "UPDATE app_history set count=%s, timestamp=%s where movie_id_id=%s and user_id_id=%s "
        cursor.execute(sql, [count, browser_time, movie_id, user_id])
    else:
        sql = "INSERT INTO app_history (user_id_id, movie_id_id, timestamp, count) values" \
          "  (%s,%s,%s,%s);"
        cursor.execute(sql, [user_id, movie_id, browser_time, 1])
    db.commit()
    cursor.close()
    db.close()


def change_profile_pic(user_id, path):
    db = pymysql.connect(host="localhost", user="root", password="123456", database="moviehub", charset="utf8")
    cursor = db.cursor()
    sql = 'UPDATE app_user set profile_pic=%s where id=%s;'
    cursor.execute(sql, [path, user_id])
    db.commit()
    cursor.close()
    db.close()


def change_profile_info(username, email, gender, age, occupation, user_id):
    db = pymysql.connect(host="localhost", user="root", password="123456", database="moviehub", charset="utf8")
    cursor = db.cursor()
    sql = 'UPDATE app_user set username=%s, email=%s, gender=%s, age=%s, occupation=%s where id=%s;'
    cursor.execute(sql, [username, email, gender, age, occupation, user_id])
    db.commit()
    cursor.close()
    db.close()


def change_password(user_id, password):
    db = pymysql.connect(host="localhost", user="root", password="123456", database="moviehub", charset="utf8")
    cursor = db.cursor()
    sql = 'UPDATE app_user set password=%s where id=%s;'
    cursor.execute(sql, [password, user_id])
    db.commit()
    cursor.close()
    db.close()


def delete_browsing_history(user_id):
    db = pymysql.connect(host="localhost", user="root", password="123456", database="moviehub", charset="utf8")
    cursor = db.cursor()
    sql = 'DELETE FROM app_history where user_id_id=%s;'
    cursor.execute(sql, [user_id])
    db.commit()
    cursor.close()
    db.close()


def get_movie_review_user_list(movie_id):
    db = pymysql.connect(host="localhost", user="root", password="123456", database="moviehub", charset="utf8")
    cursor = db.cursor()
    sql = 'SELECT user_id_id, rating, timestamp FROM app_rating where movie_id_id="%s" ORDER by timestamp DESC ;' % movie_id
    cursor.execute(sql)
    movie_review_user_list = []
    rating_results = cursor.fetchall()
    for result in rating_results:
        user_id = result[0]
        rating = result[1]
        timestamp = result[2]
        user = models.User.objects.all().filter(id=user_id).first()
        info = {
            'rating': rating,
            'user': user,
            'timestamp': timestamp,
        }
        movie_review_user_list.append(info)
    return movie_review_user_list


def get_star_num(rating):
    rating = int(rating)
    light_star = ''
    grey_star = ''
    for i in range(0, rating):
        light_star += '1'
    for i in range(0, 5-rating):
        grey_star += '1'
    return light_star, grey_star


def combine_genres(genres_list):
    genres_text = ''
    for genres in genres_list:
        genres_text += genres
    return genres_text.rstrip('|')


def split_genres(genres_text):
    return str(genres_text).split('|')


def get_user_recommend_movie_list_by_genres(genres_list):
    q = Q(rating_count__gt=20)
    for genres in genres_list:
        q |= Q(genres__contains=genres)
    movie_recommend_list = models.Movie.objects.all().order_by('-popularity').filter(q)
    return movie_recommend_list[0:10]


def rating_movie(user_id, movie_id, rating):
    db = pymysql.connect(host="localhost", user="root", password="123456", database="moviehub", charset="utf8")
    rating_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    cursor = db.cursor()
    sql = "INSERT INTO app_rating (user_id_id, movie_id_id, timestamp, rating) values" \
          "  (%s,%s,%s,%s);"
    cursor.execute(sql, [user_id, movie_id, rating_time, rating])
    db.commit()
    sql = 'SELECT * FROM app_rating where movie_id_id="%s";' % movie_id
    cursor.execute(sql)
    rating_results = cursor.fetchall()
    rating_sum = 0
    for rating in rating_results:
        rating_sum += rating[1]
    try:
        rating_avg = round(rating_sum / len(rating_results), 1)
    except:
        rating_avg = 0
    sql = 'UPDATE app_movie set rating=%s where movie_id=%s; '
    cursor.execute(sql, [rating_avg, movie_id])
    sql = 'UPDATE app_movie set rating_count=%s where movie_id=%s; '
    cursor.execute(sql, [len(rating_results), movie_id])
    db.commit()
    cursor.close()
    db.close()


def change_rating_movie(user_id, movie_id, rating):
    db = pymysql.connect(host="localhost", user="root", password="123456", database="moviehub", charset="utf8")
    change_rating_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    cursor = db.cursor()
    sql = "UPDATE app_rating SET rating=%s, timestamp=%s WHERE user_id_id=%s and movie_id_id=%s;"
    cursor.execute(sql, [rating, change_rating_time, user_id, movie_id])
    db.commit()
    sql = 'SELECT * FROM app_rating where movie_id_id="%s";' % movie_id
    cursor.execute(sql)
    rating_results = cursor.fetchall()
    rating_sum = 0
    for rating in rating_results:
        rating_sum += rating[1]
    try:
        rating_avg = round(rating_sum / len(rating_results), 1)
    except:
        rating_avg = 0
    sql = 'UPDATE app_movie set rating=%s where movie_id=%s; '
    cursor.execute(sql, [rating_avg, movie_id])
    sql = 'UPDATE app_movie set rating_count=%s where movie_id=%s; '
    cursor.execute(sql, [len(rating_results), movie_id])
    db.commit()
    cursor.close()
    db.close()



def age_display(age):
    if age == '1':
        return 'Under 18'
    elif age == '18':
        return '18-24'
    elif age == '25':
        return '25-34'
    elif age == '35':
        return '35-44'
    elif age == '45':
        return '45-49'
    elif age == '50':
        return '50-55'
    else:
        return '56+'


def occupation_display(occ):
    if occ == '0':
        return '"other" or not specified'
    elif occ == '1':
        return 'academic/educator'
    elif occ == '2':
        return 'artist'
    elif occ == '3':
        return 'clerical/admin'
    elif occ == '4':
        return 'college/grad student'
    elif occ == '5':
        return 'customer service'
    elif occ == '6':
        return 'doctor/health care'
    elif occ == '7':
        return 'executive/managerial'
    elif occ == '8':
        return 'farmer'
    elif occ == '9':
        return 'homemaker'
    elif occ == '10':
        return 'K-12 student'
    elif occ == '11':
        return 'lawyer'
    elif occ == '12':
        return 'programmer'
    elif occ == '13':
        return 'retired'
    elif occ == '14':
        return 'sales/marketing'
    elif occ == '15':
        return 'scientist'
    elif occ == '16':
        return 'self-employed'
    elif occ == '17':
        return 'technician/engineer'
    elif occ == '18':
        return 'tradesman/craftsman'
    elif occ == '19':
        return 'unemployed'
    else:
        return 'writer'


def gender_display(gender):
    if gender == 'M':
        return 'Male'
    elif gender == 'F':
        return 'Female'
    else:
        return 'Secret'


if __name__ == '__main__':
    print('utilities')