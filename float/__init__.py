"""Float ? a working companion for car rental operators and fleet teams.

A small, self-contained assistant: one SQLite file, one stdlib HTTP server,
no build step. Runs on the rental desk or fleet manager's own laptop, on their own API key.
"""

from .config import APP_NAME, APP_TAGLINE, VERSION

__all__ = ["APP_NAME", "APP_TAGLINE", "VERSION"]
