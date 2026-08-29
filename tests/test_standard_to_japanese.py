"""
Gregorian -> wareki formatting, plus the round trip.
"""

from datetime import date, datetime

import pytest

from japanese_date_converter import (
    UnsupportedDateError, convert_date, describe, to_japanese, to_standard,
)


def jp(text, **kwargs):
    kwargs.setdefault("use_full_width", False)
    kwargs.setdefault("strict", True)
    return to_japanese(text, **kwargs)


@pytest.mark.parametrize("text,expected", [
    ("2023-12-15", "令和5年12月15日"),
    ("2018-01-01", "平成30年1月1日"),
    ("1989-01-07", "昭和64年1月7日"),
    ("1989-01-08", "平成元年1月8日"),
    ("2019-04-30", "平成31年4月30日"),
    ("2019-05-01", "令和元年5月1日"),
    ("1926-12-25", "昭和元年12月25日"),
    ("1912-07-30", "大正元年7月30日"),
])
def test_boundaries_resolve_by_date_not_year(text, expected):
    assert jp(text) == expected


@pytest.mark.parametrize("text", [
    "2023-12-15", "2023/12/15", "20231215", "December 15, 2023",
    "Dec 15 2023", "15 December 2023", "2023年12月15日",
    "2023-12-15T00:00:00.000Z",
])
def test_western_input_shapes(text):
    assert jp(text) == "令和5年12月15日"


def test_accepts_date_and_datetime_objects():
    assert jp(date(2023, 12, 15)) == "令和5年12月15日"
    assert jp(datetime(2023, 12, 15, 9, 30)) == "令和5年12月15日"


@pytest.mark.parametrize("style,expected", [
    ("standard", "令和5年12月15日"),
    ("full_width", "令和５年１２月１５日"),
    ("kanji", "令和五年十二月十五日"),
    ("formal", "令和5年12月15日付"),
    ("period", "令和5年12月分"),
    ("code", "R05.12.15"),
    ("romaji", "Reiwa 5, December 15"),
])
def test_output_styles(style, expected):
    assert jp("2023-12-15", output_style=style) == expected


def test_full_width_is_the_default():
    assert to_japanese("2023-12-15") == "令和５年１２月１５日"


def test_gannen_can_be_switched_off():
    assert jp("2019-05-01") == "令和元年5月1日"
    assert jp("2019-05-01", use_gannen=False) == "令和1年5月1日"


def test_include_day():
    assert jp("2023-12-15", include_day=False) == "令和5年12月"


def test_day_first_toggle():
    assert jp("5/6/2023") == "令和5年5月6日"
    assert jp("5/6/2023", day_first=True) == "令和5年6月5日"
    # Only one reading is possible here, so the toggle is irrelevant.
    assert jp("15/6/2023") == "令和5年6月15日"
    assert jp("15/6/2023", day_first=True) == "令和5年6月15日"


def test_ambiguity_is_reported():
    assert any("two valid readings" in n for n in describe("5/6/2023")["notes"])
    assert not describe("15/6/2023")["notes"]


def test_pre_meiji_is_refused_with_a_reason():
    with pytest.raises(UnsupportedDateError):
        jp("1868-10-22")
    assert to_japanese("1868-10-22", default_on_error="N/A") == "N/A"


@pytest.mark.parametrize("text", ["not a date", "2023-13-01", "2023-02-29", ""])
def test_bad_input(text):
    assert to_japanese(text, default_on_error="N/A") == "N/A"


@pytest.mark.parametrize("original", [
    "2023-12-15", "2019-05-01", "2019-04-30", "1989-01-07", "1989-01-08",
    "1926-12-25", "1912-07-30", "1873-01-01", "2024-02-29",
])
def test_round_trip(original):
    wareki = jp(original)
    assert to_standard(wareki, output_format="%Y-%m-%d", strict=True) == original


def test_auto_direction_detection():
    assert convert_date("令和5年12月15日", output_format="%Y-%m-%d") == "2023-12-15"
    assert convert_date("R5.12.15", output_format="%Y-%m-%d") == "2023-12-15"
    assert convert_date("2023-12-15", use_full_width=False) == "令和5年12月15日"
    assert convert_date(date(2023, 12, 15), use_full_width=False) == "令和5年12月15日"


def test_describe_returns_every_form():
    info = describe("令和5年12月15日")
    assert info["iso"] == "2023-12-15"
    assert info["era"] == "令和" and info["era_year"] == 5
    assert info["weekday_en"] == "Friday" and info["weekday_ja"] == "金曜日"
    assert info["koki_year"] == 2683
    assert info["day_of_year"] == 349
    assert info["wareki"]["kanji"] == "令和五年十二月十五日"
    assert info["wareki"]["code"] == "R05.12.15"


def test_describe_handles_unsupported_dates_without_raising():
    info = describe("1600-01-01")
    assert info["iso"] == "1600-01-01"
    assert info["era"] is None and info["wareki"] is None
    assert any("明治元年" in n for n in info["notes"])
