"""Domain models for padel-finder."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CourtSlot:
    """An available padel court slot."""

    venue: str
    court: str
    date: str
    start_time: str
    end_time: str
    price: int
