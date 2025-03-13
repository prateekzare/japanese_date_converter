"""
Tests for the Japanese to standard date converter.
"""

import unittest
from datetime import datetime, timezone

from japanese_date_converter.converters import convert_to_standard
from japanese_date_converter.exceptions import InvalidDateFormatError


class TestJapaneseToStandard(unittest.TestCase):
    """Test suite for Japanese to standard date conversion."""
    
    def test_basic_conversion(self):
        """Test basic Japanese date conversion."""
        # Standard format
        self.assertEqual(
            convert_to_standard("令和5年12月15日", output_format="%Y-%m-%d"),
            "2023-12-15"
        )
        
        # With full-width digits
        self.assertEqual(
            convert_to_standard("令和５年１２月１５日", output_format="%Y-%m-%d"),
            "2023-12-15"
        )
        
        # With spaces
        self.assertEqual(
            convert_to_standard("令和 5 年 12 月 15 日", output_format="%Y-%m-%d"),
            "2023-12-15"
        )
    
    def test_different_eras(self):
        """Test conversion with different Japanese eras."""
        self.assertEqual(
            convert_to_standard("令和1年5月1日", output_format="%Y-%m-%d"),
            "2019-05-01"
        )
        
        self.assertEqual(
            convert_to_standard("平成31年4月30日", output_format="%Y-%m-%d"),
            "2019-04-30"
        )
        
        self.assertEqual(
            convert_to_standard("昭和64年1月7日", output_format="%Y-%m-%d"),
            "1989-01-07"
        )
        
        self.assertEqual(
            convert_to_standard("大正15年12月25日", output_format="%Y-%m-%d"),
            "1926-12-25"
        )
        
        self.assertEqual(
            convert_to_standard("明治45年7月30日", output_format="%Y-%m-%d"),
            "1912-07-30"
        )
    
    def test_partial_dates(self):
        """Test conversion with partial dates (missing day or month)."""
        # Year and month only
        self.assertEqual(
            convert_to_standard("令和5年12月", output_format="%Y-%m-%d"),
            "2023-12-01"
        )
        
        # Month with 分 suffix
        self.assertEqual(
            convert_to_standard("令和5年12月分", output_format="%Y-%m-%d"),
            "2023-12-01"
        )
        
        # Year only (should default to January 1)
        self.assertEqual(
            convert_to_standard("令和5年", output_format="%Y-%m-%d"),
            "2023-01-01"
        )
    
    def test_output_formats(self):
        """Test different output formats."""
        date_str = "令和5年12月15日"
        
        # ISO format
        iso_result = convert_to_standard(date_str, output_format="iso")
        self.assertTrue(iso_result.startswith("2023-12-15T"))
        self.assertTrue(iso_result.endswith("Z"))
        
        # Custom format
        self.assertEqual(
            convert_to_standard(date_str, output_format="%Y/%m/%d"),
            "2023/12/15"
        )
        
        self.assertEqual(
            convert_to_standard(date_str, output_format="%B %d, %Y"),
            "December 15, 2023"
        )
        
        # Datetime object
        dt_result = convert_to_standard(date_str, output_format="datetime")
        self.assertIsInstance(dt_result, datetime)
        self.assertEqual(dt_result.year, 2023)
        self.assertEqual(dt_result.month, 12)
        self.assertEqual(dt_result.day, 15)
        
        # Timezone aware
        dt_tz = convert_to_standard(date_str, output_format="datetime", timezone_aware=True)
        self.assertEqual(dt_tz.tzinfo, timezone.utc)
        
        # Non-timezone aware
        dt_no_tz = convert_to_standard(date_str, output_format="datetime", timezone_aware=False)
        self.assertIsNone(dt_no_tz.tzinfo)
    
    def test_error_handling(self):
        """Test error handling."""
        # Invalid date
        self.assertEqual(
            convert_to_standard("invalid text", default_on_error="ERROR"),
            "ERROR"
        )
        
        # Invalid month
        self.assertEqual(
            convert_to_standard("令和5年13月1日", default_on_error="ERROR"),
            "ERROR"
        )
        
        # Invalid day
        self.assertEqual(
            convert_to_standard("令和5年2月30日", default_on_error="ERROR"),
            "ERROR"
        )
        
        # Empty string
        self.assertEqual(
            convert_to_standard("", default_on_error="ERROR"),
            "ERROR"
        )
        
        # None value
        self.assertEqual(
            convert_to_standard(None, default_on_error="ERROR"),
            "ERROR"
        )


if __name__ == "__main__":
    unittest.main()