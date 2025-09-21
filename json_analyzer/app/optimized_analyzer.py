import time
import io
from typing import Dict, Any, List, Union
from collections import defaultdict, Counter
from .models import *
from .core import (
    config, logger, OptimizedStreamProcessor, MetadataAnalyzer,
    UniversalMetricsCalculator, MemoryManager, DataValidator,
    AnalysisError, MemoryLimitExceeded, SemanticPatternAnalyzer
)

class OptimizedBigDataAnalyzer:
    """Modular big data JSON analyzer with optimized performance"""

    def __init__(self):
        self.stream_processor = OptimizedStreamProcessor()
        self.metadata_analyzer = MetadataAnalyzer()
        self.metrics_calculator = UniversalMetricsCalculator()
        self.memory_manager = MemoryManager()
        self.validator = DataValidator()
        self.semantic_analyzer = SemanticPatternAnalyzer()
        self.processed_records = 0

    def analyze_json_structure(self, data_source: Union[str, io.IOBase, List[Dict], Dict]) -> AnalysisResponse:
        """Main analysis method with modular architecture"""
        start_time = time.time()
        start_memory = self.memory_manager.get_memory_usage_mb()

        try:
            # Initialize optimized collectors
            key_stats = defaultdict(lambda: {
                'count': 0, 'types': Counter(), 'sample_values': [],
                'null_count': 0, 'unique_values': set()
            })
            total_records = 0
            max_depth = 0
            structure_samples = []

            # Process data with optimization
            if isinstance(data_source, (list, dict)):
                total_records, max_depth = self._process_direct_data(
                    data_source, key_stats, structure_samples
                )
            else:
                total_records, max_depth = self._process_stream_data(
                    data_source, key_stats, structure_samples
                )

            # Calculate processing metrics
            end_time = time.time()
            processing_time = end_time - start_time
            end_memory = self.memory_manager.get_memory_usage_mb()
            memory_usage = max(0, end_memory - start_memory)

            # Build optimized response
            return self._build_optimized_response(
                key_stats, total_records, max_depth, structure_samples,
                processing_time, memory_usage
            )

        except MemoryLimitExceeded as e:
            logger.error(f"Memory limit exceeded during analysis: {e}")
            raise
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise AnalysisError(f"Analysis failed: {e}")

    def _process_direct_data(self, data_source: Union[List[Dict], Dict],
                           key_stats: Dict, structure_samples: List) -> tuple:
        """Process direct data (list or dict) with optimization"""
        records = data_source if isinstance(data_source, list) else [data_source]
        total_records = 0
        max_depth = 0
        processed_count = 0

        for record in records:
            total_records += 1

            # Apply sampling for large datasets
            if total_records % max(1, self.stream_processor.sample_rate) == 0:
                if self.validator.should_process_object(record):
                    self.metadata_analyzer.analyze_record(record, key_stats)
                    processed_count += 1

                    # Calculate depth with limits
                    depth = self.metadata_analyzer.calculate_depth(record)
                    max_depth = max(max_depth, depth)

                    # Store structure sample
                    if len(structure_samples) < 50:
                        structure_samples.append(self._create_structure_sample(record))

                    # Memory cleanup
                    if processed_count % 100 == 0:
                        self.memory_manager.cleanup_key_stats(key_stats)

                    # Early exit conditions
                    if processed_count >= config.MAX_SAMPLE_SIZE:
                        break

        return total_records, max_depth

    def _count_total_records(self, data_source: Union[str, io.IOBase]) -> int:
        """Count total records in the data source for accurate statistics"""
        try:
            if isinstance(data_source, str):
                # File path - count records efficiently
                return self.stream_processor.count_json_objects(data_source)
            elif hasattr(data_source, 'read'):
                # File-like object - count with stream processor
                return self.stream_processor.count_json_objects(data_source)
            else:
                logger.warning(f"Cannot count records for data source type: {type(data_source)}")
                return 0
        except Exception as e:
            logger.error(f"Failed to count total records: {e}")
            return 0

    def _process_stream_data(self, data_source: Union[str, io.IOBase],
                           key_stats: Dict, structure_samples: List) -> tuple:
        """Process streaming data with optimization"""
        # First, count total records in file
        total_records = self._count_total_records(data_source)

        max_depth = 0
        processed_count = 0

        try:
            for record in self.stream_processor.stream_json_objects(data_source):
                processed_count += 1

                self.metadata_analyzer.analyze_record(record, key_stats)

                # Calculate depth
                depth = self.metadata_analyzer.calculate_depth(record)
                max_depth = max(max_depth, depth)

                # Store structure sample
                if len(structure_samples) < 25:
                    structure_samples.append(self._create_structure_sample(record))

                # Memory management
                if processed_count % 100 == 0:
                    self.memory_manager.cleanup_key_stats(key_stats)
                    if len(structure_samples) > 25:
                        structure_samples = structure_samples[-15:]

        except Exception as e:
            logger.error(f"Stream processing error: {e}")
            # Continue with partial data

        return total_records, max_depth

    def _create_structure_sample(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Create optimized structure sample"""
        sample = {}
        for k, v in record.items():
            if isinstance(v, (str, int, float, bool)) or v is None:
                # Truncate long strings
                if isinstance(v, str) and len(v) > 50:
                    sample[k] = v[:50] + "..."
                else:
                    sample[k] = v
            elif isinstance(v, dict):
                sample[k] = f"<object_with_{len(v)}_keys>"
            elif isinstance(v, list):
                sample[k] = f"<array_with_{len(v)}_items>"
        return sample

    def _safe_float(self, value: Any) -> float:
        """Safely convert value to float"""
        if value is None or str(value).lower() in ['nan', 'inf', '-inf']:
            return 0.0
        try:
            result = float(value)
            return result if not (result != result or abs(result) == float('inf')) else 0.0
        except (ValueError, TypeError, OverflowError):
            return 0.0

    def _build_optimized_response(self, key_stats: Dict, total_records: int, max_depth: int,
                                structure_samples: List, processing_time: float,
                                memory_usage: float) -> AnalysisResponse:
        """Build optimized analysis response"""

        # Generate universal metrics
        cardinality_patterns = self.metrics_calculator.analyze_cardinality_patterns(key_stats, total_records)
        distribution_skew = self.metrics_calculator.analyze_distribution_skew(key_stats)
        field_types = self.metrics_calculator.classify_field_types(key_stats)

        # Advanced semantic analysis
        detected_patterns = self.semantic_analyzer.analyze_semantic_patterns(key_stats)
        domain_indicators = self.semantic_analyzer.detect_domain_indicators(key_stats)
        pii_risk = self.semantic_analyzer.assess_pii_risk(key_stats, detected_patterns)

        # Select primary key with business logic
        suggested_pk = self._select_primary_key(key_stats, total_records)

        # Calculate quality metrics
        total_possible_values = sum(s['count'] for s in key_stats.values())
        non_null_values = total_possible_values - sum(s['null_count'] for s in key_stats.values())
        data_density = self._safe_float(non_null_values / max(total_possible_values, 1))

        # Build uniqueness distribution
        uniqueness_dist = {}
        for key, stats in key_stats.items():
            if stats['count'] > 0:
                uniqueness_dist[key] = self._safe_float(
                    min(1.0, len(stats['unique_values']) / min(stats['count'], config.MAX_UNIQUE_VALUES))
                )

        # Generate performance hints with single primary key
        performance_hints = self._generate_performance_hints(key_stats, total_records, field_types, suggested_pk)

        # Extract semantic patterns
        temporal_indicators = [k for k, v in field_types.items() if v == 'temporal']
        identifier_candidates = [k for k, v in field_types.items() if v == 'identifier']
        categorical_fields = [k for k, v in field_types.items() if v == 'categorical']
        text_content_fields = [k for k, v in field_types.items() if v == 'text_content']

        # Build value type distribution
        value_type_dist = self._calculate_value_type_distribution(key_stats)

        # Build nested structure map
        nested_structure_map = self._build_nested_structure_map(structure_samples[:5])

        return AnalysisResponse(
            analysis_metadata=AnalysisMetadata(
                source_info=SourceInfo(
                    source_type=SourceType.FILE_UPLOAD,
                    total_records=total_records,
                    total_keys=len(key_stats),
                    file_size_mb=0,
                    processing_time_seconds=self._safe_float(processing_time)
                ),
                structure_analysis=StructureAnalysis(
                    nesting_depth=max_depth,
                    schema_consistency=0.9,
                    most_frequent_keys=list(key_stats.keys())[:10],
                    value_type_distribution=value_type_dist,
                    nested_structure_map=nested_structure_map
                ),
                key_analysis=self._build_field_info(key_stats),
                quality_metrics=QualityMetrics(
                    completeness_score=self._safe_float(1.0 - sum(s['null_count'] for s in key_stats.values()) / max(sum(s['count'] for s in key_stats.values()), 1)),
                    consistency_score=0.9,
                    validity_score=0.9,
                    duplicate_records=0,
                    missing_values_total=sum(s['null_count'] for s in key_stats.values()),
                    data_density=data_density,
                    uniqueness_distribution=uniqueness_dist
                ),
                semantic_analysis=SemanticAnalysis(
                    detected_patterns=detected_patterns,
                    domain_indicators=domain_indicators,
                    pii_risk_assessment=pii_risk
                ),
                agent_recommendations=AgentRecommendations(
                    suggested_primary_key=suggested_pk,
                    structural_characteristics=StructuralCharacteristics(
                        cardinality_patterns=cardinality_patterns,
                        data_distribution_skew=distribution_skew,
                        field_correlation_strength=0.3,
                        schema_stability=0.9
                    ),
                    universal_semantics=UniversalSemanticPatterns(
                        temporal_indicators=temporal_indicators,
                        identifier_candidates=identifier_candidates,
                        categorical_fields=categorical_fields,
                        text_content_fields=text_content_fields,
                        field_types=field_types
                    ),
                    performance_hints=PerformanceHints(
                        size_growth_indicators=performance_hints['size_growth_indicators'],
                        query_performance_hints=performance_hints['query_performance_hints'],
                        optimal_storage_format=performance_hints['optimal_storage_format'],
                        compression_potential=self._safe_float(performance_hints['compression_potential']),
                        indexing_strategy=performance_hints['indexing_strategy']
                    )
                )
            ),
            ydata_profile_summary={"disabled": True, "reason": "big_data_optimization"},
            processing_stats=ProcessingStats(
                memory_usage_mb=self._safe_float(memory_usage),
                processing_duration=self._safe_float(processing_time),
                records_per_second=self._safe_float(total_records / max(processing_time, 0.001)),
                analysis_timestamp=str(time.time())
            )
        )

    def _select_primary_key(self, key_stats: Dict, total_records: int) -> str:
        """Select primary key with hierarchical business logic"""
        candidates = []

        for key, stats in key_stats.items():
            if stats['count'] == 0:
                continue

            uniqueness = len(stats['unique_values']) / min(stats['count'], config.MAX_UNIQUE_VALUES)
            coverage = stats['count'] / total_records if total_records > 0 else 0

            # Business identifier hierarchy
            business_bonus = 0
            key_lower = key.lower()

            if 'innfl' in key_lower or 'inn' in key_lower:
                business_bonus = 1000
            elif 'ogrn' in key_lower:
                business_bonus = 900
            elif 'uuid' in key_lower or 'uid' in key_lower:
                business_bonus = 700
            elif 'id' in key_lower and 'card' not in key_lower:
                business_bonus = 600

            score = (uniqueness * 1000) + (coverage * 500) + business_bonus
            candidates.append((key, score))

        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]

        return list(key_stats.keys())[0] if key_stats else ""

    def _build_field_info(self, key_stats: Dict) -> List[FieldAnalysis]:
        """Build field information with optimization"""
        fields = []
        for key, stats in key_stats.items():
            fields.append(FieldAnalysis(
                field_name=key,
                field_type="string",  # Simplified
                sample_values=stats['sample_values'][:3],
                unique_count=len(stats['unique_values']),
                null_count=stats['null_count'],
                completeness_ratio=self._safe_float(stats['count'] / max(stats['count'] + stats['null_count'], 1))
            ))
        return fields

    def _generate_performance_hints(self, key_stats: Dict, total_records: int, field_types: Dict, primary_key: str) -> Dict:
        """Generate performance optimization hints with OLAP-aware storage recommendations"""
        # Detect OLAP patterns for storage format recommendation
        storage_format = self._determine_optimal_storage_format(key_stats, field_types, total_records)

        hints = {
            'size_growth_indicators': {},
            'query_performance_hints': [],
            'optimal_storage_format': storage_format,
            'compression_potential': 0.0,
            'indexing_strategy': {}
        }

        # Database recommendation algorithm with safe fallbacks
        try:
            domain_indicators = self.semantic_analyzer.detect_domain_indicators(key_stats) if hasattr(self, 'semantic_analyzer') else []
            pii_risk = self.semantic_analyzer.assess_pii_risk(key_stats, {}) if hasattr(self, 'semantic_analyzer') else 0.0

            database_recommendation = self._recommend_database(
                storage_format,
                key_stats,
                field_types,
                total_records,
                domain_indicators,
                pii_risk
            )
            hints['recommended_database'] = database_recommendation['database']
            hints['database_rationale'] = database_recommendation['rationale']
        except Exception as e:
            # Fallback to safe defaults
            hints['recommended_database'] = 'postgresql'
            hints['database_rationale'] = f"Default recommendation due to analysis error: {str(e)}"

        # Add database-specific query hints
        recommended_db = hints.get('recommended_database', 'postgresql')
        if recommended_db == 'clickhouse':
            hints['query_performance_hints'].extend([
                'Optimize for GROUP BY and aggregation queries',
                'Consider partitioning by time-based fields',
                'Use projection/materialized views for common aggregations'
            ])
        elif recommended_db == 'postgresql':
            hints['query_performance_hints'].extend([
                'Use appropriate indexes for transactional queries',
                'Consider row-level security for PII data',
                'Implement proper ACID transaction boundaries'
            ])
        elif recommended_db == 'hdfs':
            hints['query_performance_hints'].extend([
                'Consider data compression (gzip, snappy)',
                'Partition data by date/time for efficient querying',
                'Use appropriate file formats (Parquet, ORC)'
            ])

        # Calculate compression potential
        categorical_ratio = len([f for f in field_types.values() if f == 'categorical']) / max(len(field_types), 1)
        hints['compression_potential'] = min(0.9, categorical_ratio + 0.3)

        # Size growth indicators
        for key, field_type in field_types.items():
            stats = key_stats.get(key, {})
            unique_ratio = len(stats.get('unique_values', [])) / max(stats.get('count', 1), 1)

            if field_type == 'identifier' or unique_ratio > 0.9:
                hints['size_growth_indicators'][key] = 'linear'
            elif field_type == 'categorical':
                hints['size_growth_indicators'][key] = 'logarithmic'
            elif field_type == 'text_content':
                hints['size_growth_indicators'][key] = 'unpredictable'
            else:
                hints['size_growth_indicators'][key] = 'stable'

        # Indexing strategy with single primary key
        for key, field_type in field_types.items():
            if key == primary_key:
                hints['indexing_strategy'][key] = 'primary_btree'  # Only one primary key
            elif field_type == 'identifier':
                hints['indexing_strategy'][key] = 'unique_btree'   # Other identifiers as unique
            elif field_type == 'categorical':
                hints['indexing_strategy'][key] = 'hash'
            elif field_type == 'temporal':
                hints['indexing_strategy'][key] = 'btree_range'
            elif field_type == 'text_content':
                hints['indexing_strategy'][key] = 'fulltext'

        # Performance hints
        high_cardinality_fields = len([f for f in field_types.values() if f == 'identifier'])
        if high_cardinality_fields > 5:
            hints['query_performance_hints'].append('Consider partitioning by high-cardinality fields')
        if len([f for f in field_types.values() if f == 'text_content']) > 3:
            hints['query_performance_hints'].append('Full-text search indices recommended for text fields')
        if total_records > 100000:
            hints['query_performance_hints'].append('Implement data archiving strategy for old records')

        return hints

    def _determine_optimal_storage_format(self, key_stats: Dict, field_types: Dict, total_records: int) -> str:
        """Determine optimal storage format based on OLAP/OLTP patterns"""
        analytics_score = 0
        transactional_score = 0

        # Analytics indicators
        temporal_fields = len([f for f in field_types.values() if f == 'temporal'])
        numeric_fields = len([f for f in field_types.values() if f == 'numeric'])
        categorical_fields = len([f for f in field_types.values() if f == 'categorical'])
        total_fields = len(field_types)

        # Check for time-series patterns (strong OLAP indicator)
        has_timestamp = any('timestamp' in k.lower() for k in key_stats.keys())
        has_event_data = any(word in k.lower() for k in key_stats.keys()
                           for word in ['event', 'action', 'activity', 'log', 'metric'])

        # Analytics scoring
        if has_timestamp:
            analytics_score += 3  # Time-series data
        if has_event_data:
            analytics_score += 2  # Event/log data
        if numeric_fields / max(total_fields, 1) > 0.3:
            analytics_score += 2  # Many metrics/measurements
        if categorical_fields / max(total_fields, 1) > 0.4:
            analytics_score += 1  # Many dimensions
        if total_records > 10000:
            analytics_score += 1  # Large volume

        # Check for web analytics patterns
        web_analytics_indicators = [
            'page_load_time', 'response_size', 'session_duration', 'conversion_value',
            'bounce_rate', 'user_agent', 'referrer', 'viewport', 'browser', 'device'
        ]
        web_analytics_count = sum(1 for indicator in web_analytics_indicators
                                 if any(indicator in k.lower() for k in key_stats.keys()))
        if web_analytics_count >= 3:
            analytics_score += 3  # Strong web analytics pattern

        # Transactional indicators
        identifier_fields = len([f for f in field_types.values() if f == 'identifier'])
        text_fields = len([f for f in field_types.values() if f == 'text_content'])

        # Transactional scoring
        if identifier_fields / max(total_fields, 1) > 0.3:
            transactional_score += 2  # Many unique identifiers
        if text_fields / max(total_fields, 1) > 0.3:
            transactional_score += 2  # Many text fields
        if total_records < 1000:
            transactional_score += 1  # Small volume

        # Check for normalized/relational patterns
        has_normalized_ids = any(k.lower().endswith('_id') for k in key_stats.keys())
        if has_normalized_ids:
            transactional_score += 1

        # Decision logic
        if analytics_score >= 4:
            return 'columnar'
        elif transactional_score >= 3 and analytics_score < 2:
            return 'document'
        elif total_records > 50000 and numeric_fields > 0:
            return 'columnar'  # Large datasets with metrics lean towards analytics
        else:
            return 'document'

    def _recommend_database(self, storage_format: str, key_stats: Dict, field_types: Dict,
                           total_records: int, domain_indicators: List[str], pii_risk: float) -> Dict[str, str]:
        """Recommend database based on data characteristics and usage patterns"""

        # Calculate key metrics
        file_size_mb = sum(len(str(v)) for stats in key_stats.values()
                          for v in stats.get('sample_values', [])) / (1024 * 1024)
        numeric_fields_count = len([f for f in field_types.values() if f == 'numeric'])
        total_fields = len(field_types)
        has_temporal = any(f == 'temporal' for f in field_types.values())

        # ClickHouse scoring
        clickhouse_score = 0
        clickhouse_reasons = []

        if storage_format == 'columnar':
            clickhouse_score += 3
            clickhouse_reasons.append("columnar storage format")

        if any(domain in ['web_analytics', 'metrics', 'logs', 'telemetry'] for domain in domain_indicators):
            clickhouse_score += 3
            clickhouse_reasons.append(f"analytics domain: {', '.join(domain_indicators)}")

        if numeric_fields_count / max(total_fields, 1) > 0.3:
            clickhouse_score += 2
            clickhouse_reasons.append(f"{numeric_fields_count} numeric fields for aggregation")

        if has_temporal:
            clickhouse_score += 2
            clickhouse_reasons.append("time-series data")

        if total_records > 10000:
            clickhouse_score += 1
            clickhouse_reasons.append("large dataset")

        # PostgreSQL scoring
        postgresql_score = 0
        postgresql_reasons = []

        if storage_format == 'document':
            postgresql_score += 2
            postgresql_reasons.append("document storage format")

        if pii_risk > 0.7:
            postgresql_score += 3
            postgresql_reasons.append(f"high PII risk ({pii_risk:.1f})")

        # Check for transactional patterns
        identifier_ratio = len([f for f in field_types.values() if f == 'identifier']) / max(total_fields, 1)
        if identifier_ratio > 0.3:
            postgresql_score += 2
            postgresql_reasons.append("many identifiers suggest relational data")

        # Check for complex relationships
        if any(domain in ['finance', 'user_management', 'crm'] for domain in domain_indicators):
            postgresql_score += 2
            postgresql_reasons.append("transactional domain")

        if total_records < 10000:
            postgresql_score += 1
            postgresql_reasons.append("moderate dataset size")

        # HDFS scoring
        hdfs_score = 0
        hdfs_reasons = []

        if file_size_mb > 1000:
            hdfs_score += 4
            hdfs_reasons.append(f"large file size ({file_size_mb:.1f}MB)")

        # Check for batch processing indicators
        if any(domain in ['logs', 'batch_processing', 'etl'] for domain in domain_indicators):
            hdfs_score += 2
            hdfs_reasons.append("batch processing domain")

        # Check for unstructured data patterns
        text_fields_ratio = len([f for f in field_types.values() if f == 'text_content']) / max(total_fields, 1)
        if text_fields_ratio > 0.5:
            hdfs_score += 2
            hdfs_reasons.append("high proportion of unstructured text")

        if total_records > 100000:
            hdfs_score += 1
            hdfs_reasons.append("very large dataset")

        # Decision logic with confidence scoring
        scores = {
            'clickhouse': clickhouse_score,
            'postgresql': postgresql_score,
            'hdfs': hdfs_score
        }

        reasons_map = {
            'clickhouse': clickhouse_reasons,
            'postgresql': postgresql_reasons,
            'hdfs': hdfs_reasons
        }

        # Get highest scoring database
        recommended_db = max(scores.keys(), key=lambda k: scores[k])
        max_score = scores[recommended_db]

        # Require minimum score for recommendation
        if max_score < 2:
            recommended_db = 'postgresql'  # Default fallback
            rationale = "Default recommendation - insufficient indicators for specialized database"
        else:
            rationale = f"Score: {max_score}/10. Reasons: {', '.join(reasons_map[recommended_db])}"

        return {
            'database': recommended_db,
            'rationale': rationale,
            'scores': scores
        }

    def _calculate_value_type_distribution(self, key_stats: Dict) -> Dict[str, float]:
        """Calculate distribution of value types across all fields"""
        type_counts = {}
        total_values = 0

        for stats in key_stats.values():
            types_counter = stats.get('types', {})
            for value_type, count in types_counter.items():
                type_counts[value_type] = type_counts.get(value_type, 0) + count
                total_values += count

        if total_values == 0:
            return {}

        return {
            value_type: self._safe_float(count / total_values)
            for value_type, count in type_counts.items()
        }

    def _build_nested_structure_map(self, structure_samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build nested structure map from samples"""
        if not structure_samples:
            return {}

        structure_map = {}
        for sample in structure_samples:
            for key, value in sample.items():
                if key not in structure_map:
                    if isinstance(value, str) and value.startswith('<object_with_'):
                        structure_map[key] = 'nested_object'
                    elif isinstance(value, str) and value.startswith('<array_with_'):
                        structure_map[key] = 'array'
                    else:
                        structure_map[key] = 'primitive'

        return structure_map