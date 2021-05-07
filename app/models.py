from django.db import models


class Movie(models.Model):
    movie_title = models.CharField(max_length=150)
    movie_id = models.CharField(max_length=30)
    imdb_id = models.CharField(max_length=30, unique=True)
    genres = models.CharField(max_length=100)
    poster_url = models.CharField(max_length=200, null=True)
    summary = models.CharField(max_length=500, null=True)
    director = models.CharField(max_length=100, null=True)
    stars = models.CharField(max_length=100, null=True)
    release_date = models.CharField(max_length=30, null=True)
    time = models.CharField(max_length=30, null=True)
    rating = models.IntegerField(null=True)


class User(models.Model):
    username = models.CharField(max_length=30, unique=True)
    user_age = models.IntegerField()
    gender = models.CharField(max_length=10)
    occupation = models.CharField(max_length=30, null=True)
    profile_pic = models.CharField(max_length=200, null=True)
    password = models.CharField(max_length=30, null=True)


class Rating(models.Model):
    rating = models.IntegerField()
    user = models.ForeignKey(User, related_name='rating_user', on_delete=models.CASCADE, default='')
    movie = models.ForeignKey(Movie, related_name='rating_movie', on_delete=models.CASCADE, default='')


class Tag(models.Model):
    tag = models.CharField(max_length=30)
    user = models.ForeignKey(User, related_name='tag_user', on_delete=models.CASCADE, default='')
    movie = models.ForeignKey(Movie, related_name='tag_movie', on_delete=models.CASCADE, default='')