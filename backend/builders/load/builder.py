"""Load configuration builder."""

from models.extract import ExtractConfig
from models.load import (
    BatchConfig,
    CompressionConfig,
    Field,
    FlatMetaModel,
    Index,
    IndexingConfig,
    LoadConfig,
    LoadResourceConfig,
    LoadStrategy,
    MonitoringConfig,
    NestingMetaModel,
    PartitioningConfig,
    TargetStorageTypeRecommendation,
)


class LoadConfigBuilder:
    """Builder for LoadConfig."""

    async def __call__(self, extract_config: ExtractConfig, prompt: str) -> LoadConfig:
        """Build LoadConfig from ExtractConfig and prompt.

        Args:
            extract_config: The extract configuration.
            prompt: User prompt.

        Returns:
            LoadConfig with mocked data.
        """
        # Mocked data
        return LoadConfig(
            target_storage_type=TargetStorageTypeRecommendation(
                storage_type="postgres",
                explanation="Mocked target storage",
            ),
            target_storage_connection_string="postgresql://mock:mock@localhost/mock",
            nesting_metamodel=NestingMetaModel(
                data_structure={},
                partitioning_key="id",
            ),
            flat_meta_model=FlatMetaModel(
                fields=[
                    Field(name="id", data_type="integer", nullable=False),
                    Field(name="name", data_type="varchar(255)", nullable=True),
                ],
                indexes=[
                    Index(
                        name="idx_id",
                        is_clustered=True,
                        fields=[Field(name="id")],
                    )
                ],
                partitioning_key="id",
            ),
            load_strategy=LoadStrategy.APPEND,
            batch_config=BatchConfig(),
            partitioning=PartitioningConfig(),
            indexing=IndexingConfig(),
            compression=CompressionConfig(),
            resources=LoadResourceConfig(),
            monitoring=MonitoringConfig(),
        )
