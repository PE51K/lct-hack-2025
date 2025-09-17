"""
Main FastAPI application module.

This module sets up the FastAPI application with lifespan management,
logging, and API endpoints.
"""

import json
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Dict

from pydantic import BaseModel
from langfuse._client.client import Langfuse
from langchain_core.messages import UserMessage
from langgraph.checkpoint.postgres.aio import (
    AsyncConnectionPool, 
    AsyncPostgresSaver,
)
from langfuse.langchain import CallbackHandler
from langgraph.prebuilt import create_react_agent
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

# Add parent directory to sys.path for local imports
sys.path.insert(0, "..")

from core.logging import setup_logger
from core.settings import settings
from ai.llm import llm
from pydantic import BaseModel
from ai.agents.calculcator_agent import (
    calculator_agent_system_prompt_template,
    calculator_agent_tools,
)


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
            prompt=calculator_agent_system_prompt_template,
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


class ChatWithAgentRequest(BaseModel):
    message: str
    thread_id: str
    user_id: str


@app.post("/chat/{agent_name}")
async def chat_with_agent(agent_name: str, request: ChatWithAgentRequest = Form(...)) -> StreamingResponse:
    """Chat with the specified agent."""
    logger = app.state.logger
    await logger.info(f"Received chat message for agent {agent_name}: {request.message}")

    inputs = {
        "messages": UserMessage(content=request.message),
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
