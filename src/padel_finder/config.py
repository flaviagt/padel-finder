"""Supported venue configuration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Venue:
    """A padel venue supported by the AYO availability endpoint."""

    name: str
    venue_id: int


SUPPORTED_VENUES: tuple[Venue, ...] = (
    Venue(name="Casablanca Padel Club", venue_id=1059),
    Venue(name="The Six Point Padel Club", venue_id=1387),
    Venue(name="Bumi Pancasona Sports Club", venue_id=1121),
)
