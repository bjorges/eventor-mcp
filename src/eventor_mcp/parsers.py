"""Turn xmltodict-parsed Eventor XML into plain, predictable dicts/lists.

The field mappings here (Person/PersonId/content, Name/Family+Given,
ControlCard[].@punchingSystem == "Emit", etc.) are taken from a working
real-world integration against this API (ttime.pl), since Eventor's own
API documentation is sparse on response shapes.
"""

from __future__ import annotations

from typing import Any


def _as_list(value: Any) -> list[Any]:
    """xmltodict collapses a single repeated element to a dict; normalize to a list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _text(value: Any) -> str | None:
    """Some fields are plain text, others are {"@id": "...", "#text": "..."}."""
    if value is None:
        return None
    if isinstance(value, dict):
        return value.get("#text")
    return str(value)


def _date_clock(node: Any) -> str | None:
    """Fields like EntryDate/ModifyDate hold {"Date": ..., "Clock": ...}."""
    if not isinstance(node, dict):
        return None
    date = _text(node.get("Date"))
    clock = _text(node.get("Clock"))
    if date and clock:
        return f"{date} {clock}"
    return date


def parse_events(doc: dict) -> list[dict]:
    root = doc.get("EventList", doc)
    events = _as_list(root.get("Event"))
    result = []
    for e in events:
        organiser = e.get("Organiser") or {}
        organiser_ids = [_text(oid) for oid in _as_list(organiser.get("OrganisationId"))]
        result.append(
            {
                "id": _text(e.get("EventId")),
                "name": _text(e.get("Name")),
                "start_date": (e.get("StartDate") or {}).get("Date"),
                "finish_date": (e.get("FinishDate") or {}).get("Date"),
                "status_id": e.get("EventStatusId"),
                "organiser_ids": [oid for oid in organiser_ids if oid],
            }
        )
    return result


def parse_organisations(doc: dict) -> list[dict]:
    root = doc.get("OrganisationList", doc)
    orgs = _as_list(root.get("Organisation"))
    result = []
    for o in orgs:
        result.append(
            {
                "id": _text(o.get("Id")),
                "name": _text(o.get("Name")),
                "short_name": _text(o.get("ShortName")),
                "parent_id": _text(o.get("ParentOrganisationId")),
            }
        )
    return result


def parse_classes(doc: dict) -> list[dict]:
    root = doc.get("ClassList", doc)
    classes = _as_list(root.get("Class"))
    return [{"id": _text(c.get("EventClassId") or c.get("Id")), "name": _text(c.get("Name"))} for c in classes]


def parse_entry_changes(doc: dict) -> list[dict]:
    """Parse the (unversioned) export/entries response: who entered/changed when."""
    root = doc.get("EntryList", doc)
    result = []
    for club_entry in _as_list(root.get("ClubEntry")):
        for entry in _as_list(club_entry.get("Entry")):
            person = entry.get("Person") or {}
            result.append(
                {
                    "person_id": _text(person.get("PersonId")),
                    "entry_date": _date_clock(entry.get("EntryDate")),
                    "modify_date": _date_clock(entry.get("ModifyDate")),
                }
            )
    return result


def _control_card(node: dict) -> str | None:
    for cc in _as_list(node.get("ControlCard")):
        if isinstance(cc, dict) and cc.get("@punchingSystem") == "Emit":
            return _text(cc)
    return None


def parse_entries(doc: dict) -> list[dict]:
    """Parse the export/entries?version=3.0 response: full competitor entries."""
    root = doc.get("EntryList", doc)
    result = []
    for pe in _as_list(root.get("PersonEntry")):
        person = pe.get("Person") or {}
        name = person.get("Name") or {}
        org = pe.get("Organisation") or {}
        result.append(
            {
                "person_id": _text(person.get("Id")),
                "given_name": _text(name.get("Given")),
                "family_name": _text(name.get("Family")),
                "birth_date": _text(person.get("BirthDate")),
                "club_id": _text(org.get("Id")),
                "club_name": _text(org.get("Name")),
                "class_name": _text((pe.get("Class") or {}).get("Name")),
                "control_card": _control_card(pe),
            }
        )
    return result


def parse_competitors(doc: dict) -> list[dict]:
    """Parse the export/competitors?version=3.0 response: registered club members."""
    root = doc.get("CompetitorList", doc)
    result = []
    for c in _as_list(root.get("Competitor")):
        person = c.get("Person") or {}
        name = person.get("Name") or {}
        org = c.get("Organisation") or {}
        result.append(
            {
                "person_id": _text(person.get("Id")),
                "given_name": _text(name.get("Given")),
                "family_name": _text(name.get("Family")),
                "birth_date": _text(person.get("BirthDate")),
                "club_id": _text(org.get("Id")),
                "club_name": _text(org.get("Name")),
                "control_card": _control_card(c),
            }
        )
    return result
