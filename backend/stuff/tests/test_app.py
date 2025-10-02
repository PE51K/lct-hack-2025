"""Tests for the FastAPI application endpoints."""

import json

import pytest
from fastapi.testclient import TestClient

from app.app import app


@pytest.fixture
def client() -> TestClient:
    """Test client fixture."""
    return TestClient(app)


@pytest.mark.asyncio
async def test_generate_etl_endpoint(client: TestClient):
    """Test the generate_etl endpoint with streaming response."""
    request_data = {
        "data_uri": "s3://mock-bucket/data.csv",
        "ids": {"thread_id": "test-thread-123", "user_id": "test-user-456"},
    }

    response = client.post("/generate_etl", json=request_data)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/x-ndjson"

    # Collect streamed lines
    lines = response.iter_lines()
    streamed_data = []
    for line in lines:
        if line:
            streamed_data.append(json.loads(line))

    # Check that we have multiple messages
    assert len(streamed_data) > 1

    # Check the first message
    first_msg = streamed_data[0]
    assert "ids" in first_msg
    assert first_msg["ids"]["thread_id"] == "test-thread-123"
    assert first_msg["ids"]["user_id"] == "test-user-456"
    assert "message" in first_msg
    assert not first_msg["done"]

    # Check the last message
    last_msg = streamed_data[-1]
    assert last_msg["done"]
    assert "extract_config" in last_msg
    assert "transform_config" in last_msg
    assert "load_config" in last_msg
    assert "ddl" in last_msg
    assert "dag" in last_msg


@pytest.mark.asyncio
async def test_execute_etl_endpoint(client: TestClient):
    """Test the execute_etl endpoint with streaming response."""
    request_data = {"ids": {"thread_id": "test-thread-123", "user_id": "test-user-456"}}

    response = client.post("/execute_etl", json=request_data)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/x-ndjson"

    # Collect streamed lines
    lines = response.iter_lines()
    streamed_data = []
    for line in lines:
        if line:
            streamed_data.append(json.loads(line))

    # Check that we have multiple messages
    assert len(streamed_data) > 1

    # Check the first message
    first_msg = streamed_data[0]
    assert "ids" in first_msg
    assert first_msg["ids"]["thread_id"] == "test-thread-123"
    assert first_msg["ids"]["user_id"] == "test-user-456"
    assert "message" in first_msg
    assert not first_msg["done"]
    assert not first_msg["success"]

    # Check the last message
    last_msg = streamed_data[-1]
    assert last_msg["done"]
    assert last_msg["success"]


@pytest.mark.asyncio
async def test_update_etl_endpoint(client: TestClient):
    """Test the update_etl endpoint with streaming response."""
    request_data = {
        "feedback": {
            "items": [
                {
                    "area": "extract",
                    "message": "Change source type",
                    "suggestion": "Use Kafka instead",
                }
            ],
            "overall": "Improve performance",
        },
        "ids": {"thread_id": "test-thread-123", "user_id": "test-user-456"},
    }

    response = client.post("/update_etl", json=request_data)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/x-ndjson"

    # Collect streamed lines
    lines = response.iter_lines()
    streamed_data = []
    for line in lines:
        if line:
            streamed_data.append(json.loads(line))

    # Check that we have multiple messages
    assert len(streamed_data) > 1

    # Check the first message
    first_msg = streamed_data[0]
    assert "ids" in first_msg
    assert first_msg["ids"]["thread_id"] == "test-thread-123"
    assert first_msg["ids"]["user_id"] == "test-user-456"
    assert "message" in first_msg
    assert not first_msg["done"]

    # Check the last message
    last_msg = streamed_data[-1]
    assert last_msg["done"]
    assert "extract_config" in last_msg
    assert "transform_config" in last_msg
    assert "load_config" in last_msg
    assert "ddl" in last_msg
    assert "dag" in last_msg
