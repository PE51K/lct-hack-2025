class AnalysisError(Exception):
    """Base exception for analysis errors"""
    pass

class MemoryLimitExceeded(AnalysisError):
    """Raised when memory limit is exceeded"""
    pass

class InvalidDataFormat(AnalysisError):
    """Raised when data format is invalid"""
    pass

class ProcessingTimeout(AnalysisError):
    """Raised when processing takes too long"""
    pass

class LargeIntegerError(AnalysisError):
    """Raised when integer is too large to process"""
    pass