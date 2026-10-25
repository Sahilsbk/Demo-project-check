"""External API clients, mocked — no network needed."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.clients import (
    fetch_github_repo,
    fetch_post,
    fetch_random_dog_image,
    greet,
    search_books,
)


def test_greet_uses_no_api():
    assert greet("Sahil") == "Hello, Sahil!"


def test_fetch_post_uses_requests():
    fake = MagicMock()
    fake.json.return_value = {"id": 1, "title": "hello"}
    with patch("src.clients.requests.get", return_value=fake) as mocked:
        assert fetch_post(1)["title"] == "hello"
    assert "jsonplaceholder.typicode.com" in mocked.call_args[0][0]


def test_fetch_github_repo_uses_httpx():
    fake = MagicMock()
    fake.json.return_value = {
        "full_name": "python/cpython",
        "description": "Python",
        "stargazers_count": 1,
        "language": "Python",
        "html_url": "https://github.com/python/cpython",
    }
    with patch("src.clients.httpx.get", return_value=fake) as mocked:
        assert fetch_github_repo("python", "cpython")["full_name"] == "python/cpython"
    assert "api.github.com/repos/python/cpython" in mocked.call_args[0][0]


def test_fetch_random_dog_image():
    fake = MagicMock()
    fake.json.return_value = {"message": "https://images.dog.ceo/dog.jpg", "status": "success"}
    with patch("src.clients.requests.get", return_value=fake) as mocked:
        assert fetch_random_dog_image().endswith(".jpg")
    assert "dog.ceo" in mocked.call_args[0][0]


def test_search_books():
    fake = MagicMock()
    fake.json.return_value = {"docs": [{"title": "Python 101", "author_name": ["A. Author"], "first_publish_year": 2020}]}
    with patch("src.clients.requests.get", return_value=fake) as mocked:
        books = search_books("python", limit=1)
    assert books[0]["title"] == "Python 101"
    assert "openlibrary.org" in mocked.call_args[0][0]
