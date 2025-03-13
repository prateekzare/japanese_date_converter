# Japanese Date Converter

A comprehensive Python library for converting dates between Japanese and standard formats.

## Features

- **Bidirectional Conversion**: Convert between Japanese date formats and standard formats
- **Multiple Japanese Eras**: Support for Meiji (明治), Taisho (大正), Showa (昭和), Heisei (平成), and Reiwa (令和)
- **Flexible Output Formats**: ISO 8601, custom format strings, datetime objects
- **Japanese Style Options**: Standard (年月日), formal (年月日付), period (年月分)
- **Full-width Digit Support**: Handle both half-width and full-width digits
- **Robust Error Handling**: Configurable error responses
- **Lightweight**: No external dependencies required

## Installation

```bash
pip install japanese-date-converter
```

## Quick Start

```python
from japanese_date_converter import convert_date

# Japanese to standard (auto-detected)
print(convert_date("令和5年12月15日"))  # 2023-12-15T00:00:00.000Z

# Standard to Japanese (auto-detected)
print(convert_date("2024-07-01"))  # 令和６年７月１日

# Specify output format for standard dates
print(convert_date("令和5年12月15日", output_format="%Y/%m/%d"))  # 2023/12/15

# Specify Japanese style
print(convert_date("2023-06-15", japanese_style="formal"))  # 令和５年６月日付
print(convert_date("2023-06", japanese_style="period"))    # 令和５年６月分
```

## Detailed Usage

### Converting Japanese Dates to Standard Formats

```python
from japanese_date_converter import convert_to_standard

# Basic conversion to ISO 8601
iso_date = convert_to_standard("令和5年12月15日")
print(iso_date)  # 2023-12-15T00:00:00.000Z

# Get a datetime object
from datetime import datetime
dt = convert_to_standard("令和6年3月1日", output_format="datetime")
print(dt)  # 2024-03-01 00:00:00+00:00
print(dt.year, dt.month, dt.day)  # 2024 3 1

# Custom output format
formatted = convert_to_standard("令和5年12月分", output_format="%Y/%m/%d")
print(formatted)  # 2023/12/01

# Without timezone information
local_date = convert_to_standard("平成30年1月1日", 
                                output_format="%Y-%m-%d", 
                                timezone_aware=False)
print(local_date)  # 2018-01-01

# Custom value on error
result = convert_to_standard("invalid text", default_on_error="INVALID DATE")
print(result)  # INVALID DATE
```

### Converting Standard Dates to Japanese Format

```python
from japanese_date_converter import convert_to_japanese

# Basic conversion
jp_date = convert_to_japanese("2023-12-15")
print(jp_date)  # 令和５年１２月１５日

# Different styles
standard = convert_to_japanese("2023-06-15", output_style="standard")
print(standard)  # 令和５年６月１５日

formal = convert_to_japanese("2023-06-15", output_style="formal")
print(formal)    # 令和５年６月日付

period = convert_to_japanese("2023-06-15", output_style="period")
print(period)    # 令和５年６月分

# Using half-width digits
half_width = convert_to_japanese("2023-06-15", use_full_width=False)
print(half_width)  # 令和5年6月15日

# Without day
no_day = convert_to_japanese("2023-06-15", include_day=False)
print(no_day)    # 令和５年６月
```

### Automatic Direction Detection

```python
from japanese_date_converter import convert_date

# Auto-detect and convert
jp_to_std = convert_date("令和5年12月15日")  # Japanese to Standard
print(jp_to_std)  # 2023-12-15T00:00:00.000Z

std_to_jp = convert_date("2023-12-15")  # Standard to Japanese
print(std_to_jp)  # 令和５年１２月１５日
```

## Supported Date Formats

### Japanese Input Formats

- `令和5年12月15日` (standard)
- `令和６年 ７月２５日` (with full-width numbers and spaces)
- `令和07年01月23日` (with zero-padded numbers)
- `令和5年12月` (year and month only)
- `令和６年１２月分` (month period format)

### Standard Input Formats

- ISO 8601: `2023-12-15T00:00:00.000Z`
- Common formats: `2023-12-15`, `12/15/2023`, `December 15, 2023`
- Various datetime objects

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.