"""
Functions for converting standard date formats to Japanese date formats.
"""

import re
from datetime import datetime
from typing import Dict, Optional, Union, Any

from ..constants import ERA_START, MONTH_NAMES_JP
from ..exceptions import InvalidDateFormatError, InvalidDateComponentError
from .utils import parse_english_date, get_era_from_year


class StandardToJapaneseConverter:
    """
    Converter for standard date formats to Japanese date formats.
    """
    
    def __init__(self):
        self.iso_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z$')
    
    def convert(self,
                date_string: str,
                output_style: str = "standard",
                use_full_width: bool = True,
                include_day: bool = True,
                default_on_error: Any = "") -> str:
        """
        Convert a standard date format to Japanese date format.
        
        Args:
            date_string: The standard date string
            output_style: Style of output - "standard" (年月日), "formal" (年月日付), "period" (年月分)
            use_full_width: Whether to use full-width digits
            include_day: Whether to include the day in the output (ignored for "period" style)
            default_on_error: Value to return if parsing fails
            
        Returns:
            Japanese date string or default_on_error if parsing fails
        """
        try:
            # Parse the input date string
            date_components = None
            
            # Check if it's an ISO date
            if self.iso_pattern.match(date_string):
                dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
                date_components = {"year": dt.year, "month": dt.month, "day": dt.day}
            else:
                # Try to parse as datetime object
                try:
                    dt = datetime.fromisoformat(date_string)
                    date_components = {"year": dt.year, "month": dt.month, "day": dt.day}
                except ValueError:
                    # Try other formats
                    date_components = parse_english_date(date_string)
            
            if not date_components:
                return default_on_error
                
            # Get Japanese era
            era, year_in_era = get_era_from_year(date_components["year"])
            
            # Format digits as full-width if requested
            if use_full_width:
                year_str = ''.join(['０１２３４５６７８９'[int(d)] for d in str(year_in_era)])
                month_str = MONTH_NAMES_JP[date_components["month"]]
                day_str = ''.join(['０１２３４５６７８９'[int(d)] for d in str(date_components["day"])]) + '日'
            else:
                year_str = str(year_in_era)
                month_str = str(date_components["month"]) + '月'
                day_str = str(date_components["day"]) + '日'
            
            # Build output based on style
            if output_style == "formal":
                result = f"{era}{year_str}年{month_str}{'日付' if include_day else ''}"
            elif output_style == "period":
                result = f"{era}{year_str}年{month_str}分"
            else:  # standard
                if include_day:
                    result = f"{era}{year_str}年{month_str}{day_str}"
                else:
                    result = f"{era}{year_str}年{month_str}"
                    
            return result
            
        except (InvalidDateFormatError, InvalidDateComponentError):
            return default_on_error
        except Exception:
            return default_on_error


# Function interface for easier use
def to_japanese(
    date_string: str,
    output_style: str = "standard",
    use_full_width: bool = True,
    include_day: bool = True,
    default_on_error: Any = ""
) -> str:
    """
    Convert a standard date to Japanese format.
    
    Args:
        date_string: Standard date string (e.g., "2023-12-15", "December 15, 2023")
        output_style: Style of output - "standard" (年月日), "formal" (年月日付), "period" (年月分)
        use_full_width: Whether to use full-width digits
        include_day: Whether to include the day in the output (ignored for "period" style)
        default_on_error: Value to return if parsing fails
        
    Returns:
        Japanese date string or default_on_error on failure
    """
    converter = StandardToJapaneseConverter()
    return converter.convert(
        date_string, 
        output_style, 
        use_full_width, 
        include_day,
        default_on_error
    )