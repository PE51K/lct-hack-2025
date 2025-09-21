import ijson
import io
from typing import Dict, Any, Generator, Union
from collections import defaultdict, Counter
from .config import config, logger
from .validators import DataValidator
from .memory_manager import MemoryManager
from .exceptions import ProcessingTimeout, MemoryLimitExceeded

class OptimizedStreamProcessor:
    """Optimized JSON streaming processor for big data"""

    def __init__(self):
        self.validator = DataValidator()
        self.memory_manager = MemoryManager()
        self.schema_fields = set()
        self.schema_stability_counter = 0
        self.sample_rate = config.INITIAL_SAMPLE_RATE

    def stream_json_objects(self, data_source: Union[str, io.IOBase]) -> Generator[Dict[str, Any], None, None]:
        """Stream JSON objects with optimized parsing"""
        try:
            if isinstance(data_source, str):
                with open(data_source, 'rb') as file:
                    parser = ijson.parse(file)
                    yield from self._parse_optimized_stream(parser)
            else:
                parser = ijson.parse(data_source)
                yield from self._parse_optimized_stream(parser)
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            raise ProcessingTimeout(f"Stream processing failed: {e}")

    def _parse_optimized_stream(self, parser) -> Generator[Dict[str, Any], None, None]:
        """Parse stream with aggressive optimization for big data"""
        current_object = {}
        key_stack = []
        objects_yielded = 0
        objects_skipped = 0

        for prefix, event, value in parser:
            # Dynamic sampling rate adjustment
            if objects_yielded > 0 and objects_yielded % 100 == 0:
                self._adjust_sampling_rate(objects_yielded)

            # Memory check every 500 objects
            if objects_yielded % 500 == 0:
                if self.memory_manager.check_memory_limit():
                    self.sample_rate = min(config.AGGRESSIVE_SAMPLE_RATE, self.sample_rate * 3)
                    logger.warning(f"Memory limit approached, increasing sample rate to {self.sample_rate}")

            if event == 'start_map':
                if not key_stack:
                    current_object = {}
                key_stack.append({})

            elif event == 'end_map':
                if len(key_stack) == 1:
                    # Schema stability detection
                    if current_object:
                        self._update_schema_tracking(current_object)

                    # Apply sampling
                    if objects_skipped % self.sample_rate == 0:
                        yield self._sanitize_object(current_object)
                        objects_yielded += 1

                        # Early stop conditions
                        if self._should_early_stop(objects_yielded):
                            logger.info(f"Early stop triggered after {objects_yielded} objects")
                            break

                    objects_skipped += 1
                    current_object = {}
                key_stack.pop()

            elif event == 'map_key':
                key_stack[-1]['current_key'] = value

            elif event in ['string', 'number', 'boolean', 'null']:
                if key_stack and 'current_key' in key_stack[-1]:
                    key = key_stack[-1]['current_key']
                    if len(key_stack) == 1:
                        # Only store relevant fields
                        if self.validator.is_metadata_relevant_field(key, value):
                            sanitized_value = self.validator.validate_and_sanitize_value(value)
                            if sanitized_value is not None:
                                current_object[key] = sanitized_value

    def _adjust_sampling_rate(self, objects_yielded: int) -> None:
        """Dynamically adjust sampling rate based on processing state"""
        memory_mb = self.memory_manager.get_memory_usage_mb()
        new_rate = self.memory_manager.calculate_optimal_sample_rate(objects_yielded, memory_mb)

        if new_rate != self.sample_rate:
            self.sample_rate = new_rate
            if config.ENABLE_PERFORMANCE_LOGGING:
                logger.info(f"Adjusted sampling rate to {self.sample_rate} (memory: {memory_mb:.1f}MB)")

    def _update_schema_tracking(self, obj: Dict[str, Any]) -> None:
        """Update schema tracking for stability detection"""
        current_keys = set(obj.keys())

        if len(self.schema_fields) > 0:
            # Check if schema is stable
            if current_keys.issubset(self.schema_fields) or self.schema_fields.issubset(current_keys):
                self.schema_stability_counter += 1
            else:
                self.schema_stability_counter = 0

        self.schema_fields.update(current_keys)

        # Increase sampling if schema is stable
        if self.schema_stability_counter >= config.SCHEMA_STABILITY_THRESHOLD:
            self.sample_rate = min(config.AGGRESSIVE_SAMPLE_RATE // 2, self.sample_rate * 2)
            logger.info(f"Schema stable, adjusted sampling to {self.sample_rate}")

    def _should_early_stop(self, objects_yielded: int) -> bool:
        """Determine if processing should stop early"""
        # Stop if schema is stable and we have enough samples
        if (self.schema_stability_counter >= config.SCHEMA_STABILITY_THRESHOLD and
            objects_yielded >= config.EARLY_STOP_THRESHOLD):
            return True

        # Stop if we've reached maximum samples
        if objects_yielded >= config.MAX_SAMPLE_SIZE:
            return True

        return False

    def count_json_objects(self, data_source: Union[str, io.IOBase]) -> int:
        """Count total JSON objects in the data source efficiently"""
        count = 0
        try:
            if isinstance(data_source, str):
                with open(data_source, 'rb') as file:
                    parser = ijson.parse(file)
                    count = self._count_objects_in_stream(parser)
            else:
                # Reset stream position if possible
                if hasattr(data_source, 'seek'):
                    try:
                        data_source.seek(0)
                    except (OSError, io.UnsupportedOperation):
                        pass
                parser = ijson.parse(data_source)
                count = self._count_objects_in_stream(parser)
        except Exception as e:
            logger.error(f"Error counting JSON objects: {e}")
            return 0
        return count

    def _count_objects_in_stream(self, parser) -> int:
        """Count objects in the parser stream efficiently"""
        count = 0
        depth = 0

        try:
            for prefix, event, value in parser:
                if event == 'start_map':
                    depth += 1
                elif event == 'end_map':
                    depth -= 1
                    if depth == 0:  # Completed top-level object
                        count += 1

                        # Stop counting if we exceed reasonable limits
                        if count > config.MAX_SAMPLE_SIZE * 10:
                            logger.warning(f"Large dataset detected, stopping count at {count}")
                            break
        except Exception as e:
            logger.error(f"Error in stream counting: {e}")

        return count

    def _sanitize_object(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize object for safe processing"""
        sanitized = {}
        for key, value in obj.items():
            sanitized_value = self.validator.validate_and_sanitize_value(value)
            if sanitized_value is not None:
                sanitized[key] = sanitized_value
        return sanitized