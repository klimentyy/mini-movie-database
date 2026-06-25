import os
import json
from django.apps import apps
from django.core.management.base import BaseCommand
from movies.models import Actor, Movie


class Command(BaseCommand):
    help = "Seeds the database using a local static JSON data fixture."

    def handle(self, *args, **options):
        app_config = apps.get_app_config("movies")
        json_file_path = os.path.join(
            app_config.path, "management", "data", "movies_data.json"
        )

        if not os.path.exists(json_file_path):
            self.stdout.write(
                self.style.ERROR(f"Data file not found at: {json_file_path}")
            )
            return

        self.stdout.write(self.style.WARNING(f"Loading data from {json_file_path}..."))

        with open(json_file_path, "r", encoding="utf-8") as f:
            movie_dataset = json.load(f)

        for index, movie_data in enumerate(movie_dataset, start=1):
            cz_title = movie_data.get("cz_title")
            en_title = movie_data.get("en_title")
            actors_names = movie_data.get("actors", [])

            if not cz_title:
                continue

            movie_obj, _ = Movie.objects.update_or_create(
                cz_title=cz_title, defaults={"en_title": en_title}
            )

            actor_objects = [
                Actor.objects.get_or_create(name=name)[0] for name in actors_names
            ]
            movie_obj.actors.set(actor_objects)

            self.stdout.write(
                self.style.SUCCESS(
                    f"[{index}/{len(movie_dataset)}] Imported: {cz_title}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS("Database population successfully completed!")
        )
