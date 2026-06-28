from django.db.models import F, Func, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from unidecode import unidecode
from .models import Movie, Actor


class RemoveAccent(Func):
    function = "remove_accents"


def search_page_view(request):
    return render(request, "movies/search.html")


def movie_detail_view(request, pk):
    movie = get_object_or_404(Movie.objects.prefetch_related("actors"), pk=pk)
    return render(request, "movies/movie_detail.html", {"movie": movie})


def actor_detail_view(request, pk):
    actor = get_object_or_404(Actor.objects.prefetch_related("movies"), pk=pk)
    return render(request, "movies/actor_detail.html", {"actor": actor})


def search_api_view(request):
    query = request.GET.get("q", "").strip()

    if len(query) < 2:
        return JsonResponse({"results": {"movies": [], "actors": []}})

    clean_query = unidecode(query).lower()
    movies = (
        Movie.objects.annotate(
            clean_title=RemoveAccent(F("titles__name"))
        )
        .filter(clean_title__icontains=clean_query)
        .distinct()
    )

    serialized_movies = []
    for movie in movies:
        serialized_movies.append({
            "id": movie.id,
            "cz_title": movie.cz_title,
            "en_title": movie.en_title
        })
    
    actors = (
        Actor.objects.annotate(normalized_name=RemoveAccent(F("name")))
        .filter(normalized_name__icontains=clean_query)
        .distinct()
        .values("id", "name")
    )

    return JsonResponse(
        {
            "results": {
                "movies": serialized_movies,
                "actors": list(actors),
            }
        }
    )
