"""
Wareki -> Gregorian parsing.
"""

from datetime import date, datetime, timezone

import pytest

from japanese_date_converter import (
    InvalidDateComponentError, InvalidDateFormatError, InvalidEraError,
    parse_japanese_date, to_standard,
)


def iso(text, **kwargs):
    return to_standard(text, output_format="%Y-%m-%d", strict=True, **kwargs)


@pytest.mark.parametrize("text,expected", [
    ("令和5年12月15日", "2023-12-15"),
    ("令和05年01月23日", "2023-01-23"),
    ("平成30年1月1日", "2018-01-01"),
    ("昭和64年1月7日", "1989-01-07"),
    ("大正15年12月25日", "1926-12-25"),
    ("明治45年7月29日", "1912-07-29"),
])
def test_standard_written_form(text, expected):
    assert iso(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("令和元年5月1日", "2019-05-01"),
    ("平成元年1月8日", "1989-01-08"),
    ("昭和元年12月25日", "1926-12-25"),
    ("大正元年7月30日", "1912-07-30"),
])
def test_gannen_is_year_one(text, expected):
    assert iso(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("令和５年１２月１５日", "2023-12-15"),      # full-width digits
    ("令和 ５年 １２月 １５日", "2023-12-15"),   # full-width plus spaces
    ("平成三十一年四月三十日", "2019-04-30"),     # additive kanji numerals
    ("令和五年十二月十五日", "2023-12-15"),
    ("㋿5年12月15日", "2023-12-15"),            # Unicode era ligature
    ("㍻31年4月30日", "2019-04-30"),
])
def test_full_width_kanji_and_ligatures(text, expected):
    assert iso(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("R5.12.15", "2023-12-15"),
    ("H31-04-30", "2019-04-30"),
    ("S64/1/7", "1989-01-07"),
    ("R051215", "2023-12-15"),
    ("r5.12.15", "2023-12-15"),
])
def test_id_card_codes(text, expected):
    assert iso(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("Reiwa 5/12/15", "2023-12-15"),
    ("Heisei 31年4月30日", "2019-04-30"),
    ("showa 64年1月7日", "1989-01-07"),
    ("Shōwa 64年1月7日", "1989-01-07"),
])
def test_romaji_era_names(text, expected):
    assert iso(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("令和5年", "2023-01-01"),
    ("令和5年12月", "2023-12-01"),
    ("平成30年4月分", "2018-04-01"),
    ("令和6年12月分", "2024-12-01"),
])
def test_partial_dates_default_to_the_first(text, expected):
    assert iso(text) == expected
    assert parse_japanese_date(text).notes  # the assumption is reported


def test_output_formats():
    assert to_standard("令和5年12月15日") == "2023-12-15T00:00:00.000Z"
    assert to_standard("令和5年12月15日", timezone_aware=False) == "2023-12-15T00:00:00.000"
    assert to_standard("令和5年12月15日", output_format="%Y/%m/%d") == "2023/12/15"
    assert to_standard("令和5年12月15日", output_format="date") == date(2023, 12, 15)

    stamp = to_standard("令和5年12月15日", output_format="datetime")
    assert stamp == datetime(2023, 12, 15, tzinfo=timezone.utc)
    assert to_standard("令和5年12月15日", output_format="datetime",
                       timezone_aware=False) == datetime(2023, 12, 15)


def test_iso_input_passes_through():
    assert to_standard("2023-12-15T00:00:00.000Z", output_format="%Y-%m-%d") == "2023-12-15"


def test_extended_era_year_converts_with_a_warning():
    # 昭和64年3月1日 never officially existed, but appears on long-dated forms.
    parsed = parse_japanese_date("昭和64年3月1日")
    assert parsed.date == date(1989, 3, 1)
    assert any("平成 1" in note for note in parsed.notes)


def test_pre_gregorian_dates_are_flagged():
    parsed = parse_japanese_date("明治3年5月5日")
    assert any("lunisolar" in note for note in parsed.notes)


@pytest.mark.parametrize("text,exc", [
    ("invalid text", InvalidEraError),
    ("", Exception),
    ("令和", InvalidDateFormatError),
    ("令和2年2月30日", InvalidDateComponentError),   # 2020 is a leap year, but 30 is not a day
    ("令和5年13月1日", InvalidDateComponentError),
    ("令和0年1月1日", InvalidDateComponentError),
])
def test_failures_raise_in_strict_mode(text, exc):
    with pytest.raises(exc):
        to_standard(text, strict=True)


@pytest.mark.parametrize("text", ["invalid text", "", "令和2年2月30日", None, 42])
def test_failures_return_default_by_default(text):
    assert to_standard(text, default_on_error="NOPE") == "NOPE"
    assert to_standard(text) == ""


def test_error_messages_say_what_was_wrong():
    with pytest.raises(InvalidDateComponentError) as info:
        to_standard("令和2年2月30日", strict=True)
    assert "February 2020" in str(info.value)
    assert "29 days" in str(info.value)
