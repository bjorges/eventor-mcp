"""MCP server exposing the Eventor REST API as typed tools.

Run with: python -m eventor_mcp.server  (stdio transport)

Credentials (EVENTOR_API_KEY / EVENTOR_USERNAME / EVENTOR_PASSWORD) are read
from the process environment by EventorConfig and used only inside this
process to build HTTP headers. They are never included in any tool result,
so an MCP client (including an LLM) never sees the raw secret values.
"""

from __future__ import annotations

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from . import parsers
from .client import EventorApiError, EventorClient
from .config import ConfigError

# Loads .env for local development only, if present. In production use, an
# MCP client (e.g. Claude Code) should set these in the environment it
# launches this server with instead.
load_dotenv()

mcp = FastMCP("eventor")


def _client() -> EventorClient:
    return EventorClient()


@mcp.tool()
def list_events(from_date: str, to_date: str, organisation_ids: str | None = None) -> list[dict]:
    """List events (competitions/activities) from Eventor within a date range.

    Args:
        from_date: Start date, format YYYY-MM-DD.
        to_date: End date, format YYYY-MM-DD.
        organisation_ids: Optional comma-separated Eventor organisation id(s)
            to filter by (a club or district). Omit for all events in range.

    Requires EVENTOR_API_KEY (a club API key from Eventor -> Klubben ->
    Klubbinnstillinger).
    """
    params: dict[str, object] = {"fromDate": from_date, "toDate": to_date}
    if organisation_ids:
        params["organisationIds"] = organisation_ids
    doc = _client().get("events", params=params)
    return parsers.parse_events(doc)


@mcp.tool()
def list_organisations() -> list[dict]:
    """List all organisations (clubs, districts, federations) known to Eventor.

    Requires EVENTOR_API_KEY.
    """
    doc = _client().get("export/organisations", params={"version": "3.0"})
    return parsers.parse_organisations(doc)


@mcp.tool()
def get_event_classes(event_id: int) -> list[dict]:
    """Get the competition classes defined for a specific event.

    Requires EVENTOR_USERNAME and EVENTOR_PASSWORD (a personal Eventor
    login) -- this endpoint does not accept the club API key.
    """
    doc = _client().get(
        "export/classes",
        params={"eventId": event_id, "version": "3.0"},
        use_credentials=True,
    )
    return parsers.parse_classes(doc)


@mcp.tool()
def get_event_entries(event_id: int) -> list[dict]:
    """Get all entries for a specific event: competitor name, class, club and
    control card number.

    Requires EVENTOR_USERNAME and EVENTOR_PASSWORD.
    """
    doc = _client().get(
        "export/entries",
        params={"eventId": event_id, "version": "3.0"},
        use_credentials=True,
    )
    return parsers.parse_entries(doc)


@mcp.tool()
def get_entry_changes(event_id: int) -> list[dict]:
    """Get entry/modification timestamps for a specific event (who entered or
    changed their entry, and when), without full competitor details.

    Requires EVENTOR_USERNAME and EVENTOR_PASSWORD.
    """
    doc = _client().get(
        "export/entries",
        params={"eventId": event_id},
        use_credentials=True,
    )
    return parsers.parse_entry_changes(doc)


@mcp.tool()
def get_competitors(organisation_ids: str) -> list[dict]:
    """Get all registered competitors for one or more clubs.

    Args:
        organisation_ids: Comma-separated Eventor organisation id(s).

    Requires EVENTOR_USERNAME and EVENTOR_PASSWORD.
    """
    doc = _client().get(
        "export/competitors",
        params={"organisationIds": organisation_ids, "version": "3.0"},
        use_credentials=True,
    )
    return parsers.parse_competitors(doc)


@mcp.tool()
def import_startlist(iof_xml: str) -> str:
    """Upload a start list to Eventor.

    THIS WRITES DATA: it changes what is published in Eventor. Only call
    this after the user has explicitly confirmed they want to publish this
    exact start list -- treat it like any other irreversible "publish"
    action, not a routine read.

    Args:
        iof_xml: A complete IOF XML 3.0 StartList document as a string.

    Requires EVENTOR_USERNAME and EVENTOR_PASSWORD.
    """
    return _client().post_xml("import/startlist", iof_xml, use_credentials=True)


@mcp.tool()
def import_resultlist(iof_xml: str) -> str:
    """Upload a result list to Eventor.

    THIS WRITES DATA: it publishes results. Only call this after the user
    has explicitly confirmed they want to publish these exact results.

    Args:
        iof_xml: A complete IOF XML 3.0 ResultList document as a string.

    Requires EVENTOR_USERNAME and EVENTOR_PASSWORD.
    """
    return _client().post_xml("import/resultlist", iof_xml, use_credentials=True)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
