"""
Japanese era (nengo) table and era resolution.

The important design decision in this module: an era is defined by its full
start and end *date*, not by a start year. Japanese eras change on the day a
reign changes, not on 1 January, so a year-only table silently produces the
wrong era around every transition. Two of the five modern transitions fall
mid-year and two share a boundary day with the preceding era.
"""

from datetime import date
from typing import List, Optional, Tuple

__all__ = [
    "Era",
    "ERAS",
    "ERAS_BY_JA",
    "GREGORIAN_ADOPTED",
    "MEIJI_START",
    "era_for_date",
    "find_era",
    "era_year_for",
]


class Era:
    """A single Japanese era with its exact Gregorian span."""

    __slots__ = ("ja", "en", "romaji", "code", "ligature", "start", "end")

    def __init__(self, ja, en, romaji, code, ligature, start, end):
        self.ja = ja                # 令和
        self.en = en                # Reiwa
        self.romaji = romaji        # accepted romanised spellings, lowercase
        self.code = code            # R
        self.ligature = ligature    # ㋿
        self.start = start          # first day of the era
        self.end = end              # last day, or None if ongoing

    def contains(self, d: date) -> bool:
        return self.start <= d and (self.end is None or d <= self.end)

    def year_of(self, d: date) -> int:
        """Era year for a Gregorian date (not range-checked)."""
        return d.year - self.start.year + 1

    def gregorian_year(self, era_year: int) -> int:
        return self.start.year + era_year - 1

    @property
    def is_current(self) -> bool:
        return self.end is None

    def __repr__(self):
        return "<Era {} ({}) {} - {}>".format(
            self.ja, self.en, self.start.isoformat(),
            self.end.isoformat() if self.end else "present"
        )


# Ordered newest first. That ordering is load-bearing: on the two days that
# belong to two eras at once (1912-07-30 is both 明治45年7月30日 and 大正元年
# 7月30日; 1926-12-25 is both 大正15年12月25日 and 昭和元年12月25日) the first
# match wins, which gives the newer era -- the convention used on Japanese
# government forms.
ERAS: List[Era] = [
    Era("令和", "Reiwa", ("reiwa",), "R", "㋿",
        date(2019, 5, 1), None),
    Era("平成", "Heisei", ("heisei",), "H", "㍻",
        date(1989, 1, 8), date(2019, 4, 30)),
    Era("昭和", "Showa", ("showa", "shouwa", "shōwa"), "S", "㍼",
        date(1926, 12, 25), date(1989, 1, 7)),
    Era("大正", "Taisho", ("taisho", "taishou", "taishō"), "T", "㍽",
        date(1912, 7, 30), date(1926, 12, 25)),
    Era("明治", "Meiji", ("meiji",), "M", "㍾",
        date(1868, 10, 23), date(1912, 7, 30)),
]

ERAS_BY_JA = {e.ja: e for e in ERAS}

#: First day covered by the era table.
MEIJI_START = ERAS[-1].start

#: Japan switched from the lunisolar Tenpo calendar to the Gregorian calendar
#: on this date (明治5年12月3日 was redesignated 1873-01-01). Dates before it
#: are flagged as approximate rather than silently converted.
GREGORIAN_ADOPTED = date(1873, 1, 1)


def era_for_date(d: date) -> Optional[Era]:
    """Return the era covering ``d``, or None if it predates 明治元年."""
    for era in ERAS:
        if era.contains(d):
            return era
    return None


def era_year_for(d: date) -> Optional[Tuple[Era, int]]:
    """Return ``(era, era_year)`` for a date, or None if unsupported."""
    era = era_for_date(d)
    if era is None:
        return None
    return era, era.year_of(d)


def find_era(token: str) -> Optional[Era]:
    """
    Resolve an era from a kanji name, ligature, romaji spelling, English name
    or single-letter code. Returns None if nothing matches.
    """
    if not token:
        return None
    raw = token.strip()
    lowered = "".join(c for c in raw.lower() if c.isalpha())
    for era in ERAS:
        if raw == era.ja or raw == era.ligature:
            return era
        if lowered and (lowered in era.romaji or lowered == era.en.lower()):
            return era
        if raw.upper() == era.code:
            return era
    return None
