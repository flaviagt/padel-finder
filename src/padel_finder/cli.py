"""Command-line interface for padel-finder."""

from __future__ import annotations

import argparse
from datetime import date, datetime

from padel_finder.config import SUPPORTED_VENUES
from padel_finder.scraper import AvailabilityFetchError, fetch_all_availability


def main(argv: list[str] | None = None) -> None:
    """Run the command-line interface."""

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "venues":
        _print_venues()
        return

    if args.command == "search":
        start_time, end_time = _parse_time_range(args.time)
        try:
            slots = fetch_all_availability(args.date, start_time, end_time)
        except AvailabilityFetchError as exc:
            raise SystemExit(str(exc)) from exc

        _print_search_results(args.date, start_time, end_time, slots)
        return

    parser.print_help()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="padel-finder",
        description="Find available padel courts across supported AYO venues.",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("venues", help="List supported venues.")

    search_parser = subparsers.add_parser("search", help="Search available courts.")
    search_parser.add_argument(
        "--date",
        required=True,
        type=_parse_date,
        help="Search date in YYYY-MM-DD format.",
    )
    search_parser.add_argument(
        "--time",
        required=True,
        help="Requested court time range in HH:MM-HH:MM format.",
    )

    return parser


def _parse_date(value: str) -> str:
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date must be in YYYY-MM-DD format") from exc
    return value


def _parse_time_range(value: str) -> tuple[str, str]:
    parts = [part.strip() for part in value.split("-", maxsplit=1)]
    if len(parts) != 2:
        raise SystemExit("time must be in HH:MM-HH:MM format")

    start_time, end_time = parts
    try:
        datetime.strptime(start_time, "%H:%M")
        datetime.strptime(end_time, "%H:%M")
    except ValueError as exc:
        raise SystemExit("time must be in HH:MM-HH:MM format") from exc

    if start_time >= end_time:
        raise SystemExit("time range end must be after start")

    return start_time, end_time


def _print_venues() -> None:
    print("🎾 Supported Padel Venues")
    print()
    for index, venue in enumerate(SUPPORTED_VENUES, start=1):
        print(f"{index}. {venue.name}")


def _print_search_results(date_value: str, start_time: str, end_time: str, slots: list) -> None:
    sorted_slots = sorted(slots, key=lambda slot: slot.price)

    if not sorted_slots:
        print("❌ No courts available.")
        print()
        print("No padel courts were found for:")
        print(f"Date: {date_value}")
        print(f"Time: {start_time} - {end_time}")
        return

    print("🎾 Available Courts")
    print(f"Date: {date_value}")
    print(f"Time: {start_time} - {end_time}")
    print()
    for index, slot in enumerate(sorted_slots, start=1):
        print(f"{index}. {slot.venue}")
        print(f"   Court: {slot.court}")
        print(f"   Time: {slot.start_time} - {slot.end_time}")
        print(f"   Price: Rp{slot.price:,}")
        print()
