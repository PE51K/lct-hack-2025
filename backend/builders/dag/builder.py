"""DAG configuration builder."""

import logging

from models.dag import DAG
from models.ddl import DDL
from models.extract import ExtractConfig
from models.load import LoadConfig
from models.transform import TransformConfig

logger = logging.getLogger(__name__)


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
            DAG with generated structure.
        """
        logger.info("Building DAG structure")
        # Generate DAG structure
        dag_id = (
            f"etl_{extract_config.source_metadata.source_type}_"
            f"{load_config.target_storage_type.storage_type}"
        )
        logger.info(f"Generated DAG ID: {dag_id}")
        tasks = self._generate_tasks(extract_config, transform_config, load_config, ddl)

        dag = DAG(
            dag_id=dag_id,
            description=(
                f"ETL pipeline from {extract_config.source_metadata.source_type} "
                f"to {load_config.target_storage_type.storage_type}"
            ),
            tasks=tasks,
            schedule="@daily",
            owner="data_team",
            tags=["etl", "auto_generated"],
        )
        logger.info(f"DAG built with {len(tasks)} tasks")
        return dag

    def _generate_tasks(
        self,
        extract_config: ExtractConfig,
        transform_config: TransformConfig,
        load_config: LoadConfig,
        ddl: DDL,
    ) -> list:
        """Generate DAG tasks."""
        from models.dag import DAGTask

        tasks = []

        # Extract task
        extract_task = DAGTask(
            task_id="extract",
            task_type="extract",
            description="Extract data from source",
            dependencies=[],
            config={"source_type": extract_config.source_metadata.source_type},
        )
        tasks.append(extract_task)

        # Transform task
        transform_task = DAGTask(
            task_id="transform",
            task_type="transform",
            description="Transform data",
            dependencies=["extract"],
            config={"rules_count": len(transform_config.transformation_rules)},
        )
        tasks.append(transform_task)

        # Load task
        load_task = DAGTask(
            task_id="load",
            task_type="load",
            description="Load data to target",
            dependencies=["transform"],
            config={"target_type": load_config.target_storage_type.storage_type},
        )
        tasks.append(load_task)

        return tasks
