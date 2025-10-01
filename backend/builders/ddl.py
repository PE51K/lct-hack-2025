"""Module for building DDL statements."""

import asyncio

from models.ddl import DDL
from models.extract import ExtractConfig
from models.load import LoadConfig


async def generate_ddl_from_configs(load_config: LoadConfig) -> DDL:
    """Generate DDL from ExtractConfig and LoadConfig."""
   
    query = f'''CREATE TABLE public.{load_config.flat_meta_model.table_name} ('''

    for field in load_config.flat_meta_model.fields:
        query += f'''
            {field.name} {field.data_type} { 'NULL' if field.nullable else 'NOT NULL'},'''
 
    query += f'''
        PRIMARY KEY ({load_config.flat_meta_model.partitioning_key})
    );'''

    # Mock DDL
    return DDL(
        ddl_query=query
    )
