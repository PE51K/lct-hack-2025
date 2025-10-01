"""Script to generate example connection and extraction prompts for test databases."""

from core.settings import settings


def generate_postgres_prompt(table_name: str = "example_table") -> str:
    """Generate a prompt for PostgreSQL extraction."""
    return f"Connect to PostgreSQL database using connection string: {settings.postgres.connection_string} and extract data from table: {table_name}"


def generate_clickhouse_prompt(table_name: str = "example_table") -> str:
    """Generate a prompt for ClickHouse extraction."""
    return f"Connect to ClickHouse database using connection string: {settings.clickhouse.connection_string} and extract data from table: {table_name}"


def generate_minio_prompt(folder: str = "csv/") -> str:
    """Generate a prompt for MinIO (S3) extraction."""
    return f"Connect to S3-compatible storage using endpoint: {settings.minio.endpoint_url}, bucket: {settings.minio.bucket_name}, access_key: {settings.minio.root_user}, secret_key: {settings.minio.root_password} and extract data from folder: {folder}"


def main():
    """Print example prompts for all configured test databases."""
    print("Example Extraction Prompts:")
    print("=" * 50)

    print("PostgreSQL:")
    print(generate_postgres_prompt())
    print()

    print("ClickHouse:")
    print(generate_clickhouse_prompt())
    print()

    print("MinIO (S3):")
    print(generate_minio_prompt())
    print()


if __name__ == "__main__":
    main()