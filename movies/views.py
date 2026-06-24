from django.db.models import F, Func, Q
from django.http import JsonResponse
from django.shortcuts import render
from unidecode import unidecode
from .models import Movie, Actor


class RemoveAccent(Func):
    function = "remove_accents"


def search_view(request):
    query = request.GET.get("q", "").strip()

    if len(query) < 2:
        return JsonResponse({"results": []})

    movies = []
    actors = []

    if query:
        clean_query = unidecode(query).lower()
    movies = (
        Movie.objects.annotate(
            clean_cz=RemoveAccent(F("cz_title")),
            clean_en=RemoveAccent(F("en_title")),
        )
        .filter(Q(clean_cz__contains=clean_query) | Q(clean_en__contains=clean_query))
        .distinct()
        .values("id", "cz_title", "en_title")
    )
    actors = (
        Actor.objects.annotate(normalized_name=RemoveAccent(F("name")))
        .filter(normalized_name__contains=clean_query)
        .distinct()
    )

    return JsonResponse(
        {
            "results": {
                "movies": list(movies.values("id", "cz_title", "en_title")),
                "actors": list(actors.values("id", "first_name", "last_name")),
            }
        }
    )
