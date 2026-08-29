"""
Every example from the 1.x README, pinned.

The point of this file is that upgrading to 2.0 must not break existing
callers. Two cases deliberately differ from what the 1.x README printed, and
both are marked below with the reason -- in both cases the 1.x README was
documenting a bug or a typo, not behaviour worth preserving.
"""

from datetime import date, datetime, timezone

import pytest

from japanese_date_converter import (
    JapaneseToStandardConverter, StandardToJapaneseConverter,
    convert_date, to_japanese, to_standard,
)


# --- Quick Start ----------------------------------------------------------

def test_quickstart_japanese_to_standard_autodetected():
    assert convert_date("令和5年12月15日") == "2023-12-15T00:00:00.000Z"


def test_quickstart_standard_to_japanese_autodetected():
    assert convert_date("2024-07-01") == "令和６年７月１日"


def test_quickstart_output_format():
    assert convert_date("令和5年12月15日", output_format="%Y/%m/%d") == "2023/12/15"


def test_quickstart_period_style_accepts_year_month():
    # 1.x documented this but did not implement it -- parse_english_date had no
    # year-month pattern, so it returned the error default. 2.0 parses it.
    assert convert_date("2023-06", japanese_style="period") == "令和５年６月分"


# --- Converting Japanese dates to standard formats ------------------------

def test_basic_iso_conversion():
    assert to_standard("令和5年12月15日") == "2023-12-15T00:00:00.000Z"


def test_datetime_output():
    stamp = to_standard("令和6年3月1日", output_format="datetime")
    assert stamp == datetime(2024, 3, 1, tzinfo=timezone.utc)
    assert (stamp.year, stamp.month, stamp.day) == (2024, 3, 1)


def test_custom_output_format_from_period_input():
    assert to_standard("令和5年12月分", output_format="%Y/%m/%d") == "2023/12/01"


def test_without_timezone_information():
    assert to_standard("平成30年1月1日", output_format="%Y-%m-%d",
                       timezone_aware=False) == "2018-01-01"


def test_custom_value_on_error():
    assert to_standard("invalid text", default_on_error="INVALID DATE") == "INVALID DATE"


# --- Converting standard dates to Japanese format -------------------------

def test_basic_japanese_conversion():
    assert to_japanese("2023-12-15") == "令和５年１２月１５日"


def test_standard_style():
    assert to_japanese("2023-06-15", output_style="standard") == "令和５年６月１５日"


def test_formal_style_keeps_the_day():
    # DELIBERATE CHANGE. 1.x printed 令和５年６月日付 -- the day was dropped, so
    # the string was malformed (年月日付 with no 日 value). 2.0 keeps it.
    assert to_japanese("2023-06-15", output_style="formal") == "令和５年６月１５日付"


def test_period_style():
    assert to_japanese("2023-06-15", output_style="period") == "令和５年６月分"


def test_half_width_digits():
    assert to_japanese("2023-06-15", use_full_width=False) == "令和5年6月15日"


def test_without_day():
    assert to_japanese("2023-06-15", include_day=False) == "令和５年６月"


# --- Automatic direction detection ----------------------------------------

def test_auto_detection_both_ways():
    assert convert_date("令和5年12月15日") == "2023-12-15T00:00:00.000Z"
    assert convert_date("2023-12-15") == "令和５年１２月１５日"


# --- Supported date formats -----------------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("令和5年12月15日", "2023-12-15"),          # standard
    ("令和６年 ７月２５日", "2024-07-25"),        # full-width plus spaces
    ("令和07年01月23日", "2025-01-23"),          # zero-padded, see note below
    ("令和5年12月", "2023-12-01"),               # year and month only
    ("令和６年１２月分", "2024-12-01"),           # month period
])
def test_documented_japanese_input_formats(text, expected):
    # NOTE on 令和07年: the 1.x README claimed this was 2023-01-23. It is not.
    # 令和 began in 2019, so 令和7年 is 2025 -- 2023 would be 令和5年. 1.x
    # itself returned 2025 here; only the README was wrong.
    assert to_standard(text, output_format="%Y-%m-%d") == expected


@pytest.mark.parametrize("text", [
    "2023-12-15T00:00:00.000Z",   # ISO 8601
    "2023-12-15",
    "12/15/2023",
    "December 15, 2023",
])
def test_documented_standard_input_formats(text):
    assert to_japanese(text) == "令和５年１２月１５日"


@pytest.mark.parametrize("value", [
    datetime(2023, 12, 15),
    datetime(2023, 12, 15, 9, 30, 15),
    date(2023, 12, 15),
])
def test_documented_datetime_objects(value):
    assert to_japanese(value) == "令和５年１２月１５日"
    # 2.0 also accepts them on the other side, for symmetry.
    assert to_standard(value, output_format="%Y-%m-%d") == "2023-12-15"


# --- Signatures still accept 1.x positional order -------------------------

def test_positional_arguments_are_unchanged():
    assert to_standard("令和5年12月15日", "%Y-%m-%d", "ERR", False) == "2023-12-15"
    assert to_japanese("2023-12-15", "standard", False, True, "ERR") == "令和5年12月15日"
    assert convert_date("令和5年12月15日", "ja_to_standard", "%Y-%m-%d") == "2023-12-15"


def test_explicit_direction_arguments():
    assert convert_date("令和5年12月15日", direction="ja_to_standard",
                        output_format="%Y-%m-%d") == "2023-12-15"
    assert convert_date("2023-12-15", direction="standard_to_ja",
                        use_full_width=False) == "令和5年12月15日"


def test_1x_imports_all_still_resolve():
    from japanese_date_converter import (  # noqa: F401
        ConfigurationError, ConverterRuntimeError, DateConversionError,
        InputError, InvalidDateComponentError, InvalidDateFormatError,
        InvalidEraError, JapaneseToStandardConverter,
        StandardToJapaneseConverter, UnsupportedDateError, ValidationError,
        convert_date, to_japanese, to_standard,
    )
    from japanese_date_converter.converters import (  # noqa: F401
        get_era_from_year, normalize_japanese_string, parse_english_date,
        validate_date_components,
    )


def test_1x_converter_classes_still_work():
    assert JapaneseToStandardConverter().convert(
        "令和5年12月15日", "%Y-%m-%d") == "2023-12-15"
    assert StandardToJapaneseConverter().convert(
        "2023-12-15", "standard", False) == "令和5年12月15日"


def test_1x_helper_functions_still_work():
    from japanese_date_converter.converters import (
        get_era_from_year, normalize_japanese_string, parse_english_date,
        validate_date_components,
    )
    assert normalize_japanese_string("令和５年１２月１５日") == "令和5年12月15日"
    assert parse_english_date("2023-12-15") == {"year": 2023, "month": 12, "day": 15}
    assert parse_english_date("nonsense") is None
    assert validate_date_components(2023, 12, 15) is True
    # 1.x signature was get_era_from_year(year) and returned (era, era_year).
    assert get_era_from_year(2023) == ("令和", 5)
    # 2.0 accepts the month and day too, which is the only way to be right
    # across a transition.
    assert get_era_from_year(2019, 4, 30) == ("平成", 31)
    assert get_era_from_year(2019, 5, 1) == ("令和", 1)
