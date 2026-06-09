"""Court availability ranking helpers."""

from __future__ import annotations

from collections.abc import Iterable

from padel_finder.models import CourtSlot


def rank_by_price(slots: Iterable[CourtSlot]) -> list[CourtSlot]:
    """Return available court slots sorted from cheapest to most expensive."""

    return sorted(slots, key=lambda slot: slot.price)
