"""Module for building DDL statements."""

import asyncio

from models.ddl import DDL
from models.extract import ExtractConfig
from models.load import LoadConfig


async def generate_ddl_from_configs(extract_config: ExtractConfig, load_config: LoadConfig) -> DDL:
    """Generate DDL from ExtractConfig and LoadConfig."""
    # Simulate processing
    await asyncio.sleep(1)

    # Mock DDL
    return DDL(
        statements=[
            "CREATE TABLE etl_target_table (id Int32, name String) "
            "ENGINE = MergeTree() ORDER BY id;"
        ]
    )
