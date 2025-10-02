"""
Settings for test databases initialization.

Uses Pydantic's BaseSettings to manage configuration and environment variables.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    """
    Settings for test PostgreSQL database.

    Attributes:
        user (str): Database user.
        password (str): Database password.
        db (str): Database name.
        host (str): Database host.
        port (int): Database port.
        connection_string (str): Constructed PostgreSQL connection string.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="TEST_POSTGRES_",
        extra="ignore",
    )

    user: str
    password: str
    db: str
    host: str = Field(default="localhost")
    port: int = Field(default=5433)

    @property
    def connection_string(self) -> str:
        """Constructs a PostgreSQL connection string from the settings."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class ClickHouseSettings(BaseSettings):
    """
    Settings for test ClickHouse database.

    Attributes:
        user (str): Database user.
        password (str): Database password.
        host (str): Database host.
        port (int): Database port.
        http_port (int): HTTP port for ClickHouse.
        connection_string (str): Constructed ClickHouse connection string.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="TEST_CLICKHOUSE_",
        extra="ignore",
    )

    user: str
    password: str
    host: str = Field(default="localhost")
    port: int = Field(default=9001)
    http_port: int = Field(default=8124)

    @property
    def connection_string(self) -> str:
        """Constructs a ClickHouse connection string from the settings."""
        return f"clickhouse://{self.user}:{self.password}@{self.host}:{self.port}"


class MinioSettings(BaseSettings):
    """
    Settings for test MinIO (S3-compatible) storage.

    Attributes:
        root_user (str): Root user for MinIO.
        root_password (str): Root password for MinIO.
        host (str): MinIO host.
        port (int): MinIO port.
        endpoint_url (str): Full endpoint URL for MinIO.
        bucket_name (str): Default bucket name for test data.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="TEST_MINIO_",
        extra="ignore",
    )

    root_user: str
    root_password: str
    host: str = Field(default="localhost")
    port: int = Field(default=9000)
    bucket_name: str

    @property
    def endpoint_url(self) -> str:
        """Constructs the MinIO endpoint URL."""
        return f"http://{self.host}:{self.port}"


class TestDBSettings(BaseSettings):
    """
    Main settings class for test databases.

    Attributes:
        postgres (PostgresSettings): PostgreSQL settings.
        clickhouse (ClickHouseSettings): ClickHouse settings.
        minio (MinioSettings): MinIO settings.
    """

    postgres: PostgresSettings = PostgresSettings()
    clickhouse: ClickHouseSettings = ClickHouseSettings()
    minio: MinioSettings = MinioSettings()


# Singleton instance of TestDBSettings
settings = TestDBSettings()


__all__ = ["settings"]
