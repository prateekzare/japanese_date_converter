"""
Normalisation, numeral handling and date validation helpers.
"""

import calendar
import re
import unicodedata
from datetime import date
from typing import Dict, List, Optional, Tuple

from ..constants import (
    FW_DIGITS, HW_DIGITS, KANJI_DIGITS, KANJI_UNITS,
    MONTH_LOOKUP, MONTH_NAMES_EN, KOKI_OFFSET,
    WEEKDAY_EN, WEEKDAY_JA,
)
from ..eras import ERAS, GREGORIAN_ADOPTED, era_for_date
from ..exceptions import InvalidDateComponentError, InvalidDateFormatError

__all__ = [
    "normalize_japanese_string",
    "to_half_width",
    "kanji_to_int",
    "int_to_kanji",
    "int_to_full_width",
    "kanji_numerals_to_arabic",
    "validate_date_components",
    "parse_english_date",
    "parse_western_date",
    "get_era_from_year",
    "koki_year",
    "weekday_names",
    "day_of_year",
]


# --------------------------------------------------------------------------
# Numerals
# --------------------------------------------------------------------------

def to_half_width(text: str) -> str:
    """Fold full-width ASCII and the ideographic space to half-width."""
    if not text:
        return ""
    return unicodedata.normalize("NFKC", text)


def kanji_to_int(text: str) -> Optional[int]:
    """
    Convert a kanji numeral to an int, or return None if it is not one.

    Handles both styles that appear in real documents:

    * positional -- 二〇二三 == 2023 (common in printed years)
    * additive   -- 三十一 == 31, 二千二十三 == 2023 (common in formal writing)
    """
    if not text:
        return None

    if all(c in KANJI_DIGITS for c in text):
        return int("".join(str(KANJI_DIGITS.index(c)) for c in text))

    total = 0
    current = 0
    seen = False
    for char in text:
        if char in KANJI_DIGITS:
            current = KANJI_DIGITS.index(char)
            seen = True
            continue
        unit = KANJI_UNITS.get(char)
        if unit is None:
            return None
        total += (current if current else 1) * unit
        current = 0
        seen = True
    if not seen:
        return None
    return total + current


_KANJI_RUN = re.compile("[" + KANJI_DIGITS + "".join(KANJI_UNITS) + "]+")


def kanji_numerals_to_arabic(text: str) -> str:
    """Replace every kanji numeral run in a string with its arabic value."""
    def _sub(match):
        value = kanji_to_int(match.group(0))
        return match.group(0) if value is None else str(value)
    return _KANJI_RUN.sub(_sub, text)


def int_to_full_width(value) -> str:
    return "".join(FW_DIGITS[int(c)] if c.isdigit() else c for c in str(value))


