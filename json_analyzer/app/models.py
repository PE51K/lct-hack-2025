from pydantic import BaseModel, HttpUrl
from typing import Dict, List, Any, Optional, Union
from enum import Enum

class SourceType(str, Enum):
    FILE_UPLOAD = "file_upload"
    URL = "url"
    DIRECT_DATA = "direct_data"

class DataDistributionSkew(str, Enum):
    UNIFORM = "uniform"     # Even distribution
    MODERATE = "moderate"   # Some skew
    HIGH = "high"          # Highly skewed
    EXTREME = "extreme"    # One value dominates

class FieldType(str, Enum):
    TEMPORAL = "temporal"
    IDENTIFIER = "identifier"
    CATEGORICAL = "categorical"
    TEXT_CONTENT = "text_content"
    NUMERIC = "numeric"
    BOOLEAN = "boolean"
    CONTACT = "contact"
    PERSONAL_NAME = "personal_name"
    ORGANIZATION_NAME = "organization_name"

class UrlRequest(BaseModel):
    url: HttpUrl
    encoding: Optional[str] = None

class DirectDataRequest(BaseModel):
    data: Union[Dict[str, Any], List[Dict[str, Any]]]

class SourceInfo(BaseModel):
    source_type: SourceType
    total_records: int
    total_keys: int
    file_size_mb: float
    processing_time_seconds: float

class StructureAnalysis(BaseModel):
    nesting_depth: int
    schema_consistency: float
    most_frequent_keys: List[str]
    value_type_distribution: Dict[str, float]
    nested_structure_map: Dict[str, str]

class FieldAnalysis(BaseModel):
    field_name: str
    field_type: str
    sample_values: List[str]
    unique_count: int
    null_count: int
    completeness_ratio: float

class KeyAnalysis(BaseModel):
    key_name: str
    value_type: str
    key_frequency: int
    sample_values: List[str]
    null_percentage: float
    unique_percentage: float

class QualityMetrics(BaseModel):
    completeness_score: float
    consistency_score: float
    validity_score: float
    duplicate_records: int
    missing_values_total: int
    data_density: float
    uniqueness_distribution: Dict[str, float]

class SemanticAnalysis(BaseModel):
    detected_patterns: Dict[str, List[str]]
    domain_indicators: List[str]
    pii_risk_assessment: float

class StructuralCharacteristics(BaseModel):
    cardinality_patterns: Dict[str, List[str]]
    data_distribution_skew: Dict[str, List[str]]
    field_correlation_strength: float
    schema_stability: float

class UniversalSemanticPatterns(BaseModel):
    temporal_indicators: List[str]
    identifier_candidates: List[str]
    categorical_fields: List[str]
    text_content_fields: List[str]
    field_types: Dict[str, str]

class PerformanceHints(BaseModel):
    size_growth_indicators: Dict[str, Any]
    query_performance_hints: List[str]
    optimal_storage_format: str
    compression_potential: float
    indexing_strategy: Dict[str, str]
    recommended_database: str = "postgresql"  # Default value
    database_rationale: str = "Default recommendation"  # Default value

class AgentRecommendations(BaseModel):
    suggested_primary_key: str
    structural_characteristics: StructuralCharacteristics
    universal_semantics: UniversalSemanticPatterns
    performance_hints: PerformanceHints

class AnalysisMetadata(BaseModel):
    source_info: SourceInfo
    structure_analysis: StructureAnalysis
    key_analysis: List[FieldAnalysis]
    quality_metrics: QualityMetrics
    semantic_analysis: SemanticAnalysis
    agent_recommendations: AgentRecommendations

class ProcessingStats(BaseModel):
    memory_usage_mb: float
    processing_duration: float
    records_per_second: float
    analysis_timestamp: str

class AnalysisResponse(BaseModel):
    analysis_metadata: AnalysisMetadata
    ydata_profile_summary: Dict[str, Any]
    processing_stats: ProcessingStats