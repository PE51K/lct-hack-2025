"""PostgreSQL extract configuration builder."""

import pandas as pd
from sqlalchemy import create_engine, text

from models.extract import Attribute, Content, ContentType, PostgreSqlDataType, Source


class PostgresExtractConfigBuilder:
    """Builder for PostgreSQL source configurations.

    Extracts metadata from PostgreSQL sources.
    """

    @classmethod
    async def get_content_metadata(cls, source: Source) -> Content:
        """Extract content metadata from PostgreSQL source."""
        engine = create_engine(source.connection_string)

        with engine.connect() as connection:
            column_data_query = text("""
                                        SELECT
                                            column_name,
                                            data_type,
                                            is_nullable,
                                            character_maximum_length,
                                            numeric_precision,
                                            numeric_scale
                                        FROM information_schema.columns
                                        WHERE table_name = :table_name
                                        ORDER BY ordinal_position;
                                     """)

            result = connection.execute(column_data_query, {"table_name": source.table_name})

            rows = result.fetchall()
            columns = result.keys()

            df = pd.DataFrame(rows, columns=columns)

            cnt = Content(message_name=source.table_name, metamodel=[])

            for i in range(len(df)):
                attribute = Attribute(
                    order_no=i + 1,
                    column_name=df.loc[i, "column_name"],
                    data_type=PostgreSqlDataType(df.loc[i, "data_type"]),
                    is_nullable=df.loc[i, "is_nullable"] == "YES",
                    character_maximum_length=df.loc[i, "character_maximum_length"],
                    numeric_precision=df.loc[i, "numeric_precision"],
                    numeric_scale=df.loc[i, "numeric_scale"],
                )
                cnt.metamodel.append(attribute)

            return cnt

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
