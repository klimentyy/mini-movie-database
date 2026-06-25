# Mini Movie Database

A lightweight Django web application that provides a case-insensitive and diacritic-insensitive real-time search interface for the ČSFD Top 300 movies database.

## Prerequisites

* Python 3.13
* Pipenv

## Installation & Setup

1. **Install Dependencies:**
```bash
pipenv install

```


2. **Run Migrations:**
```bash
pipenv run python manage.py migrate

```


3. **Start the Development Server:**
```bash
pipenv run python manage.py runserver

```


Access the app at `http://127.0.0.1:8000/`.

---

## Database Seeding Options

### Option 1: Live Web Scraper

Extracts real-time information directly from ČSFD.

```bash
pipenv run python manage.py fetch_movies

```

* **Why use it:** Pulls the latest live records, localized titles, and associated casting lists.
* **Downside:** Slow, dependent on external network stability and target site structural shifts.

### Option 2: Static JSON Fixture

Seeds the schema instantly using bundled mock datasets.

```bash
pipenv run python manage.py seed_data

```

* **Why use it:** Fast, deterministic environment setup that runs offline. Ideal for localized verification.
* **Downside:** Contains only 20 best movies from the ČSFD database.

---

## Testing

Execute the comprehensive unit test suite.

```bash
pipenv run python manage.py test

```