# padel-finder

`padel-finder` is a Python command-line tool that helps users find available padel courts by checking multiple venues, filtering for a requested date and time, and ranking available courts from cheapest to most expensive. 

Supported venues (personal favorite courts):

- Casablanca Padel Club
- The Six Point Padel Club
- Bumi Pancasona Sports Club

## Installation

Install directly from GitHub with `uv`:

```bash
uv add "git+https://github.com/<username>/padel-finder.git"
```

## Usage

List all supported venues:

```bash
padel-finder venues
```

Search for available courts across supported venues:

```bash
padel-finder search --date YYYY-MM-DD --time HH:MM-HH:MM
```

Example:

```bash
padel-finder search --date 2026-06-10 --time 13:00-14:00
```

## Development

Install dependencies:

```bash
uv sync
```

Run tests:

```bash
uv run pytest
```
