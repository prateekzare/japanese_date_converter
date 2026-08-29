"""
Era table and boundary resolution.

These are the tests that a start-year lookup table fails.
"""

from datetime import date

import pytest

from japanese_date_converter import ERAS, era_for_date, find_era
from japanese_date_converter.eras import MEIJI_START


@pytest.mark.parametrize("day,expected", [
    # Showa -> Heisei: consecutive days, no shared date.
    (date(1989, 1, 7), "昭和"),
    (date(1989, 1, 8), "平成"),
    # Heisei -> Reiwa: abdication, mid-year.
    (date(2019, 4, 30), "平成"),
    (date(2019, 5, 1), "令和"),
    # Taisho -> Showa and Meiji -> Taisho share a boundary day; the newer
    # era wins, which is the convention on government forms.
    (date(1926, 12, 25), "昭和"),
    (date(1926, 12, 24), "大正"),
    (date(1912, 7, 30), "大正"),
    (date(1912, 7, 29), "明治"),
    (MEIJI_START, "明治"),
])
def test_era_boundaries(day, expected):
    era = era_for_date(day)
    assert era is not None
    assert era.ja == expected


def test_before_meiji_is_unsupported():
    assert era_for_date(date(1868, 10, 22)) is None
    assert era_for_date(date(1600, 1, 1)) is None


def test_a_single_year_can_hold_two_eras():
    assert era_for_date(date(1989, 1, 1)).ja == "昭和"
    assert era_for_date(date(1989, 12, 31)).ja == "平成"
    assert era_for_date(date(2019, 1, 1)).ja == "平成"
    assert era_for_date(date(2019, 12, 31)).ja == "令和"


def test_era_year_counts_from_one():
    era = era_for_date(date(2019, 5, 1))
    assert era.year_of(date(2019, 5, 1)) == 1
    assert era.year_of(date(2023, 12, 15)) == 5


def test_showa_64_lasted_seven_days():
    showa = find_era("昭和")
    assert showa.end == date(1989, 1, 7)
    assert showa.year_of(showa.end) == 64


@pytest.mark.parametrize("token,expected", [
    ("令和", "令和"), ("reiwa", "令和"), ("Reiwa", "令和"), ("R", "令和"), ("㋿", "令和"),
    ("昭和", "昭和"), ("showa", "昭和"), ("shouwa", "昭和"), ("shōwa", "昭和"), ("S", "昭和"),
    ("大正", "大正"), ("taisho", "大正"), ("taishō", "大正"), ("T", "大正"),
    ("Heisei", "平成"), ("H", "平成"), ("meiji", "明治"), ("M", "明治"),
])
def test_find_era_accepts_every_spelling(token, expected):
    era = find_era(token)
    assert era is not None and era.ja == expected


def test_find_era_rejects_nonsense():
    assert find_era("banana") is None
    assert find_era("") is None
    assert find_era(None) is None


def test_eras_are_contiguous_and_ordered_newest_first():
    assert [e.ja for e in ERAS] == ["令和", "平成", "昭和", "大正", "明治"]
    assert ERAS[0].end is None
    for newer, older in zip(ERAS, ERAS[1:]):
        # Each era starts on, or the day after, the previous one's end.
        assert (newer.start - older.end).days in (0, 1)
