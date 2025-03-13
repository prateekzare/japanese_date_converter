"""
Constants used throughout the Japanese date converter package.
"""

# Japanese eras with their start years in Gregorian calendar
ERA_START = {
    "明治": 1868,  # Meiji
    "大正": 1912,  # Taisho
    "昭和": 1926,  # Showa
    "平成": 1989,  # Heisei
    "令和": 2019,  # Reiwa
}

# Mapping of era names for conversion
ERA_NAMES = {
    # Japanese to English
    "明治": "Meiji",
    "大正": "Taisho",
    "昭和": "Showa",
    "平成": "Heisei",
    "令和": "Reiwa",
    
    # English to Japanese
    "meiji": "明治",
    "taisho": "大正",
    "showa": "昭和",
    "heisei": "平成",
    "reiwa": "令和",
}

# Full-width and half-width digit conversion
FW_DIGITS = "０１２３４５６７８９"
HW_DIGITS = "0123456789"

# Month names in Japanese
MONTH_NAMES_JP = {
    1: "１月", 2: "２月", 3: "３月", 4: "４月", 
    5: "５月", 6: "６月", 7: "７月", 8: "８月",
    9: "９月", 10: "１０月", 11: "１１月", 12: "１２月"
}

# Month name mapping for English to Japanese conversion
MONTH_NAMES_EN = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "jun": 6, "jul": 7, "aug": 8, "sep": 9, "sept": 9,
    "oct": 10, "nov": 11, "dec": 12
}

# Default format strings
DEFAULT_ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
DEFAULT_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"