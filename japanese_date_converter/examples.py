"""
Runnable examples:  python -m japanese_date_converter.examples
"""

from .converters import to_japanese, to_standard
from .main import convert_date, describe


def _section(title):
    print("\n" + title)
    print("-" * len(title))


def run_examples():
    print("Japanese Date Converter examples")
    print("=" * 32)

    _section("1. Wareki -> Gregorian, in every input shape")
    for item in [
        "令和5年12月15日",
        "令和元年5月1日",
        "平成三十一年四月三十日",
        "令和５年１２月１５日",
        "R5.12.15",
        "H31-04-30",
        "㋿5年12月15日",
        "Reiwa 5/12/15",
        "平成30年4月分",
    ]:
        print("  {:<24} -> {}".format(item, to_standard(item, output_format="%Y-%m-%d")))

    _section("2. Gregorian -> wareki, in every output style")
    for style in ["standard", "full_width", "kanji", "formal", "period", "code", "romaji"]:
        print("  {:<12} {}".format(
            style, to_japanese("2023-12-15", output_style=style, use_full_width=False)))

    _section("3. The era boundaries a start-year table gets wrong")
    for item in ["1989-01-07", "1989-01-08", "2019-04-30", "2019-05-01",
                 "1926-12-25", "1912-07-30"]:
        print("  {} -> {}".format(item, to_japanese(item, use_full_width=False)))

    _section("4. 元年 (gannen), the first year of an era")
    for item in ["2019-05-01", "1989-01-08", "1926-12-25"]:
        print("  {} -> {}".format(item, to_japanese(item, use_full_width=False)))

    _section("5. Automatic direction detection")
    for item in ["令和5年9月1日", "2022-10-15", "R2.1.1", "May 3, 2024"]:
        print("  {:<16} -> {}".format(
            item, convert_date(item, output_format="%Y-%m-%d", use_full_width=False)))

    _section("6. Assumptions and warnings are reported, not hidden")
    for item in ["昭和64年3月1日", "5/6/2023", "令和5年", "1870-05-05"]:
        info = describe(item)
        print("  {} -> {}".format(item, info["iso"]))
        for note in info["notes"]:
            print("      ! " + note)

    _section("7. Errors say what was wrong")
    for item in ["invalid text", "令和2年2月30日", "2023-13-01", "令和0年1月1日"]:
        print("  {:<16} -> {}".format(
            item, convert_date(item, default_on_error="(could not convert)")))

    _section("8. Everything at once")
    info = describe("令和5年12月15日")
    for key in ["iso", "era", "era_year", "weekday_ja", "koki_year"]:
        print("  {:<12} {}".format(key, info[key]))
    for name, value in info["wareki"].items():
        print("  {:<12} {}".format(name, value))


if __name__ == "__main__":
    run_examples()
