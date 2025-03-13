"""
Main entry point for Japanese Date Converter.
"""

from typing import Union, Any
from datetime import datetime

from .converters import convert_to_standard, convert_to_japanese


def convert_date(
    date_string: str,
    direction: str = "auto",
    output_format: str = "iso",
    japanese_style: str = "standard",
    use_full_width: bool = True,
    include_day: bool = True,
    default_on_error: Any = "",
    timezone_aware: bool = True
) -> Union[str, datetime, Any]:
    """
    Convert between Japanese and standard date formats.
    
    Args:
        date_string: The date string to convert
        direction: "ja_to_standard", "standard_to_ja", or "auto" (detect automatically)
        output_format: For standard output - "iso", "datetime", or strftime format string
        japanese_style: For Japanese output - "standard", "formal", or "period"
        use_full_width: Whether to use full-width digits in Japanese output
        include_day: Whether to include the day in Japanese output
        default_on_error: Value to return if conversion fails
        timezone_aware: Whether to include timezone info in standard output
        
    Returns:
        Converted date in requested format or default_on_error on failure
    """
    # Detect direction if auto
    if direction == "auto":
        if any(era in date_string for era in ["明治", "大正", "昭和", "平成", "令和"]):
            direction = "ja_to_standard"
        else:
            direction = "standard_to_ja"
    
    # Perform conversion
    if direction == "ja_to_standard":
        return convert_to_standard(
            date_string, 
            output_format, 
            default_on_error, 
            timezone_aware
        )
    else:  # standard_to_ja
        return convert_to_japanese(
            date_string,
            japanese_style,
            use_full_width,
            include_day,
            default_on_error
        )