"""PostgreSQL extract configuration builder."""
import re
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import json
from models.extract import Content, ContentType, Source



class PostgresExtractConfigBuilder:
    """Builder for PostgreSQL source configurations.

    Extracts metadata from PostgreSQL sources.
    """

    @classmethod
    async def get_content_metadata(cls, source: Source, table_name: str) -> list[Content]:
        """Extract content metadata from PostgreSQL source."""

        engine = create_engine(source.connection_string)

        with engine.connect() as connection:
            
            column_data_query = text(f"""
                                        SELECT 
                                            column_name,
                                            data_type,
                                            is_nullable,
                                            character_maximum_length,
                                            numeric_precision,
                                            numeric_scale
                                        FROM information_schema.columns 
                                        WHERE table_name = '{table_name}'
                                        ORDER BY ordinal_position;
                                     """
            )

            result = connection.execute(column_data_query)

            rows = result.fetchall()
            columns = result.keys()
            
            df = pd.DataFrame(rows, columns=columns)

            json_result = df.to_json(orient='records', indent=2)


            cnt_list = []
            cnt = Content(
                message_name=table_name,
                metamodel=json_result
            )
            cnt_list.append(cnt)

            return cnt_list

    @classmethod
    async def get_connection_data(cls, user_input: str) -> str:
        """Extract content metadata from PostgreSQL source."""
        pattern = r'postgresql://[^\s]+'
        match = re.search(pattern, user_input)

        if match:
            return match.group(0)
        
        return None
    
    @classmethod
    async def get_table_name(cls, user_input: str) -> str:
        """Extract content metadata from PostgreSQL source."""
        # Паттерн для поиска фразы "загрузи таблицу" или подобных вариаций
        patterns = [
            r'загрузи таблицу\s+(\w+)',
            r'загрузи таблицу\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'таблицу\s+(\w+)\s+и загрузи',
            r'таблицу\s+(\w+)\s+из',
            r'table\s+(\w+)',  # для английской версии
            r'load table\s+(\w+)'  # для английской версии
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None

    @classmethod
    async def get_src_content_type(cls, source: Source) -> ContentType:
        """Get content type for PostgreSQL source."""

        return ContentType.table

    @classmethod
    async def get_content_statistics(cls, source: Source) -> dict:
        """Retrieve statistics about the source content.

        Args:
            source: The source configuration.

        Returns:
            Dictionary containing content statistics with
            any additional information about the source.
        """
        raise NotImplementedError(
            "Content statistics extraction not implemented for PostgreSQL sources."
        )
