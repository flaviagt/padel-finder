from padel_finder.models import CourtSlot
from padel_finder.ranking import rank_by_price


def test_rank_by_price_sorts_cheapest_first() -> None:
    expensive = CourtSlot(
        venue="Casablanca Padel Club",
        court="Court 2",
        date="2026-06-10",
        start_time="13:00",
        end_time="14:00",
        price=175000,
    )
    cheap = CourtSlot(
        venue="The Six Point Padel Club",
        court="Court 3",
        date="2026-06-10",
        start_time="13:00",
        end_time="14:00",
        price=150000,
    )

    assert rank_by_price([expensive, cheap]) == [cheap, expensive]
