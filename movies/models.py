from django.db import models


class Actor(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    cz_title = models.CharField(max_length=255)
    en_title = models.CharField(max_length=255, null=True, blank=True)
    actors = models.ManyToManyField(Actor, related_name="movies")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cz_title", "en_title"], name="unique_movie_titles"
            )
        ]

    def __str__(self):
        return self.cz_title


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Titles(models.Model):
    movie = models.ForeignKey(Movie, related_name="titles", on_delete=models.CASCADE)
    country = models.ForeignKey(
        Country, related_name="titles", on_delete=models.PROTECT
    )
    name = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["movie", "country", "name"],
                name="unique_movie_title_per_country",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.country.name})"
