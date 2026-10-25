"""Clients for real public APIs. No keys needed for any of them.

These calls are deliberately UNAFFECTED by the Payments v2 changelog,
so a correct API Guardian report detects them as API usages but reports
no breaking change for them.

* JSONPlaceholder — requests
* GitHub REST API — httpx
* Dog CEO API — requests
* Open Library API — requests
"""

from __future__ import annotations

import contextlib
import os

import httpx
import requests


def greet(name: str) -> str:
    """Plain helper with no API call at all — another true negative."""
    return f"Hello, {name}!"


def fetch_post(post_id: int = 1) -> dict:
    """Fetch one public post from JSONPlaceholder."""
    response = requests.get(
        f"https://jsonplaceholder.typicode.com/posts/{post_id}", timeout=10
    )
    response.raise_for_status()
    return response.json()


def fetch_github_repo(owner: str = "python", repo: str = "cpython") -> dict:
    """Fetch public repo metadata from the GitHub REST API."""
    with _clean_no_proxy():
        response = httpx.get(
            f"https://api.github.com/repos/{owner}/{repo}",
            headers={"Accept": "application/vnd.github+json"},
            timeout=10,
        )
    response.raise_for_status()
    data = response.json()
    return {
        "full_name": data.get("full_name"),
        "description": data.get("description"),
        "stars": data.get("stargazers_count"),
        "language": data.get("language"),
        "html_url": data.get("html_url"),
    }


def fetch_random_dog_image() -> str:
    """Fetch a random dog image URL from the Dog CEO API."""
    response = requests.get("https://dog.ceo/api/breeds/image/random", timeout=10)
    response.raise_for_status()
    return response.json()["message"]


def search_books(query: str = "python programming", limit: int = 1) -> list[dict]:
    """Search books via the Open Library API."""
    response = requests.get(
        "https://openlibrary.org/search.json",
        params={"q": query, "limit": limit},
        timeout=10,
    )
    response.raise_for_status()
    books = []
    for doc in response.json().get("docs", [])[:limit]:
        books.append(
            {
                "title": doc.get("title"),
                "author": (doc.get("author_name") or [None])[0],
                "first_published": doc.get("first_publish_year"),
            }
        )
    return books


@contextlib.contextmanager
def _clean_no_proxy():
    """Strip bracketed IPv6 entries from NO_PROXY for httpx.

    Some httpx versions mis-parse a NO_PROXY value like ``[::1]`` and
    fail with ``InvalidURL: Invalid port: ':1]'``. Bracket-free entries
    parse fine, and the proxy itself is left untouched.
    """
    saved = {}
    for key in ("NO_PROXY", "no_proxy"):
        value = os.environ.get(key)
        if value and "[" in value:
            saved[key] = value
            os.environ[key] = ",".join(
                part for part in value.split(",") if "[" not in part
            )
    try:
        yield
    finally:
        for key, value in saved.items():
            os.environ[key] = value
