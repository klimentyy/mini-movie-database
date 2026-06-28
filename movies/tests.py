from django.test import TestCase, Client
from django.urls import reverse
from .models import Movie, Actor, Title, Country


class MovieSearchTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.czechia, _ = Country.objects.get_or_create(name="Czechia")
        self.usa, _ = Country.objects.get_or_create(name="USA")

        # The rest of your setUp code remains exactly the same...
        self.actor_1 = Actor.objects.create(name="Karel Němec")
        self.actor_2 = Actor.objects.create(name="Keanu Reeves")

        # 3. Create the base Movie rows
        self.movie_1 = Movie.objects.create()
        self.movie_2 = Movie.objects.create()

        # 4. Attach titles via the new relational table
        Title.objects.create(movie=self.movie_1, country=self.czechia, name="Pelíšky")
        
        Title.objects.create(movie=self.movie_2, country=self.czechia, name="Matrix")
        Title.objects.create(movie=self.movie_2, country=self.usa, name="The Matrix")

        # 5. Link relationships
        self.movie_2.actors.add(self.actor_2)

    def test_database_relations_work(self):
        """Verifies that the Many-to-Many field maps data correctly."""
        self.assertEqual(self.movie_2.actors.count(), 1)
        self.assertIn(self.actor_2, self.movie_2.actors.all())

    def test_search_page_loads_html(self):
        """Verifies that hitting the root URL renders the standard HTML page."""
        url = reverse("search")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "movies/search.html")

    def test_accent_insensitive_search_success(self):
        """Verifies SQLite REMOVE_ACCENTS function and the API endpoint ignore case and diacritics."""
        url = reverse("search_api")

        # Search using lowercase and NO accents for "Němec"
        response = self.client.get(url, {"q": "nem"})
        self.assertEqual(response.status_code, 200)

        actors_results = response.json()["results"]["actors"]
        self.assertEqual(len(actors_results), 1)
        self.assertEqual(actors_results[0]["name"], "Karel Němec")

        # Search using lowercase and NO accents for "Matrix"
        response_matrix = self.client.get(url, {"q": "rix"})
        movies_results = response_matrix.json()["results"]["movies"]
        self.assertEqual(len(movies_results), 1)
        self.assertEqual(movies_results[0]["cz_title"], "Matrix")

    def test_search_guard_clause(self):
        """Ensures queries with fewer than 2 characters return empty datasets."""
        url = reverse("search_api")
        response = self.client.get(url, {"q": "m"})

        data = response.json()
        self.assertEqual(data["results"]["movies"], [])
        self.assertEqual(data["results"]["actors"], [])

    def test_missing_english_title_does_not_crash_database(self):
        """Verifies that running our custom SQL function over null/None values functions smoothly."""
        url = reverse("search_api")
        response = self.client.get(url, {"q": "pelisky"})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["results"]["movies"][0]["cz_title"], "Pelíšky")

    def test_whitespace_tolerance_handling(self):
        """Ensures sloppy user whitespace inputs are cleanly handled without shifting results."""
        url = reverse("search_api")
        response = self.client.get(url, {"q": "   matrix   "})

        data = response.json()
        self.assertEqual(len(data["results"]["movies"]), 1)

    def test_simultaneous_movie_and_actor_matching(self):
        """Ensures queries matching both structural types populate both response nodes correctly."""
        Actor.objects.create(name="Kim Matrix")

        url = reverse("search_api")
        response = self.client.get(url, {"q": "Matrix"})
        data = response.json()

        self.assertEqual(len(data["results"]["movies"]), 1)
        self.assertEqual(len(data["results"]["actors"]), 1)

    def test_invalid_details_raise_404_errors(self):
        """Verifies that missing object primary keys trigger proper 404 responses."""
        movie_url = reverse("movie_detail", kwargs={"pk": 99999})
        actor_url = reverse("actor_detail", kwargs={"pk": 99999})

        self.assertEqual(self.client.get(movie_url).status_code, 404)
        self.assertEqual(self.client.get(actor_url).status_code, 404)

    def test_blank_or_whitespace_only_query_returns_empty(self):
        """Ensures that query inputs consisting solely of spaces do not execute DB queries."""
        url = reverse("search_api")
        response = self.client.get(url, {"q": "     "})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["results"]["movies"], [])
        self.assertEqual(data["results"]["actors"], [])

    def test_special_characters_handling(self):
        """Ensures query matching handles special character separators or numbers safely."""
        url = reverse("search_api")
        response = self.client.get(url, {"q": "Matrix 2!"})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["results"]["movies"], [])