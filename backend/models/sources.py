"""Models for data source connections and configurations."""

from __future__ import annotations

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


class ConnectionType(str, Enum):
    """Enumeration of supported connection types for data sources."""

    POSTGRES = "postgres"
    CLICKHOUSE = "clickhouse"
    KAFKA = "kafka"
    S3 = "s3"


class PostgresConn(BaseModel):
    """PostgreSQL connection parameters.

    Attributes:
        host: Hostname or IP.
        port: Port number.
        database: Database name.
        user: Username.
        password: Password or secret reference.
        sslmode: SSL mode (e.g., 'require', 'disable').
    """

    host: str
    port: int = 5432
    database: str
    user: str
    password: str
    sslmode: str | None = None


class ClickHouseConn(BaseModel):
    """
    ClickHouse connection parameters.

    Attributes:
        host: Hostname or IP.
        port: Port number.
        database: Database name.
        user: Optional username.
        password: Optional password or secret reference.
        protocol: Connection protocol ('native' or 'http').
    """

    host: str
    port: int = 9000
    database: str
    user: str | None = None
    password: str | None = None
    protocol: str = Field("native", description="native|http")


class S3Location(BaseModel):
    """
    S3-compatible storage location descriptor.

    Attributes:
        bucket: S3 bucket name.
        prefix: Optional prefix/path within the bucket.
        role_arn: Optional IAM role ARN for access.
        endpoint_url: Optional custom endpoint (for MinIO or S3-compatible services).
    """

    bucket: str
    prefix: str = ""
    role_arn: str | None = None
    endpoint_url: str | None = Field(None, description="For MinIO or S3-compatible endpoints.")


class KafkaConn(BaseModel):
    """
    Kafka connection parameters.

    Attributes:
        bootstrap_servers: List of bootstrap server addresses.
        security_protocol: Optional security protocol (e.g., 'SASL_SSL').
        sasl_mechanism: Optional SASL mechanism (e.g., 'PLAIN', 'SCRAM-SHA-256').
        sasl_username: Optional SASL username.
        sasl_password: Optional SASL password or secret reference.
    """

    bootstrap_servers: list[str]
    security_protocol: str | None = None
    sasl_mechanism: str | None = None
    sasl_username: str | None = None
    sasl_password: str | None = None


class SourceSystem(BaseModel):
    """Generic source descriptor used by ExtractConfig."""

    type: Annotated[str, ConnectionType]
    params: PostgresConn | ClickHouseConn | KafkaConn | S3Location
