# Contributing to eventor-mcp

Thanks for looking at this. It's a small project, so this doc is short on
purpose.

## Setup

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
git clone https://github.com/bjorges/eventor-mcp.git
cd eventor-mcp
uv sync --extra dev
cp .env.example .env   # fill in your own credentials, see README
```

Run the test suite:

```bash
uv run pytest
```

## Before you commit: never let credentials in

`.env` is git-ignored on purpose. Before every commit, especially your
first one:

```bash
git status --porcelain   # .env must not appear here
```

If you ever paste an API key, password, or token into a file, a commit
message, an issue, or a chat with an AI assistant, treat it as compromised
and rotate it in Eventor (Klubben -> Klubbinnstillinger for the club API
key; your account password for personal login) even if you catch it before
pushing.

## Project layout

```
src/eventor_mcp/
  config.py    # reads credentials from environment variables only
  client.py    # HTTP calls to Eventor's REST API (both auth styles)
  parsers.py   # turns Eventor's XML into plain dicts/lists
  server.py    # MCP tool definitions (the public surface)
tests/
  test_parsers.py
```

## Adding a new tool

1. If it needs a new Eventor endpoint, add a parser function in
   `parsers.py`. Write a unit test against a **minimal real XML sample**
   first if at all possible -- Eventor's XML shapes have surprised us more
   than once (see "A note on trusting the docs" below), so a plausible
   fixture built from memory is not enough on its own.
2. Wire it up in `server.py` as a new `@mcp.tool()` function with a clear
   docstring: what it does, which credential it needs
   (`EVENTOR_API_KEY` vs `EVENTOR_USERNAME`/`EVENTOR_PASSWORD`), and --
   critically -- if it writes data, say so loudly in the docstring
   (`import_startlist`/`import_resultlist` are the existing examples).
   MCP clients (including LLM agents) read that docstring to decide how
   cautious to be.
3. Add a test in `tests/test_parsers.py` for the new parser.
4. If you can, validate against the real API once with your own
   credentials before opening a PR (see "Testing against the real API"
   below) -- Eventor's field values don't always match what the sparse
   official docs or other integrations suggest.

## A note on trusting the docs

Eventor's own API guide only documents authentication and one example
call. This project's endpoint shapes were reverse-engineered from a
working integration (`ttime.pl`), and even that got one thing wrong: it
assumed `punchingSystem="Emit"` was the only value for Emit control cards.
Live data showed `"emiTag"` is a **separate, real** system some clubs use
alongside `"Emit"`, and `"SI"` (SPORTident) shows up too -- see
`parsers.py`'s `_control_cards`. Moral: when touching parsing logic,
prefer verifying against a real response over trusting either the docs or
a previous implementation.

## Testing against the real API

You'll need:
- `EVENTOR_API_KEY` for `list_events`/`list_organisations` (club admin can
  generate one in Eventor under Klubben -> Klubbinnstillinger).
- `EVENTOR_USERNAME`/`EVENTOR_PASSWORD` (your personal Eventor login) for
  everything else.

Be careful with `import_startlist` and `import_resultlist` -- they publish
real data to a live system other people rely on. Don't call them against a
real, currently-open event unless that's actually what you mean to do.

## Pull requests

Small, focused PRs are easiest to review. Run `uv run pytest` before
opening one. There's no CI configured yet, so please actually run the
tests locally.
