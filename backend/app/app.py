"""
Main FastAPI application module.

This module sets up the FastAPI application with lifespan management,
logging, and API endpoints.
"""

import asyncio
import json
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from enum import Enum
from typing import Annotated

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from langfuse._client.client import Langfuse
from langfuse.langchain import CallbackHandler
from langgraph.checkpoint.postgres.aio import (
    AsyncConnectionPool,
    AsyncPostgresSaver,
)
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel

# Add parent directory to sys.path for local imports
sys.path.insert(0, "..")

from ai.agents.calculcator_agent import (
    calculator_agent_chat_prompt_template,
    calculator_agent_tools,
)
from ai.llm import llm
from core.logging import setup_logger
from core.settings import settings
from models.common import ThreadUserIds
from models.dag import DAG
from models.ddl import DDL
from models.extract import Content, ContentType, ExtractConfig, Source, SourceType
from models.generate_etl import GenerateETLRequest, GenerateETLResponse
from models.load import (
    Field,
    FlatMetaModel,
    LoadConfig,
    NestingMetaModel,
    TargetStorageTypeRecommendation,
)
from models.transform import TransformConfig
from models.update_etl import UpdateETLRequest, UpdateETLResponse
from models.execute_etl import ExecuteETLRequest, ExecuteETLResponse


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for FastAPI application.

    Handles startup and shutdown events.
    """
    # Setup logging
    app.state.logger = await setup_logger(__name__)

    # Startup
    await app.state.logger.info("Starting up application...")

    # Initialize LangFuse for tracing the UserCV."and monitoring
    await app.state.logger.info("Initializing LangFuse client for tracing...")
    app.state.langfuse_client = Langfuse(
        public_key=settings.ai.langfuse.public_key,
        secret_key=settings.ai.langfuse.secret_key,
        host=settings.ai.langfuse.base_url,
        tracing_enabled=settings.ai.langfuse.enabled,
    )
    app.state.langfuse_callback_handler = CallbackHandler(
        public_key=settings.ai.langfuse.public_key,
    )

    # Initialize agentic components
    await app.state.logger.info("Setting up PostgreSQL checkpointer for memory persistence...")
    async with AsyncConnectionPool(
        conninfo=settings.ai.langgraph_checkpointer.connection_string,
        kwargs={"autocommit": True},
    ) as pool:
        postgres_saver = AsyncPostgresSaver(pool)
        await postgres_saver.setup()

        # Set up calculator agent
        await app.state.logger.info("Setting up calculator agent...")
        app.state.calculator_agent = create_react_agent(
            model=llm,
            tools=calculator_agent_tools,
            prompt=calculator_agent_chat_prompt_template,
            checkpointer=postgres_saver,
        )

        # Finalize startup
        await app.state.logger.info("Application startup complete!")
        yield

    # Shutdown
    await app.state.logger.info("Application shutdown")
    await app.state.logger.shutdown()


# Initialize FastAPI application with lifespan management
app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app.cors.origins,
    allow_credentials=settings.app.cors.allow_credentials,
    allow_methods=settings.app.cors.allow_methods,
    allow_headers=settings.app.cors.allow_headers,
)

# ================== Mock Data Generators ===================


def generate_mock_extract_config() -> ExtractConfig:
    """Generate mock extract configuration."""
    return ExtractConfig(
        source_metadata=Source(
            source_type=SourceType.folder,
            connection_string="s3://mock-bucket/data/",
            content_type=ContentType.csv,
        ),
        content_metadata=[
            Content(
                message_name="data1.csv",
                metamodel={
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "value": {"type": "number"},
                    },
                },
            )
        ],
        content_statistics={"total_files": 1, "total_size": 1024},
    )


def generate_mock_transform_config() -> TransformConfig:
    """Generate mock transform configuration."""
    return TransformConfig(
        identity_keys=["id"],
        aggregate_keys=["name"],
        versioning_field="timestamp",
    )


def generate_mock_load_config() -> LoadConfig:
    """Generate mock load configuration."""
    return LoadConfig(
        target_storage_type=TargetStorageTypeRecommendation(
            storage_type="postgres",
            explanation="Relational database suitable for structured data.",
        ),
        target_storage_connection_string="postgresql://user:pass@localhost:5432/db",
        nesting_metamodel=NestingMetaModel(
            data_structure={"type": "object"},
            partitioning_key="id",
        ),
        flat_meta_model=FlatMetaModel(
            fields=[
                Field(name="id", data_type="INTEGER", nullable=False),
                Field(name="name", data_type="VARCHAR(255)", nullable=True),
                Field(name="value", data_type="DECIMAL", nullable=True),
            ],
            indexes=[],
            partitioning_key="id",
        ),
    )


def generate_mock_dag() -> DAG:
    """Generate mock DAG."""
    return DAG()  # Empty for now


def generate_mock_ddl() -> DDL:
    """Generate mock DDL."""
    return DDL()  # Empty for now


# ================== ETL Generation ===================


@app.post("/generate_etl")
async def generate_etl(request: GenerateETLRequest) -> StreamingResponse:
    """
    Generate ETL pipeline and recommendations based on input data URI.

    Args:
        request (GenerateETLRequest): The request containing input data URI and metadata.

    Returns:
        StreamingResponse: A streaming response with generation status updates.
    """
    ids = request.ids

    async def generate():
        # Step 1: Analyzing data
        yield (
            json.dumps(
                GenerateETLResponse(
                    ids=ids,
                    message="Analyzing input data from URI...",
                    done=False,
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(1)

        # Step 2: Generating extract config
        yield (
            json.dumps(
                GenerateETLResponse(
                    ids=ids,
                    message="Generating extract configuration...",
                    done=False,
                    extract_config=generate_mock_extract_config(),
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(1)

        # Step 3: Generating transform config
        yield (
            json.dumps(
                GenerateETLResponse(
                    ids=ids,
                    message="Generating transform configuration...",
                    done=False,
                    extract_config=generate_mock_extract_config(),
                    transform_config=generate_mock_transform_config(),
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(1)

        # Step 4: Generating load config
        yield (
            json.dumps(
                GenerateETLResponse(
                    ids=ids,
                    message="Generating load configuration...",
                    done=False,
                    extract_config=generate_mock_extract_config(),
                    transform_config=generate_mock_transform_config(),
                    load_config=generate_mock_load_config(),
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(1)

        # Step 5: Generating DDL
        yield (
            json.dumps(
                GenerateETLResponse(
                    ids=ids,
                    message="Generating DDL statements...",
                    done=False,
                    extract_config=generate_mock_extract_config(),
                    transform_config=generate_mock_transform_config(),
                    load_config=generate_mock_load_config(),
                    ddl=generate_mock_ddl(),
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(1)

        # Step 6: Generating DAG
        yield (
            json.dumps(
                GenerateETLResponse(
                    ids=ids,
                    message="Generating DAG structure...",
                    done=False,
                    extract_config=generate_mock_extract_config(),
                    transform_config=generate_mock_transform_config(),
                    load_config=generate_mock_load_config(),
                    ddl=generate_mock_ddl(),
                    dag=generate_mock_dag(),
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(1)

        # Final: Complete
        yield (
            json.dumps(
                GenerateETLResponse(
                    ids=ids,
                    message="ETL generation complete.",
                    done=True,
                    extract_config=generate_mock_extract_config(),
                    transform_config=generate_mock_transform_config(),
                    load_config=generate_mock_load_config(),
                    ddl=generate_mock_ddl(),
                    dag=generate_mock_dag(),
                ).model_dump()
            )
            + "\n"
        )

    return StreamingResponse(generate(), media_type="application/x-ndjson")


# ================== ETL Execution ===================


@app.post("/execute_etl")
async def execute_etl(request: ExecuteETLRequest) -> StreamingResponse:
    """
    Executes the ETL pipeline with provided metadata.

    Args:
        request (ExecuteETLRequest): The request containing metadata.

    Returns:
        StreamingResponse: A streaming response with execution status updates.
    """
    ids = request.ids

    async def generate():
        # Step 1: Starting execution
        yield (
            json.dumps(
                ExecuteETLResponse(
                    ids=ids,
                    message="Starting ETL execution...",
                    done=False,
                    success=False,
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(1)

        # Step 2: Extract phase
        yield (
            json.dumps(
                ExecuteETLResponse(
                    ids=ids,
                    message="Extracting data from source...",
                    done=False,
                    success=False,
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(2)

        # Step 3: Transform phase
        yield (
            json.dumps(
                ExecuteETLResponse(
                    ids=ids,
                    message="Transforming data...",
                    done=False,
                    success=False,
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(2)

        # Step 4: Load phase
        yield (
            json.dumps(
                ExecuteETLResponse(
                    ids=ids,
                    message="Loading data into target...",
                    done=False,
                    success=False,
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(2)

        # Final: Complete
        yield (
            json.dumps(
                ExecuteETLResponse(
                    ids=ids,
                    message="ETL execution completed successfully.",
                    done=True,
                    success=True,
                ).model_dump()
            )
            + "\n"
        )

    return StreamingResponse(generate(), media_type="application/x-ndjson")


# ================== ETL Update based on Feedback or Error ===================


@app.post("/update_etl")
async def update_etl(request: UpdateETLRequest) -> StreamingResponse:
    """
    Updates the ETL pipeline based on feedback or error messages.

    Args:
        request (UpdateETLRequest): The request containing feedback and metadata.

    Returns:
        StreamingResponse: A streaming response with update status.
    """
    ids = request.ids

    async def generate():
        # Step 1: Processing feedback
        yield (
            json.dumps(
                UpdateETLResponse(
                    ids=ids,
                    message="Processing user feedback...",
                    done=False,
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(1)

        # Step 2: Updating extract config
        yield (
            json.dumps(
                UpdateETLResponse(
                    ids=ids,
                    message="Updating extract configuration based on feedback...",
                    done=False,
                    extract_config=generate_mock_extract_config(),
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(1)

        # Step 3: Updating transform config
        yield (
            json.dumps(
                UpdateETLResponse(
                    ids=ids,
                    message="Updating transform configuration...",
                    done=False,
                    extract_config=generate_mock_extract_config(),
                    transform_config=generate_mock_transform_config(),
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(1)

        # Step 4: Updating load config
        yield (
            json.dumps(
                UpdateETLResponse(
                    ids=ids,
                    message="Updating load configuration...",
                    done=False,
                    extract_config=generate_mock_extract_config(),
                    transform_config=generate_mock_transform_config(),
                    load_config=generate_mock_load_config(),
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(1)

        # Step 5: Updating DDL
        yield (
            json.dumps(
                UpdateETLResponse(
                    ids=ids,
                    message="Updating DDL statements...",
                    done=False,
                    extract_config=generate_mock_extract_config(),
                    transform_config=generate_mock_transform_config(),
                    load_config=generate_mock_load_config(),
                    ddl=generate_mock_ddl(),
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(1)

        # Step 6: Updating DAG
        yield (
            json.dumps(
                UpdateETLResponse(
                    ids=ids,
                    message="Updating DAG structure...",
                    done=False,
                    extract_config=generate_mock_extract_config(),
                    transform_config=generate_mock_transform_config(),
                    load_config=generate_mock_load_config(),
                    ddl=generate_mock_ddl(),
                    dag=generate_mock_dag(),
                ).model_dump()
            )
            + "\n"
        )
        await asyncio.sleep(1)

        # Final: Complete
        yield (
            json.dumps(
                UpdateETLResponse(
                    ids=ids,
                    message="ETL update complete.",
                    done=True,
                    extract_config=generate_mock_extract_config(),
                    transform_config=generate_mock_transform_config(),
                    load_config=generate_mock_load_config(),
                    ddl=generate_mock_ddl(),
                    dag=generate_mock_dag(),
                ).model_dump()
            )
            + "\n"
        )

    return StreamingResponse(generate(), media_type="application/x-ndjson")


# ================== Chat with Agent ===================
# keeping for reference and backwards compatibility for now


class ChatWithAgentRequest(BaseModel):
    """
    Request model for chatting with an agent.

    Attributes:
        message (str): The message content to send to the agent.
        thread_id (str): Unique identifier for the conversation thread.
        user_id (str): Unique identifier for the user.
    """

    message: str
    thread_id: str
    user_id: str


class AgentNameEnum(str, Enum):
    """
    Enumeration of available agent names.

    Attributes:
        calculator (str): The calculator agent for performing mathematical operations.
    """

    calculator = "calculator"


@app.post("/chat/{agent_name}")
async def chat_with_agent(
    agent_name: Annotated[str, AgentNameEnum], request: ChatWithAgentRequest
) -> StreamingResponse:
    """
    Chat with the specified agent.

    Returns a streaming response with JSON lines containing message and metadata.

    Example response with different message types:
    ```
    # Tool call message
    {
        "message": {
            "content": "",
            "type": "AIMessageChunk",
            "tool_calls": [{"name": "sum_numbers", "args": {"numbers": [2, 2]}}],
        },
        "metadata": {"thread_id": "12345", "user_id": "67890", "langgraph_step": 1},
    }

    # Tool result message
    {
        "message": {
            "content": "4.0",
            "type": "tool",
            "name": "sum_numbers",
            "tool_call_id": "sum_numbers",
            "status": "success",
        },
        "metadata": {"thread_id": "12345", "user_id": "67890", "langgraph_step": 2},
    }

    # Text chunk message
    {
        "message": {"content": "The sum is 4", "type": "AIMessageChunk"},
        "metadata": {"thread_id": "12345", "user_id": "67890", "langgraph_step": 3},
    }
    ```
    """
    logger = app.state.logger
    await logger.info(f"Received chat message for agent {agent_name}: {request.message}")

    inputs = {
        "messages": HumanMessage(content=request.message),
    }
    config = {
        "configurable": {"thread_id": request.thread_id, "user_id": request.user_id},
        "callbacks": [app.state.langfuse_callback_handler],
        "run_name": f"process-{agent_name}-chat-message",
        "metadata": {
            "langfuse_session_id": request.thread_id,
            "langfuse_user_id": request.user_id,
            "langfuse_tags": ["chat", "fastapi", "agent", agent_name],
        },
    }

    async def generate():
        # Get the agent dynamically based on agent_name
        agent = getattr(app.state, f"{agent_name}_agent")
        # Stream events from the agent call
        async for event in agent.astream(
            inputs,
            config=config,
            stream_mode="messages",
        ):
            await logger.debug(event)
            # Serialize the event
            message_obj = event[0]
            metadata = event[1]
            message_dict = message_obj.dict() if hasattr(message_obj, "dict") else str(message_obj)
            # Yield as newline-delimited JSON
            yield json.dumps({"message": message_dict, "metadata": metadata}) + "\n"

    return StreamingResponse(generate(), media_type="application/x-ndjson")
