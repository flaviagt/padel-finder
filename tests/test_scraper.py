from padel_finder.models import CourtSlot
from padel_finder.scraper import parse_availability


def test_parse_availability_returns_matching_available_slots() -> None:
    payload = {
        "data": {
            "fields": [
                {
                    "field_name": "Court 3",
                    "slots": [
                        {
                            "start_time": "13:00",
                            "end_time": "14:00",
                            "available": True,
                            "price": "Rp150.000",
                        },
                        {
                            "start_time": "14:00",
                            "end_time": "15:00",
                            "available": True,
                            "price": 160000,
                        },
                    ],
                },
                {
                    "field_name": "Court 4",
                    "slots": [
                        {
                            "start_time": "13:00",
                            "end_time": "14:00",
                            "available": False,
                            "price": 125000,
                        }
                    ],
                },
            ]
        }
    }

    assert parse_availability(
        payload,
        venue_name="The Six Point Padel Club",
        date="2026-06-10",
        requested_start="13:00",
        requested_end="14:00",
    ) == [
        CourtSlot(
            venue="The Six Point Padel Club",
            court="Court 3",
            date="2026-06-10",
            start_time="13:00",
            end_time="14:00",
            price=150000,
        )
    ]


def test_parse_availability_handles_empty_availability() -> None:
    assert (
        parse_availability(
            {"data": {"fields": []}},
            venue_name="Casablanca Padel Club",
            date="2026-06-10",
            requested_start="13:00",
            requested_end="14:00",
        )
        == []
    )
