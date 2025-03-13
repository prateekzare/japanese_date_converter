"""
Tests for the standard to Japanese date converter.
"""

import unittest
from datetime import datetime

from japanese_date_converter.converters import convert_to_japanese
from japanese_date_converter.exceptions import InvalidDateFormatError


class TestStandardToJapanese(unittest.TestCase):
    """Test suite for standard to Japanese date conversion."""
    
    def test_basic_conversion(self):
        """Test basic standard date conversion."""
        # ISO format
        self.assertEqual(
            convert_to_japanese("2023-12-15", use_full_width=False),
            "令和5年12月15日"
        )
        
        # Simple format
        self.assertEqual(
            convert_to_japanese("2023/12/15", use_full_width=False),
            "令和5年12月15日"
        )
        
        # English format
        self.assertEqual(
            convert_to_japanese("December 15, 2023", use_full_width=False),
            "令和5年12月15日"
        )
        
        # MM/DD/YYYY format
        self.assertEqual(
            convert_to_japanese("12/15/2023", use_full_width=False),
            "令和5年12月15日"
        )
        
        # Full ISO with time
        self.assertEqual(
            convert_to_japanese("2023-12-15T00:00:00.000Z", use_full_width=False),
            "令和5年12月15日"
        )
    
    def test_different_eras(self):
        """Test conversion to different Japanese eras."""
        self.assertEqual(
            convert_to_japanese("2019-05-01", use_full_width=False),
            "令和1年5月1日"
        )
        
        self.assertEqual(
            convert_to_japanese("2019-04-30", use_full_width=False),
            "平成31年4月30日"
        )
        
        self.assertEqual(
            convert_to_japanese("1989-01-07", use_full_width=False),
            "昭和64年1月7日"
        )
        
        self.assertEqual(
            convert_to_japanese("1926-12-25", use_full_width=False),
            "大正15年12月25日"
        )
        
        self.assertEqual(
            convert_to_japanese("1912-07-30", use_full_width=False),
            "明治45年7月30日"
        )
    
    def test_output_styles(self):
        """Test different Japanese output styles."""
        date_str = "2023-06-15"
        
        # Standard style
        self.assertEqual(
            convert_to_japanese(date_str, output_style="standard", use_full_width=False),
            "令和5年6月15日"
        )
        
        # Formal style
        self.assertEqual(
            convert_to_japanese(date_str, output_style="formal", use_full_width=False),
            "令和5年6月日付"
        )
        
        # Period style
        self.assertEqual(
            convert_to_japanese(date_str, output_style="period", use_full_width=False),
            "令和5年6月分"
        )
        
        # Without day
        self.assertEqual(
            convert_to_japanese(date_str, include_day=False, use_full_width=False),
            "令和5年6月"
        )
        
        # With full-width digits
        full_width = convert_to_japanese(date_str, use_full_width=True)
        self.assertIn("５", full_width)
        self.assertIn("６", full_width)
        self.assertIn("１５", full_width)
    
    def test_datetime_input(self):
        """Test conversion with datetime object input."""
        dt = datetime(2023, 12, 15)
        self.assertEqual(
            convert_to_japanese(dt.isoformat(), use_full_width=False),
            "令和5年12月15日"
        )
    
    def test_error_handling(self):
        """Test error handling."""
        # Invalid date
        self.assertEqual(
            convert_to_japanese("invalid text", default_on_error="ERROR"),
            "ERROR"
        )
        
        # Invalid format
        self.assertEqual(
            convert_to_japanese("2023-13-01", default_on_error="ERROR"),
            "ERROR"
        )
        
        # Empty string
        self.assertEqual(
            convert_to_japanese("", default_on_error="ERROR"),
            "ERROR"
        )
        
        # None value
        self.assertEqual(
            convert_to_japanese(None, default_on_error="ERROR"),
            "ERROR"
        )


if __name__ == "__main__":
    unittest.main()