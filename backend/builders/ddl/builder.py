"""DDL configuration builder."""

import logging

from models.ddl import DDL
from models.extract import ExtractConfig
from models.load import LoadConfig

logger = logging.getLogger(__name__)


class DDLBuilder:
    """Builder for DDL."""

    async def __call__(self, extract_config: ExtractConfig, load_config: LoadConfig) -> DDL:
        """Build DDL from ExtractConfig and LoadConfig.

        Args:
            extract_config: The extract configuration.
            load_config: The load configuration.

        Returns:
            DDL with generated statements.
        """
        # Generate DDL statements based on load_config
        statements = self._generate_ddl_statements(load_config)
        ddl = DDL(statements=statements)
        logger.debug(f"DDL fields: {ddl}")
        return ddl

    def _generate_ddl_statements(self, load_config: LoadConfig) -> str:
        """Generate DDL statements from load configuration."""
        target_type = load_config.target_storage_type.storage_type
        database_name = load_config.database_name
        schema_name = load_config.schema_name
        table_name = load_config.table_name

        if target_type == "postgres":
            # PostgreSQL: database.schema.table
            full_table_name = f"{schema_name}.{table_name}"
            query = f"""CREATE TABLE {full_table_name} ("""

            for field in load_config.flat_meta_model.fields:
                query += f"""
                    {field.name} {field.data_type} {"NULL" if field.nullable else "NOT NULL"},"""

            query += f"""
                PRIMARY KEY ({load_config.flat_meta_model.partitioning_key})
            );"""

            return query

        elif target_type == "clickhouse":
            # ClickHouse: database.table with ENGINE
            full_table_name = f"{database_name}.{table_name}"
            query = f"""CREATE TABLE {full_table_name} ("""

            for field in load_config.flat_meta_model.fields:
                nullable = "Nullable(" if field.nullable else ""
                closing = ")" if field.nullable else ""
                query += f"""
                    {field.name} {nullable}{field.data_type}{closing},"""

            # Remove trailing comma
            query = query.rstrip(",")

            query += f"""
            ) ENGINE = MergeTree()
            ORDER BY ({load_config.flat_meta_model.partitioning_key});"""

            return query

        else:
            # HDFS or other
            return f"-- DDL for {target_type} table {database_name}.{schema_name}.{table_name}"
