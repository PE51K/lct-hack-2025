"""Models for create_dag endpoint."""

from typing import Annotated

from pydantic import BaseModel, Field

from models.app.ids import ThreadUserIds
from models.dag import DAG
from models.ddl import DDL
from models.load import LoadConfig


class PostgresCredentials(BaseModel):
    """PostgreSQL database credentials."""

    host: str = Field(..., description="PostgreSQL host address", examples=["postgres.example.com"])
    port: int = Field(5432, description="PostgreSQL port", examples=[5432])
    username: str = Field(..., description="PostgreSQL username", examples=["etl_user"])
    password: str = Field(..., description="PostgreSQL password", examples=["secure_password"])
    database: str = Field(..., description="PostgreSQL database name", examples=["analytics"])
    schema_name: str = Field(
        "public", description="PostgreSQL schema name", examples=["public", "staging"]
    )
    table_name: str | None = Field(
        None,
        description="Target table name (optional, overrides load_config)",
        examples=["employees", "sales_data"],
    )


class ClickHouseCredentials(BaseModel):
    """ClickHouse database credentials."""

    host: str = Field(
        ..., description="ClickHouse host address", examples=["clickhouse.example.com"]
    )
    port: int = Field(8123, description="ClickHouse HTTP port", examples=[8123, 9002])
    username: str = Field(..., description="ClickHouse username", examples=["etl_user"])
    password: str = Field(..., description="ClickHouse password", examples=["secure_password"])
    database: str = Field(..., description="ClickHouse database name", examples=["analytics"])
    table_name: str | None = Field(
        None,
        description="Target table name (optional, overrides load_config)",
        examples=["events", "metrics"],
    )


class HDFSCredentials(BaseModel):
    """HDFS storage credentials."""

    namenode_host: str = Field(
        ..., description="HDFS NameNode host", examples=["namenode.example.com"]
    )
    namenode_port: int = Field(9870, description="HDFS NameNode port", examples=[9870])
    user: str = Field(..., description="HDFS user", examples=["hdfs", "etl_user"])
    base_path: str = Field(..., description="Base HDFS path", examples=["/data/etl", "/warehouse"])
    authentication: str = Field(
        "simple", description="Authentication method", examples=["simple", "kerberos"]
    )
    table_name: str | None = Field(
        None,
        description="Target file/directory name (optional)",
        examples=["output_data", "results"],
    )


TargetCredentials = Annotated[
    PostgresCredentials | ClickHouseCredentials | HDFSCredentials,
    Field(discriminator="__class__"),
]


class CreateDAGRequest(BaseModel):
    """Request for creating DAG after credentials provided."""

    ids: ThreadUserIds = Field(..., description="User and thread identifiers")
    target_credentials: PostgresCredentials | ClickHouseCredentials | HDFSCredentials = Field(
        ...,
        description="Target database credentials (type depends on target storage)",
    )
    # Configs from previous /create_etl response
    extract_config: dict = Field(..., description="ExtractConfig from /create_etl")
    transform_config: dict = Field(..., description="TransformConfig from /create_etl")
    load_config: dict = Field(..., description="LoadConfig from /create_etl")
    ddl: dict = Field(..., description="DDL from /create_etl")


class CreateDAGResponse(BaseModel):
    """Response after DAG creation."""

    ids: ThreadUserIds
    processing_done: bool
    processing_percentage_done: float
    processing_message: str
    success: bool
    dag: DAG | None = None
    updated_load_config: LoadConfig | None = None
    updated_ddl: DDL | None = None
    error_message: str | None = None
