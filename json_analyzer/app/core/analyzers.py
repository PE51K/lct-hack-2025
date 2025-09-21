import re
from typing import Dict, Any, List, Set
from collections import Counter, defaultdict
from .config import config

class StatisticalAnalyzer:
    @staticmethod
    def calculate_basic_statistics(key_stats: Dict) -> Dict[str, Any]:
        """Calculate statistical metrics for all fields"""
        total_records = max([stats.get('count', 0) for stats in key_stats.values()], default=0)

        stats = {
            'total_fields': len(key_stats),
            'total_records': total_records,
            'field_completeness': {},
            'field_cardinality': {},
            'most_common_types': {}
        }

        for field, field_stats in key_stats.items():
            field_count = field_stats.get('count', 0)
            stats['field_completeness'][field] = field_count / max(total_records, 1)
            stats['field_cardinality'][field] = len(field_stats.get('unique_values', set()))

            types_counter = field_stats.get('types', Counter())
            if types_counter:
                stats['most_common_types'][field] = types_counter.most_common(1)[0][0]

        return stats

    @staticmethod
    def analyze_value_patterns(key_stats: Dict) -> Dict[str, List[str]]:
        """Analyze value patterns across fields"""
        patterns = {
            'high_cardinality': [],
            'low_cardinality': [],
            'mostly_null': [],
            'constant_values': [],
            'numeric_ranges': []
        }

        total_records = max([stats.get('count', 0) for stats in key_stats.values()], default=1)

        for key, stats in key_stats.items():
            unique_count = len(stats.get('unique_values', set()))
            null_count = stats.get('null_count', 0)
            total_count = stats.get('count', 0)

            # Cardinality analysis
            cardinality_ratio = unique_count / max(total_count, 1)
            if cardinality_ratio > 0.95:
                patterns['high_cardinality'].append(key)
            elif unique_count <= 10:
                patterns['low_cardinality'].append(key)

            # Null analysis
            null_ratio = null_count / max(total_records, 1)
            if null_ratio > 0.8:
                patterns['mostly_null'].append(key)

            # Constant values
            if unique_count == 1 and total_count > 1:
                patterns['constant_values'].append(key)

            # Numeric patterns
            types_counter = stats.get('types', Counter())
            if types_counter.get('number', 0) > types_counter.get('string', 0):
                patterns['numeric_ranges'].append(key)

        return patterns

    @staticmethod
    def detect_skew_patterns(key_stats: Dict) -> Dict[str, List[str]]:
        """Detect data distribution skew patterns"""
        skew_patterns = {
            'uniform': [],
            'moderate': [],
            'high': [],
            'extreme': []
        }

        for key, stats in key_stats.items():
            unique_values = stats.get('unique_values', set())
            total_count = stats.get('count', 0)

            if len(unique_values) <= 1 or total_count <= 1:
                continue

            # Simple skew calculation based on cardinality
            cardinality_ratio = len(unique_values) / total_count

            if cardinality_ratio > 0.8:
                skew_patterns['uniform'].append(key)
            elif cardinality_ratio > 0.5:
                skew_patterns['moderate'].append(key)
            elif cardinality_ratio > 0.2:
                skew_patterns['high'].append(key)
            else:
                skew_patterns['extreme'].append(key)

        return skew_patterns

    @staticmethod
    def classify_field_types(key_stats: Dict) -> Dict[str, str]:
        """Classify fields into semantic types with OLAP-aware logic"""
        field_types = {}

        for key, stats in key_stats.items():
            key_lower = key.lower()
            sample_values = stats.get('sample_values', [])
            types_counter = stats.get('types', Counter())
            unique_count = len(stats.get('unique_values', set()))
            total_count = stats.get('count', 0)
            uniqueness_ratio = unique_count / max(total_count, 1)

            # Priority 1: Numeric metrics and measurements (OLAP critical)
            if any(word in key_lower for word in ['_ms', '_sec', '_bytes', '_time', '_size', '_count', '_value', '_rate', '_score', '_amount', '_price', '_weight', '_duration']):
                field_types[key] = 'numeric'
            elif 'latitude' in key_lower or 'longitude' in key_lower:
                field_types[key] = 'numeric'
            elif key_lower in ['conversion_value', 'revenue', 'profit', 'cost', 'distance', 'temperature', 'speed', 'percentage']:
                field_types[key] = 'numeric'

            # Priority 2: Check if field contains numeric data but stored as strings
            elif StatisticalAnalyzer._is_numeric_field(sample_values, types_counter):
                field_types[key] = 'numeric'

            # Priority 3: Temporal detection
            elif 'timestamp' in key_lower:
                field_types[key] = 'temporal'
            elif any(word in key_lower for word in ['date', 'time', 'created', 'updated']) and 'date_ogrnip' not in key_lower:
                field_types[key] = 'temporal'
            elif any(isinstance(v, str) and re.match(r'\d{4}-\d{2}-\d{2}', str(v)) for v in sample_values[:3] if v):
                field_types[key] = 'temporal'

            # Priority 4: Russian financial identifiers (critical for financial_data)
            elif any(field in key_lower for field in ['innfl', 'ogrnip', 'insured_pf']):
                field_types[key] = 'identifier'

            # Priority 5: Contact info detection
            elif 'email' in key_lower or any('@' in str(v) for v in sample_values[:3] if v):
                field_types[key] = 'contact'
            elif any(word in key_lower for word in ['phone', 'телефон', 'tel']):
                field_types[key] = 'contact'

            # Priority 6: Organization names (authority, tax service names)
            elif any(word in key_lower for word in ['authority', 'налоговая', 'служба', 'организация']):
                if 'name' in key_lower:
                    field_types[key] = 'organization_name'
                else:
                    field_types[key] = 'text_content'

            # Priority 7: Personal names detection
            elif any(word in key_lower for word in ['firstname', 'surname', 'midname', 'фамилия', 'имя', 'отчество']):
                field_types[key] = 'personal_name'
            elif 'name' in key_lower and not any(word in key_lower for word in ['filename', 'company', 'org', 'okved']):
                field_types[key] = 'personal_name'

            # Priority 8: OKVED descriptions as text content
            elif 'okved' in key_lower and 'name' in key_lower:
                field_types[key] = 'text_content'

            # Priority 9: Codes and classifiers always categorical (semantic priority over content)
            elif any(word in key_lower for word in ['code', 'okved', 'class', 'type', 'status', 'category']) or 'inf_authority_reg_ind_entrep_code' in key_lower:
                field_types[key] = 'categorical'

            # Priority 10: Tax registration fields - consistent classification
            elif 'inf_reg_tax' in key_lower:
                field_types[key] = 'categorical'

            # Priority 11: High uniqueness identifiers
            elif uniqueness_ratio > 0.95 and total_count > 10:
                field_types[key] = 'identifier'
            elif any(word in key_lower for word in ['id', 'uuid', 'key', 'session']) and not 'code' in key_lower:
                field_types[key] = 'identifier'

            # Priority 12: Low cardinality = categorical
            elif unique_count <= 20 and total_count > 20:
                field_types[key] = 'categorical'

            # Priority 13: Text content detection
            elif any(isinstance(v, str) and len(str(v)) > 50 for v in sample_values[:3] if v):
                field_types[key] = 'text_content'

            # Priority 14: Boolean detection
            elif types_counter.get('boolean', 0) > 0:
                field_types[key] = 'boolean'

            # Priority 15: Default classification
            else:
                field_types[key] = 'categorical'

        return field_types

    @staticmethod
    def _is_numeric_field(sample_values: List, types_counter: Counter) -> bool:
        """Check if field contains numeric data regardless of storage type"""
        if not sample_values:
            return False

        # If we have actual numbers in types, it's numeric
        if types_counter.get('number', 0) > 0:
            return True

        # Check if string values are actually numbers
        numeric_count = 0
        for val in sample_values[:5]:  # Check first 5 samples
            if val is None or val == '':
                continue
            try:
                # Try to convert to float
                float(str(val))
                numeric_count += 1
            except (ValueError, TypeError):
                pass

        # If most values are numeric, classify as numeric
        return numeric_count >= len([v for v in sample_values[:5] if v is not None and v != '']) * 0.7

