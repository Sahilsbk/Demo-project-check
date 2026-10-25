"""Build a plain-text digest from the API clients. No web framework."""

from __future__ import annotations

from src.checkout import checkout
from src.clients import (
    fetch_github_repo,
    fetch_post,
    fetch_random_dog_image,
    greet,
    search_books,
)


def build_digest(name: str = "Sahil") -> str:
    lines = [greet(name), ""]
    post = fetch_post(1)
    lines.append(f"Post of the day: {post.get('title')}")
    repo = fetch_github_repo("python", "cpython")
    lines.append(f"GitHub repo: {repo['full_name']} ({repo['stars']} stars)")
    lines.append(f"Random dog image: {fetch_random_dog_image()}")
    books = search_books("python programming", limit=1)
    if books:
        lines.append(f"Book pick: {books[0]['title']} by {books[0]['author']}")
    return "\n".join(lines)


def demo_checkout(amount_dollars: float) -> dict:
    # Deliberately the v1 call path — this is what Guardian must flag.
    return checkout(amount_dollars=amount_dollars)
