import time
from typing import Dict, Optional

from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand

from movies.models import Actor, Movie
from httpx import Client

# Unfortunately, CSFD has bot protection. So this script is rather theoretical and may not work in practice.

class Command(BaseCommand):
    help = "Scrapes the top 300 movies from CSDF and fills the local database."

    BASE_URL = "https://www.csfd.cz"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    }

    def handle(self, *args, **options):

        self.stdout.write(self.style.NOTICE("Started paginated CSFD data extraction."))

        # Set up an HTTP client to bypass bot protection
        with Client(headers=self.HEADERS, http2=True, timeout=15.0) as client:
            movie_links = []
            offsets = [1, 100, 200]

            # Harvest the index pages to get movie links
            for offset in offsets:
                url = f"{self.BASE_URL}/zebricky/filmy/nejlepsi/?from={offset}"
                self.stdout.write(f"Harvesting index metadata from: {url}")

                html_content = self._fetch_html(client, url)
                if html_content:
                    page_targets = self._parse_index_page(html_content)
                    movie_links.extend(page_targets)

                time.sleep(1.0)  # Throttling index pages

            self.stdout.write(
                self.style.NOTICE(
                    f"Finished extracting movie links. Total: {len(movie_links)}"
                )
            )

            # Process the movie details
            for index, link in enumerate(movie_links, start=1):
                url = self.BASE_URL + link
                html_content = self._fetch_html(client, url)
                if not html_content:
                    self.stdout.write(self.style.WARNING(f"Failed to fetch movie details for: {url}"))
                    continue
                
                movie_data = self._parse_movie_page(html_content)
                self._save_to_database(movie_data)

                self.stdout.write(self.style.NOTICE(f"Processed movie {index}/{len(movie_links)}: {movie_data.get('cz_title')}"))
                time.sleep(1.2)  # Throttling movie pages
            
            self.stdout.write(self.style.SUCCESS("Completed CSFD data extraction and database population."))

                

    def _fetch_html(self, client: Client, url: str) -> Optional[str]:
        """Safely performs an HTTP GET request"""

        try:
            response = client.get(url)
            if response.status_code == 200:
                return response.text
            self.stdout.write(
                self.style.ERROR(f"Failed to fetch {url}. Status code: {response.status_code}")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to fetch {url}: {e}"))
        return None

    def _parse_index_page(self, html_content: str) -> list[str]:
        """Parses a single leaderboard page. Extracts a movie url"""

        soup = BeautifulSoup(html_content, "html.parser")

        title_tags = soup.find_all("a", class_="film-title-name")

        return [tag["href"] for tag in title_tags if "href" in tag.attrs]

    def _parse_movie_page(self, html_content: str) -> Dict[str, Optional[str]]:
        """Orchestrates the parsing of a single movie page."""

        soup = BeautifulSoup(html_content, "html.parser")

        data = {
            "cz_title": self.__extract_cz_title(soup),
            "en_title": self.__extract_en_title(soup),
            "actors": self.__extract_actors(soup),
        }
        return data

    def __extract_cz_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extracts the Czech title from the movie page."""
        title_tag = soup.find("h1", class_="film-header-name")
        if title_tag:
            return title_tag.get_text(strip=True)
        return None

    def __extract_en_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extracts the English title from the movie page."""
        usa_flag = soup.find("img", attrs={"title": "USA"})
        if not usa_flag:
            return None

        li_target = usa_flag.find_parent("li")
        if not li_target:
            return None

        text_segments = li_target.find_all(text=True, recursive=False)
        title = "".join(text_segments).strip()
        return title if title else None

    def __extract_actors(self, soup: BeautifulSoup) -> list[str]:
        """Collects clean strings representing actor identities."""
        actors_names = []

        creators_div = soup.find_all("div", class_="creators")

        for div in creators_div:
            header = div.find("h4")

            if header and "Hrají" in header.get_text(strip=True):
                actor_links = div.find_all("a")
                for link in actor_links:
                    name = link.get_text(strip=True)
                    if name and name != "více":
                        actors_names.append(name)
        return actors_names
    
    def _save_to_database(self, movie_data: Dict[str, Optional[str]]) -> None:
        """Saves the parsed movie data to the database."""
        cz_title = movie_data.get("cz_title")
        en_title = movie_data.get("en_title")
        actors_names = movie_data.get("actors", [])

        if not cz_title:
            self.stdout.write(self.style.WARNING("Skipping movie with no Czech title."))
            return

        # Create or get the Movie instance
        movie, _ = Movie.objects.get_or_create(
            cz_title=cz_title,
            defaults={"en_title": en_title}
        )

        # Process actors
        for actor_name in actors_names:
            actor, _ = Actor.objects.get_or_create(name=actor_name)
            movie.actors.add(actor)

        self.stdout.write(
            self.style.SUCCESS(f"Saved movie: {movie} with {len(actors_names)} actors.")
        )
        