"""
Japanese Date Converter
=======================

Convert between Japanese era dates (wareki) and Gregorian dates (seireki).

Eras are stored as full start and end *dates* rather than start years, so the
mid-year transitions resolve correctly::

    >>> to_japanese("2019-04-30", use_full_width=False)
    '平成31年4月30日'
    >>> to_japanese("2019-05-01", use_full_width=False)
    '令和元年5月1日'
    >>> to_japanese("1989-01-07", use_full_width=False)
    '昭和64年1月7日'

Try it in the browser, no install required:
https://convertnow.tools/tools/date-time/japanese-date-converter-free/
"""

from .converters import (
    JapaneseToStandardConverter,
    StandardToJapaneseConverter,
    format_wareki,
    get_era_from_year,
    int_to_kanji,
    kanji_to_int,
    normalize_japanese_string,
    parse_english_date,
    parse_japanese_date,
    parse_western_date,
    to_japanese,
    to_standard,
    validate_date_components,
)
from .eras import ERAS, Era, era_for_date, era_year_for, find_era
from .exceptions import (
    AmbiguousDateError,
    ConfigurationError,
    ConverterRuntimeError,
    DateConversionError,
    InputError,
    InvalidDateComponentError,
    InvalidDateFormatError,
    InvalidEraError,
    UnsupportedDateError,
    ValidationError,
)
from .main import convert_date, convert_many, describe, detect_direction

__version__ = "2.0.0"
__author__ = "Prateek Zare"
__url__ = "https://convertnow.tools/tools/date-time/japanese-date-converter-free/"

__all__ = [
    # high level
    "convert_date",
    "convert_many",
    "describe",
    "detect_direction",
    # directional
    "to_standard",
    "to_japanese",
    "JapaneseToStandardConverter",
    "StandardToJapaneseConverter",
    "parse_japanese_date",
    "parse_western_date",
    "format_wareki",
    # era table
    "Era",
    "ERAS",
    "era_for_date",
    "era_year_for",
    "find_era",
    "get_era_from_year",
    # helpers
    "normalize_japanese_string",
    "parse_english_date",
    "validate_date_components",
    "kanji_to_int",
    "int_to_kanji",
    # exceptions
    "DateConversionError",
    "InvalidDateFormatError",
    "InvalidEraError",
    "InvalidDateComponentError",
    "UnsupportedDateError",
    "AmbiguousDateError",
    "ConfigurationError",
    "ConverterRuntimeError",
    "ValidationError",
    "InputError",
]
