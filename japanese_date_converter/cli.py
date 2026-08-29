"""
Command line interface.

    $ jpdate 令和5年12月15日
    $ jpdate 2019-05-01 --style kanji
    $ jpdate --all 1989-01-07
    $ jpdate --file dates.txt --csv > converted.csv
"""

import argparse
import csv
import sys
from datetime import date

from . import __version__
from .exceptions import DateConversionError
from .main import convert_date, convert_many, describe

CSV_COLUMNS = ["input", "iso", "wareki", "code", "weekday_en", "note"]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jpdate",
        description="Convert between Japanese era dates (wareki) and "
                    "Gregorian dates (seireki).",
        epilog="Browser version: "
               "https://convertnow.tools/tools/date-time/japanese-date-converter-free/",
    )
    parser.add_argument("dates", nargs="*", help="dates to convert")
    parser.add_argument("-f", "--file",
                        help="read dates from a file, one per line ('-' for stdin)")
    parser.add_argument("-s", "--style", default="standard",
                        choices=["standard", "full_width", "kanji", "formal",
                                 "period", "code", "romaji"],
                        help="Japanese output style (default: standard)")
    parser.add_argument("-o", "--output-format", default="%Y-%m-%d",
                        help="strftime pattern for Western output "
                             "(default: %%Y-%%m-%%d)")
    parser.add_argument("-a", "--all", action="store_true",
                        help="print every derived form instead of one line")
    parser.add_argument("--csv", action="store_true",
                        help="emit CSV (implies batch mode)")
    parser.add_argument("--day-first", action="store_true",
                        help="read ambiguous numeric dates as day/month")
    parser.add_argument("--today", action="store_true",
                        help="use today's date")
    parser.add_argument("-V", "--version", action="version",
                        version="japanese-date-converter " + __version__)
    return parser


def _collect(args) -> list:
    items = list(args.dates)
    if args.today:
        items.append(date.today().isoformat())
    if args.file:
        stream = sys.stdin if args.file == "-" else open(args.file, encoding="utf-8")
        try:
            items.extend(line.strip() for line in stream if line.strip())
        finally:
            if stream is not sys.stdin:
                stream.close()
    return items


def _print_all(item, day_first):
    info = describe(item, day_first=day_first)
    print(info["iso"], "  ({} / {})".format(info["weekday_en"], info["weekday_ja"]))
    if info["wareki"]:
        print("  era        {} ({}) {}".format(
            info["era"], info["era_en"], info["era_year"]))
        for name, value in info["wareki"].items():
            print("  {:<11}{}".format(name, value))
    print("  koki       皇紀{}年".format(info["koki_year"]))
    print("  day/week   day {} of year, ISO week {}".format(
        info["day_of_year"], info["iso_week"]))
    for note in info["notes"]:
        print("  ! " + note)


def main(argv=None) -> int:
    args = _build_parser().parse_args(argv)
    items = _collect(args)

    if not items:
        _build_parser().print_help()
        return 2

    if args.csv:
        writer = csv.DictWriter(sys.stdout, fieldnames=CSV_COLUMNS,
                                lineterminator="\n")
        writer.writeheader()
        for row in convert_many(items, day_first=args.day_first):
            if row.get("error"):
                writer.writerow({"input": row["input"], "note": row["error"]})
                continue
            wareki = row.get("wareki") or {}
            writer.writerow({
                "input": row["input"],
                "iso": row["iso"],
                "wareki": wareki.get("standard", ""),
                "code": wareki.get("code", ""),
                "weekday_en": row["weekday_en"],
                "note": row["notes"][0] if row["notes"] else "",
            })
        return 0

    exit_code = 0
    for item in items:
        try:
            if args.all:
                _print_all(item, args.day_first)
            else:
                result = convert_date(
                    item,
                    output_format=args.output_format,
                    japanese_style=args.style,
                    use_full_width=(args.style == "full_width"),
                    day_first=args.day_first,
                    strict=True,
                )
                print(result)
        except DateConversionError as exc:
            print("{}: {}".format(item, exc.message), file=sys.stderr)
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
