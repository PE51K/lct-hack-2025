import re
from typing import Any, Dict, List, Optional
from .config import config, logger
from .exceptions import InvalidDataFormat, LargeIntegerError

class DataValidator:
    """Validates and sanitizes data for big data processing"""

    @staticmethod
    def validate_and_sanitize_value(value: Any) -> Any:
        """Validate and sanitize individual values"""
        try:
            # Handle large integers
            if isinstance(value, str) and value.isdigit() and len(value) > 4000:
                logger.warning(f"Large integer string detected: {len(value)} digits, truncating")
                return f"LARGE_INT_{len(value)}_DIGITS"

            # Handle very long strings
            if isinstance(value, str) and len(value) > config.MAX_STRING_LENGTH:
                if config.SKIP_LONG_STRINGS:
                    return value[:config.MAX_STRING_LENGTH] + "..."

            # Handle numeric conversion safely
            if isinstance(value, str):
                try:
                    # Try int conversion with limit check
                    if value.isdigit() and len(value) < 100:
                        return int(value)
                    # Try float conversion
                    elif '.' in value and len(value) < 100:
                        return float(value)
                except (ValueError, OverflowError):
                    return value

            return value

        except Exception as e:
            logger.warning(f"Value sanitization failed: {e}")
            return None

    @staticmethod
    def is_metadata_relevant_field(key: str, value: Any) -> bool:
        """Determine if field is relevant for metadata extraction"""
        key_lower = key.lower()

        # Always include identifier fields
        if any(pattern in key_lower for pattern in ['id', 'key', 'inn', 'ogrn', 'uuid']):
            return True

        # Include short categorical fields
        if isinstance(value, str) and len(value) < config.MAX_STRING_LENGTH:
            return True

        # Include numeric and boolean fields
        if isinstance(value, (int, float, bool)):
            return True

        # Include date/time fields
        if any(pattern in key_lower for pattern in ['date', 'time', 'created', 'updated']):
            return True

        # Skip very long text fields
        if isinstance(value, str) and len(value) > 500:
            return False

        return True

    @staticmethod
    def should_process_object(obj: Dict) -> bool:
        """Check if object should be processed based on complexity"""
        if not isinstance(obj, dict):
            return True

        # Skip very complex objects
        if len(obj) > config.MAX_OBJECT_KEYS:
            return False

        return True

    @staticmethod
    def should_process_array(arr: List) -> bool:
        """Check if array should be processed based on size"""
        if not isinstance(arr, list):
            return True

        # Skip very large arrays
        if len(arr) > config.MAX_ARRAY_ITEMS:
            return False

        return True