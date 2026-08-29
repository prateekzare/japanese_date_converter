"""
Seireki (Gregorian) -> wareki (Japanese era) conversion.
"""

from datetime import date, datetime
from typing import Any, List, Union

from ..constants import KOKI_OFFSET
from ..eras import MEIJI_START, era_for_date
from ..exceptions import (
    ConfigurationError, DateConversionError, InputError, UnsupportedDateError,
)
from .utils import (
    int_to_full_width, int_to_kanji, parse_western_date, weekday_names,
)

__all__ = ["StandardToJapaneseConverter", "to_japanese", "format_wareki"]

STYLES = ("standard", "formal", "period", "kanji", "code", "romaji", "full_width")


class StandardToJapaneseConverter:
    """
    Renders a Gregorian date in Japanese era form.

    Styles:

    ==============  ==================================================
    ``standard``    令和5年12月15日
    ``full_width``  令和５年１２月１５日  (full-width digits, for forms)
    ``kanji``       令和五年十二月十五日  (formal and vertical writing)
    ``formal``      令和5年12月15日付     (dated correspondence)
    ``period``      令和5年12月分         (monthly billing statements)
    ``code``        R05.12.15             (ID cards, legacy databases)
    ``romaji``      Reiwa 5, December 15
    ==============  ==================================================

    Year 1 of an era is written 元年 (*gannen*) in every Japanese style, which
    is how it appears on real documents. Pass ``use_gannen=False`` for a plain
    numeric year if a downstream system needs an integer.
    """

    def convert(self,
                date_string: Union[str, date, datetime],
                output_style: str = "standard",
                use_full_width: bool = True,
                include_day: bool = True,
                default_on_error: Any = "",
                day_first: bool = False,
                use_gannen: bool = True,
                strict: bool = False) -> Any:
        try:
            value = self._coerce(date_string, day_first)
            return format_wareki(
                value,
                style=output_style,
                use_full_width=use_full_width,
                include_day=include_day,
                use_gannen=use_gannen,
            )
        except DateConversionError:
            if strict:
                raise
            return default_on_error
        except Exception:
            if strict:
                raise
            return default_on_error

    @staticmethod
    def _coerce(value, day_first: bool) -> date:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if not isinstance(value, str) or not value.strip():
            raise InputError("Expected a date string or date object", value)
        parsed, _notes = parse_western_date(value, day_first=day_first)
        return parsed


def format_wareki(value: date,
                  style: str = "standard",
                  use_full_width: bool = True,
                  include_day: bool = True,
                  use_gannen: bool = True) -> str:
    """
    Format a :class:`datetime.date` as a Japanese era string.

    Raises :class:`UnsupportedDateError` for dates before 明治元年
    (1868-10-23) -- earlier eras used the lunisolar calendar and changed for
    omens and disasters as well as successions, so they cannot be derived.
    """
    if style not in STYLES:
        raise ConfigurationError(
            "unknown style, expected one of {}".format(", ".join(STYLES)), style)

    era = era_for_date(value)
    if era is None:
        raise UnsupportedDateError(
            "{} predates 明治元年 ({}), the earliest era supported".format(
                value.isoformat(), MEIJI_START.isoformat()),
            value.isoformat())

    era_year = era.year_of(value)

    if style == "code":
        return "{}{:02d}.{:02d}.{:02d}".format(
            era.code, era_year, value.month, value.day)

    if style == "romaji":
        from ..constants import MONTH_NAMES_EN
        base = "{} {}".format(era.en, era_year)
        if not include_day:
            return "{}, {}".format(base, MONTH_NAMES_EN[value.month - 1])
        return "{}, {} {}".format(base, MONTH_NAMES_EN[value.month - 1], value.day)

    if style == "kanji":
        year_text = "元" if (era_year == 1 and use_gannen) else int_to_kanji(era_year)
        month_text = int_to_kanji(value.month)
        day_text = int_to_kanji(value.day)
    elif style == "full_width" or (use_full_width and style in ("standard", "formal", "period")):
        year_text = "元" if (era_year == 1 and use_gannen) else int_to_full_width(era_year)
        month_text = int_to_full_width(value.month)
        day_text = int_to_full_width(value.day)
    else:
        year_text = "元" if (era_year == 1 and use_gannen) else str(era_year)
        month_text = str(value.month)
        day_text = str(value.day)

    head = "{}{}年{}月".format(era.ja, year_text, month_text)

    if style == "period":
        # 分 marks a monthly billing period, so a day would be meaningless.
        return head + "分"
    if not include_day:
        return head
    if style == "formal":
        return "{}{}日付".format(head, day_text)
    return "{}{}日".format(head, day_text)


_CONVERTER = StandardToJapaneseConverter()


def to_japanese(date_string: Union[str, date, datetime],
                output_style: str = "standard",
                use_full_width: bool = True,
                include_day: bool = True,
                default_on_error: Any = "",
                day_first: bool = False,
                use_gannen: bool = True,
                strict: bool = False) -> Any:
    """
    Convert a standard date to Japanese era form.

    >>> to_japanese("2023-12-15", use_full_width=False)
    '令和5年12月15日'
    >>> to_japanese("2019-05-01", use_full_width=False)
    '令和元年5月1日'
    >>> to_japanese("2019-04-30", use_full_width=False)
    '平成31年4月30日'
    """
    return _CONVERTER.convert(date_string, output_style, use_full_width,
                              include_day, default_on_error, day_first,
                              use_gannen, strict)
