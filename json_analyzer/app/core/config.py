import sys
import logging
from typing import Optional

# Fix large integer conversion issue
sys.set_int_max_str_digits(10000)

class BigDataConfig:
    """Configuration for big data processing"""

    # Memory limits
    MAX_MEMORY_MB: int = 1024
    MAX_SAMPLE_SIZE: int = 2000
    CHUNK_SIZE: int = 500

    # Performance optimizations
    ENABLE_YDATA_PROFILING: bool = False
    MAX_UNIQUE_VALUES: int = 500
    MAX_SAMPLE_VALUES: int = 5
    MAX_STRING_LENGTH: int = 100
    MAX_DEPTH: int = 2

    # Sampling strategy
    INITIAL_SAMPLE_RATE: int = 1
    AGGRESSIVE_SAMPLE_RATE: int = 100
    SCHEMA_STABILITY_THRESHOLD: int = 5
    EARLY_STOP_THRESHOLD: int = 1000

    # Field filtering
    SKIP_LONG_STRINGS: bool = True
    SKIP_COMPLEX_OBJECTS: bool = True
    MAX_OBJECT_KEYS: int = 20
    MAX_ARRAY_ITEMS: int = 10

    # Logging
    LOG_LEVEL: str = "INFO"
    ENABLE_PERFORMANCE_LOGGING: bool = True

def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure logging for the application"""
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

# Global config instance
config = BigDataConfig()
logger = setup_logging(config.LOG_LEVEL)