"""PostgreSQL extract configuration builder."""

from models.extract import Content, ContentType, Source

from .base import BaseExtractConfigBuilder


class PostgresExtractConfigBuilder(BaseExtractConfigBuilder):
    """Builder for PostgreSQL source configurations.

    Extracts metadata from PostgreSQL sources.
    """

    @classmethod
    async def get_content_metadata(cls, source: Source) -> list[Content]:
        """Extract content metadata from PostgreSQL source."""
        raise NotImplementedError("Metadata extraction not implemented for PostgreSQL sources.")

    @classmethod
    async def get_src_content_type(cls, source: Source) -> ContentType:
        """Get content type for PostgreSQL source.

        Args:
            source: PostgreSQL source configuration.

        Returns:
            ContentType for PostgreSQL.
        """
        raise NotImplementedError("Content type extraction not implemented for PostgreSQL sources.")

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
                        "table_name": source.table_name
                    }
                else:
                    return {
                        "total_records": 0,
                        "total_size_mb": 0,
                        "table_size_mb": 0,
                        "avg_record_size_bytes": 0,
                        "source_type": "postgresql",
                        "table_name": source.table_name
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
                "error": str(e)
            }
