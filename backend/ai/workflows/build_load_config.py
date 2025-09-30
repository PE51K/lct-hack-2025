import asyncio

from models.extract import ExtractConfig
from models.load import LoadConfig, TargetStorageEnum, TargetStorageTypeRecommendation, NestingMetaModel, FlatMetaModel, Field, Index


async def build_load_config_from_extract_config_and_prompt(
    extract_config: ExtractConfig, user_prompt: str
) -> LoadConfig:
    """Build LoadConfig from ExtractConfig and user prompt using AI."""
    # Simulate AI processing
    await asyncio.sleep(1)

    # Mock implementation: choose ClickHouse as default storage
    return LoadConfig(
        target_storage_type=TargetStorageTypeRecommendation(
            storage_type=TargetStorageEnum.CLICKHOUSE,
            explanation="Chosen as default for analytical workloads"
        ),
        target_storage_connection_string="clickhouse://user:password@localhost:8123/default",
        nesting_metamodel=NestingMetaModel(
            data_structure={"columns": []},
            partitioning_key="id"
        ),
        flat_meta_model=FlatMetaModel(
            fields=[Field(name="id", data_type="UInt64", nullable=False)],
            indexes=[],
            partitioning_key="id"
        )
    )