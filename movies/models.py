from django.db import models

# Create your models here.
class Actor(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Movie(models.Model):
    title = models.CharField(max_length=255)
    actors = models.ManyToManyField(Actor, related_name="movies")

    def __str__(self):
        return self.title
