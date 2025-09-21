import psutil
from typing import Dict, Any
from .config import config, logger
from .exceptions import MemoryLimitExceeded

class MemoryManager:
    """Manages memory usage during big data processing"""

    def __init__(self):
        self.process = psutil.Process()
        self.last_memory_check = 0
        self.memory_warnings = 0

    def get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB"""
        return self.process.memory_info().rss / 1024 / 1024

    def check_memory_limit(self) -> bool:
        """Check if memory limit is exceeded"""
        memory_mb = self.get_memory_usage_mb()

        if memory_mb > config.MAX_MEMORY_MB:
            self.memory_warnings += 1
            logger.warning(f"Memory usage: {memory_mb:.1f}MB exceeds limit {config.MAX_MEMORY_MB}MB")

            if self.memory_warnings > 3:
                raise MemoryLimitExceeded(f"Memory limit exceeded: {memory_mb:.1f}MB")

            return True

        return False

    def cleanup_key_stats(self, key_stats: Dict) -> None:
        """Clean up key statistics to reduce memory usage"""
        for key, stats in key_stats.items():
            # Limit unique values
            if len(stats.get('unique_values', set())) > config.MAX_UNIQUE_VALUES:
                unique_list = list(stats['unique_values'])
                stats['unique_values'] = set(unique_list[:config.MAX_UNIQUE_VALUES])

            # Limit sample values
            if len(stats.get('sample_values', [])) > config.MAX_SAMPLE_VALUES:
                stats['sample_values'] = stats['sample_values'][:config.MAX_SAMPLE_VALUES]

    def should_enable_aggressive_sampling(self, processed_count: int) -> bool:
        """Determine if aggressive sampling should be enabled"""
        memory_mb = self.get_memory_usage_mb()

        # Enable aggressive sampling if memory is high or processed many records
        if memory_mb > config.MAX_MEMORY_MB * 0.8:
            return True

        if processed_count > config.EARLY_STOP_THRESHOLD:
            return True

        return False

    def calculate_optimal_sample_rate(self, processed_count: int, memory_mb: float) -> int:
        """Calculate optimal sampling rate based on current conditions"""
        base_rate = config.INITIAL_SAMPLE_RATE

        # Increase sampling rate based on memory usage
        memory_factor = max(1, int(memory_mb / (config.MAX_MEMORY_MB * 0.5)))

        # Increase sampling rate based on processed count
        count_factor = max(1, processed_count // 1000)

        return min(config.AGGRESSIVE_SAMPLE_RATE, base_rate * memory_factor * count_factor)