"""AYO availability scraping and parsing."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from typing import Any

import requests

from padel_finder.config import SUPPORTED_VENUES, Venue
from padel_finder.models import CourtSlot

AYO_AVAILABILITY_URL = "https://ayo.co.id/venues-ajax/op-times-and-fields"
DEFAULT_TIMEOUT_SECONDS = 15


class PadelFinderError(RuntimeError):
    """Base exception for padel-finder failures."""


class AvailabilityFetchError(PadelFinderError):
    """Raised when AYO availability cannot be fetched."""


def fetch_all_availability(
    date: str,
    start_time: str,
    end_time: str,
    venues: Iterable[Venue] = SUPPORTED_VENUES,
) -> list[CourtSlot]:
    """Fetch and parse available court slots from all supported venues."""

    slots: list[CourtSlot] = []
    with requests.Session() as session:
        for venue in venues:
            payload = fetch_venue_availability(session, venue, date)
            slots.extend(parse_availability(payload, venue.name, date, start_time, end_time))
    return slots


def fetch_venue_availability(
    session: requests.Session,
    venue: Venue,
    date: str,
) -> Mapping[str, Any]:
    """Fetch raw availability JSON for one venue."""

    try:
        response = session.get(
            AYO_AVAILABILITY_URL,
            params={"venue_id": venue.venue_id, "date": date},
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise AvailabilityFetchError(
            f"Could not fetch availability for {venue.name}."
        ) from exc
    except ValueError as exc:
        raise AvailabilityFetchError(
            f"AYO returned invalid JSON for {venue.name}."
        ) from exc

    if not isinstance(payload, Mapping):
        raise AvailabilityFetchError(f"AYO returned unexpected data for {venue.name}.")
    return payload


def parse_availability(
    payload: Mapping[str, Any],
    venue_name: str,
    date: str,
    requested_start: str,
    requested_end: str,
) -> list[CourtSlot]:
    """Parse AYO availability JSON into matching available court slots."""

    matching_slots: list[CourtSlot] = []
    for field in _iter_fields(payload):
        court_name = _court_name(field)
        if not court_name:
            continue

        for slot in _iter_slots(field):
            if not _is_available(slot):
                continue

            start_time, end_time = _slot_times(slot)
            if start_time != requested_start or end_time != requested_end:
                continue

            matching_slots.append(
                CourtSlot(
                    venue=venue_name,
                    court=court_name,
                    date=date,
                    start_time=start_time,
                    end_time=end_time,
                    price=_slot_price(slot),
                )
            )

    return matching_slots


def _iter_fields(payload: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
    containers = (
        payload.get("fields"),
        payload.get("data"),
        payload.get("result"),
        payload.get("op_times_and_fields"),
    )
    for container in containers:
        yield from _mapping_items(container)


def _mapping_items(value: Any) -> Iterable[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        if _looks_like_field(value):
            yield value
            return
        for nested in value.values():
            yield from _mapping_items(nested)
    elif isinstance(value, list):
        for item in value:
            yield from _mapping_items(item)


def _looks_like_field(value: Mapping[str, Any]) -> bool:
    return any(key in value for key in ("field_name", "name", "court", "slots", "times"))


def _court_name(field: Mapping[str, Any]) -> str | None:
    for key in ("field_name", "fieldName", "name", "court", "court_name"):
        value = field.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _iter_slots(field: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
    for key in ("slots", "times", "op_times", "operational_times", "availability"):
        yield from _slot_items(field.get(key))


def _slot_items(value: Any) -> Iterable[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        if _looks_like_slot(value):
            yield value
            return
        for nested in value.values():
            yield from _slot_items(nested)
    elif isinstance(value, list):
        for item in value:
            yield from _slot_items(item)


def _looks_like_slot(value: Mapping[str, Any]) -> bool:
    slot_keys = {
        "available",
        "is_available",
        "isAvailable",
        "status",
        "availability_status",
        "booked",
        "is_booked",
        "isBooked",
        "start_time",
        "startTime",
        "end_time",
        "endTime",
        "time_range",
        "label",
    }
    return bool(slot_keys.intersection(value))


def _is_available(slot: Mapping[str, Any]) -> bool:
    for key in ("available", "is_available", "isAvailable"):
        value = slot.get(key)
        if isinstance(value, bool):
            return value

    status = slot.get("status") or slot.get("availability_status")
    if isinstance(status, str):
        return status.strip().lower() in {"available", "open", "free"}

    booked = slot.get("booked") or slot.get("is_booked") or slot.get("isBooked")
    if isinstance(booked, bool):
        return not booked

    return False


def _slot_times(slot: Mapping[str, Any]) -> tuple[str, str]:
    start = _normalize_time(
        slot.get("start_time") or slot.get("startTime") or slot.get("from") or slot.get("time")
    )
    end = _normalize_time(slot.get("end_time") or slot.get("endTime") or slot.get("to"))

    if not end:
        time_range = slot.get("time_range") or slot.get("label")
        if isinstance(time_range, str) and "-" in time_range:
            start_part, end_part = time_range.split("-", maxsplit=1)
            start = start or _normalize_time(start_part)
            end = _normalize_time(end_part)

    return start, end


def _normalize_time(value: Any) -> str:
    if not isinstance(value, str):
        return ""

    match = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", value)
    if not match:
        return ""
    return f"{int(match.group(1)):02d}:{match.group(2)}"


def _slot_price(slot: Mapping[str, Any]) -> int:
    for key in ("price", "total_price", "amount", "rate"):
        value = slot.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            digits = re.sub(r"\D", "", value)
            if digits:
                return int(digits)
    return 0
