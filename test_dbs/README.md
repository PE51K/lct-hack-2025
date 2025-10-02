# Test Databases

This directory contains test database configurations and initialization scripts for development and testing.

## Overview

The test databases include:
- **PostgreSQL**: Relational database for structured data
- **ClickHouse**: Columnar database for analytical queries
- **MinIO**: S3-compatible object storage

## Connection Strings

### PostgreSQL
```
postgresql://<user>:<password>@localhost:<port>/<database>
```
Example with placeholders:
```
postgresql://postgres:postgres@localhost:5433/sample
```

### ClickHouse
```
clickhouse://<user>:<password>@localhost:<port>
```
Example with placeholders:
```
clickhouse://clickhouse:clickhouse@localhost:9001
```

### MinIO (S3-compatible)
```
http://<user>:<password>@localhost:<port>/<bucket>
```
Example with placeholders:
```
http://minio:miniosecret@localhost:9002/test-bucket
```

## Setup

1. Start the test databases using Docker Compose:
   ```bash
   docker-compose up -d
   ```

   This will automatically initialize PostgreSQL and ClickHouse with test data, and upload test files to MinIO.

2. (Optional) Manually initialize MinIO test data after containers are running:
    ```bash
    # Build the Docker image
    docker build -t test-dbs-init .

    # Run the initialization script
    docker run --env-file .env --network host test-dbs-init
    ```

## Configuration

Database settings are configured via the `.env` file. Copy `.env.example` to `.env` and adjust values as needed.

## Test Data

- **PostgreSQL**: Tables `employees`, `products`, `orders` with sample data
- **ClickHouse**: Same tables with sample data optimized for analytical queries
- **MinIO**: Sample CSV, JSON, and XML files in the `test-bucket` bucket