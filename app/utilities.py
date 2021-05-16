import re
import pymysql
import time
from . import models


def check_email(email):
    c = re.compile(r'^\w+@(\w+\.)+(com|cn|net)$')
    s = c.search(email)
    if s:
        return True
    else:
        return False


def create_user(username, password, email, gender, age, occupation):
    register_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    db = pymysql.connect(host="localhost", user="root", password="123456", database="moviehub", charset="utf8")
    cursor = db.cursor()
    sql = "INSERT INTO app_user (username,age,gender,occupation,profile_pic,password,register_time,email) values" \
          "  (%s,%s,%s,%s,%s,%s,%s,%s);"
    cursor.execute(sql,
                   [username, age, gender, occupation, None, password, register_time, email])
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


if __name__ == '__main__':
    print('utilities')