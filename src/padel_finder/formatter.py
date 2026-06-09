"""Terminal output formatting."""

from __future__ import annotations

from collections.abc import Iterable

from padel_finder.config import Venue
from padel_finder.models import CourtSlot


def format_venues(venues: Iterable[Venue]) -> str:
    """Format supported venues for terminal output."""

    lines = ["🎾 Supported Padel Venues", ""]
    lines.extend(f"{index}. {venue.name}" for index, venue in enumerate(venues, start=1))
    return "\n".join(lines)


def format_available_slots(
    slots: Iterable[CourtSlot],
    date: str,
    start_time: str,
    end_time: str,
) -> str:
    """Format available court slots for terminal output."""

    slot_list = list(slots)
    if not slot_list:
        return "\n".join(
            [
                "❌ No courts available.",
                "",
                "No padel courts were found for:",
                f"Date: {date}",
                f"Time: {start_time} - {end_time}",
            ]
        )

    lines = [
        "🎾 Available Courts",
        f"Date: {date}",
        f"Time: {start_time} - {end_time}",
        "",
    ]
    for index, slot in enumerate(slot_list, start=1):
        lines.extend(
            [
                f"{index}. {slot.venue}",
                f"   Court: {slot.court}",
                f"   Time: {slot.start_time} - {slot.end_time}",
                f"   Price: {_format_price(slot.price)}",
                "",
            ]
        )

    return "\n".join(lines).rstrip()


def _format_price(price: int) -> str:
    return f"Rp{price:,}"
