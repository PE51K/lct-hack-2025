"""
Main FastAPI application module.

This module sets up the FastAPI application with lifespan management,
logging, and API endpoints.
"""

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
from models.execute_etl import ExecuteETLRequest
from models.generate_etl import GenerateETLRequest
from models.update_etl import UpdateETLRequest

from .execute import execute_etl_endpoint
from .generate import generate_etl_endpoint
from .update import update_etl_endpoint


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
    return generate_etl_endpoint(request)


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
    return execute_etl_endpoint(request)


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
    return update_etl_endpoint(request)


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
