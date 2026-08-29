"""
Exception hierarchy for the Japanese date converter.

Every exception carries a human-readable ``message`` describing what was wrong
with the input, not just that something was wrong. Parsing failures name the
string that failed; component failures name the component and the reason.
"""

__all__ = [
    "DateConversionError",
    "InvalidDateFormatError",
    "InvalidEraError",
    "InvalidDateComponentError",
    "UnsupportedDateError",
    "AmbiguousDateError",
    "ConfigurationError",
    "ConverterRuntimeError",
    "ValidationError",
    "InputError",
]


class DateConversionError(Exception):
    """Base exception for all date conversion errors."""

    def __init__(self, message="Date conversion error occurred"):
        self.message = message
        super().__init__(self.message)


class InvalidDateFormatError(DateConversionError):
    """Raised when a date string cannot be parsed by any known pattern."""

    def __init__(self, message="Invalid date format", date_string=None):
        if date_string:
            message = "{}: '{}'".format(message, date_string)
        self.date_string = date_string
        super().__init__(message)


class InvalidEraError(DateConversionError):
    """Raised when an era name is missing or not recognised."""

    def __init__(self, message="Invalid era", era=None):
        if era:
            message = "{}: '{}'".format(message, era)
        self.era = era
        super().__init__(message)


class InvalidDateComponentError(DateConversionError):
    """Raised when a year, month or day value cannot form a real date."""

    def __init__(self, message="Invalid date component", component=None, value=None):
        if component and value is not None:
            message = "{}: {}={}".format(message, component, value)
        self.component = component
        self.value = value
        super().__init__(message)


class UnsupportedDateError(DateConversionError):
    """
    Raised when a date falls outside the era table -- that is, before
    明治元年 (1868-10-23). Pre-Meiji eras used the lunisolar calendar and
    changed for omens and disasters as well as successions, so they cannot be
    derived arithmetically.
    """

    def __init__(self, message="Date is outside the supported era range", date_string=None):
        if date_string:
            message = "{}: '{}'".format(message, date_string)
        self.date_string = date_string
        super().__init__(message)


class AmbiguousDateError(DateConversionError):
    """
    Raised when a numeric date has two valid readings (5/6/2023 is both
    5 June and 6 May) and the caller asked for strict handling instead of
    accepting the ``day_first`` default.
    """

    def __init__(self, message="Ambiguous date", date_string=None, readings=None):
        if date_string:
            message = "{}: '{}'".format(message, date_string)
        if readings:
            message = "{} (could be {})".format(message, " or ".join(readings))
        self.date_string = date_string
        self.readings = readings or []
        super().__init__(message)


class ConfigurationError(DateConversionError):
    """Raised when a converter is given an option it does not understand."""

    def __init__(self, message="Invalid converter configuration", config=None):
        if config:
            message = "{}: {}".format(message, config)
        self.config = config
        super().__init__(message)


class ConverterRuntimeError(DateConversionError):
    """Catch-all for unexpected errors raised during conversion."""

    def __init__(self, message="Runtime error during conversion", original_error=None):
        if original_error:
            message = "{}: {}".format(message, original_error)
        self.original_error = original_error
        super().__init__(message)


class ValidationError(DateConversionError):
    """Raised when a date fails validation for any other reason."""

    def __init__(self, message="Date validation failed", details=None):
        if details:
            message = "{}: {}".format(message, details)
        self.details = details
        super().__init__(message)


class InputError(DateConversionError):
    """Raised when input to a converter is the wrong type or empty."""

    def __init__(self, message="Invalid input", input_value=None):
        if input_value is not None:
            text = str(input_value)
            if len(text) > 100:
                text = text[:97] + "..."
            message = "{}: '{}'".format(message, text)
        self.input_value = input_value
        super().__init__(message)
