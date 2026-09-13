# eventor-mcp

An [MCP](https://modelcontextprotocol.io) server that exposes the Norwegian/Swedish
orienteering federation's [Eventor](https://eventor.orientering.no) REST API as
typed tools, so an MCP client (e.g. Claude) can query events, clubs, entries and
competitors -- and optionally publish start/result lists -- without ever seeing
your API key or Eventor password.

## Why this exists

Eventor's own API documentation (the ["Hämta data via API"
guide](https://eventor.orientering.no/Documents/Guide_Eventor_-_Hamta_data_via_API.pdf))
only documents authentication and one example call. The actual endpoint shapes
used here were taken from a real, working integration (`ttime.pl`) against this
API.

## Security model

- Credentials (`EVENTOR_API_KEY`, `EVENTOR_USERNAME`, `EVENTOR_PASSWORD`) are
  read **only** from environment variables, by the server process itself.
- They are **never** included in any tool result, logged, or written to disk
  by this project.
- `.env` is git-ignored -- only `.env.example` (with empty values) is committed.
- An MCP client (including an LLM) only ever calls tools like
  `list_events(from_date, to_date)`; it never handles the raw key/password.

**If you ever paste your API key into a chat, file, or issue, treat it as
compromised and regenerate it in Eventor under Klubben -> Klubbinnstillinger.**

## Setup

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -e ".[dev]"
cp .env.example .env   # then fill in your own values in .env
```

Two separate credential types are used by Eventor's API:

| Credential | Used for | Where to get it |
|---|---|---|
| `EVENTOR_API_KEY` | `list_events`, `list_organisations` | Eventor -> Klubben -> Klubbinnstillinger (club admin only) |
| `EVENTOR_USERNAME` / `EVENTOR_PASSWORD` | `get_event_classes`, `get_event_entries`, `get_entry_changes`, `get_competitors`, `import_startlist`, `import_resultlist` | Your personal Eventor login |

## Running

```bash
python -m eventor_mcp.server
```

This starts the server on stdio, ready for an MCP client to connect.

## Registering with Claude Code

```bash
claude mcp add eventor -- python -m eventor_mcp.server
```

Run this from an activated virtualenv (or use the full path to the venv's
`python`), and make sure `EVENTOR_API_KEY` etc. are set in the environment
Claude Code itself runs in -- not hardcoded anywhere in this repo.

## Tools

| Tool | Auth | Notes |
|---|---|---|
| `list_events(from_date, to_date, organisation_ids=None)` | API key | Dates as `YYYY-MM-DD` |
| `list_organisations()` | API key | All clubs/districts/federations |
| `get_event_classes(event_id)` | Username/password | Classes for one event |
| `get_event_entries(event_id)` | Username/password | Full entries: name, class, club, control card |
| `get_entry_changes(event_id)` | Username/password | Just entry/modify timestamps |
| `get_competitors(organisation_ids)` | Username/password | Registered club members |
| `import_startlist(iof_xml)` | Username/password | **Writes to Eventor** -- publishes a start list |
| `import_resultlist(iof_xml)` | Username/password | **Writes to Eventor** -- publishes results |

`import_startlist` and `import_resultlist` expect a complete
[IOF XML 3.0](https://eventor.orientering.no/api/schema) document as a string;
this project does not (yet) build that XML for you.

## Testing

```bash
pytest
```

## Limitations / TODO

- No XML-building helpers for `import_startlist`/`import_resultlist` yet --
  callers must supply valid IOF XML 3.0.
- No caching, even though Eventor's usage terms ask integrations to cache
  frequently-fetched data (e.g. club member lists) client-side.
- Only tested against the Norwegian instance
  (`eventor.orientering.no`); the Swedish instance
  (`eventor.orientering.se`) uses the same API shape via `EVENTOR_BASE_URL`.
