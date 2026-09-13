"""Configuration loaded from environment variables.

Credentials are read directly from the process environment and are never
written to disk, logged, or echoed back through any tool response. This is
intentional: an MCP client (including an LLM agent) only ever sees the
structured results of API calls, never the ``EVENTOR_API_KEY`` or
``EVENTOR_PASSWORD`` values themselves.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_BASE_URL = "https://eventor.orientering.no/api/"


class ConfigError(RuntimeError):
    """Raised when required credentials are missing for a given call."""


@dataclass
class EventorConfig:
    base_url: str
    api_key: str | None
    username: str | None
    password: str | None

    @classmethod
    def from_env(cls) -> "EventorConfig":
        return cls(
            base_url=os.environ.get("EVENTOR_BASE_URL", DEFAULT_BASE_URL),
            api_key=os.environ.get("EVENTOR_API_KEY") or None,
            username=os.environ.get("EVENTOR_USERNAME") or None,
            password=os.environ.get("EVENTOR_PASSWORD") or None,
        )

    def require_api_key(self) -> str:
        if not self.api_key:
            raise ConfigError(
                "EVENTOR_API_KEY is not set. Generate a club API key in Eventor "
                "under Klubben -> Klubbinnstillinger and set it as an "
                "environment variable (see .env.example)."
            )
        return self.api_key

    def require_credentials(self) -> tuple[str, str]:
        if not self.username or not self.password:
            raise ConfigError(
                "EVENTOR_USERNAME and EVENTOR_PASSWORD are not set. This "
                "endpoint requires a personal Eventor login, not the club "
                "API key (see .env.example)."
            )
        return self.username, self.password
