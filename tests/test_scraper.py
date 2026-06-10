from padel_finder.models import CourtSlot
from padel_finder.scraper import parse_availability


def test_parse_availability_returns_matching_available_slots() -> None:
    payload = {
        "data": {
            "fields": [
                {
                    "field_name": "Court 3",
                    "sport_id": 12,
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
                    "sport_id": 12,
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


def test_parse_availability_handles_ayo_numeric_availability_flags() -> None:
    payload = {
        "op_time": {
            "day": "Jum'at",
            "dow": 5,
            "is_open": True,
            "hours": [{"open": "06:00", "close": "07:00"}],
        },
        "fields": [
            {
                "field_id": 2666,
                "field_name": "Mazda Court",
                "sport_id": 12,
                "total_available_slots": 14,
                "special_notes": None,
                "slots": [
                    {
                        "id": 121035155,
                        "start_time": "11:00:00",
                        "end_time": "12:00:00",
                        "price": 99000,
                        "strike_price": 149000,
                        "date": "2026-06-10",
                        "start_date_time": "2026-06-10 11:00:00",
                        "end_date_time": "2026-06-10 12:00:00",
                        "is_combined_slot": 0,
                        "is_popular": 0,
                        "is_available": 1,
                        "is_selected": 0,
                        "duration_per_session": 60,
                    },
                    {
                        "id": 121035162,
                        "start_time": "12:00:00",
                        "end_time": "13:00:00",
                        "price": 99000,
                        "date": "2026-06-10",
                        "is_available": 0,
                    },
                ],
            }
        ],
    }

    assert parse_availability(
        payload,
        venue_name="Casablanca Padel Club",
        date="2026-06-10",
        requested_start="11:00",
        requested_end="12:00",
    ) == [
        CourtSlot(
            venue="Casablanca Padel Club",
            court="Mazda Court",
            date="2026-06-10",
            start_time="11:00",
            end_time="12:00",
            price=99000,
        )
    ]


def test_parse_availability_filters_non_padel_fields() -> None:
    payload = {
        "fields": [
            {
                "field_name": "Badminton - Court 1",
                "sport_id": 3,
                "slots": [
                    {
                        "start_time": "11:00:00",
                        "end_time": "12:00:00",
                        "price": 120000,
                        "is_available": 1,
                    }
                ],
            },
            {
                "field_name": "Padel Court 1",
                "sport_id": 12,
                "slots": [
                    {
                        "start_time": "11:00:00",
                        "end_time": "12:00:00",
                        "price": 280000,
                        "is_available": 1,
                    }
                ],
            },
        ]
    }

    assert parse_availability(
        payload,
        venue_name="Bumi Pancasona Sports Club",
        date="2026-06-10",
        requested_start="11:00",
        requested_end="12:00",
    ) == [
        CourtSlot(
            venue="Bumi Pancasona Sports Club",
            court="Padel Court 1",
            date="2026-06-10",
            start_time="11:00",
            end_time="12:00",
            price=280000,
        )
    ]
