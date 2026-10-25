#!/usr/bin/env python3
"""Random API project — command-line entry point. No FastAPI, no server.

Usage:
    python main.py                  # print the daily digest
    python main.py --checkout 19.99 # also run a demo checkout
    python main.py --name Sahil
"""

from __future__ import annotations

import argparse
import sys

from src.digest import build_digest, demo_checkout


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Random API project — daily digest")
    parser.add_argument("--name", default="Sahil")
    parser.add_argument("--checkout", type=float, default=None, help="Demo checkout amount in dollars")
    args = parser.parse_args(argv)

    try:
        print(build_digest(args.name))
    except Exception as exc:  # public APIs can be offline; say so, don't crash silently
        print(f"Digest failed (are you offline?): {exc}", file=sys.stderr)
        return 1

    if args.checkout is not None:
        print()
        print("Checkout:", demo_checkout(args.checkout))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
