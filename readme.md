# Japanese Date Converter

Convert between Japanese era dates (**wareki**, 和暦) and Gregorian dates (**seireki**, 西暦), in both directions, with no dependencies.

### ▶ Try it live, no install

**<https://convertnow.tools/tools/date-time/japanese-date-converter-free/>**

Free browser version of this package — same era table, same parser, runs entirely client-side. Useful for checking a single date, or for confirming what this library will return before you wire it in.

---

## Why not just add 2018?

Every wareki cheat sheet says to add 2018 to a 令和 year. That is right about 97% of the time and wrong exactly where it matters, because **Japanese eras do not change on 1 January** — they change on the day a reign changes.

```python
>>> from japanese_date_converter import to_japanese
>>> to_japanese("2019-04-30", use_full_width=False)
'平成31年4月30日'
>>> to_japanese("2019-05-01", use_full_width=False)
'令和元年5月1日'
```

Both dates are in 2019. A start-year lookup table returns 令和 for both, which puts a lease start date, a birth date or a filing period in the wrong reign. This package stores each era as a full start and end **date** and resolves the era from the complete year-month-day.

## Installation

```bash
pip install japanese-date-converter
```

From a source checkout:

```bash
pip install .
```

## Quick start

```python
from japanese_date_converter import convert_date, to_standard, to_japanese

convert_date("令和5年12月15日", output_format="%Y-%m-%d")   # '2023-12-15'
convert_date("2023-12-15", use_full_width=False)            # '令和5年12月15日'

to_standard("R5.12.15", output_format="%Y-%m-%d")           # '2023-12-15'
to_japanese("2023-12-15", output_style="kanji")             # '令和五年十二月十五日'
```

## Features

- **Bidirectional**, with automatic direction detection
- **Exact era boundaries** — all five modern eras stored as date ranges, not start years
- **元年 (gannen)** read and written for the first year of every era
- **Every input shape** that appears in real documents: kanji, full-width, kanji numerals, ID-card codes, romaji, Unicode ligatures
- **Seven output styles** including formal, billing-period and kanji-numeral forms
- **Reported assumptions** — nothing is guessed silently
- **Error messages that say what was wrong**, not just that something was
- **A CLI** (`jpdate`) with CSV batch output
- **No runtime dependencies**, Python 3.7+

## The five eras

| Era | Romaji | Code | First day | Last day |
|-----|--------|------|-----------|----------|
| 明治 | Meiji | M | 1868-10-23 | 1912-07-30 |
| 大正 | Taishō | T | 1912-07-30 | 1926-12-25 |
| 昭和 | Shōwa | S | 1926-12-25 | 1989-01-07 |
| 平成 | Heisei | H | 1989-01-08 | 2019-04-30 |
| 令和 | Reiwa | R | 2019-05-01 | — |

Two dates appear twice. 1912-07-30 is both 明治45年7月30日 and 大正元年7月30日; 1926-12-25 is both 大正15年12月25日 and 昭和元年12月25日. Both readings occur in genuine documents. Japanese government forms resolve the overlap in favour of the newer era, and so does this package.

The 平成 transition worked differently — Emperor Akihito acceded the day *after* Emperor Shōwa's death, so 昭和64年1月7日 and 平成元年1月8日 are consecutive days sharing nothing.

## Supported input

### Japanese

| Input | Notes |
|-------|-------|
| `令和5年12月15日` | standard written form |
| `令和元年5月1日` | 元年, the first year of an era |
| `令和５年１２月１５日` | full-width digits |
| `平成三十一年四月三十日` | additive kanji numerals |
| `二〇二三年` | positional kanji numerals |
| `R5.12.15`, `H31-04-30`, `S64/1/7`, `R051215` | ID cards, legacy databases |
| `Reiwa 5/12/15`, `Shōwa 64年1月7日` | romaji, with or without macrons |
| `㋿5年12月15日` | Unicode era ligatures (㋿ ㍻ ㍼ ㍽ ㍾) |
| `令和5年12月` | month only, resolves to the 1st |
| `平成30年4月分` | monthly billing period |

### Western

ISO 8601 (`2023-12-15`, with or without a time part), `2023/12/15`, `20231215`, `December 15, 2023`, `15 Dec 2023`, `2023年12月15日`, `12/15/2023`, `2023-06` and `June 2023` (year-month, resolves to the 1st), bare `2023`, two-digit years, and `date` / `datetime` objects.