class KeyStatsCollector:
    def __init__(self):
        self.key_stats = defaultdict(lambda: {
            'count': 0,
            'null_count': 0,
            'types': Counter(),
            'unique_values': set(),
            'sample_values': []
        })

    def process_record(self, record: Dict[str, Any]):
        """Process a single record and update statistics"""
        for key, value in record.items():
            self.key_stats[key]['count'] += 1

            # Handle null values
            if value is None:
                self.key_stats[key]['null_count'] += 1
                continue

            # Sanitize value for processing
            sanitized_value = self._sanitize_value(value)

            # Count value types
            value_type = self._get_value_type(sanitized_value)
            self.key_stats[key]['types'][value_type] += 1

            # Limit sample collection with type consistency
            if len(self.key_stats[key]['sample_values']) < config.MAX_SAMPLE_VALUES:
                # Ensure string consistency for sample values
                sample_val = str(sanitized_value) if not isinstance(sanitized_value, str) else sanitized_value
                # Truncate long strings for samples
                if len(sample_val) > 100:
                    sample_val = sample_val[:100] + "..."
                self.key_stats[key]['sample_values'].append(sample_val)

            # Limit unique values tracking
            if len(self.key_stats[key]['unique_values']) < config.MAX_UNIQUE_VALUES:
                if isinstance(sanitized_value, str):
                    # Truncate long strings for unique tracking
                    if len(sanitized_value) > 100:
                        sanitized_value = sanitized_value[:100] + "..."

                self.key_stats[key]['unique_values'].add(str(sanitized_value))

    def _sanitize_value(self, value: Any) -> Any:
        """Sanitize value to prevent memory issues"""
        if isinstance(value, str) and len(value) > 1000:
            return value[:1000] + "..."
        elif isinstance(value, (list, dict)):
            return f"<{type(value).__name__}_with_{len(str(value)[:100])}chars>"
        return value

    def _get_value_type(self, value: Any) -> str:
        """Determine the type of a value"""
        if value is None:
            return 'null'
        elif isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, (int, float)):
            return 'number'
        elif isinstance(value, str):
            return 'string'
        elif isinstance(value, list):
            return 'array'
        elif isinstance(value, dict):
            return 'object'
        else:
            return 'unknown'

    def get_final_stats(self) -> Dict:
        """Get final statistics with converted sets to lists"""
        final_stats = {}
        for key, stats in self.key_stats.items():
            final_stats[key] = {
                'count': stats['count'],
                'null_count': stats['null_count'],
                'types': dict(stats['types']),
                'unique_values': list(stats['unique_values'])[:100],  # Limit for serialization
                'sample_values': stats['sample_values']
            }
        return final_stats

