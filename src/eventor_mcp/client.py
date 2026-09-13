"""Thin HTTP client for the Eventor REST API.

Mirrors the two authentication styles Eventor's API actually uses in
practice (confirmed against a real-world integration, ttime.pl):

- ``ApiKey`` header (a club-specific key) for most read endpoints
  (``events``, ``export/organisations``).
- ``Username``/``Password`` headers (a personal Eventor login -- not HTTP
  Basic Auth, just plain custom headers) for endpoints that expose
  competitor-level data or that write data (``export/classes``,
  ``export/entries``, ``export/competitors``, ``import/startlist``,
  ``import/resultlist``).
"""

from __future__ import annotations

import httpx
import xmltodict

from .config import EventorConfig


class EventorApiError(RuntimeError):
    def __init__(self, status_code: int, message: str, url: str):
        super().__init__(f"Eventor API error {status_code} for {url}: {message}")
        self.status_code = status_code
        self.url = url


class EventorClient:
    def __init__(self, config: EventorConfig | None = None, timeout: float = 30.0):
        self.config = config or EventorConfig.from_env()
        self.timeout = timeout

    def _headers(self, use_credentials: bool) -> dict[str, str]:
        if use_credentials:
            username, password = self.config.require_credentials()
            return {"Username": username, "Password": password}
        return {"ApiKey": self.config.require_api_key()}

    def get(
        self,
        path: str,
        params: dict[str, object] | None = None,
        use_credentials: bool = False,
    ) -> dict:
        """GET an endpoint and parse the IOF/Eventor XML response into a dict."""
        url = self.config.base_url.rstrip("/") + "/" + path.lstrip("/")
        headers = self._headers(use_credentials)
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(url, params=params, headers=headers)
        if resp.status_code != 200:
            raise EventorApiError(resp.status_code, resp.text[:500], url)
        return xmltodict.parse(resp.text)

    def post_xml(self, path: str, xml_body: str, use_credentials: bool = True) -> str:
        """POST a raw XML body (e.g. an IOF XML 3.0 document) to a write endpoint."""
        url = self.config.base_url.rstrip("/") + "/" + path.lstrip("/")
        headers = self._headers(use_credentials)
        headers["Content-Type"] = "application/xml"
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, content=xml_body.encode("utf-8"), headers=headers)
        if resp.status_code not in (200, 201, 204):
            raise EventorApiError(resp.status_code, resp.text[:500], url)
        return resp.text
