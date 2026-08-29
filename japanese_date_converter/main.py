"""
High-level entry points: automatic direction detection and full descriptions.
"""

from datetime import date, datetime
from typing import Any, Dict, List, Union

from .constants import KOKI_OFFSET
from .converters.japanese_to_standard import parse_japanese_date, to_standard
from .converters.standard_to_japanese import format_wareki, to_japanese
from .converters.utils import (
    day_of_year, normalize_japanese_string, parse_western_date, weekday_names,
)
from .eras import ERAS, GREGORIAN_ADOPTED, era_for_date
from .exceptions import DateConversionError, InputError, UnsupportedDateError

__all__ = ["convert_date", "detect_direction", "describe", "convert_many"]

_ERA_MARKERS = tuple(e.ja for e in ERAS) + tuple(e.ligature for e in ERAS)
_ROMAJI_MARKERS = ("meiji", "taisho", "taishou", "showa", "shouwa",
                   "heisei", "reiwa")


def detect_direction(date_string: str) -> str:
    """
    Guess which way a string needs converting.

    Returns ``"ja_to_standard"`` or ``"standard_to_ja"``. Detection looks for
    era kanji, era ligatures, romanised era names, and the ``R5.12.15`` style
    letter codes -- the last of these is why a plain substring check is not
    enough on its own.
    """
    if not isinstance(date_string, str):
        return "standard_to_ja"

    text = normalize_japanese_string(date_string)
    if any(marker in text for marker in _ERA_MARKERS):
        return "ja_to_standard"

    lowered = text.lower()
    if any(lowered.startswith(marker) for marker in _ROMAJI_MARKERS):
        return "ja_to_standard"

    # R5.12.15 / H31-04-30 / S640107
    if len(text) > 1 and text[0].upper() in "MTSHR" and text[1:].lstrip(". ")[:1].isdigit():
        return "ja_to_standard"

    return "standard_to_ja"


def convert_date(date_string: Union[str, date, datetime],
                 direction: str = "auto",
                 output_format: str = "iso",
                 japanese_style: str = "standard",
                 use_full_width: bool = True,
                 include_day: bool = True,
                 default_on_error: Any = "",
                 timezone_aware: bool = True,
                 day_first: bool = False,
                 use_gannen: bool = True,
                 strict: bool = False) -> Any:
    """
    Convert a date in either direction, detecting which one is needed.

    >>> convert_date("令和5年12月15日", output_format="%Y-%m-%d")
    '2023-12-15'
    >>> convert_date("2023-12-15", use_full_width=False)
    '令和5年12月15日'
    """
    if isinstance(date_string, (date, datetime)) and direction == "auto":
        direction = "standard_to_ja"
    elif direction == "auto":
        direction = detect_direction(date_string)

    if direction == "ja_to_standard":
        return to_standard(date_string, output_format, default_on_error,
                           timezone_aware, strict)
    if direction == "standard_to_ja":
        return to_japanese(date_string, japanese_style, use_full_width,
                           include_day, default_on_error, day_first,
                           use_gannen, strict)

    raise ValueError(
        "direction must be 'auto', 'ja_to_standard' or 'standard_to_ja', "
        "got {!r}".format(direction))


def describe(date_string: Union[str, date, datetime],
             day_first: bool = False) -> Dict[str, Any]:
    """
    Convert a date and return every derived form at once.

    Useful when you need more than one representation, or when you want to see
    the assumptions the parser made. Raises on unparseable input.

    The returned dict contains the parsed ``date``, the era, all seven wareki
    styles, ISO and human Western forms, weekday names, day of year, ISO week,
    the 皇紀 year, and a ``notes`` list of every assumption or boundary warning.
    """
    notes: List[str] = []

    if isinstance(date_string, datetime):
        value = date_string.date()
        era_hint = None
    elif isinstance(date_string, date):
        value = date_string
        era_hint = None
    else:
        if not isinstance(date_string, str) or not date_string.strip():
            raise InputError("Expected a non-empty date string", date_string)
        if detect_direction(date_string) == "ja_to_standard":
            parsed = parse_japanese_date(date_string)
            value, era_hint = parsed.date, (parsed.era, parsed.era_year)
            notes.extend(parsed.notes)
        else:
            value, western_notes = parse_western_date(date_string, day_first=day_first)
            era_hint = None
            notes.extend(western_notes)

    era = era_for_date(value)
    if era is None:
        notes.append(
            "No modern era covers {}. Era conversion starts at 明治元年 "
            "({}); earlier dates fall in the Edo-period eras, which need a "
            "lunisolar almanac rather than arithmetic.".format(
                value.isoformat(), ERAS[-1].start.isoformat()))
    elif value < GREGORIAN_ADOPTED and not any("Gregorian" in n for n in notes):
        notes.append(
            "Japan adopted the Gregorian calendar on 1873-01-01. Before that "
            "official dates were lunisolar, so this mapping is approximate.")

    weekday_en, weekday_ja = weekday_names(value)
    iso_year, iso_week, _ = value.isocalendar()

    result: Dict[str, Any] = {
        "date": value,
        "iso": value.isoformat(),
        "iso_timestamp": value.isoformat() + "T00:00:00.000Z",
        "slashed": value.strftime("%Y/%m/%d"),
        "compact": value.strftime("%Y%m%d"),
        "us_long": "{} {}, {}".format(value.strftime("%B"), value.day, value.year),
        "eu_long": "{} {} {}".format(value.day, value.strftime("%B"), value.year),
        "gregorian_ja": "{}年{}月{}日".format(value.year, value.month, value.day),
        "weekday_en": weekday_en,
        "weekday_ja": weekday_ja,
        "day_of_year": day_of_year(value),
        "iso_week": iso_week,
        "koki_year": value.year + KOKI_OFFSET,
        "era": None,
        "era_en": None,
        "era_year": None,
        "era_span": None,
        "wareki": None,
        "notes": notes,
    }

    if era is not None:
        result.update({
            "era": era.ja,
            "era_en": era.en,
            "era_year": era.year_of(value),
            "era_span": (era.start.isoformat(),
                         era.end.isoformat() if era.end else None),
            "wareki": {
                "standard": format_wareki(value, "standard", use_full_width=False),
                "full_width": format_wareki(value, "full_width"),
                "kanji": format_wareki(value, "kanji"),
                "formal": format_wareki(value, "formal", use_full_width=False),
                "period": format_wareki(value, "period", use_full_width=False),
                "code": format_wareki(value, "code"),
                "romaji": format_wareki(value, "romaji"),
            },
        })

    if era_hint is not None:
        result["input_era"] = era_hint[0].ja
        result["input_era_year"] = era_hint[1]

    return result


def convert_many(date_strings, day_first: bool = False) -> List[Dict[str, Any]]:
    """
    Convert a list of dates, detecting the direction of each one separately.

    Rows that fail come back with ``{"input": ..., "error": ...}`` rather than
    being dropped, so a bad row in a spreadsheet column never silently
    disappears from the output.
    """
    rows: List[Dict[str, Any]] = []
    for item in date_strings:
        try:
            row = describe(item, day_first=day_first)
            row["input"] = item
            row["error"] = None
        except DateConversionError as exc:
            row = {"input": item, "error": exc.message}
        rows.append(row)
    return rows
