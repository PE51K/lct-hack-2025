"""DAG configuration builder."""

from models.dag import DAG
from models.ddl import DDL
from models.extract import ExtractConfig
from models.load import LoadConfig
from models.transform import TransformConfig


class DAGBuilder:
    """Builder for DAG."""

    async def __call__(
        self,
        extract_config: ExtractConfig,
        transform_config: TransformConfig,
        load_config: LoadConfig,
        ddl: DDL,
    ) -> DAG:
        """Build DAG from ExtractConfig, TransformConfig, LoadConfig and DDL.

        Args:
            extract_config: The extract configuration.
            transform_config: The transform configuration.
            load_config: The load configuration.
            ddl: The DDL configuration.

        Returns:
            DAG with mocked data.
        """
        # Mocked data
        return DAG()
