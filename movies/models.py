from django.db import models

# Create your models here.
class Actor(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Movie(models.Model):
    cz_title = models.CharField(max_length=255)
    original_title = models.CharField(max_length=255, null=True, blank=True)
    actors = models.ManyToManyField(Actor, related_name="movies")

    def __str__(self):
        return self.title