Both `to_standard` and `to_japanese` accept `date` and `datetime` objects as well as strings. Passing an already-standard string to `to_standard` re-emits it in the requested format rather than failing for having no era.

## Output styles

```python
to_japanese("2023-12-15", output_style="standard",   use_full_width=False)  # 令和5年12月15日
to_japanese("2023-12-15", output_style="full_width")                        # 令和５年１２月１５日
to_japanese("2023-12-15", output_style="kanji")                             # 令和五年十二月十五日
to_japanese("2023-12-15", output_style="formal",     use_full_width=False)  # 令和5年12月15日付
to_japanese("2023-12-15", output_style="period",     use_full_width=False)  # 令和5年12月分
to_japanese("2023-12-15", output_style="code")                              # R05.12.15
to_japanese("2023-12-15", output_style="romaji")                            # Reiwa 5, December 15
```

`use_gannen=False` gives `令和1年` instead of `令和元年` where a downstream system needs an integer.

## Western output formats

```python
to_standard("令和5年12月15日")                              # '2023-12-15T00:00:00.000Z'
to_standard("令和5年12月15日", output_format="%Y/%m/%d")    # '2023/12/15'
to_standard("令和5年12月15日", output_format="date")        # datetime.date(2023, 12, 15)
to_standard("令和5年12月15日", output_format="datetime")    # datetime(2023, 12, 15, tzinfo=utc)
to_standard("令和5年12月15日", timezone_aware=False)        # '2023-12-15T00:00:00.000'
```

## `describe()` — every form at once

```python
>>> from japanese_date_converter import describe
>>> info = describe("令和5年12月15日")
>>> info["iso"]              # '2023-12-15'
>>> info["era"], info["era_year"]
('令和', 5)
>>> info["weekday_ja"]       # '金曜日'
>>> info["koki_year"]        # 2683
>>> info["wareki"]["kanji"]  # '令和五年十二月十五日'
>>> info["notes"]            # []
```

Also returns `iso_timestamp`, `slashed`, `compact`, `us_long`, `eu_long`, `gregorian_ja`, `weekday_en`, `day_of_year`, `iso_week`, `era_en` and `era_span`.

The 皇紀 (*kōki*) figure is the imperial year count from the legendary founding in 660 BC — which is why 2023 is 皇紀2683年, and why the Mitsubishi Zero, designed in 皇紀2600, was the "Type Zero".

## Assumptions are reported, never silent

```python
>>> describe("5/6/2023")["notes"]
["'5/6' has two valid readings. Read as month/day; pass day_first=True for the other one."]

>>> describe("令和5年")["notes"]
['Month and/or day were missing, so the 1st was assumed.']

>>> describe("昭和64年3月1日")["notes"]
['昭和 ended on 1989-01-07. This date was really 平成 1. Extended era years do
  appear on long-dated forms, so the conversion is still shown.']

>>> describe("明治3年5月5日")["notes"]
['Japan adopted the Gregorian calendar on 1873-01-01. Before that official
  dates were lunisolar, so this mapping is approximate.']
```

`昭和64年3月1日` never officially existed — 昭和64年 lasted seven days. Long-dated contracts and pre-printed forms carry extended era years anyway, so the date is converted **and** flagged, rather than refused.

## Errors

By default a failure returns `default_on_error` (an empty string), matching 1.x. Pass `strict=True` to raise instead:

```python
>>> to_standard("令和2年2月30日", default_on_error="N/A")
'N/A'
>>> to_standard("令和2年2月30日", strict=True)
InvalidDateComponentError: Invalid date component: February 2020 has only 29 days,
so day 30 does not exist: day=30
```

| Exception | Raised when |
|-----------|-------------|
| `InvalidEraError` | no era found, or an unknown one |
| `InvalidDateFormatError` | no pattern matched the string |
| `InvalidDateComponentError` | the year/month/day is not a real date |
| `UnsupportedDateError` | the date predates 明治元年 (1868-10-23) |
| `AmbiguousDateError` | two valid readings, under strict handling |
| `InputError` | wrong type, or empty |

All inherit from `DateConversionError`.

## Batch conversion

```python
>>> from japanese_date_converter import convert_many
>>> rows = convert_many(["令和5年12月15日", "1989-01-07", "R2.1.1", "banana"])
>>> rows[-1]["error"]
'Invalid era: No Japanese era found...'
```

Direction is detected per row, so wareki and Gregorian can be mixed in one list. Failed rows come back with an `error` rather than being dropped.

## Command line

