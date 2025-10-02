"""Script to generate example connection and extraction prompts for test databases."""

from core.settings import settings


def generate_postgres_prompt(table_name: str = "employees") -> str:
    """Generate a prompt for PostgreSQL extraction."""
    return (
        f"Connect to PostgreSQL database using connection string: "
        f"{settings.postgres.connection_string} and extract data from table: {table_name}"
    )


def generate_clickhouse_prompt(table_name: str = "employees") -> str:
    """Generate a prompt for ClickHouse extraction."""
    return (
        f"Connect to ClickHouse database using connection string: "
        f"{settings.clickhouse.connection_string} and extract data from table: {table_name}"
    )


def generate_minio_prompt(folder: str = "csv/") -> str:
    """Generate a prompt for MinIO (S3) extraction."""
    return (
        f"Connect to S3-compatible storage using endpoint: {settings.minio.endpoint_url}, "
        f"bucket: {settings.minio.bucket_name}, access_key: {settings.minio.root_user}, "
        f"secret_key: {settings.minio.root_password} and extract data from folder: {folder}"
    )


def main():
    """Print example prompts for all configured test databases."""
    print("Example Extraction Prompts:")
    print("=" * 80)
    print()
    print("NOTE: When using from browser (frontend), use 'localhost' in URLs.")
    print("      The backend automatically transforms localhost to Docker hostnames.")
    print("=" * 80)

    tables = ["employees", "products", "orders"]

    print()
    print("PostgreSQL:")
    for table in tables:
        print(f"Table: {table}")
        print(generate_postgres_prompt(table))
        print()

    print("ClickHouse:")
    for table in tables:
        print(f"Table: {table}")
        print(generate_clickhouse_prompt(table))
        print()

    print("MinIO (S3):")
    print("Frontend users should use: endpoint=http://localhost:9000")
    folders = ["csv/", "json/", "xml/"]
    for folder in folders:
        print(f"Folder: {folder}")
        print(generate_minio_prompt(folder))
        print()


if __name__ == "__main__":
    main()
