from django.db import models


class Actor(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    actors = models.ManyToManyField(Actor, related_name="movies")

    @property
    def cz_title(self):
        title_obj = self.titles.filter(country__name="Czechia").first()
        return title_obj.name if title_obj else "Neznámý název"

    @property
    def en_title(self):
        title_obj = self.titles.filter(country__name="USA").first()
        return title_obj.name if title_obj else None

    def __str__(self):
            # Fallback string representation using the new relationship
            primary_title = self.titles.first()
            return primary_title.name if primary_title else f"Movie #{self.id}"


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
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
