"""
Utility functions for date conversion operations.
"""

import re
import calendar
from datetime import datetime
from typing import Dict, Optional, Any, Tuple

from ..constants import FW_DIGITS, HW_DIGITS, ERA_START, MONTH_NAMES_EN
from ..exceptions import InvalidDateComponentError

def normalize_japanese_string(text: str) -> str:
    """
    Normalize a Japanese date string by converting full-width digits to half-width
    and removing spaces and special characters.
    
    Args:
        text: The input text to normalize
        
    Returns:
        Normalized string
    """
    if not text or not isinstance(text, str):
        return ""
            
    result = text
    
    # Convert full-width to half-width digits
    for i in range(10):
        result = result.replace(FW_DIGITS[i], HW_DIGITS[i])
    
    # Remove spaces and special characters
    result = result.replace(" ", "").replace("　", "")
    result = result.replace("~", "").replace("～", "")
    
    return result.strip()


def validate_date_components(year: int, month: int, day: int) -> bool:
    """
    Validate that the date components form a valid date.
    
    Args:
        year: The year (Gregorian)
        month: The month (1-12)
        day: The day
        
    Returns:
        True if valid, False otherwise
    
    Raises:
        InvalidDateComponentError: If any component is invalid
    """
    # Validate month
    if month < 1 or month > 12:
        raise InvalidDateComponentError(f"Invalid month: {month}")
        
    # Validate day
    try:
        max_days = calendar.monthrange(year, month)[1]
    except ValueError as e:
        raise InvalidDateComponentError(f"Invalid year or month: {e}")
        
    if day < 1 or day > max_days:
        raise InvalidDateComponentError(
            f"Invalid day {day} for {year}-{month} (max: {max_days})"
        )
        
    return True


def parse_english_date(date_string: str) -> Optional[Dict[str, int]]:
    """
    Parse an English date string into components.
    
    Supports formats:
    - Month DD, YYYY
    - MM/DD/YYYY
    - YYYY-MM-DD
    - YYYY/MM/DD
    - DD Month YYYY
    
    Args:
        date_string: The English date string
        
    Returns:
        Dictionary with year, month, day or None if parsing fails
    """
    date_string = date_string.strip().lower()
    
    # Try different date formats
    patterns = [
        # MM/DD/YYYY
        r'(\d{1,2})/(\d{1,2})/(\d{4})',
        # YYYY-MM-DD or YYYY/MM/DD
        r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})',
        # Month DD, YYYY
        r'([a-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})',
        # DD Month YYYY
        r'(\d{1,2})(?:st|nd|rd|th)?\s+([a-z]+),?\s+(\d{4})'
    ]
    
    for pattern in patterns:
        match = re.match(pattern, date_string)
        if match:
            # Extract components based on the pattern
            if pattern == patterns[0]:  # MM/DD/YYYY
                month, day, year = match.groups()
                month = int(month)
                day = int(day)
                year = int(year)
            elif pattern == patterns[1]:  # YYYY-MM-DD or YYYY/MM/DD
                year, month, day = match.groups()
                year = int(year)
                month = int(month)
                day = int(day)
            elif pattern == patterns[2]:  # Month DD, YYYY
                month_name, day, year = match.groups()
                if month_name not in MONTH_NAMES_EN:
                    continue
                month = MONTH_NAMES_EN[month_name]
                day = int(day)
                year = int(year)
            elif pattern == patterns[3]:  # DD Month YYYY
                day, month_name, year = match.groups()
                if month_name not in MONTH_NAMES_EN:
                    continue
                month = MONTH_NAMES_EN[month_name]
                day = int(day)
                year = int(year)
            
            # Validate components
            try:
                validate_date_components(year, month, day)
                return {"year": year, "month": month, "day": day}
            except InvalidDateComponentError:
                continue
    
    # If all patterns fail, try datetime parser as fallback
    try:
        dt = datetime.strptime(date_string, "%Y-%m-%d")
        return {"year": dt.year, "month": dt.month, "day": dt.day}
    except ValueError:
        pass
    
    try:
        for fmt in ["%d %B %Y", "%B %d %Y", "%m/%d/%Y", "%Y/%m/%d"]:
            try:
                dt = datetime.strptime(date_string, fmt)
                return {"year": dt.year, "month": dt.month, "day": dt.day}
            except ValueError:
                continue
    except Exception:
        pass
    
    return None


def get_era_from_year(year: int) -> Tuple[str, int]:
    """
    Determine the Japanese era for a given Gregorian year.
    
    Args:
        year: Gregorian year
        
    Returns:
        Tuple of (era_name, year_in_era)
    """
    if year < min(ERA_START.values()):
        raise InvalidDateComponentError(f"Year {year} predates supported eras")
    
    # Find the most recent era that started before or in this year
    current_era = None
    for era, start_year in sorted(ERA_START.items(), key=lambda x: x[1], reverse=True):
        if year >= start_year:
            current_era = era
            year_in_era = year - start_year + 1
            break
    
    if current_era is None:
        raise InvalidDateComponentError(f"Could not determine era for year {year}")
        
    return current_era, year_in_era