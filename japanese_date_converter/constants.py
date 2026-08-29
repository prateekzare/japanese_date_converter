"""
Character tables and format constants.

Era data lives in :mod:`japanese_date_converter.eras`, not here -- an era is a
date range, not a constant, and keeping it separate is what stops the old
"start year" shortcut from creeping back in.
"""

from .eras import ERAS

__all__ = [
    "FW_DIGITS", "HW_DIGITS", "KANJI_DIGITS", "KANJI_UNITS",
    "ERA_NAMES", "ERA_CODES", "ERA_LIGATURES",
    "MONTH_NAMES_JP", "MONTH_NAMES_EN", "MONTH_LOOKUP",
    "WEEKDAY_JA", "WEEKDAY_EN",
    "DEFAULT_ISO_FORMAT", "DEFAULT_DATE_FORMAT", "DEFAULT_DATETIME_FORMAT",
    "KOKI_OFFSET",
]

# Digits -----------------------------------------------------------------
FW_DIGITS = "０１２３４５６７８９"
HW_DIGITS = "0123456789"
KANJI_DIGITS = "〇一二三四五六七八九"
KANJI_UNITS = {"十": 10, "百": 100, "千": 1000}

# Era name lookups, generated from the era table so they cannot drift ------
ERA_NAMES = {}
for _e in ERAS:
    ERA_NAMES[_e.ja] = _e.en
    ERA_NAMES[_e.en.lower()] = _e.ja
    for _r in _e.romaji:
        ERA_NAMES[_r] = _e.ja
del _e, _r

ERA_CODES = {e.code: e.ja for e in ERAS}
ERA_LIGATURES = {e.ligature: e.ja for e in ERAS}

# Months -----------------------------------------------------------------
MONTH_NAMES_JP = {n: "{}月".format(n) for n in range(1, 13)}

MONTH_NAMES_EN = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

MONTH_LOOKUP = {}
for _i, _name in enumerate(MONTH_NAMES_EN, start=1):
    MONTH_LOOKUP[_name.lower()] = _i
    MONTH_LOOKUP[_name.lower()[:3]] = _i
MONTH_LOOKUP["sept"] = 9
del _i, _name

# Weekdays (index 0 == Sunday, matching date.isoweekday() % 7) ------------
WEEKDAY_JA = ["日", "月", "火", "水", "木", "金", "土"]
WEEKDAY_EN = ["Sunday", "Monday", "Tuesday", "Wednesday",
              "Thursday", "Friday", "Saturday"]

# Formats ----------------------------------------------------------------
DEFAULT_ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
DEFAULT_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

#: 皇紀 (koki), the imperial year count, is the Gregorian year plus this.
KOKI_OFFSET = 660
