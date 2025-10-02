"""DAG configuration builder."""

import logging
from datetime import datetime

from models.dag import DAG, DAGDefaultArgs, DAGTask
from models.ddl import DDL
from models.extract import ExtractConfig
from models.load import LoadConfig
from models.transform import TransformConfig

logger = logging.getLogger(__name__)


class DAGBuilder:
    """Builder for comprehensive DAG structures ready for execution."""

    async def __call__(
        self,
        extract_config: ExtractConfig,
        transform_config: TransformConfig,
        load_config: LoadConfig,
        ddl: DDL,
    ) -> DAG:
        """Build comprehensive DAG from ExtractConfig, TransformConfig, LoadConfig and DDL.

        Args:
            extract_config: The extract configuration.
            transform_config: The transform configuration.
            load_config: The load configuration.
            ddl: The DDL configuration.

        Returns:
            DAG with complete execution-ready structure.
        """
        # Generate DAG metadata
        dag_id = self._generate_dag_id(extract_config, load_config)
        description = self._generate_description(extract_config, load_config)

        # Generate tasks with detailed configuration
        tasks = self._generate_tasks(extract_config, transform_config, load_config, ddl)

        # Generate default arguments
        default_args = self._generate_default_args()

        # Estimate resource requirements
        estimated_runtime = self._estimate_runtime(extract_config, transform_config, load_config)
        cpu_cores = self._estimate_cpu_requirements(extract_config, transform_config, load_config)
        memory_mb = self._estimate_memory_requirements(
            extract_config, transform_config, load_config
        )

        # Generate documentation
        doc_md = self._generate_documentation(extract_config, transform_config, load_config, ddl)

        dag = DAG(
            dag_id=dag_id,
            description=description,
            tasks=tasks,
            schedule="@daily",
            start_date=datetime.now().replace(hour=2, minute=0, second=0, microsecond=0),
            catchup=False,
            max_active_runs=1,
            owner="data_team",
            team="data_engineering",
            tags=[
                "etl",
                "auto_generated",
                extract_config.source_metadata.source_type,
                load_config.target_storage_type.storage_type,
            ],
            default_args=default_args,
            concurrency=1,
            max_active_tasks=1,
            estimated_runtime_minutes=estimated_runtime,
            total_cpu_cores=cpu_cores,
            total_memory_mb=memory_mb,
            is_paused_upon_creation=True,
            doc_md=doc_md,
        )

        logger.debug(f"Generated comprehensive DAG: {dag.dag_id} with {len(dag.tasks)} tasks")
        return dag

    def _generate_dag_id(self, extract_config: ExtractConfig, load_config: LoadConfig) -> str:
        """Generate unique DAG ID."""
        source_type = extract_config.source_metadata.source_type
        target_type = load_config.target_storage_type.storage_type
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"etl_{source_type}_{target_type}_{timestamp}"

    def _generate_description(self, extract_config: ExtractConfig, load_config: LoadConfig) -> str:
        """Generate DAG description."""
        source_type = extract_config.source_metadata.source_type
        target_type = load_config.target_storage_type.storage_type
        return f"ETL pipeline extracting from {source_type} and loading to {target_type}"

    def _generate_default_args(self) -> DAGDefaultArgs:
        """Generate default arguments for DAG tasks."""
        return DAGDefaultArgs(
            owner="data_team",
            depends_on_past=False,
            start_date=datetime.now().replace(hour=2, minute=0, second=0, microsecond=0),
            email_on_failure=True,
            email_on_retry=False,
            retries=3,
            retry_delay_minutes=5,
            execution_timeout_minutes=60,
        )

    def _generate_tasks(
        self,
        extract_config: ExtractConfig,
        transform_config: TransformConfig,
        load_config: LoadConfig,
        ddl: DDL,
    ) -> list[DAGTask]:
        """Generate comprehensive DAG tasks with execution details."""
        tasks = []

        # Extract task
        extract_task = DAGTask(
            task_id="extract_data",
            task_type="extract",
            description=f"Extract data from {extract_config.source_metadata.source_type} source",
            dependencies=[],
            config={
                "source_type": extract_config.source_metadata.source_type,
                "connection_string": extract_config.source_metadata.connection_string,
                "batch_size": extract_config.batch_size,
            },
            operator_type="PythonOperator",
            pool_slots=1,
            execution_timeout_minutes=30,
            retry_count=3,
            retry_delay_minutes=5,
        )
        tasks.append(extract_task)

        # Transform task
        transform_task = DAGTask(
            task_id="transform_data",
            task_type="transform",
            description="Apply data transformations and validations",
            dependencies=["extract_data"],
            config={
                "rules_count": len(transform_config.transformation_rules),
                "identity_keys": transform_config.identity_keys,
                "processing_mode": transform_config.processing_mode,
            },
            operator_type="PythonOperator",
            pool_slots=2,
            execution_timeout_minutes=45,
            retry_count=2,
            retry_delay_minutes=5,
        )
        tasks.append(transform_task)

        # Generate full table name based on target type
        if load_config.target_storage_type.storage_type == "clickhouse":
            # ClickHouse: database.table (schema rarely used)
            full_table_name = f"{load_config.database_name}.{load_config.table_name}"
        else:
            # PostgreSQL: database.schema.table
            full_table_name = (
                f"{load_config.database_name}.{load_config.schema_name}.{load_config.table_name}"
            )

        # Load task
        load_task = DAGTask(
            task_id="load_data",
            task_type="load",
            description=f"Load transformed data to {load_config.target_storage_type.storage_type}",
            dependencies=["transform_data"],
            config={
                "target_type": load_config.target_storage_type.storage_type,
                "database_name": load_config.database_name,
                "schema_name": load_config.schema_name,
                "table_name": load_config.table_name,
                "full_table_name": full_table_name,
                "load_strategy": load_config.load_strategy,
                "batch_size": load_config.batch_config.batch_size,
            },
            operator_type="PythonOperator",
            pool_slots=1,
            execution_timeout_minutes=30,
            retry_count=3,
            retry_delay_minutes=5,
        )
        tasks.append(load_task)

        return tasks

    def _estimate_runtime(
        self,
        extract_config: ExtractConfig,
        transform_config: TransformConfig,
        load_config: LoadConfig,
    ) -> int:
        """Estimate total DAG runtime in minutes."""
        # Base time for setup and teardown
        base_time = 5

        # Extract time based on source complexity
        extract_time = 10  # Base extract time
        if hasattr(extract_config, "content_statistics") and extract_config.content_statistics:
            size_mb = extract_config.content_statistics.get("total_size_mb", 50)
            extract_time = max(10, int(size_mb / 5))  # 1 minute per 5MB

        # Transform time based on rules complexity
        transform_time = len(transform_config.transformation_rules) * 2  # 2 minutes per rule
        transform_time = max(5, min(transform_time, 30))  # Between 5-30 minutes

        # Load time based on target and volume
        load_time = 10  # Base load time
        if load_config.load_strategy == "incremental":
            load_time = 5  # Faster for incremental

        return base_time + extract_time + transform_time + load_time

    def _estimate_cpu_requirements(
        self,
        extract_config: ExtractConfig,
        transform_config: TransformConfig,
        load_config: LoadConfig,
    ) -> float:
        """Estimate CPU requirements."""
        cpu_cores = 1.0  # Base

        # Extract CPU based on parallelism
        if hasattr(extract_config, "resources") and extract_config.resources:
            cpu_cores += extract_config.resources.parallel_workers * 0.5

        # Transform CPU based on complexity
        rules_count = len(transform_config.transformation_rules)
        if rules_count > 5:
            cpu_cores += 1.0
        elif rules_count > 10:
            cpu_cores += 2.0

        # Load CPU based on connection pool size
        if hasattr(load_config, "resources") and load_config.resources:
            cpu_cores += load_config.resources.connection_pool_size * 0.1

        return min(cpu_cores, 4.0)  # Cap at 4 cores

    def _estimate_memory_requirements(
        self,
        extract_config: ExtractConfig,
        transform_config: TransformConfig,
        load_config: LoadConfig,
    ) -> int:
        """Estimate memory requirements in MB."""
        memory_mb = 1024  # Base 1GB

        # Extract memory based on batch size and data size
        if hasattr(extract_config, "content_statistics") and extract_config.content_statistics:
            size_mb = extract_config.content_statistics.get("total_size_mb", 50)
            memory_mb += int(size_mb * 2)  # 2x data size for processing

        # Transform memory based on rules
        rules_count = len(transform_config.transformation_rules)
        memory_mb += rules_count * 100  # 100MB per complex rule

        # Load memory based on batch processing
        if hasattr(load_config, "batch_config") and load_config.batch_config:
            memory_mb += load_config.batch_config.batch_size * 10  # 10MB per 1000 records

        return min(memory_mb, 8192)  # Cap at 8GB

    def _generate_documentation(
        self,
        extract_config: ExtractConfig,
        transform_config: TransformConfig,
        load_config: LoadConfig,
        ddl: DDL,
    ) -> str:
        """Generate Markdown documentation for the DAG."""
        # Generate full table name based on target type
        if load_config.target_storage_type.storage_type == "clickhouse":
            # ClickHouse: database.table
            full_table_name = f"{load_config.database_name}.{load_config.table_name}"
        else:
            # PostgreSQL: database.schema.table
            full_table_name = (
                f"{load_config.database_name}.{load_config.schema_name}.{load_config.table_name}"
            )

        doc = f"""
# ETL Pipeline: {extract_config.source_metadata.source_type} →
# {load_config.target_storage_type.storage_type}

## Overview
This DAG extracts data from {extract_config.source_metadata.source_type}, applies "
f"{len(transform_config.transformation_rules)} transformation rules, and loads to "
f"{load_config.target_storage_type.storage_type}.

## Tasks

### Extract Data
- **Source**: {extract_config.source_metadata.source_type}
- **Connection**: {extract_config.source_metadata.connection_string}
- **Batch Size**: {extract_config.batch_size}

### Transform Data
- **Rules**: {len(transform_config.transformation_rules)} transformation rules
- **Identity Keys**: {", ".join(transform_config.identity_keys)}
- **Processing Mode**: {transform_config.processing_mode}

### Load Data
- **Target**: {load_config.target_storage_type.storage_type}
- **Database**: {load_config.database_name}
- **Schema**: {load_config.schema_name}
- **Table**: {load_config.table_name}
- **Full Name**: {full_table_name}
- **Strategy**: {load_config.load_strategy}

## Schema
```sql
{ddl.statements}
```

## Monitoring
- Track extract row counts
- Monitor transformation success rates
- Verify load completion and data quality
"""
        return doc.strip()
