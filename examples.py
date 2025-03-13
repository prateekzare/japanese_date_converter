"""
Examples for using the Japanese Date Converter.
"""

from .main import convert_date
from .converters import to_standard, to_japanese


def run_examples():
    """Run examples demonstrating package functionality."""
    print("Japanese Date Converter Examples")
    print("===============================")
    
    # Example Japanese dates
    japanese_dates = [
        "令和５年 ６月２０日",
        "令和6年1月15日",
        "平成30年12月",
        "令和６年１２月分",
        "昭和64年1月7日"
    ]
    
    print("\n1. Converting Japanese dates to ISO format:")
    for date in japanese_dates:
        result = to_standard(date)
        print(f"  {date} → {result}")
    
    print("\n2. Converting Japanese dates to custom formats:")
    date = "令和5年12月15日"
    formats = ["%Y-%m-%d", "%B %d, %Y", "%Y年%m月%d日", "%d/%m/%Y"]
    for fmt in formats:
        result = to_standard(date, output_format=fmt)
        print(f"  Format {fmt}: {result}")
    
    # Example standard dates
    standard_dates = [
        "2023-12-15",
        "December 10, 2018",
        "2024-03-22T00:00:00.000Z", 
        "15/07/2023",
        "2019-05-01"
    ]
    
    print("\n3. Converting standard dates to Japanese format:")
    for date in standard_dates:
        result = to_japanese(date)
        print(f"  {date} → {result}")
    
    print("\n4. Converting with different Japanese styles:")
    date = "2023-06-15"
    styles = ["standard", "formal", "period"]
    for style in styles:
        result = to_japanese(date, output_style=style)
        print(f"  Style '{style}': {result}")
    
    print("\n5. Using the main convert_date function with auto-detection:")
    mixed_dates = [
        "令和5年9月1日",
        "2022-10-15",
        "平成30年4月",
        "May 3, 2024"
    ]
    for date in mixed_dates:
        result = convert_date(date)
        print(f"  {date} → {result}")
    
    print("\n6. Error handling examples:")
    invalid_dates = [
        "invalid text",
        "令和99年01月01日",  # Invalid year
        "2023-13-01",       # Invalid month
        ""                  # Empty string
    ]
    for date in invalid_dates:
        result = convert_date(date, default_on_error="INVALID DATE")
        print(f"  {date} → {result}")


if __name__ == "__main__":
    run_examples()