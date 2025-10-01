"""DDL configuration builder."""

from models.ddl import DDL
from models.extract import ExtractConfig
from models.load import LoadConfig


class DDLBuilder:
    """Builder for DDL."""

    async def __call__(self, extract_config: ExtractConfig, load_config: LoadConfig) -> DDL:
        """Build DDL from ExtractConfig and LoadConfig.

        Args:
            extract_config: The extract configuration.
            load_config: The load configuration.

        Returns:
            DDL with mocked data.
        """
        # Mocked data
        return DDL()
