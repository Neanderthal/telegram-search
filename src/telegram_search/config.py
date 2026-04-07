"""Configuration from environment variables."""

from __future__ import annotations

import os


def _require_env(name: str) -> str:
    """Return the value of a required environment variable or raise."""
    value = os.environ.get(name)
    if not value:
        raise ValueError(
            f"Required environment variable {name} is not set. "
            f"Export it before running the server."
        )
    return value


API_ID: int = int(_require_env("TELEGRAM_API_ID"))
API_HASH: str = _require_env("TELEGRAM_API_HASH")
PHONE: str = _require_env("TELEGRAM_PHONE")
SESSION_PATH: str = os.path.expanduser(
    os.environ.get(
        "TELEGRAM_SESSION_PATH",
        os.path.join("~", ".telegram-search", "session"),
    )
)
