import xmltodict

from eventor_mcp import parsers

EVENTS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<EventList>
  <Event>
    <EventId>24618</EventId>
    <Name>Urb-O #1 Individuell start</Name>
    <StartDate><Date>2026-11-03</Date></StartDate>
    <EventStatusId>5</EventStatusId>
    <Organiser><OrganisationId>123</OrganisationId></Organiser>
  </Event>
</EventList>
"""

ORGANISATIONS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<OrganisationList>
  <Organisation>
    <Id>8</Id>
    <Name>Hordaland</Name>
    <ShortName>HOK</ShortName>
    <ParentOrganisationId>1</ParentOrganisationId>
  </Organisation>
</OrganisationList>
"""

ENTRIES_XML = """<?xml version="1.0" encoding="UTF-8"?>
<EntryList>
  <PersonEntry>
    <Person>
      <Id>555</Id>
      <Name><Given>Ola</Given><Family>Nordmann</Family></Name>
      <BirthDate>1990-01-01</BirthDate>
    </Person>
    <Organisation>
      <Id>8</Id>
      <Name>Askoy o-lag</Name>
    </Organisation>
    <Class><Name>H21</Name></Class>
    <ControlCard punchingSystem="Emit">1234567</ControlCard>
  </PersonEntry>
  <PersonEntry>
    <Person>
      <Id>556</Id>
      <Name><Given>Kari</Given><Family>Nordmann</Family></Name>
    </Person>
    <Organisation>
      <Id>8</Id>
      <Name>Askoy o-lag</Name>
    </Organisation>
    <Class><Name>D21</Name></Class>
    <!-- Emit and emiTag are two distinct punching systems in Eventor,
         both used by this club, so both must be kept, not merged. -->
    <ControlCard punchingSystem="emiTag">7654321</ControlCard>
  </PersonEntry>
  <PersonEntry>
    <Person>
      <Id>557</Id>
      <Name><Given>Per</Given><Family>Hansen</Family></Name>
    </Person>
    <Organisation>
      <Id>8</Id>
      <Name>Askoy o-lag</Name>
    </Organisation>
    <Class><Name>H21</Name></Class>
    <ControlCard punchingSystem="Emit">1111111</ControlCard>
    <ControlCard punchingSystem="emiTag">2222222</ControlCard>
  </PersonEntry>
</EntryList>
"""


def test_parse_events():
    events = parsers.parse_events(xmltodict.parse(EVENTS_XML))
    assert events == [
        {
            "id": "24618",
            "name": "Urb-O #1 Individuell start",
            "start_date": "2026-11-03",
            "finish_date": None,
            "status_id": "5",
            "organiser_ids": ["123"],
        }
    ]


def test_parse_organisations():
    orgs = parsers.parse_organisations(xmltodict.parse(ORGANISATIONS_XML))
    assert orgs == [
        {
            "id": "8",
            "name": "Hordaland",
            "short_name": "HOK",
            "parent_id": "1",
        }
    ]


def test_parse_entries():
    entries = parsers.parse_entries(xmltodict.parse(ENTRIES_XML))
    assert entries == [
        {
            "person_id": "555",
            "given_name": "Ola",
            "family_name": "Nordmann",
            "birth_date": "1990-01-01",
            "club_id": "8",
            "club_name": "Askoy o-lag",
            "class_name": "H21",
            "control_cards": [{"system": "Emit", "number": "1234567"}],
        },
        {
            "person_id": "556",
            "given_name": "Kari",
            "family_name": "Nordmann",
            "birth_date": None,
            "club_id": "8",
            "club_name": "Askoy o-lag",
            "class_name": "D21",
            "control_cards": [{"system": "emiTag", "number": "7654321"}],
        },
        {
            "person_id": "557",
            "given_name": "Per",
            "family_name": "Hansen",
            "birth_date": None,
            "club_id": "8",
            "club_name": "Askoy o-lag",
            "class_name": "H21",
            "control_cards": [
                {"system": "Emit", "number": "1111111"},
                {"system": "emiTag", "number": "2222222"},
            ],
        },
    ]
