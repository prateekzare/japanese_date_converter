"""
Functions for converting Japanese date formats to standard formats.
"""

import re
from datetime import datetime, timezone
from typing import Dict, Optional, Union, Any

from ..constants import ERA_START, DEFAULT_ISO_FORMAT
from ..exceptions import InvalidDateFormatError, InvalidEraError, InvalidDateComponentError
from .utils import normalize_japanese_string, validate_date_components


class JapaneseToStandardConverter:
    """
    Converter for Japanese date formats to standard date formats.
    """
    
    def __init__(self):
        # Compiled regex patterns for performance
        self.era_pattern = re.compile(r'(明治|大正|昭和|平成|令和)')
        self.year_pattern = re.compile(r'(明治|大正|昭和|平成|令和)(\d{1,2})年')
        self.month_patterns = [
            re.compile(r'(\d{1,2})月(?!分)'),
            re.compile(r'(\d{1,2})月分')
        ]
        self.day_pattern = re.compile(r'(\d{1,2})日')
        self.iso_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z$')
    
    def parse_components(self, normalized_text: str) -> Optional[Dict[str, int]]:
        """
        Extract year, month, and day components from normalized Japanese date string.
        
        Args:
            normalized_text: Normalized Japanese date string
            
        Returns:
            Dictionary with year, month, day or None if parsing fails
            
        Raises:
            InvalidEraError: If the era is not recognized
            InvalidDateFormatError: If the date format is not recognized
        """
        # Check for Japanese era
        era_match = self.era_pattern.search(normalized_text)
        if not era_match:
            return None
            
        era = era_match.group(1)
        if era not in ERA_START:
            raise InvalidEraError(f"Unknown era: {era}")
        
        # Extract year
        year_match = self.year_pattern.search(normalized_text)
        if not year_match:
            raise InvalidDateFormatError(f"Cannot extract year from: {normalized_text}")
            
        year_in_era = int(year_match.group(2))
        gregorian_year = ERA_START[era] + year_in_era - 1
        
        # Extract month
        month = None
        for pattern in self.month_patterns:
            month_match = pattern.search(normalized_text)
            if month_match:
                month = int(month_match.group(1))
                break
                
        # Default to January if no month specified
        if month is None:
            month = 1
        
        # Extract day
        day_match = self.day_pattern.search(normalized_text)
        
        # If it's a month with 分 suffix or no day specified, use the 1st of the month
        if not day_match or '月分' in normalized_text:
            day = 1
        else:
            day = int(day_match.group(1))
        
        # Validate date components
        try:
            validate_date_components(gregorian_year, month, day)
        except InvalidDateComponentError as e:
            raise InvalidDateComponentError(f"Invalid date: {e}")
            
        return {
            "year": gregorian_year,
            "month": month,
            "day": day
        }
    
    def convert(self, 
                date_string: str,
                output_format: str = "iso",
                default_on_error: Any = "",
                timezone_aware: bool = True) -> Union[str, datetime, Any]:
        """
        Convert a Japanese date string to the specified output format.
        
        Args:
            date_string: The Japanese date string
            output_format: Output format - "iso" for ISO 8601, "datetime" for datetime object,
                           or a strftime format string like "%Y-%m-%d"
            default_on_error: Value to return if parsing fails
            timezone_aware: Whether to include timezone info (UTC) in the result
            
        Returns:
            Converted date in requested format, or default_on_error if parsing fails
        """
        try:
            if not date_string or not isinstance(date_string, str):
                return default_on_error
                
            # Check if already in ISO 8601 format
            if self.iso_pattern.match(date_string):
                if output_format == "iso":
                    return date_string
                elif output_format == "datetime":
                    # Parse ISO string to datetime
                    dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
                    return dt
                else:
                    # Format according to custom format string
                    dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
                    return dt.strftime(output_format)
            
            # Clean and normalize the input
            normalized = normalize_japanese_string(date_string)
            if not normalized:
                return default_on_error
                
            # Parse date components
            components = self.parse_components(normalized)
            if not components:
                return default_on_error
                
            # Create datetime object
            if timezone_aware:
                dt = datetime(
                    components["year"], 
                    components["month"], 
                    components["day"], 
                    0, 0, 0, 0, 
                    tzinfo=timezone.utc
                )
            else:
                dt = datetime(
                    components["year"], 
                    components["month"], 
                    components["day"], 
                    0, 0, 0, 0
                )
            
            # Return in requested format
            if output_format == "iso":
                return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + ('Z' if timezone_aware else '')
            elif output_format == "datetime":
                return dt
            else:
                return dt.strftime(output_format)
                
        except (InvalidDateFormatError, InvalidEraError, InvalidDateComponentError):
            return default_on_error
        except Exception:
            return default_on_error


# Function interface for easier use
def to_standard(
    date_string: str,
    output_format: str = "iso",
    default_on_error: Any = "",
    timezone_aware: bool = True
) -> Union[str, datetime, Any]:
    """
    Convert a Japanese date to standard format.
    
    Args:
        date_string: Japanese date string (e.g., "令和5年12月15日")
        output_format: Format to return - "iso" for ISO 8601, "datetime" for datetime object,
                      or a strftime format string like "%Y-%m-%d"
        default_on_error: Value to return if parsing fails
        timezone_aware: Whether to include timezone info in the result
        
    Returns:
        Converted date in requested format or default_on_error on failure
    """
    converter = JapaneseToStandardConverter()
    return converter.convert(date_string, output_format, default_on_error, timezone_aware)