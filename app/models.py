from django.db import models


class Movie(models.Model):
    movietitle = models.CharField(max_length=30)