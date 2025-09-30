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
        try:
            engine = create_engine(source.connection_string)

            with engine.connect() as connection:
                # Получаем статистику по таблице
                stats_query = text("""
                    SELECT 
                        COUNT(*) as total_records,
                        pg_total_relation_size(quote_ident(:table_name)::regclass) as total_size_bytes,
                        pg_relation_size(quote_ident(:table_name)::regclass) as table_size_bytes
                """)

                result = connection.execute(stats_query, {"table_name": source.table_name})
                row = result.fetchone()

                if row:
                    total_records = row[0] if row[0] is not None else 0
                    total_size_bytes = row[1] if row[1] is not None else 0
                    table_size_bytes = row[2] if row[2] is not None else 0

                    return {
                        "total_records": total_records,
                        "total_size_mb": total_size_bytes / (1024 * 1024),
                        "table_size_mb": table_size_bytes / (1024 * 1024),
                        "avg_record_size_bytes": total_size_bytes / max(total_records, 1),
                        "source_type": "postgresql",
                        "table_name": source.table_name,
                    }
                else:
                    return {
                        "total_records": 0,
                        "total_size_mb": 0,
                        "table_size_mb": 0,
                        "avg_record_size_bytes": 0,
                        "source_type": "postgresql",
                        "table_name": source.table_name,
                    }

        except Exception as e:
            print(f"Ошибка получения статистики PostgreSQL: {e}")
            return {
                "total_records": 0,
                "total_size_mb": 0,
                "table_size_mb": 0,
                "avg_record_size_bytes": 0,
                "source_type": "postgresql",
                "table_name": source.table_name,
                "error": str(e),
            }
