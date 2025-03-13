"""
Custom exceptions for the Japanese date converter package.
Provides a comprehensive exception hierarchy for handling various error conditions.
"""

class DateConversionError(Exception):
    """Base exception for all date conversion errors."""
    def __init__(self, message="Date conversion error occurred"):
        self.message = message
        super().__init__(self.message)


class InvalidDateFormatError(DateConversionError):
    """Raised when the date string format is not recognized or cannot be parsed."""
    def __init__(self, message="Invalid date format", date_string=None):
        if date_string:
            message = f"{message}: '{date_string}'"
        self.message = message
        super().__init__(self.message)


class InvalidEraError(DateConversionError):
    """Raised when an unknown or invalid era is specified."""
    def __init__(self, message="Invalid era", era=None):
        if era:
            message = f"{message}: '{era}'"
        self.message = message
        super().__init__(self.message)


class InvalidDateComponentError(DateConversionError):
    """Raised when a date component (year, month, day) is invalid."""
    def __init__(self, message="Invalid date component", component=None, value=None):
        if component and value is not None:
            message = f"{message}: {component}={value}"
        self.message = message
        super().__init__(self.message)


class UnsupportedDateError(DateConversionError):
    """Raised when a date is outside the supported range (e.g., before Meiji era)."""
    def __init__(self, message="Date is outside supported range", date_string=None):
        if date_string:
            message = f"{message}: '{date_string}'"
        self.message = message
        super().__init__(self.message)


class ConfigurationError(DateConversionError):
    """Raised when there's an issue with the converter configuration."""
    def __init__(self, message="Invalid converter configuration", config=None):
        if config:
            message = f"{message}: {config}"
        self.message = message
        super().__init__(self.message)


class ConverterRuntimeError(DateConversionError):
    """
    Raised for runtime errors during conversion that are not covered by other exceptions.
    This is a catch-all for unexpected errors.
    """
    def __init__(self, message="Runtime error during conversion", original_error=None):
        if original_error:
            message = f"{message}: {str(original_error)}"
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


class ValidationError(DateConversionError):
    """Raised when validation of a date fails for any reason."""
    def __init__(self, message="Date validation failed", details=None):
        if details:
            message = f"{message}: {details}"
        self.message = message
        super().__init__(self.message)


class InputError(DateConversionError):
    """Raised when input to a converter function is invalid."""
    def __init__(self, message="Invalid input", input_value=None):
        if input_value is not None:
            # Limit the displayed input to prevent overly long error messages
            input_str = str(input_value)
            if len(input_str) > 100:
                input_str = input_str[:97] + "..."
            message = f"{message}: '{input_str}'"
        self.message = message
        super().__init__(self.message)