class MetadataAnalyzer:
    """Core metadata analysis functionality"""

    def __init__(self):
        self.stats_collector = KeyStatsCollector()

    def analyze_record(self, record: Dict[str, Any], key_stats: Dict):
        """Analyze a single record and update key statistics"""
        for key, value in record.items():
            key_stats[key]['count'] += 1

            # Handle null values
            if value is None:
                key_stats[key]['null_count'] += 1
                continue

            # Get value type
            value_type = self._get_value_type(value)
            key_stats[key]['types'][value_type] += 1

            # Sanitize and store sample values
            sanitized_value = self._sanitize_value(value)
            if len(key_stats[key]['sample_values']) < config.MAX_SAMPLE_VALUES:
                sample_val = str(sanitized_value) if not isinstance(sanitized_value, str) else sanitized_value
                if len(sample_val) > 100:
                    sample_val = sample_val[:100] + "..."
                key_stats[key]['sample_values'].append(sample_val)

            # Track unique values
            if len(key_stats[key]['unique_values']) < config.MAX_UNIQUE_VALUES:
                unique_val = str(sanitized_value)
                if len(unique_val) > 100:
                    unique_val = unique_val[:100] + "..."
                key_stats[key]['unique_values'].add(unique_val)

    def calculate_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calculate nesting depth with limits"""
        if current_depth >= config.MAX_DEPTH:
            return current_depth

        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self.calculate_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self.calculate_depth(item, current_depth + 1) for item in obj[:5])  # Limit array depth check
        else:
            return current_depth

    def _sanitize_value(self, value: Any) -> Any:
        """Sanitize value to prevent memory issues"""
        if isinstance(value, str) and len(value) > 1000:
            return value[:1000] + "..."
        elif isinstance(value, (list, dict)):
            return f"<{type(value).__name__}_with_{len(str(value)[:100])}chars>"
        return value

    def _get_value_type(self, value: Any) -> str:
        """Determine the type of a value"""
        if value is None:
            return 'null'
        elif isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, (int, float)):
            return 'number'
        elif isinstance(value, str):
            return 'string'
        elif isinstance(value, list):
            return 'array'
        elif isinstance(value, dict):
            return 'object'
        else:
            return 'unknown'

class UniversalMetricsCalculator:
    """Universal metrics calculation for big data analysis"""

    def analyze_cardinality_patterns(self, key_stats: Dict, total_records: int) -> Dict[str, List[str]]:
        """Analyze cardinality patterns across fields"""
        patterns = {
            'high_cardinality': [],      # > 95% unique
            'medium_cardinality': [],    # 20-95% unique
            'low_cardinality': [],       # < 20% unique
            'constant_values': []        # Single value
        }

        for key, stats in key_stats.items():
            unique_count = len(stats.get('unique_values', set()))
            total_count = stats.get('count', 0)

            if total_count == 0:
                continue

            cardinality_ratio = unique_count / total_count

            if unique_count == 1 and total_count > 1:
                patterns['constant_values'].append(key)
            elif cardinality_ratio > 0.95:
                patterns['high_cardinality'].append(key)
            elif cardinality_ratio > 0.2:
                patterns['medium_cardinality'].append(key)
            else:
                patterns['low_cardinality'].append(key)

        return patterns

    def analyze_distribution_skew(self, key_stats: Dict) -> Dict[str, List[str]]:
        """Analyze data distribution skew"""
        return StatisticalAnalyzer.detect_skew_patterns(key_stats)

    def classify_field_types(self, key_stats: Dict) -> Dict[str, str]:
        """Classify field semantic types"""
        return StatisticalAnalyzer.classify_field_types(key_stats)