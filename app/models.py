from django.db import models
from django.utils import timezone


class Movie(models.Model):
    movie_title = models.CharField(max_length=150)
    movie_id = models.CharField(max_length=30, unique=True)
    imdb_id = models.CharField(max_length=30, unique=True)
    genres = models.CharField(max_length=100)
    poster_url = models.CharField(max_length=200, null=True)
    summary = models.CharField(max_length=500, null=True)
    director = models.CharField(max_length=100, null=True)
    stars = models.CharField(max_length=100, null=True)
    release_date = models.CharField(max_length=30, null=True)
    time = models.CharField(max_length=30, null=True)
    rating = models.FloatField(null=True)
    rating_count = models.IntegerField(null=True, default=0)
    popularity = models.FloatField(null=True, default=0)


class User(models.Model):
    username = models.CharField(max_length=30, unique=True)
    age = models.IntegerField()
    gender = models.CharField(max_length=9)
    occupation = models.CharField(max_length=30, null=True)
    profile_pic = models.CharField(max_length=200, null=True)
    password = models.CharField(max_length=30, null=True)
    email = models.CharField(max_length=100, unique=True, null=True)
    register_time = models.DateTimeField(default=timezone.now)


class Rating(models.Model):
    rating = models.IntegerField()
    user_id = models.ForeignKey(User, related_name='rating_user', on_delete=models.CASCADE, default='')
    movie_id = models.ForeignKey(Movie, to_field="movie_id", related_name='rating_movie', on_delete=models.CASCADE, default='')
    timestamp = models.DateTimeField(default=timezone.now)


class Tag(models.Model):
    tag = models.CharField(max_length=100)
    user_id = models.ForeignKey(User, related_name='tag_user', on_delete=models.CASCADE, default='')
    movie_id = models.ForeignKey(Movie, to_field="movie_id", related_name='tag_movie', on_delete=models.CASCADE, default='')
    timestamp = models.DateTimeField(default=timezone.now)


class Like(models.Model):
    user_id = models.ForeignKey(User, related_name='like_user', on_delete=models.CASCADE, default='')
    movie_id = models.ForeignKey(Movie, to_field="movie_id", related_name='like_movie', on_delete=models.CASCADE, default='')
    timestamp = models.DateTimeField(default=timezone.now)


class History(models.Model):
    user_id = models.ForeignKey(User, related_name='history_user', on_delete=models.CASCADE, default='')
    movie_id = models.ForeignKey(Movie, to_field="movie_id", related_name='history_movie', on_delete=models.CASCADE, default='')
    timestamp = models.DateTimeField(default=timezone.now)
    count = models.IntegerField(default=1)