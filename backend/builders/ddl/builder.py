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
        # This is a simplified implementation - in real scenario would generate proper DDL
        target_type = load_config.target_storage_type.storage_type
        table_name = (
            load_config.flat_meta_model.fields[0].name
            if load_config.flat_meta_model.fields
            else "target_table"
        )

        if target_type == "postgres":
            query = f'''CREATE TABLE public.{load_config.flat_meta_model.table_name} ('''

            for field in load_config.flat_meta_model.fields:
                query += f'''
                    {field.name} {field.data_type} { 'NULL' if field .nullable else 'NOT NULL'},'''
        
            query += f'''
                PRIMARY KEY ({load_config.flat_meta_model.partitioning_key})
            );'''

            return query
        else:
            return f"-- DDL for {target_type} table {table_name}"