def int_to_kanji(value: int) -> str:
    """Render an int in additive kanji form (31 -> 三十一)."""
    value = int(value)
    if value < 0:
        return "-" + int_to_kanji(-value)
    if value == 0:
        return "〇"
    if value < 10:
        return KANJI_DIGITS[value]
    if value < 20:
        return "十" + (KANJI_DIGITS[value % 10] if value % 10 else "")
    if value < 100:
        return KANJI_DIGITS[value // 10] + "十" + (KANJI_DIGITS[value % 10] if value % 10 else "")
    if value < 1000:
        head, rest = divmod(value, 100)
        return ("" if head == 1 else KANJI_DIGITS[head]) + "百" + (int_to_kanji(rest) if rest else "")
    head, rest = divmod(value, 1000)
    return ("" if head == 1 else KANJI_DIGITS[head]) + "千" + (int_to_kanji(rest) if rest else "")


# --------------------------------------------------------------------------
# Normalisation
# --------------------------------------------------------------------------

def normalize_japanese_string(text: str) -> str:
    """
    Prepare a Japanese date string for parsing.

    Expands the single-codepoint era ligatures (㋿㍻㍼㍽㍾) that appear in
    vertical typesetting, folds full-width characters to ASCII, converts kanji
    numerals to digits, and collapses whitespace. Dates copied out of Japanese
    PDFs and spreadsheets are full-width far more often than not, so this runs
    before every parse rather than as an opt-in.
    """
    if not text or not isinstance(text, str):
        return ""

    result = text
    for era in ERAS:
        result = result.replace(era.ligature, era.ja)
    result = result.replace("㍺", "明治")  # legacy ligature variant

    result = to_half_width(result)
    result = kanji_numerals_to_arabic(result)
    result = re.sub(r"[、。,~～]", "", result)
    result = re.sub(r"\s+", " ", result)
    return result.strip()


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------

def validate_date_components(year: int, month: int, day: int) -> bool:
    """
    Check that the three components form a real Gregorian date.

    Raises :class:`InvalidDateComponentError` with a message that says which
    component is wrong and why, rather than a generic failure.
    """
    for name, value in (("year", year), ("month", month), ("day", day)):
        if not isinstance(value, int) or isinstance(value, bool):
            raise InvalidDateComponentError(
                "{} must be a whole number".format(name), name, value)

    if not 1 <= month <= 12:
        raise InvalidDateComponentError(
            "month {} does not exist, use 1 through 12".format(month), "month", month)

    if year < 1:
        raise InvalidDateComponentError(
            "year {} is out of range".format(year), "year", year)

    max_days = calendar.monthrange(year, month)[1]
    if day < 1:
        raise InvalidDateComponentError(
            "day {} does not exist, days start at 1".format(day), "day", day)
    if day > max_days:
        raise InvalidDateComponentError(
            "{} {} has only {} days, so day {} does not exist".format(
                MONTH_NAMES_EN[month - 1], year, max_days, day),
            "day", day)
    return True


# --------------------------------------------------------------------------
# Western date parsing
# --------------------------------------------------------------------------

_ORDINAL = re.compile(r"\b(\d{1,2})(st|nd|rd|th)\b", re.IGNORECASE)

_PATTERNS = [
    # ISO 8601, with an optional time part that we deliberately discard
    ("iso", re.compile(
        r"^(\d{1,4})-(\d{1,2})-(\d{1,2})(?:[T ][\d:.]+(?:Z|[+-]\d{2}:?\d{2})?)?$")),
    # 2023年12月15日 -- a Gregorian year written with Japanese markers
    ("jp_marked", re.compile(r"^(\d{1,4})年\s*(?:(\d{1,2})月\s*(?:(\d{1,2})日?)?)?$")),
    # 2023/12/15, 2023.12.15
    ("year_first", re.compile(r"^(\d{4})[/.](\d{1,2})[/.](\d{1,2})$")),
    # December 15, 2023
    ("month_name_first", re.compile(r"^([A-Za-z]+)\.?\s+(\d{1,2})\s+(\d{1,4})$")),
    # 15 December 2023
    ("day_first_name", re.compile(r"^(\d{1,2})\s+([A-Za-z]+)\.?\s+(\d{1,4})$")),
    # December 2023
    ("month_year", re.compile(r"^([A-Za-z]+)\.?\s+(\d{4})$")),
    # 12/15/2023 or 15/12/2023 -- genuinely ambiguous
    ("numeric", re.compile(r"^(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{2,4})$")),
    # 20231215
    ("compact", re.compile(r"^(\d{4})(\d{2})(\d{2})$")),
    # 2023
    ("year_only", re.compile(r"^(\d{4})$")),
]


def parse_western_date(date_string: str, day_first: bool = False):
    """
    Parse a Gregorian date in any of the supported shapes.

    Returns ``(date, notes)`` where *notes* is a list of assumptions the parser
    had to make -- a missing day filled in as the 1st, or which way round an
    ambiguous ``5/6/2023`` was read. Nothing is assumed silently.

    Raises :class:`InvalidDateFormatError` if no pattern matches, or
    :class:`InvalidDateComponentError` if the components are not a real date.
    """
    if not date_string or not isinstance(date_string, str):
        raise InvalidDateFormatError("No date given", date_string)

    text = normalize_japanese_string(date_string)
    if not text:
        raise InvalidDateFormatError("No date given", date_string)
    text = _ORDINAL.sub(r"\1", text)

    notes: List[str] = []

    for name, pattern in _PATTERNS:
        match = pattern.match(text)
        if not match:
            continue
        groups = match.groups()

        if name == "iso" or name == "year_first" or name == "compact":
            year, month, day = int(groups[0]), int(groups[1]), int(groups[2])

        elif name == "jp_marked":
            year = int(groups[0])
            month = int(groups[1]) if groups[1] else 1
            day = int(groups[2]) if groups[2] else 1
            if not groups[1] or not groups[2]:
                notes.append("No full day was given, so the 1st of the month was assumed.")

        elif name == "month_name_first":
            month = MONTH_LOOKUP.get(groups[0].lower())
            if month is None:
                continue
            day, year = int(groups[1]), int(groups[2])

        elif name == "day_first_name":
            month = MONTH_LOOKUP.get(groups[1].lower())
            if month is None:
                continue
            day, year = int(groups[0]), int(groups[2])

        elif name == "month_year":
            month = MONTH_LOOKUP.get(groups[0].lower())
            if month is None:
                continue
            year, day = int(groups[1]), 1
            notes.append("No day was given, so the 1st of the month was assumed.")

        elif name == "year_only":
            year, month, day = int(groups[0]), 1, 1
            notes.append("Only a year was given, so 1 January was assumed.")

        elif name == "numeric":
            first, second, year = int(groups[0]), int(groups[1]), int(groups[2])
            if year < 100:
                # Two-digit year window: 00-39 -> 2000s, 40-99 -> 1900s.
                year += 2000 if year < 40 else 1900
                notes.append("Two-digit year read as {}.".format(year))
            if first > 12 >= second:
                # Only one reading is possible, so no guess is involved.
                month, day = second, first
            elif second > 12 >= first:
                month, day = first, second
            else:
                month, day = (second, first) if day_first else (first, second)
                if first != second:
                    notes.append(
                        "'{}/{}' has two valid readings. Read as {}; "
                        "pass day_first={} for the other one.".format(
                            first, second,
                            "day/month" if day_first else "month/day",
                            not day_first))
        else:  # pragma: no cover - defensive
            continue

        validate_date_components(year, month, day)
        return date(year, month, day), notes

    raise InvalidDateFormatError(
        "Could not read as a Western date, try 2023-12-15, 15/12/2023 or "
        "December 15, 2023", date_string)


def parse_english_date(date_string: str) -> Optional[Dict[str, int]]:
    """
    Backwards-compatible wrapper kept from version 1.x.

    Returns ``{"year": ..., "month": ..., "day": ...}`` or None on failure,
    swallowing the exception. New code should call :func:`parse_western_date`,
    which reports *why* a string failed and what it assumed.
    """
    try:
        parsed, _notes = parse_western_date(date_string)
    except (InvalidDateFormatError, InvalidDateComponentError):
        return None
    return {"year": parsed.year, "month": parsed.month, "day": parsed.day}


# --------------------------------------------------------------------------
# Small derived values
# --------------------------------------------------------------------------

def get_era_from_year(year: int, month: int = 1, day: int = 1) -> Tuple[str, int]:
    """
    Return ``(era_name, era_year)`` for a date.

    Month and day default to 1 January, but pass the real ones whenever you
    have them: a year alone cannot distinguish 昭和64年 from 平成元年 (both
    1989) or 平成31年 from 令和元年 (both 2019).
    """
    target = date(year, month, day)
    era = era_for_date(target)
    if era is None:
        raise InvalidDateComponentError(
            "{} predates 明治元年 ({}), the earliest era supported".format(
                target.isoformat(), ERAS[-1].start.isoformat()),
            "year", year)
    return era.ja, era.year_of(target)


def koki_year(value: date) -> int:
    """皇紀 (imperial) year -- Gregorian year plus 660."""
    return value.year + KOKI_OFFSET


def weekday_names(value: date) -> Tuple[str, str]:
    """Return ``(english, japanese)`` weekday names."""
    index = (value.weekday() + 1) % 7  # Monday=0 -> Sunday-first index
    return WEEKDAY_EN[index], WEEKDAY_JA[index] + "曜日"


def day_of_year(value: date) -> int:
    return value.timetuple().tm_yday