```bash
jpdate 令和5年12月15日                  # 2023-12-15
jpdate 2019-05-01 --style kanji        # 令和元年五月一日
jpdate --all 1989-01-07                # every derived form
jpdate --file dates.txt --csv > out.csv
jpdate --today --all
```

## Limits

- **No pre-Meiji eras.** Edo-period eras changed for earthquakes, comets and auspicious omens as well as successions, and mapping them needs a lunisolar almanac rather than a formula. Gregorian output still works; era fields come back `None`.
- **Dates before 1873-01-01 are approximate.** Japan ran on the lunisolar 天保暦 calendar until 明治5年12月3日 was redesignated 1873-01-01.
- **No future eras.** If a sixth era is announced, this package returns 令和 for dates past that boundary until the era table is updated — a limitation shared by every wareki converter, spreadsheet formula and government system.

## Development

```bash
python -m venv .venv
.venv/Scripts/activate          # Windows;  source .venv/bin/activate elsewhere
pip install -e ".[dev]"
pytest
```

### Reinstalling into an existing venv

A plain `pip install .` over an existing install is unreliable — pip serves a cached wheel when the version number has not changed, and editable installs leave a `.pth` or `__editable__` finder behind that keeps the old source tree importable. The scripts in `scripts/` handle both:

```powershell
# Windows PowerShell
.\scripts\reinstall.ps1                                     # uses .venv
.\scripts\reinstall.ps1 -Venv C:\projects\app\.venv -Test
.\scripts\reinstall.ps1 -Editable                           # pip install -e .
```

```bash
# Linux, macOS, Git Bash
./scripts/reinstall.sh
./scripts/reinstall.sh --venv ~/projects/app/.venv --test
./scripts/reinstall.sh --editable
```

Both scripts uninstall under both the hyphen and underscore spellings, delete leftover editable-install artefacts, warn if the module is still importable from somewhere outside site-packages, reinstall with `--no-cache-dir --force-reinstall`, then verify by converting the two 2019 boundary dates.

Manual equivalent:

```bash
pip uninstall -y japanese-date-converter japanese_date_converter
pip install --no-cache-dir --force-reinstall .
python -c "import japanese_date_converter as j; print(j.__version__, j.to_japanese('2019-05-01', use_full_width=False))"
```

## Upgrading from 1.x

**2.0 is a drop-in replacement.** `to_standard`, `to_japanese`, `convert_date`, both
converter classes and the whole exception hierarchy keep their 1.x names, positional
argument order and default values. Every new argument is keyword-with-default. Failures
still return `default_on_error` unless you opt into `strict=True`.

`tests/test_v1_compatibility.py` pins every example from the 1.x README so this cannot
regress.

### Two documented outputs deliberately changed

| Call | 1.x printed | 2.0 prints | Why |
|------|-------------|-----------|-----|
| `to_japanese("2023-06-15", output_style="formal")` | `令和５年６月日付` | `令和５年６月１５日付` | 1.x dropped the day, producing a 年月日付 string with no 日 value. Use `include_day=False` if you want the day gone. |
| `to_standard("令和07年01月23日")` | *README said* `2023-01-23` | `2025-01-23` | The README was wrong. 令和 began in 2019, so 令和7年 is 2025; 2023 is 令和5年. 1.x returned 2025 here too. |

### Things the 1.x README documented but 1.x did not do

- `convert_date("2023-06", japanese_style="period")` returned the error default, because
  there was no year-month parsing pattern. It now returns `令和５年６月分`.
- `from japanese_date_converter import convert_date` raised `ImportError` — `convert_date`
  was never in `__all__`, despite being the first line of the Quick Start.
- Calling `convert_date` at all raised `NameError`: it dispatched to
  `convert_to_standard` / `convert_to_japanese`, neither of which existed.

### What else is new

- Eras are date ranges, not start years — fixes wrong results across all five transitions
- 元年, kanji numerals, era ligatures, ID-card codes and romaji era names are all parsed
- `strict=` raises instead of silently returning a default
- `describe()`, `convert_many()`, `parse_western_date()`, `format_wareki()`, the era table
  API and the `jpdate` CLI
- `get_era_from_year(year, month, day)` — the month and day are optional, but they are the
  only way to be right across a transition
- All arithmetic uses `datetime.date`, so no timezone can shift a date across an era boundary

## License

MIT

## Contributing

Pull requests welcome. New parsing cases are especially useful — if you have a date format from a real Japanese document that this fails on, please open an issue with the string.
