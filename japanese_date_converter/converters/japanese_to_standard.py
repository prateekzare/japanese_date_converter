"""
Wareki (Japanese era) -> seireki (Gregorian) conversion.
"""

import re
from datetime import date, datetime, timezone
from typing import Any, List, Optional, Tuple, Union

from ..eras import Era, GREGORIAN_ADOPTED, find_era
from ..exceptions import (
    DateConversionError, InvalidDateComponentError,
    InvalidDateFormatError, InvalidEraError, InputError,
)
from .utils import normalize_japanese_string, validate_date_components

__all__ = ["JapaneseToStandardConverter", "to_standard", "parse_japanese_date"]


class ParsedJapaneseDate:
    """The result of parsing a wareki string."""

    __slots__ = ("date", "era", "era_year", "notes")

    def __init__(self, value: date, era: Era, era_year: int, notes: List[str]):
        self.date = value
        self.era = era
        self.era_year = era_year
        self.notes = notes

    def __repr__(self):
        return "<ParsedJapaneseDate {} = {}{}>".format(
            self.date.isoformat(), self.era.ja, self.era_year)


class JapaneseToStandardConverter:
    """
    Parses Japanese era dates in every shape that turns up in real documents.

    Accepted input:

    * ``令和5年12月15日`` -- the standard written form
    * ``令和元年5月1日`` -- 元年 (gannen), the first year of an era
    * ``平成三十一年四月三十日`` -- kanji numerals, additive or positional
    * ``令和５年１２月１５日`` -- full-width digits
    * ``R5.12.15`` / ``H31-04-30`` / ``S64/1/7`` / ``R051215`` -- ID-card codes
    * ``Reiwa 5/12/15`` / ``Heisei 31年4月30日`` -- romanised era names
    * ``㋿5年12月15日`` -- Unicode era ligatures
    * ``平成30年4月分`` -- billing-period form, resolves to the 1st
    """

    # 元年 is written for year 1 of every era; normalise it before matching.
    _GANNEN = re.compile(r"元年")

    _ERA_KANJI = re.compile(r"^(明治|大正|昭和|平成|令和)\s*(.*)$")
    _ERA_ROMAJI = re.compile(
        r"^(meiji|taisho|taishou|taishō|showa|shouwa|shōwa|heisei|reiwa)"
        r"[.\s]*(.*)$", re.IGNORECASE)
    _ERA_CODE = re.compile(r"^([MTSHR])\.?\s*(\d.*)$", re.IGNORECASE)

    # 5年12月15日, with month and day both optional, plus the trailing
    # markers that appear on forms (分 monthly period, 度 fiscal, 付 dated).
    _YMD_MARKED = re.compile(
        r"^(\d{1,3})\s*年\s*(?:(\d{1,2})\s*月\s*(?:(\d{1,2})\s*日?)?)?"
        r"(?:分|度|付|頃|ごろ)?$")
    _YMD_SEP = re.compile(r"^(\d{1,3})[.\-/](\d{1,2})(?:[.\-/](\d{1,2}))?$")
    _YMD_PACKED = re.compile(r"^(\d{2})(\d{2})(\d{2})$")
    _YEAR_ONLY = re.compile(r"^(\d{1,3})$")

    # An already-standard string: a bare ISO date, or one with a time part.
    # These are passed through and re-emitted in the requested shape rather
    # than rejected for having no era.
    _ISO = re.compile(
        r"^(\d{4})-(\d{2})-(\d{2})"
        r"(?:[T ]\d{2}:\d{2}(?::\d{2})?(?:\.\d{1,6})?(?:Z|[+-]\d{2}:?\d{2})?)?$")

    # ---------------------------------------------------------------- parse
    def parse(self, date_string: str) -> ParsedJapaneseDate:
        """
        Parse a wareki string into a real date.

        Raises :class:`InvalidEraError`, :class:`InvalidDateFormatError` or
        :class:`InvalidDateComponentError` with a message explaining the
        failure. Non-fatal observations come back in ``.notes``.
        """
        if not date_string or not isinstance(date_string, str):
            raise InputError("Expected a non-empty date string", date_string)

        text = normalize_japanese_string(date_string)
        if not text:
            raise InvalidDateFormatError("Nothing left to parse after normalising",
                                         date_string)
        text = self._GANNEN.sub("1年", text)

        era_token, rest = self._split_era(text)
        if era_token is None:
            raise InvalidEraError(
                "No Japanese era found. Start with 令和 / 平成 / 昭和 / 大正 / 明治, "
                "a romanised name, or a code like R5.12.15", date_string)

        era = find_era(era_token)
        if era is None:
            raise InvalidEraError("Unknown era", era_token)

        rest = (rest or "").strip()
        if not rest:
            raise InvalidDateFormatError(
                "Found the era {} but no year after it".format(era.ja), date_string)

        era_year, month, day, partial = self._split_ymd(rest, date_string)

        if era_year < 1:
            raise InvalidDateComponentError(
                "era years start at 1 (or 元年)", "era_year", era_year)

        notes: List[str] = []
        if partial:
            notes.append("Month and/or day were missing, so the 1st was assumed.")

        year = era.gregorian_year(era_year)
        validate_date_components(year, month, day)
        value = date(year, month, day)

        notes.extend(self._boundary_notes(era, era_year, value))
        return ParsedJapaneseDate(value, era, era_year, notes)

    def _split_era(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        for pattern in (self._ERA_KANJI, self._ERA_ROMAJI, self._ERA_CODE):
            match = pattern.match(text)
            if match:
                return match.group(1), match.group(2)
        return None, None

    def _split_ymd(self, rest: str, original: str):
        match = self._YMD_MARKED.match(rest)
        if match:
            year = int(match.group(1))
            month = int(match.group(2)) if match.group(2) else None
            day = int(match.group(3)) if match.group(3) else None
        else:
            match = self._YMD_SEP.match(rest)
            if match:
                year = int(match.group(1))
                month = int(match.group(2))
                day = int(match.group(3)) if match.group(3) else None
            else:
                match = self._YMD_PACKED.match(rest)
                if match:
                    year, month, day = (int(g) for g in match.groups())
                else:
                    match = self._YEAR_ONLY.match(rest)
                    if not match:
                        raise InvalidDateFormatError(
                            "Could not read the year/month/day, try 令和5年12月15日 "
                            "or R5.12.15", original)
                    year, month, day = int(match.group(1)), None, None

        partial = month is None or day is None
        return year, month or 1, day or 1, partial

    @staticmethod
    def _boundary_notes(era: Era, era_year: int, value: date) -> List[str]:
        """
        Flag era years that fall outside the era's real span.

        These are not errors. 昭和64年 lasted seven days, but long-dated
        contracts and pre-printed forms carry extended era years well past the
        transition, so the conversion is returned with an explanation rather
        than refused.
        """
        notes: List[str] = []
        if value < era.start:
            notes.append(
                "{} {} began on {}, so this date falls before the era actually "
                "started; the previous era was still in use.".format(
                    era.ja, era_year, era.start.isoformat()))
        elif era.end is not None and value > era.end:
            actual = None
            from ..eras import era_for_date
            real = era_for_date(value)
            if real is not None:
                actual = "{} {}".format(real.ja, real.year_of(value))
            notes.append(
                "{} ended on {}. This date was really {}. Extended era years do "
                "appear on long-dated forms, so the conversion is still shown.".format(
                    era.ja, era.end.isoformat(), actual or "in a later era"))
        if value < GREGORIAN_ADOPTED:
            notes.append(
                "Japan adopted the Gregorian calendar on 1873-01-01. Before that "
                "official dates were lunisolar, so this mapping is approximate.")
        return notes

    # -------------------------------------------------------------- convert
    def convert(self,
                date_string: str,
                output_format: str = "iso",
                default_on_error: Any = "",
                timezone_aware: bool = True,
                strict: bool = False) -> Union[str, datetime, date, Any]:
        """
        Convert a wareki string to a standard format.

        Args:
            date_string: the Japanese date.
            output_format: ``"iso"``, ``"datetime"``, ``"date"``, or any
                strftime pattern such as ``"%Y/%m/%d"``.
            default_on_error: returned when parsing fails and ``strict`` is
                False.
            timezone_aware: attach UTC to datetime output and the trailing Z
                to ISO output.
            strict: raise instead of returning ``default_on_error``.
        """
        try:
            # date/datetime objects are already standard; just re-emit them in
            # the requested shape, so to_standard mirrors to_japanese in what
            # it will accept.
            if isinstance(date_string, datetime):
                return self._format(date_string.date(), output_format, timezone_aware)
            if isinstance(date_string, date):
                return self._format(date_string, output_format, timezone_aware)

            if isinstance(date_string, str):
                iso_match = self._ISO.match(date_string.strip())
                if iso_match:
                    year, month, day = (int(g) for g in iso_match.groups())
                    validate_date_components(year, month, day)
                    return self._format(date(year, month, day),
                                        output_format, timezone_aware)

            parsed = self.parse(date_string)
            return self._format(parsed.date, output_format, timezone_aware)

        except DateConversionError:
            if strict:
                raise
            return default_on_error
        except Exception as exc:  # unexpected, still honour the contract
            if strict:
                raise
            return default_on_error

    @staticmethod
    def _format(value: date, output_format: str, timezone_aware: bool):
        if output_format == "date":
            return value
        if output_format == "datetime":
            tz = timezone.utc if timezone_aware else None
            return datetime(value.year, value.month, value.day, tzinfo=tz)
        if output_format == "iso":
            return "{}T00:00:00.000{}".format(
                value.isoformat(), "Z" if timezone_aware else "")
        return value.strftime(output_format)


_CONVERTER = JapaneseToStandardConverter()


def parse_japanese_date(date_string: str) -> ParsedJapaneseDate:
    """Parse a wareki string, raising on failure. See the converter class."""
    return _CONVERTER.parse(date_string)


def to_standard(date_string: str,
                output_format: str = "iso",
                default_on_error: Any = "",
                timezone_aware: bool = True,
                strict: bool = False) -> Union[str, datetime, date, Any]:
    """
    Convert a Japanese era date to a standard format.

    >>> to_standard("令和5年12月15日", output_format="%Y-%m-%d")
    '2023-12-15'
    >>> to_standard("R5.12.15", output_format="%Y-%m-%d")
    '2023-12-15'
    """
    return _CONVERTER.convert(date_string, output_format, default_on_error,
                              timezone_aware, strict)
